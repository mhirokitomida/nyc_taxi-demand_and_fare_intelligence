from __future__ import annotations

from src.common.logging_utils import get_logger
from src.ingestion.bronze_pipeline import run_bronze_ingestion

from dags._dag_params import load_dag_run_parameters, should_run_layer


logger = get_logger(__name__)


def run_bronze_layer(**context: object) -> None:
    params = load_dag_run_parameters(context)
    if not should_run_layer("bronze", params.target_layers):
        logger.info("Skipping bronze layer for target_layers=%s", params.target_layers)
        return

    run_bronze_ingestion(
        start_month=params.start_month,
        end_month=params.end_month,
        rerun_mode=params.rerun_mode,
        download_max_attempts=params.download_max_attempts,
        download_initial_wait_seconds=params.download_initial_wait_seconds,
        download_backoff_multiplier=params.download_backoff_multiplier,
        download_max_wait_seconds=params.download_max_wait_seconds,
    )


def build_bronze_operator():
    from airflow.operators.python import PythonOperator

    return PythonOperator(
        task_id="run_bronze_ingestion",
        python_callable=run_bronze_layer,
    )
