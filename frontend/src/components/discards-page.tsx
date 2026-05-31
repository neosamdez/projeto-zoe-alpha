"use client";

import { useEffect, useState, useCallback } from "react";
import { getDiscards, createDiscard, authorizeDiscard, completeDiscard, getDiscardReport } from "@/lib/discards";
import type { DiscardRecord, DiscardRecordCreate, DiscardStatus as DS } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Trash2, Plus, ShieldCheck, CheckCircle, AlertTriangle, BarChart3 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";
import { StatusBadge } from "@/components/status-badge";
import { DateFilter } from "@/components/date-filter";

const PAGE_SIZE = 15;

const PRODUCT_TYPES = ["TV", "ARCONDICIONADO", "HHP", "NPC"];
const DISCARD_TYPES = ["TROCA", "DESCARTE"];

export function DiscardsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [discards, setDiscards] = useState<DiscardRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1);
  const [filterYear, setFilterYear] = useState(new Date().getFullYear());
  const [createOpen, setCreateOpen] = useState(false);
  const [report, setReport] = useState<{ product_type: string; discard_type: string; count: number }[]>([]);
  const [reportOpen, setReportOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<DiscardRecordCreate>({ serial: "", product_type: "TV", discard_type: "DESCARTE" });

  const fetchData = useCallback(async () => {
    try {
      const data = await getDiscards(statusFilter || undefined, filterMonth, filterYear);
      setDiscards(data);
    } catch {
      toast.error("Erro ao carregar descartes");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, filterMonth, filterYear]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createDiscard(form);
      toast.success("Descarte registrado");
      setCreateOpen(false);
      setForm({ serial: "", product_type: "TV", discard_type: "DESCARTE" });
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar descarte");
    }
  };

  const handleAuthorize = async (id: string) => {
    if (!confirm("Autorizar este descarte?")) return;
    try {
      await authorizeDiscard(id);
      toast.success("Descarte autorizado");
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao autorizar");
    }
  };

  const handleComplete = async (id: string) => {
    if (!confirm("Concluir este descarte?")) return;
    try {
      await completeDiscard(id);
      toast.success("Descarte concluído");
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao concluir");
    }
  };

  const openReport = async () => {
    try {
      const data = await getDiscardReport();
      setReport(data);
      setReportOpen(true);
    } catch {
      toast.error("Erro ao gerar relatório");
    }
  };

  const totalPages = Math.ceil(discards.length / PAGE_SIZE);
  const paged = discards.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Descartes</h1>
          <p className="text-zinc-400 mt-1">Gestão de Trocas e Descartes Samsung</p>
        </div>
        <div className="flex gap-3">
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg px-3 py-2">
            <option value="">Todos</option>
            <option value="PENDING">Pendente</option>
            <option value="AUTHORIZED">Autorizado</option>
            <option value="COMPLETED">Concluído</option>
          </select>
          <DateFilter month={filterMonth} year={filterYear} onMonthChange={setFilterMonth} onYearChange={setFilterYear} />
          <Button variant="outline" onClick={openReport} className="border-zinc-700 text-zinc-300 hover:bg-zinc-800">
            <BarChart3 className="h-4 w-4 mr-2" /> Relatório
          </Button>
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}>
              <Plus className="h-4 w-4 mr-2" /> Novo Descarte
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800">
              <DialogHeader>
                <DialogTitle className="text-white">Registrar Descarte/Troca</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <Label className="text-zinc-300">Serial *</Label>
                  <Input value={form.serial} onChange={(e) => setForm({ ...form, serial: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-zinc-300">Tipo Produto *</Label>
                    <select value={form.product_type} onChange={(e) => setForm({ ...form, product_type: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2" required>
                      {PRODUCT_TYPES.map((pt) => (<option key={pt} value={pt}>{pt}</option>))}
                    </select>
                  </div>
                  <div>
                    <Label className="text-zinc-300">Tipo Descarte *</Label>
                    <select value={form.discard_type} onChange={(e) => setForm({ ...form, discard_type: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2" required>
                      {DISCARD_TYPES.map((dt) => (<option key={dt} value={dt}>{dt}</option>))}
                    </select>
                  </div>
                </div>
                <div>
                  <Label className="text-zinc-300">Motivo</Label>
                  <Textarea value={form.reason || ""} onChange={(e) => setForm({ ...form, reason: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Registrar</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-amber-500" />
            {discards.length} registro(s)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Serial</TableHead>
                <TableHead className="text-zinc-400">Tipo Produto</TableHead>
                <TableHead className="text-zinc-400">Tipo</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Motivo</TableHead>
                <TableHead className="text-zinc-400">Data</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((rec) => {
                return (
                  <TableRow key={rec.id} className="border-zinc-800">
                    <TableCell className="text-amber-500 font-mono">{rec.serial}</TableCell>
                    <TableCell className="text-zinc-300">{rec.product_type}</TableCell>
                    <TableCell className="text-white">{rec.discard_type}</TableCell>
                <TableCell>
                  <StatusBadge status={rec.status as DS} />
                </TableCell>
                    <TableCell className="text-zinc-400 text-sm max-w-[200px] truncate">{rec.reason || "—"}</TableCell>
                    <TableCell className="text-zinc-400 text-sm">{new Date(rec.created_at).toLocaleDateString("pt-BR")}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {rec.status === "PENDING" && isAdmin && (
                          <Button variant="ghost" size="sm" onClick={() => handleAuthorize(rec.id)} className="text-blue-400 hover:text-blue-300">
                            <ShieldCheck className="h-4 w-4" />
                          </Button>
                        )}
                        {rec.status === "AUTHORIZED" && (
                          <Button variant="ghost" size="sm" onClick={() => handleComplete(rec.id)} className="text-green-400 hover:text-green-300">
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-zinc-500 py-8">Nenhum descarte encontrado.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      <Dialog open={reportOpen} onOpenChange={setReportOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-amber-500" /> Relatório de Descartes
            </DialogTitle>
          </DialogHeader>
          {report.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800">
                  <TableHead className="text-zinc-400">Tipo Produto</TableHead>
                  <TableHead className="text-zinc-400">Tipo Descarte</TableHead>
                  <TableHead className="text-zinc-400">Quantidade</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.map((r, i) => (
                  <TableRow key={i} className="border-zinc-800">
                    <TableCell className="text-white">{r.product_type}</TableCell>
                    <TableCell className="text-zinc-300">{r.discard_type}</TableCell>
                    <TableCell className="text-amber-500 font-mono">{r.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-zinc-500">Nenhum descarte concluído para relatório.</p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
