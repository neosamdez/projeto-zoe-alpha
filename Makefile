.PHONY: up down restart logs db-shell alembic-upgrade

# Inicia todos os containers e garante que os volumes e redes foram criados
up:
	docker compose up -d --build

# Desliga os containers
down:
	docker compose down

# Reinicia a API
restart:
	docker compose restart api

# Traz os logs da API en tempo real
logs:
	docker compose logs -f api

# Acessa o shell do banco de dados PostgreSQL interno
db-shell:
	docker compose exec db psql -U postgres -d postgres

# Executa as migrations do Alembic no banco principal
alembic-upgrade:
	docker compose exec api alembic upgrade head

# Executa a geração de nova migração (Ex: make alembic-revision m="nome_da_migracao")
alembic-revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"
