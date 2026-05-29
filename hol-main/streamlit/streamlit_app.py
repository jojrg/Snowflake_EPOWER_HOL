import streamlit as st
import json
import os
import requests
import pandas as pd

st.set_page_config(page_title="EPOWER Assistant", page_icon="⚡", layout="wide")

conn = st.connection("snowflake")
session = conn.session()

SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")
AGENT_PATH = "/api/v2/databases/EPOWER_DEMO/schemas/EPOWER_GOLD/agents/EPOWER_AGENT:run"
AGENT_URL = f"https://{SNOWFLAKE_HOST}{AGENT_PATH}"


def get_token():
    return open("/snowflake/session/token").read()


@st.cache_data(ttl=300)
def run_query(sql):
    return session.sql(sql).to_pandas()


def stream_agent(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
        "Accept": "text/event-stream",
    }
    body = {"messages": messages, "stream": True}
    response = requests.post(AGENT_URL, headers=headers, json=body, stream=True)
    full_text = ""
    tables = []
    charts = []
    request_payload = {"endpoint": f"POST {AGENT_URL}", "body": body}

    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        try:
            data = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        event_type = None
        for key in ["text", "content_index", "tool_use_id", "status", "role"]:
            if key in data:
                break

        if "text" in data and "content_index" in data and "tool_use_id" not in data:
            delta = data.get("text", "")
            full_text += delta
            yield {"type": "text_delta", "text": delta}

        elif "result_set" in data:
            rs = data.get("result_set", {})
            meta = rs.get("resultSetMetaData", {})
            cols = [r["name"] for r in meta.get("rowType", [])]
            rows = rs.get("data", [])
            if cols and rows:
                tables.append({"title": data.get("title", ""), "df": pd.DataFrame(rows, columns=cols)})

        elif "chart_spec" in data:
            try:
                charts.append(json.loads(data["chart_spec"]))
            except:
                pass

        elif "role" in data and data.get("role") == "assistant":
            for item in data.get("content", []):
                if item.get("type") == "text":
                    txt = item.get("text", "")
                    if txt and not full_text:
                        full_text = txt
                        yield {"type": "text_delta", "text": txt}
                elif item.get("type") == "table":
                    table = item.get("table", {})
                    rs = table.get("result_set", {})
                    meta = rs.get("resultSetMetaData", {})
                    cols = [r["name"] for r in meta.get("rowType", [])]
                    rows = rs.get("data", [])
                    if cols and rows:
                        tables.append({"title": table.get("title", ""), "df": pd.DataFrame(rows, columns=cols)})

    yield {"type": "done", "full_text": full_text, "tables": tables, "charts": charts, "request": request_payload, "response_preview": full_text[:200]}


def call_agent_sync(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
        "Accept": "application/json",
    }
    body = {"messages": messages, "stream": False}
    response = requests.post(AGENT_URL, headers=headers, json=body)
    return body, response.json()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=48)
    st.title("EPOWER")
    st.caption("Energy Intelligence Platform")
    st.divider()
    page = st.radio("Navigate", ["Sales Dashboard", "Agent Chat"], label_visibility="collapsed")
    st.divider()
    st.caption("Powered by Snowflake Cortex Agent REST API")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SALES DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "Sales Dashboard":
    st.title("Sales Performance")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    regions = run_query("SELECT REGION_KEY, REGION_NAME FROM EPOWER_DEMO.EPOWER_GOLD.REGION_DIM ORDER BY REGION_NAME")
    categories = run_query("SELECT DISTINCT CATEGORY_NAME FROM EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM ORDER BY 1")

    with filter_col1:
        selected_regions = st.multiselect("Region", options=regions["REGION_NAME"].tolist(), default=regions["REGION_NAME"].tolist())

    with filter_col2:
        selected_categories = st.multiselect("Product Category", options=categories["CATEGORY_NAME"].tolist(), default=categories["CATEGORY_NAME"].tolist())

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
        col1.metric("Total Revenue", f"\u20ac{kpi.iloc[0]['TOTAL_REVENUE']:,.0f}")
        col2.metric("Contracts Sold", f"{int(kpi.iloc[0]['TOTAL_CONTRACTS']):,}")
        col3.metric("Unique Customers", f"{int(kpi.iloc[0]['UNIQUE_CUSTOMERS']):,}")
        col4.metric("Avg Deal Size", f"\u20ac{kpi.iloc[0]['AVG_DEAL_SIZE']:,.0f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue Trend")
        trend = run_query(f"""
            SELECT DATE_TRUNC('month', s.DATE) AS month, ROUND(SUM(s.AMOUNT), 0) AS revenue
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
            SELECT p.CATEGORY_NAME AS category, ROUND(SUM(s.AMOUNT), 0) AS revenue
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
            SELECT r.REGION_NAME AS region, ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            JOIN EPOWER_DEMO.EPOWER_GOLD.REGION_DIM r ON s.REGION_KEY = r.REGION_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not by_region.empty:
            st.bar_chart(by_region.set_index("REGION")["REVENUE"])

    with right2:
        st.subheader("Top 10 Products")
        top_products = run_query(f"""
            SELECT p.PRODUCT_NAME AS product, ROUND(SUM(s.AMOUNT), 0) AS revenue
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """)
        if not top_products.empty:
            st.bar_chart(top_products.set_index("PRODUCT")["REVENUE"])

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AGENT CHAT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Agent Chat":
    st.title("EPOWER Agent")
    st.caption("Ask questions about sales, billing, VPP telemetry, electricity prices, HR, or search company documents.")

    show_api = st.toggle("Show REST API payloads", value=False)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_api" not in st.session_state:
        st.session_state.last_api = {"request": None, "response": None}

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tables"):
                for t in msg["tables"]:
                    if t.get("title"):
                        st.caption(t["title"])
                    st.dataframe(t["df"], use_container_width=True)

    if prompt := st.chat_input("Ask the EPOWER Agent..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        api_messages = [
            {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
            for m in st.session_state.chat_history
            if m["role"] == "user"
        ]

        with st.chat_message("assistant"):
            collected_text = ""
            collected_tables = []
            collected_charts = []
            text_placeholder = st.empty()

            for event in stream_agent(api_messages):
                if event["type"] == "text_delta":
                    collected_text += event["text"]
                    text_placeholder.markdown(collected_text + "\u2588")
                elif event["type"] == "done":
                    collected_tables = event.get("tables", [])
                    collected_charts = event.get("charts", [])
                    st.session_state.last_api = {
                        "request": event.get("request"),
                        "response": event.get("full_text", "")[:2000],
                    }

            text_placeholder.markdown(collected_text or "No response.")

            for t in collected_tables:
                if t.get("title"):
                    st.caption(t["title"])
                st.dataframe(t["df"], use_container_width=True)
            for c in collected_charts:
                st.vega_lite_chart(c, use_container_width=True)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": collected_text or "No response.",
            "tables": collected_tables,
        })

    if show_api and st.session_state.last_api["request"]:
        st.divider()
        col_req, col_resp = st.columns(2)
        with col_req:
            st.subheader("Request")
            st.code(json.dumps(st.session_state.last_api["request"], indent=2), language="json")
        with col_resp:
            st.subheader("Response (text)")
            st.text_area("", st.session_state.last_api["response"], height=300)
