# Marketing Campaign Batch Pipeline (Demo)

Synthetic data engineering project for orchestrating recurring marketing campaign data.

## Stack
- Apache Airflow
- Python / Pandas
- PostgreSQL
- Docker / Docker Compose
- SQL data-quality checks

## Flow
1. Ingest synthetic campaign and customer activity data.
2. Validate required fields and reject malformed records.
3. Standardize identifiers, dates, and campaign attributes.
4. Load clean rows into PostgreSQL staging tables.
5. Build reporting-ready campaign performance tables.
6. Run data-quality checks before publishing downstream outputs.

All data and identifiers in this project are synthetic. No proprietary employer data, production IDs, internal file names, credentials, or confidential records are included.
