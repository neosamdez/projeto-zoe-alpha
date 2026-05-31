import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models import User, RmaStatus
from app.services.rma_service import RmaService
from app.schemas.rma import (
    RmaRequestCreate, RmaRequestResponse, RmaStatusUpdate,
    RmaInspectionCreate, RmaInspectionResponse,
    ReturnedPartCreate, ReturnedPartResponse,
    DefectCodeResponse, RmaRequestDetail,
)

router = APIRouter()


@router.post("/", response_model=RmaRequestResponse, status_code=status.HTTP_201_CREATED, summary="Criar RMA")
def create_rma(
    data: RmaRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.create_rma(user_id=current_user.id, data=data)


@router.get("/", response_model=List[RmaRequestResponse], summary="Listar RMAs")
def list_rmas(
    status_filter: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.list_rmas(status=status_filter, month=month, year=year, skip=skip, limit=limit)


@router.get("/defect-codes", response_model=List[DefectCodeResponse], summary="Listar Códigos de Defeito")
def list_defect_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.list_defect_codes()


@router.get("/{rma_id}", response_model=RmaRequestDetail, summary="Detalhe do RMA")
def get_rma_detail(
    rma_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    detail = service.get_detail(rma_id)
    rma = detail["rma"]
    result = RmaRequestDetail.model_validate(rma)
    result.inspections = [RmaInspectionResponse.model_validate(i) for i in detail["inspections"]]
    result.returned_parts = [ReturnedPartResponse.model_validate(p) for p in detail["returned_parts"]]
    return result


@router.patch("/{rma_id}/status", response_model=RmaRequestResponse, summary="Atualizar Status RMA")
def update_rma_status(
    rma_id: uuid.UUID,
    data: RmaStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.update_status(rma_id=rma_id, new_status=data.status)


@router.post("/{rma_id}/inspections", response_model=RmaInspectionResponse, status_code=status.HTTP_201_CREATED, summary="Adicionar Inspeção")
def add_inspection(
    rma_id: uuid.UUID,
    data: RmaInspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.add_inspection(rma_id=rma_id, inspector_id=current_user.id, data=data)


@router.get("/{rma_id}/inspections", response_model=List[RmaInspectionResponse], summary="Listar Inspeções")
def list_inspections(
    rma_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.list_inspections(rma_id=rma_id)


@router.post("/{rma_id}/returned-parts", response_model=ReturnedPartResponse, status_code=status.HTTP_201_CREATED, summary="Adicionar Peça Devolvida")
def add_returned_part(
    rma_id: uuid.UUID,
    data: ReturnedPartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RmaService(db=db, tenant_id=current_user.tenant_id)
    return service.add_returned_part(rma_id=rma_id, data=data)
