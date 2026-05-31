import uuid
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models import KpiMetric, Technician
from app.schemas.kpi import KpiMetricCreate, KpiMetricResponse, KpiDashboard, KpiBonusSummary
from app.core.cache import cache_get, cache_set, cache_invalidate
from fastapi import HTTPException

BONUS_TIERS = {
    "DIAMOND": {"min_points": 90, "value": Decimal("2000.00")},
    "GOLD": {"min_points": 75, "value": Decimal("1500.00")},
    "SILVER": {"min_points": 60, "value": Decimal("1000.00")},
    "BRONZE": {"min_points": 45, "value": Decimal("500.00")},
}

METRIC_WEIGHTS = {
    "nps_score": 15,
    "first_visit_rate": 12,
    "waiting_time_avg": 8,
    "oow_hq_rate": 8,
    "ow_repair_approved": 8,
    "ltp_mx_rate": 10,
    "crrr_mx_rate": 10,
    "eco_repair_rate": 8,
    "ssr_rate": 7,
    "gd_ta_rate": 7,
    "atendimento_10min": 4,
    "meta_vendas": 3,
}


class KpiService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def _calculate_points(self, data: KpiMetricCreate) -> int:
        points = 0
        for metric, weight in METRIC_WEIGHTS.items():
            val = getattr(data, metric, Decimal("0.00"))
            if metric == "waiting_time_avg" or metric == "atendimento_10min":
                normalized = max(0, 100 - float(val))
            else:
                normalized = float(val)
            points += int((normalized / 100) * weight)
        return min(points, 100)

    def _calculate_tier(self, points: int) -> Optional[str]:
        for tier_name, tier_info in BONUS_TIERS.items():
            if points >= tier_info["min_points"]:
                return tier_name
        return None

    def _calculate_bonus_value(self, tier: Optional[str]) -> Decimal:
        if tier and tier in BONUS_TIERS:
            return BONUS_TIERS[tier]["value"]
        return Decimal("0.00")

    def create_or_update_metric(self, data: KpiMetricCreate) -> KpiMetric:
        existing = self.db.query(KpiMetric).filter(
            KpiMetric.tenant_id == self.tenant_id,
            KpiMetric.technician_id == data.technician_id,
            KpiMetric.month == data.month,
            KpiMetric.year == data.year,
            KpiMetric.deleted_at.is_(None),
        ).first()

        total_points = self._calculate_points(data)
        bonus_tier = self._calculate_tier(total_points)
        bonus_value = self._calculate_bonus_value(bonus_tier)

        if existing:
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(existing, field):
                    setattr(existing, field, value)
            existing.total_points = total_points
            existing.bonus_tier = bonus_tier
            existing.bonus_value = bonus_value
            self.db.commit()
            self.db.refresh(existing)
            cache_invalidate(f"kpi_dashboard:{self.tenant_id}")
            return existing

        metric = KpiMetric(
            tenant_id=self.tenant_id,
            technician_id=data.technician_id,
            month=data.month,
            year=data.year,
            nps_score=data.nps_score,
            first_visit_rate=data.first_visit_rate,
            waiting_time_avg=data.waiting_time_avg,
            oow_hq_rate=data.oow_hq_rate,
            ow_repair_approved=data.ow_repair_approved,
            ltp_mx_rate=data.ltp_mx_rate,
            crrr_mx_rate=data.crrr_mx_rate,
            eco_repair_rate=data.eco_repair_rate,
            ssr_rate=data.ssr_rate,
            gd_ta_rate=data.gd_ta_rate,
            atendimento_10min=data.atendimento_10min,
            meta_vendas=data.meta_vendas,
            total_points=total_points,
            bonus_tier=bonus_tier,
            bonus_value=bonus_value,
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        cache_invalidate(f"kpi_dashboard:{self.tenant_id}")
        return metric

    def list_metrics(self, month: Optional[int] = None, year: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[KpiMetric]:
        q = self.db.query(KpiMetric).filter(KpiMetric.tenant_id == self.tenant_id, KpiMetric.deleted_at.is_(None))
        if month:
            q = q.filter(KpiMetric.month == month)
        if year:
            q = q.filter(KpiMetric.year == year)
        return q.order_by(desc(KpiMetric.year), desc(KpiMetric.month)).offset(skip).limit(limit).all()

    def get_metric(self, metric_id: uuid.UUID) -> KpiMetric:
        metric = self.db.query(KpiMetric).filter(
            KpiMetric.id == metric_id,
            KpiMetric.tenant_id == self.tenant_id,
            KpiMetric.deleted_at.is_(None),
        ).first()
        if not metric:
            raise HTTPException(status_code=404, detail="Métrica KPI não encontrada.")
        return metric

    def get_dashboard(self, month: int, year: int) -> KpiDashboard:
        cache_key = f"kpi_dashboard:{self.tenant_id}:{month}:{year}"
        cached = cache_get(cache_key)
        if cached:
            return KpiDashboard(**cached)

        metrics = self.db.query(KpiMetric).filter(
            KpiMetric.tenant_id == self.tenant_id,
            KpiMetric.month == month,
            KpiMetric.year == year,
            KpiMetric.deleted_at.is_(None),
        ).all()

        if not metrics:
            return KpiDashboard(technicians=[])

        avg = lambda field: sum(float(getattr(m, field)) for m in metrics) / len(metrics)

        result = KpiDashboard(
            avg_nps=Decimal(str(round(avg("nps_score"), 2))),
            avg_first_visit=Decimal(str(round(avg("first_visit_rate"), 2))),
            avg_waiting_time=Decimal(str(round(avg("waiting_time_avg"), 2))),
            avg_ltp_mx=Decimal(str(round(avg("ltp_mx_rate"), 2))),
            avg_crrr_mx=Decimal(str(round(avg("crrr_mx_rate"), 2))),
            avg_eco_repair=Decimal(str(round(avg("eco_repair_rate"), 2))),
            avg_ssr=Decimal(str(round(avg("ssr_rate"), 2))),
            avg_gd_ta=Decimal(str(round(avg("gd_ta_rate"), 2))),
            technicians=[KpiMetricResponse.model_validate(m) for m in metrics],
        )
        cache_set(cache_key, result.model_dump(), ttl=300)
        return result

    def get_bonus_summary(self, month: int, year: int) -> List[KpiBonusSummary]:
        metrics = self.db.query(KpiMetric).filter(
            KpiMetric.tenant_id == self.tenant_id,
            KpiMetric.month == month,
            KpiMetric.year == year,
            KpiMetric.deleted_at.is_(None),
        ).all()

        summaries = []
        for m in metrics:
            tech_name = m.technician.name if m.technician else "Geral"
            summaries.append(KpiBonusSummary(
                technician_id=m.technician_id or uuid.uuid4(),
                technician_name=tech_name,
                total_points=m.total_points,
                bonus_tier=m.bonus_tier,
                bonus_value=m.bonus_value,
            ))
        return sorted(summaries, key=lambda s: s.total_points, reverse=True)
