import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class KpiMetricCreate(BaseModel):
    technician_id: Optional[uuid.UUID] = Field(None, description="FK do técnico (null = geral do tenant)")
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)
    nps_score: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    first_visit_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    waiting_time_avg: Decimal = Field(default=Decimal("0.00"), ge=0)
    oow_hq_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    ow_repair_approved: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    ltp_mx_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    crrr_mx_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    eco_repair_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    ssr_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    gd_ta_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    atendimento_10min: Decimal = Field(default=Decimal("0.00"), ge=0)
    meta_vendas: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)


class KpiMetricResponse(BaseModel):
    id: uuid.UUID
    technician_id: Optional[uuid.UUID] = None
    month: int
    year: int
    nps_score: Decimal
    first_visit_rate: Decimal
    waiting_time_avg: Decimal
    oow_hq_rate: Decimal
    ow_repair_approved: Decimal
    ltp_mx_rate: Decimal
    crrr_mx_rate: Decimal
    eco_repair_rate: Decimal
    ssr_rate: Decimal
    gd_ta_rate: Decimal
    atendimento_10min: Decimal
    meta_vendas: Decimal
    total_points: int
    bonus_tier: Optional[str] = None
    bonus_value: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class KpiDashboard(BaseModel):
    avg_nps: Decimal = Decimal("0.00")
    avg_first_visit: Decimal = Decimal("0.00")
    avg_waiting_time: Decimal = Decimal("0.00")
    avg_ltp_mx: Decimal = Decimal("0.00")
    avg_crrr_mx: Decimal = Decimal("0.00")
    avg_eco_repair: Decimal = Decimal("0.00")
    avg_ssr: Decimal = Decimal("0.00")
    avg_gd_ta: Decimal = Decimal("0.00")
    technicians: List[KpiMetricResponse] = []


class KpiBonusSummary(BaseModel):
    technician_id: uuid.UUID
    technician_name: str
    total_points: int
    bonus_tier: Optional[str] = None
    bonus_value: Decimal = Decimal("0.00")


class AttendanceMetric(BaseModel):
    attendant_name: str
    total_tickets: int = 0
    wait_5min: int = 0
    attend_10min: int = 0
    effective: int = 0
