from __future__ import annotations

import os
from pathlib import Path

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths
from src.ingestion.period_config import IngestionPeriod


logger = get_logger(__name__)


def create_spark_session(app_name: str, master: str | None = None):
    from pyspark.sql import SparkSession

    spark_master = master or os.getenv("SPARK_MASTER_URL") or "local[1]"
    logger.info("Creating SparkSession with master=%s", spark_master)
    return (
        SparkSession.builder.appName(app_name)
        .master(spark_master)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def bronze_input_paths(start_month: str, end_month: str, data_root: Path | None = None) -> list[str]:
    period = IngestionPeriod(start_month=start_month, end_month=end_month)
    root = data_root or get_data_paths().root
    paths: list[str] = []
    for year_month in period.iter_months():
        target = root / "bronze" / year_month / f"yellow_tripdata_{year_month}.parquet"
        if not target.exists():
            raise FileNotFoundError(f"Bronze parquet not found for {year_month}: {target}")
        paths.append(str(target))
    return paths


def read_bronze_dataframe(spark, start_month: str, end_month: str, data_root: Path | None = None):
    paths = bronze_input_paths(start_month=start_month, end_month=end_month, data_root=data_root)
    logger.info("Reading bronze parquet files: %s", paths)
    return spark.read.parquet(*paths)
