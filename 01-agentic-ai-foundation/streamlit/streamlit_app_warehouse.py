import streamlit as st
import json
import pandas as pd
from snowflake.snowpark.context import get_active_session
import _snowflake

st.set_page_config(page_title="EPOWER Sales Dashboard", layout="wide")

session = get_active_session()

AGENT_ENDPOINT = "/api/v2/databases/EPOWER_DEMO/schemas/EPOWER_GOLD/agents/EPOWER_AGENT:run"

tab_sales, tab_chat = st.tabs(["Sales Performance", "Agent Chat"])


def run_query(sql):
    return session.sql(sql).to_pandas()


def call_agent(messages):
    body = {"messages": messages, "stream": False}
    try:
        resp = _snowflake.send_snow_api_request(
            "POST", AGENT_ENDPOINT, {}, {}, body, {}, 60000
        )
        status = resp.get("status", 0) if isinstance(resp, dict) else None
        content = resp.get("content", "") if isinstance(resp, dict) else str(resp)
        if status == 200:
            return json.loads(content)
        return {"error": f"Status {status}: {content[:500]}"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}


def extract_agent_response(resp):
    texts = []
    tables = []
    charts = []
    for item in resp.get("content", []):
        if item.get("type") == "text":
            texts.append(item.get("text", ""))
        elif item.get("type") == "table":
            table = item.get("table", {})
            rs = table.get("result_set", {})
            meta = rs.get("resultSetMetaData", {})
            cols = [r["name"] for r in meta.get("rowType", [])]
            data = rs.get("data", [])
            if cols and data:
                tables.append({"title": table.get("title", ""), "df": pd.DataFrame(data, columns=cols)})
        elif item.get("type") == "chart":
            chart = item.get("chart", {})
            spec = chart.get("chart_spec", "")
            if spec:
                charts.append(json.loads(spec))
    return "\n\n".join(texts), tables, charts


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: SALES PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────
with tab_sales:
    st.header("EPOWER Sales Performance")

    # --- FILTERS ---
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    regions = run_query("SELECT REGION_KEY, REGION_NAME FROM EPOWER_DEMO.EPOWER_GOLD.REGION_DIM ORDER BY REGION_NAME")
    categories = run_query("SELECT DISTINCT CATEGORY_NAME FROM EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM ORDER BY 1")

    with filter_col1:
        selected_regions = st.multiselect(
            "Region",
            options=regions["REGION_NAME"].tolist(),
            default=regions["REGION_NAME"].tolist()
        )

    with filter_col2:
        selected_categories = st.multiselect(
            "Product Category",
            options=categories["CATEGORY_NAME"].tolist(),
            default=categories["CATEGORY_NAME"].tolist()
        )

    with filter_col3:
        time_period = st.selectbox("Time Period", ["Last 12 Months", "Last 6 Months", "Last 3 Months", "Last 30 Days", "All Time"])

    period_map = {
        "Last 12 Months": "DATEADD('month', -12, CURRENT_DATE())",
        "Last 6 Months": "DATEADD('month', -6, CURRENT_DATE())",
        "Last 3 Months": "DATEADD('month', -3, CURRENT_DATE())",
        "Last 30 Days": "DATEADD('day', -30, CURRENT_DATE())",
        "All Time": "'2020-01-01'",
    }
    date_filter = period_map[time_period]

    region_keys = regions[regions["REGION_NAME"].isin(selected_regions)]["REGION_KEY"].tolist()
    region_filter = ",".join(str(k) for k in region_keys) if region_keys else "NULL"
    cat_filter = ",".join(f"'{c}'" for c in selected_categories) if selected_categories else "''"

    base_where = f"""
        WHERE s.DATE >= {date_filter}
        AND s.REGION_KEY IN ({region_filter})
        AND p.CATEGORY_NAME IN ({cat_filter})
    """

    # --- KPIs ---
    kpi = run_query(f"""
        SELECT
            ROUND(SUM(s.AMOUNT), 0) AS total_revenue,
            COUNT(*) AS total_contracts,
            COUNT(DISTINCT s.CUSTOMER_KEY) AS unique_customers,
            ROUND(AVG(s.AMOUNT), 0) AS avg_deal_size
        FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
        JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        {base_where}
    """)

    col1, col2, col3, col4 = st.columns(4)
    if not kpi.empty:
        col1.metric("Total Revenue", f"€{kpi.iloc[0]['TOTAL_REVENUE']:,.0f}")
        col2.metric("Contracts Sold", f"{int(kpi.iloc[0]['TOTAL_CONTRACTS']):,}")
        col3.metric("Unique Customers", f"{int(kpi.iloc[0]['UNIQUE_CUSTOMERS']):,}")
        col4.metric("Avg Deal Size", f"€{kpi.iloc[0]['AVG_DEAL_SIZE']:,.0f}")

    st.markdown("---")

    # --- CHARTS ---
    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue Trend")
        trend = run_query(f"""
            SELECT
                DATE_TRUNC('month', s.DATE) AS month,
                ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 1
        """)
        if not trend.empty:
            st.line_chart(trend.set_index("MONTH")["REVENUE"])

    with right:
        st.subheader("Revenue by Product Category")
        by_cat = run_query(f"""
            SELECT
                p.CATEGORY_NAME AS category,
                ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not by_cat.empty:
            st.bar_chart(by_cat.set_index("CATEGORY")["REVENUE"])

    left2, right2 = st.columns(2)

    with left2:
        st.subheader("Revenue by Region")
        by_region = run_query(f"""
            SELECT
                r.REGION_NAME AS region,
                ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            JOIN EPOWER_DEMO.EPOWER_GOLD.REGION_DIM r ON s.REGION_KEY = r.REGION_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not by_region.empty:
            st.bar_chart(by_region.set_index("REGION")["REVENUE"])

    with right2:
        st.subheader("Top 10 Products by Revenue")
        top_products = run_query(f"""
            SELECT
                p.PRODUCT_NAME AS product,
                ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
            LIMIT 10
        """)
        if not top_products.empty:
            st.bar_chart(top_products.set_index("PRODUCT")["REVENUE"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: AGENT CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Chat with EPOWER Agent")
    st.caption("Ask questions about sales, billing, VPP telemetry, prices, HR, or search documents.")

    show_payload = st.checkbox("Show REST API Request/Response", value=False)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_request" not in st.session_state:
        st.session_state.last_request = None
    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['display']}")
        else:
            st.markdown(f"**Agent:** {msg['display']}")

    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_input("Ask the EPOWER Agent...", key="chat_input")
        submitted = st.form_submit_button("Send")

    if submitted and prompt:
        st.session_state.messages.append({"role": "user", "display": prompt})

        api_messages = [
            {
                "role": m["role"],
                "content": [{"type": "text", "text": m["display"]}],
            }
            for m in st.session_state.messages
            if m["role"] == "user"
        ]

        request_payload = {
            "endpoint": f"POST https://<account>.snowflakecomputing.com{AGENT_ENDPOINT}",
            "body": {"messages": api_messages, "stream": False}
        }
        st.session_state.last_request = request_payload

        with st.spinner("Thinking..."):
            resp = call_agent(api_messages)

        st.session_state.last_response = resp

        if "error" in resp:
            display_text = f"Error: {resp['error']}"
        else:
            text, tables, charts = extract_agent_response(resp)
            display_text = text or "No response text."
            for t in tables:
                if t["title"]:
                    st.caption(t["title"])
                st.dataframe(t["df"], use_container_width=True)
            for c in charts:
                st.vega_lite_chart(c, use_container_width=True)

        st.session_state.messages.append({"role": "assistant", "display": display_text})
        st.experimental_rerun()

    if show_payload and st.session_state.last_request:
        st.markdown("---")
        st.subheader("REST API Request")
        st.code(json.dumps(st.session_state.last_request, indent=2), language="json")
        st.subheader("REST API Response")
        resp_display = st.session_state.last_response or {}
        with st.container():
            st.text_area("Response JSON", json.dumps(resp_display, indent=2, default=str), height=400)
