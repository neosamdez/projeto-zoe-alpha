# AGENTS.md — projeto-zoe-alpha (ASI)

## Projeto
Sistema de gestão de assistência técnica (OS) multi-tenant com FastAPI + Next.js.

## Stack Atual
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
- **Frontend**: Next.js 16 + shadcn/ui + recharts + TypeScript
- **Banco**: PostgreSQL 16 (Docker dev)
- **Cache**: Redis 7 (Docker, graceful fallback)
- **Auth**: Custom JWT (PyJWT)
- **Infra**: Docker Compose (5 containers: db, api, redis, frontend, adminer)

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
- Protocolo sequencial `ASI-YY-XXXX` para ServiceOrders, `RMA-YY-XXXX` para RMAs
- NUNCA alterar `models.py` sem Alembic migration imediata
- Service layer ISOLADA dos routers — controllers são thin
- Services usam `__init__(self, db, tenant_id)` pattern (NÃO static methods)
- Soft delete via `deleted_at` (nullable)
- Enums: `UserRole` (ADMIN/TECHNICIAN), `ServiceStatus` (7 estados), `RmaStatus` (6), `DeliveryStatus` (3), `DiscardStatus` (3), `ReturnCode` (10), `InspectionResult` (3), `MovementType` (6)
- Cache: `cache_get` antes de queries pesadas, `cache_set` após, `cache_invalidate` em writes
- `RETURN_CODE_DEADLINES` dict: 805→30, 807→60, 808→7, 809→2, 816→0, 819→7, 821→30, 828→7, 838→60, 839→200

### Frontend (Steve)
- Server Components/Actions → rede Docker (`INTERNAL_API_URL = http://api:8000`)
- Client Components → proxy (`NEXT_PUBLIC_API_URL = http://localhost:8000`)
- 401 → `redirect('/login')`. NUNCA `throw new Error`
- Combobox (não Select) em listas dinâmicas
- API clients tipados com `apiFetch`

### Protocolo de Raciocínio (Reasoning Trace)

Para garantir que cada ação seja fundamentada, todos os agentes devem incluir um bloco de raciocínio em suas respostas críticas:

```markdown
### 🧠 Raciocínio (Reasoning Trace)
- **Problema**: [Breve descrição do desafio]
- **Fundamento**: Baseado em [[Modelo Mental]]
- **Justificativa**: [Por que este modelo/abordagem resolve o problema]
```

## Estado
Ver `STATE.md` para detalhes completos.


## This is NOT the Next.js you know
This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
