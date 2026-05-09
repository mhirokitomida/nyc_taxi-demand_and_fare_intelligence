from __future__ import annotations

from pathlib import Path

import yaml


def test_compose_includes_required_services() -> None:
    compose_path = Path("docker-compose.yml")
    document = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = document["services"]

    expected_services = {
        "airflow-postgres",
        "airflow-init",
        "airflow-webserver",
        "airflow-scheduler",
        "spark-master",
        "spark-worker",
        "streamlit",
    }

    assert expected_services.issubset(services.keys())


def test_compose_exposes_required_ports() -> None:
    compose_path = Path("docker-compose.yml")
    document = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = document["services"]

    airflow_ports = services["airflow-webserver"]["ports"]
    spark_ports = services["spark-master"]["ports"]
    streamlit_ports = services["streamlit"]["ports"]

    assert "8080:8080" in airflow_ports
    assert "7077:7077" in spark_ports
    assert "8081:8080" in spark_ports
    assert "8501:8501" in streamlit_ports
