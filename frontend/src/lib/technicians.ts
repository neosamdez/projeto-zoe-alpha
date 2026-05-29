import { apiFetch } from "@/lib/api";
import type { Technician, TechnicianCreate, TechnicianUpdate } from "@/types";

export async function getTechnicians(activeOnly = false, isServer = false): Promise<Technician[]> {
  return apiFetch<Technician[]>(`/technicians/?active_only=${activeOnly}`, { isServer });
}

export async function getTechnician(techId: string, isServer = false): Promise<Technician> {
  return apiFetch<Technician>(`/technicians/${techId}`, { isServer });
}

export async function createTechnician(data: TechnicianCreate, isServer = false): Promise<Technician> {
return apiFetch<Technician>("/technicians/", {
method: "POST",
body: JSON.stringify(data),
isServer });
}

export async function updateTechnician(
  techId: string,
  data: TechnicianUpdate,
  isServer = false
): Promise<Technician> {
return apiFetch<Technician>(`/technicians/${techId}`, {
method: "PATCH",
body: JSON.stringify(data),
isServer });
}

export async function deleteTechnician(techId: string, isServer = false): Promise<void> {
return apiFetch<void>(`/technicians/${techId}`, {
method: "DELETE",
isServer });
}
