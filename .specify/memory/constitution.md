<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
  - Principle 1 -> I. Reprodutibilidade Local e Gratuita
  - Principle 2 -> II. Orquestracao Padronizada com Docker Compose e Airflow
  - Principle 3 -> III. Processamento em Camadas com PySpark
  - Principle 4 -> IV. Entrega Final em Streamlit com ML Util
  - Principle 5 -> V. Incrementalismo, Validacao e Reversibilidade
- Added sections:
  - Restricoes Tecnicas Obrigatorias
  - Fluxo de Desenvolvimento e Qualidade
- Removed sections:
  - None
- Templates requiring updates:
  - updated .specify/templates/plan-template.md
  - updated .specify/templates/spec-template.md
  - updated .specify/templates/tasks-template.md
  - pending .specify/templates/commands/*.md (directory not present in this repository)
  - pending README.md or docs/quickstart.md (files not present in this repository)
- Follow-up TODOs:
  - None
-->
# NYC Taxi Demand and Fare Intelligence Constitution

## Core Principles

### I. Reprodutibilidade Local e Gratuita
O projeto MUST ser executavel localmente no Windows com Docker Desktop, sem
dependencia obrigatoria de cloud paga, credenciais privadas ou servicos externos
necessarios para o fluxo principal. Toda entrega MUST poder ser reproduzida a
partir de comandos documentados, usando apenas dados publicos e artefatos
versionados ou gerados localmente. Rationale: o objetivo do projeto e ser um
portfolio robusto, gratuito, auditavel e simples de demonstrar.

### II. Orquestracao Padronizada com Docker Compose e Airflow
Docker Compose MUST ser o contrato operacional dos servicos principais, e
Airflow MUST ser o orquestrador do pipeline de dados. Novos componentes MUST
entrar no ecossistema existente em vez de criar fluxos paralelos ou execucao
manual como caminho principal. Excecoes temporarias para depuracao local SHOULD
ser permitidas apenas quando tambem existir um caminho equivalente dentro da
orquestracao oficial. Rationale: uma topologia unica reduz ambiguidade de
execucao, facilita onboarding e torna o pipeline demonstravel de ponta a ponta.

### III. Processamento em Camadas com PySpark
Os dados MUST seguir organizacao bronze, silver e gold, com persistencia clara
de artefatos intermediarios em diretorios nomeados de forma explicita. O
processamento em escala MUST usar PySpark, priorizando transformacoes
deterministicas, particionamento compreensivel e validacoes minimas por etapa.
O MVP MUST priorizar dados publicos da NYC TLC, comecando por Yellow Taxi,
antes de ampliar escopo para outras fontes ou modalidades. Rationale: a
separacao por camadas melhora rastreabilidade, reprocessamento e evolucao
incremental do pipeline.

### IV. Entrega Final em Streamlit com ML Util
O produto final visivel ao usuario MUST ser um dashboard Streamlit que apresente
insights, metricas e resultados do pipeline de forma clara. O componente de
machine learning MUST resolver um problema pratico do dominio, preferencialmente
previsao de demanda, previsao de tarifa ou deteccao de anomalias, e MUST
explicitar entradas, saidas e limites de uso. O ML MUST consumir dados gold ou
derivacoes claramente documentadas. Rationale: o valor de portfolio depende de
ligar engenharia de dados, modelagem e visualizacao em uma historia coerente.

### V. Incrementalismo, Validacao e Reversibilidade
Cada etapa implementada MUST ser pequena, modular, testavel e reversivel.
Nenhuma entrega do MVP deve introduzir overengineering, acoplamentos
desnecessarios ou abstracoes antes da necessidade real. Toda mudanca MUST
definir uma forma simples de validacao local, produzir logs uteis quando
executada e preservar separacao de responsabilidades entre ingestao,
transformacao, modelagem e apresentacao. O Codex MUST avancar em etapas curtas,
validando antes de prosseguir para a proxima. Rationale: o projeto sera
construido incrementalmente e precisa permanecer estavel, didatico e facil de
corrigir.

## Restricoes Tecnicas Obrigatorias

- O stack principal MUST contemplar Docker Compose, Airflow, PySpark e
  Streamlit como escolhas arquiteturais centrais do projeto.
- O pipeline MUST funcionar sem segredos versionados e sem infraestrutura
  externa obrigatoria para desenvolvimento, execucao e demonstracao local.
- A documentacao MUST explicar comandos de bootstrap, execucao, reprocessamento
  e validacao minima do pipeline.
- Logs, checkpoints e dados intermediarios MUST ficar em caminhos claros e
  consistentes para facilitar auditoria e depuracao.
- Persistencia e contratos de dados SHOULD favorecer formatos simples e amplamente
  suportados no ecossistema local, evitando dependencias operacionais desnecessarias
  para o MVP.

## Fluxo de Desenvolvimento e Qualidade

- Toda specification MUST declarar como a entrega respeita execucao local,
  escopo incremental, camada de dados afetada e metodo de validacao.
- Todo implementation plan MUST falhar no Constitution Check se propuser
  servicos pagos, dependencia obrigatoria de credenciais, bypass do Airflow,
  bypass do Docker Compose, ausencia de PySpark em processamento de escala ou
  ausencia de persistencia bronze/silver/gold quando aplicavel.
- Toda task list MUST quebrar o trabalho em incrementos pequenos, com pontos de
  validacao explicitos, caminhos de arquivo concretos e checkpoints antes de
  avancar do MVP para expansoes.
- Mudancas em ML MUST documentar objetivo pratico, feature inputs, saida
  esperada e forma de avaliacao local.
- Mudancas em dashboard MUST consumir artefatos reproduziveis do pipeline e nao
  depender de consultas manuais ou preparacao externa nao documentada.

## Governance

Esta constitution prevalece sobre convencoes informais do repositorio para
decisoes de arquitetura, planejamento e implementacao. Alteracoes MUST ser
registradas neste arquivo e refletidas nos templates dependentes antes de serem
consideradas concluidas.

Emendas seguem versionamento semantico: MAJOR para redefinicoes incompativeis
de principios ou governanca; MINOR para novos principios, secoes ou expansao
material de regras; PATCH para clarificacoes sem mudanca de obrigacao. Revisoes
de conformidade MUST ocorrer em toda spec, plan e tasks gerados a partir deste
repositorio, com justificativa explicita para qualquer excecao aprovada.

Nenhuma implementacao pode avancar como padrao do projeto se nao puder ser
executada localmente, validada com passos documentados e revertida sem impacto
estrutural desproporcional. Quando houver conflito entre rapidez e
reprodutibilidade, a reprodutibilidade local vence.

**Version**: 1.0.0 | **Ratified**: 2026-05-09 | **Last Amended**: 2026-05-09
