# Module 2: Snowflake Postgres — "Mein EPOWER" Customer Portal

## What This Module Does

Extends the EPOWER demo with a **Snowflake Postgres** instance backing a customer self-service portal. 20,000 customers manage meter readings, tariff switches, service requests, and VPP enrollments through a standard web application stack (React + REST API + PostgreSQL).

The key demo story: **operational portal data flows into Snowflake for analytics — with zero middleware.**

## Architecture

```
Portal (Web App) → Snowflake Postgres (OLTP)
                        │
                   portal_activity_log (append-only, denormalized)
                        │
                   pg_incremental (1-min sync)
                        ▼
                   Iceberg table (pg_lake managed)
                        │
                   Catalog Integration (auto-refresh 30s)
                        ▼
                   Snowflake (EPOWER_BRONZE.PORTAL_ACTIVITY_LOG)
                        │
                   MART_PORTAL_ENGAGEMENT → PORTAL_SEMANTIC_VIEW → EPOWER AGENT
```

## Why Postgres (Not Snowflake) for the Portal?

The portal needs sub-second CRUD, row-level locking, transaction semantics, and concurrent session management — all OLTP patterns that PostgreSQL excels at. Snowflake is the analytical layer, not the transactional backend.

## Why pg_lake (Not Kafka)?

In a traditional setup: Postgres → Kafka Connect → Kafka → Snowpipe Streaming → Snowflake.
With pg_lake: **Postgres → Iceberg → Snowflake.** Zero additional infrastructure.

pg_lake eliminates Kafka as middleware *for the Postgres-to-Snowflake path specifically*. Kafka is still the right choice when multiple consumers need the same events, you need replay capability, or you're at massive scale. For the "one OLTP source → one analytical destination" pattern, pg_lake is simpler.

## Portal Activity Log Schema

| Column | Type | Meaning |
|--------|------|---------|
| `activity_id` | BIGSERIAL | Auto-increment PK |
| `customer_key` | INT | FK to portal_users / links to EPOWER CUSTOMER_DIM |
| `event_time` | TIMESTAMPTZ | When the action occurred |
| `event_type` | TEXT | `LOGIN`, `METER_READING`, `TARIFF_CHANGE`, `SERVICE_REQUEST` |
| `event_detail` | JSONB | Action-specific payload (meter type, kWh, requested product, etc.) |
| `city` | TEXT | Customer's city (denormalized) |
| `region` | TEXT | North / South / East / West (denormalized) |
| `customer_type` | TEXT | Privatkunde / Kleingewerbe / Gewerbekunde (denormalized) |

Append-only, denormalized — ideal for Iceberg replication. No joins needed at query time.

## Snowflake Features Introduced

| Feature | Role in This Module |
|---------|-------------------|
| **Snowflake Postgres** | Fully managed PostgreSQL — portal transactional backend |
| **pg_lake** | Native Iceberg table support in Postgres |
| **pg_incremental** | Exactly-once incremental sync (heap → Iceberg, every 1 min) |
| **Catalog Integration** | Snowflake reads Postgres-managed Iceberg catalog |
| **Auto-Refresh** | Polls Iceberg catalog every 30s for new snapshots |
| **Semantic View** | Portal engagement metrics queryable in natural language |

## Files

| File | Purpose |
|------|---------|
| `hol-module2.ipynb` | Snowsight notebook — provisions Postgres, sets up catalog integration, creates analytics model + semantic view |
| `portal_postgres_setup.sql` | Schema, indexes, pg_lake extensions, Iceberg mirror table, pg_incremental pipeline |
| `portal_seed_data.sql` | Pre-generated INSERT statements for 20K users + 60 days of activity (timestamps use `now() - interval` — always relative) |

## Quick Start

1. Run Module 1 (`hol/epower_hol.ipynb`) first
2. Open `hol-module2.ipynb` in Snowsight and run through Sections 1-3
3. In your Postgres client:
   ```bash
   psql service=my_epower_portal -f portal_postgres_setup.sql
   psql service=my_epower_portal -f portal_seed_data.sql
   ```
4. Wait ~2 minutes for Iceberg sync, then continue the notebook (Sections 5-8)

**Runtime:** ~15 minutes
