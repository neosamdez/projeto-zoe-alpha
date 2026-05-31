import { apiFetch } from "@/lib/api";
import type {
  RmaRequest,
  RmaRequestCreate,
  RmaRequestDetail,
  RmaInspection,
  RmaInspectionCreate,
  ReturnedPart,
  ReturnedPartCreate,
  DefectCode,
} from "@/types";

export async function getRmas(status?: string, month?: number, year?: number, isServer = false): Promise<RmaRequest[]> {
  const params = new URLSearchParams();
  if (status) params.set("status_filter", status);
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  const path = qs ? `/rma/?${qs}` : "/rma/";
  return apiFetch<RmaRequest[]>(path, { isServer });
}

export async function createRma(data: RmaRequestCreate, isServer = false): Promise<RmaRequest> {
  return apiFetch<RmaRequest>("/rma/", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function getRmaDetail(rmaId: string, isServer = false): Promise<RmaRequestDetail> {
  return apiFetch<RmaRequestDetail>(`/rma/${rmaId}`, { isServer });
}

export async function updateRmaStatus(rmaId: string, status: string, isServer = false): Promise<RmaRequest> {
  return apiFetch<RmaRequest>(`/rma/${rmaId}/status`, { method: "PATCH", body: JSON.stringify({ status }), isServer });
}

export async function addInspection(rmaId: string, data: RmaInspectionCreate, isServer = false): Promise<RmaInspection> {
  return apiFetch<RmaInspection>(`/rma/${rmaId}/inspections`, { method: "POST", body: JSON.stringify(data), isServer });
}

export async function getInspections(rmaId: string, isServer = false): Promise<RmaInspection[]> {
  return apiFetch<RmaInspection[]>(`/rma/${rmaId}/inspections`, { isServer });
}

export async function addReturnedPart(rmaId: string, data: ReturnedPartCreate, isServer = false): Promise<ReturnedPart> {
  return apiFetch<ReturnedPart>(`/rma/${rmaId}/returned-parts`, { method: "POST", body: JSON.stringify(data), isServer });
}

export async function getDefectCodes(isServer = false): Promise<DefectCode[]> {
  return apiFetch<DefectCode[]>("/rma/defect-codes", { isServer });
}
