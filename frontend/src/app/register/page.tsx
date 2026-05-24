"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Zap, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { API_URL } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm) {
      toast.error("As senhas não coincidem");
      return;
    }
    if (form.password.length < 8) {
      toast.error("A senha deve ter no mínimo 8 caracteres");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: form.full_name,
          email: form.email,
          password: form.password,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Erro ao registrar" }));
        throw new Error(err.detail || "Erro ao registrar");
      }
      toast.success("Registro concluído! Faça login para entrar.");
      router.push("/login");
    } catch (err: any) {
      toast.error(err.message || "Erro ao registrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 px-4">
      <Card className="w-full max-w-md bg-zinc-900 border-zinc-800">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-amber-500/10 rounded-xl">
              <Zap className="h-8 w-8 text-amber-500" />
            </div>
          </div>
          <CardTitle className="text-2xl text-white">Criar Conta</CardTitle>
          <CardDescription className="text-zinc-400">
            Novo Operador — Crie sua Cidadela
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="full_name" className="text-zinc-300">Nome Completo</Label>
              <Input
                id="full_name"
                placeholder="Seu nome de operador"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email" className="text-zinc-300">E-mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="operador@amenti.io"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-zinc-300">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm" className="text-zinc-300">Confirmar Senha</Label>
              <Input
                id="confirm"
                type="password"
                placeholder="Repita a senha"
                value={form.confirm}
                onChange={(e) => setForm({ ...form, confirm: e.target.value })}
                required
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
              />
            </div>
            <Button
              type="submit"
              className="w-full bg-amber-500 hover:bg-amber-600 text-black font-semibold"
              disabled={loading}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Forjar Minha Cidadela
            </Button>
          </form>
          <p className="text-center text-sm text-zinc-500 mt-4">
            Já possui conta?{" "}
            <a href="/login" className="text-amber-500 hover:underline">Entrar</a>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
