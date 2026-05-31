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

export type RmaStatus = "PENDING" | "INSPECTING" | "APPROVED" | "REJECTED" | "SHIPPED" | "COMPLETED";
export type ReturnCode = "805" | "807" | "808" | "809" | "816" | "819" | "821" | "828" | "838" | "839";
export type MovementType = "IN" | "OUT" | "RESERVE" | "RELEASE" | "RETURN" | "DISCARD";
export type DeliveryStatus = "PENDING" | "RECEIVED" | "OVERDUE";
export type DiscardStatus = "PENDING" | "AUTHORIZED" | "COMPLETED";

export interface RmaRequest {
  id: string;
  protocol: string;
  order_id?: string;
  product_id?: string;
  delivery_code?: string;
  samsung_nf?: string;
  return_code: string;
  status: RmaStatus;
  deadline_days: number;
  deadline_date?: string;
  inspection_photos?: string;
  notes?: string;
  created_at: string;
}

export interface RmaRequestCreate {
  order_id?: string;
  product_id?: string;
  delivery_code?: string;
  samsung_nf?: string;
  return_code: ReturnCode;
  notes?: string;
}

export interface RmaInspection {
  id: string;
  rma_request_id: string;
  defect_code: string;
  defect_description: string;
  inspector_id?: string;
  photos_url?: string;
  result: string;
  notes?: string;
  created_at: string;
}

export interface RmaInspectionCreate {
  defect_code: string;
  defect_description: string;
  photos_url?: string;
  result?: string;
  notes?: string;
}

export interface ReturnedPart {
  id: string;
  rma_request_id: string;
  order_id?: string;
  part_code: string;
  delivery_code?: string;
  samsung_nf?: string;
  invoice_date?: string;
  return_reason: string;
  devolution_deadline: number;
  devolution_date?: string;
  return_nf?: string;
  technician_signature: boolean;
  stock_signature: boolean;
  created_at: string;
}

export interface ReturnedPartCreate {
  order_id?: string;
  part_code: string;
  delivery_code?: string;
  samsung_nf?: string;
  invoice_date?: string;
  return_reason: string;
  devolution_deadline?: number;
  devolution_date?: string;
  return_nf?: string;
  technician_signature?: boolean;
  stock_signature?: boolean;
}

export interface DefectCode {
  id: string;
  code: string;
  description: string;
  category: string;
  most_used_part?: string;
  is_active: boolean;
  created_at: string;
}

export interface RmaRequestDetail extends RmaRequest {
  inspections: RmaInspection[];
  returned_parts: ReturnedPart[];
}

export interface InventoryMovement {
  id: string;
  product_id: string;
  movement_type: MovementType;
  quantity: number;
  reference_id?: string;
  notes?: string;
  created_by?: string;
  created_at: string;
}

export interface InventoryMovementCreate {
  product_id: string;
  movement_type: MovementType;
  quantity: number;
  reference_id?: string;
  notes?: string;
}

export interface InventoryDashboard {
  total_products: number;
  total_stock: number;
  total_reserved: number;
  total_available: number;
  low_stock_count: number;
}

export interface DeliveryPending {
  id: string;
  delivery_number: string;
  pending_qty: number;
  reference_date: string;
  product_code?: string;
  status: DeliveryStatus;
  received_date?: string;
  notes?: string;
  created_at: string;
}

export interface DeliveryPendingCreate {
  delivery_number: string;
  pending_qty: number;
  reference_date: string;
  product_code?: string;
  notes?: string;
}

export interface DiscardRecord {
  id: string;
  serial: string;
  product_type: string;
  discard_type: string;
  reason?: string;
  term_document?: string;
  authorized_by?: string;
  status: DiscardStatus;
  created_at: string;
}

export interface DiscardRecordCreate {
  serial: string;
  product_type: string;
  discard_type: string;
  reason?: string;
  term_document?: string;
}

export interface KpiMetric {
  id: string;
  technician_id?: string;
  month: number;
  year: number;
  nps_score: number;
  first_visit_rate: number;
  waiting_time_avg: number;
  oow_hq_rate: number;
  ow_repair_approved: number;
  ltp_mx_rate: number;
  crrr_mx_rate: number;
  eco_repair_rate: number;
  ssr_rate: number;
  gd_ta_rate: number;
  atendimento_10min: number;
  meta_vendas: number;
  total_points: number;
  bonus_tier?: string;
  bonus_value: number;
  created_at: string;
}

export interface KpiMetricCreate {
  technician_id?: string;
  month: number;
  year: number;
  nps_score?: number;
  first_visit_rate?: number;
  waiting_time_avg?: number;
  oow_hq_rate?: number;
  ow_repair_approved?: number;
  ltp_mx_rate?: number;
  crrr_mx_rate?: number;
  eco_repair_rate?: number;
  ssr_rate?: number;
  gd_ta_rate?: number;
  atendimento_10min?: number;
  meta_vendas?: number;
}

export interface KpiDashboard {
  avg_nps: number;
  avg_first_visit: number;
  avg_waiting_time: number;
  avg_ltp_mx: number;
  avg_crrr_mx: number;
  avg_eco_repair: number;
  avg_ssr: number;
  avg_gd_ta: number;
  technicians: KpiMetric[];
}

export interface KpiBonusSummary {
  technician_id: string;
  technician_name: string;
  total_points: number;
  bonus_tier?: string;
  bonus_value: number;
}

export interface AlertConfig {
  id: string;
  name: string;
  recipient_email: string;
  is_active: boolean;
  min_stock_threshold: number;
  created_at: string;
  updated_at: string;
}

export interface AlertConfigCreate {
  name: string;
  recipient_email: string;
  is_active?: boolean;
  min_stock_threshold?: number;
}

export interface AlertConfigUpdate {
  name?: string;
  recipient_email?: string;
  is_active?: boolean;
  min_stock_threshold?: number;
}
