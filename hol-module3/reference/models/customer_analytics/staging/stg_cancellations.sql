SELECT
    cc.cancellation_id,
    cc.customer_key,
    c.customer_name,
    c.customer_type,
    c.city,
    c.state AS region,
    cc.product_key,
    p.product_name,
    p.category_name,
    cc.cancellation_date,
    cc.reason,
    cc.channel,
    cc.retention_offered,
    cc.retention_accepted
FROM {{ source('epower_bronze', 'contract_cancellations') }} cc
INNER JOIN {{ source('epower_gold', 'customer_dim') }} c
    ON cc.customer_key = c.customer_key
INNER JOIN {{ source('epower_gold', 'product_dim') }} p
    ON cc.product_key = p.product_key
