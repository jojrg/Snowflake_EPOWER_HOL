# Plan: Realistic CoCo Prompts for Module 3

## Problem

The current §5 dbt prompt is too prescriptive — it specifies exact column names, join keys, folder structures, model names, and aggregation logic. A real user wouldn't have this level of detail upfront. Similarly, §7 (Semantic View + Agent) uses hardcoded SQL that will break if CoCo names models differently than expected.

## Design Principles

1. **Prompts should be business-level** — state the *what* and *why*, not the *how*
2. **Verification should be discovery-based** — check what CoCo actually built, not hardcoded names
3. **Reference folder = safety net** — all expected SQL lives in `reference/` for fallback
4. **Progressive disclosure** — prompt 1 (dbt) → prompt 2 (semantic view) → prompt 3 (agent update)

## Changes

### Task 1: Rewrite §5 Step 2 — Realistic dbt Prompt (Cell 19)

**Current prompt** (26 lines, specifies columns, join keys, folder paths, model names):
```
I have two new source tables... cancellation_id, customer_key, product_key...
Please extend the dbt project by:
- Adding these as sources in sources.yml
- Creating a new models/customer_analytics/ folder...
```

**New prompt** (~5 lines, business-level):
```
We just loaded two new tables into EPOWER_DEMO.EPOWER_BRONZE:

- CONTRACT_CANCELLATIONS — tracks when and why customers cancel contracts
- CUSTOMER_SURVEYS — NPS satisfaction surveys with scores and comments

Explore these tables and the existing dbt project, then extend the pipeline
with appropriate staging models and analytical marts. We want to understand
churn patterns and customer satisfaction across our business.
```

This is realistic: the user knows the table names and their business purpose, but lets CoCo discover the schema, figure out joins, decide on model granularity, etc.

**Also update in the same cell:**
- **Step 3 (Review & Apply):** Replace the exact file table with a general description: "CoCo will typically generate: source definitions, staging models (enriched with dimension context), analytical marts, schema tests, and config updates. Review what it proposes."
- **Step 4 (Run & Test):** Keep as-is (generic enough already)
- **What to Watch For:** Keep mostly as-is, tweak wording slightly to emphasize discovery ("CoCo explores the tables and discovers join keys" instead of "CoCo identifies the correct join keys")

### Task 2: Update §5 Step 3 — Flexible Expectations (Cell 19)

Replace the deterministic file table with a softer guide:

```markdown
Cortex Code will explore the source tables and propose a set of changes.
Typically you should see:

- **Source definitions** — the new tables added to `sources.yml`
- **Staging models** — enriched versions joining with existing dimensions
- **Mart models** — aggregated business metrics (churn analysis, NPS breakdown, potentially a combined view)
- **Schema tests** — data quality assertions (not_null, unique, accepted_values)
- **Config updates** — `dbt_project.yml` updated for the new model paths

> **Presenter tip:** The exact model names and structure may vary —
> that's the point. CoCo reasons about the data and proposes its own design.
> Check the `reference/` folder for one expected solution.
```

### Task 3: Add CoCo Prompts for Semantic View + Agent (Cells 28-31)

**Current state:**
- Cell 28: markdown intro mentioning "You can also ask Cortex Code to generate these for you!"
- Cell 29: 61-line hardcoded `CREATE SEMANTIC VIEW` SQL
- Cell 30: markdown intro for agent update
- Cell 31: 53-line hardcoded `CREATE AGENT` SQL

**New state:**

**Cell 28** — Rewrite as a full CoCo challenge section with two prompts:

```markdown
## 7. Bonus: Extend the AI Layer with CoCo

Now that the new dbt models are materialized, let's use Cortex Code again —
this time to make the data queryable in natural language.

### Step 1: Create a Semantic View

In Cortex Code, prompt:

\```
I've just built new mart tables for customer churn and NPS analysis
in EPOWER_GOLD (the exact names from the dbt run).
Create a Semantic View called CUSTOMER_HEALTH_SEMANTIC_VIEW in
EPOWER_DEMO.EPOWER_GOLD that covers these marts — include relevant
facts, dimensions, and metrics with German synonyms (this is a
German energy company). Look at the existing semantic views in
EPOWER_GOLD for style reference.
\```

Review and execute the generated SQL.

### Step 2: Update the Agent

Then prompt CoCo:

\```
Add the new CUSTOMER_HEALTH_SEMANTIC_VIEW as a tool called
customer_health_analyst to the existing EPOWER_AGENT in
EPOWER_DEMO.EPOWER_GOLD. Preserve all existing tools. You can
inspect the current agent definition with DESCRIBE AGENT.
\```

Review and execute.

> **Fallback:** If CoCo's output needs adjustment, reference SQL is
> available in `hol-module3/reference/`.
```

**Delete cells 29, 30, 31** (the hardcoded SQL) — or convert them to a single collapsed "Reference / Fallback" section. I recommend keeping them but re-labeling as fallback.

**Revised approach:** Rather than deleting, convert cells 29-31 into:
- Cell 29: markdown header "### Fallback: Manual SQL" with note
- Cell 30: keep semantic view SQL (unchanged) — relabeled as reference
- Cell 31: keep agent SQL (unchanged) — relabeled as reference

This way the presenter can skip the CoCo prompts and run the SQL directly if needed.

### Task 4: Make §6 Verification Flexible (Cells 22-27)

**Current cells** hardcode exact table names (`MART_CUSTOMER_CHURN`, `MART_NPS_ANALYSIS`, `MART_CUSTOMER_HEALTH`).

**New approach:**

**Cell 22** (markdown) — update text:
```markdown
## 6. Verification

After Cortex Code has generated the models and you've executed the dbt build,
let's verify what was created.
```

**Cell 23** — Replace with discovery query:
```sql
%%sql
-- Discover new staging models in SILVER
SHOW TABLES IN SCHEMA EPOWER_DEMO.EPOWER_SILVER;
```

**Cell 24** — Replace with discovery query:
```sql
%%sql
-- Discover new mart models in GOLD
SELECT TABLE_NAME, ROW_COUNT, CREATED
FROM EPOWER_DEMO.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'EPOWER_GOLD'
  AND TABLE_NAME ILIKE ANY ('%CHURN%', '%NPS%', '%HEALTH%', '%CANCEL%', '%SURVEY%')
ORDER BY CREATED DESC;
```

**Cell 25** — Keep a sample query but make it dynamic-ish. Change to use a comment noting the user should substitute the actual mart name:
```sql
%%sql
-- Sample the churn/cancellation mart (adjust name if CoCo chose differently)
SELECT * FROM EPOWER_DEMO.EPOWER_GOLD.MART_CUSTOMER_CHURN
LIMIT 10;
```

**Cells 26-27** — Same pattern, add comment about adjusting names.

### Task 5: Add Reference Files

Create two new reference files:
- `hol-module3/reference/semantic_view.sql` — copy of current cell 29 SQL
- `hol-module3/reference/agent_definition.sql` — copy of current cell 31 SQL

### Task 6: Update Summary + Memory

**Cell 33** — Minor wording update to reflect that both dbt AND semantic view/agent were CoCo-driven:

```markdown
| **AI-assisted engineering** | Cortex Code generated dbt models, semantic views, and agent config |
```

Update memory file with changes made.

## Risk Mitigation

- **Reference folder** contains all expected outputs as fallback
- **Verification cells** discover what exists rather than asserting exact names
- **Fallback SQL cells** remain in the notebook (just re-labeled) so presenter can execute them directly
- **Presenter tips** throughout remind that variance is expected and welcome

## Cells Changed Summary

| Cell | Current | New |
|------|---------|-----|
| 19 | Prescriptive CoCo prompt | Realistic business-level prompt + flexible expectations |
| 22 | "verify everything landed correctly" | Softer "verify what was created" |
| 23 | Hardcoded STG row counts | Discovery: SHOW TABLES |
| 24 | Hardcoded MART row counts | Discovery: INFORMATION_SCHEMA query |
| 25-27 | Hardcoded SELECT * | Keep but add "adjust name" comments |
| 28 | Brief intro + "ask CoCo" hint | Full CoCo challenge with 2 prompts |
| 29 | Hardcoded semantic view SQL | Relabeled as "Fallback: Manual SQL" |
| 30 | Agent intro markdown | Merged into fallback section |
| 31 | Hardcoded agent SQL | Kept under fallback label |
| 33 | Summary table | Minor wording update |
