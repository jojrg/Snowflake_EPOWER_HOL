SELECT
    DATE_TRUNC('DAY', event_time)::DATE AS activity_date,
    region,
    customer_type,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT customer_key) AS unique_customers
FROM {{ source('epower_bronze', 'portal_activity_log') }}
GROUP BY 1, 2, 3, 4
