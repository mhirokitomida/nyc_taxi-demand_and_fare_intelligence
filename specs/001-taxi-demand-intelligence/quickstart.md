# Quickstart: NYC Taxi Demand and Fare Intelligence MVP

## Objective

Executar localmente o MVP ponta a ponta: subir o stack, ingerir um recorte
controlado de Yellow Taxi, gerar silver, gold e previsoes, e abrir o dashboard
com os artefatos produzidos.

## Prerequisites

- Windows com Docker Desktop funcional
- Docker Compose disponivel no ambiente local
- Recursos locais suficientes para executar containers do Airflow, Postgres,
  Spark e Streamlit com uma janela de dados de 3 a 12 meses

## Local Stack Startup

1. Na raiz do repositorio, iniciar o stack local via `docker compose`.
2. Confirmar que os servicos principais estao ativos:
   - Airflow webserver
   - scheduler do Airflow
   - Postgres do Airflow
   - Spark master
   - pelo menos um Spark worker
   - Streamlit
3. Validar que os diretorios `data/bronze`, `data/silver`, `data/gold` e
   `data/ml` existem ou sao criados pelo fluxo.

## Access Local Services

- Abrir a interface local do Airflow para acompanhar DAGs, estados e logs
- Abrir a interface local do Streamlit para consumir os artefatos produzidos
- Consultar as interfaces do Spark, quando expostas, para depuracao operacional

## Run the Pipeline

### Step 1: Bronze ingestion

1. Selecionar um intervalo controlado entre 3 e 12 meses.
2. Acionar a DAG principal a partir do Airflow com os parametros do periodo e o
   modo de rerun desejado.
3. Verificar se os arquivos brutos foram persistidos em `data/bronze`.

**Validate**:
- arquivos esperados existem
- periodo carregado foi registrado
- logs da ingestao mostram sucesso ou falha clara por mes

### Step 2: Silver processing

1. Executar a etapa de transformacao bronze para silver.
2. Verificar se os registros invalidos foram filtrados ou sinalizados.
3. Confirmar persistencia da camada `data/silver`.

**Validate**:
- colunas obrigatorias existem
- contagem de linhas foi registrada
- nulos criticos foram tratados
- faixas invalidas de tarifa, distancia ou duracao foram bloqueadas ou
  reportadas

### Step 3: Gold processing

1. Executar a etapa silver para gold.
2. Confirmar agregacoes diarias por zona.
3. Verificar persistencia da camada `data/gold`.

**Validate**:
- metricas de demanda, corridas, tarifa, distancia e duracao existem
- agregados cobrem o periodo esperado
- logs mostram quantidades produzidas

### Step 4: ML baseline

1. Executar a etapa de treino e previsao a partir dos dados gold.
2. Confirmar que previsoes e metricas foram persistidas em `data/ml`.

**Validate**:
- previsoes diarias por zona existem
- metricas como MAE e RMSE foram geradas
- MAPE foi gerado quando aplicavel ao recorte

### Step 5: Dashboard

1. Abrir o Streamlit local.
2. Verificar indicadores, graficos e tabelas analiticas.
3. Verificar a comparacao entre previsto e observado.

**Validate**:
- dashboard abre sem preparo manual adicional
- gold e ml foram consumidos a partir dos artefatos persistidos
- ausencia de artefatos de ML e mostrada de forma clara, se ocorrer

## Rerun Guidance

- Para o mesmo periodo, usar o modo de rerun definido pela DAG antes de repetir
  a carga
- Verificar se o rerun substituiu ou regenerou somente os artefatos esperados
- Nao interpretar saidas antigas como validas sem confirmar o estado do lote

## Common Failure Modes

- Arquivo publico indisponivel para um ou mais meses do periodo escolhido
- Servico local ainda nao pronto quando a DAG ou o dashboard e acionado
- Saida intermediaria vazia, incompleta ou inconsistente
- Artefatos de ML ausentes, impedindo comparacao previsto vs observado
- Rerun executado sem limpar ou substituir corretamente os artefatos do mesmo periodo

## Expected Outcome

Ao final do quickstart, o operador deve conseguir demonstrar um fluxo local
completo, do carregamento bruto ao dashboard, usando somente dados publicos e
artefatos persistidos no proprio ambiente.
