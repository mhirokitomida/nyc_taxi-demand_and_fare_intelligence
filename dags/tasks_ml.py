from __future__ import annotations

from src.common.logging_utils import get_logger
from src.ml.run_ml_pipeline import run_ml_pipeline

from dags._dag_params import load_dag_run_parameters, should_run_layer


logger = get_logger(__name__)


def run_ml_layer(**context: object) -> None:
    params = load_dag_run_parameters(context)
    if not should_run_layer("ml", params.target_layers):
        logger.info("Skipping ml layer for target_layers=%s", params.target_layers)
        return

    run_ml_pipeline(
        start_month=params.start_month,
        end_month=params.end_month,
        rerun_mode=params.rerun_mode,
        run_id=params.run_id,
    )


def build_ml_operator():
    from airflow.operators.python import PythonOperator

    return PythonOperator(
        task_id="run_ml_pipeline",
        python_callable=run_ml_layer,
    )
