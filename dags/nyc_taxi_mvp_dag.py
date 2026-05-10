from __future__ import annotations

from datetime import datetime

from airflow import DAG

from dags.tasks_bronze import build_bronze_operator
from dags.tasks_ml import build_ml_operator
from dags.tasks_processing import build_gold_operator, build_silver_operator


with DAG(
    dag_id="nyc_taxi_mvp",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["nyc-taxi", "bronze", "silver", "gold", "ml"],
) as dag:
    bronze_ingestion = build_bronze_operator()
    bronze_to_silver = build_silver_operator()
    silver_to_gold = build_gold_operator()
    ml_forecast = build_ml_operator()

    bronze_ingestion >> bronze_to_silver >> silver_to_gold >> ml_forecast
