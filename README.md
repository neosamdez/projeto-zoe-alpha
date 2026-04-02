# Amenti Service Intelligence (ASI)

> A Maestria Inegociável da Gestão Tática e Operacional.

Este repositório encapsula o sistema ASI, estruturado puramente na **Fórmula Amenti** (Design-First, Clean Architecture e Segurança por Design).

## 🏛 Arquitetura Central

A aplicação Backend foi isolada em FastAPI e regida por:
- **BaseModel Amenti**: Injeção compulsória e rígida de `tenant_id` e UUID v4 nativos no PostgreSQL, eliminando colisões.
- **Service Layers Ocultas**: Nenhuma lógica de negócio reside nos Controladores. Controladores são apenas mensageiros; serviços ditam a verdade.
- **Schemas Intransigentes**: Uso massivo do Pydantic V2 para que os objetos transitem pelo pipeline com 100% de confiabilidade e tipagem matemática.

## 🚀 Como Iniciar (A Mão do Rei)

A infraestrutura inteira do reino jaz no `docker-compose.yml` e pode ser regida via `Makefile`.

Para levantar a Cidadela:
```bash
make up
```
Para ver aos bastidores (logs em tempo real):
```bash
make logs
```

Acesse o Swagger e domine a documentação interativa em: `http://localhost:8000/docs`

## 🛡️ Módulo de Ordens de Serviço (Core OS)

A última etapa integrou a essência do ciclo de vida com `Gestão de Fluxo` e `Acesso Universal`:

### 1. Protocolo Sequencial Inquebrável (`ASI-YY-XXXX`)
A lógica de negócio varre a persistência baseada no ano vigente e extrai a ordem natural sem brechas. Diferente do UUID bruto, este formato é amigável a humanos e essencial para telefonemas ou rastreio do consumidor.

### 2. Trava Anti-Duplicidade
O método de criação inspeciona preventivamente o banco. Se o `Lead` já manifesta interesse protegido, o motor aborta com `HTTP 400`, eliminando fraude conceitual e falhas do operador.

### 3. Visibilidade Multi-Tenant (Segregação)
`GET /api/v1/orders/` obriga o porte de `X-Tenant-ID`. Um administrador nunca vislumbrará a frota que não lhe pertence. Isso blinda o ecossistema SaaS.

---
**Elaborado pelas Inteligências da Tríplice Aliança:**
- 📐 **Arquiteto** (Fatoração e Banco)
- ⚙️ **Engenheiro** (Códificação Limpa e Fast API)
- 👁️ **Oráculo** (Documentação, QA e Regras de Segurança)
- 🛡️ **Mão do Rei** (DevOps e Empacotamento Lógico)
