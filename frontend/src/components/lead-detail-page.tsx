"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getLead } from "@/lib/leads";
import { getOrders } from "@/lib/orders";
import type { Lead, ServiceOrder } from "@/types";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowLeft, Mail, Phone, User, ClipboardList } from "lucide-react";
import { toast } from "sonner";

interface LeadDetailPageProps {
  leadId: string;
}

export function LeadDetailPage({ leadId }: LeadDetailPageProps) {
  const router = useRouter();
  const [lead, setLead] = useState<Lead | null>(null);
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [leadData, ordersData] = await Promise.all([
          getLead(leadId),
          getOrders(),
        ]);
        setLead(leadData);
        setOrders(ordersData.filter((o) => o.lead_id === leadId));
      } catch {
        toast.error("Erro ao carregar dados do cliente");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [leadId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-zinc-500">Carregando...</p>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-zinc-500">Cliente não encontrado</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.push("/leads")} className="text-zinc-400 hover:text-white">
          <ArrowLeft className="h-4 w-4 mr-1" /> Voltar
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-white">{lead.name}</h1>
          <p className="text-zinc-400 mt-1">Ficha do Cliente</p>
        </div>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <User className="h-5 w-5 text-amber-500" />
            Informações
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-zinc-500">E-mail</p>
              <p className="text-white flex items-center gap-1"><Mail className="h-3 w-3 text-zinc-400" /> {lead.email}</p>
            </div>
            <div>
              <p className="text-zinc-500">Telefone</p>
              <p className="text-white flex items-center gap-1"><Phone className="h-3 w-3 text-zinc-400" /> {lead.phone}</p>
            </div>
            {lead.device_interest && (
              <div>
                <p className="text-zinc-500">Dispositivo de Interesse</p>
                <p className="text-white">{lead.device_interest}</p>
              </div>
            )}
            {lead.notes && (
              <div>
                <p className="text-zinc-500">Observações</p>
                <p className="text-zinc-300">{lead.notes}</p>
              </div>
            )}
            <div>
              <p className="text-zinc-500">Cadastro</p>
              <p className="text-white">{new Date(lead.created_at).toLocaleDateString("pt-BR")}</p>
            </div>
            <div>
              <p className="text-zinc-500">Total OS</p>
              <p className="text-amber-500 font-semibold">{lead.total_os}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-amber-500" />
            Ordens de Serviço ({orders.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {orders.length === 0 ? (
            <p className="text-zinc-500 text-center py-8">Nenhuma OS vinculada a este cliente</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800">
                  <TableHead className="text-zinc-400">Protocolo</TableHead>
                  <TableHead className="text-zinc-400">Dispositivo</TableHead>
                  <TableHead className="text-zinc-400">Status</TableHead>
                  <TableHead className="text-zinc-400">Técnico</TableHead>
                  <TableHead className="text-zinc-400">Valor</TableHead>
                  <TableHead className="text-zinc-400">Data</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id} className="border-zinc-800">
                    <TableCell className="text-amber-500 font-mono font-semibold">{order.protocol}</TableCell>
                    <TableCell className="text-zinc-300 max-w-48 truncate">{order.device_info}</TableCell>
                    <TableCell><StatusBadge status={order.status} /></TableCell>
                    <TableCell className="text-zinc-400">{order.technician?.name || "—"}</TableCell>
                    <TableCell className="text-white">R$ {Number(order.total_value).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className="text-zinc-500">{new Date(order.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
