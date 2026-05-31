import { apiFetch } from "@/lib/api";
import type { AlertConfig, AlertConfigCreate, AlertConfigUpdate } from "@/types";

export async function getAlertConfigs(isServer = false): Promise<AlertConfig[]> {
  return apiFetch<AlertConfig[]>("/alert-configs", { isServer });
}

export async function getAlertConfig(id: string, isServer = false): Promise<AlertConfig> {
  return apiFetch<AlertConfig>(`/alert-configs/${id}`, { isServer });
}

export async function createAlertConfig(data: AlertConfigCreate, isServer = false): Promise<AlertConfig> {
  return apiFetch<AlertConfig>("/alert-configs", { method: "POST", body: JSON.stringify(data), isServer });
}

export async function updateAlertConfig(id: string, data: AlertConfigUpdate, isServer = false): Promise<AlertConfig> {
  return apiFetch<AlertConfig>(`/alert-configs/${id}`, { method: "PATCH", body: JSON.stringify(data), isServer });
}

export async function deleteAlertConfig(id: string, isServer = false): Promise<void> {
  return apiFetch<void>(`/alert-configs/${id}`, { method: "DELETE", isServer });
}
