from __future__ import annotations

import pandas as pd
import streamlit as st

from app.streamlit.data_loader import list_gold_periods, load_dashboard_artifacts


st.title("Forecast vs Observed")
periods = list_gold_periods()
selected_period = st.sidebar.selectbox("Periodo de dados", [period.label for period in periods], index=len(periods) - 1)
artifacts = load_dashboard_artifacts(requested_period=selected_period)

if artifacts.ml_status.state != "ready" or artifacts.ml_predictions is None:
    st.warning(artifacts.ml_status.message)
    st.info("As paginas historicas continuam disponiveis mesmo sem artefatos de ML.")
else:
    forecast_frame = artifacts.ml_predictions.copy()
    forecast_frame["forecast_date"] = pd.to_datetime(forecast_frame["forecast_date"])

    daily_forecast = (
        forecast_frame.groupby("forecast_date", as_index=False)
        .agg(
            predicted_demand=("predicted_demand", "sum"),
            observed_demand=("observed_demand", "sum"),
        )
        .sort_values("forecast_date")
    )
    daily_forecast["absolute_error"] = (
        daily_forecast["observed_demand"] - daily_forecast["predicted_demand"]
    ).abs()

    metrics = artifacts.ml_metrics or {}
    metric_cols = st.columns(3)
    metric_cols[0].metric("MAE", f"{metrics.get('mae', 0):,.2f}")
    metric_cols[1].metric("RMSE", f"{metrics.get('rmse', 0):,.2f}")
    mape_value = metrics.get("mape_if_applicable")
    metric_cols[2].metric("MAPE", "N/A" if mape_value is None else f"{mape_value:,.2f}%")

    st.markdown("### Daily comparison")
    st.line_chart(daily_forecast.set_index("forecast_date")[["predicted_demand", "observed_demand"]])

    st.markdown("### Error by day")
    st.bar_chart(daily_forecast.set_index("forecast_date")["absolute_error"])

    st.markdown("### Forecast sample")
    st.dataframe(forecast_frame.head(30), use_container_width=True)
