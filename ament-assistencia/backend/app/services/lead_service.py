from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Lead
from app.schemas.lead import LeadCreate

class LeadService:
    """Service layer para isolar a regra de negócio da tabela de Leads."""
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    def create_lead(self, lead_in: LeadCreate) -> Lead:
        """Cria um Lead no banco de dados isolando-o pelo tenant."""
        lead_data = lead_in.model_dump()
        db_lead = Lead(**lead_data, tenant_id=self.tenant_id)
        
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        
        return db_lead
