# AGENTS.md — projeto-zoe-alpha (ASI)

## Projeto
Sistema de gestão de assistência técnica (OS) multi-tenant com FastAPI + Next.js.

## Stack Atual
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
- **Frontend**: Next.js 16 + shadcn/ui + recharts + TypeScript
- **Banco**: PostgreSQL 16 (Docker dev)
- **Auth**: Custom JWT (PyJWT)
- **Infra**: Docker Compose (4 containers: db, api, frontend, adminer)

## Agentes Responsáveis
- **Heisenberg**: Backend Python (routers, services, models, schemas, migrations)
- **Steve**: Frontend Next.js (páginas, componentes, API clients)
- **Sheldon**: NÃO se aplica — este projeto tem backend FastAPI, não Server Actions
- **Elliot**: QA + LSP diagnostics
- **Loki**: Git conventional commits
- **Neo**: DevOps (deploy Railway + Vercel quando sair do Docker dev)

## Regras Específicas

### Backend (Heisenberg)
- Toda tabela DEVE ter `tenant_id`. Queries SEMPRE filtradas
- Protocolo sequencial `ASI-YY-XXXX` para ServiceOrders
- NUNCA alterar `models.py` sem Alembic migration imediata
- Service layer ISOLADA dos routers — controllers são thin
- Soft delete via `deleted_at` (nullable)
- Enums: `UserRole` (ADMIN/TECHNICIAN), `ServiceStatus` (7 estados)

### Frontend (Steve)
- Server Components/Actions → rede Docker (`INTERNAL_API_URL = http://api:8000`)
- Client Components → proxy (`NEXT_PUBLIC_API_URL = http://localhost:8000`)
- 401 → `redirect('/login')`. NUNCA `throw new Error`
- Combobox (não Select) em listas dinâmicas
- API clients em `src/lib/api/` — tipados com interfaces TypeScript

### Infra
- Docker Compose para dev local: `make up`
- Nenhum deploy serverless ainda — quando pronto, Neo migra
- Seed credentials: admin@amenti.io / amenti2026

## Sprint Atual
Sprint 28 — Blindagem de Segurança (em andamento)
- C1-C3 (Critical): pg_lock condicional, secrets rotation, stale import
- H1-H6 (High): server-side role, user email scoped, tenant filter OS history, apiFetch raw, auth-context refactor, mass-assignment fix
- 35 apiFetch call sites migrados para nova assinatura
- UserCreate sem `role` — register sempre TECHNICIAN
- UniqueConstraint('tenant_id','email') em User + Lead
- Zero raw `fetch()` no frontend — tudo via apiFetch
- 31+ endpoints, 7 routers, 10 páginas, 11 migrations

## Testes
- **Comando**: `make test` (roda `pytest -v` dentro do container api)
- **Fixtures**: `conftest.py` com SQLite in-memory, seed_admin, seed_technician, admin_headers, tech_headers
- **Módulos**: test_health, test_auth, test_leads, test_products, test_technicians, test_orders, test_users

## Estado
Ver `STATE.md` para detalhes completos.

## This is NOT the Next.js you know
This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
