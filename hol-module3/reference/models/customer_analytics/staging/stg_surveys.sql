SELECT
    s.survey_id,
    s.customer_key,
    c.customer_name,
    c.customer_type,
    c.city,
    c.state AS region,
    s.survey_date,
    s.nps_score,
    CASE
        WHEN s.nps_score >= 9 THEN 'Promoter'
        WHEN s.nps_score >= 7 THEN 'Passive'
        ELSE 'Detractor'
    END AS nps_segment,
    s.category,
    s.comment
FROM {{ source('epower_bronze', 'customer_surveys') }} s
INNER JOIN {{ source('epower_gold', 'customer_dim') }} c
    ON s.customer_key = c.customer_key
