# EPOWER Assistant — Streamlit Workspace App

Interactive dashboard and AI chat interface for the EPOWER Energy Intelligence Demo.
Demonstrates the **Cortex Agent REST API** with streaming responses inside a Streamlit container-runtime app.

## Features

| Tab | Description |
|-----|-------------|
| **Dashboard** | Sales KPIs, monthly revenue trends, product category breakdown, VPP fleet status (solar/battery/grid), and day-ahead electricity prices |
| **Agent Chat** | Natural-language chat with the EPOWER Agent via streaming SSE. Supports text, tables, and chart responses. Optional REST payload viewer for inspecting request/response bodies |

## Prerequisites

Run the `hol-main/epower_hol_main.ipynb` notebook first. This app depends on:

- `EPOWER_DEMO.EPOWER_GOLD.SALES_FACT`
- `EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM` / `PRODUCT_CATEGORY_DIM` / `REGION_DIM`
- `EPOWER_DEMO.EPOWER_GOLD.MART_VPP_CAPACITY_HOURLY`
- `EPOWER_DEMO.EPOWER_GOLD.MART_DAY_AHEAD_PRICES`
- `EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT`

## Setup (Snowsight Workspace)

1. Open your workspace in Snowsight
2. Click **+ Add new** → **Streamlit app**
3. Select **Run on container** in the dialog
4. Set **Compute pool**: `SYSTEM_COMPUTE_POOL_CPU`
5. Set **Query warehouse**: `EPOWER_COMPUTE`
6. Replace the generated starter files with the contents of this folder:
   - `streamlit_app.py` — main application code
   - `.streamlit/config.toml` — theme configuration
   - `snowflake.yml` — deployment settings
7. **Delete** the auto-generated `pyproject.toml` (not needed; the container base image includes all required packages)
8. Click **Run**

The first start takes 1-2 minutes while the container initializes.

## Runtime Configuration

| Setting | Value |
|---------|-------|
| Runtime | `SYSTEM$ST_CONTAINER_RUNTIME_PY3_11` |
| Compute pool | `SYSTEM_COMPUTE_POOL_CPU` |
| Query warehouse | `EPOWER_COMPUTE` |
| Python | 3.11 |
| Dependencies | None (base image provides streamlit, requests, pandas, snowflake-snowpark-python) |

## Architecture

```
Browser → Streamlit Container (SPCS)
              │
              ├── SQL queries → EPOWER_COMPUTE warehouse → EPOWER_GOLD tables
              │
              └── REST API (SSE) → Cortex Agent → Semantic Views / Cortex Search
                                     └── EPOWER_COMPUTE warehouse (execution_environment)
```

The app authenticates to the Agent REST API using the container's session token (`/snowflake/session/token`) with OAuth bearer authentication.

## File Structure

```
hol-module4/
├── streamlit_app.py          # Main app (dashboard + chat)
├── snowflake.yml             # Container runtime deployment config
├── .streamlit/
│   └── config.toml           # Theme (EPOWER blue branding)
└── README.md                 # This file
```

## Deploying to Other Users

After testing, click **Deploy** in the workspace toolbar to publish the app as a STREAMLIT object. In the deploy dialog, add roles that should have access (e.g., `EPOWER_ROLE`).
