SELECT
    fetch_date,
    start_time,
    end_time,
    price_eur_mwh,
    ROUND(price_eur_mwh / 1000, 4) AS price_eur_kwh,
    DATE_TRUNC('HOUR', start_time) AS hour,
    DAYNAME(start_time) AS day_of_week,
    HOUR(start_time) AS hour_of_day
FROM {{ ref('stg_day_ahead_prices') }}
