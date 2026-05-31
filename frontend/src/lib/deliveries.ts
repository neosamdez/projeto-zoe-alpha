import { apiFetch } from "@/lib/api";
import type { DeliveryPending, DeliveryPendingCreate } from "@/types";

export async function getDeliveries(status?: string, month?: number, year?: number, isServer = false): Promise<DeliveryPending[]> {
  const params = new URLSearchParams();
  if (status) params.set("status_filter", status);
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  const path = qs ? `/deliveries/?${qs}` : "/deliveries/";
  return apiFetch<DeliveryPending[]>(path, { isServer });
}

export async function createDelivery(data: DeliveryPendingCreate, isServer = false): Promise<DeliveryPending> {
  return apiFetch<DeliveryPending>("/deliveries/", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function receiveDelivery(deliveryId: string, receivedDate?: string, notes?: string, isServer = false): Promise<DeliveryPending> {
  const body: any = {};
  if (receivedDate) body.received_date = receivedDate;
  if (notes) body.notes = notes;
  return apiFetch<DeliveryPending>(`/deliveries/${deliveryId}/receive`, { method: "PATCH", body: JSON.stringify(body), isServer });
}

export async function getOverdue(isServer = false): Promise<DeliveryPending[]> {
  return apiFetch<DeliveryPending[]>("/deliveries/overdue", { isServer });
}

export async function markOverdue(isServer = false): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/deliveries/mark-overdue", { method: "POST", isServer });
}
