from __future__ import annotations

import pandas as pd
import streamlit as st

from app.streamlit.data_loader import list_gold_periods, load_dashboard_artifacts
from src.processing.analytics_views import build_daily_demand_series, build_zone_summary


st.title("Demand Trends")
periods = list_gold_periods()
selected_period = st.sidebar.selectbox("Periodo de dados", [period.label for period in periods], index=len(periods) - 1)
artifacts = load_dashboard_artifacts(requested_period=selected_period)

records = artifacts.gold_frame.to_dict(orient="records")
daily_series = pd.DataFrame(build_daily_demand_series(records))
zone_summary = pd.DataFrame(build_zone_summary(records, limit=15))

st.markdown("### Daily demand")
st.line_chart(daily_series.set_index("service_date"))

st.markdown("### Top pickup zones by rides")
st.bar_chart(zone_summary.set_index("pickup_zone_id")["trip_count"])

st.markdown("### Zone summary")
st.dataframe(zone_summary, use_container_width=True)
