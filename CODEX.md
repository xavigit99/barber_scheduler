# CODEX — Barber Scheduler: Estado Completo e Próximas Tarefas

> Documento de handoff para agente de código autónomo.
> Descreve o projeto, o que já foi implementado, o que falta, e como proceder.
> **Lê este ficheiro na íntegra antes de escrever qualquer linha de código.**

---

## 1. Visão Geral do Projeto

**barber_scheduler** é uma plataforma SaaS multi-tenant para gestão de barbearias.
Stack: **FastAPI + SQLAlchemy + PostgreSQL** (backend), **React + TypeScript + Tailwind** (frontend).
Arquitetura: **CQRS via `diator`** (mediator pattern). Todos os casos de uso têm um Command/Query + um Handler.

### Estrutura de directorias

```
barber_scheduler/
├── backend/
│   ├── api/routes/          # 27 routers FastAPI
│   ├── application/
│   │   ├── commands/        # Frozen dataclasses (Request)
│   │   ├── queries/         # Frozen dataclasses (Request)
│   │   └── handlers/        # Auto-descobertos pelo meditor.py
│   ├── core/                # 33 modelos SQLAlchemy + lógica de domínio
│   ├── infrastructure/
│   │   ├── database.py      # engine, SessionLocal, Base
│   │   └── schemas.py       # Todos os schemas Pydantic de I/O HTTP
├── repositories/
│   └── base_repository.py   # Soft-delete + tenant filtering automático
├── alembic/versions/        # 11 migrações encadeadas
├── tests/                   # 320 testes pytest (49 ficheiros)
├── frontend/src/
│   ├── pages/admin/         # 21 páginas admin
│   ├── pages/client/        # 6 páginas cliente
│   ├── pages/barber/        # 3 páginas barbeiro
│   ├── pages/public/        # 4 páginas públicas
│   ├── components/          # Button, Input, Modal, Select, Table, Toast, Navbar, Spinner
│   ├── contexts/AuthContext.tsx
│   └── lib/api.ts           # axios com interceptors (JWT + X-Tenant-Id)
├── main.py                  # Entry point — routers + APScheduler lifespan
├── meditor.py               # DI container, auto-discovery de handlers
├── requirements.txt
└── ROADMAP.md
```

---

## 2. Regras de Arquitectura — NUNCA violar

### Backend

1. **Comandos e Queries são frozen dataclasses:**
   ```python
   from dataclasses import dataclass
   from diator.requests import Request

   @dataclass(frozen=True)
   class CreateFooCommand(Request):
       nome: str
       tenant_id: int | None = None
   ```

2. **Handlers em `backend/application/handlers/<dominio>/`** com `__init__.py` vazio. São auto-descobertos — não precisam de registo manual.

3. **Tipos Python 3.12:** usar `X | Y` em vez de `Optional[X]`, `class Repo[T]` em vez de `Generic[T]`.

4. **Ruff limpo:** `ruff check backend/ --quiet` tem de passar a zero. Imports ordenados (I001). Sem imports não usados (F401).

5. **Migrações Alembic encadeadas:** cada nova migração revisa a anterior. Verificar o head actual em `alembic/versions/` antes de criar uma nova.
   - Head actual: `e5f6a7b8c9d0` (F36-F41)

6. **Soft-delete uniforme:** todos os modelos mutáveis têm `deleted = Column(Boolean, default=False)` e `deleted_at = Column(DateTime, nullable=True)`.

7. **Multi-tenant:** todos os modelos têm `tenant_id`. Usar `BaseRepository(Model, db, tenant_id)` para queries — filtra tenant automaticamente.

8. **Best-effort em side-effects:** notificações, webhooks, pontos de fidelização — sempre em `try/except Exception: pass` no handler.

9. **Testar sempre:** após qualquer mudança, correr `venv/bin/python -m pytest tests/ -q --tb=short`.

### Frontend

1. **API via `api` de `../../lib/api`** (axios com auth + tenant automáticos — NÃO usar `fetch` raw).

2. **Layout padrão:**
   ```tsx
   <div className="flex min-h-screen bg-slate-950 text-slate-100">
     <Navbar />
     <main className="ml-60 flex-1 p-8">
       <h1 className="text-2xl font-bold text-white mb-6">Título</h1>
       ...
     </main>
   </div>
   ```

3. **Componentes reutilizáveis:** `Button`, `Input`, `Modal`, `Select`, `Table`, `Spinner`, `Toast` já existem em `frontend/src/components/`.

4. **Build limpo:** `cd frontend && npm run build` não pode ter erros TypeScript.

5. **Registar novas rotas em `App.tsx` e novos links em `Navbar.tsx`.**

---

## 3. O que já está implementado

### Backend (F0–F41, tudo em `main`)

| Features | O que existe |
|----------|-------------|
| **Auth** | JWT, RBAC (`admin`/`barber`/`client`), multi-role, bootstrap admin |
| **Dados mestres** | Barbers, Clients, Services, Barbershops CRUD completo |
| **Disponibilidade** | `BarberAvailability` semanal + `BarberBlock` (3 tipos) + slots calculator |
| **Agendamentos** | Criar/remarcar/cancelar, validação completa, overlaps, timezone |
| **Multi-tenant** | `Tenant`, `BarbershopMembership`, tenant isolation em todas as queries |
| **Observabilidade** | Audit log, stats, GDPR export/purge |
| **Webhooks** | HMAC-SHA256, registo de eventos, dispatcher |
| **Marcações recorrentes** | Semanal/quinzenal até 12 ocorrências |
| **F25 Lembretes** | APScheduler 30min, email+WhatsApp 24h antes, `reminder_sent_at` |
| **F26 Confirmação** | UUID token, `GET /appointments/confirm/{token}`, status pending/confirmed |
| **F27 Grupo** | `max_capacity` em Service, `POST /appointments/group`, `group_id` |
| **F28 Packs** | `ServicePack` + `ClientPack`, `/packs/services`, `/packs/me` |
| **F30 Fidelização** | `LoyaltyAccount` + `LoyaltyTransaction`, 1pt/min, `/loyalty/me`, `/loyalty/redeem` |
| **F31 Aniversários** | `data_nascimento` em Client, cron 09:00, deduplicação por `birthday_msg_year` |
| **F32 Segmentação** | `GET /clients/segment?inactive_days=&min_spend=&service_id=&has_birthday_this_month=` |
| **F33 Campanhas** | `Campaign` model, `/campaigns` CRUD, `POST /campaigns/{id}/send` |
| **F34 Stripe** | `payment_status` em Appointment, `/payments/checkout`, `/payments/webhook` |
| **F35 Faturação** | `Invoice` model, InvoiceXpress API ou draft local, `/invoices` |
| **F36 SAF-T** | `GET /admin/saft?year=` — agregado JSON por serviço |
| **F37 Stocks** | `Product` + `ServiceProduct`, CRUD + stock adjust, dedução automática |
| **F38 Salas** | `Resource`, `resource_id` em Appointment, overlap check |
| **F39 QR Code** | `GET /public/qr/{tenant_id}` — PNG via `qrcode[pil]` |
| **F40 Widget** | `GET /public/widget/{tenant_id}` — JS iframe snippet |
| **F41 Clínico** | `ClinicalRecord` + `ClinicalNote`, consentimento digital, `/clinical/{client_id}` |

### Frontend (em PR #36, branch `feature/frontend-f25-f41`)

| Página | Rota |
|--------|------|
| PacksPage | `/admin/packs` |
| LoyaltyPage | `/admin/loyalty` |
| CampaignsPage | `/admin/campaigns` |
| PaymentsPage | `/admin/payments` |
| InvoicesPage | `/admin/invoices` |
| StocksPage | `/admin/stocks` |
| ResourcesPage | `/admin/resources` |
| ClinicalPage | `/admin/clinical` |
| SAFTPage | `/admin/saft` |
| ClientSegmentPage | `/admin/clients/segment` |
| MyPacksPage | `/client/packs` |
| MyLoyaltyPage | `/client/loyalty` |

---

## 4. O que falta fazer — Lista priorizada

### P0 — Testes em falta (crítico, bloqueia CI)

Os testes existentes cobrem F0–F24. As features F25–F41 **não têm testes**. Adicionar em `tests/`:

#### 4.1 `tests/application/handlers/test_reminders_handler.py`
```python
# Testar send_appointment_reminders():
# - appointment com start_at em 24h e reminder_sent_at=None → deve enviar e setar reminder_sent_at
# - appointment já com reminder_sent_at → não envia novamente
# - appointment cancelado (deleted=True) → ignorado
# Usar mocks para NotificationService e WhatsApp
```

#### 4.2 `tests/application/handlers/test_confirm_appointment_handler.py`
```python
# - token válido → status="confirmed", confirmed_at preenchido
# - token inválido → NotFoundError
# - token já confirmado → idempotente (não falha)
```

#### 4.3 `tests/application/handlers/test_group_appointment_handler.py`
```python
# - criar grupo com 2 clientes → ambos têm mesmo group_id
# - capacidade excedida (service.max_capacity=1, 2 clientes) → ConflictError
# - barber não existe → NotFoundError
```

#### 4.4 `tests/application/handlers/test_packs_handlers.py`
```python
# - criar ServicePack → persiste com tenant_id correto
# - comprar ClientPack → sessoes_restantes = pack.n_sessoes
# - listar packs do cliente → só os seus, só os ativos (sessoes_restantes > 0)
```

#### 4.5 `tests/application/handlers/test_loyalty_handlers.py`
```python
# - criar agendamento → LoyaltyAccount criado, pontos = duracao_minutos
# - redimir pontos suficientes → pontos_disponiveis decrementado, transação tipo="redeem"
# - redimir mais do que disponível → ConflictError
```

#### 4.6 `tests/application/handlers/test_birthday_handler.py`
```python
# - cliente com aniversário hoje e birthday_msg_year != ano_atual → envia
# - cliente com aniversário hoje e birthday_msg_year == ano_atual → não envia
# - cliente sem data_nascimento → ignorado
```

#### 4.7 `tests/application/handlers/test_campaign_handler.py`
```python
# - criar campanha → status="draft"
# - enviar campanha → status="sent", total_sent > 0, enviado_em preenchido
# - enviar campanha já enviada → erro ou idempotente
```

#### 4.8 `tests/application/handlers/test_stock_handlers.py`
```python
# - criar produto → stock_atual=0
# - ajustar stock com delta=+5 → stock_atual=5
# - ajustar stock com delta=-10 quando stock_atual=5 → stock_atual=-5 (permitido) ou ConflictError (decidir)
# - criar agendamento com ServiceProduct → stock deduzido automaticamente
```

#### 4.9 `tests/application/handlers/test_resource_handlers.py`
```python
# - criar agendamento com resource_id → persiste
# - criar agendamento com resource_id já ocupado no mesmo horário → ConflictError
```

#### 4.10 `tests/application/handlers/test_clinical_handlers.py`
```python
# - upsert clinical record → cria se não existe, atualiza se existe
# - sign consent → consentimento_assinado=True, consentimento_data preenchido
# - add note → ClinicalNote criada com clinical_record_id correto
```

#### 4.11 `tests/api/routes/test_new_routes.py`
Testes HTTP para todas as rotas novas (packs, loyalty, campaigns, payments, invoices, products, resources, clinical, saft):
```python
# Para cada rota: testar 200/201 com dados válidos, 401 sem auth, 403 com role errado, 404 com id inválido
```

---

### P1 — Melhorias de Backend (importante)

#### 4.12 Decremento automático de sessões de pack ao criar agendamento
Em `backend/application/handlers/appointment/create_appointment_handler.py`, após criar o agendamento, adicionar (best-effort):
```python
# Após criar appointment, verificar se o cliente tem ClientPack ativo para aquele service
# Se sim, decrementar sessoes_restantes -= 1
# Não falhar se não houver pack
```
O código actual não implementa isto — o `ClientPack` tem `sessoes_restantes` mas nunca é decrementado.

#### 4.13 Endpoint `GET /packs/all` (admin)
Falta endpoint para admin listar todos os `ClientPack` do tenant (não só os do cliente autenticado). Criar:
- `backend/application/queries/list_all_client_packs_query.py`
- `backend/application/handlers/packs/list_all_client_packs_handler.py`
- Adicionar rota `GET /packs/all` em `backend/api/routes/pack_routes.py` (admin only)

#### 4.14 Paginação nas listagens
Os endpoints que devolvem listas não têm paginação. Adicionar `skip: int = 0, limit: int = 50` nos handlers que devolvem listas grandes (appointments, clients, products, invoices, campaigns).

#### 4.15 Validação de stock negativo
Em `adjust_stock_handler.py`, decidir e implementar: permitir stock negativo ou lançar `ConflictError` quando `stock_atual + delta < 0`.

#### 4.16 Stripe — reembolso automático no cancelamento
Em `backend/application/handlers/appointment/cancel_appointment_handler.py` (verificar se existe ou criar), adicionar lógica best-effort:
```python
if appointment.payment_status == "paid":
    # chamar stripe.Refund.create(payment_intent=...)
    # setar appointment.payment_status = "refunded"
```

#### 4.17 Campanha — filtros de segmentação reais
`send_campaign_handler.py` provavelmente envia para todos os clientes. Implementar parsing do campo `segment_filters` (JSON) e aplicar os mesmos filtros que `get_client_segment_handler.py`.

---

### P2 — Frontend (melhorias e páginas em falta)

#### 4.18 Página de Confirmação de Presença (pública)
Criar `frontend/src/pages/public/ConfirmAppointmentPage.tsx` na rota `/confirm/:token`:
```tsx
// Ao montar: GET /appointments/confirm/{token}
// Se sucesso: mostrar "Presença confirmada! Até breve."
// Se erro: mostrar "Link inválido ou expirado."
// Sem autenticação necessária
```
Registar em `App.tsx`: `<Route path="/confirm/:token" element={<ConfirmAppointmentPage />} />`

#### 4.19 Dashboard admin — adicionar KPIs novos
Em `frontend/src/pages/admin/DashboardPage.tsx`, adicionar cards para:
- Total de pontos de fidelização em circulação (GET /loyalty/me não serve — criar endpoint ou usar stats)
- Produtos com stock baixo (GET /products?low_stock=true — mostrar count)
- Campanhas enviadas este mês

#### 4.20 Página de Agendamento Público — mostrar disponibilidade de sala
Em `frontend/src/pages/public/PublicBookPage.tsx`, ao seleccionar um serviço, mostrar se existe recurso disponível (opcional, só informativo).

#### 4.21 Perfil do cliente — mostrar data de nascimento
Em `frontend/src/pages/client/ProfilePage.tsx`, adicionar campo `data_nascimento` (date input) ao formulário de edição do perfil. Chamar `PUT /clients/{id}` com o campo.

#### 4.22 Página barber — ver fichas clínicas
Criar `frontend/src/pages/barber/ClientClinicalPage.tsx` na rota `/barber/clinical/:clientId`:
- Barbeiro pode ver ficha clínica do cliente antes da visita
- Ver alergias, notas, histórico de notas
- Adicionar nota clínica

#### 4.23 MyAppointmentsPage — mostrar status de pagamento e botão de pagamento
Em `frontend/src/pages/client/MyAppointmentsPage.tsx`:
- Adicionar coluna `status_pagamento` com badge (not_required=cinza, pending=amarelo, paid=verde)
- Para appointments com `payment_status === "pending"`, mostrar botão "Pagar" que chama `POST /payments/checkout` e redireciona para `checkout_url`

---

### P3 — Infraestrutura e Qualidade

#### 4.24 Variáveis de ambiente — documentar todas em `.env.example`
O ficheiro `.env.example` precisa de ser actualizado com as novas variáveis:
```env
# Stripe (F34)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=http://localhost:5173/client/appointments
STRIPE_CANCEL_URL=http://localhost:5173/client/appointments

# InvoiceXpress (F35)
INVOICEXPRESS_API_KEY=
INVOICEXPRESS_ACCOUNT_NAME=

# QR / Widget (F39, F40)
APP_BASE_URL=http://localhost:5173

# Scheduler
REMINDER_HOURS_BEFORE=24
REMINDER_CHECK_INTERVAL_MINUTES=30
```

#### 4.25 CI — adicionar cobertura de testes
Em `.github/workflows/`, actualizar o workflow para correr `pytest --cov=backend --cov-report=term-missing` e falhar se cobertura < 70%.

#### 4.26 Docker Compose — variáveis Stripe e InvoiceXpress
Adicionar ao `docker-compose.yml` (ou `docker-compose.prod.yml`) as novas env vars como placeholders comentados.

---

## 5. Como correr o projecto

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# Testes
venv/bin/python -m pytest tests/ -q
venv/bin/python -m ruff check backend/ --quiet

# Build frontend
cd frontend && npm run build
```

---

## 6. Convenções de commit e branch

- Branch: `feature/fXX-<nome-curto>` a partir de `main`
- Commit: `feat(fXX): descrição concisa` ou `fix: descrição`
- Após implementar: correr testes + ruff antes do commit
- PR: um por batch de features
- Co-author sempre: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

---

## 7. Ordem de execução recomendada

1. **Criar branch:** `git checkout main && git pull && git checkout -b feature/tests-f25-f41`
2. **Escrever todos os testes em falta** (secção 4.1 a 4.11) — um ficheiro por domínio
3. **Correr:** `venv/bin/python -m pytest tests/ -q --tb=short` — todos têm de passar
4. **Correr:** `venv/bin/python -m ruff check backend/ --quiet` — zero erros
5. **Commit + push + PR**
6. **Nova branch para P1:** implementar 4.12 (decremento de sessões) + 4.13 (GET /packs/all) + 4.17 (segment filters em campanhas)
7. **Nova branch para P2:** páginas frontend em falta (4.18 confirm page, 4.21 data_nascimento, 4.23 pagamento no cliente)
8. **Nova branch para P3:** `.env.example` + CI coverage

---

## 8. Gotchas conhecidos

| Problema | Causa | Solução |
|----------|-------|---------|
| `TypeError: cannot inherit non-frozen dataclass from frozen one` | Esqueceu `frozen=True` no `@dataclass` | Sempre `@dataclass(frozen=True)` |
| `MultipleHeads` no Alembic | Nova migração com `down_revision` errado | Verificar o head actual em `alembic/versions/` |
| Ruff I001 em `__init__.py` | Imports fora de ordem alfabética | Ordenar imports por nome de módulo |
| RTK filtra output do pytest | Proxy RTK corta output | Usar `venv/bin/python -m pytest` directamente |
| `diator` não encontra handler | Handler não tem `__init__.py` na pasta | Criar `__init__.py` vazio em cada pasta de handlers |
| Conflitos no rebase | Branch baseada em main desactualizado | `git fetch origin main && git rebase origin/main`, resolver conflitos mantendo AMBOS os lados |

---

## 9. Modelos SQLAlchemy — referência rápida

```
Appointment     — barber_id, client_id, service_id, tenant_id, start_at, end_at,
                  status, confirmation_token, confirmed_at, reminder_sent_at,
                  group_id, payment_status, resource_id
Barber          — user_id, nome, telefone, tenant_id
BarberAvailability — barber_id, day_of_week, start_time, end_time
BarberBlock     — barber_id, start_at, end_at, kind (break/day_off/manual)
Barbershop      — owner_user_id, nome, tenant_id
BarbershopMembership — barber_id, barbershop_id, role
Campaign        — nome, subject, body_template, segment_filters, status, tenant_id,
                  criado_em, enviado_em, total_sent
Client          — user_id, nome, email, telefone, data_nascimento, birthday_msg_year
ClinicalNote    — clinical_record_id, tenant_id, nota, criado_em, barber_id
ClinicalRecord  — client_id, tenant_id, alergias, notas_saude,
                  consentimento_assinado, consentimento_data
Feedback        — appointment_id, client_id, rating, comentario
Invoice         — appointment_id, tenant_id, invoice_number, invoice_url, status
LoyaltyAccount  — client_id, tenant_id, pontos_total, pontos_disponiveis
LoyaltyTransaction — loyalty_account_id, appointment_id, pontos, tipo, criado_em
Product         — nome, descricao, stock_atual, stock_minimo, preco_unitario, tenant_id
Resource        — nome, tipo, tenant_id
Service         — nome, duracao_minutos, preco, max_capacity, tenant_id
ServicePack     — nome, service_id, n_sessoes, preco, tenant_id
ClientPack      — client_id, service_pack_id, tenant_id, sessoes_restantes,
                  comprado_em, expira_em
ServiceProduct  — service_id, product_id, quantidade, tenant_id
Tenant          — nome, slug
User            — email, hashed_password, role (comma-separated)
Webhook         — url, secret, events (JSON), tenant_id
```

---

*Última actualização: 18 de março de 2026 — Claude Sonnet 4.6*
