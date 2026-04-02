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
