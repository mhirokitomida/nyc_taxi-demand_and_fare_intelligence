from __future__ import annotations

import os
import urllib.error
import urllib.request

import pytest


def _access_checks_enabled() -> bool:
    return os.getenv("RUN_LOCAL_SERVICE_CHECKS") == "1"


@pytest.mark.local_services
@pytest.mark.skipif(not _access_checks_enabled(), reason="Local service checks are disabled by default.")
def test_airflow_web_ui_is_reachable() -> None:
    try:
        with urllib.request.urlopen("http://localhost:8080/health", timeout=5) as response:
            assert response.status == 200
    except urllib.error.URLError as exc:  # pragma: no cover - runtime integration guard
        pytest.fail(f"Airflow UI health endpoint is not reachable: {exc}")


@pytest.mark.local_services
@pytest.mark.skipif(not _access_checks_enabled(), reason="Local service checks are disabled by default.")
def test_streamlit_health_is_reachable() -> None:
    try:
        with urllib.request.urlopen("http://localhost:8501/_stcore/health", timeout=5) as response:
            assert response.status == 200
    except urllib.error.URLError as exc:  # pragma: no cover - runtime integration guard
        pytest.fail(f"Streamlit health endpoint is not reachable: {exc}")
