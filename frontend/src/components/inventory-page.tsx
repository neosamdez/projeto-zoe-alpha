"use client";

import { useEffect, useState, useCallback } from "react";
import { getMovements, createMovement, getInventoryDashboard, getLowStock } from "@/lib/inventory";
import { getProducts } from "@/lib/products";
import type { InventoryMovement, InventoryMovementCreate, InventoryDashboard, Product, MovementType } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PackageSearch, Plus, ArrowDown, ArrowUp, Archive, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

const MOVEMENT_TYPE_LABELS: Record<MovementType, { label: string; color: string }> = {
  IN: { label: "Entrada", color: "bg-green-500/20 text-green-400" },
  OUT: { label: "Saída", color: "bg-red-500/20 text-red-400" },
  RESERVE: { label: "Reserva", color: "bg-orange-500/20 text-orange-400" },
  RELEASE: { label: "Liberação", color: "bg-blue-500/20 text-blue-400" },
  RETURN: { label: "Devolução", color: "bg-purple-500/20 text-purple-400" },
  DISCARD: { label: "Descarte", color: "bg-zinc-500/20 text-zinc-400" },
};

export function InventoryPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [dashboard, setDashboard] = useState<InventoryDashboard | null>(null);
  const [lowStock, setLowStock] = useState<Product[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<InventoryMovementCreate>({ product_id: "", movement_type: "IN", quantity: 1 });

  const fetchData = useCallback(async () => {
    try {
      const [movs, dash, low, prods] = await Promise.all([
        getMovements(),
        getInventoryDashboard(),
        getLowStock(),
        getProducts(),
      ]);
      setMovements(movs);
      setDashboard(dash);
      setLowStock(low);
      setProducts(prods);
    } catch {
      toast.error("Erro ao carregar inventário");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createMovement(form);
      toast.success("Movimentação registrada");
      setCreateOpen(false);
      setForm({ product_id: "", movement_type: "IN", quantity: 1 });
      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar movimentação");
    }
  };

  const totalPages = Math.ceil(movements.length / PAGE_SIZE);
  const paged = movements.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const productMap = new Map(products.map((p) => [p.id, p]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Movimentações</h1>
          <p className="text-zinc-400 mt-1">Controle de Entrada, Saída e Reserva</p>
        </div>
        {isAdmin && (
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}>
              <Plus className="h-4 w-4 mr-2" /> Nova Movimentação
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800">
              <DialogHeader>
                <DialogTitle className="text-white">Registrar Movimentação</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <Label className="text-zinc-300">Produto *</Label>
                  <select value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2" required>
                    <option value="">Selecione...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-zinc-300">Tipo *</Label>
                  <select value={form.movement_type} onChange={(e) => setForm({ ...form, movement_type: e.target.value as MovementType })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2" required>
                    {Object.entries(MOVEMENT_TYPE_LABELS).map(([key, { label }]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-zinc-300">Quantidade *</Label>
                  <Input type="number" min={1} value={form.quantity} onChange={(e) => setForm({ ...form, quantity: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" required />
                </div>
                <div>
                  <Label className="text-zinc-300">Referência</Label>
                  <Input value={form.reference_id || ""} onChange={(e) => setForm({ ...form, reference_id: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" placeholder="order_id, rma_id..." />
                </div>
                <div>
                  <Label className="text-zinc-300">Notas</Label>
                  <Textarea value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Registrar</Button>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {dashboard && (
        <div className="grid grid-cols-5 gap-4">
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="p-4 text-center">
              <Archive className="h-5 w-5 text-amber-500 mx-auto mb-1" />
              <p className="text-2xl font-bold text-white">{dashboard.total_products}</p>
              <p className="text-zinc-500 text-xs">Produtos</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="p-4 text-center">
              <ArrowDown className="h-5 w-5 text-green-400 mx-auto mb-1" />
              <p className="text-2xl font-bold text-white">{dashboard.total_stock}</p>
              <p className="text-zinc-500 text-xs">Estoque Total</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="p-4 text-center">
              <PackageSearch className="h-5 w-5 text-orange-400 mx-auto mb-1" />
              <p className="text-2xl font-bold text-orange-400">{dashboard.total_reserved}</p>
              <p className="text-zinc-500 text-xs">Reservado</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="p-4 text-center">
              <ArrowUp className="h-5 w-5 text-blue-400 mx-auto mb-1" />
              <p className="text-2xl font-bold text-white">{dashboard.total_available}</p>
              <p className="text-zinc-500 text-xs">Disponível</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800">
            <CardContent className="p-4 text-center">
              <AlertTriangle className="h-5 w-5 text-red-400 mx-auto mb-1" />
              <p className="text-2xl font-bold text-red-400">{dashboard.low_stock_count}</p>
              <p className="text-zinc-500 text-xs">Estoque Baixo</p>
            </CardContent>
          </Card>
        </div>
      )}

      {lowStock.length > 0 && (
        <Card className="bg-zinc-900 border-red-900/50">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2 text-sm">
              <AlertTriangle className="h-4 w-4" /> Produtos com Estoque Baixo ({lowStock.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {lowStock.map((p) => (
                <span key={p.id} className="bg-red-500/10 text-red-400 text-xs px-2 py-1 rounded">
                  {p.name} ({p.current_stock}/{p.min_stock})
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <PackageSearch className="h-5 w-5 text-amber-500" />
            {movements.length} movimentação(ões)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Produto</TableHead>
                <TableHead className="text-zinc-400">Tipo</TableHead>
                <TableHead className="text-zinc-400">Qtd</TableHead>
                <TableHead className="text-zinc-400">Referência</TableHead>
                <TableHead className="text-zinc-400">Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((mov) => {
                const prod = productMap.get(mov.product_id);
                const typeInfo = MOVEMENT_TYPE_LABELS[mov.movement_type];
                return (
                  <TableRow key={mov.id} className="border-zinc-800">
                    <TableCell className="text-white">{prod?.name || mov.product_id.slice(0, 8)}</TableCell>
                    <TableCell>
                      <span className={`text-xs px-2 py-1 rounded ${typeInfo.color}`}>{typeInfo.label}</span>
                    </TableCell>
                    <TableCell className="text-white font-mono">{mov.quantity}</TableCell>
                    <TableCell className="text-zinc-400 font-mono text-xs">{mov.reference_id || "—"}</TableCell>
                    <TableCell className="text-zinc-400 text-sm">{new Date(mov.created_at).toLocaleString("pt-BR")}</TableCell>
                  </TableRow>
                );
              })}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-zinc-500 py-8">Nenhuma movimentação registrada.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />
    </div>
  );
}
