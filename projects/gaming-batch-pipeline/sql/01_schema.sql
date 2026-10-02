CREATE TABLE IF NOT EXISTS stg_gaming_events (
 event_id BIGINT PRIMARY KEY,
 player_id BIGINT NOT NULL,
 property_id INT NOT NULL,
 gaming_date DATE NOT NULL,
 coin_in NUMERIC(14,2) NOT NULL CHECK (coin_in >= 0),
 theo_win NUMERIC(14,2) NOT NULL,
 net_win NUMERIC(14,2) NOT NULL,
 free_play NUMERIC(14,2) NOT NULL CHECK (free_play >= 0),
 minutes_played INT NOT NULL CHECK (minutes_played >= 0)
);

CREATE TABLE IF NOT EXISTS fact_gaming_daily (
 player_id BIGINT NOT NULL,
 property_id INT NOT NULL,
 gaming_date DATE NOT NULL,
 coin_in NUMERIC(16,2) NOT NULL,
 theo_win NUMERIC(16,2) NOT NULL,
 net_win NUMERIC(16,2) NOT NULL,
 free_play NUMERIC(16,2) NOT NULL,
 minutes_played INT NOT NULL,
 PRIMARY KEY(player_id, property_id, gaming_date)
);
