import type { ServiceStatus, RmaStatus, DeliveryStatus, DiscardStatus } from "@/types";

type AnyStatus = ServiceStatus | RmaStatus | DeliveryStatus | DiscardStatus;

const SERVICE_STATUS: Record<ServiceStatus, { label: string; color: string }> = {
  OPEN: { label: "Aberta", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  DIAGNOSING: { label: "Diagnosticando", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  AWAITING_PARTS: { label: "Aguardando Peças", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  IN_REPAIR: { label: "Em Reparo", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  COMPLETED: { label: "Concluída", color: "bg-green-500/10 text-green-400 border-green-500/20" },
  DELIVERED: { label: "Entregue", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  CANCELED: { label: "Cancelada", color: "bg-red-500/10 text-red-400 border-red-500/20" },
};

const RMA_STATUS: Record<RmaStatus, { label: string; color: string }> = {
  PENDING: { label: "Pendente", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  INSPECTING: { label: "Inspecionando", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  APPROVED: { label: "Aprovado", color: "bg-green-500/10 text-green-400 border-green-500/20" },
  REJECTED: { label: "Rejeitado", color: "bg-red-500/10 text-red-400 border-red-500/20" },
  SHIPPED: { label: "Enviado", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  COMPLETED: { label: "Concluído", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
};

const DELIVERY_STATUS: Record<DeliveryStatus, { label: string; color: string }> = {
  PENDING: { label: "Pendente", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  RECEIVED: { label: "Recebido", color: "bg-green-500/10 text-green-400 border-green-500/20" },
  OVERDUE: { label: "Atrasado", color: "bg-red-500/10 text-red-400 border-red-500/20" },
};

const DISCARD_STATUS: Record<DiscardStatus, { label: string; color: string }> = {
  PENDING: { label: "Pendente", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" },
  AUTHORIZED: { label: "Autorizado", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  COMPLETED: { label: "Concluído", color: "bg-green-500/10 text-green-400 border-green-500/20" },
};

const ALL_CONFIGS: Record<string, { label: string; color: string }> = {
  ...SERVICE_STATUS,
  ...RMA_STATUS,
  ...DELIVERY_STATUS,
  ...DISCARD_STATUS,
};

export function StatusBadge({ status }: { status: AnyStatus }) {
  const config = ALL_CONFIGS[status] || { label: status, color: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20" };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
      {config.label}
    </span>
  );
}
