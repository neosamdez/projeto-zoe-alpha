import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import LeadCreate, LeadResponse
from app.database import get_db
from app.api.dependencies import get_tenant_id
from app.services.lead_service import LeadService

router = APIRouter()

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """
    Controlador Agnóstico. Exige Lead Schema validado, 
    recupera dados contextuais e passa a bola para o LeadService.
    """
    service = LeadService(db=db, tenant_id=tenant_id)
    created_lead = service.create_lead(lead_in=lead_in)
    
    return LeadResponse(
        id=created_lead.id,
        message="Lead Registrado com Sucesso.",
        created_at=created_lead.created_at
    )
