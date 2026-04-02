"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { getAssistantConfig, updateAssistantConfig } from "@/lib/api";
import { getMerchantContext, setMerchantContext } from "@/lib/tenant-context";

const basePrompt = `You are an AI sales and support assistant for a Shopify store.\n\nGoals:\n- help customers find the right product\n- answer questions clearly and accurately\n- recommend relevant products naturally\n- capture contact details on strong buying intent`;

export function AssistantConfigForm() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [tone, setTone] = useState<"sales" | "balanced" | "support">("balanced");
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [merchantInstructions, setMerchantInstructions] = useState(
    "Focus on high-converting bundles, mention shipping policy when asked, and collect email for premium product inquiries.",
  );
  const [assistantName, setAssistantName] = useState("Omniweb assistant");
  const [welcomeMessage, setWelcomeMessage] = useState(
    "Hi! I can recommend products, answer policy questions, and help capture leads for premium items.",
  );

  useEffect(() => {
    async function loadConfig() {
      const context = getMerchantContext();
      if (!context) {
        setStatus("Create a tenant on the Connect Store page first.");
        setLoading(false);
        return;
      }

      try {
        const config = await getAssistantConfig({
          tenantId: context.tenantId,
          storeId: context.storeId,
        });
        setTone(config.tone);
        setVoiceEnabled(config.voice_enabled);
        setMerchantInstructions(config.system_prompt ?? merchantInstructions);
        setAssistantName(config.assistant_name);
        setWelcomeMessage(config.welcome_message);
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Failed to load assistant config.");
      } finally {
        setLoading(false);
      }
    }

    void loadConfig();
  }, []);

  const preview = useMemo(() => {
    return `${basePrompt}\n\nAssistant name: ${assistantName}\nTone mode: ${tone}\nWelcome message: ${welcomeMessage}\n\nMerchant instructions:\n${merchantInstructions}`;
  }, [assistantName, merchantInstructions, tone, welcomeMessage]);

  async function handleSave() {
    const context = getMerchantContext();
    if (!context) {
      setStatus("Create a tenant on the Connect Store page first.");
      return;
    }

    setSaving(true);
    setStatus("");

    try {
      await updateAssistantConfig({
        tenant_id: context.tenantId,
        store_id: context.storeId,
        assistant_name: assistantName,
        tone,
        system_prompt: merchantInstructions,
        welcome_message: welcomeMessage,
        voice_enabled: voiceEnabled,
        sales_mode_enabled: true,
        support_mode_enabled: true,
      });
      setMerchantContext({
        ...context,
        assistantName,
        tone,
        welcomeMessage,
      });
      setStatus("Assistant settings saved.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to save assistant config.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <Card className="space-y-5">
        <div>
          <div className="mb-2 text-sm text-slate-400">Assistant name</div>
          <Input value={assistantName} onChange={(event) => setAssistantName(event.target.value)} />
        </div>
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
          <div className="mb-2 text-sm text-slate-400">Welcome message</div>
          <Textarea value={welcomeMessage} onChange={(event) => setWelcomeMessage(event.target.value)} />
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
            {voiceEnabled ? "Voice ready" : "Text-only mode"}
          </Badge>
          <Button disabled={loading || saving} onClick={() => void handleSave()}>
            {saving ? "Saving..." : "Save config"}
          </Button>
          {status ? <span className="text-sm text-slate-300">{status}</span> : null}
        </div>
      </Card>
      <Card className="space-y-4">
        <div className="text-sm text-slate-400">Prompt preview</div>
        <pre className="whitespace-pre-wrap rounded-2xl bg-slate-950/60 p-4 text-xs text-slate-200">{preview}</pre>
      </Card>
    </div>
  );
}
