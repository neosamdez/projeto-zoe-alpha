import uuid
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, extract
from app.models import DeliveryPending, DeliveryStatus
from app.schemas.delivery import DeliveryPendingCreate, DeliveryReceiveUpdate
from fastapi import HTTPException


class DeliveryService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def list_deliveries(self, status: Optional[str] = None, month: Optional[int] = None, year: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[DeliveryPending]:
        q = self.db.query(DeliveryPending).filter(DeliveryPending.tenant_id == self.tenant_id, DeliveryPending.deleted_at.is_(None))
        if status:
            q = q.filter(DeliveryPending.status == status)
        if month:
            q = q.filter(extract('month', DeliveryPending.reference_date) == month)
        if year:
            q = q.filter(extract('year', DeliveryPending.reference_date) == year)
        return q.order_by(desc(DeliveryPending.reference_date)).offset(skip).limit(limit).all()

    def create_delivery(self, data: DeliveryPendingCreate) -> DeliveryPending:
        delivery = DeliveryPending(
            tenant_id=self.tenant_id,
            delivery_number=data.delivery_number,
            pending_qty=data.pending_qty,
            reference_date=data.reference_date,
            product_code=data.product_code,
            status=DeliveryStatus.PENDING,
            notes=data.notes,
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def receive_delivery(self, delivery_id: uuid.UUID, data: DeliveryReceiveUpdate) -> DeliveryPending:
        delivery = self.db.query(DeliveryPending).filter(
            DeliveryPending.id == delivery_id,
            DeliveryPending.tenant_id == self.tenant_id,
            DeliveryPending.deleted_at.is_(None),
        ).first()
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery não encontrado.")
        delivery.status = DeliveryStatus.RECEIVED
        delivery.received_date = data.received_date or date.today()
        if data.notes:
            delivery.notes = data.notes
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def list_overdue(self) -> List[DeliveryPending]:
        today = date.today()
        cutoff = today - timedelta(days=7)
        return self.db.query(DeliveryPending).filter(
            DeliveryPending.tenant_id == self.tenant_id,
            DeliveryPending.deleted_at.is_(None),
            DeliveryPending.status == DeliveryStatus.PENDING,
            DeliveryPending.reference_date < cutoff,
        ).order_by(desc(DeliveryPending.reference_date)).all()

    def mark_overdue(self) -> int:
        today = date.today()
        cutoff = today - timedelta(days=7)
        count = self.db.query(DeliveryPending).filter(
            DeliveryPending.tenant_id == self.tenant_id,
            DeliveryPending.deleted_at.is_(None),
            DeliveryPending.status == DeliveryStatus.PENDING,
            DeliveryPending.reference_date < cutoff,
        ).update({DeliveryPending.status: DeliveryStatus.OVERDUE}, synchronize_session="fetch")
        self.db.commit()
        return count
