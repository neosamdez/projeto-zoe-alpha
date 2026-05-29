export type ServiceStatus =
  | "OPEN"
  | "DIAGNOSING"
  | "AWAITING_PARTS"
  | "IN_REPAIR"
  | "COMPLETED"
  | "DELIVERED"
  | "CANCELED";

export interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  device_interest?: string;
  notes?: string;
  created_at: string;
  total_os: number;
}

export interface LeadCreate {
  name: string;
  email: string;
  phone: string;
  device_interest?: string;
  notes?: string;
}

export interface LeadUpdate {
  name?: string;
  email?: string;
  phone?: string;
  device_interest?: string;
  notes?: string;
}

export interface ServiceOrder {
  id: string;
  lead_id: string;
  lead_name?: string;
  protocol: string;
  status: ServiceStatus;
  device_info: string;
  technical_notes?: string;
  total_value: number;
  parts_cost: number;
  technician_id?: string;
  technician?: { id: string; name: string; specialization?: string; is_active: boolean } | null;
  created_at: string;
}

export interface ServiceOrderCreate {
  device_info: string;
  technical_notes?: string;
}

export interface OrderEvent {
  id: string;
  event_type: string;
  description: string;
  created_at: string;
}

export interface OrdersStats {
  total: number;
  open: number;
  repairing: number;
  completed: number;
  projected_revenue: number;
  realized_revenue: number;
  total_parts_cost: number;
  realized_net_profit: number;
  technician_ranking: { technician_id: string; name: string; profit: number }[];
}

export interface OrderPart {
  id: string;
  order_id: string;
  product_id: string;
  quantity: number;
  snapshot_cost_price: number;
  snapshot_selling_price: number;
  created_at: string;
}

export interface OrderPartCreate {
  product_id: string;
  quantity: number;
}

export interface Product {
  id: string;
  name: string;
  sku: string;
  cost_price: number;
  selling_price: number;
  current_stock: number;
  reserved_stock: number;
  min_stock: number;
  created_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  cost_price: number;
  selling_price: number;
  current_stock?: number;
  min_stock?: number;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  cost_price?: number;
  selling_price?: number;
  current_stock?: number;
  min_stock?: number;
}

export interface Technician {
  id: string;
  name: string;
  specialization?: string;
  is_active: boolean;
  created_at: string;
}

export interface TechnicianCreate {
  name: string;
  specialization?: string;
  is_active?: boolean;
}

export interface TechnicianUpdate {
  name?: string;
  specialization?: string;
  is_active?: boolean;
}

export interface VolumeItem {
  date: string;
  count: number;
}

export interface StatusItem {
  status: string;
  count: number;
}

export interface AnalyticsResponse {
  volume: VolumeItem[];
  distribution: StatusItem[];
}
