# Implementation Plan: NYC Taxi Demand and Fare Intelligence

**Branch**: `001-taxi-demand-intelligence` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-taxi-demand-intelligence/spec.md`

## Summary

Construir um MVP local e reproduzivel que ingere dados publicos de Yellow Taxi,
persiste camadas bronze, silver, gold e ml em disco, executa orquestracao ponta
a ponta via Airflow, processa dados com PySpark, gera previsao diaria de demanda
por zona com baseline em scikit-learn e apresenta resultados analiticos e
preditivos em um dashboard Streamlit acessivel localmente.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Apache Airflow, PySpark, Streamlit, scikit-learn, pandas, pyarrow, pytest  
**Storage**: arquivos locais em `data/bronze`, `data/silver`, `data/gold` e `data/ml`; Postgres apenas para metadados do Airflow  
**Testing**: pytest, checagens leves de qualidade de dados e validacao de artefatos do pipeline  
**Target Platform**: Windows com Docker Desktop no host e containers Linux em Docker Compose  
**Project Type**: plataforma local de dados + machine learning + dashboard  
**Performance Goals**: executar o recorte controlado do MVP localmente, completar uma corrida ponta a ponta sem preparo manual extra e abrir o dashboard a partir dos artefatos gerados  
**Constraints**: sem cloud paga, sem credenciais obrigatorias, sem servicos externos privados, entregas incrementais e reversiveis, janela de dados limitada entre 3 e 12 meses  
**Scale/Scope**: Yellow Taxi parquet apenas, analise e previsao diaria por zona para o recorte inicial do MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Runs locally on Windows with Docker Desktop and does not require paid
      cloud services, private credentials, or mandatory external infrastructure
- [x] Uses Docker Compose for service orchestration and keeps Airflow as the
      primary pipeline orchestrator
- [x] Preserves or extends bronze, silver, and gold data layering with clear
      persisted artifacts and explicit affected paths
- [x] Uses PySpark for scale-oriented data processing when the feature changes
      ingestion or transformation logic beyond trivial local utilities
- [x] Keeps the MVP incremental, avoids overengineering, and defines a small,
      reversible validation step before wider rollout
- [x] Documents how the feature affects Streamlit outputs or explains why no
      user-facing dashboard impact exists
- [x] If ML is involved, states the practical use case, input/output contract,
      and local evaluation approach

**Pre-design gate result**: PASS. O plano permanece compativel com a
constitution ao manter Docker Compose, Airflow, bronze/silver/gold, PySpark,
persistencia local, Streamlit e um caso de ML pratico e explicito.

**Post-design gate result**: PASS. Os artefatos de design preservam a
arquitetura local, a separacao por camadas, a previsao diaria por zona e a
operacao sem credenciais privadas ou cloud obrigatoria.

## Project Structure

### Documentation (this feature)

```text
specs/001-taxi-demand-intelligence/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- pipeline-contract.md
|   |-- data-artifacts-contract.md
|   |-- dashboard-contract.md
|   `-- local-services-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
docker-compose.yml
README.md
config/
dags/
app/
`-- streamlit/
src/
|-- common/
|-- ingestion/
|-- processing/
`-- ml/
data/
|-- bronze/
|-- silver/
|-- gold/
`-- ml/
tests/
|-- unit/
|-- integration/
`-- data_quality/
```

**Structure Decision**: Usar uma raiz unica com `docker-compose.yml` e
separacao clara entre orquestracao (`dags/`), logica Python modular (`src/`),
dashboard (`app/streamlit/`), configuracoes (`config/`), artefatos de dados
(`data/`) e testes (`tests/`). Essa estrutura reduz acoplamento, deixa as
camadas evidentes para portfolio e suporta evolucao incremental sem introduzir
subprojetos desnecessarios.

## Complexity Tracking

Nenhuma violacao da constitution foi identificada neste plano. Nao ha
justificativa para infraestrutura adicional de cloud, streaming ou modelagem
mais complexa nesta fase.
