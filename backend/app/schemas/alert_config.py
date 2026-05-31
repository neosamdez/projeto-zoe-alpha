import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class AlertConfigCreate(BaseModel):
    name: str = Field(..., max_length=100, description="Nome identificador da configuração")
    recipient_email: str = Field(..., max_length=255, description="Email do destinatário")
    is_active: bool = Field(default=True, description="Configuração ativa")
    min_stock_threshold: int = Field(default=0, ge=0, description="Limiar mínimo de estoque para disparar alerta")


class AlertConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    recipient_email: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    min_stock_threshold: Optional[int] = Field(None, ge=0)


class AlertConfigResponse(BaseModel):
    id: uuid.UUID
    name: str
    recipient_email: str
    is_active: bool
    min_stock_threshold: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
