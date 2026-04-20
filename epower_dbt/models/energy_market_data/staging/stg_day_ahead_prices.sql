{{
    config(
        materialized='incremental',
        unique_key='start_time',
        on_schema_change='sync_all_columns'
    )
}}

WITH flattened AS (
    SELECT
        r.fetch_timestamp,
        r.fetch_date,
        ts.INDEX AS idx,
        ts.VALUE::NUMBER AS unix_seconds,
        r.raw_data:price[ts.INDEX]::FLOAT AS price_eur_mwh
    FROM {{ source('epower_bronze', 'raw_day_ahead_prices') }} r,
    LATERAL FLATTEN(input => r.raw_data:unix_seconds) ts
    {% if is_incremental() %}
    WHERE r.fetch_date > (SELECT COALESCE(MAX(fetch_date), '1900-01-01') FROM {{ this }})
    {% endif %}
)

SELECT
    fetch_timestamp,
    fetch_date,
    TO_TIMESTAMP_NTZ(unix_seconds) AS start_time,
    DATEADD('minute', 15, TO_TIMESTAMP_NTZ(unix_seconds)) AS end_time,
    price_eur_mwh
FROM flattened
