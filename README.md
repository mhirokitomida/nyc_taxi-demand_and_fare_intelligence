# NYC Taxi Demand and Fare Intelligence

Local MVP scaffold for a Windows + Docker Desktop setup with Airflow, Postgres,
Spark standalone, and a Streamlit shell app.

## Current Scope

This repository currently implements only:
- base repository structure
- local data layer folders
- shared configuration and helper modules
- Docker Compose topology for Airflow, Postgres, Spark, and Streamlit
- smoke-test scaffolding for local service readiness
- Streamlit shell app

It does **not** yet implement:
- bronze ingestion
- silver or gold processing
- ML pipeline
- analytical dashboard pages

## Prerequisites

- Docker Desktop running locally
- Docker Compose available in the shell
- Python 3.12 for local test execution if you want to run the initial pytest suite

## First Validation Command

Use the following command to validate the Compose file syntax and merged service
configuration:

```powershell
docker compose config
```

Expected result:
- the Compose file renders without syntax errors
- the services `airflow-postgres`, `airflow-init`, `airflow-webserver`,
  `airflow-scheduler`, `spark-master`, `spark-worker`, and `streamlit` appear

## Start the Minimal Local Stack

Run:

```powershell
docker compose up -d
```

After startup, validate:
- Airflow health endpoint: `http://localhost:8080/health`
- Spark master UI: `http://localhost:8081`
- Streamlit health endpoint: `http://localhost:8501/_stcore/health`

## Initial Local Directories

The base implementation creates these directories for later pipeline stages:
- `data/bronze/`
- `data/silver/`
- `data/gold/`
- `data/ml/`

## Local Test Scaffolding

The initial test scaffolding includes:
- `tests/integration/test_docker_compose_structure.py`
- `tests/integration/test_service_readiness.py`
- `tests/integration/test_local_service_access.py`

`test_service_readiness.py` and `test_local_service_access.py` are skipped by
default unless you explicitly set:

```powershell
$env:RUN_LOCAL_SERVICE_CHECKS="1"
```

## Validation Notes

- `docker compose config` is the first required validation for this phase
- `docker compose up -d` is the preferred runtime validation if Docker is available
- No ingestion, processing, ML, or analytical dashboard validation is in scope yet
