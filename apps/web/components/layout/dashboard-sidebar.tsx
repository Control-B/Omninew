"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bot,
  Boxes,
  LayoutDashboard,
  Link2,
  MessageSquareText,
  UserRoundPlus,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { dashboardNav } from "@/lib/data";
import { cn } from "@/lib/utils";

const navIcons = {
  "/dashboard": LayoutDashboard,
  "/dashboard/connect": Link2,
  "/dashboard/sync": Boxes,
  "/dashboard/assistant": Bot,
  "/dashboard/transcripts": MessageSquareText,
  "/dashboard/leads": UserRoundPlus,
} as const;

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full max-w-xs rounded-[28px] border border-white/8 bg-[#0b1220]/85 p-4 shadow-glow backdrop-blur xl:sticky xl:top-24 xl:h-fit">
      <div className="mb-5 rounded-3xl border border-white/8 bg-gradient-to-br from-[#13213a] to-[#0d1728] p-5">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Omniweb</div>
            <h2 className="mt-2 text-xl font-semibold text-white">OmniNew</h2>
          </div>
          <Badge className="bg-success/15 text-green-200">Starter</Badge>
        </div>
        <p className="text-sm leading-6 text-slate-300">
          Manage store connection, assistant behavior, conversations, and buyer intent from one place.
        </p>
        <div className="mt-5 rounded-2xl border border-white/8 bg-white/[0.03] p-4">
          <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Current workspace</div>
          <div className="mt-2 text-sm font-medium text-white">Merchant operations</div>
          <div className="mt-1 text-xs text-slate-400">Shopify AI sales + support control room</div>
        </div>
      </div>
      <nav className="space-y-2">
        {dashboardNav.map((item) => {
          const active = pathname === item.href;
          const Icon = navIcons[item.href as keyof typeof navIcons] ?? LayoutDashboard;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-start gap-3 rounded-2xl border px-4 py-3 transition",
                active
                  ? "border-accent/40 bg-accent/12 text-white shadow-[0_0_0_1px_rgba(109,94,252,0.15)]"
                  : "border-white/5 bg-white/[0.03] text-slate-300 hover:border-white/12 hover:bg-white/[0.05]",
              )}
            >
              <div
                className={cn(
                  "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border",
                  active
                    ? "border-accent/30 bg-accent/15 text-accent2"
                    : "border-white/8 bg-white/[0.04] text-slate-400",
                )}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <div className="text-sm font-medium">{item.label}</div>
                <div className="mt-1 text-xs text-slate-400">{item.description}</div>
              </div>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
