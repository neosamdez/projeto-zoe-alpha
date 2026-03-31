import uuid
from sqlalchemy.orm import Session
from app.models import Lead
from app.schemas import LeadCreate

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
