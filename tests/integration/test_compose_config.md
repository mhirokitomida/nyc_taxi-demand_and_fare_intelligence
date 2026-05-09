# Docker Compose Validation Coverage

Use this validation note together with `docker compose config` after editing
`docker-compose.yml`.

Expected checks:
- Compose file parses without syntax errors
- Required services exist: Airflow, Postgres, Spark master, Spark worker, Streamlit
- Local ports are exposed for Airflow (`8080`), Spark master (`7077`, `8081`), and Streamlit (`8501`)
