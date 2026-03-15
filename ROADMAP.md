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
| F6 | Produção e Operação | 🟡 Em progresso | 12 Abr 2026 |
| F7 | Post-MVP | ⬜ Planeado | 3 Mai 2026 |
| F8 | Multi-Tenant Hardening | ⬜ Planeado | 17 Mai 2026 |
| F9–F11 | Plataforma & Inovação | ⬜ Planeado | Q3 2026 |

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

## F6 — Produção e Operação 🟡

### Concluído (15 Mar 2026)
- ✅ `main.py` corrigido — todos os 8 routers registados
- ✅ `GET /health/` — health check com `SELECT 1`
- ✅ `echo=False` no SQLAlchemy engine
- ✅ Tenant isolation em appointments — `tenant_id` no modelo `Appointment` + propagação nos handlers
- ✅ Ownership guards — `user_id` em `Barber` e `Client`, guards DB-based

### Por fazer

#### BL-030: Migrations Formais
- Instalar e configurar Alembic
- Criar migration inicial a partir dos modelos SQLAlchemy atuais
- Documentar `alembic upgrade head` no README e Makefile (`make migrate`)

#### BL-031: CI/CD Hardening
- Adicionar Alembic migration check ao pipeline CI
- Adicionar lint (ruff ou flake8) ao pipeline

#### BL-032: Logging Estruturado
- Configurar `logging` com formato JSON (ou `structlog`)
- Logar: requests, erros de negócio, eventos de autenticação

#### BL-034: Hardening de Segurança
- Configurar CORS corretamente (não wildcard em produção)
- Rate limiting básico (`slowapi`)
- Security headers via middleware

#### BL-035: Documentação de Deploy e Operação
- README com setup local e produção
- Documentar variáveis de ambiente obrigatórias
- Runbook mínimo: deploy, migrations, logs

---

## F7 — Post-MVP ⬜ (Alvo: 3 Mai 2026)

#### BL-036 + BL-037: Página Pública de Booking
- `GET /public/barbershops/{id}/slots` — sem autenticação
- `POST /public/appointments` — cria appointment como cliente

#### BL-038: Abstração de Notificações
- Interface desacoplada para email/SMS/WhatsApp
- Confirmação, cancelamento e remarcação

#### BL-040: Relatórios Operacionais Iniciais
- `GET /admin/reports/daily` — appointments do dia por barbeiro
- `GET /admin/reports/revenue` — faturação por período

---

## F8 — Multi-Tenant Hardening ⬜ (Alvo: 17 Mai 2026)

#### BL-041: Modelo de Memberships Multi-Barbershop
- `BarbershopMembership` (barber_id, barbershop_id, role)
- Um barbeiro pode pertencer a várias barbearias

#### BL-042 + BL-043: Soft Delete Uniforme + RBAC Multi-Shop
- Auditar soft-delete em todos os recursos mutáveis
- Guards que validam tenant ownership antes de qualquer ação mutável

#### BL-044 + BL-045: Tenant-Aware Queries + Testes
- Propagar filtros tenant em todos os handlers e queries
- Testes end-to-end de isolamento entre tenants

---

## F9–F11 — Plataforma & Inovação ⬜ (Alvo: Q3 2026)

- **F9:** Observabilidade por tenant, auditoria de dados deletados, analytics, compliance
- **F10:** API pública para parceiros, onboarding automatizado
- **F11:** Painel de feedback, agenda multi-slot e recorrente, features avançadas

---

## Resumo de Estimativas

| Fase | O Que Falta | Estimativa | Alvo |
|------|-------------|-----------|------|
| F6 Produção | Migrations + CI/CD + Logging + Segurança + Docs | 2 semanas | 12 Abr 2026 |
| F7 Post-MVP | Public booking + Notificações + Relatórios | 3 semanas | 3 Mai 2026 |
| F8 Multi-Tenant | Memberships + Soft-delete + RBAC + Queries | 2 semanas | 17 Mai 2026 |
| F9–F11 Plataforma | Observabilidade, APIs externas, Inovação | 6 semanas | Q3 2026 |

**MVP completo estimado:** finais de abril de 2026

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
- [ ] Migrations formais (Alembic)
- [ ] CI com lint e migration check
- [ ] Logging estruturado
- [ ] Healthcheck estável
- [ ] CORS, rate limiting, security headers
- [ ] Documentação mínima de setup, API e operação

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
