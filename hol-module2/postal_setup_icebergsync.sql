-- Drop the broken pipeline if exists
-- SELECT incremental.drop_pipeline('sync_portal_activity_to_iceberg');

-- Recreate with correct start_time (now, since historical data is already synced)
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







-- ---------------------------------------------------------------------------
-- Section 4: Automated Sync Pipeline (pg_incremental)
-- ---------------------------------------------------------------------------
-- Syncs new portal_activity_log entries to the Iceberg table every 1 minute.
-- Uses pg_incremental for exactly-once, time-interval-based processing.
-- NOTE: Run this AFTER loading the seed data (portal_seed_data.sql),
--       so that start_time picks up the earliest event.

-- SELECT incremental.create_time_interval_pipeline(
--    pipeline_name      := 'sync_portal_activity_to_iceberg',
--    time_interval      := '1 minute',
--    source_table_name  := 'portal_activity_log',
--    start_time         := (SELECT min(event_time) FROM portal_activity_log),
--    command            := $inner$
--        INSERT INTO portal_activity_log_iceberg
--        SELECT activity_id, customer_key, event_time, event_type,
--               event_detail, city, region, customer_type
--        FROM portal_activity_log
--        WHERE event_time >= $1 AND event_time < $2
--    $inner$
-- );

-- ---------------------------------------------------------------------------
-- Section 5: Verification
-- ---------------------------------------------------------------------------

SELECT 'portal_users' AS table_name, count(*) AS rows FROM portal_users
UNION ALL SELECT 'meter_readings', count(*) FROM meter_readings
UNION ALL SELECT 'tariff_orders', count(*) FROM tariff_orders
UNION ALL SELECT 'service_requests', count(*) FROM service_requests
UNION ALL SELECT 'portal_activity_log', count(*) FROM portal_activity_log
ORDER BY table_name;

SELECT
    (SELECT count(*) FROM portal_activity_log) AS heap_rows,
    (SELECT count(*) FROM portal_activity_log_iceberg) AS iceberg_rows;

-- ---------------------------------------------------------------------------
-- Section 6: Live Demo Helper
-- ---------------------------------------------------------------------------
-- Run this during a demo to simulate 50 customers using the portal RIGHT NOW.
-- After running, wait ~60 seconds for pg_incremental to sync to Iceberg,
-- then verify in Snowflake.

-- INSERT INTO portal_activity_log (customer_key, event_time, event_type, event_detail, city, region, customer_type)
-- SELECT
--     customer_key,
--     now(),
--     (ARRAY['LOGIN', 'METER_READING', 'TARIFF_CHANGE', 'SERVICE_REQUEST'])[1 + (random() * 3)::int],
--     '{"source": "live_demo"}',
--     'Hamburg',
--     'Nord',
--     'Privatkunde'
-- FROM portal_users
-- ORDER BY random()
-- LIMIT 50;