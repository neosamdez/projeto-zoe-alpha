"use client";

import { useEffect, useState, useCallback } from "react";
import { getTechnicians, getTechnician, createTechnician, updateTechnician, deleteTechnician } from "@/lib/technicians";
import type { Technician, TechnicianCreate, TechnicianUpdate } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { UserPlus, Pencil, Trash2, Wrench } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

export function TechniciansPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTech, setEditingTech] = useState<Technician | null>(null);
  const [form, setForm] = useState<TechnicianCreate>({ name: "" });
  const [editForm, setEditForm] = useState<TechnicianUpdate>({});
  const [page, setPage] = useState(1);
  const [detailTech, setDetailTech] = useState<Technician | null>(null);

  const openDetail = async (tech: Technician) => {
    setDetailTech(tech);
    try {
      const fresh = await getTechnician(tech.id);
      setDetailTech(fresh);
    } catch {
      toast.error("Erro ao carregar detalhes do técnico");
    }
  };

  const fetchTechnicians = useCallback(async () => {
    try {
      const data = await getTechnicians();
      setTechnicians(data);
    } catch {
      toast.error("Erro ao carregar equipe");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTechnicians();
  }, [fetchTechnicians]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTechnician(form);
      toast.success("Técnico adicionado à Guilda");
      setDialogOpen(false);
      setForm({ name: "" });
      fetchTechnicians();
    } catch (err: any) {
      toast.error(err.message || "Erro ao cadastrar");
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTech) return;
    try {
      await updateTechnician(editingTech.id, editForm);
      toast.success("Dados atualizados");
      setEditDialogOpen(false);
      setEditingTech(null);
      fetchTechnicians();
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remover este técnico da Guilda?")) return;
    try {
      await deleteTechnician(id);
      toast.success("Técnico removido");
      fetchTechnicians();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover");
    }
  };

  const openEdit = (tech: Technician) => {
    setEditingTech(tech);
    setEditForm({ name: tech.name, specialization: tech.specialization || "", is_active: tech.is_active });
    setEditDialogOpen(true);
  };

  const totalPages = Math.ceil(technicians.length / PAGE_SIZE);
  const paged = technicians.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Equipe</h1>
          <p className="text-zinc-400 mt-1">Mestres da Bancada — Guilda de Técnicos</p>
        </div>
        {isAdmin && (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger
            render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}
          >
            <UserPlus className="h-4 w-4 mr-2" /> Novo Técnico
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800">
            <DialogHeader>
              <DialogTitle className="text-white">Novo Mestre</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label className="text-zinc-300">Nome</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Especialização</Label>
                <Input value={form.specialization || ""} onChange={(e) => setForm({ ...form, specialization: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Cadastrar</Button>
            </form>
          </DialogContent>
        </Dialog>
        )}
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Wrench className="h-5 w-5 text-amber-500" />
            {technicians.length} técnico(s) — exibindo {paged.length} de {technicians.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Nome</TableHead>
                <TableHead className="text-zinc-400">Especialização</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Cadastro</TableHead>
                <TableHead className="text-zinc-400"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
        {paged.map((tech) => (
          <TableRow key={tech.id} className="border-zinc-800 cursor-pointer hover:bg-zinc-800/50" onClick={() => openDetail(tech)}>
            <TableCell className="text-white font-medium">{tech.name}</TableCell>
            <TableCell className="text-zinc-300">{tech.specialization || "—"}</TableCell>
            <TableCell>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${tech.is_active ? "bg-green-500/10 text-green-400 border-green-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"}`}>
                {tech.is_active ? "Ativo" : "Inativo"}
              </span>
            </TableCell>
            <TableCell className="text-zinc-500">{new Date(tech.created_at).toLocaleDateString("pt-BR")}</TableCell>
            <TableCell>
              {isAdmin && (
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="sm" onClick={() => openEdit(tech)} className="text-zinc-400 hover:text-white">
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(tech.id)} className="text-zinc-400 hover:text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </TableCell>
          </TableRow>
        ))}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-zinc-500 py-8">Nenhum técnico cadastrado</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaginationControls page={page} totalPages={totalPages} onPageChange={setPage} />

      {isAdmin && (
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white">Editar Técnico</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label className="text-zinc-300">Nome</Label>
              <Input value={editForm.name || ""} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div>
              <Label className="text-zinc-300">Especialização</Label>
              <Input value={editForm.specialization || ""} onChange={(e) => setEditForm({ ...editForm, specialization: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="is_active" checked={editForm.is_active ?? true} onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })} className="rounded" />
              <Label htmlFor="is_active" className="text-zinc-300">Ativo</Label>
            </div>
            <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
      )}

      <Dialog open={!!detailTech} onOpenChange={() => setDetailTech(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Wrench className="h-5 w-5 text-amber-500" />
              {detailTech?.name}
            </DialogTitle>
          </DialogHeader>
          {detailTech && (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-zinc-500">Especialização</p>
                  <p className="text-white">{detailTech.specialization || "—"}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Status</p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${detailTech.is_active ? "bg-green-500/10 text-green-400 border-green-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"}`}>
                    {detailTech.is_active ? "Ativo" : "Inativo"}
                  </span>
                </div>
                <div>
                  <p className="text-zinc-500">Cadastro</p>
                  <p className="text-white">{new Date(detailTech.created_at).toLocaleDateString("pt-BR")}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
