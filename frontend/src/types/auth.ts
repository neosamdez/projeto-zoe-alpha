export type UserRole = "ADMIN" | "TECHNICIAN" | "CUSTOMER";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
}

export interface UserCreate {
  full_name: string;
  email: string;
  password: string;
  role?: UserRole;
}
