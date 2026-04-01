import { Card } from "@/components/ui/card";
import { sampleTranscripts } from "@/lib/data";

export default function TranscriptsPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Transcripts</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Review customer conversations</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          Store text and voice transcripts in Supabase so merchants can audit answers, measure support load reduction, and spot sales opportunities.
        </p>
      </div>
      <div className="grid gap-4">
        {sampleTranscripts.map((item) => (
          <Card key={item.id} className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-lg font-medium text-white">{item.customer}</div>
                <div className="text-sm text-slate-400">{item.channel}</div>
              </div>
              <div className="text-xs text-slate-500">{new Date(item.createdAt).toLocaleString()}</div>
            </div>
            <p className="text-sm leading-7 text-slate-300">{item.summary}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
