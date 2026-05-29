"use client";

import { useEffect, useState, useCallback } from "react";
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from "@/lib/products";
import type { Product, ProductCreate, ProductUpdate } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PackagePlus, Pencil, Trash2, Package } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { PaginationControls } from "@/components/pagination-controls";

const PAGE_SIZE = 15;

export function ProductsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductCreate>({ name: "", sku: "", cost_price: 0, selling_price: 0 });
  const [editForm, setEditForm] = useState<ProductUpdate>({});
  const [page, setPage] = useState(1);
  const [detailProduct, setDetailProduct] = useState<Product | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const openDetail = async (product: Product) => {
    setDetailProduct(product);
    setDetailLoading(true);
    try {
      const fresh = await getProduct(product.id);
      setDetailProduct(fresh);
    } catch {
      toast.error("Erro ao carregar detalhes do produto");
    } finally {
      setDetailLoading(false);
    }
  };

  const fetchProducts = useCallback(async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch {
      toast.error("Erro ao carregar inventário");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProduct(form);
      toast.success("Produto cadastrado no Arsenal");
      setDialogOpen(false);
      setForm({ name: "", sku: "", cost_price: 0, selling_price: 0 });
      fetchProducts();
    } catch (err: any) {
      toast.error(err.message || "Erro ao cadastrar");
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProduct) return;
    try {
      await updateProduct(editingProduct.id, editForm);
      toast.success("Produto atualizado");
      setEditDialogOpen(false);
      setEditingProduct(null);
      fetchProducts();
    } catch (err: any) {
      toast.error(err.message || "Erro ao atualizar");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remover este item do Arsenal?")) return;
    try {
      await deleteProduct(id);
      toast.success("Item removido");
      fetchProducts();
    } catch (err: any) {
      toast.error(err.message || "Erro ao remover");
    }
  };

  const openEdit = (product: Product) => {
    setEditingProduct(product);
    setEditForm({
      name: product.name,
      sku: product.sku,
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      current_stock: product.current_stock,
      min_stock: product.min_stock,
    });
    setEditDialogOpen(true);
  };

  const totalPages = Math.ceil(products.length / PAGE_SIZE);
  const paged = products.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Inventário</h1>
          <p className="text-zinc-400 mt-1">Arsenal de Elite — Peças e Insumos</p>
        </div>
        {isAdmin && (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger
            render={<Button className="bg-amber-500 hover:bg-amber-600 text-black" />}
          >
            <PackagePlus className="h-4 w-4 mr-2" /> Novo Item
          </DialogTrigger>
          <DialogContent className="bg-zinc-900 border-zinc-800">
            <DialogHeader>
              <DialogTitle className="text-white">Novo Item no Arsenal</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label className="text-zinc-300">Nome</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">SKU</Label>
                <Input value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-zinc-300">Preço Custo (R$)</Label>
                  <Input type="number" step="0.01" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: parseFloat(e.target.value) })} required className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <div>
                  <Label className="text-zinc-300">Preço Venda (R$)</Label>
                  <Input type="number" step="0.01" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: parseFloat(e.target.value) })} required className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-zinc-300">Estoque Atual</Label>
                  <Input type="number" value={form.current_stock || 0} onChange={(e) => setForm({ ...form, current_stock: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                <div>
                  <Label className="text-zinc-300">Estoque Mínimo</Label>
                  <Input type="number" value={form.min_stock || 0} onChange={(e) => setForm({ ...form, min_stock: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
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
      <Package className="h-5 w-5 text-amber-500" />
              {products.length} item(ns) — exibindo {paged.length} de {products.length}{products.filter(p => p.current_stock <= p.min_stock).length > 0 && (
        <span className="text-red-400 text-sm font-normal ml-1">— {products.filter(p => p.current_stock <= p.min_stock).length} estoque baixo</span>
      )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Nome</TableHead>
                <TableHead className="text-zinc-400">SKU</TableHead>
                <TableHead className="text-zinc-400">Custo</TableHead>
                <TableHead className="text-zinc-400">Venda</TableHead>
                <TableHead className="text-zinc-400">Estoque</TableHead>
                <TableHead className="text-zinc-400">Reservado</TableHead>
                <TableHead className="text-zinc-400"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
        {paged.map((product) => (
          <TableRow key={product.id} className="border-zinc-800 cursor-pointer hover:bg-zinc-800/50" onClick={() => openDetail(product)}>
            <TableCell className="text-white font-medium">{product.name}</TableCell>
            <TableCell className="text-amber-500 font-mono">{product.sku}</TableCell>
            <TableCell className="text-zinc-300">R$ {Number(product.cost_price).toFixed(2)}</TableCell>
            <TableCell className="text-zinc-300">R$ {Number(product.selling_price).toFixed(2)}</TableCell>
            <TableCell className="text-white">
              {product.current_stock}
              {product.current_stock <= product.min_stock && (
                <span className="ml-2 bg-red-500/20 text-red-400 text-xs px-1.5 py-0.5 rounded">Baixo</span>
              )}
            </TableCell>
            <TableCell className="text-orange-400">{product.reserved_stock}</TableCell>
            <TableCell>
              {isAdmin && (
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="sm" onClick={() => openEdit(product)} className="text-zinc-400 hover:text-white">
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(product.id)} className="text-zinc-400 hover:text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </TableCell>
          </TableRow>
        ))}
              {paged.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-zinc-500 py-8">Arsenal vazio. Cadastre o primeiro item.</TableCell>
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
            <DialogTitle className="text-white">Editar Item</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label className="text-zinc-300">Nome</Label>
              <Input value={editForm.name || ""} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div>
              <Label className="text-zinc-300">SKU</Label>
              <Input value={editForm.sku || ""} onChange={(e) => setEditForm({ ...editForm, sku: e.target.value })} className="bg-zinc-800 border-zinc-700 text-white" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-zinc-300">Preço Custo</Label>
                <Input type="number" step="0.01" value={editForm.cost_price ?? 0} onChange={(e) => setEditForm({ ...editForm, cost_price: parseFloat(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Preço Venda</Label>
                <Input type="number" step="0.01" value={editForm.selling_price ?? 0} onChange={(e) => setEditForm({ ...editForm, selling_price: parseFloat(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-zinc-300">Estoque</Label>
                <Input type="number" value={editForm.current_stock ?? 0} onChange={(e) => setEditForm({ ...editForm, current_stock: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
              <div>
                <Label className="text-zinc-300">Estoque Mínimo</Label>
                <Input type="number" value={editForm.min_stock ?? 0} onChange={(e) => setEditForm({ ...editForm, min_stock: parseInt(e.target.value) })} className="bg-zinc-800 border-zinc-700 text-white" />
              </div>
            </div>
            <Button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-black">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
      )}

      <Dialog open={!!detailProduct} onOpenChange={() => setDetailProduct(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Package className="h-5 w-5 text-amber-500" />
              {detailProduct?.name}
            </DialogTitle>
          </DialogHeader>
          {detailProduct && (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-zinc-500">SKU</p>
                  <p className="text-amber-500 font-mono">{detailProduct.sku}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Status</p>
                  <p className={detailProduct.current_stock <= detailProduct.min_stock ? "text-red-400" : "text-green-400"}>
                    {detailProduct.current_stock <= detailProduct.min_stock ? "Estoque Baixo" : "Normal"}
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500">Preço Custo</p>
                  <p className="text-white">R$ {Number(detailProduct.cost_price).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Preço Venda</p>
                  <p className="text-white">R$ {Number(detailProduct.selling_price).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Margem</p>
                  <p className="text-white">
                    {detailProduct.cost_price > 0
                      ? `${(((detailProduct.selling_price - detailProduct.cost_price) / detailProduct.cost_price) * 100).toFixed(1)}%`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500">Estoque Disponível</p>
                  <p className="text-white">{detailProduct.current_stock - detailProduct.reserved_stock}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Estoque Total</p>
                  <p className="text-white">{detailProduct.current_stock}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Reservado</p>
                  <p className="text-orange-400">{detailProduct.reserved_stock}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
