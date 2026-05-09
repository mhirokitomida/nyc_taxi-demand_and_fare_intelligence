from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.ingestion.bronze_pipeline import run_bronze_ingestion


def _run_bronze_task(**context: object) -> None:
    dag_run = context.get("dag_run")
    conf = getattr(dag_run, "conf", {}) if dag_run else {}
    start_month = conf.get("start_month", "2024-01")
    end_month = conf.get("end_month", start_month)
    rerun_mode = conf.get("rerun_mode", "fail")
    run_bronze_ingestion(
        start_month=start_month,
        end_month=end_month,
        rerun_mode=rerun_mode,
    )


with DAG(
    dag_id="bronze_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["nyc-taxi", "bronze"],
) as dag:
    bronze_ingestion = PythonOperator(
        task_id="run_bronze_ingestion",
        python_callable=_run_bronze_task,
    )
