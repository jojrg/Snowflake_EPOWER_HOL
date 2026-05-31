import streamlit as st
import json
import os
import requests
import pandas as pd

st.set_page_config(page_title="EPOWER Assistant", layout="wide")

AGENT_PATH = "/api/v2/databases/EPOWER_DEMO/schemas/EPOWER_GOLD/agents/EPOWER_AGENT:run"
SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")
AGENT_URL = f"https://{SNOWFLAKE_HOST}{AGENT_PATH}"


def get_token():
    with open("/snowflake/session/token") as f:
        return f.read().strip()


def get_session():
    return st.connection("snowflake").session()


def run_query(sql):
    return get_session().sql(sql).to_pandas()


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_dashboard, tab_chat = st.tabs(["Dashboard", "Agent Chat"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: SALES & ENERGY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.title("EPOWER Sales & Energy Dashboard")

    regions = run_query("SELECT REGION_KEY, REGION_NAME FROM EPOWER_DEMO.EPOWER_GOLD.REGION_DIM ORDER BY REGION_NAME")
    categories = run_query("SELECT DISTINCT CATEGORY_NAME FROM EPOWER_DEMO.EPOWER_GOLD.PRODUCT_CATEGORY_DIM ORDER BY 1")

    f1, f2, f3 = st.columns(3)
    with f1:
        selected_regions = st.multiselect("Region", options=regions["REGION_NAME"].tolist(), default=regions["REGION_NAME"].tolist())
    with f2:
        selected_categories = st.multiselect("Product Category", options=categories["CATEGORY_NAME"].tolist(), default=categories["CATEGORY_NAME"].tolist())
    with f3:
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
    region_in = ",".join(str(k) for k in region_keys) if region_keys else "NULL"
    cat_in = ",".join(f"'{c}'" for c in selected_categories) if selected_categories else "''"

    base_where = f"""
        WHERE s.DATE >= {date_filter}
        AND s.REGION_KEY IN ({region_in})
        AND p.CATEGORY_NAME IN ({cat_in})
    """

    # --- KPIs ---
    kpi_sales = run_query(f"""
        SELECT
            COALESCE(SUM(s.AMOUNT), 0) AS total_revenue,
            COUNT(*) AS total_contracts,
            COUNT(DISTINCT s.CUSTOMER_KEY) AS unique_customers,
            COALESCE(ROUND(AVG(s.AMOUNT), 0), 0) AS avg_deal_size
        FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
        JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        {base_where}
    """)

    vpp_latest = run_query("""
        SELECT
            SUM(ACTIVE_VPP_DEVICES) AS devices,
            ROUND(AVG(AVG_BATTERY_SOC_PCT), 1) AS battery_soc,
            ROUND(SUM(TOTAL_SOLAR_YIELD_KW), 0) AS solar_kw,
            ROUND(SUM(NET_GRID_KW), 0) AS grid_kw
        FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY
        WHERE HOUR = (SELECT MAX(HOUR) FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY)
    """)

    c1, c2, c3, c4 = st.columns(4)
    if not kpi_sales.empty:
        c1.metric("Total Revenue", f"\u20ac{kpi_sales.iloc[0]['TOTAL_REVENUE']:,.0f}")
        c2.metric("Contracts Sold", f"{int(kpi_sales.iloc[0]['TOTAL_CONTRACTS']):,}")
    if not vpp_latest.empty:
        c3.metric("VPP Devices Online", f"{int(vpp_latest.iloc[0]['DEVICES']):,}")
        c4.metric("Solar Generation", f"{int(vpp_latest.iloc[0]['SOLAR_KW']):,} kW")

    st.divider()

    # --- Charts Row 1 ---
    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue Trend")
        trend = run_query(f"""
            SELECT
                DATE_TRUNC('month', s.DATE)::DATE AS MONTH,
                ROUND(SUM(s.AMOUNT), 0) AS REVENUE
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 1
        """)
        if not trend.empty:
            st.line_chart(trend, x="MONTH", y="REVENUE")

    with right:
        st.subheader("Revenue by Category")
        by_cat = run_query(f"""
            SELECT
                p.CATEGORY_NAME AS CATEGORY,
                ROUND(SUM(s.AMOUNT), 0) AS REVENUE
            FROM EPOWER_DEMO.EPOWER_GOLD.SALES_FACT s
            JOIN EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM p ON s.PRODUCT_KEY = p.PRODUCT_KEY
            {base_where}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not by_cat.empty:
            st.bar_chart(by_cat, x="CATEGORY", y="REVENUE")

    # --- Charts Row 2 ---
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("VPP Fleet (Last 7 Days)")
        vpp_trend = run_query("""
            SELECT
                HOUR,
                SUM(TOTAL_SOLAR_YIELD_KW) AS SOLAR_KW,
                AVG(AVG_BATTERY_SOC_PCT) AS BATTERY_SOC,
                SUM(NET_GRID_KW) AS NET_GRID_KW
            FROM EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY
            WHERE HOUR >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY HOUR ORDER BY HOUR
        """)
        if not vpp_trend.empty:
            st.line_chart(vpp_trend, x="HOUR", y=["SOLAR_KW", "NET_GRID_KW"])

    with right2:
        st.subheader("Electricity Spot Price (Last 7 Days)")
        prices = run_query("""
            SELECT
                HOUR,
                PRICE_EUR_MWH
            FROM EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES
            WHERE HOUR >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            ORDER BY HOUR
        """)
        if not prices.empty:
            st.line_chart(prices, x="HOUR", y="PRICE_EUR_MWH")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: AGENT CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.title("EPOWER Agent Chat")
    st.caption("Ask questions about sales, billing, VPP telemetry, energy prices, or search company documents.")

    show_payload = st.toggle("Show REST API Payloads", value=False)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "last_request" not in st.session_state:
        st.session_state.last_request = None
    if "last_response_raw" not in st.session_state:
        st.session_state.last_response_raw = None

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tables"):
                for t in msg["tables"]:
                    if t.get("title"):
                        st.caption(t["title"])
                    st.dataframe(pd.DataFrame(t["data"], columns=t["columns"]), use_container_width=True)
            if msg.get("charts"):
                for c in msg["charts"]:
                    st.vega_lite_chart(c, use_container_width=True)

    # Starter prompts
    if not st.session_state.chat_messages:
        st.markdown("**Try one of these:**")
        prompt_cols = st.columns(3)
        starters = [
            "What was last month's revenue by region?",
            "Show VPP battery trend for the last week",
            "Top 5 products by revenue this quarter",
        ]
        for i, starter in enumerate(starters):
            if prompt_cols[i].button(starter, key=f"starter_{i}"):
                st.session_state["_pending_prompt"] = starter
                st.rerun()

    pending = st.session_state.pop("_pending_prompt", None)
    prompt = st.chat_input("Ask the EPOWER Agent...")
    user_input = pending or prompt

    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        api_messages = [
            {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
            for m in st.session_state.chat_messages
            if m["role"] == "user"
        ]

        request_body = {"messages": api_messages, "stream": True}
        st.session_state.last_request = {
            "method": "POST",
            "url": AGENT_URL.split(".com")[-1],
            "body": request_body,
        }

        with st.chat_message("assistant"):
            try:
                token = get_token()
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                    "X-Snowflake-Authorization-Token-Type": "OAUTH",
                    "Accept": "text/event-stream",
                }
                response = requests.post(AGENT_URL, headers=headers, json=request_body, stream=True)
                response.raise_for_status()

                collected_text = []
                collected_tables = []
                collected_charts = []
                raw_events = []
                text_placeholder = st.empty()

                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload.strip() == "[DONE]":
                        break
                    try:
                        event = json.loads(payload)
                        raw_events.append(event)
                    except json.JSONDecodeError:
                        continue

                    for item in event.get("data", {}).get("choices", [{}]):
                        delta = item.get("delta", {})
                        for content_item in delta.get("content", []):
                            ctype = content_item.get("type", "")
                            if ctype == "text":
                                collected_text.append(content_item.get("text", ""))
                                text_placeholder.markdown("".join(collected_text))
                            elif ctype == "table":
                                table = content_item.get("table", {})
                                rs = table.get("result_set", {})
                                meta = rs.get("resultSetMetaData", {})
                                cols = [r["name"] for r in meta.get("rowType", [])]
                                data = rs.get("data", [])
                                if cols and data:
                                    collected_tables.append({"title": table.get("title", ""), "columns": cols, "data": data})
                            elif ctype == "chart":
                                spec = content_item.get("chart", {}).get("chart_spec", "")
                                if spec:
                                    try:
                                        collected_charts.append(json.loads(spec))
                                    except json.JSONDecodeError:
                                        pass

                final_text = "".join(collected_text) or "Done."
                text_placeholder.markdown(final_text)

                for t in collected_tables:
                    if t.get("title"):
                        st.caption(t["title"])
                    st.dataframe(pd.DataFrame(t["data"], columns=t["columns"]), use_container_width=True)
                for c in collected_charts:
                    st.vega_lite_chart(c, use_container_width=True)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": final_text,
                    "tables": collected_tables,
                    "charts": collected_charts,
                })
                st.session_state.last_response_raw = raw_events

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                st.session_state.last_response_raw = {"error": str(e)}

    # REST Payload Viewer
    if show_payload and st.session_state.last_request:
        st.divider()
        with st.expander("REST API Request", expanded=False):
            st.code(json.dumps(st.session_state.last_request, indent=2, default=str), language="json")
        with st.expander("REST API Response (raw SSE events)", expanded=False):
            resp_json = json.dumps(st.session_state.last_response_raw, indent=2, default=str)
            st.markdown(
                f'<div style="max-height:400px;overflow-y:auto;background:#f8f9fa;padding:12px;border-radius:6px;"><pre><code>{resp_json}</code></pre></div>',
                unsafe_allow_html=True,
            )
