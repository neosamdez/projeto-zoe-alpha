"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getLeads, createLead, updateLead, deleteLead } from "@/lib/leads";
import { createOrderFromLead } from "@/lib/orders";
import type { Lead, LeadCreate, LeadUpdate } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { UserPlus, Search, Pencil, Trash2, Users, Phone, Mail, ClipboardPlus } from "lucide-react";
import { toast } from "sonner";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

export function LeadsPage() {
const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [form, setForm] = useState<LeadCreate>({ name: "", email: "", phone: "" });
  const [editForm, setEditForm] = useState<LeadUpdate>({});
  const [osDialogOpen, setOsDialogOpen] = useState(false);
  const [osLead, setOsLead] = useState<Lead | null>(null);
  const [osForm, setOsForm] = useState({ device_info: "", technical_notes: "" });
  const [osLoading, setOsLoading] = useState(false);
  const [page, setPage] = useState(1);

  const fetchLeads = useCallback(async () => {
    try {
      const data = await getLeads();
      setLeads(data);
    } catch {
      toast.error("Erro ao carregar clientes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createLead(form);
      toast.success("Lead cadastrado com sucesso");
      setDialogOpen(false);
      setForm({ name: "", email: "", phone: "" });
      fetchLeads();
    } catch (err: any) {
      toast.error(err.message || "Erro ao cadastrar lead");
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingLead) return;
    try {
      await updateLead(editingLead.id, editForm);
      toast.success("Cliente atualizado");
      setEditDialogOpen(false);
      setEditingLead(null);
      setEditForm({});
      fetchLeads();
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar");
    }
  };

  const openEdit = (lead: Lead) => {
    setEditingLead(lead);
    setEditForm({ name: lead.name, email: lead.email, phone: lead.phone });
    setEditDialogOpen(true);
  };

  const openCreateOS = (lead: Lead) => {
    setOsLead(lead);
    setOsForm({ device_info: lead.device_interest || "", technical_notes: lead.notes || "" });
    setOsDialogOpen(true);
  };

  const handleCreateOS = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!osLead) return;
    setOsLoading(true);
    try {
      await createOrderFromLead(osLead.id, osForm);
      toast.success(`OS criada para ${osLead.name}`);
      setOsDialogOpen(false);
      setOsLead(null);
      fetchLeads();
    } catch (err: any) {
      toast.error(err.message || "Erro ao criar OS");
    } finally {
      setOsLoading(false);
    }
  };

  const handleDelete = async (lead: Lead) => {
    if (lead.total_os > 0) {
      toast.error("Este cliente possui OS vinculada(s). Remova as OS primeiro.");
      return;
    }
    if (!confirm(`Remover ${lead.name} da base de clientes?`)) return;
    try {
      await deleteLead(lead.id);
      toast.success("Cliente removido");
      fetchLeads();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover cliente");
    }
  };

  const filtered = leads.filter(
    (l) =>
      l.name.toLowerCase().includes(search.toLowerCase()) ||
      l.email.toLowerCase().includes(search.toLowerCase()) ||
      l.phone.includes(search)
  );

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Clientes</h1>
          <p className="text-zinc-400 mt-1">CRM — Base de Leads e Clientes</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger
            render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}
          >
            <UserPlus className="h-4 w-4 mr-2" /> Novo Lead
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800">
            <DialogHeader>
              <DialogTitle className="text-white">Novo Lead</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label className="text-zinc-300">Nome</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">E-mail</Label>
                <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Telefone</Label>
                <Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Dispositivo de Interesse</Label>
                <Input value={form.device_interest || ""} onChange={(e) => setForm({ ...form, device_interest: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Observações</Label>
                <Input value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Cadastrar</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
        <Input
          placeholder="Buscar por nome, e-mail ou telefone..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="pl-10 bg-zinc-900 border-zinc-800 text-white"
        />
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-amber-500" />
            {filtered.length} cliente(s) — exibindo {paged.length} de {filtered.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Nome</TableHead>
                <TableHead className="text-zinc-400">E-mail</TableHead>
                <TableHead className="text-zinc-400">Telefone</TableHead>
              <TableHead className="text-zinc-400">OS</TableHead>
              <TableHead className="text-zinc-400">Cadastro</TableHead>
              <TableHead className="text-zinc-400"></TableHead>
              <TableHead className="text-zinc-400"></TableHead>
              <TableHead className="text-zinc-400"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
        {paged.map((lead) => (
          <TableRow key={lead.id} className="border-zinc-800 cursor-pointer hover:bg-zinc-800/50" onClick={() => router.push(`/leads/${lead.id}`)}>
            <TableCell className="text-white font-medium">{lead.name}</TableCell>
            <TableCell>
              <span className="flex items-center gap-1 text-zinc-400"><Mail className="h-3 w-3" />{lead.email}</span>
            </TableCell>
            <TableCell>
              <span className="flex items-center gap-1 text-zinc-400"><Phone className="h-3 w-3" />{lead.phone}</span>
            </TableCell>
            <TableCell className="text-amber-500 font-semibold">{lead.total_os}</TableCell>
            <TableCell className="text-zinc-500">{new Date(lead.created_at).toLocaleDateString("pt-BR")}</TableCell>
            <TableCell onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="sm" onClick={() => openEdit(lead)} className="text-zinc-400 hover:text-white">
                <Pencil className="h-4 w-4" />
              </Button>
            </TableCell>
            <TableCell onClick={(e) => e.stopPropagation()}>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => openCreateOS(lead)}
                disabled={lead.total_os > 0}
                className={lead.total_os > 0 ? "text-zinc-600" : "text-amber-500 hover:text-amber-400"}
                title={lead.total_os > 0 ? "Este lead já possui OS" : "Criar Ordem de Serviço"}
              >
                <ClipboardPlus className="h-4 w-4" />
              </Button>
            </TableCell>
            <TableCell onClick={(e) => e.stopPropagation()}>
              <Button
                variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(lead)}
                    disabled={lead.total_os > 0}
                    className={lead.total_os > 0 ? "text-zinc-600" : "text-zinc-400 hover:text-red-400"}
                    title={lead.total_os > 0 ? "Cliente com OS vinculada" : "Remover cliente"}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
                </TableRow>
              ))}
            {paged.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-zinc-500 py-8">Nenhum cliente encontrado</TableCell>
              </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white">Editar Cliente</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label className="text-zinc-300">Nome</Label>
              <Input value={editForm.name || ""} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div>
              <Label className="text-zinc-300">E-mail</Label>
              <Input type="email" value={editForm.email || ""} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div>
              <Label className="text-zinc-300">Telefone</Label>
              <Input value={editForm.phone || ""} onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
      <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Salvar</Button>
      </form>
      </DialogContent>
      </Dialog>

      <Dialog open={osDialogOpen} onOpenChange={setOsDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white">Criar OS — {osLead?.name}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateOS} className="space-y-4">
            <div>
              <Label className="text-zinc-300">Dispositivo / Equipamento</Label>
              <Input
                value={osForm.device_info}
                onChange={(e) => setOsForm({ ...osForm, device_info: e.target.value })}
                required
                placeholder="Ex: MacBook Pro M2 2023"
                className="bg-zinc-800 border-zinc-700 text-white"
              />
            </div>
            <div>
              <Label className="text-zinc-300">Notas Técnicas</Label>
              <Input
                value={osForm.technical_notes}
                onChange={(e) => setOsForm({ ...osForm, technical_notes: e.target.value })}
                placeholder="Sintomas, observações..."
                className="bg-zinc-800 border-zinc-700 text-white"
              />
            </div>
            <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black" disabled={osLoading}>
              {osLoading ? "Forjando..." : "Forjar Ordem de Serviço"}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
      </div>
  );
}
