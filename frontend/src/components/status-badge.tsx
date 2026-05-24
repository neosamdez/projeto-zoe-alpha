import type { ServiceStatus } from "@/types";

const statusConfig: Record<ServiceStatus, { label: string; color: string }> = {
  OPEN: { label: "Aberta", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  DIAGNOSING: { label: "Diagnosticando", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  AWAITING_PARTS: { label: "Aguardando Peças", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  IN_REPAIR: { label: "Em Reparo", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  COMPLETED: { label: "Concluída", color: "bg-green-500/10 text-green-400 border-green-500/20" },
  DELIVERED: { label: "Entregue", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  CANCELED: { label: "Cancelada", color: "bg-red-500/10 text-red-400 border-red-500/20" },
};

export function StatusBadge({ status }: { status: ServiceStatus }) {
  const config = statusConfig[status] || { label: status, color: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20" };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
      {config.label}
    </span>
  );
}
