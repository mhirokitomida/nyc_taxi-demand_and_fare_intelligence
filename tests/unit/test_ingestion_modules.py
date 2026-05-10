from __future__ import annotations

import io
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from src.common.paths import DataPaths
from src.ingestion.batch_registry import build_batch_metadata
from src.ingestion.downloader import (
    DEFAULT_DOWNLOAD_BACKOFF_MULTIPLIER,
    DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS,
    DEFAULT_DOWNLOAD_MAX_ATTEMPTS,
    DEFAULT_DOWNLOAD_MAX_WAIT_SECONDS,
    DownloadResult,
    DownloadRetryConfig,
    RemoteArtifactUnavailableError,
    _calculate_retry_wait_seconds,
    download_source_file,
    verify_remote_exists,
)
from src.ingestion.period_config import IngestionPeriod, default_validation_period
from src.ingestion.source_catalog import build_yellow_taxi_source, resolve_period_sources


class FakeResponse:
    def __init__(self, body: bytes = b"payload", status: int = 200) -> None:
        self._buffer = io.BytesIO(body)
        self.status = status
        self.headers: dict[str, str] = {}

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def _make_data_paths(tmp_path) -> DataPaths:
    root = tmp_path / "data"
    return DataPaths(
        root=root,
        bronze=root / "bronze",
        silver=root / "silver",
        gold=root / "gold",
        ml=root / "ml",
    )


def test_resolve_period_sources_builds_expected_public_yellow_taxi_artifacts() -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-03")

    sources = resolve_period_sources(period)

    assert [source.year_month for source in sources] == ["2024-01", "2024-02", "2024-03"]
    assert all(source.dataset == "yellow_taxi" for source in sources)
    assert all(source.source_uri.endswith(f"yellow_tripdata_{source.year_month}.parquet") for source in sources)


def test_build_yellow_taxi_source_uses_expected_relative_bronze_path() -> None:
    source = build_yellow_taxi_source("2024-01")

    assert source.filename == "yellow_tripdata_2024-01.parquet"
    assert source.local_relative_path == "bronze/2024-01/yellow_tripdata_2024-01.parquet"
    assert source.source_uri == "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"


def test_build_batch_metadata_keeps_period_and_download_status_traceable(tmp_path) -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-01")
    download_results = [
        DownloadResult(
            source_uri="https://example/yellow_tripdata_2024-01.parquet",
            local_path=tmp_path / "yellow_tripdata_2024-01.parquet",
            year_month="2024-01",
            load_status="downloaded",
            downloaded_bytes=123,
        )
    ]

    metadata = build_batch_metadata(
        period=period,
        download_results=download_results,
        status="completed",
        rerun_mode="replace",
    )

    assert metadata.batch_id == "yellow_taxi_2024-01_to_2024-01"
    assert metadata.rerun_mode == "replace"
    assert metadata.files[0].year_month == "2024-01"
    assert metadata.files[0].load_status == "downloaded"


def test_default_validation_period_returns_single_month_window() -> None:
    period = default_validation_period()

    assert period.start_month == period.end_month
    assert period.month_count == 1


def test_verify_remote_exists_uses_get_request_and_succeeds_first_try(monkeypatch) -> None:
    requests: list[tuple[str, str]] = []

    def fake_urlopen(request, timeout: int):
        requests.append((request.full_url, request.get_method()))
        return FakeResponse(body=b"ok")

    monkeypatch.setattr("src.ingestion.downloader.urlopen", fake_urlopen)

    verify_remote_exists("https://example.com/file.parquet", year_month="2024-01")

    assert requests == [("https://example.com/file.parquet", "GET")]


def test_download_source_file_succeeds_on_first_attempt(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("src.ingestion.downloader.get_data_paths", lambda: _make_data_paths(tmp_path))
    monkeypatch.setattr("src.ingestion.downloader.urlopen", lambda request, timeout: FakeResponse(body=b"abc"))
    source = build_yellow_taxi_source("2024-01")

    result = download_source_file(source)

    assert result.downloaded_bytes == 3
    assert result.local_path.exists()
    assert result.local_path.read_bytes() == b"abc"
    assert not result.local_path.with_name(f"{result.local_path.name}.tmp").exists()


def test_download_source_file_retries_http_403_then_succeeds(monkeypatch, tmp_path) -> None:
    from urllib.error import HTTPError

    monkeypatch.setattr("src.ingestion.downloader.get_data_paths", lambda: _make_data_paths(tmp_path))
    waits: list[float] = []
    attempts = {"count": 0}

    def fake_sleep(seconds: float) -> None:
        waits.append(seconds)

    def fake_urlopen(request, timeout: int):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)
        return FakeResponse(body=b"retry-success")

    monkeypatch.setattr("src.ingestion.downloader.sleep", fake_sleep)
    monkeypatch.setattr("src.ingestion.downloader.urlopen", fake_urlopen)

    result = download_source_file(build_yellow_taxi_source("2024-01"))

    assert attempts["count"] == 2
    assert waits == [DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS]
    assert result.local_path.read_bytes() == b"retry-success"


@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_verify_remote_exists_retries_retryable_http_statuses(monkeypatch, status_code: int) -> None:
    from urllib.error import HTTPError

    attempts = {"count": 0}
    waits: list[float] = []

    def fake_sleep(seconds: float) -> None:
        waits.append(seconds)

    def fake_urlopen(request, timeout: int):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise HTTPError(request.full_url, status_code, "retryable", hdrs=None, fp=None)
        return FakeResponse(body=b"ok")

    monkeypatch.setattr("src.ingestion.downloader.sleep", fake_sleep)
    monkeypatch.setattr("src.ingestion.downloader.urlopen", fake_urlopen)

    verify_remote_exists("https://example.com/file.parquet", year_month="2024-01")

    assert attempts["count"] == 3
    assert waits == [DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS, DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS * 2]


def test_download_source_file_fails_after_exhausting_max_attempts(monkeypatch, tmp_path) -> None:
    from urllib.error import HTTPError

    monkeypatch.setattr("src.ingestion.downloader.get_data_paths", lambda: _make_data_paths(tmp_path))
    waits: list[float] = []

    def fake_sleep(seconds: float) -> None:
        waits.append(seconds)

    def fake_urlopen(request, timeout: int):
        raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)

    retry_config = DownloadRetryConfig(max_attempts=3, initial_wait_seconds=1, backoff_multiplier=2, max_wait_seconds=10)
    monkeypatch.setattr("src.ingestion.downloader.sleep", fake_sleep)
    monkeypatch.setattr("src.ingestion.downloader.urlopen", fake_urlopen)

    with pytest.raises(RemoteArtifactUnavailableError):
        download_source_file(build_yellow_taxi_source("2024-01"), retry_config=retry_config)

    assert waits == [1, 2]


def test_backoff_calculation_grows_with_cap() -> None:
    config = DownloadRetryConfig(max_attempts=6, initial_wait_seconds=5, backoff_multiplier=2, max_wait_seconds=60)

    waits = [_calculate_retry_wait_seconds(attempt, config) for attempt in range(1, 7)]

    assert waits == [0.0, 5, 10, 20, 40, 60]


def test_download_source_file_removes_tmp_file_after_failed_attempt(monkeypatch, tmp_path) -> None:
    from urllib.error import URLError

    monkeypatch.setattr("src.ingestion.downloader.get_data_paths", lambda: _make_data_paths(tmp_path))
    monkeypatch.setattr("src.ingestion.downloader.sleep", lambda seconds: None)
    source = build_yellow_taxi_source("2024-01")
    temp_holder: dict[str, str] = {}
    def fake_urlopen(request, timeout: int):
        return FakeResponse(body=b"ignored")

    def fake_copyfileobj(src, dst, length: int = 0) -> None:
        dst.write(b"partial")
        temp_holder["path"] = dst.name
        raise URLError("temporary timeout")

    monkeypatch.setattr("src.ingestion.downloader.urlopen", fake_urlopen)
    monkeypatch.setattr("src.ingestion.downloader.shutil.copyfileobj", fake_copyfileobj)

    with pytest.raises(RemoteArtifactUnavailableError):
        download_source_file(
            source,
            retry_config=replace(
                DownloadRetryConfig(),
                max_attempts=1,
            ),
        )

    assert temp_holder["path"].endswith(".tmp")
    assert not Path(temp_holder["path"]).exists()
    final_path = _make_data_paths(tmp_path).bronze / "2024-01" / source.filename
    assert not final_path.exists()


def test_download_source_file_writes_final_artifact_only_after_complete_download(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("src.ingestion.downloader.get_data_paths", lambda: _make_data_paths(tmp_path))
    monkeypatch.setattr("src.ingestion.downloader.urlopen", lambda request, timeout: FakeResponse(body=b"complete-download"))

    result = download_source_file(build_yellow_taxi_source("2024-01"))

    assert result.local_path.exists()
    assert result.local_path.read_bytes() == b"complete-download"
    assert not result.local_path.with_name(f"{result.local_path.name}.tmp").exists()
