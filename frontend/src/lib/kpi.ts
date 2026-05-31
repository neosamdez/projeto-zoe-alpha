import { apiFetch } from "@/lib/api";
import type { KpiMetric, KpiMetricCreate, KpiDashboard, KpiBonusSummary } from "@/types";

export async function createOrUpdateMetric(data: KpiMetricCreate, isServer = false): Promise<KpiMetric> {
  return apiFetch<KpiMetric>("/kpi/", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function getKpiMetrics(month?: number, year?: number, isServer = false): Promise<KpiMetric[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return apiFetch<KpiMetric[]>(`/kpi/${qs ? `?${qs}` : ""}`, { isServer });
}

export async function getKpiDashboard(month: number, year: number, isServer = false): Promise<KpiDashboard> {
  return apiFetch<KpiDashboard>(`/kpi/dashboard?month=${month}&year=${year}`, { isServer });
}

export async function getBonusSummary(month: number, year: number, isServer = false): Promise<KpiBonusSummary[]> {
  return apiFetch<KpiBonusSummary[]>(`/kpi/bonus-summary?month=${month}&year=${year}`, { isServer });
}
