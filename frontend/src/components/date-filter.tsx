"use client";

import { Input } from "@/components/ui/input";

const MONTHS = [
  { value: 1, label: "Janeiro" },
  { value: 2, label: "Fevereiro" },
  { value: 3, label: "Março" },
  { value: 4, label: "Abril" },
  { value: 5, label: "Maio" },
  { value: 6, label: "Junho" },
  { value: 7, label: "Julho" },
  { value: 8, label: "Agosto" },
  { value: 9, label: "Setembro" },
  { value: 10, label: "Outubro" },
  { value: 11, label: "Novembro" },
  { value: 12, label: "Dezembro" },
];

interface DateFilterProps {
  month: number;
  year: number;
  onMonthChange: (m: number) => void;
  onYearChange: (y: number) => void;
}

export function DateFilter({ month, year, onMonthChange, onYearChange }: DateFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <select
        value={month}
        onChange={(e) => onMonthChange(Number(e.target.value))}
        className="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg px-3 py-2"
      >
        {MONTHS.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
          </option>
        ))}
      </select>
      <Input
        type="number"
        value={year}
        onChange={(e) => onYearChange(Number(e.target.value))}
        min={2020}
        max={2100}
        className="w-24 bg-zinc-800 border border-zinc-700 text-white"
      />
    </div>
  );
}
