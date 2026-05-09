from __future__ import annotations

from collections import defaultdict
from datetime import date

from src.common.read_gold_artifacts import read_gold_records


def extract_gold_kpis(records: list[dict]) -> dict[str, float | int]:
    if not records:
        raise ValueError("Gold records are required to extract analytical KPIs")

    total_trip_count = sum(int(record["trip_count"]) for record in records)
    total_fare = sum(float(record["total_fare"]) for record in records)
    total_distance = sum(float(record["total_distance"]) for record in records)
    weighted_duration = sum(float(record["avg_duration_minutes"]) * int(record["trip_count"]) for record in records)

    service_dates = {record["service_date"] for record in records}
    pickup_zones = {record["pickup_zone_id"] for record in records}

    return {
        "total_rides": total_trip_count,
        "total_demand": total_trip_count,
        "total_fare": total_fare,
        "avg_fare": total_fare / total_trip_count,
        "total_distance": total_distance,
        "avg_distance": total_distance / total_trip_count,
        "avg_duration_minutes": weighted_duration / total_trip_count,
        "service_days": len(service_dates),
        "pickup_zones": len(pickup_zones),
    }


def build_daily_demand_series(records: list[dict]) -> list[dict[str, date | int]]:
    demand_by_day: dict[date, int] = defaultdict(int)
    for record in records:
        demand_by_day[record["service_date"]] += int(record["trip_count"])
    return [
        {"service_date": service_date, "trip_count": demand_by_day[service_date]}
        for service_date in sorted(demand_by_day)
    ]


def build_zone_summary(records: list[dict], limit: int | None = None) -> list[dict[str, float | int]]:
    totals_by_zone: dict[int, dict[str, float | int]] = {}
    for record in records:
        zone_id = int(record["pickup_zone_id"])
        zone_totals = totals_by_zone.setdefault(
            zone_id,
            {"pickup_zone_id": zone_id, "trip_count": 0, "total_fare": 0.0, "total_distance": 0.0},
        )
        zone_totals["trip_count"] += int(record["trip_count"])
        zone_totals["total_fare"] += float(record["total_fare"])
        zone_totals["total_distance"] += float(record["total_distance"])

    rows = sorted(totals_by_zone.values(), key=lambda row: row["trip_count"], reverse=True)
    if limit is not None:
        rows = rows[:limit]
    return rows


def load_default_gold_kpis() -> dict[str, float | int]:
    records = read_gold_records(start_month="2024-01", end_month="2024-01")
    return extract_gold_kpis(records)
