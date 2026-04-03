# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  MAKEFILE DA CIDADELA ASI                                               ║
# ║  Sprint 13: A Convergência Absoluta                                     ║
# ║  Um único comando para governar toda a infraestrutura.                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

.PHONY: up down restart restart-api restart-frontend logs logs-api logs-frontend \
        db-shell alembic-upgrade alembic-revision ps

# ── ORQUESTRAÇÃO PRINCIPAL ────────────────────────────────────────────────────

## Inicia toda a Cidadela: banco, API e frontend em modo desenvolvimento
up:
	docker compose up -d --build

## Derruba todos os containers (preserva volumes de dados)
down:
	docker compose down

## Derruba containers E remove volumes (reset total do banco de dados)
down-v:
	docker compose down -v

## Status de todos os serviços ativos
ps:
	docker compose ps

# ── RESTART CIRÚRGICO ─────────────────────────────────────────────────────────

## Reinicia todos os serviços
restart:
	docker compose restart

## Reinicia apenas a API (FastAPI)
restart-api:
	docker compose restart api

## Reinicia apenas o Frontend (Next.js)
restart-frontend:
	docker compose restart frontend

# ── LOGS EM TEMPO REAL ────────────────────────────────────────────────────────

## Logs de todos os serviços
logs:
	docker compose logs -f

## Logs apenas da API
logs-api:
	docker compose logs -f api

## Logs apenas do Frontend
logs-frontend:
	docker compose logs -f frontend

# ── BANCO DE DADOS ────────────────────────────────────────────────────────────

## Acessa o shell PostgreSQL interno
db-shell:
	docker compose exec db psql -U postgres -d asi_db

## Executa todas as migrations pendentes do Alembic
alembic-upgrade:
	docker compose exec api alembic upgrade head

## Gera nova migration (uso: make alembic-revision m="descricao_da_migration")
alembic-revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"
