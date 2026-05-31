"use client";

import { useEffect, useState, useCallback } from "react";
import { getAlertConfigs, createAlertConfig, updateAlertConfig, deleteAlertConfig } from "@/lib/alert-configs";
import type { AlertConfig, AlertConfigCreate, AlertConfigUpdate } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Bell, Plus, Pencil, Trash2, ToggleLeft, ToggleRight } from "lucide-react";
import { toast } from "sonner";

export function AlertConfigsPage() {
  const [configs, setConfigs] = useState<AlertConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<AlertConfig | null>(null);
  const [form, setForm] = useState<AlertConfigCreate & { id?: string }>({
    name: "",
    recipient_email: "",
    is_active: true,
    min_stock_threshold: 0,
  });

  const fetchConfigs = useCallback(async () => {
    try {
      const data = await getAlertConfigs();
      setConfigs(data);
    } catch {
      toast.error("Erro ao carregar configurações");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfigs();
  }, [fetchConfigs]);

  const openCreate = () => {
    setEditingConfig(null);
    setForm({ name: "", recipient_email: "", is_active: true, min_stock_threshold: 0 });
    setDialogOpen(true);
  };

  const openEdit = (config: AlertConfig) => {
    setEditingConfig(config);
    setForm({
      id: config.id,
      name: config.name,
      recipient_email: config.recipient_email,
      is_active: config.is_active,
      min_stock_threshold: config.min_stock_threshold,
    });
    setDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingConfig) {
        const updateData: AlertConfigUpdate = {
          name: form.name,
          recipient_email: form.recipient_email,
          is_active: form.is_active,
          min_stock_threshold: form.min_stock_threshold,
        };
        await updateAlertConfig(editingConfig.id, updateData);
        toast.success("Configuração atualizada");
      } else {
        await createAlertConfig({
          name: form.name,
          recipient_email: form.recipient_email,
          is_active: form.is_active,
          min_stock_threshold: form.min_stock_threshold,
        });
        toast.success("Configuração criada");
      }
      setDialogOpen(false);
      fetchConfigs();
    } catch (err: any) {
      toast.error(err.message || "Erro ao salvar");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remover esta configuração de alerta?")) return;
    try {
      await deleteAlertConfig(id);
      toast.success("Configuração removida");
      fetchConfigs();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover");
    }
  };

  const toggleActive = async (config: AlertConfig) => {
    try {
      await updateAlertConfig(config.id, { is_active: !config.is_active });
      toast.success(config.is_active ? "Alerta desativado" : "Alerta ativado");
      fetchConfigs();
    } catch (err: any) {
      toast.error(err.message || "Erro ao alterar status");
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 w-64 bg-zinc-800 rounded mb-2" />
          <div className="h-4 w-96 bg-zinc-800 rounded" />
        </div>
        <Card className="bg-zinc-900 border-zinc-800 animate-pulse">
          <CardContent className="p-6">
            <div className="h-40 bg-zinc-800 rounded" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Configurações de Alerta</h1>
          <p className="text-zinc-400 mt-1">Gerencie quem recebe alertas de estoque baixo</p>
        </div>
        <Button onClick={openCreate} className="bg-amber-500 hover:bg-amber-600 text-black">
          <Plus className="h-4 w-4 mr-2" />
          Nova Configuração
        </Button>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2 text-sm">
            <Bell className="h-4 w-4 text-amber-500" />
            Destinatários de Alerta ({configs.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {configs.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="h-12 w-12 text-zinc-700 mx-auto mb-3" />
              <p className="text-zinc-500 text-sm">Nenhuma configuração de alerta cadastrada</p>
              <p className="text-zinc-600 text-xs mt-1">Crie uma para definir quem recebe notificações de estoque baixo</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800 hover:bg-transparent">
                  <TableHead className="text-zinc-400">Nome</TableHead>
                  <TableHead className="text-zinc-400">Email</TableHead>
                  <TableHead className="text-zinc-400">Limiar Mínimo</TableHead>
                  <TableHead className="text-zinc-400">Status</TableHead>
                  <TableHead className="text-zinc-400 text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {configs.map((config) => (
                  <TableRow key={config.id} className="border-zinc-800 hover:bg-zinc-800/50">
                    <TableCell className="text-white font-medium">{config.name}</TableCell>
                    <TableCell className="text-zinc-300 text-sm">{config.recipient_email}</TableCell>
                    <TableCell className="text-zinc-300 text-sm font-mono">
                      {config.min_stock_threshold === 0 ? "Qualquer nível" : `${config.min_stock_threshold} un.`}
                    </TableCell>
                    <TableCell>
                      <button
                        onClick={() => toggleActive(config)}
                        className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-colors ${
                          config.is_active
                            ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                            : "bg-zinc-700/50 text-zinc-500 hover:bg-zinc-700"
                        }`}
                      >
                        {config.is_active ? (
                          <><ToggleRight className="h-3.5 w-3.5" /> Ativo</>
                        ) : (
                          <><ToggleLeft className="h-3.5 w-3.5" /> Inativo</>
                        )}
                      </button>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="icon" onClick={() => openEdit(config)} className="text-zinc-400 hover:text-amber-400 hover:bg-amber-400/10 h-8 w-8">
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(config.id)} className="text-zinc-400 hover:text-red-400 hover:bg-red-400/10 h-8 w-8">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800 text-white">
          <DialogHeader>
            <DialogTitle>{editingConfig ? "Editar Configuração" : "Nova Configuração de Alerta"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-zinc-400 text-sm">Nome</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Ex: Alerta Estoque - Admin"
                required
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
              />
            </div>
            <div>
              <Label className="text-zinc-400 text-sm">Email do Destinatário</Label>
              <Input
                type="email"
                value={form.recipient_email}
                onChange={(e) => setForm({ ...form, recipient_email: e.target.value })}
                placeholder="admin@empresa.com"
                required
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
              />
            </div>
            <div>
              <Label className="text-zinc-400 text-sm">Limiar Mínimo de Estoque</Label>
              <Input
                type="number"
                min={0}
                value={form.min_stock_threshold}
                onChange={(e) => setForm({ ...form, min_stock_threshold: parseInt(e.target.value) || 0 })}
                placeholder="0 = qualquer nível"
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
              />
              <p className="text-zinc-600 text-xs mt-1">0 = alerta quando qualquer produto atingir estoque baixo</p>
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => setForm({ ...form, is_active: !form.is_active })}
                className={`relative w-11 h-6 rounded-full transition-colors ${form.is_active ? "bg-green-500" : "bg-zinc-700"}`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${form.is_active ? "translate-x-5" : ""}`}
                />
              </button>
              <span className="text-sm text-zinc-300">{form.is_active ? "Ativo" : "Inativo"}</span>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="ghost" onClick={() => setDialogOpen(false)} className="text-zinc-400 hover:text-white">
                Cancelar
              </Button>
              <Button type="submit" className="bg-amber-500 hover:bg-amber-600 text-black">
                {editingConfig ? "Salvar" : "Criar"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
