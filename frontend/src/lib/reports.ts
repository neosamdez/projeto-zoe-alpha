import { apiFetch } from "@/lib/api";

export async function getMonthlyReport(
  month: number,
  year: number,
  format: "pdf" | "csv" | "json" = "json"
) {
  if (format === "pdf" || format === "csv") {
    const res = await apiFetch<Response>(
      `/reports/monthly?month=${month}&year=${year}&format=${format}`,
      { raw: true }
    );
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

  return apiFetch(`/reports/monthly?month=${month}&year=${year}&format=json`);
}
