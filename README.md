# BarberPro — Barber Scheduler API

Sistema de gestão de barbearias construído em **FastAPI + SQLAlchemy** com arquitetura CQRS.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2 |
| Base de dados | PostgreSQL |
| Arquitetura | CQRS via Mediator (`diator`) |
| Auth | JWT (`python-jose`) |
| Migrations | Alembic |
| Testes | pytest + httpx |
| Lint | ruff |
| Contentor | Docker Compose |
| Frontend | React + TypeScript + Vite |

---

## Setup Local (sem Docker)

### Pré-requisitos

- Python 3.12+
- PostgreSQL (ou SQLite para dev/testes)
- Node.js 20+ (para o frontend)

### Backend

```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# editar .env com as tuas credenciais

# Aplicar migrações
make migrate

# Arrancar o servidor
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Setup com Docker

```bash
docker compose up --build
```

Inicia: PostgreSQL + FastAPI na porta 8000.

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | — | URI da base de dados (obrigatória) |
| `SECRET_KEY` | — | Chave secreta para JWT (obrigatória em produção) |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiração do token |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Origens CORS (separadas por vírgula) |
| `LOG_LEVEL` | `INFO` | Nível de logging (`DEBUG`, `INFO`, `WARNING`) |

---

## Makefile

```bash
make install        # instalar dependências
make test           # correr testes
make lint           # ruff check
make migrate        # alembic upgrade head
make migrate-create msg="descrição"  # nova migration
make run            # uvicorn dev server
make clean          # limpar __pycache__
```

---

## API

Documentação interativa disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Autenticação

```bash
# Login
POST /auth/login
{ "username": "admin", "password": "..." }

# Registo (clientes)
POST /auth/register
{ "username": "...", "email": "...", "password": "..." }
```

Todos os endpoints protegidos requerem:
```
Authorization: Bearer <token>
X-Tenant-Id: <tenant_id>   # para rotas com isolamento por tenant
```

---

## Testes

```bash
make test
```

Corre a suite completa com SQLite in-memory. Inclui:
- Testes de handlers (CQRS)
- Testes de rotas HTTP
- Testes de isolamento multi-tenant
- Testes de migrations Alembic

---

## Runbook

### Deploy

1. Definir variáveis de ambiente (ver tabela acima)
2. `make migrate` — aplicar migrações pendentes
3. `uvicorn main:app --host 0.0.0.0 --port 8000`

### Logs

Os logs são emitidos em formato JSON para stdout:
```json
{"timestamp": "2026-03-15T10:00:00Z", "level": "INFO", "logger": "main", "message": "..."}
```

### Health Check

```bash
GET /health/
# → { "status": "ok" }
```

### Bootstrap Admin

Na primeira execução, criar o admin:
```bash
POST /auth/bootstrap-admin
{ "username": "admin", "email": "admin@example.com", "password": "..." }
```
