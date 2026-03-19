# BarberPro — Barber Scheduler

Sistema SaaS de gestão de barbearias com suporte multi-tenant, agendamentos online, portal de cliente público e painel administrativo completo.

---

## Índice

- [Visão Geral](#visão-geral)
- [Stack Tecnológica](#stack-tecnológica)
- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Modelos de Dados](#modelos-de-dados)
- [API — Endpoints](#api--endpoints)
- [Frontend — Páginas e Rotas](#frontend--páginas-e-rotas)
- [Instalação e Execução](#instalação-e-execução)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Testes](#testes)
- [CI/CD](#cicd)

---

## Visão Geral

O **BarberPro** é uma plataforma de agendamento para barbearias com três perfis de utilizador distintos, incluindo suporte a serviços complementares de grooming e estética.

| Perfil | Acesso |
|--------|--------|
| **Admin** | Gestão total — barbearias, barbeiros, clientes, serviços, agendamentos, relatórios |
| **Barbeiro** | Agenda pessoal, gestão de bloqueios (férias, pausas) |
| **Cliente** | Marcação online (com ou sem login), histórico de agendamentos, avaliações |

Funcionalidades principais:

- **Multi-tenant** — cada barbearia opera num tenant isolado
- **Portal público** — clientes marcam via link sem conta (`/book/:tenantId`)
- **Slots dinâmicos** — cálculo automático de horários disponíveis com base na disponibilidade, bloqueios e agendamentos existentes
- **Feedback** — clientes avaliam barbeiros (1–5 estrelas) após o serviço
- **Relatórios** — receita diária e por intervalo de datas
- **Audit log** — registo de alterações por entidade
- **Soft delete** — registos nunca apagados fisicamente, com purga periódica opcional

---

## Stack Tecnológica

### Backend

| Componente | Tecnologia |
|-----------|------------|
| Framework | FastAPI 0.135 |
| Servidor | Uvicorn |
| ORM | SQLAlchemy 2.x |
| Base de dados | PostgreSQL (produção) / SQLite (dev e testes) |
| Migrações | Alembic |
| Arquitetura | CQRS + Mediator Pattern (`meditor`) |
| Autenticação | JWT — `python-jose` + `passlib[bcrypt]` |
| Validação | Pydantic v2 com `pydantic[email]` |
| Rate limiting | slowapi (200 req/min por defeito) |
| Linting | Ruff |

### Frontend

| Componente | Tecnologia |
|-----------|------------|
| Framework | React 19 |
| Routing | React Router DOM 7 |
| Linguagem | TypeScript 5 (strict mode) |
| HTTP Client | Axios |
| Build | Vite 7 |
| Estilos | Tailwind CSS 4 |
| Linting | ESLint 9 |

---

## Arquitetura

### CQRS + Mediator

Toda a lógica de negócio é separada em **Comandos** (escrita) e **Queries** (leitura), processados por handlers dedicados via mediator:

```
Pedido HTTP
    └─ Route Handler
        └─ build_mediator(db)
            └─ Command / Query
                └─ Handler
                    └─ Repository / Domain Logic
                        └─ Response
```

### Multi-Tenancy

Cada recurso (barbeiro, cliente, serviço, agendamento) tem `tenant_id`. O isolamento é imposto ao nível das queries via `BaseRepository[T]`. Nas rotas autenticadas, o tenant é identificado pelo header `X-Tenant-Id`.

### Soft Delete

Entidades têm campo `deleted` (Boolean) + `deleted_at` (DateTime). Todas as queries filtram `deleted = False`. O endpoint `DELETE /admin/purge` remove fisicamente registos apagados há mais de N dias.

### Autenticação e RBAC

- JWT gerado em `POST /auth/login`, passado como `Authorization: Bearer <token>`
- Roles: `admin`, `barber`, `client`
- Dependência `require_roles()` em FastAPI aplica controlo de acesso por endpoint

### Algoritmo de Slots

O `build_daily_slots` gera slots de 15 em 15 minutos dentro das janelas de disponibilidade do barbeiro, excluindo:

1. `BarberBlock` — bloqueios manuais (férias, breaks, folgas)
2. `Appointment` existentes — cada agendamento ocupa `duracao_minutos` do serviço

---

## Estrutura do Projeto

```
barber_scheduler/
├── main.py                        # Entry point FastAPI (CORS, middlewares, routers)
├── requirements.txt               # Dependências raiz (referência)
├── Makefile                       # Comandos de desenvolvimento
├── ruff.toml                      # Configuração do linter
├── alembic.ini
│
├── backend/
│   ├── requirements.txt           # Dependências usadas no CI
│   ├── api/
│   │   ├── routes/                # 14 ficheiros de rotas FastAPI
│   │   ├── *_http.py              # Factories de commands/queries por entidade
│   │   ├── auth_dependencies.py   # Dependências JWT e RBAC
│   │   └── error_http.py          # Mapeamento exceções → HTTP status codes
│   ├── application/
│   │   ├── commands/              # 28+ command dataclasses
│   │   ├── queries/               # 15+ query dataclasses
│   │   └── handlers/              # Handlers agrupados por entidade
│   ├── core/
│   │   ├── *.py                   # Modelos SQLAlchemy (Appointment, Barber, …)
│   │   ├── scheduling.py          # Cálculo de slots disponíveis
│   │   ├── exceptions.py          # Exceções de domínio (NotFoundError, ConflictError, …)
│   │   ├── security.py            # JWT encode/decode, password hashing
│   │   └── notifications.py       # Serviço de notificações
│   └── infrastructure/
│       ├── database.py            # SessionLocal, engine, Base
│       └── schemas.py             # Pydantic request/response schemas
│
├── repositories/
│   └── base_repository.py         # BaseRepository[T] genérico com tenant isolation
│
├── alembic/
│   └── versions/                  # Migrações de base de dados
│
├── tests/                         # Suite de testes (291 testes)
│   ├── api/routes/                # Testes de rotas (mock mediator)
│   ├── api/test_*.py              # Testes de http utils, auth, etc.
│   └── application/handlers/      # Testes de handlers (mock SQLAlchemy)
│
└── frontend/
    ├── src/
    │   ├── App.tsx                # Routing principal
    │   ├── components/            # Button, Input, Table, Navbar, Toast, Modal, …
    │   ├── contexts/
    │   │   └── AuthContext.tsx    # Estado de autenticação global
    │   ├── lib/api.ts             # Axios com base URL e interceptors JWT
    │   ├── pages/
    │   │   ├── admin/             # Dashboard, Barbershops, Barbers, Clients, Services, Appointments
    │   │   ├── barber/            # Schedule, Blocks
    │   │   ├── client/            # Book, MyAppointments, MyFeedback
    │   │   └── public/            # PublicBookPage (wizard sem login)
    │   └── types/index.ts         # Interfaces TypeScript dos modelos de domínio
    └── package.json
```

---

## Modelos de Dados

```
Tenant
├── Barbershop (N por tenant)
├── Barber
│   ├── BarberAvailability  (janelas de trabalho por dia da semana)
│   └── BarberBlock         (bloqueios: férias, breaks, folgas)
├── Client
├── Service (nome, duração em minutos, preço)
├── Appointment
│   ├── barber_id → Barber
│   ├── client_id → Client
│   ├── service_id → Service
│   └── start_at / end_at / created_at / updated_at
├── Feedback (1 por agendamento)
│   ├── rating (1–5)
│   └── comentario (até 2000 chars, opcional)
└── BarbershopMembership (utilizador ↔ barbearia com role)
```

Todos os modelos têm `deleted` (Boolean) + `deleted_at` (DateTime) para soft delete.

---

## API — Endpoints

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/auth/bootstrap-admin` | Criar primeiro admin | Não |
| POST | `/auth/register` | Auto-registo de cliente | Não |
| POST | `/auth/login` | Login → JWT token | Não |
| GET | `/auth/me` | Perfil do utilizador atual | Sim |
| POST | `/auth/users` | Criar utilizador | Admin |

### Barbearias

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST / GET | `/barbershops/` | Criar / listar barbearias | Admin |
| GET / PUT / PATCH / DELETE | `/barbershops/{id}` | CRUD barbearia | Admin |
| POST / GET | `/barbershops/{id}/memberships` | Gerir membros | Admin |
| DELETE | `/barbershops/{id}/memberships/{mid}` | Remover membro | Admin |

### Barbeiros e Disponibilidade

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST / GET | `/barbers/` | Criar / listar barbeiros | Admin / Admin, Cliente |
| GET / PUT / PATCH / DELETE | `/barbers/{id}` | CRUD barbeiro | Admin |
| POST / GET | `/barbers/{id}/availability/windows` | Janelas de disponibilidade | Admin |
| PATCH / DELETE | `/barbers/{id}/availability/windows/{aid}` | Editar / remover janela | Admin |
| POST / GET / DELETE | `/barbers/{id}/availability/blocks` | Bloqueios do barbeiro | Admin |
| GET | `/barbers/{id}/availability/slots` | Slots disponíveis (com login) | Admin, Barbeiro, Cliente |

### Clientes

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/clients/me` | Perfil de cliente próprio | Cliente |
| POST / GET | `/clients/` | Criar / listar clientes | Admin, Barbeiro |
| GET / PUT / PATCH / DELETE | `/clients/{id}` | CRUD cliente | Admin, Barbeiro |

### Serviços

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST / GET | `/services/` | Criar / listar serviços | Admin / Admin, Cliente |
| GET / PUT / PATCH / DELETE | `/services/{id}` | CRUD serviço | Admin |

### Agendamentos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/appointments/` | Criar agendamento | Admin, Barbeiro, Cliente |
| PATCH | `/appointments/{id}` | Reagendar | Admin, Barbeiro, Cliente |
| DELETE | `/appointments/{id}` | Cancelar | Admin, Barbeiro, Cliente |
| GET | `/appointments/{id}` | Detalhes | Admin, Barbeiro |
| GET | `/appointments/barbers/{id}` | Agenda do barbeiro | Admin, Barbeiro |
| GET | `/appointments/clients/me/appointments` | Meus agendamentos | Cliente |

### Feedback / Avaliações

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/feedback` | Criar avaliação (1 por agendamento) | Cliente |
| GET | `/feedback/me` | Minhas avaliações | Cliente |
| GET | `/feedback/barber/{id}` | Avaliações públicas de um barbeiro | Não |
| GET | `/admin/feedback` | Todas as avaliações | Admin |

### Públicos (sem autenticação)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/public/tenants/{id}/barbers` | Barbeiros do tenant |
| GET | `/public/tenants/{id}/services` | Serviços do tenant |
| GET | `/public/tenants/{id}/barbers/{bid}/slots` | Slots disponíveis |
| POST | `/public/appointments` | Criar agendamento sem conta |

### Admin — Relatórios, Audit e Stats

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/reports/daily` | Relatório diário de receita |
| GET | `/admin/reports/revenue` | Receita por intervalo de datas |
| GET | `/admin/audit` | Audit log por entidade e data |
| DELETE | `/admin/purge` | Purgar registos apagados (N dias) |
| GET | `/admin/export` | Exportar dados do tenant |
| GET | `/admin/stats` | Estatísticas do tenant |

### Sistema

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health/` | Health check (DB + API) |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

---

## Frontend — Páginas e Rotas

### Públicas (sem login)

| Rota | Descrição |
|------|-----------|
| `/login` | Login com email e password |
| `/register` | Auto-registo de cliente |
| `/book/:tenantId` | **Wizard de marcação pública** — 6 passos, mobile-first, sem conta |

O wizard público segue os passos: **Barbeiro → Serviço → Data → Horário → Dados pessoais → Confirmação**

### Admin (`/admin/*`)

| Rota | Descrição |
|------|-----------|
| `/admin` | Dashboard com estatísticas |
| `/admin/barbershops` | Gestão de barbearias |
| `/admin/barbers` | Gestão de barbeiros |
| `/admin/barbers/:id/availability` | Disponibilidades e bloqueios |
| `/admin/clients` | Gestão de clientes |
| `/admin/services` | Gestão de serviços |
| `/admin/appointments` | Todos os agendamentos |

### Barbeiro (`/barber/*`)

| Rota | Descrição |
|------|-----------|
| `/barber` | Agenda pessoal |
| `/barber/blocks` | Gerir bloqueios (férias, pausas) |

### Cliente (`/client/*`)

| Rota | Descrição |
|------|-----------|
| `/client` | Agendar (com login) |
| `/client/appointments` | Meus agendamentos + botão Avaliar em agendamentos passados |
| `/client/feedback` | Minhas avaliações com classificação em estrelas |

---

## Instalação e Execução

### Pré-requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL (ou SQLite para desenvolvimento)

### 1. Clonar o repositório

```bash
git clone https://github.com/xavigit99/barber_scheduler.git
cd barber_scheduler
```

### 2. Backend

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# Instalar dependências
pip install -r backend/requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com DATABASE_URL e AUTH_SECRET

# Aplicar migrações
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 4. Usando Make

```bash
make install          # Instalar dependências Python
make migrate          # Aplicar migrações Alembic
make run              # Iniciar servidor backend (reload)
make test             # Correr suite de testes
make lint             # Ruff check
make migrate-create msg="descrição"   # Nova migração
make clean            # Limpar __pycache__
```

### 5. Primeiro utilizador Admin

```bash
curl -X POST http://localhost:8000/auth/bootstrap-admin \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "changeme"}'
```

### 6. Link de marcação pública

Após criar uma barbearia e configurar os barbeiros, partilhar o link:

```
http://localhost:5173/book/<tenant_id>
```

Os clientes acedem sem qualquer conta e completam a marcação em 6 passos.

---

## Variáveis de Ambiente

| Variável | Padrão | Obrigatória | Descrição |
|----------|--------|-------------|-----------|
| `DATABASE_URL` | — | Sim | URI de conexão (ex: `postgresql://user:pass@localhost/barber`) |
| `AUTH_SECRET` | — | Sim (produção) | Chave secreta para assinar JWTs |
| `AUTH_TOKEN_TTL_SECONDS` | `86400` | Não | Validade do token JWT em segundos (24h) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Não | Origens CORS permitidas (vírgula-separadas) |
| `LOG_LEVEL` | `INFO` | Não | Nível de logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

Exemplo de `.env`:

```env
DATABASE_URL=postgresql://postgres:secret@localhost:5432/barber_scheduler
AUTH_SECRET=minha-chave-super-secreta-de-producao
AUTH_TOKEN_TTL_SECONDS=86400
ALLOWED_ORIGINS=https://minha-app.com,http://localhost:5173
LOG_LEVEL=INFO
```

---

## Testes

```bash
# Todos os testes
venv/bin/python -m pytest tests/ -q

# Ficheiro específico
venv/bin/python -m pytest tests/api/routes/test_public_routes.py -v

# Lint
venv/bin/ruff check backend/

# Build frontend (verificar TypeScript)
cd frontend && npm run build
```

Os testes usam **SQLite em memória** e mocks do mediator — não precisam de PostgreSQL a correr.

A suite inclui:
- Testes de handlers CQRS (mock SQLAlchemy)
- Testes de rotas HTTP (mock mediator)
- Testes de isolamento multi-tenant
- Testes de migrações Alembic

---

## CI/CD

### GitHub Actions — `ci.yml`

Executa em cada push para `main` ou `feature/**` e em Pull Requests.

**Job `lint`** — instala `ruff` e corre `ruff check .`

**Job `test`** — instala `backend/requirements.txt`, corre `make test` com `DATABASE_URL=sqlite:///:memory:`

### Notificações Telegram — `telegram-pr-notify.yml`

Envia mensagem no Telegram quando um PR é aberto ou atualizado.

Secrets necessários no repositório:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

## Runbook

### Health Check

```bash
GET /health/
# → { "status": "ok" }
```

### Logs

Emitidos em formato estruturado para stdout. Nível configurável via `LOG_LEVEL`.

### Deploy

```bash
# 1. Configurar variáveis de ambiente
# 2. Aplicar migrações
alembic upgrade head

# 3. Iniciar servidor
uvicorn main:app --host 0.0.0.0 --port 8000
```
