SELECT
    region,
    customer_type,
    category,
    DATE_TRUNC('MONTH', survey_date)::DATE AS survey_month,
    COUNT(*) AS total_responses,
    ROUND(AVG(nps_score), 1) AS avg_nps,
    SUM(CASE WHEN nps_segment = 'Promoter' THEN 1 ELSE 0 END) AS promoters,
    SUM(CASE WHEN nps_segment = 'Passive' THEN 1 ELSE 0 END) AS passives,
    SUM(CASE WHEN nps_segment = 'Detractor' THEN 1 ELSE 0 END) AS detractors,
    ROUND(
        (SUM(CASE WHEN nps_segment = 'Promoter' THEN 1 ELSE 0 END)
         - SUM(CASE WHEN nps_segment = 'Detractor' THEN 1 ELSE 0 END))
        * 100.0 / NULLIF(COUNT(*), 0),
        1
    ) AS nps_index
FROM {{ ref('stg_surveys') }}
GROUP BY 1, 2, 3, 4
