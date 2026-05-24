import { apiFetch } from "@/lib/api";

export async function getMonthlyReport(
  month: number,
  year: number,
  format: "pdf" | "csv" | "json" = "json"
) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const res = await fetch(
    `${baseUrl}/reports/monthly?month=${month}&year=${year}&format=${format}`,
    {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    }
  );

  if (!res.ok) {
    throw new Error("Erro ao gerar relatório");
  }

  if (format === "pdf" || format === "csv") {
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `relatorio_${year}_${month.toString().padStart(2, "0")}.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    return;
  }

  return res.json();
}
