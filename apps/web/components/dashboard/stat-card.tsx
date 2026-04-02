import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";

export function StatCard({
  label,
  value,
  trend,
}: {
  label: string;
  value: string;
  trend: string;
}) {
  return (
    <Card className="rounded-[28px] border-white/8 bg-[#0c1424]/95 p-5 shadow-glow">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-6 flex items-end justify-between gap-3">
        <div className="text-4xl font-semibold tracking-tight text-white">{value}</div>
        <div className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-green-300">
          <ArrowUpRight className="h-4 w-4" />
          {trend}
        </div>
      </div>
    </Card>
  );
}
