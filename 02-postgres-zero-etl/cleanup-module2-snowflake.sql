-- ========================================================================
-- Module 2 Cleanup: Snowflake Side
-- Run this AFTER the Postgres cleanup (cleanup-module2-postgres.sql).
-- Requires ACCOUNTADMIN role.
-- ========================================================================

USE ROLE ACCOUNTADMIN;

-- Drop Iceberg table (Snowflake side)
DROP ICEBERG TABLE IF EXISTS EPOWER_DEMO.EPOWER_BRONZE.PORTAL_ACTIVITY_LOG;

-- Drop analytics view
DROP VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.MART_PORTAL_ENGAGEMENT;

-- Drop semantic view
DROP SEMANTIC VIEW IF EXISTS EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEMANTIC_VIEW;

-- Drop seed data stage
DROP STAGE IF EXISTS EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEED_STAGE;

-- Drop catalog integration
DROP CATALOG INTEGRATION IF EXISTS PORTAL_POSTGRES_CATALOG;

-- Drop network objects
DROP NETWORK POLICY IF EXISTS EPOWER_PG_POLICY;
DROP NETWORK RULE IF EXISTS EPOWER_PG_INGRESS;

-- Drop Postgres instance (this is irreversible)
DROP POSTGRES INSTANCE IF EXISTS MY_EPOWER_PORTAL;

-- Recreate the EPOWER Agent WITHOUT the portal_analyst tool
-- (restores Module 1 agent definition)
USE ROLE EPOWER_ROLE;
USE WAREHOUSE EPOWER_COMPUTE;

CREATE OR REPLACE AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT
WITH PROFILE='{ "display_name": "EPOWER AGENT" }'
FROM SPECIFICATION $$
models:
  orchestration: auto
instructions:
  response: |
    You are a data analyst for EPOWER Energie Deutschland.
    CRITICAL LANGUAGE RULE: You MUST always respond in the SAME language as the user's question.
    DATA ACCESS: Energy sales, billing/consumption, service tickets, HR data, day-ahead electricity market prices, VPP IoT telemetry, and documents.
  orchestration: |
    TOOL SELECTION:
    - Document questions → energy_docs_search, product_docs_search, service_docs_search
    - Consumption + products → customer_energy_analyst
    - Sales/contracts → energy_sales_analyst
    - Billing → billing_analyst
    - Service tickets → service_analyst
    - HR data → hr_analyst
    - Electricity market prices, day-ahead → epulse_prices_analyst
    - VPP telemetry, solar yield, battery SOC, grid import/export → vpp_telemetry_analyst
tools:
  - tool_spec: {type: cortex_analyst_text_to_sql, name: energy_sales_analyst, description: "Contracts, products, sales, revenue"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: billing_analyst, description: "Consumption, billing, payments"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: customer_energy_analyst, description: "Consumption by product ownership"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: service_analyst, description: "Service tickets, complaints"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: hr_analyst, description: "HR data, salaries"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: market_prices_analyst, description: "Day-ahead electricity market prices"}
  - tool_spec: {type: cortex_analyst_text_to_sql, name: vpp_telemetry_analyst, description: "VPP IoT telemetry: solar yield, battery SOC, grid import/export"}
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
  energy_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_ENERGY_DOCS", max_results: 5}
  product_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_PRODUCT_DOCS", max_results: 5}
  service_docs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_DOCS", max_results: 5}
  service_logs_search: {search_service: "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_LOGS", max_results: 5}
$$;

SELECT 'Module 2 Snowflake cleanup completed. Agent restored to Module 1 state.' AS status;
