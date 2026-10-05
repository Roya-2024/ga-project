/*
Sanitized portfolio example: aggregate customer gaming performance and assign segments.
All table/column names and thresholds are fictional.
*/

WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(wager_amount) AS total_coin_in,
        SUM(expected_value) AS total_theo_win,
        COUNT(DISTINCT CAST(activity_date AS date)) AS total_trips
    FROM demo_daily_activity
    WHERE activity_date BETWEEN '2026-01-01' AND '2026-01-31'
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_coin_in,
    total_theo_win,
    total_trips,
    CASE
        WHEN total_coin_in < 5000 THEN 'Entry'
        WHEN total_coin_in < 25000 THEN 'Core'
        WHEN total_coin_in < 100000 THEN 'High Value'
        ELSE 'Top Value'
    END AS customer_segment
FROM customer_totals
ORDER BY total_coin_in DESC;
