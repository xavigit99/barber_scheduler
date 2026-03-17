# ROADMAP — barber_scheduler

> Sistema de gestão de barbearias construído em FastAPI + SQLAlchemy com arquitetura CQRS via padrão Mediator (`diator`).
> Suporte a múltiplos perfis (`admin`, `barbeiro`, `cliente`) com tenant foundation para evolução multi-barbearia.
>
> **Referência:** 15 de março de 2026

---

## Estado por Fase

| Fase | Nome | Estado | Alvo |
|------|------|--------|------|
| F0 | Fundação Técnica | ✅ Completo | — |
| F1 | Auth & Contexto Base | ✅ Completo | — |
| F2 | Dados Mestres | ✅ Completo | — |
| F3 | Disponibilidade e Slots | ✅ Completo | — |
| F4 | Appointments Core | ✅ Completo | — |
| F5 | Superfícies Operacionais | ✅ Completo | — |
| F6 | Produção e Operação | ✅ Completo | — |
| F7 | Post-MVP | ✅ Completo | — |
| F8 | Multi-Tenant Hardening | ✅ Completo | — |
| F9 | Observabilidade, Auditoria & Compliance | ✅ Completo | — |
| F12 | Portal do Cliente (frontend) | ✅ Completo | — |
| F13 | Dashboard de Relatórios (frontend) | ✅ Completo | — |
| F14 | Reagendamento de Appointments (frontend) | ✅ Completo | — |
| F15 | Perfil do Cliente (frontend) | ✅ Completo | — |
| F16 | Painel do Barbeiro Melhorado (frontend) | ✅ Completo | — |
| F17 | Compliance & Auditoria (frontend) | ✅ Completo | — |
| F18 | Feedback & Memberships (frontend) | ✅ Completo | — |
| F19 | Registo de Barbeiro (backend + frontend) | ✅ Completo | — |
| F20 | CI/CD + Branch Protection | ✅ Completo | — |
| F21–F22 | Plataforma & Inovação | ⬜ Planeado | Q3 2026 |

---

## Fases Concluídas

### F0 — Fundação Técnica ✅
- Estrutura de módulos: `api/`, `application/`, `core/`, `infrastructure/`, `repositories/`
- Docker Compose com PostgreSQL + FastAPI
- CI mínima via GitHub Actions (`make test`)
- Makefile com comandos de dev (`test`, `run`, `install`)
- `BaseRepository` com soft-delete e tenant filtering automático

### F1 — Auth & Contexto Base ✅
- Modelo `User` com roles (`admin`, `barbeiro`, `cliente`)
- JWT tokens com expiração configurável
- RBAC nas rotas via `auth_dependencies.py`
- Tenant foundation: entidade `Tenant` + `Barbershop` com `tenant_id` 1:1
- Bootstrap admin endpoint + login endpoint

### F2 — Dados Mestres ✅
- **Barbers** CRUD completo (handlers, queries, rotas, schemas, testes)
- **Clients** CRUD completo
- **Services** CRUD completo (com `duracao_minutos` e `preco`)
- **Barbershop** CRUD completo (com `owner_user_id`)
- Soft-delete consistente em todas as entidades
- Tenant isolation via `BaseRepository`

### F3 — Disponibilidade e Slots ✅
- `BarberAvailability`: disponibilidade semanal (dia da semana + horário)
- `BarberBlock`: pausas, folgas e bloqueios manuais (3 tipos)
- `GetAvailableSlotsHandler`: cálculo de slots livres (15min, timezone-aware)
- Validação de overlaps e bloqueios
- Testes de edge cases de disponibilidade

### F4 — Appointments Core ✅
- Criar appointment com validação completa:
  - Verifica barber, client e service existem
  - Calcula `end_at` a partir da duração do serviço
  - Valida janela de disponibilidade semanal
  - Valida bloqueios ativos
  - Detecta conflito → `409 CONFLICT`
- Remarcar appointment (mesmas validações, exclui self do conflict check)
- Cancelar appointment (soft-delete)
- Listar por barbeiro e por cliente (com filtro opcional de data)

### F5 — Superfícies Operacionais ✅
- `GET /appointments/barbers/{barber_id}` — agenda diária do barbeiro
- `GET /appointments/clients/me/appointments` — self-service do cliente
- Segregação de acesso por perfil (admin vê tudo, barbeiro vê os seus, cliente vê os seus)

---

## F6 — Produção e Operação ✅

### Concluído (15 Mar 2026)
- ✅ `main.py` corrigido — todos os 8 routers registados
- ✅ `GET /health/` — health check com `SELECT 1`
- ✅ `echo=False` no SQLAlchemy engine
- ✅ Tenant isolation em appointments — `tenant_id` no modelo `Appointment` + propagação nos handlers
- ✅ Ownership guards — `user_id` em `Barber` e `Client`, guards DB-based

- ✅ BL-031: CI/CD Hardening — ruff lint no CI, `requirements-dev.txt`, `ruff.toml`, `make lint`
- ✅ BL-032: Logging Estruturado — `logging_config.py` com JSON formatter, setup no `main.py`
- ✅ BL-034: Hardening de Segurança — CORS configurável, rate limiting (`slowapi`), security headers middleware
- ✅ BL-035: Documentação de Deploy e Operação — README completo com setup, API, variáveis de ambiente e runbook

---

## F7 — Post-MVP ✅ (Alvo: 3 Mai 2026)

#### BL-036 + BL-037: Página Pública de Booking ✅
- `GET /public/barbershops/{id}/barbers/{barber_id}/slots` — sem autenticação
- `POST /public/appointments` — cria appointment como cliente (find-or-create client by email)

#### BL-038: Abstração de Notificações ✅
- Interface desacoplada para email/SMS/WhatsApp (`NotificationService` ABC)
- `LogNotificationService` — implementação log-based para dev/staging
- Confirmação, cancelamento e remarcação integrados nos handlers

#### BL-040: Relatórios Operacionais Iniciais ✅
- `GET /admin/reports/daily` — appointments do dia por barbeiro (admin-only)
- `GET /admin/reports/revenue` — faturação por período com breakdown por serviço (admin-only)

---

## F8 — Multi-Tenant Hardening ✅

#### BL-041: Modelo de Memberships Multi-Barbershop ✅
- `BarbershopMembership` (barber_id, barbershop_id, role)
- Um barbeiro pode pertencer a várias barbearias

#### BL-042 + BL-043: Soft Delete Uniforme + RBAC Multi-Shop ✅
- Auditar soft-delete em todos os recursos mutáveis
- Guards que validam tenant ownership antes de qualquer ação mutável

#### BL-044 + BL-045: Tenant-Aware Queries + Testes ✅
- Propagar filtros tenant em todos os handlers e queries
- Testes end-to-end de isolamento entre tenants

---

## F9 — Observabilidade, Auditoria & Compliance ✅

#### BL-046: Audit Trail ✅
- `GET /admin/audit?entity=barber&from_date=…&to_date=…`
- Registos soft-deleted do tenant com filtros por data

#### BL-047: Tenant Stats ✅
- `GET /admin/stats`
- Contagens e receita do tenant no mês corrente

#### BL-048: Data Retention (purge) ✅
- `DELETE /admin/purge` body: `{"entity": "barber", "older_than_days": 90}`
- Hard-delete de registos antigos soft-deleted; retorna `purged_count`

#### BL-049: Compliance Export (GDPR) ✅
- `GET /admin/export`
- JSON com todos os dados do tenant (activos + deleted) para GDPR/LGPD

#### BL-050: Testes ✅
- Testes unitários para todos os handlers F9 (audit, stats, purge, export)

---

## F12–F20 — Frontend Completo ✅ (Mar 2026)

- **F12:** Portal do cliente público (registo, login, booking sem conta)
- **F13:** Dashboard de relatórios admin (KPIs, receita, agendamentos do dia)
- **F14:** Reagendamento de appointments pelo cliente (modal + slots)
- **F15:** Perfil do cliente (editar dados + alterar password)
- **F16:** Painel do barbeiro melhorado (nomes de clientes/serviços + gestão de disponibilidade)
- **F17:** Compliance & Auditoria UI (audit log, export GDPR, purge)
- **F18:** Feedback & Memberships UI (avaliações admin, membros por barbearia)
- **F19:** Registo atómico de barbeiro (User + Barber em transação única)
- **F20:** CI/CD com GitHub Actions (lint + testes + build frontend em PRs)

---

## F21–F22 — Plataforma & Inovação ⬜ (Alvo: Q3 2026)

- **F21:** API pública para parceiros, onboarding automatizado
- **F22:** Agenda multi-slot e recorrente, notificações reais (email/WhatsApp)

---

## Resumo de Estimativas

| Fase | O Que Falta | Estimativa | Alvo |
|------|-------------|-----------|------|
| F6 Produção | Migrations + CI/CD + Logging + Segurança + Docs | 2 semanas | 12 Abr 2026 |
| F7 Post-MVP | Public booking + Notificações + Relatórios | 3 semanas | 3 Mai 2026 |
| F8 Multi-Tenant | Memberships + Soft-delete + RBAC + Queries | 2 semanas | 17 Mai 2026 |
| F9–F20 Frontend & CI | UI completa + CI/CD | ✅ Completo | Mar 2026 |
| F21–F22 Plataforma | APIs externas, Inovação | 4 semanas | Q3 2026 |

**MVP completo:** março de 2026 ✅

---

## Critérios de MVP Completo

- [x] Auth e roles ativos
- [x] Tenant foundation
- [x] Clients, barbers, services completos
- [x] Disponibilidade semanal e exceções
- [x] Appointments: create, reschedule, cancel
- [x] Conflitos bloqueados com `409`
- [x] Agenda diária disponível
- [x] `main.py` corrigido — todos os endpoints acessíveis
- [x] Tenant isolation completo em appointments
- [x] Migrations formais (Alembic — delta migrations para schema existente)
- [x] CI com lint, testes e build frontend
- [x] Logging estruturado
- [ ] Healthcheck estável
- [x] CORS, rate limiting, security headers
- [x] Documentação mínima de setup, API e operação

---

## Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Framework HTTP | FastAPI |
| ORM | SQLAlchemy |
| Base de dados | PostgreSQL |
| Arquitetura | CQRS via Mediator (`diator`) |
| Auth | JWT (`python-jose`) |
| Migrations | Alembic (planeado — F6) |
| Testes | pytest + httpx |
| Contentor | Docker Compose |
| CI | GitHub Actions |
| Lint | ruff (planeado — F6) |

---

## Ficheiros Críticos

| Ficheiro | Propósito |
|----------|-----------|
| `main.py` | Entry point — registar todos os routers |
| `meditor.py` | DI container via diator |
| `backend/core/*.py` | Entidades SQLAlchemy + regras de negócio |
| `backend/infrastructure/schemas.py` | Schemas Pydantic para HTTP I/O |
| `backend/api/routes/*.py` | Routers FastAPI |
| `backend/api/error_http.py` | Mapeamento de exceções → HTTP status codes |
| `backend/api/auth_dependencies.py` | RBAC e extração de tenant do header |
| `repositories/base_repository.py` | Soft-delete + tenant filtering automático |
| `backend/application/handlers/appointment/` | Lógica core de appointments |
| `backend/core/scheduling.py` | Cálculo de slots (timezone-aware, 15min) |
