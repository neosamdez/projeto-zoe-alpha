"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { getStoredToken, setStoredToken, clearStoredToken, apiFetch } from "@/lib/api";
import type { UserResponse } from "@/types/auth";

interface AuthContextType {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async (storedToken: string) => {
    try {
      localStorage.setItem("access_token", storedToken);
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/auth/me`,
        {
          headers: { Authorization: `Bearer ${storedToken}` },
        }
      );
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setToken(storedToken);
      } else {
        clearStoredToken();
      }
    } catch {
      clearStoredToken();
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const stored = getStoredToken();
    if (stored) {
      loadUser(stored);
    } else {
      setIsLoading(false);
    }
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/auth/login`,
      {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      }
    );

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Credenciais inválidas" }));
      throw new Error(err.detail || "Credenciais inválidas");
    }

    const data = await res.json();
    setStoredToken(data.access_token);
    setToken(data.access_token);

    await loadUser(data.access_token);
  };

  const logout = () => {
    clearStoredToken();
    setUser(null);
    setToken(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
