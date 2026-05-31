import uuid
import enum
from datetime import datetime, timezone, date
from sqlalchemy import String, DateTime, Date, Enum as SqlEnum, ForeignKey, Numeric, Text, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from typing import Optional
from decimal import Decimal

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


class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_user_tenant_email'),
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, native_enum=False), default=UserRole.TECHNICIAN, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Lead(BaseModel):
    __tablename__ = 'leads'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_lead_tenant_email'),
    )

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


class Technician(BaseModel):
    """
    [MESTRES DA BANCADA] Identidade técnica operacional.
    Responsável pela execução e lucro de cada OS.
    Sprint 28: +bp_code (BPCODE Samsung), +occupation (cargo P4P).
    """
    __tablename__ = 'technicians'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    bp_code: Mapped[str | None] = mapped_column(String(50))
    occupation: Mapped[str | None] = mapped_column(String(100))


class ServiceOrder(BaseModel):
    __tablename__ = 'service_orders'

    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='RESTRICT'), nullable=False)
    technician_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('technicians.id', ondelete='SET NULL'), nullable=True, index=True)

    protocol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    status: Mapped[ServiceStatus] = mapped_column(SqlEnum(ServiceStatus, native_enum=False), default=ServiceStatus.OPEN, nullable=False)
    device_info: Mapped[str] = mapped_column(Text, nullable=False)
    technical_notes: Mapped[str | None] = mapped_column(Text)
    total_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    parts_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))

    defect_code: Mapped[str | None] = mapped_column(String(10))
    grms_number: Mapped[str | None] = mapped_column(String(50))
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    scheduled_shift: Mapped[str | None] = mapped_column(String(10))
    route_car: Mapped[str | None] = mapped_column(String(20))
    route_technicians: Mapped[str | None] = mapped_column(Text)

    technician: Mapped[Optional["Technician"]] = relationship("Technician", lazy="selectin")


class OrderEvent(BaseModel):
    """
    [AUDITORIA ABSOLUTA] Registro de Eventos da OS.
    - STATUS_CHANGED: Mudança de estágio no Kanban.
    - CREATED: Abertura da OS.
    - NOTE_ADDED: Adição de observação técnica.
    """
    __tablename__ = 'order_events'

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('service_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # Ex: STATUS_CHANGED
    description: Mapped[str] = mapped_column(Text, nullable=False)


class OrderPart(BaseModel):
    """
    [CENTRAL DE CUSTOS E RESERVA] Insumos e Peças vinculadas à OS.
    - Congelamento de preços para blindagem de faturamento (Snapshot).
    - Subtração lógica via Tese C (Matriz Híbrida Militar).
    """
    __tablename__ = 'order_parts'

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('service_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=True, index=True)
    
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    snapshot_cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    snapshot_selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))


class Product(BaseModel):
    """
    [ARSENAL DE ELITE] Gestão de Estoque e Inventário (TESE C - Reserva Lógica).
    Sprint 28: +category (divisão Samsung), +samsung_part_code (código peça BN96/GH82).
    """
    __tablename__ = 'products'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'sku', name='uq_product_tenant_sku'),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    current_stock: Mapped[int] = mapped_column(default=0, nullable=False)
    reserved_stock: Mapped[int] = mapped_column(default=0, nullable=False)
    min_stock: Mapped[int] = mapped_column(default=0, nullable=False)
    category: Mapped[str] = mapped_column(String(20), default="VD")
    samsung_part_code: Mapped[str | None] = mapped_column(String(50))


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 28 — FASE 2: NOVOS MODELOS (RMA, KPI, INVENTÁRIO, DELIVERIES, DESCARTE)
# ══════════════════════════════════════════════════════════════════════════════


class ReturnCode(str, enum.Enum):
    C805 = '805'
    C807 = '807'
    C808 = '808'
    C809 = '809'
    C816 = '816'
    C819 = '819'
    C821 = '821'
    C828 = '828'
    C838 = '838'
    C839 = '839'


RETURN_CODE_DEADLINES = {
    ReturnCode.C805: 30,
    ReturnCode.C807: 60,
    ReturnCode.C808: 7,
    ReturnCode.C809: 2,
    ReturnCode.C816: 0,
    ReturnCode.C819: 7,
    ReturnCode.C821: 30,
    ReturnCode.C828: 7,
    ReturnCode.C838: 60,
    ReturnCode.C839: 200,
}


class RmaStatus(str, enum.Enum):
    PENDING = 'PENDING'
    INSPECTING = 'INSPECTING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    SHIPPED = 'SHIPPED'
    COMPLETED = 'COMPLETED'


class RmaRequest(BaseModel):
    __tablename__ = 'rma_requests'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'protocol', name='uq_rma_tenant_protocol'),
    )

    protocol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('service_orders.id', ondelete='SET NULL'), nullable=True, index=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='SET NULL'), nullable=True, index=True)
    delivery_code: Mapped[str | None] = mapped_column(String(50))
    samsung_nf: Mapped[str | None] = mapped_column(String(50))
    return_code: Mapped[ReturnCode] = mapped_column(SqlEnum(ReturnCode, native_enum=False), nullable=False)
    status: Mapped[RmaStatus] = mapped_column(SqlEnum(RmaStatus, native_enum=False), default=RmaStatus.PENDING, nullable=False)
    deadline_days: Mapped[int] = mapped_column(default=0, nullable=False)
    deadline_date: Mapped[date | None] = mapped_column(Date)
    inspection_photos: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    order: Mapped[Optional["ServiceOrder"]] = relationship("ServiceOrder", lazy="selectin")
    product: Mapped[Optional["Product"]] = relationship("Product", lazy="selectin")


class InspectionResult(str, enum.Enum):
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PENDING = 'PENDING'


class RmaInspection(BaseModel):
    __tablename__ = 'rma_inspections'

    rma_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('rma_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    defect_code: Mapped[str] = mapped_column(String(10), nullable=False)
    defect_description: Mapped[str] = mapped_column(String(255), nullable=False)
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    photos_url: Mapped[str | None] = mapped_column(Text)
    result: Mapped[InspectionResult] = mapped_column(SqlEnum(InspectionResult, native_enum=False), default=InspectionResult.PENDING, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    rma_request: Mapped[Optional["RmaRequest"]] = relationship("RmaRequest", lazy="selectin")
    inspector: Mapped[Optional["User"]] = relationship("User", lazy="selectin")


class DefectCode(BaseModel):
    __tablename__ = 'defect_codes'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_defect_tenant_code'),
    )

    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    most_used_part: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class ReturnedPart(BaseModel):
    __tablename__ = 'returned_parts'

    rma_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('rma_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('service_orders.id', ondelete='SET NULL'), nullable=True, index=True)
    part_code: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_code: Mapped[str | None] = mapped_column(String(50))
    samsung_nf: Mapped[str | None] = mapped_column(String(50))
    invoice_date: Mapped[date | None] = mapped_column(Date)
    return_reason: Mapped[str] = mapped_column(String(10), nullable=False)
    devolution_deadline: Mapped[int] = mapped_column(default=0, nullable=False)
    devolution_date: Mapped[date | None] = mapped_column(Date)
    return_nf: Mapped[str | None] = mapped_column(String(50))
    technician_signature: Mapped[bool] = mapped_column(default=False, nullable=False)
    stock_signature: Mapped[bool] = mapped_column(default=False, nullable=False)


class KpiMetric(BaseModel):
    __tablename__ = 'kpi_metrics'

    technician_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('technicians.id', ondelete='SET NULL'), nullable=True, index=True)
    month: Mapped[int] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    nps_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    first_visit_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    waiting_time_avg: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    oow_hq_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    ow_repair_approved: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    ltp_mx_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    crrr_mx_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    eco_repair_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    ssr_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    gd_ta_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    atendimento_10min: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    meta_vendas: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    total_points: Mapped[int] = mapped_column(default=0, nullable=False)
    bonus_tier: Mapped[str | None] = mapped_column(String(20))
    bonus_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))

    technician: Mapped[Optional["Technician"]] = relationship("Technician", lazy="selectin")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'technician_id', 'month', 'year', name='uq_kpi_tenant_tech_month'),
    )


class MovementType(str, enum.Enum):
    IN = 'IN'
    OUT = 'OUT'
    RESERVE = 'RESERVE'
    RELEASE = 'RELEASE'
    RETURN = 'RETURN'
    DISCARD = 'DISCARD'


class InventoryMovement(BaseModel):
    __tablename__ = 'inventory_movements'

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    movement_type: Mapped[MovementType] = mapped_column(SqlEnum(MovementType, native_enum=False), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    product: Mapped[Optional["Product"]] = relationship("Product", lazy="selectin")
    creator: Mapped[Optional["User"]] = relationship("User", lazy="selectin")


class DeliveryStatus(str, enum.Enum):
    PENDING = 'PENDING'
    RECEIVED = 'RECEIVED'
    OVERDUE = 'OVERDUE'


class DeliveryPending(BaseModel):
    __tablename__ = 'delivery_pendings'

    delivery_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pending_qty: Mapped[int] = mapped_column(default=0, nullable=False)
    reference_date: Mapped[date] = mapped_column(Date, nullable=False)
    product_code: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[DeliveryStatus] = mapped_column(SqlEnum(DeliveryStatus, native_enum=False), default=DeliveryStatus.PENDING, nullable=False)
    received_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


class DiscardStatus(str, enum.Enum):
    PENDING = 'PENDING'
    AUTHORIZED = 'AUTHORIZED'
    COMPLETED = 'COMPLETED'


class DiscardRecord(BaseModel):
    __tablename__ = 'discard_records'

    serial: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    product_type: Mapped[str] = mapped_column(String(30), nullable=False)
    discard_type: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    term_document: Mapped[str | None] = mapped_column(Text)
    authorized_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status: Mapped[DiscardStatus] = mapped_column(SqlEnum(DiscardStatus, native_enum=False), default=DiscardStatus.PENDING, nullable=False)

    authorizer: Mapped[Optional["User"]] = relationship("User", lazy="selectin")


class AlertConfig(BaseModel):
    __tablename__ = 'alert_configs'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_alert_config_tenant_name'),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    min_stock_threshold: Mapped[int] = mapped_column(default=0, nullable=False)

