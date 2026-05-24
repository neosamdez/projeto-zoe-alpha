"use client";

import { useState } from "react";
import { getMonthlyReport } from "@/lib/reports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { FileBarChart, Download, FileText } from "lucide-react";
import { toast } from "sonner";

export function ReportsPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<any>(null);

  const handleGenerate = async (format: "pdf" | "csv" | "json") => {
    setLoading(true);
    try {
      if (format === "json") {
        const data = await getMonthlyReport(month, year, "json");
        setReportData(data);
      } else {
        await getMonthlyReport(month, year, format);
        toast.success(`Relatório ${format.toUpperCase()} gerado com sucesso`);
      }
    } catch (err: any) {
      toast.error(err.message || "Erro ao gerar relatório");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Relatórios</h1>
        <p className="text-zinc-400 mt-1">Registro de Guerra — Balanço Financeiro</p>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileBarChart className="h-5 w-5 text-amber-500" />
            Gerar Relatório Mensal
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-4 max-w-xs">
            <div>
              <Label className="text-zinc-300">Mês</Label>
              <Input
                type="number"
                min={1}
                max={12}
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
                className="bg-zinc-800 border-zinc-700 text-white"
              />
            </div>
            <div>
              <Label className="text-zinc-300">Ano</Label>
              <Input
                type="number"
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
                className="bg-zinc-800 border-zinc-700 text-white"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={() => handleGenerate("pdf")}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              <Download className="h-4 w-4 mr-2" /> PDF
            </Button>
            <Button
              onClick={() => handleGenerate("csv")}
              disabled={loading}
              variant="outline"
              className="border-zinc-700 text-white hover:bg-zinc-800"
            >
              <Download className="h-4 w-4 mr-2" /> CSV
            </Button>
            <Button
              onClick={() => handleGenerate("json")}
              disabled={loading}
              variant="outline"
              className="border-zinc-700 text-white hover:bg-zinc-800"
            >
              <FileText className="h-4 w-4 mr-2" /> Visualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {reportData && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-white">
              Resumo — {reportData.month.toString().padStart(2, "0")}/{reportData.year}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center p-4 bg-zinc-800 rounded-lg">
                <p className="text-sm text-zinc-400 mb-1">Receita Bruta</p>
                <p className="text-2xl font-bold text-green-400">
                  R$ {Number(reportData.revenue).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-center p-4 bg-zinc-800 rounded-lg">
                <p className="text-sm text-zinc-400 mb-1">Custos</p>
                <p className="text-2xl font-bold text-orange-400">
                  R$ {Number(reportData.costs).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-center p-4 bg-zinc-800 rounded-lg">
                <p className="text-sm text-zinc-400 mb-1">Lucro Líquido</p>
                <p className="text-2xl font-bold text-emerald-400">
                  R$ {Number(reportData.profit).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
