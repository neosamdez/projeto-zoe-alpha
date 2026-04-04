import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user
from app.schemas import TechnicianCreate, TechnicianUpdate, TechnicianResponse
from app.models import User
from app.services.technician_service import TechnicianService

router = APIRouter()

@router.get("/", response_model=List[TechnicianResponse])
def list_technicians(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Inspeção da Guilda: Lista todos os técnicos do Tenant."""
    service = TechnicianService(db, current_user.tenant_id)
    return service.list_technicians(active_only=active_only)

@router.post("/", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
def create_technician(
    tech_in: TechnicianCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Forja de Talentos: Adiciona um novo mestre à equipe."""
    service = TechnicianService(db, current_user.tenant_id)
    return service.create_technician(tech_in)

@router.get("/{tech_id}", response_model=TechnicianResponse)
def get_technician(
    tech_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Visão Tática: Detalhes de um técnico específico."""
    service = TechnicianService(db, current_user.tenant_id)
    return service.get_technician(tech_id)

@router.patch("/{tech_id}", response_model=TechnicianResponse)
def update_technician(
    tech_id: uuid.UUID,
    tech_in: TechnicianUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refino de Mestre: Atualiza dados do técnico."""
    service = TechnicianService(db, current_user.tenant_id)
    return service.update_technician(tech_id, tech_in)

@router.delete("/{tech_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(
    tech_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Expurgo de Cadastro: Remove (Soft Delete) um técnico da guilda."""
    service = TechnicianService(db, current_user.tenant_id)
    service.delete_technician(tech_id)
    return None
