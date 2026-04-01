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
    title: "DO AI text orchestration",
    body: "Frontend is ready to send customer chat context into your FastAPI orchestration layer and DigitalOcean AI Agent.",
    icon: Bot,
  },
  {
    title: "LiveKit voice + telephony",
    body: "The widget includes voice-ready controls and can expand into cloud voice sessions and AI phone support.",
    icon: PhoneCall,
  },
];

export default function HomePage() {
  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-16 px-6 py-14">
      <section className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-6">
          <Badge className="bg-accent/15 text-indigo-100">Shopify-focused AI assistant MVP</Badge>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-white md:text-6xl">
              Increase conversions and automate support with a storefront AI assistant.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              OmniNew combines a merchant dashboard, embedded chat widget, product recommendations, and LiveKit-ready voice surfaces for Shopify stores.
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
        <Card className="space-y-5 border-white/15 bg-gradient-to-br from-slate-950/80 to-slate-900/70">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent/15 text-accent2">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <div className="text-lg font-semibold">Launch-ready surfaces</div>
              <div className="text-sm text-slate-400">Dashboard, widget, and backend hooks are scaffolded.</div>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {featureCards.map((feature) => (
              <div key={feature.title} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <feature.icon className="mb-3 h-5 w-5 text-accent2" />
                <div className="text-sm font-medium text-white">{feature.title}</div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{feature.body}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>
      <section className="grid gap-6 md:grid-cols-3">
        {featureCards.map((feature) => (
          <Card key={feature.title} className="space-y-3">
            <feature.icon className="h-6 w-6 text-accent2" />
            <h2 className="text-xl font-semibold text-white">{feature.title}</h2>
            <p className="text-sm leading-7 text-slate-300">{feature.body}</p>
          </Card>
        ))}
      </section>
      <Suspense fallback={null}>
        <ChatWidget />
      </Suspense>
    </main>
  );
}
