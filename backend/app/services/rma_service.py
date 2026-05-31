import uuid
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, extract
from app.models import (
    RmaRequest, RmaInspection, ReturnedPart, DefectCode,
    ReturnCode, RmaStatus, InspectionResult, RETURN_CODE_DEADLINES,
)
from app.schemas.rma import (
    RmaRequestCreate, RmaInspectionCreate, ReturnedPartCreate,
)
from fastapi import HTTPException


class RmaService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def _generate_protocol(self) -> str:
        year = date.today().strftime("%y")
        prefix = f"RMA-{year}-"
        last = (
            self.db.query(RmaRequest)
            .filter(RmaRequest.tenant_id == self.tenant_id, RmaRequest.protocol.like(f"{prefix}%"))
            .order_by(desc(RmaRequest.protocol))
            .first()
        )
        if last:
            num = int(last.protocol.split("-")[-1]) + 1
        else:
            num = 1
        return f"{prefix}{num:04d}"

    def create_rma(self, user_id: uuid.UUID, data: RmaRequestCreate) -> RmaRequest:
        protocol = self._generate_protocol()
        deadline_days = RETURN_CODE_DEADLINES.get(data.return_code, 0)
        deadline_date = date.today() + timedelta(days=deadline_days) if deadline_days > 0 else None

        rma = RmaRequest(
            tenant_id=self.tenant_id,
            protocol=protocol,
            order_id=data.order_id,
            product_id=data.product_id,
            delivery_code=data.delivery_code,
            samsung_nf=data.samsung_nf,
            return_code=data.return_code,
            status=RmaStatus.PENDING,
            deadline_days=deadline_days,
            deadline_date=deadline_date,
            notes=data.notes,
        )
        self.db.add(rma)
        self.db.commit()
        self.db.refresh(rma)
        return rma

    def list_rmas(self, status: Optional[str] = None, month: Optional[int] = None, year: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[RmaRequest]:
        q = self.db.query(RmaRequest).filter(RmaRequest.tenant_id == self.tenant_id, RmaRequest.deleted_at.is_(None))
        if status:
            q = q.filter(RmaRequest.status == status)
        if month:
            q = q.filter(extract('month', RmaRequest.created_at) == month)
        if year:
            q = q.filter(extract('year', RmaRequest.created_at) == year)
        return q.order_by(desc(RmaRequest.created_at)).offset(skip).limit(limit).all()

    def get_rma(self, rma_id: uuid.UUID) -> Optional[RmaRequest]:
        rma = self.db.query(RmaRequest).filter(
            RmaRequest.id == rma_id, RmaRequest.tenant_id == self.tenant_id, RmaRequest.deleted_at.is_(None)
        ).first()
        if not rma:
            raise HTTPException(status_code=404, detail="RMA não encontrado.")
        return rma

    def update_status(self, rma_id: uuid.UUID, new_status: RmaStatus) -> RmaRequest:
        rma = self.get_rma(rma_id)
        rma.status = new_status
        self.db.commit()
        self.db.refresh(rma)
        return rma

    def add_inspection(self, rma_id: uuid.UUID, inspector_id: uuid.UUID, data: RmaInspectionCreate) -> RmaInspection:
        self.get_rma(rma_id)

        inspection = RmaInspection(
            tenant_id=self.tenant_id,
            rma_request_id=rma_id,
            defect_code=data.defect_code,
            defect_description=data.defect_description,
            inspector_id=inspector_id,
            photos_url=data.photos_url,
            result=data.result,
            notes=data.notes,
        )
        self.db.add(inspection)

        rma = self.get_rma(rma_id)
        if data.result == InspectionResult.APPROVED:
            rma.status = RmaStatus.APPROVED
        elif data.result == InspectionResult.REJECTED:
            rma.status = RmaStatus.REJECTED
        else:
            rma.status = RmaStatus.INSPECTING

        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    def list_inspections(self, rma_id: uuid.UUID) -> List[RmaInspection]:
        self.get_rma(rma_id)
        return self.db.query(RmaInspection).filter(
            RmaInspection.rma_request_id == rma_id,
            RmaInspection.tenant_id == self.tenant_id,
            RmaInspection.deleted_at.is_(None),
        ).order_by(desc(RmaInspection.created_at)).all()

    def add_returned_part(self, rma_id: uuid.UUID, data: ReturnedPartCreate) -> ReturnedPart:
        self.get_rma(rma_id)
        part = ReturnedPart(
            tenant_id=self.tenant_id,
            rma_request_id=rma_id,
            order_id=data.order_id,
            part_code=data.part_code,
            delivery_code=data.delivery_code,
            samsung_nf=data.samsung_nf,
            invoice_date=data.invoice_date,
            return_reason=data.return_reason,
            devolution_deadline=data.devolution_deadline,
            devolution_date=data.devolution_date,
            return_nf=data.return_nf,
            technician_signature=data.technician_signature,
            stock_signature=data.stock_signature,
        )
        self.db.add(part)
        self.db.commit()
        self.db.refresh(part)
        return part

    def list_defect_codes(self) -> List[DefectCode]:
        return self.db.query(DefectCode).filter(
            DefectCode.tenant_id == self.tenant_id,
            DefectCode.is_active == True,
            DefectCode.deleted_at.is_(None),
        ).order_by(DefectCode.code).all()

    def get_detail(self, rma_id: uuid.UUID) -> dict:
        rma = self.get_rma(rma_id)
        inspections = self.list_inspections(rma_id)
        returned_parts = self.db.query(ReturnedPart).filter(
            ReturnedPart.rma_request_id == rma_id,
            ReturnedPart.tenant_id == self.tenant_id,
            ReturnedPart.deleted_at.is_(None),
        ).all()
        return {"rma": rma, "inspections": inspections, "returned_parts": returned_parts}
