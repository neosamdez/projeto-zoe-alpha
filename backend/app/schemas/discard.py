import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models import DiscardStatus


class DiscardRecordCreate(BaseModel):
    serial: str = Field(..., max_length=100, description="Serial do produto")
    product_type: str = Field(..., max_length=30, description="TV|ARCONDICIONADO|HHP|NPC")
    discard_type: str = Field(..., max_length=20, description="TROCA|DESCARTE")
    reason: Optional[str] = None
    term_document: Optional[str] = Field(None, description="URL do termo de descarte")


class DiscardRecordResponse(BaseModel):
    id: uuid.UUID
    serial: str
    product_type: str
    discard_type: str
    reason: Optional[str] = None
    term_document: Optional[str] = None
    authorized_by: Optional[uuid.UUID] = None
    status: str
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


class DiscardAuthorizeUpdate(BaseModel):
    term_document: Optional[str] = Field(None, description="URL do termo assinado")
