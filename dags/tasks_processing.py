from __future__ import annotations

from src.common.logging_utils import get_logger
from src.processing.bronze_to_silver import run_bronze_to_silver
from src.processing.silver_to_gold import run_silver_to_gold

from dags._dag_params import load_dag_run_parameters, should_run_layer


logger = get_logger(__name__)


def run_silver_layer(**context: object) -> None:
    params = load_dag_run_parameters(context)
    if not should_run_layer("silver", params.target_layers):
        logger.info("Skipping silver layer for target_layers=%s", params.target_layers)
        return

    run_bronze_to_silver(
        start_month=params.start_month,
        end_month=params.end_month,
        spark_master=None,
        rerun_mode=params.rerun_mode,
        run_id=params.run_id,
    )


def run_gold_layer(**context: object) -> None:
    params = load_dag_run_parameters(context)
    if not should_run_layer("gold", params.target_layers):
        logger.info("Skipping gold layer for target_layers=%s", params.target_layers)
        return

    run_silver_to_gold(
        start_month=params.start_month,
        end_month=params.end_month,
        spark_master=None,
        rerun_mode=params.rerun_mode,
        run_id=params.run_id,
    )


def build_silver_operator():
    from airflow.operators.python import PythonOperator

    return PythonOperator(
        task_id="run_bronze_to_silver",
        python_callable=run_silver_layer,
    )


def build_gold_operator():
    from airflow.operators.python import PythonOperator

    return PythonOperator(
        task_id="run_silver_to_gold",
        python_callable=run_gold_layer,
    )
