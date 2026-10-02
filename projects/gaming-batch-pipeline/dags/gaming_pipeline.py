from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="synthetic_gaming_batch_pipeline",
    start_date=datetime(2026,1,1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio","data-engineering"],
) as dag:
    generate = BashOperator(
        task_id="generate_synthetic_data",
        bash_command="python /opt/airflow/project/src/generate_data.py",
    )
    quality = BashOperator(
        task_id="quality_check",
        bash_command="python /opt/airflow/project/src/quality_check.py",
    )
    generate >> quality
