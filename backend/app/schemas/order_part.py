import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class OrderPartCreate(BaseModel):
    """
    [TESE C ABSOLUTA]
    Vinculação Tática. Sem peças avulsas, exige Cadastro no Catálogo.
    Valores monetários Snapshot serão extraídos via Backend.
    """
    product_id: uuid.UUID = Field(..., description="FK Obrigatória do Arsenal (Catálogo)")
    quantity: int = Field(default=1, gt=0, description="Quantidade a ser consumida logicamente")

class OrderPartResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    snapshot_cost_price: Decimal = Field(..., description="Custo travado no tempo - Precisão Absoluta")
    snapshot_selling_price: Decimal = Field(..., description="Venda travada no tempo - Precisão Absoluta")
    created_at: datetime

    class Config:
        from_attributes = True
