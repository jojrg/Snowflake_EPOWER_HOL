# Plan: Fix Iceberg Sync Pipeline (Module 2)

## Problem Analysis

There are **three issues** with the current setup:

### Issue 1: Ordering / Chicken-and-Egg Problem

In `portal_postgres_setup.sql` (line 126), the pipeline is created with:
```sql
start_time := (SELECT min(event_time) FROM portal_activity_log),
```

But when this runs, `portal_activity_log` is **empty** — the seed data hasn't been loaded yet. This means `start_time` evaluates to `NULL`, which likely causes the pipeline to either fail silently or never process any data.

The intended execution order is:
1. `portal_postgres_setup.sql` — creates schema + extensions + iceberg table + pipeline
2. `portal_seed_data.sql` — inserts data

But the pipeline's `start_time` depends on data that doesn't exist yet at step 1.

### Issue 2: The separate `postal_setup_icebergsync.sql` file

This file exists as a "fix attempt" — it drops and recreates the pipeline with `start_time := now()`. But:
- Its name is confusing (`postal` vs `portal`)
- It doesn't solve the backfill problem — using `now()` means all historical seed data (60 days worth) is **never** synced to iceberg
- It's unclear when users should run it (before or after seed?)
- It duplicates logic from the main setup script

### Issue 3: Understanding `$1` and `$2`

These are **pg_incremental's time window parameters** — they are NOT user-supplied. When `pg_incremental` fires the pipeline every 1 minute, it automatically substitutes:
- `$1` = start of the current time window (e.g., `2026-05-18 10:00:00`)
- `$2` = end of the current time window (e.g., `2026-05-18 10:01:00`)

The pipeline processes data in 1-minute chunks starting from `start_time`, catching up minute-by-minute until it reaches the present. This is documented in the pg_incremental extension's behavior — it's similar to how `pg_cron` schedules work but with exactly-once semantics and time-bounded windows.

## Proposed Solution

**Strategy: Two-phase approach with explicit historical backfill**

### Revised `portal_postgres_setup.sql`
- Keep schema, extensions, and iceberg table creation as-is
- **Remove** the `create_time_interval_pipeline` call from this file (since it depends on data existing)
- Add a comment explaining the pipeline is created after seeding

### Revised `portal_seed_data.sql`
At the **end** of the seed script (after all INSERTs + COMMIT), add:

```sql
-- Phase 1: Bulk-copy all historical data directly to iceberg
INSERT INTO portal_activity_log_iceberg
SELECT activity_id, customer_key, event_time, event_type,
       event_detail, city, region, customer_type
FROM portal_activity_log;

-- Phase 2: Create the incremental pipeline for NEW data going forward
SELECT incremental.create_time_interval_pipeline(
    pipeline_name      := 'sync_portal_activity_to_iceberg',
    time_interval      := '1 minute',
    source_table_name  := 'portal_activity_log',
    start_time         := now(),
    command            := $inner$
        INSERT INTO portal_activity_log_iceberg
        SELECT activity_id, customer_key, event_time, event_type,
               event_detail, city, region, customer_type
        FROM portal_activity_log
        WHERE event_time >= $1 AND event_time < $2
    $inner$
);
```

This gives us:
- **Immediate iceberg data**: The bulk INSERT copies all 60 days of historical activity directly
- **Ongoing sync**: The pipeline starts from `now()` and picks up only new inserts going forward
- **No gap**: Since `start_time = now()` and the bulk copy already handled everything before now, nothing is missed

### Delete `postal_setup_icebergsync.sql`
This file becomes unnecessary since the pipeline creation is now properly integrated into the seed script.

### Update notebook markdown (Section 4)
Clarify the execution steps:
```
Step 1: psql -f portal_postgres_setup.sql   (schema + extensions + iceberg table)
Step 2: psql -f portal_seed_data.sql         (data + bulk iceberg copy + pipeline creation)
Step 3: Verify immediately — both heap and iceberg should have matching counts
```

## File Changes Summary

| File | Action |
|------|--------|
| `portal_postgres_setup.sql` | Remove Section 4 (pipeline creation), add comment pointing to seed script |
| `portal_seed_data.sql` | Add bulk INSERT + pipeline creation at the end |
| `postal_setup_icebergsync.sql` | **Delete** |
| `hol-module2.ipynb` | Update Section 4 markdown to reflect new workflow |
