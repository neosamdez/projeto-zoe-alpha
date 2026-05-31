import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models import User
from app.services.discard_service import DiscardService
from app.schemas.discard import DiscardRecordCreate, DiscardRecordResponse, DiscardAuthorizeUpdate

router = APIRouter()


@router.get("/", response_model=List[DiscardRecordResponse], summary="Listar Descartes")
def list_discards(
    status_filter: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DiscardService(db=db, tenant_id=current_user.tenant_id)
    return service.list_discards(status=status_filter, month=month, year=year, skip=skip, limit=limit)


@router.post("/", response_model=DiscardRecordResponse, status_code=status.HTTP_201_CREATED, summary="Criar Descarte")
def create_discard(
    data: DiscardRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DiscardService(db=db, tenant_id=current_user.tenant_id)
    return service.create_discard(data=data)


@router.get("/report", summary="Relatório de Descartes por Tipo")
def get_discard_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DiscardService(db=db, tenant_id=current_user.tenant_id)
    return service.get_report()


@router.patch("/{discard_id}/authorize", response_model=DiscardRecordResponse, summary="Autorizar Descarte (ADMIN)")
def authorize_discard(
    discard_id: uuid.UUID,
    data: DiscardAuthorizeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = DiscardService(db=db, tenant_id=current_user.tenant_id)
    return service.authorize_discard(discard_id=discard_id, user_id=current_user.id, data=data)


@router.patch("/{discard_id}/complete", response_model=DiscardRecordResponse, summary="Completar Descarte")
def complete_discard(
    discard_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DiscardService(db=db, tenant_id=current_user.tenant_id)
    return service.complete_discard(discard_id=discard_id)
