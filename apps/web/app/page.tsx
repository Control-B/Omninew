import Link from "next/link";
import { ArrowRight, Bot, PhoneCall, ShoppingBag, Sparkles } from "lucide-react";
import { Suspense } from "react";

import { ChatWidget } from "@/components/widget/chat-widget";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const featureCards = [
  {
    title: "Storefront conversion assistant",
    body: "Recommend products, answer objections, and encourage larger carts without touching checkout.",
    icon: ShoppingBag,
  },
  {
    title: "Omniweb AI engine",
    body: "Every customer message is routed through Omniweb's AI engine for accurate product recommendations and contextual support answers.",
    icon: Bot,
  },
  {
    title: "Voice + telephony",
    body: "The widget includes voice-ready controls and can expand into cloud voice sessions and AI phone support.",
    icon: PhoneCall,
  },
];

export default function HomePage() {
  return (
    <main className="mx-auto flex w-full max-w-[1600px] flex-col gap-14 px-6 py-12 xl:px-8">
      <section className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
        <div className="space-y-6">
          <Badge className="bg-accent/15 text-indigo-100">Omniweb product · Shopify AI assistant</Badge>
          <div className="space-y-4">
            <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white md:text-6xl">
              Omniweb helps Shopify brands convert more shoppers and automate support.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              Omniweb combines a merchant dashboard, embedded storefront assistant, product recommendations, and voice-ready support surfaces.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="inline-flex h-12 items-center justify-center rounded-xl bg-accent px-5 text-base font-medium text-white transition hover:bg-[#5d4ef2]"
            >
              Open dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              href="/widget-demo"
              className="inline-flex h-12 items-center justify-center rounded-xl border border-white/15 px-5 text-base font-medium text-white transition hover:bg-white/10"
            >
              Launch widget demo
            </Link>
          </div>
        </div>
        <Card className="space-y-5 rounded-[32px] border-white/8 bg-gradient-to-br from-[#0c1424] to-[#0b1020] p-6 shadow-glow">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent/15 text-accent2">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <div className="text-lg font-semibold">Operator surfaces</div>
              <div className="text-sm text-slate-400">Clean control layers for merchants, assistants, and storefront conversations.</div>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {featureCards.map((feature) => (
              <div key={feature.title} className="rounded-2xl border border-white/8 bg-white/[0.04] p-4">
                <feature.icon className="mb-3 h-5 w-5 text-accent2" />
                <div className="text-sm font-medium text-white">{feature.title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{feature.body}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        <Card className="rounded-[28px] border-white/8 bg-[#0c1424]/95 p-5 shadow-glow">
          <div className="text-xs uppercase tracking-[0.18em] text-slate-500">For merchants</div>
          <div className="mt-4 text-2xl font-semibold text-white">A dashboard that feels operational</div>
          <p className="mt-3 text-sm leading-7 text-slate-300">Give merchants a simple command center for store connection, assistant tuning, transcripts, and lead capture.</p>
        </Card>
        <Card className="rounded-[28px] border-white/8 bg-[#0c1424]/95 p-5 shadow-glow">
          <div className="text-xs uppercase tracking-[0.18em] text-slate-500">For shoppers</div>
          <div className="mt-4 text-2xl font-semibold text-white">A lightweight storefront assistant</div>
          <p className="mt-3 text-sm leading-7 text-slate-300">Surface recommendations, answer policy questions, and escalate into richer support experiences when needed.</p>
        </Card>
        <Card className="rounded-[28px] border-white/8 bg-[#0c1424]/95 p-5 shadow-glow">
          <div className="text-xs uppercase tracking-[0.18em] text-slate-500">For Omniweb</div>
          <div className="mt-4 text-2xl font-semibold text-white">A branded product, not a vendor wrapper</div>
          <p className="mt-3 text-sm leading-7 text-slate-300">Position Omniweb as the product experience across merchants, assistants, and storefront conversations.</p>
        </Card>
      </section>
      <Suspense fallback={null}>
        <ChatWidget />
      </Suspense>
    </main>
  );
}
