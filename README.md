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
- silver or gold processing
- ML pipeline
- analytical dashboard pages

## Prerequisites

- Docker Desktop running locally
- Docker Compose available in the shell
- Python 3.12 for local test execution if you want to run the initial pytest suite
- For local Python validation outside containers, install the development extra
  with `pip install -e ".[dev]"` to get `pytest` and optional `pyspark`

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

## Bronze Ingestion Validation

The bronze implementation now supports a bounded Yellow Taxi period, explicit
batch metadata, and a bronze-only Airflow DAG in `dags/bronze_ingestion_dag.py`.

Current bronze behavior:
- the ingestion period must be between 1 and 12 months
- the expected artifact URL is resolved from the public NYC TLC Yellow Taxi naming convention
- raw files are persisted under `data/bronze/<YYYY-MM>/`
- batch metadata is persisted under `data/bronze/_batch_metadata/`
- rerun behavior is explicit:
  - `rerun_mode="fail"` stops if metadata for the same period already exists
  - `rerun_mode="replace"` allows replacing the same period after removing prior batch metadata
- if an expected public artifact is unavailable, the ingestion fails explicitly

Local structural validation commands:

```powershell
pytest tests/unit/test_ingestion_config.py tests/data_quality/test_bronze_artifacts.py
```

Local DAG validation path:
- the bronze DAG should appear in Airflow with `dag_id="bronze_ingestion"`
- trigger it with a very small recorte, for example one month only

Recommended small local validation recorte:
- `start_month=2024-01`
- `end_month=2024-01`

Example local validation call from Python:

```powershell
python -c "from src.ingestion.bronze_pipeline import run_bronze_ingestion; run_bronze_ingestion('2024-01', '2024-01', rerun_mode='fail')"
```

If the current environment cannot reach the public dataset or Docker/Airflow is
not running, use the command above locally on a machine with network access and
Docker Desktop available.

## Silver and Gold Validation

The silver implementation now reads persisted bronze parquet files, validates
required Yellow Taxi columns, filters invalid records, derives time and zone
features, and writes clean outputs into `data/silver/`.

The gold implementation now reads persisted silver artifacts, aggregates daily
metrics by pickup zone, and writes analytical outputs into `data/gold/`.

Current silver behavior:
- reads persisted bronze parquet inputs for a bounded period
- rejects missing required Yellow Taxi columns
- filters invalid rows with critical nulls or invalid fare, distance, total, or duration ranges
- derives `service_date`, `pickup_hour`, `day_of_week`, `trip_duration_minutes`,
  `pickup_zone_id`, and `dropoff_zone_id`

Current gold behavior:
- reads persisted silver outputs for the same bounded period
- aggregates by `service_date` and `pickup_zone_id`
- computes `trip_count`, `total_fare`, `avg_fare`, `total_distance`,
  `avg_distance`, and `avg_duration_minutes`

Local structural validation commands:

```powershell
& 'C:\Users\mht-1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests\data_quality\test_silver_schema.py tests\data_quality\test_gold_schema.py tests\data_quality\test_value_ranges.py tests\integration\test_processing_outputs.py
```

If `pyspark` is installed locally, a bounded local run can be validated with:

```powershell
python -c "from src.processing.bronze_to_silver import run_bronze_to_silver; run_bronze_to_silver('2024-01', '2024-01', spark_master='local[1]')"
python -c "from src.processing.silver_to_gold import run_silver_to_gold; run_silver_to_gold('2024-01', '2024-01', spark_master='local[1]')"
```

Expected local outputs:
- silver artifacts under `data/silver/2024-01_to_2024-01/`
- gold artifacts under `data/gold/2024-01_to_2024-01/`

If `pyspark` is not available in the current environment, the tests still
validate schema, range rules, and pipeline wiring, while the execution commands
above can be run locally on a machine with PySpark installed.
