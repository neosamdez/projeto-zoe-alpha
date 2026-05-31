import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from app.models import MovementType


class InventoryMovementCreate(BaseModel):
    product_id: uuid.UUID = Field(..., description="FK do produto")
    movement_type: MovementType = Field(..., description="Tipo: IN, OUT, RESERVE, RELEASE, RETURN, DISCARD")
    quantity: int = Field(..., description="Quantidade movimentada (positivo)")
    reference_id: Optional[str] = Field(None, max_length=100, description="ID de referência (order_id, rma_id, etc.)")
    notes: Optional[str] = None


class InventoryMovementResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    movement_type: str
    quantity: int
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'movement_type') and hasattr(obj.movement_type, 'value'):
            obj_dict = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            obj_dict['movement_type'] = obj.movement_type.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class InventoryDashboard(BaseModel):
    total_products: int
    total_stock: int
    total_reserved: int
    total_available: int
    low_stock_count: int


class PartRepairCreate(BaseModel):
    service: str = Field(..., max_length=50, description="Nº da Service (OS Samsung)")
    part_code: str = Field(..., max_length=50, description="Código da peça")
    delivery_code: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class PartRepairResponse(BaseModel):
    id: uuid.UUID
    service: str
    part_code: str
    delivery_code: Optional[str] = None
    technician_signed: bool = False
    stock_signed: bool = False
    devolution_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
