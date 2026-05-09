# Research: NYC Taxi Demand and Fare Intelligence

## Decision 1: Spark standalone em containers

**Decision**: Planejar Spark com topologia standalone local, usando pelo menos
um container master e um worker no `docker-compose.yml`.

**Rationale**: Essa topologia reforca o valor de portfolio do projeto, deixa o
uso de PySpark explicito em um ambiente distribuivel local e separa de forma
clara o papel da orquestracao do Airflow do papel do processamento Spark.

**Alternatives considered**:
- Executar PySpark localmente em um unico servico: mais simples, mas menos fiel
  a arquitetura esperada e menos demonstravel.
- Adiar Spark dedicado para uma fase futura: reduz complexidade agora, mas
  enfraquece a historia tecnica do MVP.

## Decision 2: Previsao diaria de demanda por zona

**Decision**: Fixar o alvo de ML do MVP como previsao diaria de demanda por zona
de embarque.

**Rationale**: O recorte diario por zona equilibra interpretabilidade,
estabilidade estatistica e custo operacional local, alem de conectar bem com as
agregacoes gold e com a narrativa do dashboard.

**Alternatives considered**:
- Previsao horaria por zona: mais rica, mas aumenta sparsity e risco de
  complexidade desnecessaria no MVP.
- Previsao diaria da cidade inteira: mais simples, mas perde valor analitico
  espacial.

## Decision 3: Persistencia em arquivos por camadas

**Decision**: Persistir bronze, silver, gold e ml em diretorios locais sob
`data/`, usando artefatos de arquivos como contrato principal entre etapas.

**Rationale**: A abordagem atende a reproducibilidade local, facilita auditoria
e reprocessamento, elimina dependencia de infraestrutura externa e deixa as
camadas do pipeline visiveis para avaliacao de portfolio.

**Alternatives considered**:
- Centralizar dados em banco analitico: adiciona operacao extra sem necessidade
  para o MVP.
- Persistencia mista em banco e arquivos: amplia superficie operacional sem
  ganho proporcional nesta fase.

## Decision 4: Airflow como orquestrador principal

**Decision**: Todo fluxo ponta a ponta do MVP deve ser desenhado para partir de
DAGs do Airflow, mesmo que existam comandos auxiliares de depuracao local.

**Rationale**: Isso satisfaz a constitution, evita caminhos paralelos de
execucao como padrao e fortalece a demonstracao de um pipeline orquestrado de
engenharia de dados.

**Alternatives considered**:
- Scripts manuais como caminho principal: mais rapido de montar, mas viola a
  direcao arquitetural definida.
- Orquestracao por agendador externo: adiciona dependencia desnecessaria.

## Decision 5: Janela inicial limitada entre 3 e 12 meses

**Decision**: O plano assume um intervalo inicial controlado dentro de 3 a 12
meses de Yellow Taxi parquet.

**Rationale**: A janela limitada mantem o MVP executavel em ambiente local,
permite iteracao rapida e reduz risco de gargalos precoces de armazenamento e
tempo de execucao.

**Alternatives considered**:
- Carregar todo o historico de uma vez: incompatível com a meta de MVP local.
- Usar menos de 3 meses por padrao: pode ser insuficiente para demonstrar a
  utilidade do pipeline e do modelo.

## Decision 6: Baseline de ML com scikit-learn

**Decision**: Usar um baseline simples e interpretavel em scikit-learn para a
primeira previsao de demanda.

**Rationale**: O baseline atende o objetivo pratico de ML do MVP, facilita a
explicacao das metricas e reduz o risco de overengineering.

**Alternatives considered**:
- Modelos mais complexos de boosting ou deep learning: podem melhorar resultado,
  mas aumentam custo cognitivo e operacional cedo demais.
- Apenas regra heuristica sem modelo: simplifica em excesso e reduz o valor de
  portfolio do componente preditivo.

## Decision 7: Dashboard consome artefatos gold e ml persistidos

**Decision**: O Streamlit deve ler datasets analiticos e preditivos persistidos
em `data/gold` e `data/ml`, em vez de acionar transformacoes intermediarias em
tempo de uso.

**Rationale**: Isso preserva separacao de responsabilidades, facilita
depuracao, evita preparo manual adicional e deixa clara a dependencia do
dashboard em saídas reproduziveis do pipeline.

**Alternatives considered**:
- Dashboard consultando silver diretamente: mistura analise com camada de
  trabalho intermediaria.
- Dashboard executando pipeline parcial: aumenta acoplamento e risco de falhas
  opacas para o operador.
