from __future__ import annotations

import ast
import importlib.util
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DAG_FILE = ROOT_DIR / "dags" / "nyc_taxi_mvp_dag.py"
TASKS_BRONZE_FILE = ROOT_DIR / "dags" / "tasks_bronze.py"
TASKS_PROCESSING_FILE = ROOT_DIR / "dags" / "tasks_processing.py"
TASKS_ML_FILE = ROOT_DIR / "dags" / "tasks_ml.py"


def test_mvp_dag_definition_has_expected_order_and_ids() -> None:
    dag_source = DAG_FILE.read_text(encoding="utf-8")
    tree = ast.parse(dag_source, filename=str(DAG_FILE))
    bronze_source = TASKS_BRONZE_FILE.read_text(encoding="utf-8")
    processing_source = TASKS_PROCESSING_FILE.read_text(encoding="utf-8")
    ml_source = TASKS_ML_FILE.read_text(encoding="utf-8")

    assert "dag_id=\"nyc_taxi_mvp\"" in dag_source
    assert "build_bronze_operator" in dag_source
    assert "build_silver_operator" in dag_source
    assert "build_gold_operator" in dag_source
    assert "build_ml_operator" in dag_source
    assert "bronze_ingestion >> bronze_to_silver >> silver_to_gold >> ml_forecast" in dag_source
    assert "rerun_mode=params.rerun_mode" in processing_source
    assert "run_id=params.run_id" in processing_source
    assert "rerun_mode=params.rerun_mode" in ml_source
    assert "run_id=params.run_id" in ml_source
    assert 'task_id="run_bronze_ingestion"' in bronze_source
    assert 'task_id="run_bronze_to_silver"' in processing_source
    assert 'task_id="run_silver_to_gold"' in processing_source
    assert 'task_id="run_ml_pipeline"' in ml_source
    assert isinstance(tree, ast.Module)


def test_mvp_dag_imports_without_errors_when_airflow_is_available() -> None:
    if importlib.util.find_spec("airflow") is None:
        return

    from airflow.models import DagBag

    dag_bag = DagBag(dag_folder=str(ROOT_DIR / "dags"), include_examples=False)
    assert not dag_bag.import_errors
    dag = dag_bag.get_dag("nyc_taxi_mvp")
    assert dag is not None
    assert dag.task_ids == {
        "run_bronze_ingestion",
        "run_bronze_to_silver",
        "run_silver_to_gold",
        "run_ml_pipeline",
    }
    assert dag.get_task("run_bronze_ingestion").downstream_task_ids == {"run_bronze_to_silver"}
    assert dag.get_task("run_bronze_to_silver").downstream_task_ids == {"run_silver_to_gold"}
    assert dag.get_task("run_silver_to_gold").downstream_task_ids == {"run_ml_pipeline"}
