from fastapi import APIRouter
from app.api.v1.endpoints import leads, orders, auth, products, technicians, reports, users, rma, inventory, deliveries, discards, kpi, alert_configs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(products.router, prefix="/products", tags=["Inventário"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["Equipe"])
api_router.include_router(users.router, prefix="/users", tags=["Usuários"])
api_router.include_router(reports.router, prefix="/reports", tags=["Relatórios"])
api_router.include_router(rma.router, prefix="/rma", tags=["RMA"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventário Movimentações"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
api_router.include_router(discards.router, prefix="/discards", tags=["Descarte"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["KPI / P4P"])
api_router.include_router(alert_configs.router, prefix="/alert-configs", tags=["Alertas Config"])
