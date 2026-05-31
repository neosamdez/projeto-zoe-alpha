import { apiFetch } from "@/lib/api";
import type { InventoryMovement, InventoryMovementCreate, InventoryDashboard, Product } from "@/types";

export async function getMovements(productId?: string, isServer = false): Promise<InventoryMovement[]> {
  const path = productId ? `/inventory/movements?product_id=${productId}` : "/inventory/movements";
  return apiFetch<InventoryMovement[]>(path, { isServer });
}

export async function createMovement(data: InventoryMovementCreate, isServer = false): Promise<InventoryMovement> {
  return apiFetch<InventoryMovement>("/inventory/movements", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function getInventoryDashboard(isServer = false): Promise<InventoryDashboard> {
  return apiFetch<InventoryDashboard>("/inventory/dashboard", { isServer });
}

export async function getLowStock(isServer = false): Promise<Product[]> {
  return apiFetch<Product[]>("/inventory/low-stock", { isServer });
}
