"""
[ENDPOINT: LEADS — BLINDADO COM JWT]
Sprint 9: Lockdown Total.
O tenant_id não vem mais do Header X-Tenant-ID.
Ele é extraído estritamente do token JWT do usuário autenticado.
Ninguém forja um tenant que não lhe pertence.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import LeadCreate, LeadResponse
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
    current_user: User = Depends(get_current_user),  # 🔒 JWT required
):
    """
    Controlador blindado. O tenant_id é extraído do JWT autenticado —
    nunca do corpo da requisição ou de um header manipulável.
    """
    service = LeadService(db=db, tenant_id=current_user.tenant_id)
    created_lead = service.create_lead(lead_in=lead_in)

    return LeadResponse(
        id=created_lead.id,
        message="Lead Registrado com Sucesso.",
        created_at=created_lead.created_at
    )
