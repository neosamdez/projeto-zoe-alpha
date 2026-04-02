from fastapi import APIRouter
from app.api.v1.endpoints import leads, orders

api_router = APIRouter()
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])

