import { Card } from "@/components/ui/card";
import { sampleLeads } from "@/lib/data";

export default function LeadsPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Leads</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Captured buying intent</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          High-ticket and high-intent shoppers can be routed into a follow-up workflow once the assistant detects strong purchase signals.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {sampleLeads.map((lead) => (
          <Card key={lead.id} className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-lg font-medium text-white">{lead.name}</div>
                <div className="text-sm text-slate-400">{lead.email}</div>
              </div>
              <div className="text-xs uppercase tracking-[0.2em] text-accent2">{lead.intent}</div>
            </div>
            <div className="text-sm text-slate-300">Interested in: {lead.productInterest}</div>
            <div className="text-xs text-slate-500">Captured {new Date(lead.createdAt).toLocaleString()}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
