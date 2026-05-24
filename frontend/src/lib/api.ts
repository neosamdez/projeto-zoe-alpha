export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export const INTERNAL_API_URL = process.env.INTERNAL_API_URL || "http://api:8000/api/v1";

export function getApiUrl(isServer: boolean = false): string {
  return isServer ? INTERNAL_API_URL : API_URL;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  isServer: boolean = false
): Promise<T> {
  const baseUrl = getApiUrl(isServer);
  const token = !isServer ? getStoredToken() : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401 && !isServer) {
    clearStoredToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (res.status === 204) {
    return undefined as T;
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(body.detail || `Erro ${res.status}`);
  }

  return res.json();
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function setStoredToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("access_token", token);
}

export function clearStoredToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
}
