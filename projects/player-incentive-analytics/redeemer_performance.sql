/*
Sanitized portfolio example: compare incentive redemption with gaming performance.
*/

WITH performance AS (
    SELECT
        customer_id,
        SUM(wager_amount) AS total_coin_in,
        SUM(expected_value) AS total_theo_win
    FROM demo_daily_activity
    WHERE activity_date BETWEEN '2026-01-01' AND '2026-01-31'
    GROUP BY customer_id
),
redeemers AS (
    SELECT DISTINCT
        site_code,
        customer_id,
        promotion_code,
        redemption_date
    FROM demo_promotion_redemptions
    WHERE redemption_date BETWEEN '2026-01-01' AND '2026-01-31'
)
SELECT
    r.site_code,
    r.customer_id,
    MAX(r.promotion_code) AS promotion_code,
    MAX(r.redemption_date) AS latest_redemption,
    p.total_coin_in,
    p.total_theo_win
FROM redeemers r
LEFT JOIN performance p
    ON r.customer_id = p.customer_id
GROUP BY
    r.site_code,
    r.customer_id,
    p.total_coin_in,
    p.total_theo_win;
