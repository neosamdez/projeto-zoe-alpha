import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255, description="Nome da peça/insumo")
    sku: str = Field(..., max_length=100, description="Código SKU de identificação única do item")
    cost_price: Decimal = Field(..., ge=0, description="Preço de custo da peça (Decimal exato)")
    selling_price: Decimal = Field(..., ge=0, description="Preço de venda da peça (Decimal exato)")
    current_stock: int = Field(default=0, ge=0, description="Quantidade física atual em estoque")
    min_stock: int = Field(default=0, ge=0, description="Estoque mínimo recomendável")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: uuid.UUID
    reserved_stock: int = Field(..., description="Estoque reservado logicamente (Tese C)")
    created_at: datetime

    class Config:
        from_attributes = True
