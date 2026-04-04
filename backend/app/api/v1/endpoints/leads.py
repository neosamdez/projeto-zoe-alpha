from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.schemas import LeadCreate, LeadResponse, LeadUpdate, LeadListItem, LeadDetails
from app.database import get_db
from app.api.dependencies import get_current_user
from app.services.lead_service import LeadService
from app.models import User

router = APIRouter()


@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo Lead",
    description="Requer Bearer Token. O tenant_id é inferido do token JWT automaticamente."
)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LeadService(db=db, tenant_id=current_user.tenant_id)
    created_lead = service.create_lead(lead_in=lead_in)

    return LeadResponse(
        id=created_lead.id,
        message="Lead Registrado com Sucesso.",
        created_at=created_lead.created_at
    )


@router.get(
    "/",
    response_model=List[LeadListItem],
    summary="Listar Clientes (CRM)",
    description="Retorna a base de clientes do tenant com contagem de OS."
)
def list_leads(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LeadService(db=db, tenant_id=current_user.tenant_id)
    return service.list_leads(search=q, skip=skip, limit=limit)


@router.get(
    "/{lead_id}",
    response_model=LeadDetails,
    summary="Obter Detalhes do Cliente",
    description="Retorna dados do lead e seu histórico completo de Ordens de Serviço."
)
def get_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LeadService(db=db, tenant_id=current_user.tenant_id)
    lead = service.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado na base tática."
        )
    return lead


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Atualizar Dados do Cliente",
    description="Permite atualizar nome, e-mail ou telefone do lead."
)
def update_lead(
    lead_id: uuid.UUID,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LeadService(db=db, tenant_id=current_user.tenant_id)
    updated = service.update_lead(lead_id, lead_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado para atualização."
        )
    
    return LeadResponse(
        id=updated.id,
        message="Dados do Cliente Atualizados.",
        created_at=updated.created_at
    )
