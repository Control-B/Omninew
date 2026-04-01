"use client";

import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const basePrompt = `You are an AI sales and support assistant for a Shopify store.\n\nGoals:\n- help customers find the right product\n- answer questions clearly and accurately\n- recommend relevant products naturally\n- capture contact details on strong buying intent`;

export function AssistantConfigForm() {
  const [tone, setTone] = useState<"sales" | "balanced" | "support">("balanced");
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [merchantInstructions, setMerchantInstructions] = useState(
    "Focus on high-converting bundles, mention shipping policy when asked, and collect email for premium product inquiries.",
  );

  const preview = useMemo(() => {
    return `${basePrompt}\n\nTone mode: ${tone}\n\nMerchant instructions:\n${merchantInstructions}`;
  }, [merchantInstructions, tone]);

  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <Card className="space-y-5">
        <div>
          <div className="text-sm text-slate-400">Assistant tone</div>
          <div className="mt-3 flex flex-wrap gap-3">
            {(["sales", "balanced", "support"] as const).map((value) => (
              <Button
                key={value}
                variant={tone === value ? "primary" : "secondary"}
                onClick={() => setTone(value)}
              >
                {value}
              </Button>
            ))}
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm text-slate-400">Merchant instructions</div>
          <Textarea value={merchantInstructions} onChange={(event) => setMerchantInstructions(event.target.value)} />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant={voiceEnabled ? "primary" : "outline"} onClick={() => setVoiceEnabled((current) => !current)}>
            {voiceEnabled ? "Voice enabled" : "Voice disabled"}
          </Button>
          <Badge className={voiceEnabled ? "bg-green-500/15 text-green-200" : "bg-amber-500/15 text-amber-200"}>
            {voiceEnabled ? "LiveKit ready" : "Text-only mode"}
          </Badge>
        </div>
      </Card>
      <Card className="space-y-4">
        <div className="text-sm text-slate-400">Prompt preview</div>
        <pre className="whitespace-pre-wrap rounded-2xl bg-slate-950/60 p-4 text-xs text-slate-200">{preview}</pre>
      </Card>
    </div>
  );
}
