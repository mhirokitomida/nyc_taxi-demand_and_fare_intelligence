from __future__ import annotations

import streamlit as st

from app.streamlit.data_loader import list_gold_periods, load_dashboard_artifacts


st.set_page_config(
    page_title="NYC Taxi Demand and Fare Intelligence",
    page_icon="Taxi",
    layout="wide",
)

st.title("NYC Taxi Demand and Fare Intelligence")
st.caption("Dashboard local consumindo apenas artefatos persistidos em data/gold e data/ml")

periods = list_gold_periods()
period_labels = [period.label for period in periods]
selected_period = st.sidebar.selectbox("Periodo de dados", options=period_labels, index=len(period_labels) - 1)
artifacts = load_dashboard_artifacts(requested_period=selected_period)

st.sidebar.markdown("### Artifact Status")
st.sidebar.success(f"Gold pronto: {artifacts.period.label}")
if artifacts.ml_status.state == "ready":
    st.sidebar.success(artifacts.ml_status.message)
elif artifacts.ml_status.state in {"stale", "incomplete"}:
    st.sidebar.warning(artifacts.ml_status.message)
else:
    st.sidebar.info(artifacts.ml_status.message)

left, right = st.columns([1.3, 1.0])

with left:
    st.markdown(
        """
        ### O que este dashboard mostra

        - visao historica de corridas, tarifa, distancia e duracao a partir da camada `gold`
        - comparacao entre previsto e observado quando artefatos de ML estiverem disponiveis
        - nenhuma pagina dispara Airflow, Spark ou treinamento em tempo de uso
        """
    )

with right:
    st.markdown("### Resumo do Periodo")
    st.metric("Periodo carregado", artifacts.period.label)
    st.metric("Linhas em gold", len(artifacts.gold_frame))
    st.metric("Status de ML", artifacts.ml_status.state.upper())

st.markdown("### Navegacao")
st.info(
    "Use o menu lateral do Streamlit para abrir as paginas de Overview, Demand Trends, Operations e Forecast."
)

if artifacts.ml_status.state != "ready":
    st.warning(
        "As paginas historicas funcionam normalmente. A pagina de forecast exibira uma mensagem clara ate os artefatos de ML estarem prontos."
    )
