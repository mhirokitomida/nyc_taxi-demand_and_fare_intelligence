# Data Model: NYC Taxi Demand and Fare Intelligence

## Overview

O MVP usa entidades orientadas a artefatos persistidos e saídas analiticas.
Cada etapa do pipeline transforma um conjunto controlado de dados de Yellow Taxi
ate chegar em agregados diarios por zona e resultados de previsao de demanda.

## Entities

### IngestionBatch

**Purpose**: Representa um lote logico de ingestao para uma janela controlada do MVP.

**Fields**:
- `batch_id`: identificador unico do lote
- `source_name`: nome da fonte publica carregada
- `start_month`: primeiro mes do intervalo solicitado
- `end_month`: ultimo mes do intervalo solicitado
- `loaded_at`: data e hora de conclusao da carga
- `status`: estado atual do lote

**Validation Rules**:
- `batch_id` MUST ser unico
- `start_month` MUST ser menor ou igual a `end_month`
- `status` MUST pertencer ao conjunto previsto de estados

### BronzeTaxiFile

**Purpose**: Representa um arquivo bruto preservado na camada bronze.

**Fields**:
- `batch_id`: referencia ao lote de ingestao
- `year_month`: competencia do arquivo
- `source_uri`: origem publica do arquivo
- `local_path`: caminho persistido localmente
- `row_count_if_known`: contagem de linhas, quando disponivel
- `load_status`: estado de download e persistencia

**Validation Rules**:
- `batch_id`, `year_month`, `source_uri` e `local_path` MUST existir
- `load_status` MUST indicar sucesso ou falha explicitamente

### SilverTripRecord

**Purpose**: Representa uma corrida limpa e pronta para analise.

**Fields**:
- `pickup_datetime`
- `dropoff_datetime`
- `service_date`
- `pickup_hour`
- `day_of_week`
- `pickup_zone_id`
- `dropoff_zone_id`
- `trip_distance`
- `fare_amount`
- `total_amount`
- `trip_duration_minutes`
- `passenger_count`
- `payment_type`

**Validation Rules**:
- colunas temporais, zona de embarque, distancia, tarifa e duracao MUST existir
- `trip_distance`, `fare_amount` e `trip_duration_minutes` MUST ser nao negativos
- registros com nulos criticos em campos necessarios para analise MUST ser
  descartados ou sinalizados antes de seguir para gold

### GoldDailyZoneDemand

**Purpose**: Representa o agregado analitico diario por zona usado em dashboard e ML.

**Fields**:
- `service_date`
- `pickup_zone_id`
- `trip_count`
- `total_fare`
- `avg_fare`
- `total_distance`
- `avg_distance`
- `avg_duration_minutes`

**Validation Rules**:
- `service_date` e `pickup_zone_id` MUST identificar unicamente cada agregado
- `trip_count` MUST ser maior que zero
- metricas agregadas MUST ser derivadas apenas de registros silver validos

### ForecastTrainingSlice

**Purpose**: Representa a fatia preparada para treino ou avaliacao de previsao.

**Fields**:
- `service_date`
- `pickup_zone_id`
- `feature_window_id`
- `observed_demand`

**Validation Rules**:
- `observed_demand` MUST ser inteiro ou numerico nao negativo
- `feature_window_id` MUST permitir rastrear a janela de dados usada

### DemandForecastResult

**Purpose**: Representa previsoes geradas para o alvo diario por zona.

**Fields**:
- `forecast_date`
- `pickup_zone_id`
- `predicted_demand`
- `observed_demand`
- `model_name`
- `run_id`

**Validation Rules**:
- `predicted_demand` MUST ser nao negativo
- `run_id` MUST ligar previsoes ao processo de avaliacao correspondente

### ModelEvaluationSummary

**Purpose**: Representa o resumo de qualidade do baseline preditivo.

**Fields**:
- `run_id`
- `model_name`
- `evaluation_window`
- `mae`
- `rmse`
- `mape_if_applicable`

**Validation Rules**:
- `mae` e `rmse` MUST existir
- `mape_if_applicable` MAY ficar ausente quando a metrica nao for apropriada

## Relationships

- Um `IngestionBatch` produz um ou mais `BronzeTaxiFile`
- `BronzeTaxiFile` alimenta a geracao de `SilverTripRecord`
- `SilverTripRecord` alimenta `GoldDailyZoneDemand`
- `GoldDailyZoneDemand` alimenta `ForecastTrainingSlice`
- `ForecastTrainingSlice` gera `DemandForecastResult` e `ModelEvaluationSummary`
- `GoldDailyZoneDemand`, `DemandForecastResult` e `ModelEvaluationSummary`
  alimentam a `Visao de Dashboard`

## State Transitions

### IngestionBatch

`discovered -> downloaded -> validated -> transformed -> aggregated -> forecasted -> visualized`

### BronzeTaxiFile

`discovered -> downloaded -> stored -> validated`

### SilverTripRecord

`derived -> validated -> persisted`

### GoldDailyZoneDemand

`aggregated -> validated -> published`

### DemandForecastResult

`trained -> predicted -> evaluated -> published`

## Data Quality and Rerun Rules

- Colunas obrigatorias MUST existir antes de uma camada alimentar a proxima
- Tarifa, distancia e duracao MUST respeitar faixas nao negativas
- Nulos criticos em campos de tempo, zona ou medida MUST ser tratados antes do
  consumo em gold ou ML
- Reexecucao do mesmo periodo MUST gerar um resultado determinavel para o
  operador: sobrescrita controlada, substituicao explicita ou limpeza previa
  definida pelo modo de rerun do pipeline
- Cada camada MUST expor contagem de linhas ou sinal equivalente para apoiar
  validacao local
