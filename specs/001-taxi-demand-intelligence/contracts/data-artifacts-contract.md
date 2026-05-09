# Data Artifacts Contract

## Purpose

Definir os contratos minimos dos artefatos persistidos que conectam as camadas
do MVP.

## Directories

- `data/bronze/`: arquivos brutos por periodo carregado
- `data/silver/`: dados limpos e preparados para analise
- `data/gold/`: agregados diarios por zona para analise e dashboard
- `data/ml/`: previsoes e metricas do baseline de demanda

## Naming Expectations

- Artefatos MUST indicar claramente o periodo coberto
- Artefatos de ML MUST indicar a execucao ou lote que os produziu
- O operador MUST conseguir distinguir artefatos atuais de reruns anteriores

## Minimum Fields by Layer

### Bronze

- identificador do periodo
- referencia ao lote de ingestao
- caminho local persistido

### Silver

- campos de tempo
- zona de embarque
- distancia
- tarifa
- duracao

### Gold

- data de servico
- zona de embarque
- contagem de corridas
- tarifa total e media
- distancia total e media
- duracao media

### ML

- data prevista
- zona de embarque
- demanda prevista
- demanda observada quando houver avaliacao
- identificador do modelo ou execucao
- metricas de avaliacao associadas

## Freshness and Rerun Expectations

- Artefatos MUST refletir o periodo solicitado pela execucao mais recente para
  aquele lote
- O modo de rerun MUST deixar claro se houve substituicao, sobrescrita ou
  regeneracao dos artefatos
- Artefatos incompletos MUST ser reconheciveis como falha e nao como resultado final
