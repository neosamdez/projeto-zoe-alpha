"use client";

import { useEffect, useState, useCallback } from "react";
import { getOrders, updateOrderStatus, getOrderEvents, getOrderParts, addOrderPart, removeOrderPart, assignTechnician, updateOrderValue, updateOrder, addOrderNote, deleteOrder, getOrdersStats, getOrdersAnalytics } from "@/lib/orders";
import { getTechnicians } from "@/lib/technicians";
import { getProducts } from "@/lib/products";
import { useAuth } from "@/contexts/auth-context";
import type { ServiceOrder, ServiceStatus, OrderEvent, OrderPart, Technician, Product } from "@/types";
import { StatusBadge } from "@/components/status-badge";
import { Combobox, type ComboboxItem } from "@/components/combobox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Search, ClipboardList, ArrowRight, Clock, Package, UserCheck, Plus, Trash2, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

const STATUS_FLOW: Record<ServiceStatus, ServiceStatus[]> = {
  OPEN: ["DIAGNOSING", "CANCELED"],
  DIAGNOSING: ["AWAITING_PARTS", "IN_REPAIR", "CANCELED"],
  AWAITING_PARTS: ["IN_REPAIR", "CANCELED"],
  IN_REPAIR: ["COMPLETED", "CANCELED"],
  COMPLETED: ["DELIVERED"],
  DELIVERED: [],
  CANCELED: [],
};

const EVENT_COLORS: Record<string, string> = {
  CREATED: "bg-green-500/10 text-green-400 border-green-500/20",
  STATUS_CHANGED: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  TECH_ASSIGNED: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  NOTE_ADDED: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  VALUE_UPDATED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  ORDER_UPDATED: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  ORDER_DELETED: "bg-red-500/10 text-red-400 border-red-500/20",
};

const EVENT_LABELS: Record<string, string> = {
  CREATED: "Criação",
  STATUS_CHANGED: "Status",
  TECH_ASSIGNED: "Técnico",
  NOTE_ADDED: "Nota",
  VALUE_UPDATED: "Valor",
  ORDER_UPDATED: "Edição",
  ORDER_DELETED: "Remoção",
};

export function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [detailOrder, setDetailOrder] = useState<ServiceOrder | null>(null);

  const [events, setEvents] = useState<OrderEvent[]>([]);
  const [parts, setParts] = useState<OrderPart[]>([]);
  const [detailTab, setDetailTab] = useState("geral");

  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedTechId, setSelectedTechId] = useState("");
  const [assigning, setAssigning] = useState(false);

  const [addPartProductId, setAddPartProductId] = useState("");
  const [addPartQty, setAddPartQty] = useState(1);
  const [addingPart, setAddingPart] = useState(false);

  const [editValue, setEditValue] = useState("");
  const [savingValue, setSavingValue] = useState(false);

  const [noteContent, setNoteContent] = useState("");
  const [addingNote, setAddingNote] = useState(false);

  const [editDeviceInfo, setEditDeviceInfo] = useState("");
  const [editTechNotes, setEditTechNotes] = useState("");
  const [editingFields, setEditingFields] = useState(false);
  const [savingFields, setSavingFields] = useState(false);
  const [page, setPage] = useState(1);

  const fetchOrders = useCallback(async () => {
    try {
      const data = await getOrders();
      setOrders(data);
    } catch {
      toast.error("Erro ao carregar ordens");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const fetchDetailData = async (orderId: string) => {
    try {
      const [evts, pts] = await Promise.all([
        getOrderEvents(orderId),
        getOrderParts(orderId),
      ]);
      setEvents(evts);
      setParts(pts);
    } catch {
      toast.error("Erro ao carregar detalhes");
    }
  };

  const fetchSupportData = async () => {
    try {
      const [techs, prods] = await Promise.all([
        getTechnicians(true),
        getProducts(),
      ]);
      setTechnicians(techs);
      setProducts(prods);
    } catch {}
  };

  const openDetail = (order: ServiceOrder) => {
    setDetailOrder(order);
    setDetailTab("geral");
    setSelectedTechId("");
    setAddPartProductId("");
    setAddPartQty(1);
    setEditValue("");
    setNoteContent("");
    setEditDeviceInfo("");
    setEditTechNotes("");
    setEditingFields(false);
    fetchDetailData(order.id);
    fetchSupportData();
  };

  const handleStatusUpdate = async (orderId: string, newStatus: ServiceStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      toast.success(`Status atualizado para ${newStatus}`);
      fetchOrders();
      if (detailOrder?.id === orderId) {
        const fresh = orders.find((o) => o.id === orderId);
        if (fresh) setDetailOrder({ ...fresh, status: newStatus });
        fetchDetailData(orderId);
      }
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar status");
    }
  };

  const handleAssignTech = async () => {
    if (!detailOrder || !selectedTechId) return;
    setAssigning(true);
    try {
      await assignTechnician(detailOrder.id, selectedTechId);
      toast.success("Técnico atribuído com sucesso");
      fetchOrders();
      fetchDetailData(detailOrder.id);
      setSelectedTechId("");
    } catch (err: any) {
      toast.error(err.message || "Erro ao atribuir técnico");
    } finally {
      setAssigning(false);
    }
  };

  const handleRemoveTech = async () => {
    if (!detailOrder) return;
    setAssigning(true);
    try {
      await assignTechnician(detailOrder.id, null);
      toast.success("Técnico removido");
      fetchOrders();
      fetchDetailData(detailOrder.id);
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover técnico");
    } finally {
      setAssigning(false);
    }
  };

  const handleAddPart = async () => {
    if (!detailOrder || !addPartProductId) return;
    setAddingPart(true);
    try {
      await addOrderPart(detailOrder.id, { product_id: addPartProductId, quantity: addPartQty });
      toast.success("Insumo adicionado à OS");
      fetchDetailData(detailOrder.id);
      setAddPartProductId("");
      setAddPartQty(1);
    } catch (err: any) {
      toast.error(err.message || "Erro ao adicionar insumo");
    } finally {
      setAddingPart(false);
    }
  };

  const handleRemovePart = async (partId: string) => {
    try {
      await removeOrderPart(partId);
      toast.success("Insumo removido");
      fetchDetailData(detailOrder!.id);
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover insumo");
    }
  };

  const handleSaveValue = async () => {
    if (!detailOrder) return;
    const val = parseFloat(editValue);
    if (isNaN(val) || val < 0) {
      toast.error("Valor inválido");
      return;
    }
    setSavingValue(true);
    try {
      const updated = await updateOrderValue(detailOrder.id, val);
      setDetailOrder(updated);
      toast.success("Valor do serviço atualizado");
      fetchOrders();
      fetchDetailData(detailOrder.id);
      setEditValue("");
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar valor");
    } finally {
      setSavingValue(false);
    }
  };

  const handleAddNote = async () => {
    if (!detailOrder || !noteContent.trim()) return;
    setAddingNote(true);
    try {
      await addOrderNote(detailOrder.id, noteContent.trim());
      toast.success("Nota adicionada");
      fetchDetailData(detailOrder.id);
      setNoteContent("");
    } catch (err: any) {
      toast.error(err.message || "Erro ao adicionar nota");
    } finally {
      setAddingNote(false);
    }
  };

  const handleSaveFields = async () => {
    if (!detailOrder) return;
    setSavingFields(true);
    try {
      const data: { device_info?: string; technical_notes?: string } = {};
      if (editDeviceInfo) data.device_info = editDeviceInfo;
      if (editTechNotes !== undefined) data.technical_notes = editTechNotes;
      const updated = await updateOrder(detailOrder.id, data);
      setDetailOrder(updated);
      toast.success("Dados da OS atualizados");
      fetchOrders();
      fetchDetailData(detailOrder.id);
      setEditingFields(false);
      setEditDeviceInfo("");
      setEditTechNotes("");
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar OS");
    } finally {
      setSavingFields(false);
    }
  };

  const handleDeleteOrder = async () => {
    if (!detailOrder) return;
    if (!confirm(`Remover OS ${detailOrder.protocol}? Estoque reservado será estornado.`)) return;
    try {
      await deleteOrder(detailOrder.id);
      toast.success("OS removida com sucesso");
      setDetailOrder(null);
      fetchOrders();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover OS");
    }
  };

  const techItems: ComboboxItem[] = technicians.map((t) => ({
    value: t.id,
    label: `${t.name}${t.specialization ? ` — ${t.specialization}` : ""}`,
  }));

  const productItems: ComboboxItem[] = products.map((p) => ({
    value: p.id,
    label: `${p.name} (Estoque: ${p.current_stock - p.reserved_stock})`,
  }));

  const filtered = orders.filter((o) => {
    const matchStatus = statusFilter === "ALL" || o.status === statusFilter;
    const matchSearch =
      !search ||
      o.protocol.toLowerCase().includes(search.toLowerCase()) ||
      o.lead_name?.toLowerCase().includes(search.toLowerCase()) ||
      o.device_info.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Ordens de Serviço</h1>
        <p className="text-zinc-400 mt-1">Gestão e acompanhamento de OS</p>
      </div>

      <div className="flex gap-4 items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
          <Input
            placeholder="Buscar por protocolo, cliente ou dispositivo..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-10 bg-zinc-900 border-zinc-800 text-white"
          />
        </div>
      </div>

      <Tabs value={statusFilter} onValueChange={setStatusFilter}>
        <TabsList className="bg-zinc-900 border border-zinc-800">
          <TabsTrigger value="ALL" className="data-[state=active]:bg-amber-500 data-[state=active]:text-black">Todas</TabsTrigger>
          <TabsTrigger value="OPEN">Abertas</TabsTrigger>
          <TabsTrigger value="IN_REPAIR">Em Reparo</TabsTrigger>
          <TabsTrigger value="COMPLETED">Concluídas</TabsTrigger>
          <TabsTrigger value="DELIVERED">Entregues</TabsTrigger>
        </TabsList>
      </Tabs>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-amber-500" />
            {filtered.length} ordem(ns) — exibindo {paged.length} de {filtered.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Protocolo</TableHead>
                <TableHead className="text-zinc-400">Cliente</TableHead>
                <TableHead className="text-zinc-400">Dispositivo</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Técnico</TableHead>
                <TableHead className="text-zinc-400">Valor</TableHead>
                <TableHead className="text-zinc-400">Data</TableHead>
                <TableHead className="text-zinc-400"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((order) => (
                <TableRow key={order.id} className="border-zinc-800">
                  <TableCell className="text-amber-500 font-mono font-semibold">{order.protocol}</TableCell>
                  <TableCell className="text-white">{order.lead_name || "—"}</TableCell>
                  <TableCell className="text-zinc-300 max-w-48 truncate">{order.device_info}</TableCell>
                  <TableCell><StatusBadge status={order.status} /></TableCell>
                  <TableCell className="text-zinc-400">{order.technician?.name || "—"}</TableCell>
                  <TableCell className="text-white">R$ {Number(order.total_value).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                  <TableCell className="text-zinc-500">{new Date(order.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => openDetail(order)} className="text-zinc-400 hover:text-white">
                      Detalhes
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-zinc-500 py-8">Nenhuma ordem encontrada</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      <Dialog open={!!detailOrder} onOpenChange={() => setDetailOrder(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <span className="text-amber-500 font-mono">{detailOrder?.protocol}</span>
            </DialogTitle>
          </DialogHeader>
          {detailOrder && (
            <Tabs value={detailTab} onValueChange={setDetailTab}>
              <TabsList className="bg-zinc-800 border border-zinc-700 w-full">
                <TabsTrigger value="geral" className="flex-1 data-[state=active]:bg-amber-500 data-[state=active]:text-black">Geral</TabsTrigger>
                <TabsTrigger value="timeline" className="flex-1 data-[state=active]:bg-amber-500 data-[state=active]:text-black">
                  <Clock className="h-3 w-3 mr-1" /> Timeline
                </TabsTrigger>
                <TabsTrigger value="insumos" className="flex-1 data-[state=active]:bg-amber-500 data-[state=active]:text-black">
                  <Package className="h-3 w-3 mr-1" /> Insumos
                </TabsTrigger>
              </TabsList>

              <TabsContent value="geral" className="mt-4 space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-zinc-500">Cliente</p>
                    <p className="text-white">{detailOrder.lead_name || "—"}</p>
                  </div>
                  <div>
                    <p className="text-zinc-500">Status</p>
                    <StatusBadge status={detailOrder.status} />
                  </div>
                <div>
                  <p className="text-zinc-500">Dispositivo</p>
                  {editingFields ? (
                    <Input value={editDeviceInfo} onChange={(e) => setEditDeviceInfo(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white text-sm h-8 mt-1" />
                  ) : (
                    <p className="text-white">{detailOrder.device_info}</p>
                  )}
                </div>
                  <div>
                    <p className="text-zinc-500">Técnico</p>
                    {detailOrder.technician ? (
                      <div className="flex items-center gap-2">
                        <span className="text-white">{detailOrder.technician.name}</span>
                        <Button variant="ghost" size="sm" onClick={handleRemoveTech} disabled={assigning} className="text-red-400 hover:text-red-300 h-6 px-2">
                          Remover
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Combobox
                          items={techItems}
                          value={selectedTechId}
                          onValueChange={setSelectedTechId}
                          placeholder="Atribuir técnico..."
                          searchPlaceholder="Buscar técnico..."
                          emptyMessage="Nenhum técnico encontrado."
                          className="text-sm h-8"
                        />
                        <Button size="sm" onClick={handleAssignTech} disabled={!selectedTechId || assigning} className="bg-amber-500 hover:bg-amber-600 text-black h-8">
                          {assigning ? <Loader2 className="h-3 w-3 animate-spin" /> : <UserCheck className="h-3 w-3" />}
                        </Button>
                      </div>
                    )}
                  </div>
                <div>
                  <p className="text-zinc-500">Valor do Serviço</p>
                  <div className="flex items-center gap-2">
                    <span className="text-white">R$ {Number(detailOrder.total_value).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</span>
                    {editValue === "" ? (
                      <Button variant="ghost" size="sm" onClick={() => setEditValue(String(detailOrder.total_value))} className="text-amber-400 hover:text-amber-300 h-6 px-2 text-xs">
                        Editar
                      </Button>
                    ) : (
                      <>
                        <Input
                          type="number"
                          min={0}
                          step={0.01}
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="bg-zinc-800 border-zinc-700 text-white h-7 w-28 text-sm"
                        />
                        <Button size="sm" onClick={handleSaveValue} disabled={savingValue} className="bg-amber-500 hover:bg-amber-600 text-black h-7 px-2 text-xs">
                          {savingValue ? <Loader2 className="h-3 w-3 animate-spin" /> : "Salvar"}
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setEditValue("")} className="text-zinc-400 hover:text-white h-7 px-2 text-xs">
                          Cancelar
                        </Button>
                      </>
                    )}
                  </div>
                </div>
                  <div>
                    <p className="text-zinc-500">Custo Peças</p>
                    <p className="text-white">R$ {Number(detailOrder.parts_cost).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</p>
                  </div>
                </div>
                {detailOrder.technical_notes && !editingFields && (
                  <div className="col-span-2">
                    <p className="text-zinc-500">Notas Técnicas</p>
                    <p className="text-zinc-300 text-sm">{detailOrder.technical_notes}</p>
                  </div>
                )}
                {editingFields && (
                  <div className="col-span-2">
                    <p className="text-zinc-500">Notas Técnicas</p>
                    <Input value={editTechNotes} onChange={(e) => setEditTechNotes(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white text-sm h-8 mt-1" placeholder="Observações técnicas..." />
                  </div>
                )}
                {editingFields ? (
                  <div className="col-span-2 flex gap-2">
                    <Button size="sm" onClick={handleSaveFields} disabled={savingFields} className="bg-amber-500 hover:bg-amber-600 text-black h-7 px-3 text-xs">
                      {savingFields ? <Loader2 className="h-3 w-3 animate-spin" /> : "Salvar Dados"}
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setEditingFields(false)} className="text-zinc-400 hover:text-white h-7 px-3 text-xs">
                      Cancelar
                    </Button>
                  </div>
                ) : (
                  <div className="col-span-2">
                    <Button variant="ghost" size="sm" onClick={() => { setEditDeviceInfo(detailOrder.device_info); setEditTechNotes(detailOrder.technical_notes || ""); setEditingFields(true); }} className="text-amber-400 hover:text-amber-300 h-7 px-2 text-xs">
                      Editar Dados
                    </Button>
                  </div>
                )}
              {STATUS_FLOW[detailOrder.status]?.length > 0 && (
                <div>
                  <p className="text-zinc-500 text-sm mb-2">Avançar Status</p>
                  <div className="flex gap-2">
                    {STATUS_FLOW[detailOrder.status].map((nextStatus) => (
                      <Button
                        key={nextStatus}
                        variant="outline"
                        size="sm"
                        className="border-zinc-700 text-white hover:bg-amber-500 hover:text-black"
                        onClick={() => handleStatusUpdate(detailOrder.id, nextStatus)}
                      >
                        <ArrowRight className="h-3 w-3 mr-1" />
                        {nextStatus}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
              {user?.role === "ADMIN" && (
                <div className="border-t border-zinc-800 pt-4">
                  <Button variant="ghost" size="sm" onClick={handleDeleteOrder} className="text-red-400 hover:text-red-300 hover:bg-red-500/10">
                    <Trash2 className="h-3 w-3 mr-1" /> Excluir OS
                  </Button>
                </div>
              )}
              </TabsContent>

          <TabsContent value="timeline" className="mt-4 space-y-4">
              <div className="border border-zinc-800 rounded-lg p-3 bg-zinc-950 space-y-3">
                <p className="text-sm text-zinc-400 font-medium flex items-center gap-1">
                  <Plus className="h-3 w-3" /> Adicionar Nota Técnica
                </p>
                <div className="flex gap-2">
                  <Input
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    placeholder="Observação técnica..."
                    className="bg-zinc-800 border-zinc-700 text-white h-8 text-sm flex-1"
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAddNote(); } }}
                  />
                  <Button size="sm" onClick={handleAddNote} disabled={!noteContent.trim() || addingNote} className="bg-amber-500 hover:bg-amber-600 text-black h-8">
                    {addingNote ? <Loader2 className="h-3 w-3 animate-spin" /> : "Enviar"}
                  </Button>
                </div>
              </div>
              {events.length === 0 ? (
                  <p className="text-zinc-500 text-center py-8">Nenhum evento registrado</p>
                ) : (
                  <div className="space-y-3">
                    {events.map((evt) => (
                      <div key={evt.id} className="flex gap-3 items-start">
                        <div className="mt-1">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${EVENT_COLORS[evt.event_type] || EVENT_COLORS.NOTE_ADDED}`}>
                            {EVENT_LABELS[evt.event_type] || evt.event_type}
                          </span>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-zinc-300">{evt.description}</p>
                          <p className="text-xs text-zinc-600 mt-0.5">
                            {new Date(evt.created_at).toLocaleString("pt-BR")}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="insumos" className="mt-4 space-y-4">
                <div className="border border-zinc-800 rounded-lg p-3 bg-zinc-950 space-y-3">
                  <p className="text-sm text-zinc-400 font-medium flex items-center gap-1">
                    <Plus className="h-3 w-3" /> Adicionar Insumo
                  </p>
                  <div className="flex gap-2 items-end">
                    <div className="flex-1">
                      <Label className="text-zinc-500 text-xs">Produto</Label>
                      <Combobox
                        items={productItems}
                        value={addPartProductId}
                        onValueChange={setAddPartProductId}
                        placeholder="Selecionar produto..."
                        searchPlaceholder="Buscar produto..."
                        emptyMessage="Nenhum produto encontrado."
                        className="text-sm h-8"
                      />
                    </div>
                    <div className="w-20">
                      <Label className="text-zinc-500 text-xs">Qtd</Label>
                      <Input
                        type="number"
                        min={1}
                        value={addPartQty}
                        onChange={(e) => setAddPartQty(Math.max(1, parseInt(e.target.value) || 1))}
                        className="bg-zinc-800 border-zinc-700 text-white h-8 text-sm"
                      />
                    </div>
                    <Button
                      size="sm"
                      onClick={handleAddPart}
                      disabled={!addPartProductId || addingPart}
                      className="bg-amber-500 hover:bg-amber-600 text-black h-8"
                    >
                      {addingPart ? <Loader2 className="h-3 w-3 animate-spin" /> : <Plus className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>

                {parts.length === 0 ? (
                  <p className="text-zinc-500 text-center py-6">Nenhum insumo vinculado</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-zinc-800">
                        <TableHead className="text-zinc-400 text-xs">Produto ID</TableHead>
                        <TableHead className="text-zinc-400 text-xs">Qtd</TableHead>
                        <TableHead className="text-zinc-400 text-xs">Custo (Snapshot)</TableHead>
                        <TableHead className="text-zinc-400 text-xs">Venda (Snapshot)</TableHead>
                        <TableHead className="text-zinc-400 text-xs"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {parts.map((part) => {
                        const prod = products.find((p) => p.id === part.product_id);
                        return (
                          <TableRow key={part.id} className="border-zinc-800">
                            <TableCell className="text-white text-sm">
                              {prod?.name || part.product_id.slice(0, 8)}
                            </TableCell>
                            <TableCell className="text-white text-sm">{part.quantity}</TableCell>
                            <TableCell className="text-zinc-400 text-sm">
                              R$ {Number(part.snapshot_cost_price).toFixed(2)}
                            </TableCell>
                            <TableCell className="text-zinc-400 text-sm">
                              R$ {Number(part.snapshot_selling_price).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleRemovePart(part.id)}
                                className="text-red-400 hover:text-red-300 h-6 px-2"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                )}
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
