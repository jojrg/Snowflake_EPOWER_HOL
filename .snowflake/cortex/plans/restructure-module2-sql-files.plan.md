---
name: "restructure-module2-sql-files"
created: "2026-05-12T13:14:41.947Z"
status: pending
---

# Plan: Restructure Module 2 — Separate Snowflake Notebook from Postgres SQL

## Overview

Split Module 2 into:

- **Notebook (Snowflake SQL + Python)**: Instance creation, network policy, .sql file generation, catalog integration, Iceberg tables, analytics models, semantic view, agent
- **Standalone .sql files (Postgres)**: Schema DDL, data seed, pg\_lake setup, pg\_incremental pipeline
- **Markdown guide cells**: psql installation, connection instructions, step-by-step PG client workflow

## Files to Create

### 1. `hol/portal_postgres_setup.sql`

Complete Postgres SQL for the Portal use case — runnable via `psql -f`:

- Schema (5 tables + indexes)
- pg\_lake extensions
- Iceberg table creation
- pg\_incremental pipeline
- Live demo helper (INSERT for simulating real-time activity)

### 2. `hol/dispatch_postgres_setup.sql`

Complete Postgres SQL for the VPP Dispatch use case:

- Schema (4 tables + indexes)
- pg\_lake extensions
- Iceberg table creation
- pg\_incremental pipeline
- Live demo helper

### 3. Rewrite `hol/hol-module2.ipynb`

#### Portal Section (cells 0–34)

| Cell | Type | Content                                                                                                                                                                    |
| ---- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0    | md   | Module 2 intro (keep existing)                                                                                                                                             |
| 1    | md   | §1 Prerequisites                                                                                                                                                           |
| 2    | code | Session init                                                                                                                                                               |
| 3    | code | %%sql — USE ROLE/WAREHOUSE/DATABASE + prerequisites check                                                                                                                  |
| 4    | md   | §2 Create Snowflake Postgres Instance                                                                                                                                      |
| 5    | code | %%sql — CREATE POSTGRES INSTANCE MY\_EPOWER\_PORTAL                                                                                                                        |
| 6    | code | %%sql — Network policy + DESCRIBE                                                                                                                                          |
| 7    | md   | **NEW: psql Setup Guide** — install psql (brew), `~/.pg_service.conf`, connection string, how to run the .sql file                                                         |
| 8    | md   | §3 Portal Schema + Data (Postgres Client) — step-by-step guide with the full SQL inline in fenced code blocks, plus instruction to run `psql -f portal_postgres_setup.sql` |
| 9    | code | Python cell that generates `portal_seed_data.sql` by reading CUSTOMER\_DIM and PRODUCT\_DIM from Snowflake                                                                 |
| 10   | md   | Instructions to run the generated seed file via psql                                                                                                                       |
| 11   | md   | §4 pg\_lake + Iceberg Sync (Postgres Client) — SQL shown inline, or "already included in portal\_postgres\_setup.sql"                                                      |
| 12   | md   | §5 Verify in Postgres (optional) — show SELECT count queries                                                                                                               |
| 13   | md   | §6 Snowflake Catalog Integration                                                                                                                                           |
| 14   | code | %%sql — CREATE CATALOG INTEGRATION                                                                                                                                         |
| 15   | code | %%sql — CREATE ICEBERG TABLE + AUTO\_REFRESH                                                                                                                               |
| 16   | code | %%sql — Verify (SELECT from Iceberg table)                                                                                                                                 |
| 17   | md   | §7 Analytics Model                                                                                                                                                         |
| 18   | code | %%sql — CREATE TABLE MART\_PORTAL\_ENGAGEMENT                                                                                                                              |
| 19   | code | %%sql — Verify                                                                                                                                                             |
| 20   | md   | §8 Semantic View + Agent Update                                                                                                                                            |
| 21   | code | %%sql — CREATE SEMANTIC VIEW                                                                                                                                               |
| 22   | code | %%sql — CREATE AGENT                                                                                                                                                       |
| 23   | md   | §9 Verification & Demo                                                                                                                                                     |
| 24   | md   | Live Demo: Real-Time Sync — instructions to INSERT in PG client                                                                                                            |
| 25   | code | %%sql — Verify in Snowflake                                                                                                                                                |

#### VPP Section (cells 26+)

Same pattern as above but for EPULSE\_DISPATCH.

### Key Design Decisions

**Data generation approach**: A notebook Python cell reads `CUSTOMER_DIM`, `PRODUCT_DIM`, `EPULSE_DEVICES` from Snowflake and writes two files:

- `hol/portal_seed_data.sql` — INSERT statements for portal\_users, meter\_readings, tariff\_orders, service\_requests, portal\_activity\_log
- `hol/dispatch_seed_data.sql` — INSERT statements for devices, dispatch\_commands, command\_execution\_log, dispatch\_alerts

These generated files are then run via `psql -f`.

**Static .sql files** (`portal_postgres_setup.sql`, `dispatch_postgres_setup.sql`) contain:

- Schema DDL (always the same)
- pg\_lake + pg\_incremental setup (always the same)
- Verification queries
- Live demo INSERT helpers

**psql guide** includes:

- `brew install libpq` (macOS)
- `~/.pg_service.conf` setup to avoid long connection strings
- `~/.pgpass` for password storage
- One-liner: `psql -f portal_postgres_setup.sql "host=<host> port=5432 dbname=postgres user=snowflake_admin sslmode=require"`
- Alternative: `psql service=my_epower_portal -f portal_postgres_setup.sql`

## Cells to Remove

All psycopg2 Python cells (cells 3, 8, 10, 13, 15, 16, 18, 19, 20, 33 in current numbering) plus the data generation Python cells (12, 14) will be replaced with:

- One Python cell per use case that generates the seed .sql
- Markdown cells with the PG instructions

## Summary of Changes

| Current                               | New                                                  |
| ------------------------------------- | ---------------------------------------------------- |
| psycopg2 helper cell                  | Removed                                              |
| Python schema creation                | Markdown with SQL + standalone .sql file             |
| Python data generation + bulk insert  | Python generates .sql file + markdown "run via psql" |
| Python pg\_lake/pg\_incremental setup | Included in standalone .sql file + markdown          |
| Python live demo INSERT               | Markdown instructions + SQL in .sql file             |
| %%sql Snowflake cells                 | Kept as-is                                           |
