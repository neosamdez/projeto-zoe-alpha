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
