import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class LeadCreate(BaseModel):
    """
    [CONTRATO REST RÍGIDO] Captura inicial de Dados (Lead).
    - Tipagem 100% estrita.
    - Tenant_id abstraído da requisição intencionalmente.
    """
    name: str = Field(..., max_length=255, description="Nome do Proponente da OS")
    email: EmailStr = Field(..., description="E-mail verificado")
    phone: str = Field(..., max_length=20, description="Contato Whatsapp ou Ligação Direta")
    device_interest: Optional[str] = Field(None, max_length=150, description="Modelo-foco de interesse do conserto (Ex: Macbook Pro M1)")
    notes: Optional[str] = Field(None, description="Métricas textuais adicionais de auxílio diagnóstico")

class LeadResponse(BaseModel):
    """
    [RESPONSE CONTRACT] Retorno Otimizado após Injeção em Banco.
    """
    id: uuid.UUID
    message: str = "Lead Amenti Registrado com Sucesso."
    created_at: datetime


class ServiceOrderCreate(BaseModel):
    """
    [CONTRATO REST RÍGIDO] Criação de OS a partir de Lead
    """
    device_info: str = Field(..., max_length=150, description="Descrição ou informações da máquina/equipamento")
    technical_notes: Optional[str] = Field(None, description="Observações iniciais ou notas técnicas")


class ServiceOrderResponse(BaseModel):
    """
    [RESPONSE CONTRACT] Retorno completo após Criação da OS.
    """
    id: uuid.UUID
    lead_id: uuid.UUID
    protocol: str
    status: str
    device_info: str
    technical_notes: Optional[str] = None
    total_value: float
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Allow converting enum to string representation
        if hasattr(obj, 'status') and hasattr(obj.status, 'value'):
            obj_dict = obj.__dict__.copy()
            obj_dict['status'] = obj.status.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)

