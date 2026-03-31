from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class LeadBase(BaseModel):
    name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    status: str = Field("NEW", max_length=50)
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadOut(LeadBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
