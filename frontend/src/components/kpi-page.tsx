"use client";

import { useEffect, useState, useCallback } from "react";
import { getKpiDashboard, getBonusSummary, createOrUpdateMetric } from "@/lib/kpi";
import type { KpiDashboard, KpiBonusSummary, KpiMetricCreate } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Award, Plus, TrendingUp, Clock, Wrench, BarChart3 } from "lucide-react";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from "recharts";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";

const MONTHS = [
  { value: 1, label: "Janeiro" }, { value: 2, label: "Fevereiro" },
  { value: 3, label: "Março" }, { value: 4, label: "Abril" },
  { value: 5, label: "Maio" }, { value: 6, label: "Junho" },
  { value: 7, label: "Julho" }, { value: 8, label: "Agosto" },
  { value: 9, label: "Setembro" }, { value: 10, label: "Outubro" },
  { value: 11, label: "Novembro" }, { value: 12, label: "Dezembro" },
];

const TIER_CONFIG: Record<string, { label: string; color: string }> = {
  DIAMOND: { label: "Diamante", color: "bg-cyan-500/20 text-cyan-400" },
  GOLD: { label: "Ouro", color: "bg-amber-500/20 text-amber-400" },
  SILVER: { label: "Prata", color: "bg-zinc-400/20 text-zinc-300" },
  BRONZE: { label: "Bronze", color: "bg-orange-700/20 text-orange-500" },
};

const RADAR_KEYS: { key: keyof KpiDashboard; label: string }[] = [
  { key: "avg_nps", label: "NPS" },
  { key: "avg_first_visit", label: "1ª Visita" },
  { key: "avg_ltp_mx", label: "LTP MX" },
  { key: "avg_crrr_mx", label: "CRRR MX" },
  { key: "avg_eco_repair", label: "Eco Repair" },
  { key: "avg_ssr", label: "SSR" },
{ key: "avg_gd_ta", label: "GD TA" },
];

const METRIC_FIELDS: { key: keyof KpiMetricCreate; label: string; suffix: string }[] = [
  { key: "nps_score", label: "NPS", suffix: "%" },
  { key: "first_visit_rate", label: "1ª Visita", suffix: "%" },
  { key: "waiting_time_avg", label: "Tempo Espera", suffix: "min" },
  { key: "oow_hq_rate", label: "OOW HQ", suffix: "%" },
  { key: "ow_repair_approved", label: "OW Repair Aprov.", suffix: "%" },
  { key: "ltp_mx_rate", label: "LTP MX", suffix: "%" },
  { key: "crrr_mx_rate", label: "CRRR MX", suffix: "%" },
  { key: "eco_repair_rate", label: "Eco Repair", suffix: "%" },
  { key: "ssr_rate", label: "SSR", suffix: "%" },
  { key: "gd_ta_rate", label: "GD TA", suffix: "%" },
  { key: "atendimento_10min", label: "Atend. 10min", suffix: "%" },
  { key: "meta_vendas", label: "Meta Vendas", suffix: "%" },
];

const emptyForm: KpiMetricCreate = {
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear(),
  nps_score: 0,
  first_visit_rate: 0,
  waiting_time_avg: 0,
  oow_hq_rate: 0,
  ow_repair_approved: 0,
  ltp_mx_rate: 0,
  crrr_mx_rate: 0,
  eco_repair_rate: 0,
  ssr_rate: 0,
  gd_ta_rate: 0,
  atendimento_10min: 0,
  meta_vendas: 0,
};

export function KpiPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [dashboard, setDashboard] = useState<KpiDashboard | null>(null);
  const [bonusSummary, setBonusSummary] = useState<KpiBonusSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState<KpiMetricCreate>({ ...emptyForm });

  const fetchData = useCallback(async () => {
    try {
      const [dash, bonus] = await Promise.all([
        getKpiDashboard(month, year),
        getBonusSummary(month, year),
      ]);
      setDashboard(dash);
      setBonusSummary(bonus);
    } catch {
      toast.error("Erro ao carregar KPIs");
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const radarData = dashboard
    ? RADAR_KEYS.map(({ key, label }) => ({
        metric: label,
        value: Number((dashboard as unknown as Record<string, unknown>)[key]) || 0,
        fullMark: 100,
      }))
    : [];

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createOrUpdateMetric({ ...form, month, year });
      toast.success("Métrica KPI salva");
      setCreateOpen(false);
      setForm({ ...emptyForm });
      fetchData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro ao salvar métrica";
      toast.error(msg);
    }
  };

  const avgCards = dashboard
    ? [
        { icon: TrendingUp, label: "NPS Médio", value: Number(dashboard.avg_nps), suffix: "%" },
        { icon: Wrench, label: "1ª Visita Médio", value: Number(dashboard.avg_first_visit), suffix: "%" },
        { icon: Clock, label: "Espera Média", value: Number(dashboard.avg_waiting_time), suffix: "min" },
        { icon: BarChart3, label: "Técnicos", value: dashboard.technicians.length, suffix: "" },
      ]
    : [];

  const totalBonus = bonusSummary.reduce((sum, b) => sum + Number(b.bonus_value), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Award className="h-8 w-8 text-amber-500 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">KPI / P4P</h1>
          <p className="text-zinc-400 mt-1">Performance e Bonificação Técnica</p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={month}
            onChange={(e) => { setMonth(Number(e.target.value)); setLoading(true); }}
            className="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg px-3 py-2"
          >
            {MONTHS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
          <Input
            type="number"
            min={2020}
            max={2100}
            value={year}
            onChange={(e) => { setYear(Number(e.target.value)); setLoading(true); }}
            className="w-24 bg-zinc-800 border-zinc-700 text-white"
          />
          {isAdmin && (
            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
              <DialogTrigger render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}>
                <Plus className="h-4 w-4 mr-2" /> Nova Métrica
              </DialogTrigger>
              <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-white">Registrar Métrica KPI</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreate} className="space-y-4">
                  <div>
                    <Label className="text-zinc-300">Técnico (vazio = geral)</Label>
                    <Input
                      value={form.technician_id || ""}
                      onChange={(e) => setForm({ ...form, technician_id: e.target.value || undefined })}
                      className="bg-zinc-800 border-zinc-700 text-white"
                      placeholder="ID do técnico (opcional)"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {METRIC_FIELDS.map(({ key, label, suffix }) => (
                      <div key={key}>
                        <Label className="text-zinc-300 text-xs">{label}</Label>
                        <div className="relative">
                          <Input
                            type="number"
                            step="0.1"
                            min={0}
                            max={suffix === "%" ? 100 : undefined}
                            value={(form as unknown as Record<string, unknown>)[key] as number}
                            onChange={(e) => setForm({ ...form, [key]: parseFloat(e.target.value) || 0 })}
                            className="bg-zinc-800 border-zinc-700 text-white pr-10"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 text-xs">
                            {suffix}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">
                    Salvar Métrica
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {avgCards.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          {avgCards.map(({ icon: Icon, label, value, suffix }) => (
            <Card key={label} className="bg-zinc-900 border-zinc-800">
              <CardContent className="p-4 text-center">
                <Icon className="h-5 w-5 text-amber-500 mx-auto mb-1" />
                <p className="text-2xl font-bold text-white">
                  {typeof value === "number" && suffix === "%" ? value.toFixed(1) : value}
                  {suffix && <span className="text-sm text-zinc-500 ml-1">{suffix}</span>}
                </p>
                <p className="text-zinc-500 text-xs">{label}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {radarData.length > 0 && dashboard!.technicians.length > 0 && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-amber-500" /> Radar de Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#3f3f46" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#71717a", fontSize: 10 }} />
                <Radar
                  name="Média do Time"
                  dataKey="value"
                  stroke="#f59e0b"
                  fill="#f59e0b"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
                <Legend wrapperStyle={{ color: "#a1a1aa" }} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-500" /> Bonificação P4P
            {totalBonus > 0 && (
              <span className="text-amber-400 text-sm font-normal ml-auto">
                Total: R$ {totalBonus.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {bonusSummary.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800">
                  <TableHead className="text-zinc-400">Técnico</TableHead>
                  <TableHead className="text-zinc-400 text-center">Pontos</TableHead>
                  <TableHead className="text-zinc-400 text-center">Nível</TableHead>
                  <TableHead className="text-zinc-400 text-right">Bônus</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bonusSummary.map((b) => {
                  const tc = TIER_CONFIG[b.bonus_tier || ""] || { label: "—", color: "bg-zinc-700/20 text-zinc-500" };
                  return (
                    <TableRow key={b.technician_id} className="border-zinc-800">
                      <TableCell className="text-white font-medium">{b.technician_name}</TableCell>
                      <TableCell className="text-center">
                        <span className="text-amber-500 font-mono font-bold text-lg">{b.total_points}</span>
                        <span className="text-zinc-500 text-xs ml-1">/100</span>
                      </TableCell>
                      <TableCell className="text-center">
                        <span className={`text-xs px-2 py-1 rounded ${tc.color}`}>{tc.label}</span>
                      </TableCell>
                      <TableCell className="text-right text-green-400 font-mono">
                        R$ {Number(b.bonus_value).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          ) : (
            <p className="text-zinc-500 text-center py-8">
              Nenhuma métrica KPI registrada para {MONTHS.find((m) => m.value === month)?.label} {year}.
            </p>
          )}
        </CardContent>
      </Card>

      {dashboard && dashboard.technicians.length > 0 && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Wrench className="h-5 w-5 text-amber-500" /> Detalhamento por Técnico
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-zinc-800">
                    <TableHead className="text-zinc-400">Técnico</TableHead>
                    <TableHead className="text-zinc-400 text-center">NPS</TableHead>
                    <TableHead className="text-zinc-400 text-center">1ª Visita</TableHead>
                    <TableHead className="text-zinc-400 text-center">LTP MX</TableHead>
                    <TableHead className="text-zinc-400 text-center">CRRR MX</TableHead>
                    <TableHead className="text-zinc-400 text-center">Eco Repair</TableHead>
                    <TableHead className="text-zinc-400 text-center">SSR</TableHead>
                    <TableHead className="text-zinc-400 text-center">Pts</TableHead>
                    <TableHead className="text-zinc-400 text-center">Nível</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboard.technicians.map((t) => {
                    const tc = TIER_CONFIG[t.bonus_tier || ""] || { label: "—", color: "bg-zinc-700/20 text-zinc-500" };
                    return (
                      <TableRow key={t.id} className="border-zinc-800">
                        <TableCell className="text-white font-medium">
                          {t.technician_id ? "ID: " + t.technician_id.slice(0, 8) + "…" : "Geral"}
                        </TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.nps_score).toFixed(1)}%</TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.first_visit_rate).toFixed(1)}%</TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.ltp_mx_rate).toFixed(1)}%</TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.crrr_mx_rate).toFixed(1)}%</TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.eco_repair_rate).toFixed(1)}%</TableCell>
                        <TableCell className="text-center text-zinc-300">{Number(t.ssr_rate).toFixed(1)}%</TableCell>
                        <TableCell className="text-center">
                          <span className="text-amber-500 font-mono font-bold">{t.total_points}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className={`text-xs px-2 py-1 rounded ${tc.color}`}>{tc.label}</span>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
