# Marketing Data Orchestration (Demo)

Synthetic Data Engineering portfolio project showing a production-style batch workflow for marketing data.

## Stack
- Apache Airflow
- Python / Pandas
- PostgreSQL
- Docker Compose
- SQL
- Data-quality checks

## Flow
1. Ingest synthetic campaign, customer, and conversion files.
2. Validate schema and required fields.
3. Standardize identifiers and timestamps.
4. Deduplicate customer/campaign events.
5. Load curated tables into PostgreSQL.
6. Run SQL data-quality checks.
7. Publish an analytics-ready campaign-performance table.

All names, records, identifiers, and values are synthetic. No employer or proprietary data is included.
