from __future__ import annotations

import pandas as pd
import streamlit as st

from app.streamlit.data_loader import list_gold_periods, load_dashboard_artifacts
from src.processing.analytics_views import extract_gold_kpis


st.title("Overview")
periods = list_gold_periods()
selected_period = st.sidebar.selectbox("Periodo de dados", [period.label for period in periods], index=len(periods) - 1)
artifacts = load_dashboard_artifacts(requested_period=selected_period)

kpis = extract_gold_kpis(artifacts.gold_frame.to_dict(orient="records"))

metrics_row_1 = st.columns(4)
metrics_row_1[0].metric("Total rides", f"{int(kpis['total_rides']):,}")
metrics_row_1[1].metric("Total fare", f"${kpis['total_fare']:,.2f}")
metrics_row_1[2].metric("Avg fare", f"${kpis['avg_fare']:,.2f}")
metrics_row_1[3].metric("Pickup zones", int(kpis["pickup_zones"]))

metrics_row_2 = st.columns(3)
metrics_row_2[0].metric("Total distance", f"{kpis['total_distance']:,.1f}")
metrics_row_2[1].metric("Avg distance", f"{kpis['avg_distance']:,.2f}")
metrics_row_2[2].metric("Weighted avg duration (min)", f"{kpis['avg_duration_minutes']:,.2f}")

st.markdown("### Historical sample")
st.dataframe(
    artifacts.gold_frame.sort_values(["service_date", "pickup_zone_id"]).head(20),
    use_container_width=True,
)

st.markdown("### Predictive status")
if artifacts.ml_status.state == "ready":
    ml_metrics = artifacts.ml_metrics or {}
    summary = pd.DataFrame(
        [
            {"metric": "model_name", "value": ml_metrics.get("model_name")},
            {"metric": "mae", "value": ml_metrics.get("mae")},
            {"metric": "rmse", "value": ml_metrics.get("rmse")},
            {"metric": "mape_if_applicable", "value": ml_metrics.get("mape_if_applicable")},
        ]
    )
    st.success(artifacts.ml_status.message)
    st.dataframe(summary, use_container_width=True, hide_index=True)
else:
    st.warning(artifacts.ml_status.message)
