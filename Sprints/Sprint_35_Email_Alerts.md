---
tags: [sprint, planejamento, projeto-zoe-alpha]
sprint: 35
projeto: projeto-zoe-alpha
titulo: Implementação de Alertas de Estoque via Email
status: planejado
data_criacao: 2026-05-30
responsavel: gojo
---

# Sprint 35 — Alertas de Estoque via Email

## Contexto
O sistema precisa notificar administradores quando itens atingirem o nível crítico de estoque para evitar rupturas.

## Missão
Implementar um serviço de notificação de email assíncrono integrado ao sistema de inventário.

## Fases

### Fase 1: Backend (Heisenberg)
- Criar `EmailService` (usando SMTP ou provider externo).
- Criar `InventoryAlertService` que monitora mudanças de estoque.
- Adicionar trigger de notificação no `InventoryService.update_stock`.
- Implementar tarefa agendada (cron/celery) para checagem de níveis críticos.

### Fase 2: Frontend (Steve)
- Adicionar indicador visual de "estoque baixo" no Dashboard.
- Adicionar página de configurações de alerta (quem recebe, quais itens).

### Fase 3: QA (Elliot)
- Testar envio de email em ambiente de sandbox.
- Testar integridade do estoque após disparos de alertas.
- Validar que alertas não duplicam em re-envios.

## Delegação
| Fase | Agente | Domínio | Entregável |
|------|--------|---------|------------|
| 1 | Heisenberg | Backend | Email & Alert Services |
| 2 | Steve | Frontend | Dashboard Alerts UI |
| 3 | Elliot | QA | QA Report (ALL_CLEAR) |

## Critérios de Aceite
1. Email é enviado quando um item cai abaixo do `min_stock`.
2. O envio não bloqueia a transação de atualização de estoque (assíncrono).
3. O dashboard mostra um alerta visual para itens em nível crítico.
4. Não há vazamento de memória ou threads presas no processo de envio.
