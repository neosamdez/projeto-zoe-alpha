import { apiFetch } from "@/lib/api";
import type { Product, ProductCreate, ProductUpdate } from "@/types";

export async function getProducts(isServer = false): Promise<Product[]> {
  return apiFetch<Product[]>("/products/", { isServer });
}

export async function getProduct(productId: string, isServer = false): Promise<Product> {
  return apiFetch<Product>(`/products/${productId}`, { isServer });
}

export async function createProduct(data: ProductCreate, isServer = false): Promise<Product> {
return apiFetch<Product>("/products/", {
method: "POST",
body: JSON.stringify(data),
isServer });
}

export async function updateProduct(
  productId: string,
  data: ProductUpdate,
  isServer = false
): Promise<Product> {
return apiFetch<Product>(`/products/${productId}`, {
method: "PATCH",
body: JSON.stringify(data),
isServer });
}

export async function deleteProduct(productId: string, isServer = false): Promise<void> {
return apiFetch<void>(`/products/${productId}`, {
method: "DELETE",
isServer });
}
