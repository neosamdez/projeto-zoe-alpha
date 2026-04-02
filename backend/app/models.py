import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SqlEnum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class BaseModel(Base):
    """
    Modelo Base Padrão Amenti.
    - Multi-Tenancy Isolado (tenant_id)
    - UUIDs v4 Nativos PostgreSQL
    - Controle Temporal Intacto (created/updated)
    - Soft Deletes
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserRole(str, enum.Enum):
    ADMIN = 'ADMIN'
    TECHNICIAN = 'TECHNICIAN'
    CUSTOMER = 'CUSTOMER'


class User(BaseModel):
    __tablename__ = 'users'

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, native_enum=False), default=UserRole.TECHNICIAN, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Lead(BaseModel):
    __tablename__ = 'leads'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    device_interest: Mapped[str | None] = mapped_column(String(150))
    notes: Mapped[str | None] = mapped_column(Text)


class ServiceStatus(str, enum.Enum):
    OPEN = 'OPEN'
    DIAGNOSING = 'DIAGNOSING'
    AWAITING_PARTS = 'AWAITING_PARTS'
    IN_REPAIR = 'IN_REPAIR'
    COMPLETED = 'COMPLETED'
    DELIVERED = 'DELIVERED'
    CANCELED = 'CANCELED'


class ServiceOrder(BaseModel):
    __tablename__ = 'service_orders'

    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='RESTRICT'), nullable=False)
    protocol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    status: Mapped[ServiceStatus] = mapped_column(SqlEnum(ServiceStatus, native_enum=False), default=ServiceStatus.OPEN, nullable=False)
    device_info: Mapped[str] = mapped_column(Text, nullable=False)
    technical_notes: Mapped[str | None] = mapped_column(Text)
    total_value: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)

