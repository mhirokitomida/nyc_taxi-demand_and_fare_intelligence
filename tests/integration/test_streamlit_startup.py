from __future__ import annotations

import importlib.util
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


STREAMLIT_AVAILABLE = importlib.util.find_spec("streamlit") is not None
ROOT_DIR = Path(__file__).resolve().parents[2]
PYTHON_EXE = Path(sys.executable)


@pytest.mark.skipif(not STREAMLIT_AVAILABLE, reason="streamlit is not installed in this environment")
def test_streamlit_home_starts_and_serves_healthcheck() -> None:
    command = [
        str(PYTHON_EXE),
        "-m",
        "streamlit",
        "run",
        "app/streamlit/Home.py",
        "--server.headless",
        "true",
        "--server.address",
        "127.0.0.1",
        "--server.port",
        "8511",
        "--browser.gatherUsageStats",
        "false",
    ]
    process = subprocess.Popen(
        command,
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if process.poll() is not None:
                pytest.fail("Streamlit process exited before serving the healthcheck")
            try:
                with urllib.request.urlopen("http://127.0.0.1:8511/_stcore/health", timeout=2) as response:
                    assert response.status == 200
                    return
            except Exception:
                time.sleep(1)
        pytest.fail("Streamlit healthcheck did not become reachable in time")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
