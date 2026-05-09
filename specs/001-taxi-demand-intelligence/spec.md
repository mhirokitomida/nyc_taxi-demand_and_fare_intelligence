# Feature Specification: NYC Taxi Demand and Fare Intelligence

**Feature Branch**: `001-taxi-demand-intelligence`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Projeto completo e local de portfolio para engenharia de dados, machine learning e dashboard com dados publicos de Yellow Taxi NYC, com pipeline reproduzivel, camadas analiticas e componente de previsao de demanda."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir o ambiente local (Priority: P1)

Como desenvolvedor ou avaliador, quero iniciar o ambiente local do projeto a
partir de instrucoes documentadas para conseguir executar o MVP sem configurar
servicos manualmente.

**Why this priority**: Sem um ambiente local previsivel, nenhuma das demais
entregas do MVP pode ser demonstrada com confianca.

**Independent Test**: Uma pessoa nova no projeto segue os passos documentados,
inicia o ambiente local e confirma que os servicos necessarios para o MVP
ficam disponiveis para uso.

**Acceptance Scenarios**:

1. **Given** uma maquina compativel com o ambiente local esperado, **When** a
   pessoa segue os passos documentados de inicializacao, **Then** o ambiente do
   MVP fica disponivel sem configuracao manual adicional de servicos.
2. **Given** o ambiente local inicializado, **When** a pessoa verifica os
   componentes esperados do MVP, **Then** ela consegue identificar com clareza
   como iniciar a execucao do fluxo e como validar que o ambiente esta pronto.

---

### User Story 2 - Ingerir dados brutos em bronze (Priority: P1)

Como usuario tecnico, quero executar uma ingestao inicial de dados publicos de
Yellow Taxi para organizar arquivos brutos em uma camada bronze local e
auditavel.

**Why this priority**: A camada bronze e a primeira prova concreta de que o
projeto consegue consumir dados publicos reais de forma reproduzivel.

**Independent Test**: O usuario executa a ingestao inicial e confirma que um
conjunto controlado de dados publicos foi trazido para a area bruta local com
identificacao clara do periodo carregado.

**Acceptance Scenarios**:

1. **Given** que o ambiente local esta pronto, **When** o usuario executa a
   ingestao inicial para o periodo configurado do MVP, **Then** os arquivos
   brutos ficam disponiveis em uma area bronze local com estrutura clara.
2. **Given** uma ingestao concluida, **When** o usuario revisa os resultados,
   **Then** ele consegue identificar quais periodos foram carregados e se a
   captura de dados foi concluida com sucesso.

---

### User Story 3 - Gerar silver e gold reproduziveis (Priority: P1)

Como usuario tecnico, quero transformar os dados brutos em camadas limpas e
analiticas reproduziveis para sustentar metricas confiaveis do projeto.

**Why this priority**: O valor do MVP depende de transformar dados brutos em
informacao consistente e reutilizavel para analise e modelagem.

**Independent Test**: O usuario executa o processamento sobre os dados brutos e
confirma que existem saidas limpas e agregadas para o mesmo periodo, com
regras consistentes de qualidade.

**Acceptance Scenarios**:

1. **Given** dados brutos disponiveis para o periodo do MVP, **When** o
   usuario executa o processamento padrao, **Then** a camada silver e gerada
   com registros limpos e coerentes para analise posterior.
2. **Given** a camada silver concluida, **When** o usuario executa a geracao de
   saidas analiticas, **Then** a camada gold fica disponivel com agregacoes
   prontas para consumo.

---

### User Story 4 - Consultar metricas analiticas (Priority: P2)

Como analista, quero acessar metricas agregadas de corridas, tarifas, demanda,
distancia e duracao por periodo e zona para entender o comportamento do
servico de taxis no recorte do MVP.

**Why this priority**: As metricas analiticas demonstram utilidade pratica e
mostram que o pipeline entrega informacao de negocio, nao apenas dados
processados.

**Independent Test**: O analista acessa as saidas agregadas e confirma que
consegue comparar periodos e zonas com indicadores interpretableis e coerentes.

**Acceptance Scenarios**:

1. **Given** saidas analiticas geradas para o periodo do MVP, **When** o
   analista consulta os agregados disponiveis, **Then** ele encontra metricas
   de corridas, tarifas, demanda, distancia e duracao por periodo e zona.
2. **Given** diferentes recortes temporais ou geograficos, **When** o analista
   compara os indicadores, **Then** ele consegue identificar variacoes
   relevantes no comportamento das corridas.

---

### User Story 5 - Explorar o dashboard local (Priority: P2)

Como analista, quero visualizar um dashboard local com indicadores, graficos e
tabelas para apresentar os principais resultados do projeto de forma clara.

**Why this priority**: O dashboard e a principal camada de demonstracao do
portfolio para avaliadores e usuarios tecnicos.

**Independent Test**: O analista abre o dashboard local, navega pelas visoes
disponiveis e confirma que os resultados do pipeline aparecem de forma clara e
consistente.

**Acceptance Scenarios**:

1. **Given** dados analiticos disponiveis, **When** o analista abre o painel
   local do projeto, **Then** ele visualiza indicadores, graficos e tabelas sem
   depender de preparacao manual adicional.
2. **Given** um conjunto de visoes analiticas no painel, **When** o analista
   interage com os recortes disponiveis, **Then** ele consegue entender o
   comportamento geral da demanda e das corridas no periodo carregado.

---

### User Story 6 - Avaliar previsao de demanda (Priority: P3)

Como avaliador de portfolio, quero ver um componente de previsao de demanda com
objetivo claro, metricas compreensiveis e resultados interpretaveis para julgar
o valor analitico do projeto.

**Why this priority**: O componente preditivo diferencia o projeto como um
portfolio completo, conectando dados historicos a um uso pratico de modelagem.

**Independent Test**: O avaliador consulta o resumo do componente preditivo e
confirma que o objetivo, os recortes previstos e os resultados podem ser
entendidos sem conhecimento interno do pipeline.

**Acceptance Scenarios**:

1. **Given** dados historicos preparados para o recorte do MVP, **When** o
   avaliador acessa os resultados preditivos, **Then** ele encontra previsoes de
   demanda por periodo e zona acompanhadas de metricas de avaliacao.
2. **Given** os resultados do componente preditivo, **When** o avaliador
   compara previsoes e observacoes, **Then** ele consegue interpretar a utilidade
   e as limitacoes do modelo para o contexto do projeto.

### Edge Cases

- O sistema precisa informar de forma clara quando um arquivo publico esperado
  do periodo selecionado nao estiver disponivel.
- O sistema precisa tratar reexecucoes do mesmo periodo sem gerar ambiguidade
  sobre quais saidas continuam validas.
- O sistema precisa sinalizar quando registros brutos estiverem incompletos,
  com nulos criticos ou faixas claramente invalidas para analise.
- O sistema precisa manter o MVP em um volume controlado para nao comprometer a
  demonstracao local.
- O sistema precisa deixar visivel quando uma etapa intermediaria falhar para
  evitar que resultados incompletos sejam interpretados como finais.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir que uma pessoa nova prepare o ambiente
  local do MVP a partir de instrucoes documentadas e verificaveis.
- **FR-002**: O sistema MUST obter dados publicos de Yellow Taxi para um recorte
  temporal controlado do MVP e registrar com clareza o periodo carregado.
- **FR-003**: O sistema MUST persistir os dados do MVP em camadas locais
  distintas para dados brutos, dados limpos e saidas analiticas.
- **FR-004**: O sistema MUST gerar uma camada limpa reutilizavel para analise a
  partir dos dados brutos carregados.
- **FR-005**: O sistema MUST gerar agregacoes analiticas por periodo e zona
  contendo, no minimo, indicadores de corridas, tarifas, demanda, distancia e
  duracao.
- **FR-006**: O sistema MUST aplicar validacoes minimas sobre os dados e tornar
  visiveis inconsistencias criticas antes do consumo analitico.
- **FR-007**: O sistema MUST disponibilizar uma forma local de consulta aos
  resultados analiticos em formato adequado para avaliacao do projeto.
- **FR-008**: O sistema MUST oferecer um componente de previsao de demanda com
  resultados acompanhados de metricas de avaliacao compreensiveis.
- **FR-009**: O sistema MUST permitir a demonstracao local do projeto sem
  depender de servicos pagos, credenciais privadas ou infraestrutura externa
  obrigatoria.
- **FR-010**: O sistema MUST documentar como executar, validar e repetir o MVP
  do inicio ao fim.

### Constitution Alignment *(mandatory)*

- **CA-001**: Esta feature precisa ser executavel e validavel localmente em
  Windows com Docker Desktop a partir de comandos documentados.
- **CA-002**: Esta feature afeta as camadas bronze, silver, gold, ML e a camada
  final de visualizacao, exigindo rastreabilidade clara entre entradas e saidas.
- **CA-003**: Esta feature nao introduz dependencia obrigatoria de cloud paga,
  credenciais privadas ou servicos externos nao documentados.
- **CA-004**: O menor incremento reversivel desta feature e um MVP com volume
  limitado de Yellow Taxi que prove a jornada completa entre ingestao, analise,
  previsao e apresentacao.

### Key Entities *(include if feature involves data)*

- **Recorte de Ingestao**: Representa o periodo escolhido para o MVP, incluindo
  meses selecionados, status de captura e identificacao do lote local.
- **Snapshot Bronze**: Representa os arquivos brutos preservados para auditoria,
  reprocessamento e confirmacao do periodo ingerido.
- **Registro de Corrida Limpo**: Representa uma corrida validada para uso
  analitico, com atributos essenciais de tempo, zona, tarifa, distancia e
  duracao.
- **Agregado Gold por Periodo e Zona**: Representa a visao consolidada de
  demanda e desempenho operacional usada em analises e apresentacoes.
- **Resultado de Previsao de Demanda**: Representa previsoes, observacoes e
  metricas de avaliacao para o recorte escolhido do MVP.
- **Visao de Dashboard**: Representa os indicadores, graficos e tabelas finais
  consumidos por analistas e avaliadores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma pessoa avaliadora consegue sair de zero ate um ambiente local
  pronto para uso seguindo apenas a documentacao oficial do projeto.
- **SC-002**: O MVP consegue carregar e organizar um recorte controlado de
  dados publicos de Yellow Taxi para um periodo entre 3 e 12 meses sem exigir
  configuracao manual de servicos.
- **SC-003**: O projeto disponibiliza metricas agregadas de corridas, tarifas,
  demanda, distancia e duracao por periodo e zona para todo o recorte do MVP.
- **SC-004**: O painel local apresenta os principais resultados do pipeline de
  forma clara o suficiente para que um avaliador entenda a narrativa do
  projeto, seus dados e seus resultados.
- **SC-005**: O componente de previsao de demanda gera pelo menos um conjunto
  de metricas de avaliacao e permite comparar previsoes com valores observados
  no recorte escolhido.
- **SC-006**: A documentacao do projeto permite repetir a jornada completa do
  MVP sem recorrer a credenciais privadas, servicos pagos ou conhecimento
  implicito do autor.

## Assumptions

- O MVP representa o projeto ponta a ponta, nao apenas uma fundacao tecnica ou
  uma etapa isolada do pipeline.
- O escopo inicial usa apenas dados publicos de Yellow Taxi e nao inclui outras
  modalidades da NYC TLC.
- O volume inicial do MVP permanecera dentro de um intervalo entre 3 e 12 meses
  para manter a demonstracao local viavel e auditavel.
- A jornada do MVP termina em uma experiencia local de consulta a resultados
  analiticos e preditivos, sem incluir publicacao em cloud.
- O projeto nao precisa cobrir streaming em tempo real, autenticacao de
  usuarios, integracoes pagas, processamento historico completo ou modelos
  complexos nesta primeira especificacao.
- A documentacao oficial do projeto sera a fonte primaria para preparar,
  executar, validar e repetir o MVP local.
- A avaliacao do componente preditivo sera suficiente quando permitir entender
  o objetivo da previsao, o recorte analisado e a qualidade geral dos
  resultados sem exigir acesso ao processo interno de implementacao.
