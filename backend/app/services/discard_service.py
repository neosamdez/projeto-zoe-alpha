import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, extract
from app.models import DiscardRecord, DiscardStatus
from app.schemas.discard import DiscardRecordCreate, DiscardAuthorizeUpdate
from fastapi import HTTPException


class DiscardService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def list_discards(self, status: Optional[str] = None, month: Optional[int] = None, year: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[DiscardRecord]:
        q = self.db.query(DiscardRecord).filter(DiscardRecord.tenant_id == self.tenant_id, DiscardRecord.deleted_at.is_(None))
        if status:
            q = q.filter(DiscardRecord.status == status)
        if month:
            q = q.filter(extract('month', DiscardRecord.created_at) == month)
        if year:
            q = q.filter(extract('year', DiscardRecord.created_at) == year)
        return q.order_by(desc(DiscardRecord.created_at)).offset(skip).limit(limit).all()

    def create_discard(self, data: DiscardRecordCreate) -> DiscardRecord:
        record = DiscardRecord(
            tenant_id=self.tenant_id,
            serial=data.serial,
            product_type=data.product_type,
            discard_type=data.discard_type,
            reason=data.reason,
            term_document=data.term_document,
            status=DiscardStatus.PENDING,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def authorize_discard(self, discard_id: uuid.UUID, user_id: uuid.UUID, data: DiscardAuthorizeUpdate) -> DiscardRecord:
        record = self.db.query(DiscardRecord).filter(
            DiscardRecord.id == discard_id,
            DiscardRecord.tenant_id == self.tenant_id,
            DiscardRecord.deleted_at.is_(None),
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Descarte não encontrado.")
        record.authorized_by = user_id
        record.status = DiscardStatus.AUTHORIZED
        if data.term_document:
            record.term_document = data.term_document
        self.db.commit()
        self.db.refresh(record)
        return record

    def complete_discard(self, discard_id: uuid.UUID) -> DiscardRecord:
        record = self.db.query(DiscardRecord).filter(
            DiscardRecord.id == discard_id,
            DiscardRecord.tenant_id == self.tenant_id,
            DiscardRecord.deleted_at.is_(None),
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Descarte não encontrado.")
        record.status = DiscardStatus.COMPLETED
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_report(self) -> List[dict]:
        results = self.db.query(
            DiscardRecord.product_type,
            DiscardRecord.discard_type,
            func.count(DiscardRecord.id).label("count"),
        ).filter(
            DiscardRecord.tenant_id == self.tenant_id,
            DiscardRecord.deleted_at.is_(None),
            DiscardRecord.status == DiscardStatus.COMPLETED,
        ).group_by(DiscardRecord.product_type, DiscardRecord.discard_type).all()

        return [{"product_type": r.product_type, "discard_type": r.discard_type, "count": r.count} for r in results]
