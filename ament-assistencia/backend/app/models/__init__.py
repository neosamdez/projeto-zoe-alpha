from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base, BaseModel

class User(BaseModel):
    __tablename__ = "users"
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    full_name = Column(String)

class Lead(BaseModel):
    __tablename__ = "leads"
    name = Column(String, nullable=False)
    phone = Column(String, index=True)
    email = Column(String)
    status = Column(String, default="NEW")
    notes = Column(Text)

class ServiceOrder(BaseModel):
    __tablename__ = "service_orders"
    number = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    status = Column(String, default="OPEN")
    lead_id = Column(ForeignKey("leads.id"), nullable=True)
    
    lead = relationship("Lead")
