"use client";

import { useEffect, useState, useCallback } from "react";
import { getRmas, createRma, getRmaDetail, updateRmaStatus, addInspection, addReturnedPart, getDefectCodes } from "@/lib/rma";
import { getProducts } from "@/lib/products";
import type { RmaRequest, RmaRequestCreate, RmaRequestDetail, RmaInspectionCreate, ReturnedPartCreate, DefectCode, ReturnCode, RmaStatus as RmaStatusType, Product } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RotateCcw, Plus, Eye, ClipboardCheck, PackageCheck } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";
import { StatusBadge } from "@/components/status-badge";
import { DateFilter } from "@/components/date-filter";

const PAGE_SIZE = 15;

const RETURN_CODES: { value: ReturnCode; label: string; deadline: number }[] = [
  { value: "805", label: "805 — Defeito de fábrica (30d)", deadline: 30 },
  { value: "807", label: "807 — Troca em garantia (60d)", deadline: 60 },
  { value: "808", label: "808 — Peça faltante (7d)", deadline: 7 },
  { value: "809", label: "809 — Atraso entrega (2d)", deadline: 2 },
  { value: "816", label: "816 — Sem conserto (0d)", deadline: 0 },
  { value: "819", label: "819 — Reclamação cliente (7d)", deadline: 7 },
  { value: "821", label: "821 — Produto devolvido (30d)", deadline: 30 },
  { value: "828", label: "828 — Erro pedido (7d)", deadline: 7 },
  { value: "838", label: "838 — Avaria transporte (60d)", deadline: 60 },
  { value: "839", label: "839 — Outros (200d)", deadline: 200 },
];

const RMA_STATUS_LIST: RmaStatusType[] = ["PENDING", "INSPECTING", "APPROVED", "REJECTED", "SHIPPED", "COMPLETED"];

export function RmaPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [rmas, setRmas] = useState<RmaRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1);
  const [filterYear, setFilterYear] = useState(new Date().getFullYear());
  const [createOpen, setCreateOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedRma, setSelectedRma] = useState<RmaRequestDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [defectCodes, setDefectCodes] = useState<DefectCode[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [inspectionTab, setInspectionTab] = useState("geral");

  const [createForm, setCreateForm] = useState<RmaRequestCreate>({ return_code: "805" });
  const [inspectionForm, setInspectionForm] = useState<RmaInspectionCreate>({ defect_code: "", defect_description: "" });
  const [partForm, setPartForm] = useState<ReturnedPartCreate>({ part_code: "", return_reason: "805" });

  const fetchRmas = useCallback(async () => {
    try {
      const data = await getRmas(statusFilter || undefined, filterMonth, filterYear);
      setRmas(data);
    } catch {
      toast.error("Erro ao carregar RMAs");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, filterMonth, filterYear]);

  useEffect(() => { fetchRmas(); }, [fetchRmas]);

  useEffect(() => {
    getDefectCodes().then(setDefectCodes).catch(() => {});
    getProducts().then(setProducts).catch(() => {});
  }, []);

  const openDetail = async (rma: RmaRequest) => {
    setDetailLoading(true);
    setDetailOpen(true);
    try {
      const detail = await getRmaDetail(rma.id);
      setSelectedRma(detail);
    } catch {
      toast.error("Erro ao carregar detalhes do RMA");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createRma(createForm);
      toast.success("RMA criado com sucesso");
      setCreateOpen(false);
      setCreateForm({ return_code: "805" });
      fetchRmas();
    } catch (err: any) {
      toast.error(err.message || "Erro ao criar RMA");
    }
  };

  const handleStatusChange = async (rmaId: string, newStatus: RmaStatusType) => {
    try {
      await updateRmaStatus(rmaId, newStatus);
      toast.success("Status atualizado");
      openDetail({ id: rmaId } as RmaRequest);
      fetchRmas();
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar status");
    }
  };

  const handleInspection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRma) return;
    try {
      await addInspection(selectedRma.id, inspectionForm);
      toast.success("Inspeção registrada");
      setInspectionForm({ defect_code: "", defect_description: "" });
      openDetail(selectedRma);
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar inspeção");
    }
  };

  const handleReturnedPart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRma) return;
    try {
      await addReturnedPart(selectedRma.id, partForm);
      toast.success("Peça devolvida registrada");
      setPartForm({ part_code: "", return_reason: "805" });
      openDetail(selectedRma);
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar peça");
    }
  };

  const totalPages = Math.ceil(rmas.length / PAGE_SIZE);
  const paged = rmas.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">RMA</h1>
          <p className="text-zinc-400 mt-1">Gerenciamento de Devoluções Samsung</p>
        </div>
        <div className="flex gap-3">
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg px-3 py-2"
          >
            <option value="">Todos os Status</option>
          {RMA_STATUS_LIST.map((s) => (
            <option key={s} value={s}>{s}</option>
            ))}
</select>
      <DateFilter month={filterMonth} year={filterYear} onMonthChange={setFilterMonth} onYearChange={setFilterYear} />
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}>
              <Plus className="h-4 w-4 mr-2" /> Novo RMA
            </DialogTrigger>
            <DialogContent className="bg-zinc-900 border-zinc-800 max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-white">Novo RMA</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <Label className="text-zinc-300">Código de Retorno *</Label>
                  <select
                    value={createForm.return_code}
                    onChange={(e) => setCreateForm({ ...createForm, return_code: e.target.value as ReturnCode })}
                    className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2"
                    required
                  >
                    {RETURN_CODES.map((rc) => (
                      <option key={rc.value} value={rc.value}>{rc.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-zinc-300">Nº Delivery</Label>
                  <Input value={createForm.delivery_code || ""} onChange={(e) => setCreateForm({ ...createForm, delivery_code: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <div>
                  <Label className="text-zinc-300">NF Samsung</Label>
                  <Input value={createForm.samsung_nf || ""} onChange={(e) => setCreateForm({ ...createForm, samsung_nf: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <div>
                  <Label className="text-zinc-300">Notas</Label>
                  <Textarea value={createForm.notes || ""} onChange={(e) => setCreateForm({ ...createForm, notes: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Criar RMA</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <RotateCcw className="h-5 w-5 text-amber-500" />
            {rmas.length} RMA(s)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Protocolo</TableHead>
                <TableHead className="text-zinc-400">Return Code</TableHead>
                <TableHead className="text-zinc-400">Delivery</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Prazo</TableHead>
                <TableHead className="text-zinc-400">Criado</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((rma) => (
                <TableRow key={rma.id} className="border-zinc-800 cursor-pointer hover:bg-zinc-800/50">
                  <TableCell className="text-amber-500 font-mono">{rma.protocol}</TableCell>
                  <TableCell className="text-white">{rma.return_code}</TableCell>
                  <TableCell className="text-zinc-300">{rma.delivery_code || "—"}</TableCell>
                <TableCell>
                  <StatusBadge status={rma.status as RmaStatusType} />
                </TableCell>
                  <TableCell className="text-zinc-300">
                    {rma.deadline_date ? new Date(rma.deadline_date).toLocaleDateString("pt-BR") : "—"}
                  </TableCell>
                  <TableCell className="text-zinc-400 text-sm">{new Date(rma.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => openDetail(rma)} className="text-zinc-400 hover:text-white">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-zinc-500 py-8">Nenhum RMA encontrado.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <RotateCcw className="h-5 w-5 text-amber-500" />
              {selectedRma?.protocol}
            </DialogTitle>
          </DialogHeader>
          {detailLoading ? (
            <p className="text-zinc-400">Carregando...</p>
          ) : selectedRma ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
            <StatusBadge status={selectedRma.status as RmaStatusType} />
                <span className="text-zinc-400 text-sm">Return Code: {selectedRma.return_code}</span>
                {selectedRma.deadline_date && (
                  <span className="text-zinc-400 text-sm">Prazo: {new Date(selectedRma.deadline_date).toLocaleDateString("pt-BR")}</span>
                )}
              </div>

              <div className="flex gap-2 flex-wrap">
                {selectedRma.status === "PENDING" && (
                  <Button size="sm" onClick={() => handleStatusChange(selectedRma.id, "INSPECTING")} className="bg-blue-600 hover:bg-blue-700 text-white">Iniciar Inspeção</Button>
                )}
                {selectedRma.status === "INSPECTING" && (
                  <>
                    <Button size="sm" onClick={() => handleStatusChange(selectedRma.id, "APPROVED")} className="bg-green-600 hover:bg-green-700 text-white">Aprovar</Button>
                    <Button size="sm" onClick={() => handleStatusChange(selectedRma.id, "REJECTED")} className="bg-red-600 hover:bg-red-700 text-white">Rejeitar</Button>
                  </>
                )}
                {selectedRma.status === "APPROVED" && (
                  <Button size="sm" onClick={() => handleStatusChange(selectedRma.id, "SHIPPED")} className="bg-purple-600 hover:bg-purple-700 text-white">Enviar</Button>
                )}
                {selectedRma.status === "SHIPPED" && (
                  <Button size="sm" onClick={() => handleStatusChange(selectedRma.id, "COMPLETED")} className="bg-zinc-600 hover:bg-zinc-700 text-white">Concluir</Button>
                )}
              </div>

              <Tabs value={inspectionTab} onValueChange={setInspectionTab}>
                <TabsList className="bg-zinc-800">
                  <TabsTrigger value="geral">Geral</TabsTrigger>
                  <TabsTrigger value="inspections">Inspeções ({selectedRma.inspections.length})</TabsTrigger>
                  <TabsTrigger value="parts">Peças Devolvidas ({selectedRma.returned_parts.length})</TabsTrigger>
                </TabsList>
                <TabsContent value="geral" className="space-y-2">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div><p className="text-zinc-500">Delivery</p><p className="text-white">{selectedRma.delivery_code || "—"}</p></div>
                    <div><p className="text-zinc-500">NF Samsung</p><p className="text-white">{selectedRma.samsung_nf || "—"}</p></div>
                    <div><p className="text-zinc-500">Prazo (dias)</p><p className="text-white">{selectedRma.deadline_days}</p></div>
                    <div><p className="text-zinc-500">Notas</p><p className="text-white">{selectedRma.notes || "—"}</p></div>
                  </div>
                </TabsContent>
                <TabsContent value="inspections" className="space-y-4">
                  {selectedRma.inspections.length > 0 ? (
                    <div className="space-y-2">
                      {selectedRma.inspections.map((insp) => (
                        <div key={insp.id} className="bg-zinc-800 rounded-lg p-3 text-sm">
                          <div className="flex justify-between">
                            <span className="text-amber-500 font-mono">{insp.defect_code}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${insp.result === "APPROVED" ? "bg-green-500/20 text-green-400" : insp.result === "REJECTED" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"}`}>{insp.result}</span>
                          </div>
                          <p className="text-zinc-300 mt-1">{insp.defect_description}</p>
                          {insp.notes && <p className="text-zinc-500 mt-1">{insp.notes}</p>}
                          <p className="text-zinc-600 text-xs mt-1">{new Date(insp.created_at).toLocaleString("pt-BR")}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-zinc-500 text-sm">Nenhuma inspeção registrada.</p>
                  )}
                  {(selectedRma.status === "INSPECTING" || selectedRma.status === "PENDING") && (
                    <form onSubmit={handleInspection} className="space-y-3 border-t border-zinc-800 pt-4">
                      <p className="text-white text-sm font-medium flex items-center gap-2"><ClipboardCheck className="h-4 w-4 text-amber-500" /> Nova Inspeção</p>
                      <div>
                        <Label className="text-zinc-300 text-xs">Código Defeito</Label>
                        <select value={inspectionForm.defect_code} onChange={(e) => setInspectionForm({ ...inspectionForm, defect_code: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2 text-sm" required>
                          <option value="">Selecione...</option>
                          {defectCodes.map((dc) => (
                            <option key={dc.id} value={dc.code}>{dc.code} — {dc.description}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label className="text-zinc-300 text-xs">Descrição</Label>
                        <Input value={inspectionForm.defect_description} onChange={(e) => setInspectionForm({ ...inspectionForm, defect_description: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white text-sm" required />
                      </div>
                      <div>
                        <Label className="text-zinc-300 text-xs">Resultado</Label>
                        <select value={inspectionForm.result || "PENDING"} onChange={(e) => setInspectionForm({ ...inspectionForm, result: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2 text-sm">
                          <option value="PENDING">Pendente</option>
                          <option value="APPROVED">Aprovado</option>
                          <option value="REJECTED">Rejeitado</option>
                        </select>
                      </div>
                      <div>
                        <Label className="text-zinc-300 text-xs">Notas</Label>
                        <Textarea value={inspectionForm.notes || ""} onChange={(e) => setInspectionForm({ ...inspectionForm, notes: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white text-sm" />
                      </div>
                      <Button type="submit" size="sm" className="bg-amber-500 hover:bg-amber-600 text-black">Registrar Inspeção</Button>
                    </form>
                  )}
                </TabsContent>
                <TabsContent value="parts" className="space-y-4">
                  {selectedRma.returned_parts.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow className="border-zinc-800">
                          <TableHead className="text-zinc-400">Código Peça</TableHead>
                          <TableHead className="text-zinc-400">Motivo</TableHead>
                          <TableHead className="text-zinc-400">NF Retorno</TableHead>
                          <TableHead className="text-zinc-400">Assinaturas</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedRma.returned_parts.map((part) => (
                          <TableRow key={part.id} className="border-zinc-800">
                            <TableCell className="text-amber-500 font-mono">{part.part_code}</TableCell>
                            <TableCell className="text-zinc-300">{part.return_reason}</TableCell>
                            <TableCell className="text-zinc-300">{part.return_nf || "—"}</TableCell>
                            <TableCell className="text-zinc-400 text-xs">
                              {part.technician_signature ? "✓ Técnico" : "○ Técnico"} {part.stock_signature ? "✓ Estoque" : "○ Estoque"}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <p className="text-zinc-500 text-sm">Nenhuma peça devolvida registrada.</p>
                  )}
                  {selectedRma.status !== "COMPLETED" && selectedRma.status !== "REJECTED" && (
                    <form onSubmit={handleReturnedPart} className="space-y-3 border-t border-zinc-800 pt-4">
                      <p className="text-white text-sm font-medium flex items-center gap-2"><PackageCheck className="h-4 w-4 text-amber-500" /> Registrar Peça Devolvida</p>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-zinc-300 text-xs">Código Peça *</Label>
                          <Input value={partForm.part_code} onChange={(e) => setPartForm({ ...partForm, part_code: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white text-sm" required />
                        </div>
                        <div>
                          <Label className="text-zinc-300 text-xs">Motivo Devolução</Label>
                          <select value={partForm.return_reason} onChange={(e) => setPartForm({ ...partForm, return_reason: e.target.value })} className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-lg px-3 py-2 text-sm">
                            {RETURN_CODES.map((rc) => (
                              <option key={rc.value} value={rc.value}>{rc.value}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-zinc-300 text-xs">NF Retorno</Label>
                          <Input value={partForm.return_nf || ""} onChange={(e) => setPartForm({ ...partForm, return_nf: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white text-sm" />
                        </div>
                        <div>
                          <Label className="text-zinc-300 text-xs">Delivery</Label>
                          <Input value={partForm.delivery_code || ""} onChange={(e) => setPartForm({ ...partForm, delivery_code: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white text-sm" />
                        </div>
                      </div>
                      <Button type="submit" size="sm" className="bg-amber-500 hover:bg-amber-600 text-black">Registrar</Button>
                    </form>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}
