---
tags: [sprint, planejamento, projeto-zoe-alpha, amentidigital]
sprint: 25
projeto: projeto-zoe-alpha
titulo: A Consolidação do Domínio
status: planejado
data_criacao: 2026-05-24
responsavel: gojo
sprint_anterior: 24
---

# Sprint 25 — A Consolidação do Domínio

> *"O Primeiro Voo mostrou que as asas funcionam. Agora precisamos blindar o motor antes de ganhar altitude."*

## Contexto

O Sprint 24 ("O Primeiro Voo Completo") entregou o ciclo operacional básico: login → dashboard → CRUD → OS → relatórios. Todos os 21 endpoints estão funcionais, 4 containers UP, frontend completo commitado e pushed.

Porém, a análise de gaps revelou **18 falhas** que vão desde bugs críticos de integridade de dados até features incompletas. Este sprint é dedicado a consolidar o que existe antes de expandir.

---

## Gap Analysis — 18 Gaps Identificados

### CRÍTICO (Integridade de Dados)

| ID | Gap | Descrição | Impacto |
|----|-----|-----------|---------|
| **G2** | `total_value` nunca é atualizado | Não existe endpoint para definir o valor do serviço. Toda receita mostra R$ 0,00 para OS criadas manualmente. Dashboard e relatórios mentem. | Dashboard, stats e reports mostram receita R$ 0,00 |
| **G14** | `assignTechnician` body/param mismatch | Frontend envia `technician_id` no JSON body, mas backend lê como query parameter. Atribuição de técnico silenciosamente falha ou remove o técnico. | Atribuição de técnico quebrada na UI |

### ALTO (Features Core Faltantes)

| ID | Gap | Descrição | Impacto |
|----|-----|-----------|---------|
| **G1** | Lead DELETE ausente | Sem endpoint e sem botão de exclusão de leads. Leads incorretos persistem para sempre. | Frontend + Backend |
| **G3** | ServiceOrder PATCH geral ausente | Não é possível editar `device_info`, `technical_notes` ou `total_value` após criação. Typos são permanentes. | Frontend + Backend |
| **G5** | `require_admin` existe mas não é usado | Qualquer usuário autenticado (TECHNICIAN, CUSTOMER) tem acesso total a todos os endpoints. Zero RBAC. | Segurança |
| **G10** | Reports exclui status DELIVERED | `ReportService` filtra apenas COMPLETED. Dashboard inclui COMPLETED+DELIVERED. Números divergem. | Inconsistência financeira |
| **G18** | Sem User Management UI | Nenhum endpoint de listagem/edição de usuários, nenhuma página de gestão de equipe. ADMIN não pode gerenciar acessos. | Governança |

### MÉDIO (Gaps Funcionais)

| ID | Gap | Descrição |
|----|-----|-----------|
| **G4** | ServiceOrder DELETE ausente | Sem soft-delete para OS |
| **G7** | Lead email não-único por tenant | Duplicatas de CRM possíveis |
| **G11** | `NOTE_ADDED` evento sem suporte | Frontend pronto, backend não gera |
| **G12** | Protocol race condition | Criação concorrente pode causar IntegrityError 500 |
| **G13** | Sem paginação no frontend | Listas truncam em 100 itens silenciosamente |
| **G16** | Sem página de detalhe do Lead | Backend retorna histórico, frontend não consome |
| **G17** | Sem alerta de estoque baixo | `min_stock` existe mas sem indicador visual |

### BAIXO (Polish / Backlog)

| ID | Gap | Descrição |
|----|-----|-----------|
| **G6** | CUSTOMER role não utilizado | Enum morto, feature futura |
| **G8** | Technician type mismatch no frontend | Frontend ignora specialization, is_active |
| **G9** | Funções API client não usadas | `getProduct()`, `getTechnician()` sem UI |
| **G15** | Register page usa fetch() cru | Inconsistente com apiFetch |

---

## Fases do Sprint 25

### FASE 1 — Blindagem Crítica (G2 + G14)

> Prioridade máxima. Dados mentem e feature principal quebra silenciosamente.

**G2: total_value — O Preço do Serviço**
- **Backend**:
  - Criar `PATCH /orders/{order_id}/value` — atualiza `total_value` com validação (>= 0)
  - Schema: `OrderValueUpdate(total_value: Decimal)`
  - Recalcular `parts_cost` + `net_profit` na atualização
  - Adicionar evento `VALUE_UPDATED` no timeline
- **Frontend**:
  - No modal de OS (tab Geral), adicionar campo editável "Valor do Serviço" com botão "Atualizar"
  - Chamar `PATCH /orders/{order_id}/value`
  - Atualizar stats do dashboard em tempo real

**G14: assignTechnician — O Parâmetro Perdido**
- **Backend**:
  - Corrigir `PATCH /orders/{order_id}/assign` para ler `technician_id` do JSON body (não query param)
  - Schema: `OrderAssignTechnician(technician_id: Optional[UUID])`
  - Aceitar `null` para remoção de técnico
- **Frontend**:
  - Verificar que `orders.ts` envia `{ technician_id: "uuid" }` no body (já faz isso)
  - Testar atribuição e remoção no modal de OS

### FASE 2 — CRUD Completo (G1 + G3 + G4)

> Toda entidade principal deve ter CRUD completo.

**G1: Lead DELETE**
- **Backend**:
  - `DELETE /leads/{lead_id}` — soft delete (set `deleted_at`)
  - Regra: não permitir exclusão se lead tem OS (retornar 400)
- **Frontend**:
  - Adicionar botão "Excluir" na listagem de leads
  - Dialog de confirmação
  - `leads.ts`: adicionar `deleteLead(leadId)`

**G3: ServiceOrder PATCH Geral**
- **Backend**:
  - `PATCH /orders/{order_id}` — atualiza `device_info`, `technical_notes`, `total_value`
  - Schema: `ServiceOrderUpdate(device_info?, technical_notes?, total_value?)`
  - Adicionar evento `ORDER_UPDATED` no timeline
- **Frontend**:
  - No modal de OS (tab Geral), tornar campos editáveis com modo "edição"
  - Botão "Salvar" para submeter alterações

**G4: ServiceOrder DELETE**
- **Backend**:
  - `DELETE /orders/{order_id}` — soft delete (set `deleted_at`)
  - Regra: apenas ADMIN pode deletar OS
- **Frontend**:
  - Adicionar botão "Excluir OS" no modal (apenas para ADMIN)
  - Dialog de confirmação com aviso de irreversibilidade

### FASE 3 — Governança (G5 + G18)

> Quem pode fazer o quê.

**G5: RBAC — O Escudo de Permissões**
- **Backend**:
  - Aplicar `require_admin` nos endpoints destrutivos: DELETE leads, DELETE orders, criar/editar technicians, criar/editar products, user management
  - `TECHNICIAN` pode: ver OS, atualizar status, adicionar notas, ver leads/products/technicians
  - `CUSTOMER` pode: ver suas OS (futuro — por agora, bloquear tudo exceto auth/me)
  - Criar `require_admin_or_technician` para endpoints de operação
- **Frontend**:
  - Auth context expõe `role` do usuário
  - Ocultar botões destrutivos para não-ADMINs
  - Sidebar: ocultar links de gestão (Products, Technicians, Users) para TECHNICIAN

**G18: User Management**
- **Backend**:
  - `GET /users/` — lista usuários do tenant (ADMIN only)
  - `PATCH /users/{user_id}` — atualiza role, is_active (ADMIN only)
  - `DELETE /users/{user_id}` — soft delete (ADMIN only, não pode deletar a si mesmo)
- **Frontend**:
  - Nova página `/users` com tabela de usuários
  - Dialog de edição (role selector, is_active toggle)
  - `users.ts` — API client para CRUD de usuários
  - Tipos: `User`, `UserUpdate`

### FASE 4 — Consistência (G10 + G11 + G17)

> Fechar arestas que causam confusão ou perda de dados.

**G10: Reports com DELIVERED**
- **Backend**:
  - `ReportService.get_monthly_data()`: filtrar por `ServiceStatus.in_([COMPLETED, DELIVERED])`
  - Consistente com `OrderService.get_stats()` que já usa `REALIZED_STATUSES`

**G11: NOTE_ADDED — O Diário de Bordo**
- **Backend**:
  - `POST /orders/{order_id}/notes` — cria evento `NOTE_ADDED`
  - Schema: `OrderNoteCreate(content: str)`
- **Frontend**:
  - No modal de OS (tab Timeline), adicionar campo de texto + botão "Adicionar Nota"
  - `orders.ts`: adicionar `addOrderNote(orderId, content)`

**G17: Low Stock Alert**
- **Frontend**:
  - ProductsPage: indicador visual (badge vermelho) quando `current_stock <= min_stock`
  - Card de resumo no topo: "X produtos com estoque baixo"
- **Backend** (opcional):
  - `GET /products/low-stock` — retorna produtos com `current_stock <= min_stock`

---

## Delegação pelo Ciclo da Expansão de Domínio

| Fase | Agente | Domínio | Entregável |
|------|--------|---------|------------|
| FASE 1 | **Heisenberg** (Python) | G14 fix body/param, G2 PATCH /value | Backend blindado |
| FASE 2 | **Heisenberg** (Python) | G1 DELETE leads, G3 PATCH orders, G4 DELETE orders | CRUD completo |
| FASE 3 | **Heisenberg** + **Sheldon** | G5 RBAC backend, G18 User CRUD backend + frontend | Governança |
| FASE 4 | **Heisenberg** + **Steve** | G10 reports fix, G11 notes, G17 low stock | Consistência |
| **QA** | **Elliot** | LSP diagnostics + testes de regressão | Zero errors |
| **Git** | **Loki** | Conventional commits, PR template | Historia limpa |

---

## Critérios de Aceite

1. **G2**: `PATCH /orders/{id}/value` atualiza `total_value` e recalcula lucro no dashboard
2. **G14**: Atribuição de técnico funciona via UI (modal de OS → Combobox → salvar → técnico aparece)
3. **G1**: Lead pode ser excluído (soft delete) via UI, com proteção se tem OS
4. **G3**: OS pode ser editada (device_info, notes, value) via modal
5. **G4**: OS pode ser excluída (soft delete) por ADMIN via UI
6. **G5**: Endpoints destrutivos exigem role ADMIN; TECHNICIAN vê mas não edita gestão
7. **G10**: Relatório mensal inclui OS COMPLETED e DELIVERED (consistente com dashboard)
8. **G11**: Notas podem ser adicionadas ao timeline de OS via UI
9. **G17**: Produtos com estoque baixo têm indicador visual na listagem
10. **G18**: ADMIN pode listar, editar roles e desativar usuários via UI

---

## Estimativa de Esforço

| Fase | Complexidade | Arquivos Backend | Arquivos Frontend |
|------|-------------|------------------|-------------------|
| FASE 1 | Alta (bugs críticos) | 3-4 | 2-3 |
| FASE 2 | Média (CRUD padrão) | 4-5 | 3-4 |
| FASE 3 | Alta (RBAC + nova página) | 5-6 | 5-6 |
| FASE 4 | Baixa-Média (fixes + polish) | 2-3 | 3-4 |
| **TOTAL** | — | **14-18** | **13-17** |

---

## Métricas do Sprint 24 (Linha de Base)

| Métrica | Valor |
|---------|-------|
| Endpoints operacionais | 21 |
| Containers UP | 4/4 |
| Smoke tests passando | 7/7 |
| Frontend pages | 8 |
| Backend models | 7 |
| Gaps identificados | 18 |

## Meta do Sprint 25

| Métrica | Valor Alvo |
|---------|-----------|
| Gaps CRÍTICO resolvidos | 2/2 |
| Gaps ALTO resolvidos | 5/5 |
| Gaps MÉDIO resolvidos | 3/7 |
| Novos endpoints | +6 (value, order PATCH, lead DELETE, order DELETE, users, notes) |
| Novas páginas frontend | +1 (Users) |
| LSP errors | 0 |
