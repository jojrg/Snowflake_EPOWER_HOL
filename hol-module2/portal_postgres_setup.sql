-- =============================================================================
-- EPOWER Module 2: "Mein EPOWER" Portal — Postgres Setup
-- =============================================================================
-- Run this file against your Snowflake Postgres instance:
--
--   psql service=my_epower_portal -f portal_postgres_setup.sql
--
-- Or with a full connection string:
--
--   psql "host=<HOST> port=5432 dbname=postgres user=snowflake_admin sslmode=require" \
--        -f portal_postgres_setup.sql
--
-- This creates:
--   1. Portal schema (5 tables + indexes)
--   2. pg_lake + pg_incremental extensions
--   3. Iceberg mirror table for portal_activity_log
--   4. Automated 1-minute sync pipeline (heap → Iceberg)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Section 1: Portal Schema
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS portal_users (
    customer_key       INT PRIMARY KEY,
    email              TEXT NOT NULL UNIQUE,
    display_name       TEXT NOT NULL,
    registered_at      TIMESTAMPTZ DEFAULT now(),
    last_login_at      TIMESTAMPTZ,
    login_count        INT DEFAULT 0,
    preferred_language TEXT DEFAULT 'de',
    notifications_enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS meter_readings (
    reading_id         BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    reading_date       DATE NOT NULL,
    meter_type         TEXT NOT NULL,
    reading_kwh        INT NOT NULL,
    submitted_at       TIMESTAMPTZ DEFAULT now(),
    source             TEXT DEFAULT 'PORTAL',
    CONSTRAINT valid_meter_type CHECK (meter_type IN ('ELECTRICITY', 'GAS'))
);

CREATE TABLE IF NOT EXISTS tariff_orders (
    order_id           BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    order_type         TEXT NOT NULL,
    current_product    TEXT,
    requested_product  TEXT NOT NULL,
    status             TEXT DEFAULT 'PENDING',
    created_at         TIMESTAMPTZ DEFAULT now(),
    confirmed_at       TIMESTAMPTZ,
    effective_date     DATE,
    CONSTRAINT valid_status CHECK (status IN ('PENDING', 'CONFIRMED', 'ACTIVE', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS service_requests (
    request_id         BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL REFERENCES portal_users(customer_key),
    request_type       TEXT NOT NULL,
    subject            TEXT NOT NULL,
    description        TEXT,
    status             TEXT DEFAULT 'OPEN',
    priority           TEXT DEFAULT 'NORMAL',
    created_at         TIMESTAMPTZ DEFAULT now(),
    resolved_at        TIMESTAMPTZ,
    CONSTRAINT valid_request_type CHECK (request_type IN ('SUPPORT', 'COMPLAINT', 'VPP_ENROLLMENT', 'VPP_OPTOUT', 'BILLING_INQUIRY', 'MOVE'))
);

CREATE TABLE IF NOT EXISTS portal_activity_log (
    activity_id        BIGSERIAL PRIMARY KEY,
    customer_key       INT NOT NULL,
    event_time         TIMESTAMPTZ DEFAULT now(),
    event_type         TEXT NOT NULL,
    event_detail       JSONB DEFAULT '{}',
    city               TEXT,
    region             TEXT,
    customer_type      TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_email ON portal_users(email);
CREATE INDEX IF NOT EXISTS idx_readings_customer ON meter_readings(customer_key, reading_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON tariff_orders(status) WHERE status = 'PENDING';
CREATE INDEX IF NOT EXISTS idx_requests_open ON service_requests(status) WHERE status = 'OPEN';
CREATE INDEX IF NOT EXISTS idx_activity_time ON portal_activity_log(event_time);

-- ---------------------------------------------------------------------------
-- Section 2: pg_lake + pg_incremental Extensions
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS pg_lake CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_incremental;

-- ---------------------------------------------------------------------------
-- Section 3: Iceberg Mirror Table
-- ---------------------------------------------------------------------------
-- This table stores portal_activity_log data in Apache Iceberg format.
-- pg_lake manages the Iceberg metadata and Parquet data files on object storage.

CREATE TABLE IF NOT EXISTS portal_activity_log_iceberg (
    activity_id        BIGINT,
    customer_key       INT,
    event_time         TIMESTAMPTZ,
    event_type         TEXT,
    event_detail       JSONB,
    city               TEXT,
    region             TEXT,
    customer_type      TEXT
) USING iceberg;

-- ---------------------------------------------------------------------------
-- Section 4: Automated Sync Pipeline (pg_incremental)
-- ---------------------------------------------------------------------------
-- Syncs new portal_activity_log entries to the Iceberg table every 1 minute.
-- Uses pg_incremental for exactly-once, time-interval-based processing.
-- NOTE: Run this AFTER loading the seed data (portal_seed_data.sql),
--       so that start_time picks up the earliest event.

SELECT incremental.create_time_interval_pipeline(
    pipeline_name      := 'sync_portal_activity_to_iceberg',
    time_interval      := '1 minute',
    source_table_name  := 'portal_activity_log',
    start_time         := (SELECT min(event_time) FROM portal_activity_log),
    command            := $inner$
        INSERT INTO portal_activity_log_iceberg
        SELECT activity_id, customer_key, event_time, event_type,
               event_detail, city, region, customer_type
        FROM portal_activity_log
        WHERE event_time >= $1 AND event_time < $2
    $inner$
);

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
