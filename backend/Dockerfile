# 1. Estágio de Build (Builder)
FROM python:3.12-slim AS builder

WORKDIR /app

# Otimizações de ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalação das dependências C/Rust para compilação (ex: psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cria os wheels (pacotes pré-compilados) na pasta /app/wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# 2. Estágio Final (Runtime)
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Libs essenciais de runtime para Postgres Native Driver
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Instala via wheels - Extremamente rápido
RUN pip install --no-cache /wheels/*

# Copia o código da aplicação
COPY . /app

EXPOSE 8000

# Comando Otimizado para Produção (Pode ser sobrescrito pelo compose-dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
