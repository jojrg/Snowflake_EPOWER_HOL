SELECT
    category_name,
    region,
    DATE_TRUNC('MONTH', cancellation_date)::DATE AS cancellation_month,
    reason,
    COUNT(*) AS cancellations,
    COUNT(DISTINCT customer_key) AS unique_customers,
    SUM(CASE WHEN retention_offered THEN 1 ELSE 0 END) AS retention_offered_count,
    SUM(CASE WHEN retention_accepted THEN 1 ELSE 0 END) AS retention_accepted_count,
    ROUND(
        SUM(CASE WHEN retention_accepted THEN 1 ELSE 0 END) * 100.0
        / NULLIF(SUM(CASE WHEN retention_offered THEN 1 ELSE 0 END), 0),
        1
    ) AS retention_success_rate_pct
FROM {{ ref('stg_cancellations') }}
GROUP BY 1, 2, 3, 4
