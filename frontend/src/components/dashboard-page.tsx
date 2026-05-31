"use client";

import { useEffect, useState } from "react";
import { getOrdersStats, getOrdersAnalytics } from "@/lib/orders";
import { getRmas } from "@/lib/rma";
import { getLowStock } from "@/lib/inventory";
import type { OrdersStats, VolumeItem, StatusItem, RmaRequest, Product } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StockAlert } from "@/components/ui/stock-alert";
import {
  ClipboardList,
  CircleDot,
  Wrench,
  CheckCircle2,
  DollarSign,
  TrendingUp,
  Package,
  BarChart3,
  RotateCcw,
  AlertTriangle,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const PIE_COLORS: Record<string, string> = {
  OPEN: "#3b82f6",
  DIAGNOSING: "#eab308",
  AWAITING_PARTS: "#f97316",
  IN_REPAIR: "#a855f7",
  COMPLETED: "#22c55e",
  DELIVERED: "#10b981",
  CANCELED: "#ef4444",
};

const PIE_LABELS: Record<string, string> = {
  OPEN: "Aberta",
  DIAGNOSING: "Diagnosticando",
  AWAITING_PARTS: "Aguard. Peças",
  IN_REPAIR: "Em Reparo",
  COMPLETED: "Concluída",
  DELIVERED: "Entregue",
  CANCELED: "Cancelada",
};

function SkeletonCard() {
  return (
    <Card className="bg-zinc-900 border-zinc-800 animate-pulse">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="h-4 w-24 bg-zinc-800 rounded" />
        <div className="h-4 w-4 bg-zinc-800 rounded" />
      </CardHeader>
      <CardContent>
        <div className="h-7 w-20 bg-zinc-800 rounded" />
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const [stats, setStats] = useState<OrdersStats | null>(null);
  const [analytics, setAnalytics] = useState<{ volume: VolumeItem[]; distribution: StatusItem[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [pendingRmas, setPendingRmas] = useState<RmaRequest[]>([]);
  const [lowStockProducts, setLowStockProducts] = useState<Product[]>([]);

  useEffect(() => {
    Promise.all([
      getOrdersStats().catch(() => null),
      getOrdersAnalytics(30).catch(() => null),
      getRmas("PENDING").catch(() => []),
      getLowStock().catch(() => []),
    ]).then(([s, a, rmas, lowStock]) => {
      setStats(s);
      setAnalytics(a);
      setPendingRmas(rmas);
      setLowStockProducts(lowStock);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-zinc-400 mt-1">Visão tática e operacional da Cidadela</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center text-zinc-500 py-20">
        Nenhuma estatística disponível. Crie sua primeira Ordem de Serviço.
      </div>
    );
  }

  const statCards = [
    { title: "Total OS", value: stats.total, icon: ClipboardList, color: "text-blue-400" },
    { title: "Abertas", value: stats.open, icon: CircleDot, color: "text-amber-400" },
    { title: "Em Reparo", value: stats.repairing, icon: Wrench, color: "text-purple-400" },
    { title: "Concluídas", value: stats.completed, icon: CheckCircle2, color: "text-green-400" },
    {
      title: "Receita Projetada",
      value: `R$ ${Number(stats.projected_revenue).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: "text-blue-400",
    },
    {
      title: "Receita Realizada",
      value: `R$ ${Number(stats.realized_revenue).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
      icon: TrendingUp,
      color: "text-green-400",
    },
    {
      title: "Custo de Peças",
      value: `R$ ${Number(stats.total_parts_cost).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
      icon: Package,
      color: "text-orange-400",
    },
    {
      title: "Lucro Líquido",
      value: `R$ ${Number(stats.realized_net_profit).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
      icon: BarChart3,
      color: "text-emerald-400",
    },
  ];

  const pieData = (analytics?.distribution || []).map((d) => ({
name: PIE_LABELS[d.status] || d.status,
      value: d.count,
      color: PIE_COLORS[d.status] || "#71717a",
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-zinc-400 mt-1">Visão tática e operacional da Cidadela</p>
        <StockAlert count={lowStockProducts.length} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <Card key={card.title} className="bg-zinc-900 border-zinc-800">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400">
                {card.title}
              </CardTitle>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-white">{card.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {analytics && analytics.volume.length > 0 && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white">Volume de OS (Últimos 30 dias)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={analytics.volume}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#71717a", fontSize: 11 }}
                    tickFormatter={(v: string) => v.slice(5)}
                  />
                  <YAxis tick={{ fill: "#71717a", fontSize: 11 }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#18181b",
                      border: "1px solid #27272a",
                      borderRadius: 8,
                      color: "#fff",
                    }}
                    labelFormatter={(v: string) => `Data: ${v}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    dot={{ fill: "#f59e0b", r: 3 }}
                    name="OS"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {pieData.length > 0 && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle className="text-white">Distribuição por Status</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#18181b",
                      border: "1px solid #27272a",
                      borderRadius: 8,
                      color: "#fff",
                    }}
                  />
                  <Legend
                    formatter={(value: string) => (
                      <span style={{ color: "#a1a1aa", fontSize: 12 }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2 text-sm">
              <RotateCcw className="h-4 w-4 text-amber-500" />
              RMA Pendentes ({pendingRmas.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {pendingRmas.length === 0 ? (
              <p className="text-zinc-500 text-sm">Nenhum RMA pendente</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {pendingRmas.slice(0, 8).map((rma) => (
                  <span key={rma.id} className="bg-amber-500/10 text-amber-400 text-xs px-2 py-1 rounded font-mono">
                    {rma.protocol}
                  </span>
                ))}
                {pendingRmas.length > 8 && <span className="text-zinc-500 text-xs">+{pendingRmas.length - 8} mais</span>}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2 text-sm">
              <AlertTriangle className="h-4 w-4 text-red-400" />
              Estoque Baixo ({lowStockProducts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {lowStockProducts.length === 0 ? (
              <p className="text-zinc-500 text-sm">Nenhum produto com estoque baixo</p>
            ) : (
              <div className="space-y-2">
                {lowStockProducts.slice(0, 5).map((p) => (
                  <div key={p.id} className="flex items-center justify-between">
                    <span className="text-white text-sm">{p.name}</span>
                    <span className="text-red-400 text-xs font-mono">{p.current_stock}/{p.min_stock}</span>
                  </div>
                ))}
                {lowStockProducts.length > 5 && <span className="text-zinc-500 text-xs">+{lowStockProducts.length - 5} mais</span>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {stats.technician_ranking && stats.technician_ranking.length > 0 && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">Ranking de Técnicos — Lucro</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.technician_ranking.map((tech, idx) => (
                <div key={tech.technician_id} className="flex items-center justify-between py-2 border-b border-zinc-800 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-amber-500 font-bold w-6">{idx + 1}.</span>
                    <span className="text-white">{tech.name}</span>
                  </div>
                  <span className="text-emerald-400 font-semibold">
                    R$ {Number(tech.profit).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

