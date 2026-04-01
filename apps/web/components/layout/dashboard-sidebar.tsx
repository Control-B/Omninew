"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { dashboardNav } from "@/lib/data";
import { cn } from "@/lib/utils";

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full max-w-xs rounded-3xl border border-white/10 bg-slate-950/40 p-4 backdrop-blur xl:sticky xl:top-24 xl:h-fit">
      <div className="mb-6 rounded-2xl border border-white/10 bg-gradient-to-br from-accent/15 to-accent2/10 p-4">
        <Badge className="mb-3 bg-success/20 text-green-200">MVP ready</Badge>
        <h2 className="text-lg font-semibold text-white">Merchant cockpit</h2>
        <p className="mt-2 text-sm text-slate-300">
          Connect your Shopify store, shape the assistant behavior, and review leads plus transcripts.
        </p>
      </div>
      <nav className="space-y-2">
        {dashboardNav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block rounded-2xl border px-4 py-3 transition",
                active
                  ? "border-accent/60 bg-accent/15 text-white"
                  : "border-white/5 bg-white/5 text-slate-300 hover:border-white/15 hover:bg-white/10",
              )}
            >
              <div className="text-sm font-medium">{item.label}</div>
              <div className="mt-1 text-xs text-slate-400">{item.description}</div>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
