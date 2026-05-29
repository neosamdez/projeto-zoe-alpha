import { apiFetch } from "@/lib/api";
import type { Lead, LeadCreate, LeadUpdate } from "@/types";

export async function getLeads(isServer = false): Promise<Lead[]> {
  return apiFetch<Lead[]>("/leads/", { isServer });
}

export async function searchLeads(query: string, isServer = false): Promise<Lead[]> {
  return apiFetch<Lead[]>(`/leads/?q=${encodeURIComponent(query)}`, { isServer });
}

export async function getLead(leadId: string, isServer = false) {
  return apiFetch<any>(`/leads/${leadId}`, { isServer });
}

export async function createLead(data: LeadCreate, isServer = false): Promise<any> {
return apiFetch<any>("/leads/", {
method: "POST",
body: JSON.stringify(data),
isServer });
}

export async function updateLead(leadId: string, data: LeadUpdate, isServer = false): Promise<any> {
return apiFetch<any>(`/leads/${leadId}`, {
method: "PATCH",
body: JSON.stringify(data),
isServer });
}

export async function deleteLead(leadId: string, isServer = false): Promise<any> {
return apiFetch<any>(`/leads/${leadId}`, {
method: "DELETE",
isServer });
}
