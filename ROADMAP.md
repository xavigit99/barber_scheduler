# ROADMAP.md

Estado de referencia: 12 de marco de 2026

Este roadmap usa a organizacao de agentes definida em `AGENTS.md` como modelo operacional. As estimativas assumem inicio em 16 de marco de 2026, uma squad pequena com foco principal em backend, e apoio parcial continuo de QA, seguranca, docs e DevOps.

## 1. Baseline Atual

Estado observado no repositorio:

- existe backend em `FastAPI` com `SQLAlchemy`, `Pydantic` e `Diator`
- `auth`, `barbershop`, `barbers`, `services`, `clients` e `availability` ja existem com handlers, rotas e testes
- existe bootstrap local, `Makefile`, CI minima e cobertura automatizada relevante para os contextos atuais
- `appointments` e cancelamentos com conflitos estáo em desenvolvimento
- a fundacao de `tenant` ja existe na `barbershop`, mas membership e isolamento ainda nao foram propagados a todos os contextos
- deletes logicos passaram a ser a semantica correta para recursos apagaveis

Impacto no planeamento:

- `F0` esta maioritariamente fechado
- `F1`, `F2` e `F3` estao substancialmente adiantadas
- o proximo objetivo pragmatica e tecnicamente correto e fechar `appointments`, membership de tenant e isolamento pelos contextos operacionais
- public booking, notificacoes e relatorios continuam planeados logo a seguir ao MVP

## 2. Premissas de Estimativa

As estimativas abaixo sao em semanas corridas de calendario, nao em dias ideais.

Capacidade assumida:

- `1.0` Backend / Full Stack equivalente
- `0.3` QA + Code Reviewer
- `0.2` Security + Dependency Manager
- `0.2` DevOps + Observability + Documentation

Convencoes:

- `Alta` confianca: variacao esperada de ate `+-20%`
- `Media` confianca: variacao esperada de ate `+-35%`
- `Baixa` confianca: variacao esperada acima de `+-35%`
- quando o trabalho de agentes corre em paralelo, a estimativa abaixo ja considera essa compressao

Objetivos de entrega:

- `MVP`: backend interno utilizavel para operacao de agenda da barbearia
- `Post-MVP`: fluxo publico de marcacao, notificacoes e reporting inicial

## 3. Roadmap Resumido

| Fase | Janela | Objetivo | Agentes Lideres | Estimativa | Confianca |
| --- | --- | --- | --- | --- | --- |
| F0 | 16 Mar 2026 a 27 Mar 2026 | Endireitar a base tecnica e a forma de entrega | Planner, Architect, Backend, QA, DevOps | 2 semanas | Alta |
| F1 | 30 Mar 2026 a 17 Abr 2026 | Autenticacao, perfis, contexto base da barbearia e tenant foundation | Product, Architect, Backend, Security | 3 semanas | Media |
| F2 | 20 Abr 2026 a 08 Mai 2026 | Completar dados mestres: barbers, services, clients hardening | Backend, QA, Code Reviewer | 3 semanas | Media |
| F3 | 11 Mai 2026 a 29 Mai 2026 | Disponibilidade, pausas, folgas, bloqueios e slots | System Design, Backend, QA | 3 semanas | Media |
| F4 | 01 Jun 2026 a 26 Jun 2026 | Motor de appointments com remarcacao e conflitos | Backend, QA, Security | 4 semanas | Media |
| F5 | 29 Jun 2026 a 10 Jul 2026 | Superficies operacionais para admin, barbeiro e cliente | Product, UX, Backend, QA | 2 semanas | Media |
| F6 | 13 Jul 2026 a 24 Jul 2026 | Readiness para producao, release e operacao | DevOps, Observability, Security, Documentation | 2 semanas | Alta |
| F7 | 27 Jul 2026 a 14 Ago 2026 | Public booking, notificacoes e relatorios iniciais | Full Stack, Growth, Documentation | 3 semanas | Baixa |

Estimativa agregada:

- `MVP completo`: 17 a 19 semanas, alvo em `24 de julho de 2026`
- `Roadmap alargado com post-MVP`: 20 a 22 semanas, alvo em `14 de agosto de 2026`

## 4. Milestones e Criterios de Saida

### F0. Fundacao e Higiene Tecnica

Objetivo:

- tornar o repositorio previsivel para evolucao acelerada sem acumular divida evitavel

Backlog:

- `BL-001` limpar artefactos gerados e historico legado do repositorio
- `BL-002` normalizar estrutura de modulos e naming por contexto funcional
- `BL-003` consolidar comandos de teste e setup local
- `BL-004` introduzir linting, formatting e validacao automatica em CI
- `BL-005` documentar bootstrap local, env vars e fluxo de contribuicao

Agentes principais:

- Planner Agent
- Architect Agent
- Backend Engineer Agent
- QA / Testing Agent
- DevOps Agent
- Documentation Agent

Estimativa:

- `2 semanas`

Saida esperada:

- ambiente local reprodutivel
- suite de testes executavel por um unico comando
- CI minima ativa
- sem artefactos gerados versionados

### F1. Auth e Contexto Base

Objetivo:

- estabelecer identidade, perfis, ownership inicial e base de tenant antes de abrir mais capacidade funcional

Backlog:

- `BL-006` definir modelo de autenticacao e autorizacao por `admin`, `barbeiro` e `cliente`
- `BL-007` criar entidade base `barbershop` e ownership inicial do sistema
- `BL-007A` criar `tenant` foundation em `barbershop`
- `BL-008` implementar login basico e estrategia de token
- `BL-009` adicionar guards de role nas rotas existentes
- `BL-010` cobertura de testes para autenticacao, `403` e acessos indevidos

Agentes principais:

- Product Manager Agent
- Architect Agent
- Backend Engineer Agent
- Security Agent
- QA / Testing Agent

Estimativa:

- `3 semanas`

Saida esperada:

- auth funcional
- roles aplicadas nas rotas
- `tenant_id` disponivel no ownership da `barbershop`
- regras de acesso cobertas por testes

### F2. Dados Mestres

Objetivo:

- completar as entidades de cadastro necessarias antes de disponibilidade e appointments

Backlog:

- `BL-011` CRUD de `barbers`
- `BL-012` CRUD de `services` com duracao e preco
- `BL-013` hardening de `clients` com validacoes, filtros e erros consistentes
- `BL-014` queries e handlers por contexto com testes dedicados
- `BL-015` documentacao API basica dos contextos mestres
- `BL-015A` propagar `tenant` e memberships aos contextos mestres

Agentes principais:

- Backend Engineer Agent
- Full Stack Agent
- QA / Testing Agent
- Code Reviewer Agent

Estimativa:

- `3 semanas`

Saida esperada:

- `clients`, `barbers` e `services` completos
- contexto preparado para isolamento por `tenant`
- contratos HTTP previsiveis
- cobertura de testes por camada

### F3. Disponibilidade e Slots

Objetivo:

- modelar disponibilidade semanal e excecoes, que e a dependencia central do motor de agenda

Backlog:

- `BL-016` modelar disponibilidade semanal do barbeiro
- `BL-017` suportar pausas, folgas e bloqueios
- `BL-018` criar query de slots livres por barbeiro e servico
- `BL-019` validar timezone, duracao e calculo de fim de slot
- `BL-020` cobrir edge cases de disponibilidade em testes

Agentes principais:

- System Design Agent
- Backend Engineer Agent
- QA / Testing Agent
- Performance Agent

Estimativa:

- `3 semanas`

Saida esperada:

- slots livres calculados de forma confiavel
- regras de excecao cobertas
- base pronta para appointments

### F4. Appointments Core

Objetivo:

- entregar o coracao do produto com criacao, remarcacao e cancelamento sem sobreposicao

Backlog:

- `BL-021` entidade e repositorio de `appointments`
- `BL-022` command/handler para criar appointment
- `BL-023` validacao de overlap, disponibilidade e duracao do servico
- `BL-023A` aplicar isolamento por `tenant` em appointments e vistas operacionais
- `BL-024` remarcacao e cancelamento com erros `409`, `404` e `400` consistentes
- `BL-025` testes de conflito e edge cases de agenda

Agentes principais:

- Backend Engineer Agent
- QA / Testing Agent
- Security Agent
- Code Reviewer Agent

Estimativa:

- `4 semanas`

Saida esperada:

- criar, remarcar e cancelar appointments
- impedir sobreposicao do mesmo barbeiro
- appointments isolados por `tenant` mesmo sem multi-tenant completo no mesmo deploy
- respostas HTTP consistentes

### F5. Operacao Interna e Self-Service

Objetivo:

- expor superficies operacionais minimas para os tres atores do produto

Backlog:

- `BL-026` agenda diaria do barbeiro
- `BL-027` vista administrativa dos appointments
- `BL-028` endpoints do cliente para consultar e cancelar os proprios appointments
- `BL-029` regras de ownership por perfil autenticado

Agentes principais:

- Product Manager Agent
- UX Designer Agent
- Backend Engineer Agent
- QA / Testing Agent

Estimativa:

- `2 semanas`

Saida esperada:

- fluxo interno MVP completo
- segregacao correta entre `admin`, `barbeiro` e `cliente`

### F6. Producao e Operacao

Objetivo:

- preparar o backend para deploy real e manutencao segura

Backlog:

- `BL-030` migrations formais e estrategia de evolucao de schema
- `BL-031` pipeline CI/CD com testes automatizados
- `BL-032` logging estruturado e eventos operacionais
- `BL-033` metricas base, healthchecks e alertas iniciais
- `BL-034` scan de dependencias, cabecalhos e checklist de seguranca
- `BL-035` documentacao de deploy, rollback e operacao

Agentes principais:

- DevOps Agent
- Observability Agent
- Security Agent
- Dependency Manager Agent
- Documentation Agent
- Release Manager Agent

Estimativa:

- `2 semanas`

Saida esperada:

- deploy repetivel
- observabilidade minima
- runbook operacional
- pronto para release MVP

### F7. Post-MVP

Objetivo:

- abrir crescimento do produto apos estabilizar o backend interno

Backlog:

- `BL-036` pagina publica de marcacao
- `BL-037` fluxo publico de descoberta de slots e booking
- `BL-038` abstracao de notificacoes para email/SMS/WhatsApp
- `BL-039` metadata e estrutura SEO da pagina publica
- `BL-040` relatorios operacionais iniciais

Agentes principais:

- Full Stack Agent
- Growth & SEO Agent
- Documentation Agent
- Observability Agent

Estimativa:

- `3 semanas`

Saida esperada:

- public booking inicial
- notificacoes desacopladas
- reporting basico

## 5. Backlog Priorizado com Estimativas

| ID | Item | Dono Principal | Estimativa | Dependencias | Fase |
| --- | --- | --- | --- | --- | --- |
| BL-001 | Limpar artefactos gerados e legado | Refactor Agent | 0.5 semana | nenhuma | F0 |
| BL-002 | Normalizar estrutura modular | Architect Agent | 0.5 semana | BL-001 | F0 |
| BL-003 | Setup local e comando unico de testes | Backend Engineer Agent | 0.5 semana | nenhuma | F0 |
| BL-004 | CI minima | DevOps Agent | 0.5 semana | BL-003 | F0 |
| BL-005 | Docs de onboarding | Documentation Agent | 0.5 semana | BL-003 | F0 |
| BL-006 | Modelo de auth e permissao | Architect Agent | 0.5 semana | F0 | F1 |
| BL-007 | Entidade `barbershop` | Backend Engineer Agent | 0.5 semana | BL-006 | F1 |
| BL-007A | Tenant foundation em `barbershop` | Architect Agent | 0.5 semana | BL-007 | F1 |
| BL-008 | Login e token flow | Backend Engineer Agent | 1 semana | BL-006 | F1 |
| BL-009 | Guards de role | Security Agent | 0.5 semana | BL-008 | F1 |
| BL-010 | Testes de auth e autorizacao | QA / Testing Agent | 0.5 semana | BL-008, BL-009 | F1 |
| BL-011 | CRUD de `barbers` | Backend Engineer Agent | 1 semana | BL-007 | F2 |
| BL-012 | CRUD de `services` | Backend Engineer Agent | 1 semana | BL-007 | F2 |
| BL-013 | Hardening de `clients` | Backend Engineer Agent | 0.5 semana | F0 | F2 |
| BL-014 | Queries e handlers por contexto | Full Stack Agent | 0.5 semana | BL-011, BL-012 | F2 |
| BL-015 | Docs API dos dados mestres | Documentation Agent | 0.5 semana | BL-011, BL-012 | F2 |
| BL-015A | Tenant propagation e memberships nos dados mestres | Backend Engineer Agent | 1 semana | BL-007A, BL-011, BL-012, BL-013 | F2 |
| BL-016 | Disponibilidade semanal | Backend Engineer Agent | 1 semana | BL-011 | F3 |
| BL-017 | Pausas, folgas e bloqueios | Backend Engineer Agent | 1 semana | BL-016 | F3 |
| BL-018 | Query de slots livres | Backend Engineer Agent | 0.5 semana | BL-016, BL-017, BL-012 | F3 |
| BL-019 | Regras de timezone e calculo de duracao | Backend Engineer Agent | 0.5 semana | BL-018 | F3 |
| BL-020 | Testes de edge cases de disponibilidade | QA / Testing Agent | 0.5 semana | BL-016, BL-017, BL-018 | F3 |
| BL-021 | Persistencia de `appointments` | Backend Engineer Agent | 0.5 semana | F3 | F4 |
| BL-022 | Criacao de appointment | Backend Engineer Agent | 1 semana | BL-021 | F4 |
| BL-023 | Validacao de overlap e disponibilidade | Backend Engineer Agent | 1 semana | BL-022 | F4 |
| BL-023A | Tenant isolation em appointments | Security Agent | 0.5 semana | BL-022, BL-015A | F4 |
| BL-024 | Remarcacao e cancelamento | Backend Engineer Agent | 1 semana | BL-022 | F4 |
| BL-025 | Testes de conflito | QA / Testing Agent | 0.5 semana | BL-023, BL-024 | F4 |
| BL-026 | Agenda diaria do barbeiro | Backend Engineer Agent | 0.5 semana | F4 | F5 |
| BL-027 | Vista administrativa | Full Stack Agent | 0.5 semana | F4 | F5 |
| BL-028 | Self-service do cliente | Backend Engineer Agent | 0.5 semana | F4, F1 | F5 |
| BL-029 | Ownership por perfil | Security Agent | 0.5 semana | BL-028 | F5 |
| BL-030 | Migrations formais | DevOps Agent | 0.5 semana | F4 | F6 |
| BL-031 | CI/CD | DevOps Agent | 0.5 semana | F0 | F6 |
| BL-032 | Logging estruturado | Observability Agent | 0.5 semana | F4 | F6 |
| BL-033 | Metrics e healthchecks | Observability Agent | 0.5 semana | BL-032 | F6 |
| BL-034 | Hardening de seguranca | Security Agent | 0.5 semana | F1, F4 | F6 |
| BL-035 | Runbooks e release docs | Documentation Agent | 0.5 semana | BL-031 | F6 |
| BL-036 | Pagina publica de booking | Frontend Engineer Agent | 1 semana | F6 | F7 |
| BL-037 | Booking publico | Full Stack Agent | 1 semana | BL-036, F4 | F7 |
| BL-038 | Abstracao de notificacoes | Backend Engineer Agent | 0.5 semana | F7 | F7 |
| BL-039 | SEO e metadados | Growth & SEO Agent | 0.5 semana | BL-036 | F7 |
| BL-040 | Relatorios operacionais | Data Engineer Agent | 0.5 semana | F4 | F7 |
| BL-041 | Modelo de memberships multi-barbershop e base model | Backend Engineer Agent | 1 semana | BL-007, BL-011 | F8 |
| BL-042 | Soft delete uniforme para recursos mutáveis | Backend Engineer Agent | 0.5 semana | BL-013, BL-021 | F8 |
| BL-043 | RBAC e ownership para multi-shop | Security Agent | 0.5 semana | BL-041, BL-042 | F8 |
| BL-044 | Filtros e queries tenant-aware | Backend Engineer Agent | 0.5 semana | BL-023A, BL-041 | F8 |
| BL-045 | Testes de fluxo multi-barbershop e soft delete | QA / Testing Agent | 0.5 semana | BL-041, BL-044 | F8 |
| BL-046 | Docs e comandos de onboarding tenant | Documentation Agent | 0.5 semana | BL-045 | F8 |
| BL-047 | Observabilidade e tracing por tenant | Observability Agent | 0.5 semana | BL-032, BL-041 | F9 |
| BL-048 | Retencao e auditoria para registros deletados | Security Agent | 0.5 semana | BL-042 | F9 |
| BL-049 | Analitica e metricas por barber shop | Data Engineer Agent | 1 semana | BL-047, BL-048 | F9 |
| BL-050 | Revisao de governanca e compliance | Security Agent | 0.5 semana | BL-048, BL-049 | F9 |
| BL-051 | API publica para parceiros e integrações | Infrastructure Agent | 1 semana | BL-035, BL-047 | F10 |
| BL-052 | Scripts e onboarding automatizado | Documentation Agent | 0.5 semana | BL-036, BL-046 | F10 |
| BL-053 | Growth experiment e landing templates | Growth & SEO Agent | 0.5 semana | BL-051 | F10 |
| BL-054 | Testes de contrato para APIs externas | QA / Testing Agent | 0.5 semana | BL-051 | F10 |
| BL-055 | Release notes automatizadas | Documentation Agent | 0.5 semana | BL-031, BL-052 | F10 |
| BL-056 | Painel de feedback e KPIs internos | Product Manager Agent | 1 semana | BL-049 | F11 |
| BL-057 | Ciclo de demonstrações e replaneamento | Planner Agent | 0.5 semana | BL-056 | F11 |
| BL-058 | Auditorias recorrentes de performance e segurança | Performance Agent | 0.5 semana | BL-034 | F11 |
| BL-059 | Proposta de features de agenda avançada | Backend Engineer Agent | 1 semana | BL-053, BL-056 | F11 |
| BL-060 | Arquivo de lições aprendidas e backlog atualizado | Documentation Agent | 0.5 semana | BL-057, BL-058 | F11 |

## 6. Dependencias Criticas

Dependencias que nao devem ser quebradas:

- `auth` antes de ownership e self-service
- tenant foundation antes de ownership fino e pagina publica
- `barbers` e `services` antes de disponibilidade
- disponibilidade antes de appointments
- appointments antes de agenda diaria e pagina publica
- CI, migrations e observabilidade antes de release MVP
- membership multi-barbershop antes de governanca tenant e analytics
- soft delete antes de retencao e auditoria de dados
- APIs públicas/partners somente depois de governança e observabilidade estabilizadas
- auditorias recorrentes antes de escalar experimentos externos

## 7. Riscos Principais

| Risco | Impacto | Mitigacao |
| --- | --- | --- |
| Falta de auth cedo demais | rework em quase todas as rotas | fechar F1 antes de expandir endpoints externos |
| Regras de disponibilidade subestimadas | atraso direto no motor de appointments | escrever testes de edge case em F3 antes de fechar design |
| Repositorio continuar com legado estrutural | aumenta custo de cada feature nova | tratar F0 como gate, nao como nice-to-have |
| Falta de migrations e CI | regressao silenciosa e deploy inseguro | nao considerar MVP concluido sem F6 |
| Tenant isolation ficar parcial | vazamento de dados entre operacoes futuras | fechar foundation cedo e propagar filtros antes de self-service/public booking |
| Falta de documentacao de contratos | acoplamento e inconsistencias | docs curtas e atualizadas por contexto no fecho de cada fase |
| Membership incompleto entre barbers e barbershops | barbaeiros acessam dados de outras unidades | modelar e testar memberships antes de publicar planos multi-loja |

## 8. Cadencia Recomendada

Cadencia operacional:

- planeamento semanal pelo `Planner Agent`
- review tecnica continua pelo `Code Reviewer Agent`
- validacao de seguranca no fecho de cada fase sensivel
- teste automatizado obrigatorio em todas as entregas de backend
- release notes no final de F6 e em cada entrega relevante de F7

Ritmo sugerido:

- checkpoint tecnico a cada sexta-feira
- demo interna no fecho de cada fase
- replaneamento a cada `2 semanas`

## 9. Definicao de MVP

O MVP esta completo quando todos os pontos abaixo forem verdade:

- auth e roles ativos
- tenant foundation pronta, mesmo sem multi-tenant real completo
- `clients`, `barbers` e `services` completos
- disponibilidade semanal e excecoes implementadas
- appointments com create, reschedule e cancel
- conflitos de agenda bloqueados com `409`
- agenda diaria disponivel para operacao interna
- CI, migrations, logs e healthchecks ativos
- documentacao minima de setup, API e operacao pronta

## 10. Proxima Acao Recomendada

Se o trabalho continuar imediatamente a partir do estado atual do repositorio, a ordem mais correta e:

1. fechar `BL-015A` com memberships e isolamento por tenant nos contextos mestres
2. entrar em `F4` com `appointments`
3. fechar ownership por perfil e agenda diaria em `F5`

## 11. Extended Tenant Governance Plan

As duas fases seguintes (F8 e F9) focam-se em solidificar a fundacao de multi-tenancy, soft delete e governanca de dados antes de escalar para operadores externos e compliance.

### F8. Tenant & Multi-Shop Hardening (17 de agosto a 28 de agosto de 2026)

Objetivo:

- garantir que o modelo base (base model) e as classes do core expostas em `core/` trabalham com memberships, tenants e soft delete sem comprometer as rotas.
- permitir que um barbeiro pertença a varias barbearias enquanto o sistema valida o tenant antes de permitir qualquer acao mutavel.

Backlog:

- `BL-041` consolidar o base model de `barber` + `barbershop` com a classe de membership e repositorio dedicado.
- `BL-042` aplicar soft delete em todos os recursos mutaveis (barbers, clients, appointments, services) e garantir que o `deleted` fica apenas marcado no banco.
- `BL-043` adicionar RBAC e guards especificos para membership multi-shop e garantir que apenas barbershop owners/tentas certificados conseguem agir sobre os dados.
- `BL-044` propagar filtros tenant-aware nas queries e handlers (como `appointments` e `availability`) usando as novas classes do core.
- `BL-045` escrever testes para os fluxos multi-barbershop e soft delete e garantir que os comandos/handlers respeitam os tenants.
- `BL-046` documentar o onboarding e os comandos principais (`make`/`python -m`), inclusive o que deve ser configurado nos `env`, para tornar o start do projeto previsivel.

Agentes principais:

- Architect Agent
- Backend Engineer Agent
- Security Agent
- QA / Testing Agent
- Documentation Agent

Estimativa:

- `2 semanas`

Saida esperada:

- membership multi-shop funcional
- soft delete preservado no banco e acessivel para auditoria
- docs e comandos de start claros para novos contribuidores

### F9. Platform Expansion & Compliance (31 de agosto a 11 de setembro de 2026)

Objetivo:

- fortalecer governanca, observabilidade e compliance antes de abrir o sistema a mais barbearias ou uso publico adicional.

Backlog:

- `BL-047` instrumentar observabilidade por tenant com tracing e logs enriquecidos.
- `BL-048` definir e documentar politica de retencao para os registros marcados como deleted e rodar auditorias automatizadas com revisão de dependencias.
- `BL-049` publicar analitica my-tenant (uso, disponibilidade e conflitos por barbershop) e dashboards para os administradores internos.
- `BL-050` completar revisao de governanca e compliance, abordando checklist de seguranca, tokens e segredos rotativos.

Agentes principais:

- Observability Agent
- Security Agent
- Dependency Manager Agent
- Data Engineer Agent
- Documentation Agent

Estimativa:

- `2 semanas`

Saida esperada:

- camada de governanca com logs, tracing e auditar apta a provar isolamento
- analytics por tenant para guiar operacoes e proximas fases

### F10. Growth + External Integrations (14 de setembro a 25 de setembro de 2026)

Objetivo:

- abrir canais externos, parcerias e APIs adicionais que suportem clientes empresariais e marketing.

Backlog:

- `BL-051` criar API pública para parceiros e integrações (webhooks, read-only views, tokens restringidos).
- `BL-052` documentar e automatizar onboarding via scripts, GitHub actions e templates para novos tenants.
- `BL-053` desenvolver experimento de growth (ex: campanhas via API ou templates de landing page com SEO básico).
- `BL-054` construir teste automatizado para APIs externas e eventos (contract tests ou schema validation).
- `BL-055` introduzir seção de change log / release notes geradas automaticamente para stakeholders externos.

Agentes principais:

- Product Manager Agent
- Growth & SEO Agent
- Infrastructure Agent
- Documentation Agent

Estimativa:

- `2 semanas`

Saida esperada:

- APIs públicas seguras e observáveis disponíveis para parceiros.
- docs e scripts de onboarding padronizados e autoatendimento.

### F11. Innovation & Feedback Loop (28 de setembro a 9 de outubro de 2026)

Objetivo:

- colocar as ferramentas internas em rotinas de experimento, benchmark e feedback para futura priorização.

Backlog:

- `BL-056` implementar painel interno de feedback do cliente e métricas operacionais iniciando com target de 2 KPIs.
- `BL-057` validar roadmap com ciclo de demonstrações, demos, replaneamento e revisao de risks.
- `BL-058` automatizar auditorias de performance e segurança recorrente (scripts + alertas).
- `BL-059` propor novas features de agenda avançada (ex: multi-slot, reservas em bloco) acompanhando dados reais.
- `BL-060` revisar e arquivar lições aprendidas, mantendo backlog pronto para próxima sprint.

Agentes principais:

- Planner Agent
- Performance Agent
- QA / Testing Agent
- Documentation Agent

Estimativa:

- `2 semanas`

Saida esperada:

- feedback estruturado e backlog atualizado com prioridades reais.
- automação de auditorias e checkpoints para garantir estabilidade.
