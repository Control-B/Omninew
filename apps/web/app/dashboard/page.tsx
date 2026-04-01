import { Activity, Bot, MessageSquareText, UserRoundPlus } from "lucide-react";

import { StatCard } from "@/components/dashboard/stat-card";
import { Card } from "@/components/ui/card";
import { sampleLeads, sampleTranscripts } from "@/lib/data";

export default function DashboardOverviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Overview</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Merchant dashboard</h1>
        <p className="mt-2 text-sm text-slate-300">
          A conversion-focused control center for Shopify AI chat, LiveKit voice, transcripts, and lead capture.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Conversations" value="184" trend="+12% this week" />
        <StatCard label="Leads captured" value="27" trend="+8 high-intent" />
        <StatCard label="Voice sessions" value="11" trend="LiveKit ready" />
        <StatCard label="Sync freshness" value="14m" trend="catalog current" />
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="space-y-4">
          <div className="flex items-center gap-3 text-white">
            <Activity className="h-5 w-5 text-accent2" />
            <h2 className="text-lg font-semibold">Recent activity</h2>
          </div>
          <div className="space-y-3 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">Product sync refreshed inventory and policy data for the last connected store.</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">DO AI Agent prompt tuned for stronger bundle recommendations and clearer support handoff behavior.</div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">LiveKit voice controls are enabled in the widget shell for cloud voice and telephony expansion.</div>
          </div>
        </Card>
        <Card className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <Bot className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Assistant mode</div>
              <div className="mt-1 text-xs text-slate-400">Balanced sales + support</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <UserRoundPlus className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Lead triggers</div>
              <div className="mt-1 text-xs text-slate-400">Premium items, wholesale, callback requests</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <MessageSquareText className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Transcript health</div>
              <div className="mt-1 text-xs text-slate-400">{sampleTranscripts.length} demo sessions in view</div>
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-sm text-slate-300">
            Latest lead: <span className="font-medium text-white">{sampleLeads[0]?.name}</span> requested help with <span className="font-medium text-white">{sampleLeads[0]?.productInterest}</span>.
          </div>
        </Card>
      </div>
    </div>
  );
}
