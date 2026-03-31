from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.lead import LeadCreate, LeadOut
from app.api.dependencies import get_db, get_tenant_id
from app.services.lead_service import LeadService

router = APIRouter()

@router.post("/", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    *,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    lead_in: LeadCreate
) -> Any:
    """
    Cadastra um novo Lead.
    """
    lead_service = LeadService(db=db, tenant_id=tenant_id)
    return lead_service.create_lead(lead_in=lead_in)
