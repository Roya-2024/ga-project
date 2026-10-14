-- SQLite. Amounts are integer USD cents; aggregate across locations per player.
-- Bind :report_date (local calendar date) and :threshold_cents (1000000).
SELECT player_id,
       GROUP_CONCAT(DISTINCT location) AS locations,
       COUNT(*) AS session_count,
       SUM(coin_in_cents) AS coin_in_cents
FROM sessions
WHERE report_date = :report_date
GROUP BY player_id
HAVING SUM(coin_in_cents) > :threshold_cents
ORDER BY coin_in_cents DESC, player_id;
