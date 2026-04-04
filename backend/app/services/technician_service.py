import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Technician
from app.schemas import TechnicianCreate, TechnicianUpdate

class TechnicianService:
    """
    [PROTOCOLO AMENTI: TECHNICIAN SERVICE]
    Camada de inteligência para Gestão de Equipe.
    Garante o isolamento de talentos por Cidadela (Tenant).
    """
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def list_technicians(self, active_only: bool = False) -> list[Technician]:
        """Recupera a guilda de técnicos do Tenant."""
        query = self.db.query(Technician).filter(
            Technician.tenant_id == self.tenant_id,
            Technician.deleted_at.is_(None)
        )
        if active_only:
            query = query.filter(Technician.is_active.is_(True))
        return query.order_by(Technician.name).all()

    def get_technician(self, tech_id: uuid.UUID) -> Technician:
        """Busca um mestre específico na guilda."""
        tech = self.db.query(Technician).filter(
            Technician.id == tech_id,
            Technician.tenant_id == self.tenant_id,
            Technician.deleted_at.is_(None)
        ).first()

        if not tech:
            raise HTTPException(status_code=404, detail="Técnico não encontrado na Cidadela.")
        return tech

    def create_technician(self, tech_in: TechnicianCreate) -> Technician:
        """Forja uma nova identidade técnica no sistema."""
        db_tech = Technician(
            tenant_id=self.tenant_id,
            **tech_in.model_dump()
        )
        self.db.add(db_tech)
        self.db.commit()
        self.db.refresh(db_tech)
        return db_tech

    def update_technician(self, tech_id: uuid.UUID, tech_in: TechnicianUpdate) -> Technician:
        """Refina os dados de um mestre da bancada."""
        db_tech = self.get_technician(tech_id)
        
        update_data = tech_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tech, field, value)
            
        self.db.commit()
        self.db.refresh(db_tech)
        return db_tech

    def delete_technician(self, tech_id: uuid.UUID):
        """Desativa permanentemente um técnico (Soft Delete)."""
        db_tech = self.get_technician(tech_id)
        
        from datetime import datetime, timezone
        db_tech.is_active = False
        db_tech.deleted_at = datetime.now(timezone.utc)
        
        self.db.commit()
