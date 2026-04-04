import uuid
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Lead, ServiceOrder
from app.schemas import LeadCreate, LeadUpdate, LeadListItem, LeadDetails

class LeadService:
    """
    Camada Exclusiva de Processamento de Negócio para entidade Lead.
    """
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def create_lead(self, lead_in: LeadCreate) -> Lead:
        """Processo Estrito de Cadastramento e Vinculação ao Tenant."""
        db_lead = Lead(
            tenant_id=self.tenant_id,
            name=lead_in.name,
            email=lead_in.email,
            phone=lead_in.phone,
            device_interest=lead_in.device_interest,
            notes=lead_in.notes
        )
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def list_leads(self, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[LeadListItem]:
        """
        Listagem Tática de CRM.
        JOIN com ServiceOrder para retornar contagem de OS por Lead.
        """
        query = self.db.query(
            Lead.id,
            Lead.name,
            Lead.email,
            Lead.phone,
            Lead.created_at,
            func.count(ServiceOrder.id).label("total_os")
        ).outerjoin(ServiceOrder, Lead.id == ServiceOrder.lead_id)\
         .filter(Lead.tenant_id == self.tenant_id, Lead.deleted_at == None)\
         .group_by(Lead.id)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Lead.name.ilike(search_filter)) | (Lead.phone.ilike(search_filter))
            )

        results = query.offset(skip).limit(limit).all()
        
        return [
            LeadListItem(
                id=r.id,
                name=r.name,
                email=r.email,
                phone=r.phone,
                created_at=r.created_at,
                total_os=r.total_os
            ) for r in results
        ]

    def get_lead_by_id(self, lead_id: uuid.UUID) -> Optional[LeadDetails]:
        """Busca detalhada incluindo histórico de Ordens de Serviço."""
        lead = self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.tenant_id == self.tenant_id,
            Lead.deleted_at == None
        ).first()

        if not lead:
            return None

        # Busca histórico de OS
        os_history = self.db.query(ServiceOrder).filter(
            ServiceOrder.lead_id == lead_id,
            ServiceOrder.deleted_at == None
        ).order_by(ServiceOrder.created_at.desc()).all()

        # Contagem total de OS
        total_os = len(os_history)

        return LeadDetails(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            created_at=lead.created_at,
            total_os=total_os,
            os_history=os_history
        )

    def update_lead(self, lead_id: uuid.UUID, lead_in: LeadUpdate) -> Optional[Lead]:
        """Atualização parcial dos dados do cliente."""
        db_lead = self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.tenant_id == self.tenant_id,
            Lead.deleted_at == None
        ).first()

        if not db_lead:
            return None

        update_data = lead_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lead, key, value)

        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead
