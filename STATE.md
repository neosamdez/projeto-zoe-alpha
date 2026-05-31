---
projeto: projeto-zoe-alpha
sprint_atual: 35
sprint_status: em_andamento
ultima_atualizacao: 2026-05-31
responsavel: gojo
stack:
- FastAPI
- Next.js 16
- PostgreSQL 16
- Redis 7
- Docker
- shadcn/ui
repo: https://github.com/neosamdez/projeto-zoe-alpha
---

# STATE — Projeto Zoe Alpha (ASI)

## Visão Geral

Sistema de gestão de assistência técnica (OS) multi-tenant com FastAPI + Next.js.

## Sprint 35 — Alertas de Estoque via Email (Em andamento)

### Fase 1: Backend (Concluído)
- [x] Criar `EmailService` (usando SMTP ou provider externo).
- [x] Criar `InventoryAlertService` que monitora mudanças de estoque.
- [x] Adicionar trigger de notificação no `InventoryService.update_stock`.
- [x] Implementar lógica de tarefa agendada (`process_alerts_batch`).

### Fase 2: Frontend + Backend CRUD AlertConfig (Concluído)
- [x] Adicionar indicador visual de "estoque baixo" no Dashboard (StockAlert melhorado, dark-mode, link /products).
- [x] Adicionar página de configurações de alerta (quem recebe, quais itens).
- [x] Model AlertConfig + migration Alembic (c4a7b2d3e8f1).
- [x] Schema, Service, Router CRUD para AlertConfig.
- [x] AlertService refatorado para usar AlertConfigService.get_active_recipients() com fallback.
- [x] Frontend: types, API client, página alert-configs, sidebar com Bell icon.
- [x] Fixes: PackageReturn→PackageCheck, avg_oow_hq removido, cast TS em kpi-page.
- [x] conftest.py: mock de env vars com os.environ.setdefault().
- [x] Frontend build passando (18 rotas).

### Fase 3: QA (Pendente)
- [ ] Testar envio de email em ambiente de sandbox.
- [ ] Testar integridade do estoque após disparos de alertas.
- [ ] Validar que alertas não duplicam em re-envios.

## Sprint 34 — Cache, Testes, Filtros e Dashboard (concluído)

### Entregue
- **Redis cache integrado**: OrderService.get_stats/get_analytics, KpiService.get_dashboard, InventoryService.get_dashboard com cache_get/cache_set/cache_invalidate (TTL 120-300s)
- **Cache invalidation**: create_order, update_order_status, create/update KPI metric, create inventory movement
- **5 test modules**: test_rma (4), test_inventory (5), test_deliveries (5), test_discards (5), test_kpi (6) — total 25 novos testes
- **DateFilter component**: `<DateFilter>` reutilizável (mês/ano) adicionado a RMA, Deliveries, Discards pages
- **Backend month/year filters**: routers + services de RMA, Deliveries, Discards com `extract()` SQL month/year
- **Dashboard enriquecido**: resumo RMA pendentes + alerta estoque baixo na página principal
- **KPI bug fix**: `create_or_update_metric` — fixed indentation + `model_dump(exclude_unset=True)` + `hasattr` guard
- **Conftest fix**: `from app.models import Base` (not `from app.database`), `StaticPool` + in-memory SQLite
- **Docker port remap**: Zoe uses 8001/3001/5433 to avoid sougenios conflict
- **Frontend Dockerfile**: `frontend/Dockerfile` criado (node:20-alpine)
- **StatusBadge**: RMA, Deliveries, Discards pages usam `<StatusBadge>` em vez de inline status configs

## Sprint 32-33 — Status Badges + KPI Page

### Entregue
- **StatusBadge unificado**: `status-badge.tsx` suporta ServiceStatus|RmaStatus|DeliveryStatus|DiscardStatus via `ALL_CONFIGS` map
- **KPI Page**: month/year selector, 4 avg KPI cards, RadarChart (recharts), P4P bonus table, technician detail table, create metric dialog (ADMIN)
- **KPI Route**: `app/kpi/page.tsx` com `<AppShell>` wrapper
- **Redis container**: redis:7-alpine no docker-compose (port 6379, healthcheck, persistent volume)
- **Cache module**: `core/cache.py` — get_redis(), cache_get/set/delete/invalidate com graceful fallback
- **Config**: REDIS_URL setting + .env.example

## Sprint 29-31 — Phase 2 Backend + Frontend

### Entregue
- **5 schemas**: rma, inventory, delivery, discard, kpi
- **5 services**: RmaService, InventoryService, DeliveryService, DiscardService, KpiService
- **5 routers** (27 endpoints): rma (8), inventory (4), deliveries (5), discards (5), kpi (5)
- **15 models**: User, Lead, ServiceOrder, OrderEvent, OrderPart, Product, Technician + RmaRequest, RmaInspection, ReturnedPart, DefectCode, InventoryMovement, DeliveryPending, DiscardRecord, KpiMetric
- **8 enums**: UserRole, ServiceStatus, ReturnCode, RmaStatus, InspectionResult, MovementType, DeliveryStatus, DiscardStatus
- **22 defect codes**: SR01-SR22 seeded por tenant
- **Alembic migration**: b3f7a1c2d4e5 (head: cd1826eb6e07)
- **Frontend types**: 32+ TypeScript interfaces
- **5 API clients**: rma.ts, inventory.ts, deliveries.ts, discards.ts, kpi.ts
- **5 page components**: rma-page, inventory-page, deliveries-page, discards-page, kpi-page
- **5 route files**: rma, inventory, deliveries, discards, kpi
- **Sidebar**: 9 nav items + 4 admin-only

## Sprint 28 — Blindagem de Segurança

### Entregue
- C1-C3 (Critical): pg_lock condicional, secrets rotation, stale import
- H1-H6 (High): server-side role, user email scoped, tenant filter OS history, apiFetch raw, auth-context refactor, mass-assignment fix
- 35 apiFetch call sites migrados para nova assinatura

## Métricas Atuais

### Backend
- **Models**: 15 (User, Lead, ServiceOrder, OrderEvent, OrderPart, Product, Technician, RmaRequest, RmaInspection, ReturnedPart, DefectCode, InventoryMovement, DeliveryPending, DiscardRecord, KpiMetric)
- **Enums**: 8 (UserRole, ServiceStatus, ReturnCode, RmaStatus, InspectionResult, MovementType, DeliveryStatus, DiscardStatus)
- **Routers**: 12 (auth, leads, orders, products, technicians, users, reports, rma, inventory, deliveries, discards, kpi)
- **Endpoints**: 65+
- **Services**: 11 (Auth, Lead, Order, Product, Technician, Report, Rma, Inventory, Delivery, Discard, KPI)
- **Migrations**: 12 (até b3f7a1c2d4e5)
- **Tests**: 12 modules (7 originais + 5 novos), 61 test cases (100% pass)

### Frontend
- **Pages**: 15 (login, register, dashboard, leads, leads/[id], orders, products, technicians, users, reports, rma, inventory, deliveries, discards, kpi)
- **Components**: 19 custom (dashboard-page, orders-page, leads-page, products-page, technicians-page, users-page, reports-page, rma-page, inventory-page, deliveries-page, discards-page, kpi-page, sidebar, app-shell, status-badge, pagination-controls, combobox, date-filter, auth-context)
- **API Clients**: 13 modules
- **Auth**: JWT + apiFetch + useAuth + RBAC

### Infra
- **Docker**: 5 containers (db, api, redis, frontend, adminer)
- **Cache**: Redis 7 com graceful degradation
- **Volumes**: postgres_data, redis_data
- **Credenciais Seed**: admin@amenti.io / amenti2026

## Arquitetura

### Multi-Tenant
- `tenant_id` em toda tabela com filtro obrigatório
- JWT → `current_user.tenant_id` (nunca header X-Tenant-ID)
- UniqueConstraint scoped por tenant (email de User e Lead)

### Cache Strategy
- Redis com graceful fallback (app funciona sem Redis)
- TTL: 120s (stats/analytics/inventory), 300s (KPI dashboard)
- Invalidation on write: cache_invalidate(prefix) nos services

### Service Pattern
- `__init__(self, db, tenant_id)` — NÃO static methods
- Cache: cache_get antes da query, cache_set após, cache_invalidate em writes
- Soft delete via `deleted_at` (nullable)

### Frontend Pattern
- `<AppShell>` wrapper em toda página
- `<StatusBadge>` unificado para todos os enums de status
- `<DateFilter>` reutilizável para filtros mês/ano
- API clients tipados com `apiFetch`
