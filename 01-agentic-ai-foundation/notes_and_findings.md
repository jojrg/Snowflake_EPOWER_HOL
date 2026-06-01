# HOL Notes & Findings

## 2026-05-12: Stage File Download — Presigned URL vs GET

**Problem:** Files downloaded from a Snowflake internal stage via **presigned URL** arrive as encrypted binary (AES-256 server-side encryption). They cannot be opened or parsed locally.

**Root cause:** Presigned URLs serve the raw encrypted bytes stored on the cloud provider. The Snowflake client-side decryption layer is bypassed entirely.

**What does NOT work:**
- Presigned URLs (via `GET_PRESIGNED_URL()` or Snowsight "Download" link)
- `snow stage copy @STAGE/file file:///local/path/` — also downloads encrypted bytes despite appearing to succeed (status shows "UPLOADED")

**What works:**
```bash
snow sql -q "GET @EPOWER_DEMO.EPOWER_GOLD.PORTAL_SEED_STAGE/portal_seed_data.sql file:///local/path/" --connection jochen-azdemo25
```
The SQL `GET` command routes through the Snowflake connector, which handles decryption transparently.

**Notebook implication:** If the HOL notebook instructs users to download staged files (e.g., seed data SQL), it must use `GET` via a SQL worksheet or Snow CLI `snow sql -q "GET ..."` — never a presigned URL or `snow stage copy`.

## 2026-05-13: Pre-generate portal_seed_data.sql — Remove Runtime Generation

**Decision:** The Python cell that generated `portal_seed_data.sql` at notebook runtime (querying CUSTOMER_DIM + PRODUCT_DIM from Snowflake, then uploading to a stage for manual download) has been removed from `hol-module2.ipynb`.

**Why:**
- The generation step required a Snowflake session, but the output had to be executed in Postgres — creating a cumbersome stage-upload → GET-download → psql workflow
- The download itself was error-prone (presigned URL encryption issue above)
- All source data (customer_dim.csv, product_dim.csv) is already in the git repo under `demo_data/structured_data/`
- The generated SQL uses `now() - interval 'N days'` for timestamps, so dates are always relative to execution time — no staleness issue

**New approach:**
- `portal_seed_data.sql` is pre-generated and committed to `hol/` in the git repo
- HOL participants just run `psql -f portal_seed_data.sql` directly — no Snowflake dependency for Postgres seeding
- The notebook Section 4 now simply says "both SQL files are in the `hol/` folder"

**Cells removed from hol-module2.ipynb:** 4 cells (empty scratch cell, `select current_role()`, Python generator, trailing "Portal Seed Data" markdown). Cell count: 29 → 25.

## 2026-05-13: Module 2 moved to dedicated subfolder

Module 2 assets moved from `hol/` to `hol-module2/`:
- `hol-module2/hol-module2.ipynb`
- `hol-module2/portal_postgres_setup.sql`
- `hol-module2/portal_seed_data.sql`
- `hol-module2/README-module2.md` (new)
