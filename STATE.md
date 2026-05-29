---
projeto: projeto-zoe-alpha
sprint_atual: 28
sprint_status: em_andamento
ultima_atualizacao: 2026-05-28
responsavel: gojo
stack:
- FastAPI
- Next.js 16
- PostgreSQL 16
- Docker
- shadcn/ui
repo: https://github.com/neosamdez/projeto-zoe-alpha
---

# STATE — Projeto Zoe Alpha (ASI)

## Visão Geral

Sistema de gestão de assistência técnica (OS) multi-tenant com FastAPI + Next.js.

## Sprint 28 — Blindagem de Segurança (Critical + High)

### Missão
Resolver findings C1-C3 (Critical) + H1-H6 (High) da auditoria de segurança.

### Entregue
- **FASE 0 — Git Cleanup**: Sprint 26 e 27 committed separadamente
- **C1 — pg_advisory_xact_lock condicional**: `self.db.bind.dialect.name == "postgresql"` — skip lock em SQLite/test
- **C2 — Secrets rotation**: `.env` já estava no `.gitignore`; `SECRET_KEY` e `POSTGRES_PASSWORD` rotacionados; `node_modules/` adicionado ao `.gitignore`
- **C3 — Stale import removido**: `get_tenant_id` import morto removido de `auth.py`; docstring `/auth/register` corrigido
- **H1 — Server-side role assignment**: `role` removido de `UserCreate`; `register_user()` sempre cria TECHNICIAN; só `UserUpdateByAdmin` pode setar role
- **H2 — User email uniqueness scoped**: `UniqueConstraint('tenant_id', 'email')` no User model; `unique=True` removido do email column; Alembic migration `cd1826eb6e07`; `register_user()` duplicity check scoped por tenant
- **H3 — Tenant filter on OS history**: `ServiceOrder.tenant_id == self.tenant_id` adicionado na query de OS history em `lead_service.get_lead_by_id()`
- **H4 — apiFetch raw option**: `ApiFetchOptions` com `{ raw: true }` para blob/Response; `reports.ts` refatorado para usar `apiFetch` com `raw: true` ao invés de raw `fetch()`
- **H5 — auth-context apiFetch**: `loadUser()` e `login()` refatorados para usar `apiFetch`; removido `NEXT_PUBLIC_API_URL` hardcoded
- **H6 — Mass-assignment fix**: `product_service.create_product()` e `technician_service.create_technician()` agora usam `model_dump(exclude_unset=True)`
- **apiFetch signature migration**: 35 call sites migrados de `apiFetch(path, opts, isServer)` para `apiFetch(path, { ...opts, isServer })`
- **Test update**: `test_register_duplicate_email` → `test_register_creates_new_tenant` (register público cria novo tenant, email duplicado cross-tenant é permitido)

### Métricas
- **Endpoints**: 31+ (auth: 3, leads: 5, orders: 14, products: 6, technicians: 5, users: 3, reports: 1)
- **Routers**: 7 (auth, leads, orders, products, technicians, users, reports)
- **Frontend pages**: 10 (login, register, dashboard, leads, leads/[id], orders, products, technicians, users, reports)
- **RBAC**: Completo — require_admin em todos os endpoints destrutivos
- **Tests**: 6 test modules, 30+ test cases
- **Migrations**: 11 (até `cd1826eb6e07`)

## Sprint 27 — A Fortificação Final ✅

### Entregue
- G7: Lead email uniqueness por tenant
- G13: PaginationControls em 5 páginas
- G16: Lead detail page `/leads/[id]`
- G15/G9/G6/G8: apiFetch refactor, row click dialogs, CUSTOMER removed, type fix
- FASE 5: pytest + httpx + 6 test modules + make test

## Sprint 26 — RBAC + User Management ✅

### Entregue
- G5: require_admin em POST/PATCH/DELETE products e technicians
- G18: GET/PATCH/DELETE /users/ com require_admin
- G12: pg_advisory_xact_lock em generate_protocol()
- G17: GET /products/low-stock

## Arquitetura

### Backend (FastAPI)
- **Models**: User, Lead, Technician, ServiceOrder, OrderEvent, OrderPart, Product
- **Enums**: UserRole (ADMIN/TECHNICIAN), ServiceStatus (7 estados)
- **Endpoints**: 31+ rotas (auth: 3, leads: 5, orders: 14, products: 6, technicians: 5, users: 3, reports: 1)
- **Services**: Auth, Lead, Order, Product, Technician, Report (6 camadas)
- **Dependencies**: get_current_user, require_admin, require_admin_or_technician, get_tenant_id
- **Constraints**: uq_lead_tenant_email, uq_user_tenant_email (scoped por tenant)

### Frontend (Next.js 16)
- **Pages**: 10 (login, register, dashboard, leads, leads/[id], orders, products, technicians, users, reports)
- **Components**: 13 custom + 14 shadcn/ui
- **API Clients**: 31+ funções em 6 módulos — todas via `apiFetch` (zero raw fetch)
- **Auth**: JWT localStorage + apiFetch + /auth/me refresh + useRequireAuth + RBAC UI gating

### Infra
- **Docker**: 4 containers (db, api, frontend, adminer)
- **DB**: PostgreSQL 16 com 11 migrations Alembic aplicadas
- **Credenciais Seed**: admin@amenti.io / amenti2026 (rotacionados)
