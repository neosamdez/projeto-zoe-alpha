"use client";

import Link from "next/link";
import { AlertTriangle } from "lucide-react";

interface StockAlertProps {
  count: number;
}

export const StockAlert = ({ count }: StockAlertProps) => {
  if (count === 0) return null;

  return (
    <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="p-1.5 bg-amber-500/20 rounded-md">
          <AlertTriangle className="text-amber-400" size={18} />
        </div>
        <p className="text-amber-300 text-sm font-medium">
          {count} {count === 1 ? "item com estoque baixo" : "itens com estoque baixo"}
        </p>
      </div>
      <Link
        href="/products"
        className="text-amber-400 hover:text-amber-300 text-sm font-medium underline underline-offset-2 transition-colors"
      >
        Ver Produtos
      </Link>
    </div>
  );
};
