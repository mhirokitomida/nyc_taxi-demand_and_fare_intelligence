# Pipeline Contract

## Purpose

Definir o contrato operacional do pipeline ponta a ponta executado pelo Airflow.

## Operator Inputs

- `start_month`: inicio do intervalo do MVP
- `end_month`: fim do intervalo do MVP
- `rerun_mode`: comportamento para reprocessamento do mesmo periodo
- `target_layers`: camadas ou etapas alvo da execucao

## Expected Outputs

- Bronze: arquivos brutos persistidos para cada mes solicitado
- Silver: dataset limpo e validado para o mesmo recorte
- Gold: agregados diarios por zona com metricas analiticas
- ML: previsoes e metricas de avaliacao para o recorte processado

## Success Conditions

- Todas as etapas selecionadas concluem com status de sucesso
- Logs por etapa deixam claro o periodo processado
- Artefatos esperados existem nas pastas alvo
- Validacoes minimas de dados foram executadas antes da promocao de camada

## Failure Signals

- Mes solicitado indisponivel ou nao baixado
- Colunas obrigatorias ausentes
- Saida intermediaria vazia ou inconsistente
- Falha de transformacao, agregacao ou previsao
- Dashboard sem insumos minimos produzidos
