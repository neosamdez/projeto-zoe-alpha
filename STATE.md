---
projeto: projeto-zoe-alpha
sprint_atual: 27
sprint_status: em_andamento
ultima_atualizacao: 2026-05-27
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

## Sprint 27 — A Fortificação Final ✅

### Missão
Fechar gaps restantes (G7, G13, G16, G6, G9, G15, G8) + adicionar infraestrutura de testes.

### Entregue
- **FASE 1 — G7 (Lead Email Uniqueness)**:
  - `UniqueConstraint('tenant_id', 'email')` no model Lead
  - `lead_service.create_lead()` → 409 em duplicata por tenant
  - Alembic migration `a8f2c3d4e5b6`
- **FASE 2 — G13 (Pagination)**:
  - `<PaginationControls>` componente reutilizável (Anterior/Próximo, page X de Y)
  - Aplicado em 5 páginas: leads, orders, products, technicians, users
  - Client-side pagination com PAGE_SIZE=15, reset page on filter change
- **FASE 3 — G16 (Lead Detail Page)**:
  - Rota `/leads/[id]/page.tsx` com `LeadDetailPage` component
  - Informações do cliente + OS timeline vinculada (filter client-side por lead_id)
  - Row click na leads table → navega para detail page
- **FASE 4 — G15 (apiFetch refactor)**:
  - `register/page.tsx` refatorado de raw `fetch()` para `apiFetch`
  - Removido `API_URL` import, agora usa `apiFetch` com tratamento centralizado de erro
- **FASE 4 — G9 (Row Click Detail Dialogs)**:
  - Products page: row click → detail dialog (SKU, margem, estoque disponível, reservado)
  - Technicians page: row click → detail dialog (especialização, status, cadastro)
  - `stopPropagation()` nos botões de ação para não triggerar o click da row
- **FASE 4 — G6 (CUSTOMER Role Removed)**:
  - `CUSTOMER` removido do `UserRole` enum em models.py, schemas, auth.ts, users-page
  - Stale `roleColors.CUSTOMER` fallback corrigido
- **FASE 4 — G8 (ServiceOrder.technician type fix)**:
  - `technician` type no `types/index.ts` agora inclui `specialization?: string; is_active: boolean`
- **FASE 5 — Test Infrastructure**:
  - `pytest` + `httpx` + `pytest-asyncio` adicionados ao requirements.txt
  - `conftest.py` com SQLite in-memory, fixtures: `client`, `seed_admin`, `seed_technician`, `admin_headers`, `tech_headers`
  - 6 test files: test_health, test_auth, test_leads, test_products, test_technicians, test_orders, test_users
  - Cobertura smoke de 31+ endpoints
  - `make test` adicionado ao Makefile
  - `pytest.ini` configurado

### Métricas
- **Endpoints**: 31+ (auth: 3, leads: 5, orders: 14, products: 6, technicians: 5, users: 3, reports: 1)
- **Routers**: 7 (auth, leads, orders, products, technicians, users, reports)
- **Frontend pages**: 10 (login, register, dashboard, leads, leads/[id], orders, products, technicians, users, reports)
- **RBAC**: Completo — require_admin em todos os endpoints destrutivos
- **Tests**: 6 test modules, 30+ test cases

## Sprint 25 — A Consolidação do Domínio ✅

### Entregue
- FASE 1: G2 (total_value PATCH), G14 (assignTechnician body fix)
- FASE 2: G1 (Lead DELETE), G3 (Order PATCH geral), G4 (Order DELETE)
- FASE 3: G5 parcial (require_admin em DELETE orders/leads)
- FASE 4: G10 (Reports DELIVERED), G11 (NOTE_ADDED), G17 parcial (badge frontend)

## Sprint 24 — O Primeiro Voo Completo ✅

### Entregue
- Backend: `GET /auth/me`, CORS restrito, technician dict completo, indentation fix, seed.py
- Frontend: Next.js 16 + shadcn/ui + recharts — 8 páginas, 11 componentes custom, 14 UI shadcn, API layer tipada
- Infra: docker-compose.yml com frontend dev service, .gitignore

## Arquitetura

### Backend (FastAPI)
- **Models**: User, Lead, Technician, ServiceOrder, OrderEvent, OrderPart, Product
- **Enums**: UserRole (ADMIN/TECHNICIAN), ServiceStatus (7 estados)
- **Endpoints**: 31+ rotas (auth: 3, leads: 5, orders: 14, products: 6, technicians: 5, users: 3, reports: 1)
- **Services**: Auth, Lead, Order, Product, Technician, Report (6 camadas)
- **Dependencies**: get_current_user, require_admin, require_admin_or_technician, get_tenant_id

### Frontend (Next.js 16)
- **Pages**: 10 (login, register, dashboard, leads, leads/[id], orders, products, technicians, users, reports)
- **Components**: 13 custom + 14 shadcn/ui
- **API Clients**: 31+ funções em 6 módulos
- **Auth**: JWT localStorage + /auth/me refresh + useRequireAuth + RBAC UI gating

### Infra
- **Docker**: 4 containers (db, api, frontend, adminer)
- **DB**: PostgreSQL 16 com 10 migrations Alembic aplicadas
- **Credenciais Seed**: admin@amenti.io / amenti2026
