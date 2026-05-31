import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models import ReturnCode, RmaStatus, InspectionResult


class RmaRequestCreate(BaseModel):
    order_id: Optional[uuid.UUID] = Field(None, description="FK da OS vinculada")
    product_id: Optional[uuid.UUID] = Field(None, description="FK do produto/peça")
    delivery_code: Optional[str] = Field(None, max_length=50)
    samsung_nf: Optional[str] = Field(None, max_length=50)
    return_code: ReturnCode = Field(..., description="Código de devolução Samsung (805-839)")
    notes: Optional[str] = None


class RmaRequestResponse(BaseModel):
    id: uuid.UUID
    protocol: str
    order_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    delivery_code: Optional[str] = None
    samsung_nf: Optional[str] = None
    return_code: str
    status: str
    deadline_days: int
    deadline_date: Optional[date] = None
    inspection_photos: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'return_code') and hasattr(obj.return_code, 'value'):
            obj_dict = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            obj_dict['return_code'] = obj.return_code.value
            if hasattr(obj.status, 'value'):
                obj_dict['status'] = obj.status.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class RmaStatusUpdate(BaseModel):
    status: RmaStatus = Field(..., description="Novo status do RMA")


class RmaInspectionCreate(BaseModel):
    defect_code: str = Field(..., max_length=10, description="Código SR01-SR22")
    defect_description: str = Field(..., max_length=255)
    photos_url: Optional[str] = None
    result: InspectionResult = Field(default=InspectionResult.PENDING)
    notes: Optional[str] = None


class RmaInspectionResponse(BaseModel):
    id: uuid.UUID
    rma_request_id: uuid.UUID
    defect_code: str
    defect_description: str
    inspector_id: Optional[uuid.UUID] = None
    photos_url: Optional[str] = None
    result: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'result') and hasattr(obj.result, 'value'):
            obj_dict = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            obj_dict['result'] = obj.result.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class ReturnedPartCreate(BaseModel):
    order_id: Optional[uuid.UUID] = None
    part_code: str = Field(..., max_length=50, description="Código da peça (ex: GH82-26047A)")
    delivery_code: Optional[str] = Field(None, max_length=50)
    samsung_nf: Optional[str] = Field(None, max_length=50)
    invoice_date: Optional[date] = None
    return_reason: str = Field(..., max_length=10, description="Código de devolução (805-839)")
    devolution_deadline: int = Field(default=0)
    devolution_date: Optional[date] = None
    return_nf: Optional[str] = Field(None, max_length=50)
    technician_signature: bool = False
    stock_signature: bool = False


class ReturnedPartResponse(BaseModel):
    id: uuid.UUID
    rma_request_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    part_code: str
    delivery_code: Optional[str] = None
    samsung_nf: Optional[str] = None
    invoice_date: Optional[date] = None
    return_reason: str
    devolution_deadline: int
    devolution_date: Optional[date] = None
    return_nf: Optional[str] = None
    technician_signature: bool
    stock_signature: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DefectCodeResponse(BaseModel):
    id: uuid.UUID
    code: str
    description: str
    category: str
    most_used_part: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RmaRequestDetail(RmaRequestResponse):
    inspections: list[RmaInspectionResponse] = []
    returned_parts: list[ReturnedPartResponse] = []
