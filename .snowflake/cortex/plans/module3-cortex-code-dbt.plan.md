# Plan: Module 3 — Cortex Code dbt Onboarding Demo

## Overview

Build a new HOL module that demonstrates how Cortex Code (CoCo) in Snowsight accelerates dbt development. The module introduces two new data sources (contract cancellations + customer NPS surveys), loads them via a guided notebook, then challenges the user to extend the existing `epower_dbt` project using CoCo.

## Deliverables

| # | Deliverable | Path |
|---|------------|------|
| 1 | Data generator script | `generators/generate_module3_data.py` |
| 2 | Contract cancellations CSV | `demo_data/structured_data/contract_cancellations.csv` |
| 3 | Customer surveys CSV | `demo_data/structured_data/customer_surveys.csv` |
| 4 | Module 3 notebook | `hol-module3/hol-module3.ipynb` |
| 5 | Reference dbt models | `hol-module3/reference/` (expected CoCo output) |
| 6 | Cleanup script | `hol-module3/cleanup-module3.sql` |

---

## Task 1: Data Generator Script

### `generators/generate_module3_data.py`

**contract_cancellations.csv** (~2,500 rows)

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `cancellation_id` | INT | PK, sequential 1-2500 | 1..2500 |
| `customer_key` | INT | FK to customer_dim | 1..20000 (random sample) |
| `product_key` | INT | FK to product_dim | 1..15 |
| `cancellation_date` | DATE | When cancelled | 2023-01-01 to 2025-12-31 |
| `reason` | VARCHAR | German cancellation reason | Umzug, Preiserhöhung, Wettbewerber, Unzufriedenheit, Nicht mehr benötigt, Sonstiges |
| `channel` | VARCHAR | How they cancelled | Email, Telefon, App, Brief |
| `retention_offered` | BOOLEAN | Was retention attempted? | TRUE/FALSE (~60% TRUE) |
| `retention_accepted` | BOOLEAN | Did they stay? | TRUE/FALSE (~25% of offered) |

Design choices:
- ~12.5% churn rate (2,500 / 20,000) — realistic for German energy retail
- Higher churn for basic tariffs (Strom Basis, Gas Basis) — price-sensitive
- Lower churn for hardware (Solar, Wärmepumpe) — high switching cost
- Seasonal pattern: more cancellations in Q1 (after winter billing shock)
- "Umzug" (relocation) is #1 reason (~30%) — matches real market data

**customer_surveys.csv** (~5,000 rows)

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `survey_id` | INT | PK, sequential 1-5000 | 1..5000 |
| `customer_key` | INT | FK to customer_dim | 1..20000 (random sample, can repeat) |
| `survey_date` | DATE | When completed | 2024-01-01 to 2025-12-31 |
| `nps_score` | INT | Net Promoter Score | 0-10 |
| `category` | VARCHAR | Survey topic | Gesamtzufriedenheit, Kundenservice, Produkt, Installation, Preis-Leistung, App & Digital |
| `comment` | VARCHAR | Optional German feedback | Short German comments (nullable ~40%) |

Design choices:
- NPS distribution: ~20% detractors (0-6), ~30% passives (7-8), ~50% promoters (9-10) — slightly optimistic for energy retail
- Solar/battery customers have higher NPS (product satisfaction)
- Service ticket history correlates: customers with negative service sentiment have lower NPS
- Comments are short German phrases matching the category

### Consistency with existing data
- Uses same `customer_key` range (1-20000) from `customer_dim`
- Uses same `product_key` range (1-15) from `product_dim`
- Uses same German-language conventions (Umzug, not Relocation)
- Date ranges overlap with existing data (2023-2025)
- Seeds with `random.seed(42)` for reproducibility

---

## Task 2: Generate CSV Files

Run the script to produce the two CSV files in `demo_data/structured_data/`.

---

## Task 3: Module 3 Notebook

### `hol-module3/hol-module3.ipynb`

Structure follows the same patterns as Module 1 and Module 2:

```
# Module 3: Cortex Code — Accelerating dbt Development

## Title Cell
- Business case: "New data sources arrive constantly. How fast can you extend your analytics pipeline?"
- Architecture diagram showing new sources flowing into existing dbt project
- Section overview table
- Runtime: ~15 minutes
- Prerequisites: Module 1 must be deployed

## §1 Prerequisites
- Verify Module 1 objects exist (customer_dim, product_dim, sales_fact)
- Verify dbt project exists (EPOWER_ANALYTICS_PROJECT)
- USE ROLE EPOWER_ROLE; USE WAREHOUSE EPOWER_COMPUTE;

## §2 New Source Tables
- CREATE OR REPLACE TABLE EPOWER_DEMO.EPOWER_GOLD.CONTRACT_CANCELLATIONS (...)
- CREATE OR REPLACE TABLE EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_SURVEYS (...)

## §3 Upload & Ingest
- Python: Upload CSVs to @EPOWER_STAGE
- COPY INTO from stage
- Verify row counts

## §4 Explore the Data
- Quick SQL queries showing what we loaded
- "Which products have the highest cancellation rates?"
- "What's the NPS distribution?"
- These queries help CoCo understand the data context when the user describes the task

## §5 The CoCo Challenge ★ (Key Section — Markdown Only)
This is the core of the module — a guided markdown section explaining:

### What to do
"Open Cortex Code in your Snowsight workspace. Navigate to the epower_dbt/ project.
Ask CoCo to extend the pipeline with the new sources."

### Suggested Prompts
1. "I have two new source tables in EPOWER_GOLD: CONTRACT_CANCELLATIONS and 
   CUSTOMER_SURVEYS. Extend the epower_dbt project to include these sources.
   Create staging models that join with customer_dim and product_dim, 
   and mart models for churn analysis and NPS analysis. 
   Follow the existing project conventions."

2. (Bonus) "Create a combined mart_customer_health model that joins churn 
   and NPS data with customer dimensions to create a customer health score."

### What CoCo Should Generate
- Updated sources.yml (add contract_cancellations, customer_surveys)
- New model folder: models/customer_analytics/
  - staging/stg_cancellations.sql
  - staging/stg_surveys.sql
  - staging/schema.yml
  - marts/mart_customer_churn.sql
  - marts/mart_nps_analysis.sql
  - marts/mart_customer_health.sql (bonus)
  - marts/schema.yml
- Updated dbt_project.yml (add customer_analytics section)

### Run & Test
"After CoCo generates the models, click Run and Test in the Snowsight dbt UI."

## §6 Verification
- SQL queries to validate the dbt models exist and have data
- SELECT COUNT(*) from the new Silver/Gold tables
- Sample query: "Top 5 products by churn rate"
- Sample query: "NPS by region"

## §7 Bonus: Semantic View + Agent Update
- CREATE SEMANTIC VIEW for customer health analytics
- Update EPOWER_AGENT with new tool (customer_health_analyst)
- Demo questions for the agent
```

### Notebook Style Conventions (matching existing modules)
- `%%sql` magic for SQL cells
- `language: python` in cell metadata
- `codeCollapsed: true` for markdown sections
- `CREATE OR REPLACE` for idempotent DDL
- Fully qualified names: `EPOWER_DEMO.EPOWER_GOLD.TABLE_NAME`
- German domain vocabulary in comments
- Tables with `| Column | Description |` format in markdown

---

## Task 4: Reference dbt Models

Create `hol-module3/reference/` with the expected dbt output as a validation reference. This is NOT deployed — it's what CoCo should approximately generate.

```
hol-module3/reference/
├── sources_update.yml          # Additions to sources.yml
├── dbt_project_update.yml      # Additions to dbt_project.yml
├── models/
│   └── customer_analytics/
│       ├── staging/
│       │   ├── stg_cancellations.sql
│       │   ├── stg_surveys.sql
│       │   └── schema.yml
│       └── marts/
│           ├── mart_customer_churn.sql
│           ├── mart_nps_analysis.sql
│           ├── mart_customer_health.sql
│           └── schema.yml
```

### Reference Model Designs

**stg_cancellations.sql** — Join cancellations with customer_dim and product_dim:
- Customer name, type, city, region
- Product name, category
- Cancellation reason, channel, retention flags

**stg_surveys.sql** — Join surveys with customer_dim:
- Customer name, type, city, region
- NPS score, category, comment
- NPS segment (Detractor/Passive/Promoter)

**mart_customer_churn.sql** — Monthly churn metrics:
- Churn rate by product category, region, month
- Cancellation reasons distribution
- Retention offer success rate
- Avg time-to-cancel from contract date

**mart_nps_analysis.sql** — NPS aggregation:
- NPS by region, customer type, survey category
- Promoter/Passive/Detractor distribution
- Monthly NPS trend

**mart_customer_health.sql** — Combined health score:
- Join customer_dim with churn flag + NPS score
- Customer health segment (At Risk, Neutral, Healthy, Champion)

---

## Task 5: Cleanup Script

`hol-module3/cleanup-module3.sql`:
- DROP TABLE contract_cancellations
- DROP TABLE customer_surveys
- DROP tables created by dbt (stg_*, mart_customer_*, mart_nps_*)
- Note: Does NOT drop Module 1 objects

---

## Task 6: Update Memory

Record completion status and file paths.

---

## Key Design Decisions

1. **New data goes to EPOWER_GOLD** (not EPOWER_BRONZE) — matches how other domain tables (sales_fact, billing_history, etc.) are loaded directly into Gold in Module 1. The dbt staging models then re-read from Gold and enrich/join, outputting to Silver/Gold.

2. **Two small tables** — keeps the demo snappy. CoCo generates ~5 models, which takes 1-2 minutes. Enough to impress, not so much it's boring.

3. **Reference files as fallback** — if CoCo doesn't nail it perfectly, the presenter has reference files to compare against or copy from.

4. **§5 is markdown-only** — the notebook intentionally does NOT execute the dbt models. That's the user's job in CoCo. This is the "handoff" moment.

5. **German-language data** — cancellation reasons and NPS comments are in German, consistent with the rest of the EPOWER demo.
