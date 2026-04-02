import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import ServiceOrderCreate, ServiceOrderResponse
from app.database import get_db
from app.api.dependencies import get_tenant_id
from app.services.order_service import OrderService

router = APIRouter()

@router.post("/from-lead/{lead_id}", response_model=ServiceOrderResponse, status_code=status.HTTP_201_CREATED)
def create_service_order_from_lead(
    lead_id: uuid.UUID,
    order_in: ServiceOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """
    Controlador Agnóstico. Exige o ServiceOrderCreate (equipamento) e Lead ID, 
    repasse para OrderService tratar regras e travas de duplicidade.
    """
    service = OrderService(db=db, tenant_id=tenant_id)
    created_order = service.create_order_from_lead(lead_id=lead_id, order_in=order_in)
    
    # O pydantic converte via ServiceOrderResponse.model_validate as propriedades
    return created_order

from typing import List, Optional
from app.schemas import ServiceOrderStatusUpdate

@router.get("/", response_model=List[ServiceOrderResponse])
def list_service_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """
    Lista de Ordens do Tenant logado com Paginação e Filtro de Status.
    """
    service = OrderService(db=db, tenant_id=tenant_id)
    orders = service.list_orders(skip=skip, limit=limit, status_filter=status)
    return orders

@router.get("/{protocol}", response_model=ServiceOrderResponse)
def get_service_order_by_protocol(
    protocol: str,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """
    Busca cirúrgica de uma OS pelo número do protocolo (Ex: ASI-26-0001).
    """
    service = OrderService(db=db, tenant_id=tenant_id)
    order = service.get_order_by_protocol(protocol=protocol)
    return order

@router.patch("/{order_id}/status", response_model=ServiceOrderResponse)
def update_service_order_status(
    order_id: uuid.UUID,
    update_in: ServiceOrderStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """
    Atualiza o Status de uma Ordem de Serviço, com proteção de Tenant.
    """
    service = OrderService(db=db, tenant_id=tenant_id)
    updated_order = service.update_order_status(order_id=order_id, new_status=update_in.status)
    return updated_order

