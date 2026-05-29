"use client";

import { useEffect, useState, useCallback } from "react";
import { getUsers, updateUser, deleteUser } from "@/lib/users";
import type { UserResponse, UserUpdateByAdmin } from "@/types/auth";
import type { UserRole } from "@/types/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { UserCog, Pencil, Trash2, ShieldCheck, Wrench } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

const roleLabels: Record<string, string> = {
  ADMIN: "Administrador",
  TECHNICIAN: "Técnico",
};

const roleColors: Record<string, string> = {
  ADMIN: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  TECHNICIAN: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [editForm, setEditForm] = useState<UserUpdateByAdmin>({});
  const [page, setPage] = useState(1);

  const fetchUsers = useCallback(async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch {
      toast.error("Erro ao carregar operadores");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await updateUser(editingUser.id, editForm);
      toast.success("Operador atualizado");
      setEditDialogOpen(false);
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar");
    }
  };

  const handleDelete = async (id: string) => {
    if (id === currentUser?.id) {
      toast.error("Não é possível remover a si mesmo");
      return;
    }
    if (!confirm("Desativar este Operador? Ele será removido do sistema.")) return;
    try {
      await deleteUser(id);
      toast.success("Operador removido");
      fetchUsers();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover");
    }
  };

  const openEdit = (user: UserResponse) => {
    setEditingUser(user);
    setEditForm({
      full_name: user.full_name,
      role: user.role as UserRole,
      is_active: user.is_active,
    });
    setEditDialogOpen(true);
  };

  const totalPages = Math.ceil(users.length / PAGE_SIZE);
  const paged = users.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const RoleIcon = ({ role }: { role: string }) => {
    if (role === "ADMIN") return <ShieldCheck className="h-4 w-4 text-amber-500" />;
    return <Wrench className="h-4 w-4 text-blue-400" />;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Usuários</h1>
        <p className="text-zinc-400 mt-1">Conselho de Operadores — Gestão de Acesso</p>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <UserCog className="h-5 w-5 text-amber-500" />
            {users.length} operador(es) — exibindo {paged.length} de {users.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Nome</TableHead>
                <TableHead className="text-zinc-400">E-mail</TableHead>
                <TableHead className="text-zinc-400">Papel</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Cadastro</TableHead>
                <TableHead className="text-zinc-400"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paged.map((u) => (
                <TableRow key={u.id} className="border-zinc-800">
                  <TableCell className="text-white font-medium">{u.full_name}</TableCell>
                  <TableCell className="text-zinc-300">{u.email}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${roleColors[u.role] || ""}`}>
                      <RoleIcon role={u.role} />
                      {roleLabels[u.role] || u.role}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${u.is_active ? "bg-green-500/10 text-green-400 border-green-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"}`}>
                      {u.is_active ? "Ativo" : "Inativo"}
                    </span>
                  </TableCell>
                  <TableCell className="text-zinc-500">{new Date(u.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" onClick={() => openEdit(u)} className="text-zinc-400 hover:text-white">
                        <Pencil className="h-4 w-4" />
                      </Button>
                      {u.id !== currentUser?.id && (
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(u.id)} className="text-zinc-400 hover:text-red-400">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-zinc-500 py-8">Nenhum operador cadastrado</TableCell>
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
            <DialogTitle className="text-white">Editar Operador</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label className="text-zinc-300">Nome Completo</Label>
              <Input value={editForm.full_name || ""} onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div>
              <Label className="text-zinc-300">Papel</Label>
              <select
                value={editForm.role || "TECHNICIAN"}
                onChange={(e) => setEditForm({ ...editForm, role: e.target.value as UserRole })}
                className="w-full bg-zinc-800 border border-zinc-700 text-white rounded-md px-3 py-2 text-sm"
              >
                <option value="ADMIN">Administrador</option>
                <option value="TECHNICIAN">Técnico</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit_is_active"
                checked={editForm.is_active ?? true}
                onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="edit_is_active" className="text-zinc-300">Ativo</Label>
            </div>
            <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
