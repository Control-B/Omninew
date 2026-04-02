import {
  Activity,
  ArrowRight,
  Bot,
  MessageSquareText,
  PhoneCall,
  UserRoundPlus,
} from "lucide-react";
import Link from "next/link";

import { StatCard } from "@/components/dashboard/stat-card";
import { Card } from "@/components/ui/card";
import { sampleLeads, sampleTranscripts } from "@/lib/data";

export default function DashboardOverviewPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[30px] border border-white/8 bg-[linear-gradient(135deg,rgba(12,20,36,0.98),rgba(10,16,29,0.94))] p-6 shadow-glow">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Overview</div>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">OmniNew dashboard</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
              Omniweb gives each merchant a clean operations view for conversations, buyer intent, sync health, and assistant performance.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              href="/dashboard/connect"
              className="inline-flex items-center justify-center rounded-2xl border border-accent/30 bg-accent/15 px-4 py-3 text-sm font-medium text-white transition hover:bg-accent/20"
            >
              Connect a store
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              href="/dashboard/sync"
              className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-white/[0.07]"
            >
              Run catalog sync
            </Link>
          </div>
        </div>
      </section>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Conversations" value="184" trend="+12% this week" />
        <StatCard label="Leads captured" value="27" trend="+8 high-intent" />
        <StatCard label="Voice sessions" value="11" trend="Voice ready" />
        <StatCard label="Sync freshness" value="14m" trend="Catalog current" />
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="rounded-[30px] border-white/8 bg-[#0c1424]/95 p-6 shadow-glow">
          <div className="flex items-center gap-3 text-white">
            <Activity className="h-5 w-5 text-accent2" />
            <h2 className="text-lg font-semibold">Recent activity</h2>
          </div>
          <div className="mt-5 space-y-3 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">Product sync refreshed inventory and policy data for the latest connected store.</div>
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">OmniNew prompt behavior was tuned for stronger bundle recommendations and cleaner support handoff.</div>
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">Voice controls are available in the widget shell for future cloud voice and telephony expansion.</div>
          </div>
        </Card>
        <Card className="rounded-[30px] border-white/8 bg-[#0c1424]/95 p-6 shadow-glow">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <Bot className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Assistant mode</div>
              <div className="mt-1 text-xs text-slate-400">Balanced sales + support</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <UserRoundPlus className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Lead triggers</div>
              <div className="mt-1 text-xs text-slate-400">Premium items, wholesale, callback requests</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <MessageSquareText className="mb-3 h-5 w-5 text-accent2" />
              <div className="text-sm font-medium text-white">Transcript health</div>
              <div className="mt-1 text-xs text-slate-400">{sampleTranscripts.length} demo sessions in view</div>
            </div>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/8 bg-[#0a101b] p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-white">
                <PhoneCall className="h-4 w-4 text-accent2" />
                Voice expansion
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Ready for voice-driven support flows when you want to introduce higher-touch customer handling.
              </p>
            </div>
            <div className="rounded-2xl border border-white/8 bg-[#0a101b] p-4 text-sm text-slate-300">
              Latest lead: <span className="font-medium text-white">{sampleLeads[0]?.name}</span> requested help with <span className="font-medium text-white">{sampleLeads[0]?.productInterest}</span>.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
