WITH churn_summary AS (
    SELECT
        customer_key,
        customer_name,
        customer_type,
        city,
        region,
        COUNT(*) AS total_cancellations,
        MAX(cancellation_date) AS last_cancellation_date
    FROM {{ ref('stg_cancellations') }}
    GROUP BY 1, 2, 3, 4, 5
),

nps_summary AS (
    SELECT
        customer_key,
        ROUND(AVG(nps_score), 1) AS avg_nps_score,
        COUNT(*) AS survey_responses,
        MAX(survey_date) AS last_survey_date,
        MODE(nps_segment) AS dominant_segment
    FROM {{ ref('stg_surveys') }}
    GROUP BY 1
),

customers AS (
    SELECT DISTINCT
        customer_key,
        customer_name,
        customer_type,
        city,
        state AS region
    FROM {{ source('epower_gold', 'customer_dim') }}
)

SELECT
    c.customer_key,
    c.customer_name,
    c.customer_type,
    c.city,
    c.region,
    COALESCE(ch.total_cancellations, 0) AS total_cancellations,
    ch.last_cancellation_date,
    n.avg_nps_score,
    n.survey_responses,
    n.dominant_segment AS nps_segment,
    n.last_survey_date,
    CASE
        WHEN ch.total_cancellations > 0 AND COALESCE(n.avg_nps_score, 5) < 7 THEN 'At Risk'
        WHEN ch.total_cancellations > 0 AND COALESCE(n.avg_nps_score, 7) >= 7 THEN 'Neutral'
        WHEN ch.total_cancellations = 0 AND COALESCE(n.avg_nps_score, 7) >= 9 THEN 'Champion'
        WHEN ch.total_cancellations = 0 AND COALESCE(n.avg_nps_score, 7) >= 7 THEN 'Healthy'
        ELSE 'Neutral'
    END AS health_segment
FROM customers c
LEFT JOIN churn_summary ch ON c.customer_key = ch.customer_key
LEFT JOIN nps_summary n ON c.customer_key = n.customer_key
WHERE ch.customer_key IS NOT NULL OR n.customer_key IS NOT NULL
