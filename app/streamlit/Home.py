import streamlit as st


st.set_page_config(
    page_title="NYC Taxi Demand and Fare Intelligence",
    page_icon="🚕",
    layout="wide",
)

st.title("NYC Taxi Demand and Fare Intelligence")
st.caption("Local MVP shell app")

st.markdown(
    """
    This shell app confirms that the local Streamlit service is available.

    The current implementation scope is limited to:
    - local Docker Compose bootstrap
    - Airflow, Postgres, Spark, and Streamlit service readiness
    - project structure and shared configuration scaffolding

    Bronze ingestion, silver/gold processing, ML outputs, and analytical views
    are intentionally not implemented yet.
    """
)
