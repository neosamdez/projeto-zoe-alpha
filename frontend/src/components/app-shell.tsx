"use client";

import { useRequireAuth } from "@/hooks/use-require-auth";
import { Sidebar } from "@/components/sidebar";
import { Loader2 } from "lucide-react";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isLoading } = useRequireAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <Loader2 className="h-8 w-8 text-amber-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      <Sidebar />
      <main className="ml-64 p-8">{children}</main>
    </div>
  );
}
