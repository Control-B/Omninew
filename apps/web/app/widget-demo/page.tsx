import { Suspense } from "react";

import { ChatWidget } from "@/components/widget/chat-widget";
import { Card } from "@/components/ui/card";
import { embedSnippet } from "./embed-snippet";

export default function WidgetDemoPage() {
  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Widget demo</div>
        <h1 className="mt-2 text-4xl font-semibold text-white">Storefront assistant shell</h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
          This demo shows the floating widget, product suggestion cards, and LiveKit-ready voice state that can later be embedded into a Shopify storefront.
        </p>
      </div>
      <Card className="space-y-4">
        <div className="text-sm font-medium text-white">Planned embed snippet</div>
        <pre className="overflow-x-auto rounded-2xl bg-slate-950/60 p-4 text-xs text-slate-200">{embedSnippet}</pre>
      </Card>
      <div className="min-h-[500px] rounded-3xl border border-dashed border-white/10 bg-slate-950/30 p-6">
        <div className="max-w-2xl space-y-3 text-slate-300">
          <h2 className="text-xl font-semibold text-white">Demo storefront</h2>
          <p>
            Imagine this as the merchant’s product detail or collection page. The widget stays lightweight, nudges toward relevant bundles, answers policy questions, and can escalate into voice.
          </p>
        </div>
        <Suspense fallback={null}>
          <ChatWidget />
        </Suspense>
      </div>
    </main>
  );
}
