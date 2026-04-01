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
    <Card className="space-y-3 p-5">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="flex items-end justify-between gap-3">
        <div className="text-3xl font-semibold text-white">{value}</div>
        <div className="flex items-center gap-1 text-xs text-green-300">
          <ArrowUpRight className="h-4 w-4" />
          {trend}
        </div>
      </div>
    </Card>
  );
}
