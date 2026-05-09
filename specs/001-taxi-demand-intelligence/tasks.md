---

description: "Task list for implementing the NYC Taxi Demand and Fare Intelligence MVP"
---

# Tasks: NYC Taxi Demand and Fare Intelligence

**Input**: Design documents from `/specs/001-taxi-demand-intelligence/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature explicitly requires lightweight tests and validation tasks for Docker Compose, Airflow, Spark, data quality, Streamlit, and end-to-end MVP checks.

**Organization**: Tasks are grouped by phase and by user story so each increment is small, reversible, and independently verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when tasks touch different files and do not depend on incomplete outputs
- **[Story]**: User story label for story-specific phases only
- Every task includes an explicit file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the base repository structure and local validation entrypoints without implementing business logic yet.

- [X] T001 Create the base project directories in `config/`, `dags/`, `app/streamlit/`, `src/common/`, `src/ingestion/`, `src/processing/`, `src/ml/`, `tests/unit/`, `tests/integration/`, and `tests/data_quality/`
- [X] T002 Create placeholder tracking files for empty directories in `config/.gitkeep`, `dags/.gitkeep`, `app/streamlit/.gitkeep`, `src/common/.gitkeep`, `src/ingestion/.gitkeep`, `src/processing/.gitkeep`, `src/ml/.gitkeep`, `tests/unit/.gitkeep`, `tests/integration/.gitkeep`, and `tests/data_quality/.gitkeep`
- [X] T003 [P] Create the local data layer directories and placeholders in `data/bronze/.gitkeep`, `data/silver/.gitkeep`, `data/gold/.gitkeep`, and `data/ml/.gitkeep`
- [X] T004 Create the Python project baseline configuration in `pyproject.toml`
- [X] T005 [P] Create the minimal test runner configuration in `pytest.ini`
- [X] T006 [P] Create the local environment example configuration in `config/local.example.env`
- [X] T007 Document the first validation command and expected result in `README.md` for `docker compose config`

**Checkpoint**: Base structure, Python metadata, and empty local data layers exist before service configuration begins.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the local platform contract that all user stories rely on.

- [X] T008 Create the initial Docker Compose topology in `docker-compose.yml` with service placeholders for Airflow, Postgres, Spark master, Spark worker, and Streamlit
- [X] T009 [P] Create the shared project settings module in `src/common/settings.py`
- [X] T010 [P] Create the shared path and artifact location helpers in `src/common/paths.py`
- [X] T011 [P] Create the shared logging utilities in `src/common/logging_utils.py`
- [X] T012 Create the shared data validation helpers in `src/common/data_checks.py`
- [X] T013 Create the Airflow environment configuration file in `config/airflow.env`
- [X] T014 [P] Create the Spark environment configuration file in `config/spark.env`
- [X] T015 [P] Create the Streamlit environment configuration file in `config/streamlit.env`
- [X] T016 Create the service-readiness smoke validation script in `tests/integration/test_service_readiness.py`
- [X] T017 Add the first Compose validation task for `docker compose config` coverage in `tests/integration/test_compose_config.md`

**Checkpoint**: Foundational service topology, shared config modules, and readiness validation scaffolding are in place.

---

## Phase 3: User Story 1 - Subir o ambiente local (Priority: P1) MVP

**Goal**: Make the minimal local environment bootable and verifiable through Docker Compose.

**Independent Test**: Run `docker compose config` and `docker compose up`, then confirm local availability of the core Airflow, Spark, and Streamlit services.

### Tests for User Story 1

- [X] T018 [P] [US1] Add a Compose structure validation test in `tests/integration/test_docker_compose_structure.py`
- [X] T019 [P] [US1] Add an Airflow and Streamlit accessibility smoke test in `tests/integration/test_local_service_access.py`

### Implementation for User Story 1

- [X] T020 [US1] Define the Airflow webserver, scheduler, and Postgres services in `docker-compose.yml`
- [X] T021 [US1] Define the Spark master and worker services in `docker-compose.yml`
- [X] T022 [US1] Define the Streamlit service shell in `docker-compose.yml`
- [X] T023 [P] [US1] Create the Airflow healthcheck and startup notes in `config/airflow.env`
- [X] T024 [P] [US1] Create the Spark local cluster startup notes in `config/spark.env`
- [X] T025 [P] [US1] Create the Streamlit startup notes in `config/streamlit.env`
- [X] T026 [US1] Create the first Streamlit shell entrypoint in `app/streamlit/Home.py`
- [X] T027 [US1] Document the `docker compose up` validation flow in `README.md`

**Checkpoint**: The local stack can be started and checked independently before any data pipeline logic is added.

---

## Phase 4: User Story 2 - Ingerir dados brutos em bronze (Priority: P1)

**Goal**: Download a bounded Yellow Taxi slice and persist raw monthly artifacts in bronze with traceable batch metadata.

**Independent Test**: Trigger the bronze flow for a small bounded period and confirm raw files and batch registration artifacts exist in `data/bronze/`.

### Tests for User Story 2

- [X] T028 [P] [US2] Add a bounded-period ingestion config validation test in `tests/unit/test_ingestion_config.py`
- [X] T029 [P] [US2] Add a bronze artifact existence validation test in `tests/data_quality/test_bronze_artifacts.py`

### Implementation for User Story 2

- [X] T030 [P] [US2] Create the ingestion period configuration module in `src/ingestion/period_config.py`
- [X] T031 [P] [US2] Create the public Yellow Taxi source resolver in `src/ingestion/source_catalog.py`
- [X] T032 [P] [US2] Create the bronze download client in `src/ingestion/downloader.py`
- [X] T033 [US2] Create the batch metadata registration module in `src/ingestion/batch_registry.py`
- [X] T034 [US2] Create the bronze ingestion orchestrator in `src/ingestion/bronze_pipeline.py`
- [X] T035 [US2] Add bronze-specific logging and failure signaling in `src/ingestion/bronze_pipeline.py`
- [X] T036 [US2] Create the bronze-only DAG task file in `dags/bronze_ingestion_dag.py`
- [X] T037 [US2] Document bronze file existence checks under `data/bronze/` in `README.md`

**Checkpoint**: A bounded raw data slice can be ingested and verified without silver, gold, or ML.

---

## Phase 5: User Story 3 - Gerar silver e gold reproduziveis (Priority: P1)

**Goal**: Transform bronze into clean silver records and daily-by-zone gold aggregates with reproducible validations.

**Independent Test**: Starting from a valid bronze slice, generate silver and gold, then verify required columns, row counts, and persisted artifacts in `data/silver/` and `data/gold/`.

### Tests for User Story 3

- [X] T038 [P] [US3] Add a silver schema validation test in `tests/data_quality/test_silver_schema.py`
- [X] T039 [P] [US3] Add a gold aggregate schema validation test in `tests/data_quality/test_gold_schema.py`
- [X] T040 [P] [US3] Add invalid fare, distance, and duration range tests in `tests/data_quality/test_value_ranges.py`
- [X] T041 [P] [US3] Add a silver-to-gold row count and non-empty output test in `tests/integration/test_processing_outputs.py`

### Implementation for User Story 3

- [X] T042 [P] [US3] Create the bronze reader module in `src/processing/read_bronze.py`
- [X] T043 [P] [US3] Create the required-column validation module in `src/processing/validate_bronze_schema.py`
- [X] T044 [P] [US3] Create the invalid-record filtering module in `src/processing/filter_invalid_trips.py`
- [X] T045 [P] [US3] Create the derived trip feature builder in `src/processing/derive_trip_features.py`
- [X] T046 [US3] Create the bronze-to-silver pipeline entrypoint in `src/processing/bronze_to_silver.py`
- [X] T047 [US3] Create the silver artifact writer in `src/processing/write_silver.py`
- [X] T048 [P] [US3] Create the daily-by-zone aggregate builder in `src/processing/build_gold_daily_zone.py`
- [X] T049 [P] [US3] Create the gold artifact writer in `src/processing/write_gold.py`
- [X] T050 [US3] Create the silver-to-gold pipeline entrypoint in `src/processing/silver_to_gold.py`
- [X] T051 [US3] Add processing logs and layer validation hooks in `src/processing/silver_to_gold.py`
- [X] T052 [US3] Document silver and gold file verification checks in `README.md`

**Checkpoint**: Silver and gold outputs are reproducible and independently verifiable from a bronze input slice.

---

## Phase 6: User Story 4 - Consultar métricas analíticas (Priority: P2)

**Goal**: Expose stable analytical outputs for downstream consumption and contract validation.

**Independent Test**: Read the gold outputs through stable helpers and verify that all required analytical fields for rides, fares, demand, distance, and duration are available by day and zone.

### Tests for User Story 4

- [X] T053 [P] [US4] Add a gold contract validation test in `tests/data_quality/test_gold_contract.py`
- [X] T054 [P] [US4] Add an analytical reader integration test in `tests/integration/test_gold_readers.py`

### Implementation for User Story 4

- [X] T055 [P] [US4] Create the gold dataset reader helpers in `src/common/read_gold_artifacts.py`
- [X] T056 [P] [US4] Create the KPI extraction helpers in `src/processing/analytics_views.py`
- [X] T057 [US4] Create the gold contract verification module in `src/processing/validate_gold_contract.py`
- [X] T058 [US4] Document analytical output expectations in `README.md`

**Checkpoint**: Gold artifacts satisfy the analytical contract before ML and dashboard layers depend on them.

---

## Phase 7: User Story 6 - Avaliar previsão de demanda (Priority: P3)

**Goal**: Build and validate a daily-by-zone demand forecasting baseline from gold outputs.

**Independent Test**: Starting from gold artifacts, generate training slices, forecasts, and evaluation summaries in `data/ml/`, then confirm MAE and RMSE are present and MAPE is included when applicable.

### Tests for User Story 6

- [X] T059 [P] [US6] Add an ML feature dataset validation test in `tests/data_quality/test_ml_feature_dataset.py`
- [X] T060 [P] [US6] Add an ML artifact existence and metrics validation test in `tests/data_quality/test_ml_outputs.py`
- [X] T061 [P] [US6] Add a forecast pipeline integration test in `tests/integration/test_ml_pipeline.py`

### Implementation for User Story 6

- [X] T062 [P] [US6] Create the gold-to-ML dataset builder in `src/ml/build_training_slice.py`
- [X] T063 [P] [US6] Create the baseline demand model module in `src/ml/train_baseline_model.py`
- [X] T064 [P] [US6] Create the forecast generation module in `src/ml/generate_forecast.py`
- [X] T065 [P] [US6] Create the evaluation metrics module in `src/ml/evaluate_forecast.py`
- [X] T066 [US6] Create the ML pipeline entrypoint in `src/ml/run_ml_pipeline.py`
- [X] T067 [US6] Create the ML artifact writer in `src/ml/write_ml_outputs.py`
- [X] T068 [US6] Document MAE, RMSE, and MAPE validation checks in `README.md`

**Checkpoint**: Demand forecasting works independently from persisted gold artifacts before the dashboard depends on ML outputs.

---

## Phase 8: User Story 5 - Explorar o dashboard local (Priority: P2)

**Goal**: Present analytical and predictive outputs through a local Streamlit dashboard that requires no manual data preparation.

**Independent Test**: Open the local Streamlit app and verify KPI, trend, operational metrics, and predicted-vs-observed views from persisted `data/gold/` and `data/ml/`.

### Tests for User Story 5

- [ ] T069 [P] [US5] Add a dashboard input contract test for gold and ML artifacts in `tests/integration/test_dashboard_inputs.py`
- [ ] T070 [P] [US5] Add a Streamlit startup smoke test in `tests/integration/test_streamlit_startup.py`

### Implementation for User Story 5

- [ ] T071 [P] [US5] Create the dashboard data loading helpers in `app/streamlit/data_loader.py`
- [ ] T072 [P] [US5] Create the KPI and summary page in `app/streamlit/pages/01_overview.py`
- [ ] T073 [P] [US5] Create the demand trends page in `app/streamlit/pages/02_demand_trends.py`
- [ ] T074 [P] [US5] Create the fares, distance, and duration page in `app/streamlit/pages/03_operations.py`
- [ ] T075 [P] [US5] Create the predicted-vs-observed page in `app/streamlit/pages/04_forecast.py`
- [ ] T076 [US5] Add missing or stale ML artifact handling in `app/streamlit/data_loader.py`
- [ ] T077 [US5] Document the Streamlit access and smoke check flow in `README.md`

**Checkpoint**: The dashboard consumes persisted outputs only and remains blocked until gold and ML artifacts are available.

---

## Phase 9: End-to-End DAG Orchestration

**Purpose**: Connect the validated bronze, silver, gold, and ML steps into one bounded Airflow DAG.

- [ ] T078 Create the shared DAG parameter schema for bounded periods and rerun mode in `dags/_dag_params.py`
- [ ] T079 [P] Create the DAG task wrappers for bronze execution in `dags/tasks_bronze.py`
- [ ] T080 [P] Create the DAG task wrappers for silver and gold execution in `dags/tasks_processing.py`
- [ ] T081 [P] Create the DAG task wrappers for ML execution in `dags/tasks_ml.py`
- [ ] T082 Create the end-to-end MVP DAG in `dags/nyc_taxi_mvp_dag.py`
- [ ] T083 Create the DAG visibility and dependency validation test in `tests/integration/test_airflow_dag_definition.py`
- [ ] T084 Document the DAG trigger and verification flow in `README.md`

**Checkpoint**: The full Airflow DAG is visible locally and reflects bronze -> silver -> gold -> ml ordering.

---

## Phase 10: Tests and Data Quality

**Purpose**: Strengthen automated validation across shared modules and persisted layers.

- [ ] T085 [P] Add shared settings and path helper unit tests in `tests/unit/test_common_settings.py`
- [ ] T086 [P] Add ingestion module unit tests in `tests/unit/test_ingestion_modules.py`
- [ ] T087 [P] Add processing module unit tests in `tests/unit/test_processing_modules.py`
- [ ] T088 [P] Add ML module unit tests in `tests/unit/test_ml_modules.py`
- [ ] T089 Add an end-to-end data layer existence validation test in `tests/data_quality/test_layer_artifact_presence.py`
- [ ] T090 Add a critical nulls validation test across silver and gold outputs in `tests/data_quality/test_critical_nulls.py`
- [ ] T091 Add a row count sanity validation test across bronze, silver, and gold in `tests/data_quality/test_row_count_sanity.py`
- [ ] T092 Document the standard `pytest` validation command flow in `README.md`

**Checkpoint**: Automated validations cover shared utilities, data quality constraints, and artifact presence before final MVP sign-off.

---

## Phase 11: README and Local Documentation

**Purpose**: Make the MVP runnable by a new evaluator from zero using only local documentation.

- [ ] T093 Consolidate local prerequisites, startup commands, and service URLs in `README.md`
- [ ] T094 Document the bounded Yellow Taxi ingestion workflow in `README.md`
- [ ] T095 Document silver, gold, and ML validation expectations in `README.md`
- [ ] T096 Document dashboard usage and failure modes in `README.md`
- [ ] T097 Document rerun guidance and troubleshooting notes in `README.md`

**Checkpoint**: The README is aligned with `quickstart.md` and can drive a clean local run without hidden assumptions.

---

## Phase 12: Final MVP Validation

**Purpose**: Verify the full MVP contract before considering implementation complete.

- [ ] T098 Run and record `docker compose config` and `docker compose up` validation results in `README.md`
- [ ] T099 Verify local Airflow DAG visibility and service readiness using `tests/integration/test_local_service_access.py`
- [ ] T100 Verify bounded bronze ingestion outputs under `data/bronze/` using `tests/data_quality/test_bronze_artifacts.py`
- [ ] T101 Verify silver and gold outputs under `data/silver/` and `data/gold/` using `tests/data_quality/test_silver_schema.py` and `tests/data_quality/test_gold_schema.py`
- [ ] T102 Verify ML outputs under `data/ml/` using `tests/data_quality/test_ml_outputs.py`
- [ ] T103 Verify Streamlit accessibility and dashboard rendering using `tests/integration/test_streamlit_startup.py`
- [ ] T104 Verify the MVP remains free of paid services, private credentials, and cloud-only dependencies by updating `README.md`

**Checkpoint**: The MVP is locally demonstrable end-to-end and compliant with the project constitution.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on Phase 3 because the environment must boot first
- **Phase 5: US3**: Depends on Phase 4 because bronze artifacts must exist first
- **Phase 6: US4**: Depends on Phase 5 because analytical outputs come from gold
- **Phase 7: US6**: Depends on Phase 5 and should follow US4 contract validation
- **Phase 8: US5**: Depends on Phases 6 and 7 because dashboard reads gold and ml outputs
- **Phase 9: End-to-End DAG**: Depends on Phases 4 through 8
- **Phase 10: Tests and Data Quality**: Can expand after Phases 4 through 9, but final completion depends on core flows existing
- **Phase 11: README and Documentation**: Can start early, but final pass depends on validated behavior from prior phases
- **Phase 12: Final MVP Validation**: Depends on all prior phases

### User Story Dependencies

- **US1**: Minimal local environment and service readiness
- **US2**: Requires US1 because bronze ingestion depends on a working local stack
- **US3**: Requires US2 because silver and gold depend on bronze artifacts
- **US4**: Requires US3 because analytical outputs are gold artifacts
- **US6**: Requires US3 because ML depends on gold artifacts
- **US5**: Requires US4 and US6 because the dashboard depends on both analytical and predictive outputs

### Within Each User Story

- Validation tasks come before or alongside implementation when they can be defined independently
- Data artifacts must exist before downstream consumers are built
- Logging and validation must be added before a phase is considered complete
- Each story phase must end with a concrete checkpoint before advancing

### Parallel Opportunities

- T003 and T005-T006 can run in parallel after T001-T002
- T009-T015 can run in parallel after T008 where file ownership does not overlap
- Story-specific validation tests marked `[P]` can run in parallel within each phase
- T030-T032 can run in parallel before T033-T036 in US2
- T042-T045 can run in parallel before T046-T051 in US3
- T048-T049 can run in parallel after silver outputs are defined
- T055-T056 can run in parallel in US4
- T062-T065 can run in parallel before T066-T067 in US6
- T072-T075 can run in parallel after T071 in US5
- T079-T081 can run in parallel before T082 in Phase 9
- T085-T088 can run in parallel in Phase 10

---

## Parallel Example: User Story 3

```bash
# Validation tasks for silver and gold can run in parallel:
Task: "Add a silver schema validation test in tests/data_quality/test_silver_schema.py"
Task: "Add a gold aggregate schema validation test in tests/data_quality/test_gold_schema.py"
Task: "Add invalid fare, distance, and duration range tests in tests/data_quality/test_value_ranges.py"

# Independent processing modules can also be built in parallel:
Task: "Create the bronze reader module in src/processing/read_bronze.py"
Task: "Create the required-column validation module in src/processing/validate_bronze_schema.py"
Task: "Create the invalid-record filtering module in src/processing/filter_invalid_trips.py"
Task: "Create the derived trip feature builder in src/processing/derive_trip_features.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1
4. **STOP and VALIDATE** the local stack with `docker compose config` and `docker compose up`
5. Complete Phase 4: US2 and validate bounded bronze ingestion
6. Complete Phase 5: US3 and validate silver and gold artifacts

### Incremental Delivery

1. Environment first: local stack bootable
2. Bronze next: public data lands in `data/bronze/`
3. Silver and gold next: reproducible analytical layers exist
4. ML next: daily-by-zone baseline persists outputs to `data/ml/`
5. Dashboard next: Streamlit consumes `data/gold/` and `data/ml/`
6. Full DAG next: orchestration is assembled over already validated components
7. Final validation and documentation last

### Suggested MVP Stop Point

The first meaningful delivery stop point is after **Phase 3 (US1)**, when the
local environment boots successfully with Docker Compose and core services are
reachable.

---

## Notes

- Every task includes an explicit file path
- Story phases use `[US#]` labels; setup, foundational, orchestration, documentation, and final validation phases do not
- The story phase order intentionally puts `US6` before `US5` because ML outputs must exist before the dashboard depends on them
- Avoid bundling unrelated file changes into one task when implementing this list
