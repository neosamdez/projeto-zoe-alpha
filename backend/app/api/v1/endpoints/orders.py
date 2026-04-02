"""
[ENDPOINT: ORDERS — BLINDADO COM JWT]
Sprint 9: Lockdown Total.
O tenant_id não vem mais do Header X-Tenant-ID.
Ele é extraído estritamente do token JWT do usuário autenticado.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import ServiceOrderCreate, ServiceOrderResponse, ServiceOrderStatusUpdate
from app.database import get_db
from app.api.dependencies import get_current_user
from app.services.order_service import OrderService
from app.models import User

router = APIRouter()


@router.post(
    "/from-lead/{lead_id}",
    response_model=ServiceOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar OS a partir de Lead",
    description="Requer Bearer Token. tenant_id inferido do JWT."
)
def create_service_order_from_lead(
    lead_id: uuid.UUID,
    order_in: ServiceOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """
    Cria uma OS vinculada ao Lead informado.
    O tenant_id é lido de current_user.tenant_id — imutável e protegido.
    """
    service = OrderService(db=db, tenant_id=current_user.tenant_id)
    return service.create_order_from_lead(lead_id=lead_id, order_in=order_in)


@router.get(
    "/",
    response_model=List[ServiceOrderResponse],
    summary="Listar Ordens de Serviço",
    description="Retorna todas as OS do tenant autenticado. Suporta paginação e filtro de status."
)
def list_service_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """Lista paginada das OS do tenant extraído do JWT."""
    service = OrderService(db=db, tenant_id=current_user.tenant_id)
    return service.list_orders(skip=skip, limit=limit, status_filter=status)


@router.get(
    "/{protocol}",
    response_model=ServiceOrderResponse,
    summary="Buscar OS por Protocolo",
    description="Busca cirúrgica por protocolo ASI (ex: ASI-26-0001)."
)
def get_service_order_by_protocol(
    protocol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """Busca uma OS pelo protocolo. Isolamento por tenant garantido."""
    service = OrderService(db=db, tenant_id=current_user.tenant_id)
    return service.get_order_by_protocol(protocol=protocol)


@router.patch(
    "/{order_id}/status",
    response_model=ServiceOrderResponse,
    summary="Atualizar Status da OS",
    description="Atualiza o status de uma OS. Apenas o tenant dono pode operar."
)
def update_service_order_status(
    order_id: uuid.UUID,
    update_in: ServiceOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """Atualiza o status da OS com proteção dupla: JWT + tenant_id do token."""
    service = OrderService(db=db, tenant_id=current_user.tenant_id)
    return service.update_order_status(order_id=order_id, new_status=update_in.status)
