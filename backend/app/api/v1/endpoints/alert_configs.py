import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_admin, get_db
from app.models import User
from app.services.alert_config_service import AlertConfigService
from app.schemas.alert_config import AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse


router = APIRouter()


def get_alert_config_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertConfigService:
    return AlertConfigService(db=db, tenant_id=current_user.tenant_id)


@router.get("", response_model=List[AlertConfigResponse], summary="Listar Configurações de Alerta")
def list_configs(
    skip: int = 0,
    limit: int = 50,
    service: AlertConfigService = Depends(get_alert_config_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_configs(skip=skip, limit=limit)


@router.get("/{config_id}", response_model=AlertConfigResponse, summary="Detalhar Configuração de Alerta")
def get_config(
    config_id: uuid.UUID,
    service: AlertConfigService = Depends(get_alert_config_service),
    current_user: User = Depends(get_current_user),
):
    config = service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada.")
    return config


@router.post("", response_model=AlertConfigResponse, status_code=status.HTTP_201_CREATED, summary="Criar Configuração de Alerta")
def create_config(
    data: AlertConfigCreate,
    service: AlertConfigService = Depends(get_alert_config_service),
    current_user: User = Depends(require_admin),
):
    return service.create_config(data)


@router.patch("/{config_id}", response_model=AlertConfigResponse, summary="Atualizar Configuração de Alerta")
def update_config(
    config_id: uuid.UUID,
    data: AlertConfigUpdate,
    service: AlertConfigService = Depends(get_alert_config_service),
    current_user: User = Depends(require_admin),
):
    return service.update_config(config_id, data)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover Configuração de Alerta")
def delete_config(
    config_id: uuid.UUID,
    service: AlertConfigService = Depends(get_alert_config_service),
    current_user: User = Depends(require_admin),
):
    service.delete_config(config_id)
