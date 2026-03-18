# CODEX — Barber Scheduler

> Documento de referência completo para desenvolvimento autónomo.
> Lê na íntegra antes de escrever qualquer linha de código.

---

## 1. Visão Geral

**Barber Scheduler** é uma plataforma SaaS multi-tenant de gestão e agendamento para barbearias, salões e clínicas. Backend em Python (FastAPI + SQLAlchemy), frontend em React + TypeScript + Tailwind CSS, base de dados PostgreSQL.

O sistema segue CQRS via biblioteca `diator`: Commands (escrita) e Queries (leitura) são frozen dataclasses, processados por Handlers auto-descobertos. Toda a persistência passa por repositórios genéricos com soft-delete e filtro automático por tenant.

**Funcionalidades implementadas:** F0–F41 (auth, multi-tenant, agendamentos, disponibilidade, notificações email+WhatsApp, lembretes automáticos, confirmação de presença, agendamentos de grupo, recorrência, packs de sessões, fidelização, aniversários, segmentação, campanhas, pagamentos Stripe, faturação, SAF-T, stocks, salas/recursos, QR codes, widget embed, fichas clínicas).

---

## 2. Árvore do Projecto

```
barber_scheduler/
├── main.py                         # FastAPI app, APScheduler lifespan, CORS, routers
├── meditor.py                      # DI container + auto-discovery de handlers
├── requirements.txt                # FastAPI, SQLAlchemy, APScheduler, Stripe, httpx, qrcode
├── alembic/versions/               # 10 migrações encadeadas, head: e5f6a7b8c9d0
├── repositories/
│   └── base_repository.py          # BaseRepository[T] genérico
├── backend/
│   ├── api/
│   │   ├── auth_dependencies.py    # get_current_user(), require_roles()
│   │   ├── auth_http.py            # Builders: comando/query a partir de HTTP
│   │   ├── error_http.py           # to_http_exception(exc) → HTTPException
│   │   ├── tenant_header.py        # TENANT_HEADER_ALIAS, require_tenant_id()
│   │   ├── http_utils.py           # ensure_resource_found/deleted/payload_has_changes
│   │   ├── appointment_http.py     # HTTP→Command builders para appointments
│   │   ├── availability_http.py    # HTTP→Command builders para availability
│   │   ├── barber_http.py          # HTTP→Command builders para barbers
│   │   ├── barbershop_http.py      # HTTP→Command builders para barbershops
│   │   ├── client_http.py          # HTTP→Command builders para clients
│   │   ├── service_http.py         # HTTP→Command builders para services
│   │   ├── feedback_http.py        # HTTP→Command builders para feedback
│   │   ├── membership_http.py      # HTTP→Command builders para memberships
│   │   └── routes/                 # 27 routers FastAPI
│   │       ├── appointment_routes.py
│   │       ├── auth_routes.py
│   │       ├── availability_routes.py
│   │       ├── barber_routes.py
│   │       ├── barbershop_routes.py
│   │       ├── campaign_routes.py
│   │       ├── client_routes.py
│   │       ├── clinical_routes.py
│   │       ├── feedback_routes.py
│   │       ├── health_routes.py
│   │       ├── invoice_routes.py
│   │       ├── loyalty_routes.py
│   │       ├── membership_routes.py
│   │       ├── pack_routes.py
│   │       ├── payment_routes.py
│   │       ├── product_routes.py
│   │       ├── public_routes.py
│   │       ├── qr_routes.py
│   │       ├── report_routes.py
│   │       ├── resource_routes.py
│   │       ├── audit_routes.py
│   │       ├── saft_routes.py
│   │       ├── service_routes.py
│   │       ├── stats_routes.py
│   │       ├── webhook_routes.py
│   │       └── widget_routes.py
│   ├── application/
│   │   ├── commands/               # ~55 frozen dataclasses (Request)
│   │   ├── queries/                # ~40 frozen dataclasses (Request)
│   │   └── handlers/               # ~90 handlers em subpastas por domínio
│   │       ├── auth/
│   │       ├── barber/
│   │       ├── barbershop/
│   │       ├── service/
│   │       ├── client/
│   │       ├── clients/            # get_client_segment_handler
│   │       ├── appointment/
│   │       ├── availability/
│   │       ├── membership/
│   │       ├── feedback/
│   │       ├── audit/
│   │       ├── stats/
│   │       ├── report/
│   │       ├── webhook/
│   │       ├── retention/
│   │       ├── compliance/
│   │       ├── loyalty/
│   │       ├── packs/
│   │       ├── campaigns/
│   │       ├── resource/
│   │       ├── clinical/
│   │       └── product/
│   ├── core/                       # Modelos SQLAlchemy + lógica de domínio
│   │   ├── appointment.py
│   │   ├── barber.py
│   │   ├── barber_availability.py
│   │   ├── barber_block.py
│   │   ├── barbershop.py
│   │   ├── barbershop_membership.py
│   │   ├── birthdays.py            # send_birthday_messages(db)
│   │   ├── campaign.py
│   │   ├── client.py
│   │   ├── clinical.py
│   │   ├── exceptions.py
│   │   ├── feedback.py
│   │   ├── invoice.py
│   │   ├── logging_config.py
│   │   ├── loyalty.py
│   │   ├── membership_roles.py
│   │   ├── notifications.py        # NotificationService ABC + Log + SMTP
│   │   ├── product.py
│   │   ├── reminders.py            # send_appointment_reminders(db)
│   │   ├── resource.py
│   │   ├── roles.py                # ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
│   │   ├── scheduling.py           # build_daily_slots(), validações
│   │   ├── security.py             # PBKDF2 hash, JWT create/decode
│   │   ├── service.py
│   │   ├── service_pack.py
│   │   ├── tenant.py
│   │   ├── tenant_slug.py
│   │   ├── user.py
│   │   ├── webhook.py
│   │   ├── webhook_dispatcher.py
│   │   └── whatsapp.py             # WhatsAppService ABC + Log + CallMeBot
│   └── infrastructure/
│       ├── database.py             # engine, SessionLocal, Base, get_db()
│       └── schemas.py              # 58 classes Pydantic (DTOs)
├── tests/                          # ~50 ficheiros, ~320 testes
│   ├── infrastructure/
│   │   ├── test_database.py
│   │   └── test_migrations.py
│   ├── api/
│   │   ├── test_auth_dependencies.py
│   │   ├── test_auth_routes.py
│   │   ├── test_barber_http.py
│   │   ├── test_barber_routes.py
│   │   ├── test_client_http.py
│   │   ├── test_client_routes.py
│   │   ├── test_service_http.py
│   │   ├── test_service_routes.py
│   │   ├── test_barbershop_http.py
│   │   ├── test_barbershop_routes.py
│   │   ├── test_availability_http.py
│   │   ├── test_availability_routes.py
│   │   ├── test_appointment_routes.py
│   │   ├── test_public_routes.py
│   │   ├── test_membership_http.py
│   │   ├── test_membership_routes.py
│   │   └── test_http_utils.py
│   └── application/handlers/
│       ├── test_auth_handlers.py
│       ├── test_barber_handlers.py
│       ├── test_client_handlers.py
│       ├── test_service_handlers.py
│       ├── test_barbershop_handlers.py
│       ├── test_availability_handlers.py
│       ├── test_appointment_handlers.py
│       ├── test_appointment_tenant_isolation.py
│       ├── test_feedback_handlers.py
│       ├── test_feedback_tenant_isolation.py
│       ├── test_membership_handlers.py
│       ├── test_webhook_handlers.py
│       ├── test_recurring_appointment_handler.py
│       ├── test_audit_log_handler.py
│       ├── test_tenant_stats_handler.py
│       ├── test_tenant_export_handler.py
│       ├── test_purge_deleted_handler.py
│       ├── test_soft_delete_audit.py
│       ├── test_tenant_isolation.py
│       ├── test_update_client_handler.py
│       ├── test_scheduling.py
│       ├── test_security.py
│       └── test_notifications.py
└── frontend/src/
    ├── lib/api.ts                  # axios + interceptors (JWT, X-Tenant-Id)
    ├── lib/auth.ts                 # getToken(), getTenantId(), clearAuth()
    ├── contexts/AuthContext.tsx     # useAuth() → { user, token, tenantId, tenantName }
    ├── components/
    │   ├── Navbar.tsx              # Sidebar com links por role
    │   ├── Button.tsx
    │   ├── Input.tsx
    │   ├── Modal.tsx
    │   ├── Select.tsx
    │   ├── Spinner.tsx
    │   └── Toast.tsx
    ├── pages/admin/                # 21 páginas
    │   ├── DashboardPage.tsx
    │   ├── BarbershopsPage.tsx
    │   ├── BarbersPage.tsx
    │   ├── BarberAvailabilityPage.tsx
    │   ├── ClientsPage.tsx
    │   ├── ServicesPage.tsx
    │   ├── AppointmentsPage.tsx
    │   ├── ReportsPage.tsx
    │   ├── CompliancePage.tsx
    │   ├── AdminFeedbackPage.tsx
    │   ├── WebhooksPage.tsx
    │   ├── PacksPage.tsx
    │   ├── LoyaltyPage.tsx
    │   ├── CampaignsPage.tsx
    │   ├── PaymentsPage.tsx
    │   ├── InvoicesPage.tsx
    │   ├── StocksPage.tsx
    │   ├── ResourcesPage.tsx
    │   ├── ClinicalPage.tsx
    │   ├── SAFTPage.tsx
    │   └── ClientSegmentPage.tsx
    ├── pages/barber/               # 3 páginas
    │   ├── SchedulePage.tsx
    │   ├── BlocksPage.tsx
    │   └── AvailabilityPage.tsx
    ├── pages/client/               # 6 páginas
    │   ├── BookPage.tsx
    │   ├── MyAppointmentsPage.tsx
    │   ├── MyFeedbackPage.tsx
    │   ├── ProfilePage.tsx
    │   ├── MyPacksPage.tsx
    │   └── MyLoyaltyPage.tsx
    └── pages/public/               # 4 páginas
        ├── PublicBookPage.tsx
        ├── ClientRegisterPage.tsx
        ├── ClientLoginPage.tsx
        └── BarbershopsListPage.tsx
```

---

## 3. Regras de Arquitectura

### 3.1 Frozen Dataclasses (Commands e Queries)

Todos os Commands e Queries herdam de `diator.requests.Request`, que é frozen. A subclasse **tem de ser** frozen também, ou dá `TypeError`:

```python
from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True)
class CreateFooCommand(Request):
    nome: str
    tenant_id: int | None = None
```

- Sem métodos — apenas campos de dados
- Campos opcionais com `= None`
- Ficheiro em `backend/application/commands/` ou `backend/application/queries/`

### 3.2 Handlers

Cada Handler implementa `RequestHandler[TRequest, TResponse]` da `diator`:

```python
from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_foo_command import CreateFooCommand

class CreateFooHandler(RequestHandler[CreateFooCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateFooCommand):
        # lógica aqui
        return result
```

- Pasta: `backend/application/handlers/<domínio>/`
- Cada subpasta precisa de `__init__.py` (pode ser vazio)
- **Auto-descobertos** pelo `meditor.py` — sem registo manual

### 3.3 Como o meditor.py funciona

O `build_mediator(db)` faz:
1. Cria `di.Container` e liga `Session` → `lambda: db`
2. Percorre `backend/application/` com `os.walk`, importa cada `.py`
3. Para cada classe com método `handle` (excepto `RequestHandler`):
   - Liga-a no container DI
   - Lê `__orig_bases__` para extrair o tipo de Request
   - Regista `RequestMap.bind(RequestType, HandlerClass)`
4. Devolve `Mediator` configurado

**Nos testes** — instanciar directamente, sem mediator:
```python
handler = CreateFooHandler(db=mock_db)
result = await handler.handle(command)
```

### 3.4 BaseRepository[T]

```python
from repositories.base_repository import BaseRepository

repo = BaseRepository(Foo, db, tenant_id)  # tenant_id opcional
obj = repo.get(id)          # → Foo | None (filtra deleted=False + tenant_id)
objs = repo.list()          # → list[Foo]
obj = repo.create(dict)     # → Foo (add + commit + refresh)
obj = repo.update(id, dict) # → Foo | None (setattr cada campo + commit)
ok = repo.delete(id)        # → bool (soft-delete se model tiver .deleted)
```

Implementação real:
```python
class BaseRepository[T]:
    def __init__(self, model: type[T], db: Session, tenant_id: int | None = None):
        self.model = model
        self.db = db
        self.tenant_id = tenant_id

    def _query(self):
        query = self.db.query(self.model)
        if self.tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.filter(self.model.tenant_id == self.tenant_id)
        if hasattr(self.model, "deleted"):
            query = query.filter(self.model.deleted.is_(False))
        return query
```

### 3.5 Padrão de Route completo

```python
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import FooCreate, FooResponse
from meditor import build_mediator

router = APIRouter(prefix="/foos", tags=["Foos"])

@router.post("/", response_model=FooResponse, status_code=status.HTTP_201_CREATED)
async def create_foo(
    payload: FooCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    tid = require_tenant_id(tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(CreateFooCommand(nome=payload.nome, tenant_id=tid))
    except (NotFoundError, ConflictError) as exc:
        raise to_http_exception(exc) from exc
```

### 3.6 Excepções de domínio → HTTP

```python
# backend/core/exceptions.py
class ApplicationError(Exception): ...    # base
class AuthenticationError(ApplicationError): ...  # → 401
class ForbiddenError(ApplicationError): ...       # → 403
class NotFoundError(ApplicationError): ...        # → 404
class ConflictError(ApplicationError): ...        # → 409
class ValidationError(ApplicationError): ...      # → 400
```

Nas routes: `raise to_http_exception(exc) from exc`

### 3.7 Autenticação e Autorização

- JWT custom com `base64url` encode/decode (não é python-jose)
- `get_current_user()`: valida Bearer token → decode → busca user via mediator → verifica role
- `require_roles(*roles)`: verifica se algum role do user (split por vírgula) está na lista permitida
- Roles suportam multi-role: `"admin,barber"` — user tem ambos os papéis

### 3.8 Tenant Header

- Header: `X-Tenant-Id` (alias definido em `TENANT_HEADER_ALIAS`)
- `require_tenant_id(tenant_id)` → retorna int ou lança HTTP 400
- O frontend envia automaticamente via interceptor axios

### 3.9 Ruff — Python 3.12

```bash
venv/bin/python -m ruff check backend/ --fix
venv/bin/python -m ruff check backend/ --quiet
```

Regras obrigatórias:
- `X | Y` em vez de `Optional[X]` ou `Union[X, Y]`
- `class Repo[T]` em vez de `class Repo(Generic[T])`
- Imports I001: stdlib → third-party → local, alfabeticamente em cada grupo
- F401: sem imports não usados
- Sem `noqa` desnecessários

### 3.10 Migrações Alembic

Head actual: `e5f6a7b8c9d0`

Cadeia completa:
```
initial → add_user_id → multi_tenant → feedback → webhooks →
b2c3d4e5f6a7 (F25-F27) → c3d4e5f6a7b8 (F28-F31) →
d4e5f6a7b8c9 (F32-F35) → e5f6a7b8c9d0 (F36-F41)
```

Nova migração deve sempre referenciar o head actual:
```python
revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
```

---

## 4. Modelos SQLAlchemy — Todos os Campos

### Appointment (`appointments`)
```
id, barber_id→barbeiros, client_id→clientes, service_id→servicos, tenant_id→tenants
start_at (DateTime), end_at (DateTime), created_at, updated_at
deleted (Boolean), deleted_at (DateTime?)
status (String, default="pending")         — "pending" | "confirmed"
confirmation_token (String?, unique)       — UUID urlsafe para confirmação
confirmed_at (DateTime?)                   — quando foi confirmado
reminder_sent_at (DateTime?)               — quando o lembrete foi enviado
group_id (String?)                         — liga agendamentos de grupo (F27)
payment_status (String, default="not_required") — "not_required"|"pending"|"paid"|"refunded"
resource_id (Integer?, FK→resources)       — sala/recurso reservado (F38)
```

### Barber (`barbeiros`)
```
id, nome (String), email (String), telefone (String?)
tenant_id→tenants, user_id→users (nullable)
deleted, deleted_at
```

### Client (`clientes`)
```
id, nome, email, telefone (String?)
tenant_id→tenants, user_id→users (nullable)
data_nascimento (Date?)                    — para mensagens de aniversário
birthday_msg_year (Integer?)               — último ano em que recebeu mensagem
deleted, deleted_at
```

### Service (`servicos`)
```
id, nome, duracao_minutos (Integer), preco (Float)
max_capacity (Integer, default=1)          — F27 agendamentos de grupo
tenant_id→tenants
deleted, deleted_at
```

### User (`users`)
```
id, username (String, unique), email (String, unique)
hashed_password (String)
role (String)                              — "admin" | "barber" | "client" | "admin,barber"
```

### Tenant (`tenants`)
```
id, nome (String), slug (String, unique)
```

### Barbershop (`barbershops`)
```
id, nome, tenant_id→tenants, owner_user_id→users
deleted, deleted_at
```

### BarbershopMembership (`barbershop_memberships`)
```
id, barber_id→barbeiros, barbershop_id→barbershops
role (String)                              — "owner" | "member"
unique(barber_id, barbershop_id)
```

### BarberAvailability (`barber_availabilities`)
```
id, barber_id→barbeiros
weekday (Integer, 0-6), start_time (Time), end_time (Time)
```

### BarberBlock (`barber_blocks`)
```
id, barber_id→barbeiros
kind (String)                              — "break" | "day_off" | "block"
start_at (DateTime), end_at (DateTime)
reason (String?)
```

### Feedback (`feedbacks`)
```
id, appointment_id→appointments, client_id→clientes, barber_id→barbeiros
tenant_id→tenants
rating (Integer, 1-5), comentario (String?)
created_at, deleted, deleted_at
```

### Webhook (`webhooks`)
```
id, tenant_id→tenants
url (String), secret (String), events (JSON array)
created_at, deleted, deleted_at
```

### ServicePack (`service_packs`)
```
id, nome, service_id→servicos, n_sessoes (Integer), preco (Float)
tenant_id→tenants
deleted, deleted_at
```

### ClientPack (`client_packs`)
```
id, client_id→clientes, service_pack_id→service_packs
tenant_id→tenants
sessoes_restantes (Integer), comprado_em (DateTime), expira_em (Date?)
deleted, deleted_at
```

### LoyaltyAccount (`loyalty_accounts`)
```
id, client_id→clientes, tenant_id→tenants
pontos_total (Integer), pontos_disponiveis (Integer), updated_at
```

### LoyaltyTransaction (`loyalty_transactions`)
```
id, loyalty_account_id→loyalty_accounts, appointment_id (Integer?)
pontos (Integer), tipo (String)            — "earn" | "redeem"
criado_em (DateTime), descricao (String?)
```

### Campaign (`campaigns`)
```
id, nome, subject, body_template
segment_filters (String)                   — JSON: {"inactive_days": 30, "service_id": 5}
status (String)                            — "draft" | "sent"
tenant_id→tenants
criado_em, enviado_em (DateTime?), total_sent (Integer)
deleted, deleted_at
```

### Invoice (`invoices`)
```
id, appointment_id→appointments, tenant_id→tenants
invoice_number (String), invoice_url (String?)
status (String)                            — "draft" | "issued"
criado_em, deleted, deleted_at
```

### Product (`products`)
```
id, nome, descricao (String?)
stock_atual (Integer), stock_minimo (Integer), preco_unitario (Float)
tenant_id→tenants
deleted, deleted_at
```

### ServiceProduct (`service_products`)
```
id, service_id→servicos, product_id→products
quantidade (Integer)                       — quantidade consumida por execução do serviço
tenant_id→tenants
deleted, deleted_at
```

### Resource (`resources`)
```
id, nome, tipo (String)                   — "sala" | "cadeira" | "equipamento" | livre
tenant_id→tenants
deleted, deleted_at
```

### ClinicalRecord (`clinical_records`)
```
id, client_id→clientes, tenant_id→tenants
alergias (Text?), notas_saude (Text?)
consentimento_assinado (Boolean, default=False)
consentimento_data (DateTime?)
deleted, deleted_at
```

### ClinicalNote (`clinical_notes`)
```
id, clinical_record_id→clinical_records, tenant_id→tenants
nota (Text), criado_em (DateTime), barber_id (Integer?)
deleted, deleted_at
```

---

## 5. Todos os Endpoints

### Auth
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/auth/login` | — | Login: `{username, password}` → `{access_token, token_type, user}` |
| POST | `/auth/register` | — | Registo de admin: `{username, email, password}` |
| POST | `/auth/bootstrap` | — | Criar primeiro admin (one-time) |
| POST | `/auth/register/client` | — | Registo público de cliente |
| POST | `/auth/register/barber` | — | Registo de barbeiro (precisa tenant_id) |
| POST | `/auth/change-password` | JWT | `{current_password, new_password}` |
| GET | `/auth/me` | JWT | User actual |

### Barbershops
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/barbershops` | admin | Criar barbearia (cria tenant automaticamente) |
| GET | `/barbershops` | admin | Listar barbearias do admin |
| GET | `/barbershops/{id}` | admin | Detalhe |
| PUT | `/barbershops/{id}` | admin | Actualizar |
| DELETE | `/barbershops/{id}` | admin | Soft-delete |
| POST | `/barbershops/{id}/switch` | admin | Seleccionar barbearia activa (muda tenant) |

### Barbers
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/barbers` | admin | Criar barbeiro |
| GET | `/barbers` | admin | Listar |
| GET | `/barbers/{id}` | admin/barber | Detalhe |
| PUT | `/barbers/{id}` | admin | Actualizar |
| DELETE | `/barbers/{id}` | admin | Soft-delete |

### Clients
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/clients` | admin | Criar cliente |
| GET | `/clients` | admin | Listar |
| GET | `/clients/{id}` | admin/client | Detalhe |
| PUT | `/clients/{id}` | admin/client | Actualizar (inclui `data_nascimento`) |
| DELETE | `/clients/{id}` | admin | Soft-delete |
| GET | `/clients/segment` | admin | Filtrar: `?inactive_days=&min_spend=&service_id=&has_birthday_this_month=` |

### Services
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/services` | admin | Criar serviço |
| GET | `/services` | — | Listar (inclui `max_capacity`) |
| PUT | `/services/{id}` | admin | Actualizar |
| DELETE | `/services/{id}` | admin | Soft-delete |

### Availability & Slots
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/availability` | admin/barber | Criar janela semanal (weekday 0-6, start_time, end_time) |
| GET | `/availability/{barber_id}` | — | Listar janelas do barbeiro |
| DELETE | `/availability/{id}` | admin/barber | Remover |
| POST | `/blocks` | admin/barber | Criar bloqueio (break/day_off/block) |
| GET | `/blocks/{barber_id}` | — | Listar bloqueios |
| DELETE | `/blocks/{id}` | admin/barber | Remover |
| GET | `/slots/{barber_id}` | — | Slots livres: `?date=YYYY-MM-DD&service_id=&timezone=` |

### Appointments
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/appointments` | admin/client | Criar agendamento (valida overlap, barber+resource) |
| GET | `/appointments` | admin | Listar todos do tenant |
| GET | `/appointments/{id}` | admin/barber/client | Detalhe |
| POST | `/appointments/{id}/reschedule` | admin/client | Reagendar: `{nova_data_inicio}` |
| DELETE | `/appointments/{id}` | admin/client | Cancelar (soft-delete) |
| POST | `/appointments/recurring` | admin/client | Recorrente: `{recurrence: "weekly"|"biweekly", count: 1-12}` |
| GET | `/appointments/confirm/{token}` | — (público) | Confirmar presença via token único |
| POST | `/appointments/group` | admin | Grupo: `{barber_id, service_id, data_inicio, client_ids[]}` |

### Packs (F28)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/packs/services` | admin | Criar service pack: `{nome, service_id, n_sessoes, preco}` |
| GET | `/packs/services` | admin | Listar service packs do tenant |
| POST | `/packs/purchase` | admin | Comprar pack para cliente: `{client_id, service_pack_id, expira_em?}` |
| GET | `/packs/me` | client | Packs ativos do cliente autenticado |

### Loyalty (F30)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| GET | `/loyalty/me` | client | Conta e transacções do cliente |
| POST | `/loyalty/redeem` | client/admin | Resgatar: `{pontos, descricao?}` |

### Campaigns (F33)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/campaigns/` | admin | Criar campanha (status=draft) |
| GET | `/campaigns/` | admin | Listar |
| GET | `/campaigns/{id}` | admin | Detalhe |
| POST | `/campaigns/{id}/send` | admin | Enviar para segmento filtrado |

### Payments (F34)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/payments/checkout` | admin/client | Stripe Checkout: `{appointment_id}` → `{checkout_url}` |
| POST | `/payments/webhook` | — | Webhook Stripe (verifica assinatura HMAC) |

### Invoices (F35)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/invoices` | admin | Criar fatura: `{appointment_id}` |
| GET | `/invoices` | admin | Listar |
| GET | `/invoices/{id}` | admin | Detalhe |

### Products / Stock (F37)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/products` | admin | Criar produto |
| GET | `/products` | admin | Listar (`?low_stock=true` filtra stock_atual < stock_minimo) |
| PUT | `/products/{id}` | admin | Actualizar |
| DELETE | `/products/{id}` | admin | Soft-delete |
| POST | `/products/{id}/stock` | admin | Ajustar stock: `{delta: int, reason: str}` |
| POST | `/service-products` | admin | Ligar produto a serviço: `{service_id, product_id, quantidade}` |
| GET | `/service-products/{service_id}` | admin | Produtos consumidos pelo serviço |

### Resources (F38)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/resources` | admin | Criar: `{nome, tipo}` |
| GET | `/resources` | admin | Listar |
| DELETE | `/resources/{id}` | admin | Soft-delete |

### Clinical (F41)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| GET | `/clinical/{client_id}` | admin/barber | Ficha clínica |
| PUT | `/clinical/{client_id}` | admin/barber | Criar/actualizar: `{alergias?, notas_saude?}` |
| POST | `/clinical/{client_id}/consent` | admin/barber | Assinar consentimento |
| POST | `/clinical/{client_id}/notes` | admin/barber | Adicionar nota: `{nota}` |
| GET | `/clinical/{client_id}/notes` | admin/barber | Listar notas |

### Admin / Observabilidade
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| GET | `/admin/reports/daily` | admin | Relatório diário |
| GET | `/admin/reports/revenue` | admin | Receita por período |
| GET | `/admin/audit` | admin | Audit log |
| GET | `/admin/stats` | admin | KPIs do tenant (barbers, clients, services, appointments_month, cancelled_month, revenue_month) |
| POST | `/admin/purge` | admin | GDPR purge: `{entity, older_than_days}` |
| GET | `/admin/export` | admin | GDPR export JSON |
| GET | `/admin/saft` | admin | SAF-T: `?year=2026` |

### Público (sem autenticação)
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| GET | `/public/barbershops` | — | Listar barbearias |
| GET | `/public/{tenant_id}/services` | — | Serviços do tenant |
| GET | `/public/{tenant_id}/barbers` | — | Barbeiros do tenant |
| GET | `/public/{tenant_id}/slots` | — | Slots livres |
| POST | `/public/{tenant_id}/book` | — | Booking sem auth (cria/reutiliza cliente por email) |
| GET | `/public/qr/{tenant_id}` | — | QR code PNG (link para página de booking) |
| GET | `/public/widget/{tenant_id}` | — | Snippet JavaScript para embed |

### Feedback / Webhooks / Memberships / Health
| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/feedback` | client | Criar avaliação: `{appointment_id, rating, comentario?}` |
| GET | `/feedback` | admin/barber/client | Listar (filtrado por role) |
| POST | `/webhooks` | admin | Criar: `{url, secret, events[]}` |
| GET | `/webhooks` | admin | Listar |
| DELETE | `/webhooks/{id}` | admin | Remover |
| POST | `/memberships` | admin | Criar membership barbeiro↔barbearia |
| GET | `/memberships` | admin | Listar |
| DELETE | `/memberships/{id}` | admin | Remover |
| GET | `/health` | — | Health check |

---

## 6. Notificações

### NotificationService (ABC)

Singleton em `backend/core/notifications.py`, acedido via `get_notification_service()`:

```python
class NotificationService(ABC):
    def send_confirmation(self, notif: AppointmentNotification) -> None: ...
    def send_cancellation(self, notif: AppointmentNotification) -> None: ...
    def send_reschedule(self, notif: AppointmentNotification) -> None: ...
    def send_reminder(self, notif: AppointmentNotification) -> None: ...
    def send_birthday(self, client_name: str, client_email: str) -> None: ...
    def send_campaign(self, client_name: str, client_email: str, subject: str, body: str) -> None: ...

@dataclass
class AppointmentNotification:
    client_name: str
    client_email: str
    barber_name: str
    service_name: str
    start_at: datetime
    appointment_id: int
    confirmation_token: str | None = None   # incluído no email de confirmação
    app_base_url: str | None = None         # URL base para link de confirmação
```

**Implementações:**
- `LogNotificationService` — logger.info (dev/testes)
- `SmtpNotificationService` — SMTP real com emails formatados em português

**Factory:** `build_notification_service()` → se `SMTP_HOST` definido, SMTP; senão, Log.

### WhatsAppService (ABC)

Em `backend/core/whatsapp.py`, acedido via `build_whatsapp_service()`:

```python
class WhatsAppService(ABC):
    def notify_client_reminder(client_phone, client_name, barber_name, service_name, start_at, appointment_id): ...
    def notify_barber_new_appointment(barber_phone, barber_name, client_name, service_name, start_at, appointment_id): ...
    def notify_barber_cancellation(barber_phone, barber_name, client_name, service_name, start_at, appointment_id): ...
    def notify_barber_reschedule(barber_phone, barber_name, client_name, service_name, new_start_at, appointment_id): ...
    def notify_client_birthday(client_phone, client_name): ...
```

**Implementações:**
- `LogWhatsAppService` — logger.info
- `CallMeBotWhatsAppService` — HTTP GET para `api.callmebot.com/whatsapp.php`

**Factory:** `build_whatsapp_service()` → se `CALLMEBOT_API_KEY` definido, CallMeBot; senão, Log.

---

## 7. APScheduler — Jobs Agendados

Configurado no `lifespan` do FastAPI em `main.py`:

```python
# Lembretes (F25) — a cada N minutos
scheduler.add_job(_run_reminders, "interval", minutes=REMINDER_CHECK_INTERVAL_MINUTES)
# → backend.core.reminders.send_appointment_reminders(db)
# → Encontra appointments com start_at em 23h30–24h30, reminder_sent_at IS NULL
# → Envia email + WhatsApp ao cliente
# → Marca reminder_sent_at = now

# Aniversários (F31) — diário às 09:00
scheduler.add_job(_run_birthdays, "cron", hour=9, minute=0)
# → backend.core.birthdays.send_birthday_messages(db)
# → Filtra clientes com data_nascimento.day/month == hoje, birthday_msg_year != ano_actual
# → Envia email + WhatsApp
# → Marca birthday_msg_year = ano_actual
```

---

## 8. Variáveis de Ambiente

```env
# ── Core ──────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://barber:secret@localhost:5432/barber_scheduler
AUTH_SECRET=change-me-in-production-min-32-chars
AUTH_TOKEN_TTL_SECONDS=86400
ALLOWED_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO

# ── SMTP (omitir → LogNotificationService) ──────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@barberpro.app
SMTP_PASSWORD=app-password
SMTP_SENDER=noreply@barberpro.app
SMTP_USE_TLS=true

# ── WhatsApp (omitir → LogWhatsAppService) ──────────────────────────
CALLMEBOT_API_KEY=123456

# ── APScheduler ─────────────────────────────────────────────────────
REMINDER_HOURS_BEFORE=24
REMINDER_CHECK_INTERVAL_MINUTES=30

# ── Stripe (omitir → HTTP 503 no checkout) ──────────────────────────
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=http://localhost:5173/client/appointments
STRIPE_CANCEL_URL=http://localhost:5173/client/appointments

# ── InvoiceXpress (omitir → draft local) ────────────────────────────
INVOICEXPRESS_API_KEY=
INVOICEXPRESS_ACCOUNT_NAME=

# ── QR / Widget ─────────────────────────────────────────────────────
APP_BASE_URL=http://localhost:5173

# ── PostgreSQL (docker-compose) ─────────────────────────────────────
POSTGRES_USER=barber
POSTGRES_PASSWORD=secret
POSTGRES_DB=barber_scheduler
```

---

## 9. Padrões de Teste

### 9.1 Handler test — sem HTTP, db mockado

```python
import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_foo_command import CreateFooCommand
from backend.application.handlers.foo.create_foo_handler import CreateFooHandler
from backend.core.exceptions import NotFoundError


class CreateFooHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_persists_foo(self):
        db = MagicMock()
        # Configurar queries na ordem em que são chamadas no handler
        dependency_query = MagicMock()
        db.query.side_effect = [dependency_query]
        dependency_query.filter.return_value = dependency_query
        dependency_query.first.return_value = MagicMock(id=1)  # dependência existe

        handler = CreateFooHandler(db)
        await handler.handle(CreateFooCommand(nome="Test", tenant_id=1))

        db.add.assert_called_once()
        db.commit.assert_called()

    async def test_dependency_not_found_raises(self):
        db = MagicMock()
        dep_query = MagicMock()
        db.query.return_value = dep_query
        dep_query.filter.return_value = dep_query
        dep_query.first.return_value = None  # dependência não existe

        handler = CreateFooHandler(db)
        with self.assertRaises(NotFoundError):
            await handler.handle(CreateFooCommand(nome="Test", dep_id=99, tenant_id=1))
```

### 9.2 Route test — mediator mockado

```python
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.api.routes.foo_routes import create_foo
from backend.core.exceptions import ConflictError
from backend.infrastructure.schemas import FooCreate


class FakeMediator:
    def __init__(self, result=None, sequence=None):
        self.results = list(sequence) if sequence else [result]
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        r = self.results.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def _admin():
    return SimpleNamespace(id=1, role="admin")


class FooRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_returns_201(self):
        fake = SimpleNamespace(id=1, nome="Test", tenant_id=1)
        mediator = FakeMediator(fake)

        with patch("backend.api.routes.foo_routes.build_mediator", return_value=mediator):
            result = await create_foo(
                payload=FooCreate(nome="Test"),
                db=object(),
                current_user=_admin(),
                tenant_id=1,
            )

        assert result.nome == "Test"

    async def test_conflict_raises_409(self):
        mediator = FakeMediator(ConflictError("exists"))

        with patch("backend.api.routes.foo_routes.build_mediator", return_value=mediator):
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as ctx:
                await create_foo(
                    payload=FooCreate(nome="X"),
                    db=object(),
                    current_user=_admin(),
                    tenant_id=1,
                )
            assert ctx.exception.status_code == 409
```

### 9.3 Correr testes

```bash
venv/bin/python -m pytest tests/ -q --tb=short
venv/bin/python -m ruff check backend/ --quiet
```

---

## 10. Frontend — Convenções

### Axios interceptor (`lib/api.ts`)

```typescript
const api = axios.create({ baseURL: 'http://localhost:8000' });

api.interceptors.request.use(config => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (!config.headers['skipTenantHeader']) {
    const tid = getTenantId();
    if (tid) config.headers['X-Tenant-Id'] = tid;
  }
  return config;
});

api.interceptors.response.use(r => r, error => {
  if (error.response?.status === 401) window.location.href = '/login';
  return Promise.reject(error);
});
```

### Auth Context (`contexts/AuthContext.tsx`)

- `useAuth()` → `{ user, token, tenantId, tenantName, clientId, barberId, loading, login, logout, selectTenant }`
- `login(username, password)` → POST `/auth/login` → guarda token + resolve perfil
- `selectTenant(id, name)` → muda `X-Tenant-Id` para todas as requests

### Estrutura de página admin

```tsx
import { useEffect, useState } from 'react';
import Navbar from '../../components/Navbar';
import Spinner from '../../components/Spinner';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../lib/api';

interface Foo { id: number; nome: string; tenant_id: number; }

export default function FoosPage() {
  const { tenantId } = useAuth();
  const [items, setItems] = useState<Foo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [nome, setNome] = useState('');

  const load = async () => {
    try { const { data } = await api.get<Foo[]>('/foos'); setItems(data); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [tenantId]);

  const handleCreate = async () => {
    await api.post('/foos', { nome });
    setShowModal(false); setNome(''); load();
  };

  if (loading) return (
    <div className="flex min-h-screen bg-slate-950">
      <Navbar /><main className="ml-60 flex-1 flex items-center justify-center"><Spinner /></main>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <main className="ml-60 flex-1 p-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Foos</h1>
          <button onClick={() => setShowModal(true)}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm">
            + Novo
          </button>
        </div>
        <div className="bg-slate-900 rounded-xl border border-slate-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-800">
                <th className="px-4 py-3">Nome</th>
                <th className="px-4 py-3">Acoes</th>
              </tr>
            </thead>
            <tbody>
              {items.map(f => (
                <tr key={f.id} className="border-t border-slate-800">
                  <td className="px-4 py-3">{f.nome}</td>
                  <td className="px-4 py-3">
                    <button onClick={() => api.delete(`/foos/${f.id}`).then(load)}
                      className="text-red-400 hover:text-red-300 text-xs">Eliminar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {showModal && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-slate-900 rounded-xl border border-slate-700 p-6 w-full max-w-md">
              <h2 className="text-lg font-semibold text-white mb-4">Novo Foo</h2>
              <input value={nome} onChange={e => setNome(e.target.value)} placeholder="Nome"
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 w-full mb-4" />
              <div className="flex gap-3 justify-end">
                <button onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 text-sm">
                  Cancelar
                </button>
                <button onClick={handleCreate}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm">
                  Criar
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
```

### Badges de status

```tsx
const statusBadge = (status: string) => {
  const map: Record<string, string> = {
    draft:         'bg-yellow-900 text-yellow-300',
    sent:          'bg-emerald-900 text-emerald-300',
    pending:       'bg-yellow-900 text-yellow-300',
    confirmed:     'bg-emerald-900 text-emerald-300',
    paid:          'bg-emerald-900 text-emerald-300',
    not_required:  'bg-slate-700 text-slate-400',
    refunded:      'bg-red-900 text-red-300',
  };
  return <span className={`px-2 py-1 rounded-full text-xs font-medium ${map[status] ?? 'bg-slate-700 text-slate-400'}`}>{status}</span>;
};
```

### Rotas em App.tsx

```tsx
// Dentro de <Routes>:
<Route path="/admin/foos" element={<FoosPage />} />

// Navbar.tsx — adminLinks array:
{ to: '/admin/foos', label: 'Foos', requiresTenant: true }
```

---

## 11. Tarefas Pendentes — Priorizadas

### P0 — Testes (F25–F41)

Faltam testes para todas as features novas. Criar em `tests/application/handlers/`:

#### `test_reminders_handler.py`
- `test_sends_reminder_when_appointment_in_24h` — appointment com start_at = now + 24h, reminder_sent_at=None → assert send_reminder chamado, reminder_sent_at preenchido
- `test_does_not_resend_if_already_sent` — reminder_sent_at já preenchido → send_reminder NÃO chamado
- `test_skips_deleted_appointments` — deleted=True → send_reminder NÃO chamado
- `test_skips_appointment_outside_window` — start_at = now + 72h → NÃO chamado
- Mock: `patch("backend.core.notifications.get_notification_service")` + `patch("backend.core.whatsapp.build_whatsapp_service")`

#### `test_confirm_appointment_handler.py`
- `test_valid_token_sets_confirmed` — confirmation_token="abc123", status="pending" → status="confirmed", confirmed_at preenchido
- `test_invalid_token_raises_not_found` — token inexistente → NotFoundError

#### `test_group_appointment_handler.py`
- `test_creates_one_per_client_with_same_group_id` — service.max_capacity=3, client_ids=[1,2] → db.add chamado 2x, mesmo group_id
- `test_exceeds_capacity_raises_conflict` — max_capacity=1, client_ids=[1,2] → ConflictError

#### `test_packs_handlers.py`
- `test_create_service_pack_persists` — service existe → ServicePack criado
- `test_purchase_sets_sessoes_restantes` — pack com n_sessoes=10 → ClientPack.sessoes_restantes=10
- `test_list_client_packs_returns_only_active` — filtra sessoes_restantes > 0

#### `test_loyalty_handlers.py`
- `test_redeem_deducts_points` — pontos_disponiveis=100, resgatar 30 → 70
- `test_redeem_insufficient_raises_conflict` — pontos_disponiveis=10, resgatar 50 → ConflictError
- `test_loyalty_account_autocreated_if_missing` — primeira vez → account criado

#### `test_birthday_handler.py`
- `test_sends_message_today` — data_nascimento.day/month == hoje, birthday_msg_year=2025 → send_birthday chamado, birthday_msg_year=2026
- `test_does_not_resend_same_year` — birthday_msg_year=2026 → NÃO chamado
- `test_skips_null_birthday` — data_nascimento=None → NÃO chamado
- `test_skips_deleted` — deleted=True → NÃO chamado

#### `test_campaign_handler.py`
- `test_create_sets_draft` — status == "draft"
- `test_send_updates_status_and_count` — 2 clientes → status="sent", total_sent=2
- `test_send_already_sent_raises` — status="sent" → ValidationError
- `test_segment_filters_applied` — `{"inactive_days": 90}` → só inativos recebem

#### `test_stock_handlers.py`
- `test_create_product_persists` — stock_atual=0
- `test_adjust_increases` — stock=5, delta=+3 → 8
- `test_adjust_decreases` — stock=10, delta=-3 → 7
- `test_appointment_deducts_stock` — ServiceProduct.quantidade=2, stock=10 → 8 após criar appointment

#### `test_resource_handlers.py`
- `test_appointment_with_resource` — resource_id=5 → appointment.resource_id == 5
- `test_resource_conflict` — recurso ocupado no mesmo horário → ConflictError
- `test_no_conflict_different_times` — recurso ocupado 10h-11h, novo 11h-12h → sucesso

#### `test_clinical_handlers.py`
- `test_upsert_creates_if_missing` — cliente sem ficha → ClinicalRecord criado
- `test_upsert_updates_existing` — ficha existente → campos actualizados, mesmo ID
- `test_sign_consent` — consentimento_assinado=False → True, consentimento_data preenchido
- `test_add_note` — ClinicalNote criada com clinical_record_id correcto

Criar em `tests/api/routes/`:
- `test_packs_routes.py`
- `test_loyalty_routes.py`
- `test_campaigns_routes.py`
- `test_payments_routes.py`
- `test_invoices_routes.py`
- `test_products_routes.py`
- `test_resources_routes.py`
- `test_clinical_routes.py`

Cada um: testar 201/200 com auth, 401 sem auth, 403 com role errado. Seguir padrão de `test_appointment_routes.py`.

---

### P1 — Backend

#### 11.1 Decremento de sessões de pack ao criar agendamento

Em `backend/application/handlers/appointment/create_appointment_handler.py`, após o bloco de dedução de stock, adicionar best-effort:

```python
try:
    from backend.core.service_pack import ClientPack, ServicePack
    active_pack = (
        self.db.query(ClientPack)
        .join(ServicePack, ServicePack.id == ClientPack.service_pack_id)
        .filter(
            ClientPack.client_id == command.client_id,
            ClientPack.tenant_id == tenant_id,
            ClientPack.deleted.is_(False),
            ClientPack.sessoes_restantes > 0,
            ServicePack.service_id == command.service_id,
        )
        .first()
    )
    if active_pack:
        active_pack.sessoes_restantes -= 1
        self.db.commit()
except Exception:  # noqa: BLE001
    pass
```

#### 11.2 Endpoint `GET /packs/all` (admin)

Query + Handler + Rota para admin ver todos os ClientPacks do tenant.

#### 11.3 Stripe refund no cancelamento

Em `cancel_appointment_handler.py`, se `appointment.payment_status == "paid"`, criar refund Stripe e marcar como "refunded".

#### 11.4 Paginação

Adicionar `skip: int = 0, limit: int = 50` nas queries de listagem grande (appointments, invoices, campaigns, products). No handler: `.offset(query.skip).limit(query.limit)`.

#### 11.5 Actualizar `.env.example`

Adicionar variáveis Stripe, InvoiceXpress, APScheduler, APP_BASE_URL.

---

### P2 — Frontend

#### 11.6 Página pública de confirmação

`frontend/src/pages/public/ConfirmAppointmentPage.tsx`:
- Rota: `/confirm/:token`
- Ao montar: GET `/appointments/confirm/{token}`
- Sucesso: card verde "Presenca confirmada!"
- Erro 404: card vermelho "Link invalido ou ja utilizado."
- Sem Navbar

#### 11.7 Data de nascimento no perfil do cliente

Em `ProfilePage.tsx`: adicionar `<input type="date">` para `data_nascimento`, incluir no PUT.

#### 11.8 Pagamento e estado em MyAppointments

Em `MyAppointmentsPage.tsx`:
- Coluna `Pagamento`: badge por payment_status + botao "Pagar" (POST `/payments/checkout` → redirect)
- Coluna `Estado`: badge pending/confirmed

#### 11.9 Fichas clínicas para barbeiro

`frontend/src/pages/barber/ClientClinicalPage.tsx`:
- Rota: `/barber/clinical/:clientId`
- Barbeiro pode ver ficha e adicionar notas (POST), mas NÃO editar alergias/notas_saude

#### 11.10 Dashboard KPIs novos

Em `DashboardPage.tsx`: cards para produtos com stock baixo (GET `/products?low_stock=true`) e campanhas enviadas este mês.

---

### P3 — Infra

#### 11.11 Coverage no CI

Adicionar `pytest-cov` a `requirements.txt` e no workflow:
```yaml
- run: venv/bin/python -m pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=65
```

#### 11.12 Docker Compose

Adicionar variáveis Stripe, InvoiceXpress, APP_BASE_URL, REMINDER_HOURS_BEFORE ao serviço `api`.

---

## 12. Gotchas

| Problema | Causa | Solução |
|----------|-------|---------|
| `TypeError: cannot inherit non-frozen dataclass from frozen one` | Esqueceu `frozen=True` no Command/Query | Sempre `@dataclass(frozen=True)` |
| `MultipleHeads` Alembic | `down_revision` errado | Ler `alembic/versions/` — head actual: `e5f6a7b8c9d0` |
| Ruff I001 | Imports fora de ordem | Ordenar: stdlib → third-party → local, alfabeticamente |
| `diator` não encontra handler | Falta `__init__.py` na pasta | Criar ficheiro vazio |
| `get_notification_service()` retorna instância real nos testes | Singleton module-level | `patch("backend.core.notifications.get_notification_service")` |
| `build_whatsapp_service()` faz I/O | Tenta HTTP nos testes | `patch("backend.core.whatsapp.build_whatsapp_service")` |
| `require_tenant_id` lança HTTP 400 | `tenant_id=None` nos testes | Passar sempre `tenant_id=1` |
| `db.query.side_effect` | Handler faz múltiplos `db.query()` | Configurar lista na ordem de chamada |
| Rebase conflito em `schemas.py` | Ambas branches adicionam schemas | Manter TODOS os schemas de ambos os lados |
| RTK filtra output do pytest | Proxy RTK corta stdout | Usar `venv/bin/python -m pytest` directamente |
| Ruff UP046 em BaseRepository | `class Repo(Generic[T])` vs `class Repo[T]` | Usar sintaxe 3.12: `class BaseRepository[T]` |
| Testes com import cíclico | Imports top-level de models | Usar imports locais dentro de funções (ver `reminders.py`) |

---

## 13. Ordem de Execução Recomendada

```
 1.  git checkout main && git pull
 2.  git checkout -b feature/tests-f25-f41
 3.  Escrever todos os ficheiros de teste (secção P0)
 4.  venv/bin/python -m pytest tests/ -q --tb=short
 5.  venv/bin/python -m ruff check backend/ --quiet
 6.  git add tests/ && git commit -m "test: handler + route tests for F25-F41"
 7.  git push -u origin feature/tests-f25-f41 → PR

 8.  git checkout main && git checkout -b feature/backend-p1
 9.  Implementar 11.1 (pack decrement) + 11.2 (GET /packs/all) + 11.5 (.env.example)
10.  Testes + ruff + commit + push → PR

11.  git checkout main && git checkout -b feature/frontend-p2
12.  Implementar 11.6 (confirm page) + 11.7 (birthday) + 11.8 (payment badges) + 11.10 (KPIs)
13.  cd frontend && npm run build (zero erros TypeScript)
14.  Commit + push → PR
```

---

*Gerado em 18 de marco de 2026 por Claude Opus 4.6*
*Features: F0–F41 (backend + frontend) | ~320 testes | ~90 handlers | 27 routers | 34 paginas React*
