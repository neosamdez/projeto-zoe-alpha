"use client";

import { useEffect, useState, useCallback } from "react";
import { getDeliveries, createDelivery, receiveDelivery, getOverdue, markOverdue } from "@/lib/deliveries";
import type { DeliveryPending, DeliveryPendingCreate, DeliveryStatus as DS } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Truck, Plus, AlertTriangle, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";
import { StatusBadge } from "@/components/status-badge";
import { DateFilter } from "@/components/date-filter";

const PAGE_SIZE = 15;

export function DeliveriesPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [deliveries, setDeliveries] = useState<DeliveryPending[]>([]);
  const [overdue, setOverdue] = useState<DeliveryPending[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1);
  const [filterYear, setFilterYear] = useState(new Date().getFullYear());
  const [createOpen, setCreateOpen] = useState(false);
  const [receiveId, setReceiveId] = useState<string | null>(null);
  const [receiveNotes, setReceiveNotes] = useState("");
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<DeliveryPendingCreate>({ delivery_number: "", pending_qty: 0, reference_date: new Date().toISOString().split("T")[0] });

  const fetchData = useCallback(async () => {
    try {
      const [deliv, over] = await Promise.all([
        getDeliveries(statusFilter || undefined, filterMonth, filterYear),
        getOverdue(),
      ]);
      setDeliveries(deliv);
      setOverdue(over);
    } catch {
      toast.error("Erro ao carregar deliveries");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, filterMonth, filterYear]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createDelivery(form);
      toast.success("Delivery registrado");
      setCreateOpen(false);
      setForm({ delivery_number: "", pending_qty: 0, reference_date: new Date().toISOString().split("T")[0] });
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar delivery");
    }
  };

  const handleReceive = async () => {
    if (!receiveId) return;
    try {
      await receiveDelivery(receiveId, undefined, receiveNotes || undefined);
      toast.success("Delivery recebido");
      setReceiveId(null);
      setReceiveNotes("");
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao receber delivery");
    }
  };

  const handleMarkOverdue = async () => {
    if (!confirm("Marcar deliveries pendentes como atrasados?")) return;
    try {
      const result = await markOverdue();
      toast.success(result.message);
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao marcar atrasados");
    }
  };

  const totalPages = Math.ceil(deliveries.length / PAGE_SIZE);
  const paged = deliveries.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Entregas</h1>
          <p className="text-zinc-400 mt-1">Controle de Deliveries Pendentes</p>
        </div>
        <div className="flex gap-3">
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg px-3 py-2">
            <option value="">Todos</option>
            <option value="PENDING">Pendente</option>
            <option value="RECEIVED">Recebido</option>
            <option value="OVERDUE">Atrasado</option>
</select>
      <DateFilter month={filterMonth} year={filterYear} onMonthChange={setFilterMonth} onYearChange={setFilterYear} />
      {isAdmin && (
            <Button variant="outline" onClick={handleMarkOverdue} className="border-red-700 text-red-400 hover:bg-red-500/10">
              <AlertTriangle className="h-4 w-4 mr-2" /> Marcar Atrasados
            </Button>
          )}
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}>
              <Plus className="h-4 w-4 mr-2" /> Novo Delivery
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800">
              <DialogHeader>
                <DialogTitle className="text-white">Registrar Delivery</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <Label className="text-zinc-300">Nº Delivery *</Label>
                  <Input value={form.delivery_number} onChange={(e) => setForm({ ...form, delivery_number: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-zinc-300">Qtd Pendente</Label>
                    <Input type="number" min={0} value={form.pending_qty} onChange={(e) => setForm({ ...form, pending_qty: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
                  </div>
                  <div>
                    <Label className="text-zinc-300">Data Referência *</Label>
                    <Input type="date" value={form.reference_date} onChange={(e) => setForm({ ...form, reference_date: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" required />
                  </div>
                </div>
                <div>
                  <Label className="text-zinc-300">Código Produto</Label>
                  <Input value={form.product_code || ""} onChange={(e) => setForm({ ...form, product_code: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <div>
                  <Label className="text-zinc-300">Notas</Label>
                  <Textarea value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Registrar</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {overdue.length > 0 && (
        <Card className="bg-zinc-900 border-red-900/50">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2 text-sm">
              <AlertTriangle className="h-4 w-4" /> {overdue.length} delivery(ies) atrasado(s)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {overdue.slice(0, 10).map((d) => (
                <span key={d.id} className="bg-red-500/10 text-red-400 text-xs px-2 py-1 rounded">
                  {d.delivery_number} — {d.pending_qty} un.
                </span>
              ))}
              {overdue.length > 10 && <span className="text-zinc-500 text-xs">+{overdue.length - 10} mais</span>}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Truck className="h-5 w-5 text-amber-500" />
            {deliveries.length} delivery(ies)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Nº Delivery</TableHead>
                <TableHead className="text-zinc-400">Produto</TableHead>
                <TableHead className="text-zinc-400">Qtd</TableHead>
                <TableHead className="text-zinc-400">Data Ref.</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Recebido</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((del) => {
                return (
                  <TableRow key={del.id} className="border-zinc-800">
                    <TableCell className="text-amber-500 font-mono">{del.delivery_number}</TableCell>
                    <TableCell className="text-zinc-300">{del.product_code || "—"}</TableCell>
                    <TableCell className="text-white">{del.pending_qty}</TableCell>
                    <TableCell className="text-zinc-300 text-sm">{new Date(del.reference_date).toLocaleDateString("pt-BR")}</TableCell>
                <TableCell>
                  <StatusBadge status={del.status as DS} />
                </TableCell>
                    <TableCell className="text-zinc-300 text-sm">{del.received_date ? new Date(del.received_date).toLocaleDateString("pt-BR") : "—"}</TableCell>
                    <TableCell>
                      {del.status === "PENDING" && (
                        <Button variant="ghost" size="sm" onClick={() => setReceiveId(del.id)} className="text-green-400 hover:text-green-300">
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-zinc-500 py-8">Nenhum delivery encontrado.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      <Dialog open={!!receiveId} onOpenChange={() => setReceiveId(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white">Receber Delivery</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-zinc-300">Notas (opcional)</Label>
              <Textarea value={receiveNotes} onChange={(e) => setReceiveNotes(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleReceive} className="bg-green-600 hover:bg-green-700 text-white flex-1">Confirmar Recebimento</Button>
              <Button variant="outline" onClick={() => setReceiveId(null)} className="border-zinc-700 text-zinc-300">Cancelar</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
