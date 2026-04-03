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
    Hotfix Sprint 14: inclui lead_name para exibir na coluna 'Cliente' do dashboard.
    """
    id: uuid.UUID
    lead_id: uuid.UUID
    lead_name: Optional[str] = None   # Nome do cliente (via JOIN com Lead)
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
        """
        Override para converter enum ServiceStatus → string.
        Necessário para endpoints que retornam ORM objects (create, update_status).
        O list_orders retorna dicts explícitos — não passa por aqui.
        """
        if hasattr(obj, 'status') and hasattr(obj.status, 'value'):
            obj_dict = obj.__dict__.copy()
            obj_dict['status'] = obj.status.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


from app.models import ServiceStatus

class ServiceOrderStatusUpdate(BaseModel):
    """
    [CONTRATO REST RÍGIDO] Atualização de Status da OS
    """
    status: ServiceStatus = Field(..., description="Novo estágio da Ordem de Serviço")


class OrdersStats(BaseModel):
    """
    [RESPONSE CONTRACT] Estatísticas Agregadas das OS por Tenant.
    Sprint 12 — O Olho de Hórus.
    Isolamento total: só conta OS do tenant do JWT.
    """
    total: int = Field(..., description="Total de OS ativas (non-deleted)")
    open: int = Field(..., description="OS com status OPEN")
    repairing: int = Field(..., description="OS com status IN_REPAIR")
    completed: int = Field(..., description="OS com status COMPLETED")


# ── AUTH SCHEMAS ────────────────────────────────────────────────────────────────

from app.models import UserRole

class UserCreate(BaseModel):
    """
    [CONTRATO REST RÍGIDO] Registro de novo Usuário.
    A senha em texto plano é recebida aqui e imediatamente hashada no Service.
    """
    full_name: str = Field(..., max_length=255, description="Nome completo do Operador")
    email: EmailStr = Field(..., description="E-mail único do Operador")
    password: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")
    role: UserRole = Field(default=UserRole.TECHNICIAN, description="Papel do usuário no sistema")


class UserResponse(BaseModel):
    """
    [RESPONSE CONTRACT] Retorno seguro: NUNCA expõe hashed_password.
    """
    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    tenant_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'role') and hasattr(obj.role, 'value'):
            obj_dict = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            obj_dict['role'] = obj.role.value
            return super().model_validate(obj_dict, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class Token(BaseModel):
    """
    [RESPONSE CONTRACT] Payload de autenticação retornado ao cliente após login.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Claims internas extraídas do JWT para uso nas dependencies."""
    sub: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[str] = None

