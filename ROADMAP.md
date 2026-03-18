# ROADMAP — barber_scheduler

> Sistema de gestão de barbearias construído em FastAPI + SQLAlchemy com arquitetura CQRS via Mediator (`diator`).
> Suporte a múltiplos perfis (`admin`, `barbeiro`, `cliente`) com multi-tenant foundation.
>
> **Última atualização:** 18 de março de 2026 · branch `feature/f32-f35-segmentation-campaigns-payments-invoicing`

---

## Estado por Fase

| Fase | Nome | Estado | Branch / PR |
|------|------|--------|-------------|
| F0–F5 | Fundação + Core | ✅ Completo | `main` |
| F6 | Produção e Operação | ✅ Completo | `main` |
| F7 | Post-MVP (Booking Público + Notificações) | ✅ Completo | `main` |
| F8 | Multi-Tenant Hardening | ✅ Completo | `main` |
| F9 | Observabilidade, Auditoria & Compliance | ✅ Completo | `main` |
| F12–F20 | Frontend Completo + CI/CD | ✅ Completo | `main` |
| F21–F22 | Email SMTP + Docker Produção | ✅ Completo | PR #29 |
| F23–F24 | Webhooks + Marcações Recorrentes | ✅ Completo | PR #30 |
| F25–F27 | Lembretes + Confirmação + Grupo | ✅ Completo | PR #32 |
| F28–F31 | Packs + Fidelização + Aniversários | ✅ Completo | PR #33 |
| F32–F35 | Segmentação + Campanhas + Pagamentos + Faturação | 🔄 Em curso | `feature/f32-f35-segmentation-campaigns-payments-invoicing` |
| F36–F41 | Stocks + Salas + QR + Widget + Clínicas | ⬜ Futuro | — |

---

## Fases Concluídas

### F0 — Fundação Técnica ✅
- Estrutura de módulos: `api/`, `application/`, `core/`, `infrastructure/`, `repositories/`
- Docker Compose com PostgreSQL + FastAPI
- CI mínima via GitHub Actions (`make test`)
- `BaseRepository` com soft-delete e tenant filtering automático

### F1 — Auth & Contexto Base ✅
- Modelo `User` com roles (`admin`, `barbeiro`, `cliente`) + multi-role support
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

### F4 — Appointments Core ✅
- Criar appointment com validação completa (barber, client, service, disponibilidade, conflito)
- Remarcar appointment (mesmas validações)
- Cancelar appointment (soft-delete)
- Listar por barbeiro e por cliente (com filtro opcional de data)

### F5 — Superfícies Operacionais ✅
- Agenda diária do barbeiro + self-service do cliente
- Segregação de acesso por perfil (admin vê tudo, barbeiro vê os seus, cliente vê os seus)

### F6 — Produção e Operação ✅
- Health check com `SELECT 1`
- Logging estruturado (JSON formatter)
- CORS configurável, rate limiting (`slowapi`), security headers
- Tenant isolation em appointments + ownership guards DB-based
- Documentação completa no README

### F7 — Post-MVP ✅
- Página pública de booking (`/public/`) sem autenticação
- `NotificationService` ABC com `LogNotificationService` e `SmtpNotificationService`
- Relatórios operacionais: `/admin/reports/daily` e `/admin/reports/revenue`

### F8 — Multi-Tenant Hardening ✅
- `BarbershopMembership` (barber_id, barbershop_id, role) — um barbeiro em várias barbearias
- Soft-delete uniforme em todos os recursos mutáveis
- Tenant-aware queries + testes end-to-end de isolamento

### F9 — Observabilidade, Auditoria & Compliance ✅
- Audit trail (`/admin/audit`)
- Tenant stats (`/admin/stats`)
- Data retention/purge (`/admin/purge`)
- Compliance export GDPR (`/admin/export`)

### F12–F20 — Frontend Completo ✅ (Mar 2026)
- F12: Portal do cliente público (registo, login, booking)
- F13: Dashboard de relatórios admin (KPIs, receita, agendamentos)
- F14: Reagendamento pelo cliente (modal + slots)
- F15: Perfil do cliente (editar dados + password)
- F16: Painel do barbeiro melhorado (disponibilidade + nomes)
- F17: Compliance & Auditoria UI (audit log, export, purge)
- F18: Feedback & Memberships UI
- F19: Registo atómico de barbeiro (User + Barber em transação)
- F20: CI/CD GitHub Actions (lint + testes + build frontend)

### F21–F22 — Email SMTP + Docker Produção ✅
- `SmtpNotificationService` — emails reais via SMTP configurável
- CallMeBot WhatsApp para barbeiros (novo agendamento, cancelamento, reagendamento)
- Dockerfile multi-stage + docker-compose produção-pronto
- Variáveis de ambiente documentadas em `.env.example`

### F23–F24 — Webhooks + Marcações Recorrentes ✅
- `Webhook` model + dispatcher HMAC-SHA256 + registo de eventos
- `POST /webhooks` — CRUD de webhooks por tenant
- `POST /appointments/recurring` — semanal/quinzenal até 12 ocorrências
- Migração Alembic encadeada (`f1a3c5e7b9d2`)

### F25–F27 — Lembretes + Confirmação + Grupo ✅ (PR #32)
- **F25 Lembretes automáticos:** APScheduler job (30min) envia email + WhatsApp ~24h antes; `reminder_sent_at` previne duplicados; `REMINDER_HOURS_BEFORE` / `REMINDER_CHECK_INTERVAL_MINUTES` configuráveis
- **F26 Confirmação de presença:** UUID token por agendamento; link de confirmação no email de booking; `GET /appointments/confirm/{token}` público; `status` (pending/confirmed) + `confirmed_at`
- **F27 Marcações de grupo:** `service.max_capacity` para slots partilhados; `POST /appointments/group` com lista de `client_ids`; `group_id` liga as marcações; validação de capacidade
- Migração Alembic `b2c3d4e5f6a7`

### F28–F31 — Packs + Fidelização + Aniversários ✅ (PR #33)
- **F28 Packs de sessões:** `ServicePack` (nome, n_sessoes, preco) + `ClientPack` (sessoes_restantes, expira_em). Endpoints `/packs/services` e `/packs/me`. Migração `c3d4e5f6a7b8`
- **F30 Cartão de fidelização:** `LoyaltyAccount` + `LoyaltyTransaction`. 1 ponto por minuto de serviço na criação de agendamento. `/loyalty/me` + `/loyalty/redeem`
- **F31 Aniversários:** `data_nascimento` no cliente. Cron diário 09:00 envia email + WhatsApp. `birthday_msg_year` previne duplicados

---

## Em Curso

### F32 — Segmentação de Clientes 🔄
**Branch:** `feature/f32-f35-segmentation-campaigns-payments-invoicing`

`GET /clients/segment` (admin). Filtros: `inactive_days`, `min_spend`, `service_id`, `has_birthday_this_month`. Retorna lista de clientes. Base para campanhas segmentadas.

### F33 — Campanhas de Email 🔄
**Branch:** `feature/f32-f35-segmentation-campaigns-payments-invoicing`

Modelo `Campaign` (nome, subject, body_template, segment_filters JSON, status draft/sent). `POST /campaigns/{id}/send` aplica filtros de segmentação e envia email a cada cliente correspondente. `NotificationService.send_campaign()` adicionado.

### F34 — Pagamentos Online (Stripe) 🔄
**Branch:** `feature/f32-f35-segmentation-campaigns-payments-invoicing`

`payment_status` em `Appointment` (not_required/pending/paid/refunded). `POST /payments/checkout` cria Stripe Checkout Session. `POST /payments/webhook` valida assinatura e marca `paid`. Graceful degradation se `STRIPE_SECRET_KEY` não estiver definido (HTTP 503).

### F35 — Faturação Certificada (InvoiceXpress) 🔄
**Branch:** `feature/f32-f35-segmentation-campaigns-payments-invoicing`

Modelo `Invoice` (appointment_id, invoice_number, invoice_url, status draft/sent). `POST /invoices` emite via InvoiceXpress API se env vars configuradas, senão cria draft local. `GET /invoices` e `GET /invoices/{id}`.

---

## Futuro

| # | Funcionalidade | Descrição |
|---|----------------|-----------|
| F36 | SAF-T | Exportação SAF-T-PT conforme AT |
| F37 | Gestão de Stocks | Produtos, stock mínimo, consumo por serviço |
| F38 | Gestão de Salas/Recursos | Recurso obrigatório por marcação, evita dupla ocupação |
| F39 | QR Code de Marcação | QR que aponta para booking público (PNG descarregável) |
| F40 | Widget Embed | Snippet JS para embutir o formulário no website do cliente |
| F41 | Fichas Clínicas | Campos de saúde personalizados, consentimentos digitais |

---

## Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Framework HTTP | FastAPI |
| ORM | SQLAlchemy |
| Base de dados | PostgreSQL |
| Arquitetura | CQRS via Mediator (`diator`) |
| Auth | JWT (`python-jose`) |
| Migrations | Alembic |
| Testes | pytest + httpx |
| Scheduler | APScheduler |
| Notificações | SMTP + CallMeBot (WhatsApp) |
| Contentor | Docker Compose |
| CI | GitHub Actions |
| Lint | ruff |

---

## Ficheiros Críticos

| Ficheiro | Propósito |
|----------|-----------|
| `main.py` | Entry point — routers + APScheduler lifespan |
| `meditor.py` | DI container via diator (auto-discovery de handlers) |
| `backend/core/*.py` | Entidades SQLAlchemy + regras de negócio |
| `backend/infrastructure/schemas.py` | Schemas Pydantic para HTTP I/O |
| `backend/api/routes/*.py` | Routers FastAPI |
| `backend/core/reminders.py` | Job de lembretes automáticos |
| `backend/core/notifications.py` | Serviço de email (SMTP) |
| `backend/core/whatsapp.py` | Serviço WhatsApp (CallMeBot) |
| `repositories/base_repository.py` | Soft-delete + tenant filtering automático |
| `alembic/versions/` | Migrações encadeadas do schema | a568049 (feat(f28-f30-f31): service packs, loyalty points, birthday messages)
