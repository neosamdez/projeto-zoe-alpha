import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models import User
from app.services.delivery_service import DeliveryService
from app.schemas.delivery import DeliveryPendingCreate, DeliveryPendingResponse, DeliveryReceiveUpdate

router = APIRouter()


@router.get("/", response_model=List[DeliveryPendingResponse], summary="Listar Deliveries")
def list_deliveries(
    status_filter: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db=db, tenant_id=current_user.tenant_id)
    return service.list_deliveries(status=status_filter, month=month, year=year, skip=skip, limit=limit)


@router.post("/", response_model=DeliveryPendingResponse, status_code=status.HTTP_201_CREATED, summary="Criar Delivery")
def create_delivery(
    data: DeliveryPendingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db=db, tenant_id=current_user.tenant_id)
    return service.create_delivery(data=data)


@router.get("/overdue", response_model=List[DeliveryPendingResponse], summary="Deliveries Atrasados")
def list_overdue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db=db, tenant_id=current_user.tenant_id)
    return service.list_overdue()


@router.post("/mark-overdue", summary="Marcar Deliveries Atrasados")
def mark_overdue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = DeliveryService(db=db, tenant_id=current_user.tenant_id)
    count = service.mark_overdue()
    return {"message": f"{count} deliveries marcados como atrasados."}


@router.patch("/{delivery_id}/receive", response_model=DeliveryPendingResponse, summary="Receber Delivery")
def receive_delivery(
    delivery_id: uuid.UUID,
    data: DeliveryReceiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db=db, tenant_id=current_user.tenant_id)
    return service.receive_delivery(delivery_id=delivery_id, data=data)
