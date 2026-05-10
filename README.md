# NYC Taxi Demand and Fare Intelligence

Projeto de portfolio local, gratuito e reproduzivel para engenharia de dados,
machine learning e dashboard usando dados publicos da NYC TLC Yellow Taxi.

O MVP roda localmente no Windows com Docker Desktop e usa:
- Docker Compose para orquestracao local
- Apache Airflow para orquestrar o pipeline
- PySpark para processamento bronze -> silver -> gold
- scikit-learn para um baseline de previsao diaria de demanda por zona
- Streamlit para o dashboard final

Nao ha dependencia obrigatoria de cloud paga, credenciais privadas ou servicos
externos nao publicos.

## O que o MVP entrega

- download de dados publicos da NYC TLC Yellow Taxi em Parquet
- persistencia local em `data/bronze`, `data/silver`, `data/gold` e `data/ml`
- pipeline ponta a ponta `bronze -> silver -> gold -> ml`
- DAG principal `nyc_taxi_mvp` no Airflow
- dashboard Streamlit consumindo apenas artefatos persistidos
- modelo `lakehouse-light` com versionamento por `run_id` e manifest `latest`

## Stack e arquitetura local

### Servicos locais

- Airflow Webserver
- Airflow Scheduler
- Postgres para metadados do Airflow
- Spark Master
- Spark Worker
- Streamlit

### URLs locais

- Airflow UI: `http://localhost:8080`
- Spark Master UI: `http://localhost:18080`
- Spark Worker UI: `http://localhost:18081`
- Streamlit: `http://localhost:8501`

### Credenciais locais do Airflow

- usuario: `admin`
- senha: `admin`

Essas credenciais sao apenas para uso local do MVP.

## Estrutura principal

```text
docker-compose.yml
Dockerfile.airflow
requirements-airflow.txt
config/
dags/
app/streamlit/
src/common/
src/ingestion/
src/processing/
src/ml/
tests/unit/
tests/data_quality/
tests/integration/
data/
  bronze/
  silver/
  gold/
  ml/
```

## Lakehouse-light

As camadas derivadas nao sobrescrevem mais diretamente o diretorio estavel do
periodo. Cada execucao gera uma versao nova em `runs/<run_id>` e atualiza um
manifest `_manifest.json` com o `latest`.

Exemplo:

```text
data/silver/2024-01_to_2024-01/
  runs/
    <safe_run_id>/
      part-*.parquet
      _SUCCESS
  _manifest.json

data/gold/2024-01_to_2024-01/
  runs/
    <safe_run_id>/
      part-*.parquet
      _SUCCESS
  _manifest.json

data/ml/2024-01_to_2024-01/
  runs/
    <safe_run_id>/
      training_slice.parquet
      forecast_predictions.parquet
      evaluation_metrics.json
      run_metadata.json
  _manifest.json
```

Manifest atual por camada:
- `layer`
- `period_id`
- `latest_run_id`
- `latest_path`
- `created_at`
- `status`
- `row_count`, quando disponivel
- `source_paths`, quando aplicavel

Semantica de rerun:
- `rerun_mode="fail"`: falha se a camada/periodo ja tiver manifest valido
- `rerun_mode="replace"`: cria nova versao e atualiza o `latest`, sem apagar as antigas

## Dados publicos

Fonte do MVP:
- NYC TLC Yellow Taxi Parquet
- base publica: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

O pipeline baixa os arquivos publicos esperados por mes. Se um arquivo esperado
nao estiver disponivel, a ingestao falha explicitamente.

O MVP foi validado operacionalmente com uma janela pequena de `2024-01` para
manter a execucao local mais rapida e demonstravel, mas a DAG `nyc_taxi_mvp`
aceita periodos historicos longos quando houver tempo de execucao, disco e
compatibilidade de schema para isso.

## Requisitos

### Para rodar o stack principal

- Windows com Docker Desktop iniciado
- Docker Compose disponivel

### Para rodar testes Python localmente

- Python 3.12
- instalar dependencias locais com:

```powershell
python -m pip install -e ".[dev]"
```

Isso instala as dependencias de desenvolvimento, incluindo `pytest`,
`pyarrow` e `pyspark` para validacoes locais opcionais fora dos containers.

## Build e subida do ambiente

### 1. Validar o Compose

```powershell
docker compose config
```

### 2. Build da imagem customizada do Airflow

```powershell
docker compose build airflow-webserver airflow-scheduler airflow-init
```

### 3. Subir o stack

```powershell
docker compose up -d
```

### 4. Verificar import errors no Airflow

```powershell
docker compose exec airflow-webserver airflow dags list-import-errors
```

Resultado esperado:
- `No data found`

### 5. Verificar DAGs

```powershell
docker compose exec airflow-webserver airflow dags list
```

Resultado esperado:
- `bronze_ingestion`
- `nyc_taxi_mvp`

## Fluxo completo do MVP

### 1. Bronze

Responsabilidade:
- baixar um recorte controlado de Yellow Taxi
- persistir os arquivos brutos em `data/bronze`
- registrar batch metadata

Entradas:
- `start_month`
- `end_month`
- `rerun_mode`

Saidas:
- `data/bronze/<YYYY-MM>/yellow_tripdata_<YYYY-MM>.parquet`
- `data/bronze/_batch_metadata/*.json`

### 2. Silver

Responsabilidade:
- ler bronze com PySpark
- validar colunas esperadas
- filtrar registros invalidos
- derivar `service_date`, `pickup_hour`, `day_of_week`, `trip_duration_minutes` e zonas

Saida:
- `data/silver/<period_id>/runs/<run_id>/`
- `data/silver/<period_id>/_manifest.json`

### 3. Gold

Responsabilidade:
- agregar por `service_date` e `pickup_zone_id`
- calcular demanda, corridas, tarifa, distancia e duracao

Saida:
- `data/gold/<period_id>/runs/<run_id>/`
- `data/gold/<period_id>/_manifest.json`

### 4. ML

Responsabilidade:
- ler `gold` via manifest `latest`
- montar dataset de treino
- treinar baseline simples e interpretavel
- gerar previsoes e metricas

Saida:
- `data/ml/<period_id>/runs/<run_id>/`
- `data/ml/<period_id>/_manifest.json`

### 5. Dashboard

Responsabilidade:
- consumir artefatos de `gold` e `ml`
- separar analise historica de resultados preditivos
- funcionar sem disparar Airflow, Spark ou treinamento

## DAG ponta a ponta no Airflow

DAG principal:
- `nyc_taxi_mvp`

Ordem obrigatoria:
- `run_bronze_ingestion`
- `run_bronze_to_silver`
- `run_silver_to_gold`
- `run_ml_pipeline`

Payload recomendado para o MVP:

```json
{
  "start_month": "2024-01",
  "end_month": "2024-01",
  "rerun_mode": "replace",
  "target_layers": ["bronze", "silver", "gold", "ml"]
}
```

Payload de exemplo para historico longo:

```json
{
  "start_month": "2009-01",
  "end_month": "2026-02",
  "rerun_mode": "replace",
  "target_layers": ["bronze", "silver", "gold", "ml"]
}
```

Observacoes para historico longo:
- a DAG aceita periodos mensais continuos acima de 12 meses
- o tempo de execucao cresce com o volume total baixado e processado
- o uso de disco local cresce em `data/bronze`, `data/silver`, `data/gold` e `data/ml`
- dados historicos mais antigos podem exigir atencao extra a variacoes de schema da NYC TLC

Validacao manual sugerida:
1. Abrir Airflow em `http://localhost:8080`
2. Confirmar que `nyc_taxi_mvp` aparece sem import errors
3. Acionar a DAG com o payload acima
4. Confirmar geracao de artefatos em `data/bronze`, `data/silver`, `data/gold` e `data/ml`

## Dashboard

O dashboard fica em:
- `app/streamlit/Home.py`

Paginas do MVP:
- Overview
- Demand Trends
- Operations
- Forecast

Comando local alternativo para rodar Streamlit fora do container:

```powershell
python -m streamlit run app/streamlit/Home.py --server.address 127.0.0.1 --server.port 8501
```

Comportamento esperado:
- carrega `gold` via manifest `latest`
- carrega `ml` via manifest `latest`, quando disponivel
- mostra estado claro quando os artefatos de ML estiverem ausentes, incompletos ou desatualizados

## Suite principal de validacao

Comando principal:

```powershell
pytest tests/unit tests/data_quality tests/integration/test_gold_readers.py tests/integration/test_ml_pipeline.py tests/integration/test_dashboard_inputs.py tests/integration/test_airflow_dag_definition.py
```

Validacoes cobertas:
- modulos comuns
- ingestao
- processamento
- ML
- manifests e `latest_path`
- presenca de artefatos por camada
- nulos criticos em silver e gold
- sanidade de row counts entre bronze, silver e gold
- leitura de gold real
- leitura de ML real
- entradas do dashboard
- definicao e dependencias da DAG

Observacoes:
- testes que dependem de artefatos locais em `data/` fazem skip explicito quando o artefato nao existe
- o teste de integracao local com PySpark pode fazer skip quando Java local nao estiver disponivel
- os testes evitam depender de nomes exatos de `part-*.parquet`

## Estado real implementado

O MVP implementado hoje inclui:
- stack local com Docker Compose
- imagem customizada do Airflow com dependencias de pipeline
- ingestao bronze
- processamento silver e gold
- baseline de ML
- dashboard Streamlit
- DAG ponta a ponta no Airflow
- modelo `lakehouse-light` com versionamento e manifest

Fora do escopo atual:
- deploy em cloud
- streaming real-time
- deep learning
- otimizacoes avancadas de Spark

## Limitacoes do MVP

- janela local de dados ainda pequena para um caso de uso mais robusto de ML
- embora a DAG aceite historico longo, o MVP foi validado manualmente com um recorte pequeno
- baseline de ML propositalmente simples e interpretavel
- `MAPE` pode ficar muito sensivel quando a demanda observada e baixa
- ambiente Windows + OneDrive pode introduzir peculiaridades de permissao em bind mounts

## Troubleshooting

### Docker Desktop nao iniciado

Sintoma:
- `docker compose` falha ao conectar no daemon

Acao:
- iniciar o Docker Desktop
- aguardar o daemon ficar pronto
- rerodar `docker compose config` e `docker compose up -d`

### Imagem Spark

Problema historico:
- `bitnami/spark` deixou de ser uma opcao publica viavel

Estado atual:
- o projeto usa `spark:3.5.8-python3`

### Healthcheck do Spark

Estado atual:
- master testa conexao TCP com `spark-master:7077` via `python3`
- UIs expostas em:
  - master: `18080`
  - worker: `18081`

### Airflow sem dependencias Python

Sintoma:
- `airflow dags list-import-errors` mostra falta de `sklearn`, `pandas`, `pyspark` ou similares

Estado atual:
- isso foi resolvido via `Dockerfile.airflow` e `requirements-airflow.txt`

Acao:

```powershell
docker compose build airflow-webserver airflow-scheduler airflow-init
docker compose up -d airflow-webserver airflow-scheduler
docker compose exec airflow-webserver airflow dags list-import-errors
```

### Problemas de PYTHONPATH no Airflow

Sintoma:
- DAGs nao conseguem importar `src.*`

Estado atual:
- os servicos Airflow usam `PYTHONPATH=/opt/airflow`
- `./src` esta montado em `/opt/airflow/src`
- `./dags` esta montado em `/opt/airflow/dags`
- `./data` esta montado em `/opt/airflow/data`

### Java local ausente para teste PySpark fora de container

Sintoma:
- erro `JAVA_GATEWAY_EXITED`

Comportamento esperado:
- o teste local de integracao com PySpark faz skip explicito quando Java nao esta disponivel
- isso nao bloqueia o fluxo principal do MVP, que roda em containers

### Permissoes em OneDrive e bind mounts

Problema encontrado:
- bind mounts em Windows/OneDrive podem falhar ao apagar ou criar arquivos/diretorios em caminhos de Spark e Airflow

Mitigacao aplicada:
- camadas derivadas agora usam versoes por `run_id` e manifest `latest`, evitando `overwrite` destrutivo do Spark

Observacao operacional:
- dependendo do ambiente local, diretorios `runs/` e arquivos `_manifest.json` podem exigir atencao extra de permissao no host

## Dados versionados no Git

Os artefatos de `data/` nao sao versionados no Git.

O `.gitignore` ignora:
- `data/bronze/**`
- `data/silver/**`
- `data/gold/**`
- `data/ml/**`

Somente os `.gitkeep` de cada camada permanecem rastreados.

## Melhorias futuras

- ampliar a janela de dados para varios meses adicionais
- melhorar o baseline de ML com mais features temporais
- adicionar comparacoes entre multiplos modelos simples
- incluir mais visualizacoes no dashboard
- endurecer ainda mais a automacao operacional do Airflow em Windows/OneDrive
- avaliar formatos/abstracoes lakehouse mais avancados no futuro, sem sair do modelo local e gratuito

## Validacao final do MVP

Ultima validacao consolidada deste MVP:

- `pytest tests/unit tests/data_quality tests/integration/test_gold_readers.py tests/integration/test_ml_pipeline.py tests/integration/test_dashboard_inputs.py tests/integration/test_airflow_dag_definition.py`
  - resultado: `50 passed`
- `pytest tests/integration/test_local_service_access.py` com `RUN_LOCAL_SERVICE_CHECKS=1`
  - resultado: `2 passed`
- `pytest tests/integration/test_streamlit_startup.py`
  - resultado: `1 passed`
- `docker compose config`
  - resultado: Compose valido
- `docker compose exec airflow-webserver airflow dags list-import-errors`
  - resultado: `No data found`
- `docker compose exec airflow-webserver airflow dags list`
  - resultado: `bronze_ingestion` e `nyc_taxi_mvp` visiveis

Estado final confirmado:
- Airflow, Spark, Streamlit, bronze, silver, gold, ML e dashboard estao coerentes com o README
- a DAG `nyc_taxi_mvp` esta carregando sem import errors
- o dashboard tem comando de validacao documentado e smoke test automatizado
- `data/` continua ignorado pelo Git
- o README nao promete cloud, deploy ou streaming real-time

Limitacao residual conhecida:
- o MVP esta funcional e demonstravel, mas ambientes Windows com OneDrive ainda
  podem exigir atencao adicional para permissoes de bind mounts em algumas
  operacoes de escrita dos containers
