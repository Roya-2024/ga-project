# Gaming Analytics Batch Pipeline

Portfolio data-engineering project using **synthetic gaming data only**.

## Architecture
Synthetic CSV -> Python validation -> PostgreSQL staging -> SQL transformations -> analytics marts -> Airflow orchestration

## Skills demonstrated
- Python ETL and data-quality checks
- PostgreSQL dimensional modeling
- Airflow DAG orchestration
- Docker-ready project structure
- Idempotent loading pattern
- Business-facing analytics marts

## Data model
- `stg_gaming_events`
- `dim_player`
- `dim_property`
- `fact_gaming_daily`
- `mart_player_value`

## Run concept
1. Generate synthetic data with `src/generate_data.py`
2. Load raw data to PostgreSQL
3. Run SQL transformations
4. Schedule the pipeline with the Airflow DAG

> No ECL Gaming, Konami, Wynn, or real player data is included.
