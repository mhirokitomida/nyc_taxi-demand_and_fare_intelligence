# Dashboard Contract

## Purpose

Definir os insumos e comportamentos esperados do dashboard local do MVP.

## Input Artifacts

- Agregados analiticos em `data/gold`
- Previsoes e metricas em `data/ml`

## Required Views

- Resumo de KPIs principais do recorte carregado
- Tendencia de demanda diaria por zona ou agregada a partir das zonas
- Visoes de tarifa, distancia e duracao
- Tabelas analiticas de apoio
- Comparacao entre previsto e observado para o componente de ML

## Behavioral Expectations

- O dashboard MUST abrir localmente sem exigir preparo manual adicional
- O dashboard MUST ler somente artefatos persistidos e nao depender de execucao
  ad hoc do pipeline
- O dashboard MUST deixar claro quando os dados de ML estiverem ausentes,
  desatualizados ou incompletos
- O dashboard MUST manter separacao entre analise historica e resultados preditivos
