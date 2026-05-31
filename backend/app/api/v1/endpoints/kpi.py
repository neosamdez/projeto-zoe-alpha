import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models import User
from app.services.kpi_service import KpiService
from app.schemas.kpi import KpiMetricCreate, KpiMetricResponse, KpiDashboard, KpiBonusSummary

router = APIRouter()


@router.post("/", response_model=KpiMetricResponse, status_code=status.HTTP_201_CREATED, summary="Criar/Atualizar Métrica KPI")
def create_or_update_metric(
    data: KpiMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = KpiService(db=db, tenant_id=current_user.tenant_id)
    return service.create_or_update_metric(data=data)


@router.get("/", response_model=List[KpiMetricResponse], summary="Listar Métricas KPI")
def list_metrics(
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = KpiService(db=db, tenant_id=current_user.tenant_id)
    return service.list_metrics(month=month, year=year, skip=skip, limit=limit)


@router.get("/dashboard", response_model=KpiDashboard, summary="Dashboard KPI")
def get_kpi_dashboard(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = KpiService(db=db, tenant_id=current_user.tenant_id)
    return service.get_dashboard(month=month, year=year)


@router.get("/bonus-summary", response_model=List[KpiBonusSummary], summary="Resumo de Bonificação P4P")
def get_bonus_summary(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = KpiService(db=db, tenant_id=current_user.tenant_id)
    return service.get_bonus_summary(month=month, year=year)


@router.get("/{metric_id}", response_model=KpiMetricResponse, summary="Detalhe da Métrica KPI")
def get_metric(
    metric_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = KpiService(db=db, tenant_id=current_user.tenant_id)
    return service.get_metric(metric_id=metric_id)
