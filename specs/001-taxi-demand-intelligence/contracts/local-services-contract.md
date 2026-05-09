# Local Services Contract

## Purpose

Descrever os servicos locais expostos para operacao do MVP.

## Expected Services

- Interface web local do Airflow
- Scheduler e componentes internos do Airflow
- Postgres dedicado aos metadados do Airflow
- Spark master
- Pelo menos um Spark worker
- Aplicacao Streamlit local

## Service Readiness Expectations

- O Airflow MUST estar acessivel antes do disparo do pipeline
- O Spark MUST estar disponivel antes das etapas de processamento e ML
- O Streamlit MUST iniciar a partir dos artefatos produzidos sem configuracao manual adicional

## Operator-Facing Interfaces

- Airflow UI para disparo e monitoramento de DAGs
- Streamlit para visualizacao final
- Spark UIs, quando expostas, apenas para acompanhamento e depuracao

## Dependency Order

1. Postgres do Airflow pronto
2. Servicos centrais do Airflow prontos
3. Spark master e worker prontos
4. Pipeline executado e artefatos gerados
5. Streamlit consumindo artefatos do pipeline
