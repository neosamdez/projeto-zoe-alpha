import { apiFetch } from "@/lib/api";
import type { UserResponse, UserUpdateByAdmin } from "@/types/auth";

export async function getUsers(isServer = false): Promise<UserResponse[]> {
  return apiFetch<UserResponse[]>("/users/", { isServer });
}

export async function updateUser(
  userId: string,
  data: UserUpdateByAdmin,
  isServer = false
): Promise<UserResponse> {
return apiFetch<UserResponse>(`/users/${userId}`, {
method: "PATCH",
body: JSON.stringify(data),
isServer });
}

export async function deleteUser(userId: string, isServer = false): Promise<void> {
return apiFetch<void>(`/users/${userId}`, {
method: "DELETE",
isServer });
}
