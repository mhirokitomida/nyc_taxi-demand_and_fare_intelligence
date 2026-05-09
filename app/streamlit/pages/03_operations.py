from __future__ import annotations

import pandas as pd
import streamlit as st

from app.streamlit.data_loader import list_gold_periods, load_dashboard_artifacts


st.title("Operations")
periods = list_gold_periods()
selected_period = st.sidebar.selectbox("Periodo de dados", [period.label for period in periods], index=len(periods) - 1)
artifacts = load_dashboard_artifacts(requested_period=selected_period)

operations_frame = artifacts.gold_frame.copy()
operations_frame["service_date"] = pd.to_datetime(operations_frame["service_date"])

daily_operations = (
    operations_frame.groupby("service_date", as_index=False)
    .apply(
        lambda group: pd.Series(
            {
                "trip_count": group["trip_count"].sum(),
                "total_fare": group["total_fare"].sum(),
                "total_distance": group["total_distance"].sum(),
                "avg_duration_minutes": (group["avg_duration_minutes"] * group["trip_count"]).sum()
                / group["trip_count"].sum(),
            }
        ),
        include_groups=False,
    )
    .sort_values("service_date")
)

top_zone_operations = (
    operations_frame.groupby("pickup_zone_id", as_index=False)
    .apply(
        lambda group: pd.Series(
            {
                "trip_count": group["trip_count"].sum(),
                "total_fare": group["total_fare"].sum(),
                "total_distance": group["total_distance"].sum(),
                "avg_duration_minutes": (group["avg_duration_minutes"] * group["trip_count"]).sum()
                / group["trip_count"].sum(),
            }
        ),
        include_groups=False,
    )
    .sort_values("total_fare", ascending=False)
    .head(20)
)

col1, col2, col3 = st.columns(3)
col1.metric("Fare volume", f"${daily_operations['total_fare'].sum():,.2f}")
col2.metric("Distance volume", f"{daily_operations['total_distance'].sum():,.1f}")
weighted_duration = (
    (operations_frame["avg_duration_minutes"] * operations_frame["trip_count"]).sum()
    / operations_frame["trip_count"].sum()
)
col3.metric("Weighted avg duration", f"{weighted_duration:,.2f} min")

st.markdown("### Daily operations trends")
st.line_chart(daily_operations.set_index("service_date"))

st.markdown("### Top zones by fare volume")
st.dataframe(top_zone_operations, use_container_width=True)
