from __future__ import annotations

import os
import urllib.error
import urllib.request

import pytest


def _service_check_enabled() -> bool:
    return os.getenv("RUN_LOCAL_SERVICE_CHECKS") == "1"


@pytest.mark.local_services
@pytest.mark.skipif(not _service_check_enabled(), reason="Local service checks are disabled by default.")
@pytest.mark.parametrize(
    ("url", "label"),
    [
        ("http://localhost:8080/health", "airflow"),
        ("http://localhost:8501/_stcore/health", "streamlit"),
        ("http://localhost:8081", "spark-master"),
    ],
)
def test_service_health_endpoints(url: str, label: str) -> None:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            assert response.status == 200, f"{label} returned {response.status}"
    except urllib.error.URLError as exc:  # pragma: no cover - runtime integration guard
        pytest.fail(f"{label} not reachable at {url}: {exc}")
