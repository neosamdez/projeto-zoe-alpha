import { apiFetch } from "@/lib/api";
import type {
  ServiceOrder,
  ServiceOrderCreate,
  OrdersStats,
  OrderEvent,
  OrderPart,
  OrderPartCreate,
  AnalyticsResponse,
} from "@/types";

export async function getOrders(isServer = false): Promise<ServiceOrder[]> {
  return apiFetch<ServiceOrder[]>("/orders/", { isServer });
}

export async function getOrdersByStatus(status: string, isServer = false): Promise<ServiceOrder[]> {
  return apiFetch<ServiceOrder[]>(`/orders/?status=${status}`, { isServer });
}

export async function searchOrders(query: string, isServer = false): Promise<ServiceOrder[]> {
  return apiFetch<ServiceOrder[]>(`/orders/?search=${encodeURIComponent(query)}`, { isServer });
}

export async function getOrderByProtocol(protocol: string, isServer = false): Promise<ServiceOrder> {
  return apiFetch<ServiceOrder>(`/orders/${protocol}`, { isServer });
}

export async function createOrderFromLead(
  leadId: string,
  data: ServiceOrderCreate,
  isServer = false
): Promise<ServiceOrder> {
return apiFetch<ServiceOrder>(`/orders/from-lead/${leadId}`, {
method: "POST",
body: JSON.stringify(data),
isServer });
}

export async function updateOrderStatus(
  orderId: string,
  status: string,
  isServer = false
): Promise<ServiceOrder> {
return apiFetch<ServiceOrder>(`/orders/${orderId}/status`, {
method: "PATCH",
body: JSON.stringify({ status }),
isServer });
}

export async function assignTechnician(
  orderId: string,
  technicianId: string | null,
  isServer = false
): Promise<ServiceOrder> {
return apiFetch<ServiceOrder>(`/orders/${orderId}/assign`, {
method: "PATCH",
body: JSON.stringify({ technician_id: technicianId }),
isServer });
}

export async function updateOrderValue(
  orderId: string,
  totalValue: number,
  isServer = false
): Promise<ServiceOrder> {
return apiFetch<ServiceOrder>(`/orders/${orderId}/value`, {
method: "PATCH",
body: JSON.stringify({ total_value: totalValue }),
isServer });
}

export async function updateOrder(
  orderId: string,
  data: { device_info?: string; technical_notes?: string },
  isServer = false
): Promise<ServiceOrder> {
return apiFetch<ServiceOrder>(`/orders/${orderId}`, {
method: "PATCH",
body: JSON.stringify(data),
isServer });
}

export async function addOrderNote(
  orderId: string,
  content: string,
  isServer = false
): Promise<OrderEvent> {
return apiFetch<OrderEvent>(`/orders/${orderId}/notes`, {
method: "POST",
body: JSON.stringify({ content }),
isServer });
}

export async function deleteOrder(orderId: string, isServer = false): Promise<any> {
return apiFetch<any>(`/orders/${orderId}`, {
method: "DELETE",
isServer });
}

export async function getOrderEvents(orderId: string, isServer = false): Promise<OrderEvent[]> {
  return apiFetch<OrderEvent[]>(`/orders/${orderId}/events`, { isServer });
}

export async function getOrderParts(orderId: string, isServer = false): Promise<OrderPart[]> {
  return apiFetch<OrderPart[]>(`/orders/${orderId}/parts`, { isServer });
}

export async function addOrderPart(
  orderId: string,
  data: OrderPartCreate,
  isServer = false
): Promise<OrderPart> {
return apiFetch<OrderPart>(`/orders/${orderId}/parts`, {
method: "POST",
body: JSON.stringify(data),
isServer });
}

export async function removeOrderPart(partId: string, isServer = false): Promise<void> {
return apiFetch<void>(`/orders/parts/${partId}`, {
method: "DELETE",
isServer });
}

export async function getOrdersStats(isServer = false): Promise<OrdersStats> {
  return apiFetch<OrdersStats>("/orders/stats", { isServer });
}

export async function getOrdersAnalytics(days = 30, isServer = false): Promise<AnalyticsResponse> {
  return apiFetch<AnalyticsResponse>(`/orders/analytics?days=${days}`, { isServer });
}
