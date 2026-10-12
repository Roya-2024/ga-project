"""Synthetic Airflow DAG for a marketing data pipeline demo."""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd

RAW = "/opt/airflow/data/synthetic_campaign_events.csv"
CURATED = "/opt/airflow/data/curated_campaign_events.csv"

def transform():
    df = pd.read_csv(RAW)
    df.columns = [c.strip().lower() for c in df.columns]
    df["event_ts"] = pd.to_datetime(df["event_ts"], errors="coerce")
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df = df.dropna(subset=["customer_id", "campaign_id", "event_ts"])
    df = df.drop_duplicates(["customer_id", "campaign_id", "event_ts"])
    df.to_csv(CURATED, index=False)

def quality_check():
    df = pd.read_csv(CURATED)
    assert df["customer_id"].notna().all()
    assert df["campaign_id"].notna().all()
    assert not df.duplicated(["customer_id", "campaign_id", "event_ts"]).any()

with DAG(
    dag_id="demo_marketing_data_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["demo", "marketing", "data-engineering"],
) as dag:
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    dq_task = PythonOperator(task_id="quality_check", python_callable=quality_check)
    transform_task >> dq_task
