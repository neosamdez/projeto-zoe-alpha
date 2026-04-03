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

from app.schemas import ServiceOrderCreate, ServiceOrderResponse, ServiceOrderStatusUpdate, OrdersStats
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
    "/stats",
    response_model=OrdersStats,
    summary="Estatísticas de OS por Tenant",
    description="Sprint 12: O Olho de Hórus. Retorna contagens agregadas das OS do tenant autenticado."
)
def get_orders_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """
    Agrega as contagens de OS por status para o dashboard.
    Isolamento multi-tenant garantido: filtra estritamente por tenant_id do JWT.
    Registros com soft-delete (deleted_at IS NOT NULL) são excluídos da contagem.
    """
    from app.models import ServiceOrder, ServiceStatus
    from sqlalchemy import func

    # Base query: apenas OS do tenant, sem soft-deleted
    base = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.tenant_id == current_user.tenant_id,
            ServiceOrder.deleted_at.is_(None),
        )
    )

    total = base.count()
    open_count = base.filter(ServiceOrder.status == ServiceStatus.OPEN).count()
    repairing_count = base.filter(ServiceOrder.status == ServiceStatus.IN_REPAIR).count()
    completed_count = base.filter(ServiceOrder.status == ServiceStatus.COMPLETED).count()

    return OrdersStats(
        total=total,
        open=open_count,
        repairing=repairing_count,
        completed=completed_count,
    )


@router.get(
    "/",
    response_model=List[ServiceOrderResponse],
    summary="Listar Ordens de Serviço",
    description="Retorna OS do tenant autenticado. Suporta paginação, filtro de status e busca global (protocol, device_info, lead.name)."
)
def list_service_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None,  # Sprint 14: O Farol de Busca
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """Lista paginada das OS do tenant. Busca ilike em protocol, device_info e lead.name."""
    service = OrderService(db=db, tenant_id=current_user.tenant_id)
    return service.list_orders(
        skip=skip,
        limit=limit,
        status_filter=status,
        search_query=search,
    )


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
