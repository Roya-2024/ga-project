/*
Sanitized portfolio example: identify the first incentive redemption per customer.
All object names and values are fictional.
*/

WITH incentive_events AS (
    SELECT
        event_date,
        customer_id,
        site_code,
        promotion_code,
        promotion_value,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY event_date
        ) AS redemption_sequence
    FROM demo_promotion_events
    WHERE event_date BETWEEN '2026-01-01' AND '2026-01-31'
      AND promotion_code IN ('PROMO_A', 'PROMO_B', 'PROMO_C')
)
SELECT
    event_date,
    customer_id,
    site_code,
    promotion_code,
    promotion_value,
    CASE WHEN redemption_sequence = 1 THEN 1 ELSE 0 END AS is_first_redemption
FROM incentive_events;
