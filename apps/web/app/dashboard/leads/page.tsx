import { Card } from "@/components/ui/card";
import { sampleLeads } from "@/lib/data";

export default function LeadsPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Leads</div>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Captured buying intent</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          High-ticket and high-intent shoppers can be routed into a follow-up workflow once the assistant detects strong purchase signals.
        </p>
      </div>
      <Card className="overflow-hidden rounded-[28px] border-white/8 bg-[#0c1424]/95 p-0 shadow-glow">
        <div className="grid grid-cols-[1.3fr_1.5fr_1fr] border-b border-white/8 px-5 py-4 text-xs uppercase tracking-[0.18em] text-slate-500">
          <div>Lead</div>
          <div>Intent</div>
          <div>Captured</div>
        </div>
        {sampleLeads.map((lead) => (
          <div key={lead.id} className="grid grid-cols-[1.3fr_1.5fr_1fr] items-center border-b border-white/6 px-5 py-4 last:border-b-0">
            <div>
              <div className="text-sm font-medium text-white">{lead.name}</div>
              <div className="mt-1 text-xs text-slate-400">{lead.email}</div>
            </div>
            <div>
              <div className="inline-flex rounded-full bg-accent/12 px-3 py-1 text-xs text-accent2">{lead.intent}</div>
              <div className="mt-2 text-sm text-slate-300">{lead.productInterest}</div>
            </div>
            <div className="text-sm text-slate-400">{new Date(lead.createdAt).toLocaleString()}</div>
          </div>
        ))}
      </Card>
    </div>
  );
}
