INSERT INTO fact_gaming_daily
(player_id,property_id,gaming_date,coin_in,theo_win,net_win,free_play,minutes_played)
SELECT player_id,property_id,gaming_date,
       SUM(coin_in),SUM(theo_win),SUM(net_win),SUM(free_play),SUM(minutes_played)
FROM stg_gaming_events
GROUP BY player_id,property_id,gaming_date
ON CONFLICT (player_id,property_id,gaming_date) DO UPDATE SET
 coin_in=EXCLUDED.coin_in,
 theo_win=EXCLUDED.theo_win,
 net_win=EXCLUDED.net_win,
 free_play=EXCLUDED.free_play,
 minutes_played=EXCLUDED.minutes_played;

CREATE OR REPLACE VIEW mart_player_value AS
SELECT player_id,
       COUNT(DISTINCT gaming_date) AS active_days,
       SUM(coin_in) AS lifetime_coin_in,
       SUM(theo_win) AS lifetime_theo_win,
       SUM(net_win) AS lifetime_net_win,
       SUM(free_play) AS lifetime_free_play,
       CASE WHEN SUM(theo_win)=0 THEN NULL
            ELSE ROUND(SUM(free_play)/SUM(theo_win),4) END AS reinvestment_rate
FROM fact_gaming_daily
GROUP BY player_id;
