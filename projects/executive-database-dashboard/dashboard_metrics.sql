/*
Sanitized portfolio example for executive database metrics.
All names and values are fictional.
*/

WITH active_accounts AS (
    SELECT
        customer_id,
        account_open_date,
        market_type,
        country_code
    FROM demo_customer_master
    WHERE account_status = 'ACTIVE'
),
new_accounts AS (
    SELECT
        YEAR(account_open_date) AS signup_year,
        COUNT(DISTINCT customer_id) AS new_customers
    FROM active_accounts
    GROUP BY YEAR(account_open_date)
)
SELECT
    (SELECT COUNT(DISTINCT customer_id) FROM active_accounts) AS active_accounts,
    (SELECT COUNT(DISTINCT customer_id) FROM active_accounts WHERE market_type = 'LOCAL') AS local_accounts,
    (SELECT COUNT(DISTINCT customer_id) FROM active_accounts WHERE market_type = 'NON_LOCAL') AS non_local_accounts,
    (SELECT COUNT(DISTINCT customer_id) FROM active_accounts WHERE country_code <> 'US') AS international_accounts;

SELECT signup_year, new_customers
FROM new_accounts
ORDER BY signup_year;
