import { apiFetch } from "@/lib/api";
import type { DiscardRecord, DiscardRecordCreate } from "@/types";

export async function getDiscards(status?: string, month?: number, year?: number, isServer = false): Promise<DiscardRecord[]> {
  const params = new URLSearchParams();
  if (status) params.set("status_filter", status);
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  const path = qs ? `/discards/?${qs}` : "/discards/";
  return apiFetch<DiscardRecord[]>(path, { isServer });
}

export async function createDiscard(data: DiscardRecordCreate, isServer = false): Promise<DiscardRecord> {
  return apiFetch<DiscardRecord>("/discards/", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function authorizeDiscard(discardId: string, termDocument?: string, isServer = false): Promise<DiscardRecord> {
  const body: any = {};
  if (termDocument) body.term_document = termDocument;
  return apiFetch<DiscardRecord>(`/discards/${discardId}/authorize`, { method: "PATCH", body: JSON.stringify(body), isServer });
}

export async function completeDiscard(discardId: string, isServer = false): Promise<DiscardRecord> {
  return apiFetch<DiscardRecord>(`/discards/${discardId}/complete`, { method: "PATCH", isServer });
}

export async function getDiscardReport(isServer = false): Promise<{ product_type: string; discard_type: string; count: number }[]> {
  return apiFetch<{ product_type: string; discard_type: string; count: number }[]>("/discards/report", { isServer });
}
