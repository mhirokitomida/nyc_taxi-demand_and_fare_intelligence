from __future__ import annotations


REQUIRED_SILVER_COLUMNS = [
    "pickup_datetime",
    "dropoff_datetime",
    "service_date",
    "pickup_hour",
    "day_of_week",
    "pickup_zone_id",
    "dropoff_zone_id",
    "trip_distance",
    "fare_amount",
    "total_amount",
    "trip_duration_minutes",
    "passenger_count",
    "payment_type",
]


def derive_trip_features(dataframe):
    from pyspark.sql import functions as F

    duration_minutes = (
        F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")
    ) / F.lit(60.0)

    return dataframe.select(
        F.col("tpep_pickup_datetime").alias("pickup_datetime"),
        F.col("tpep_dropoff_datetime").alias("dropoff_datetime"),
        F.to_date("tpep_pickup_datetime").alias("service_date"),
        F.hour("tpep_pickup_datetime").alias("pickup_hour"),
        F.dayofweek("tpep_pickup_datetime").alias("day_of_week"),
        F.col("PULocationID").cast("int").alias("pickup_zone_id"),
        F.col("DOLocationID").cast("int").alias("dropoff_zone_id"),
        F.col("trip_distance").cast("double").alias("trip_distance"),
        F.col("fare_amount").cast("double").alias("fare_amount"),
        F.col("total_amount").cast("double").alias("total_amount"),
        duration_minutes.cast("double").alias("trip_duration_minutes"),
        F.col("passenger_count").cast("double").alias("passenger_count"),
        F.col("payment_type").cast("int").alias("payment_type"),
    )
