CREATE OR REPLACE AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT
WITH PROFILE='{ "display_name": "EPOWER AGENT" }'
FROM SPECIFICATION $$
models:
  orchestration: auto
instructions:
  response: |
    You are a data analyst for EPOWER Energie Deutschland.
    CRITICAL LANGUAGE RULE: You MUST always respond in the SAME language as the user's question.
    DATA ACCESS: Energy sales, billing/consumption, service tickets, HR data, day-ahead electricity market prices, VPP IoT telemetry, customer portal engagement, customer health (churn + NPS), and documents.
  orchestration: |
    TOOL SELECTION:
    - Document questions -> energy_docs_search, product_docs_search, service_docs_search
    - Consumption + products -> customer_energy_analyst
    - Sales/contracts -> energy_sales_analyst
    - Billing -> billing_analyst
    - Service tickets -> service_analyst
    - HR data -> hr_analyst
    - Electricity market prices, day-ahead -> market_prices_analyst
    - VPP telemetry, solar yield, battery SOC, grid import/export -> vpp_telemetry_analyst
    - Portal activity, digital engagement -> portal_analyst
    - Customer churn, cancellations, NPS, satisfaction -> customer_health_analyst
tools:
  - tool_spec: {type: cortex_analyst_text_to_sql, name: energy_sales_analyst, description: "Contracts, products, sales, revenue"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: billing_analyst, description: "Consumption, billing, payments"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: customer_energy_analyst, description: "Consumption by product ownership"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: service_analyst, description: "Service tickets, complaints"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: hr_analyst, description: "HR data, salaries"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: market_prices_analyst, description: "Day-ahead electricity market prices"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: vpp_telemetry_analyst, description: "VPP IoT telemetry: solar yield, battery SOC, grid import/export"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: portal_analyst, description: "Customer portal engagement: logins, meter readings, tariff changes, service requests."}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: customer_health_analyst, description: "Customer churn analysis, contract cancellations, NPS surveys, customer satisfaction, retention metrics."}
  - tool_spec: {type: cortex_search, name: energy_docs_search, description: "Energy policies, terms"}
  - tool_spec: {type: cortex_search, name: product_docs_search, description: "Product documentation"}
  - tool_spec: {type: cortex_search, name: service_docs_search, description: "Service handbook"}
  - tool_spec: {type: cortex_search, name: service_logs_search, description: "Historical tickets"}
  - tool_spec: {type: data_to_chart, name: data_to_chart, description: "Generate visualizations"}
tool_resources:
  energy_sales_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.ENERGY_SALES_SEMANTIC_VIEW"}
  billing_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.BILLING_SEMANTIC_VIEW"}
  customer_energy_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_ENERGY_SEMANTIC_VIEW"}
  service_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.SERVICE_SEMANTIC_VIEW"}
  hr_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.HR_SEMANTIC_VIEW"}
  market_prices_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.MARKET_PRICES_SEMANTIC_VIEW"}
  vpp_telemetry_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.EPULSE_VPP_SEMANTIC_VIEW"}
  portal_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEMANTIC_VIEW"}
  customer_health_analyst: {semantic_view: "EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_HEALTH_SEMANTIC_VIEW"}
  energy_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_ENERGY_DOCS", max_results: 5}
  product_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_PRODUCT_DOCS", max_results: 5}
  service_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_DOCS", max_results: 5}
  service_logs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_LOGS", max_results: 5}
$$;
