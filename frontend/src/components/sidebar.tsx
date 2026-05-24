"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  Package,
  Wrench,
  FileBarChart,
  LogOut,
  Zap,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/leads", label: "Clientes", icon: Users },
  { href: "/orders", label: "Ordens", icon: ClipboardList },
  { href: "/products", label: "Inventário", icon: Package },
  { href: "/technicians", label: "Equipe", icon: Wrench },
  { href: "/reports", label: "Relatórios", icon: FileBarChart },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col">
      <div className="p-6 flex items-center gap-3">
        <div className="p-2 bg-amber-500/10 rounded-lg">
          <Zap className="h-5 w-5 text-amber-500" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">ASI</h1>
          <p className="text-xs text-zinc-500">Amenti Service Intel.</p>
        </div>
      </div>

      <Separator className="bg-zinc-800" />

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
              pathname === item.href
                ? "bg-amber-500/10 text-amber-500 font-medium"
                : "text-zinc-400 hover:text-white hover:bg-zinc-800"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-zinc-800">
        <div className="px-3 py-2 mb-2">
          <p className="text-sm text-white truncate">{user?.full_name || "Operador"}</p>
          <p className="text-xs text-zinc-500 truncate">{user?.email || ""}</p>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start text-zinc-400 hover:text-red-400 hover:bg-red-400/10"
          onClick={logout}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sair
        </Button>
      </div>
    </aside>
  );
}
