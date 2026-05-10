from __future__ import annotations

import os
from pathlib import Path

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths
from src.ingestion.period_config import IngestionPeriod


logger = get_logger(__name__)


BRONZE_NORMALIZED_TYPES = {
    "VendorID": "long",
    "passenger_count": "double",
    "RatecodeID": "double",
    "PULocationID": "long",
    "DOLocationID": "long",
    "payment_type": "int",
    "trip_distance": "double",
    "fare_amount": "double",
    "total_amount": "double",
    "tip_amount": "double",
    "tolls_amount": "double",
    "extra": "double",
    "mta_tax": "double",
    "congestion_surcharge": "double",
    "airport_fee": "double",
    "tpep_pickup_datetime": "timestamp",
    "tpep_dropoff_datetime": "timestamp",
}


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
    logger.info("Reading bronze parquet files individually for schema normalization: %s", paths)

    bronze_df = None
    for path in paths:
        monthly_df = spark.read.parquet(path)
        normalized_df = normalize_bronze_dataframe(monthly_df)
        bronze_df = normalized_df if bronze_df is None else bronze_df.unionByName(
            normalized_df,
            allowMissingColumns=True,
        )

    if bronze_df is None:
        raise ValueError("No bronze parquet files were resolved for the requested period")
    return bronze_df


def normalize_bronze_dataframe(dataframe):
    from pyspark.sql import functions as F

    normalized = dataframe
    for column_name, target_type in BRONZE_NORMALIZED_TYPES.items():
        if column_name in normalized.columns:
            normalized = normalized.withColumn(column_name, F.col(column_name).cast(target_type))
        else:
            normalized = normalized.withColumn(column_name, F.lit(None).cast(target_type))

    ordered_columns = list(BRONZE_NORMALIZED_TYPES.keys()) + [
        column_name for column_name in normalized.columns if column_name not in BRONZE_NORMALIZED_TYPES
    ]
    return normalized.select(*ordered_columns)
