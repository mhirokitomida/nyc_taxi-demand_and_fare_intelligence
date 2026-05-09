from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_root: Path
    log_level: str
    airflow_base_url: str
    streamlit_port: int
    spark_master_url: str


def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    data_root = project_root / os.getenv("DATA_ROOT", "data")
    return Settings(
        project_root=project_root,
        data_root=data_root,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        airflow_base_url=os.getenv("AIRFLOW__WEBSERVER__BASE_URL", "http://localhost:8080"),
        streamlit_port=int(os.getenv("STREAMLIT_SERVER_PORT", "8501")),
        spark_master_url=os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"),
    )
