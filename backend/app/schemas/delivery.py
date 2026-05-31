import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models import DeliveryStatus


class DeliveryPendingCreate(BaseModel):
    delivery_number: str = Field(..., max_length=50, description="Nº do delivery")
    pending_qty: int = Field(default=0, ge=0, description="Quantidade pendente")
    reference_date: date = Field(..., description="Data de referência")
    product_code: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class DeliveryPendingResponse(BaseModel):
    id: uuid.UUID
    delivery_number: str
    pending_qty: int
    reference_date: date
    product_code: Optional[str] = None
    status: str
    received_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'status') and hasattr(obj.status, 'value'):
            obj_dict = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            obj_dict['status'] = obj.status.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class DeliveryReceiveUpdate(BaseModel):
    received_date: Optional[date] = Field(None, description="Data de recebimento (default: hoje)")
    notes: Optional[str] = None
