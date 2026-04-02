"use client";

import { Mic, Send, Sparkles, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getWidgetPublicConfig, sendChatMessage } from "@/lib/api";
import { sampleSuggestions } from "@/lib/data";
import type { ChatMessage, ProductSuggestion, PublicWidgetConfig } from "@/lib/types";

import { MessageBubble } from "./message-bubble";
import { ProductSuggestionCard } from "./product-suggestion-card";
import { VoiceStatus } from "./voice-status";

const starterMessages: ChatMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    content: "Hi! I can recommend products, answer policy questions, and help capture leads for premium items.",
    createdAt: new Date().toISOString(),
  },
];

function fallbackReply(message: string) {
  const normalized = message.toLowerCase();
  if (normalized.includes("shipping") || normalized.includes("return")) {
    return {
      reply: "I can help with shipping and return guidance. For the MVP, policy answers come from synced Shopify store policies.",
      suggestions: [],
      lead_capture_detected: false,
    };
  }

  if (normalized.includes("recommend") || normalized.includes("bundle") || normalized.includes("gift")) {
    return {
      reply: "Based on that intent, I’d start with these relevant products and bundles.",
      suggestions: sampleSuggestions,
      lead_capture_detected: false,
    };
  }

  if (normalized.includes("call me") || normalized.includes("bulk") || normalized.includes("wholesale")) {
    return {
      reply: "This sounds high-intent. I can capture lead details for a follow-up from sales or support.",
      suggestions: sampleSuggestions.slice(0, 1),
      lead_capture_detected: true,
    };
  }

  return {
    reply: "I can help with product discovery, policies, order help, and upsell recommendations. Tell me what the shopper wants to achieve.",
    suggestions: [],
    lead_capture_detected: false,
  };
}

export function ChatWidget() {
  const searchParams = useSearchParams();
  const widgetKey = searchParams.get("widgetKey");
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(starterMessages);
  const [suggestions, setSuggestions] = useState<ProductSuggestion[]>(sampleSuggestions);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [voiceConnected] = useState(false);
  const [widgetConfig, setWidgetConfig] = useState<PublicWidgetConfig | null>(null);

  useEffect(() => {
    async function loadWidgetConfig() {
      if (!widgetKey) {
        return;
      }

      try {
        const config = await getWidgetPublicConfig(widgetKey);
        setWidgetConfig(config);
        setVoiceEnabled(config.voice_enabled);
        setMessages([
          {
            id: "welcome",
            role: "assistant",
            content: config.welcome_message,
            createdAt: new Date().toISOString(),
          },
        ]);
      } catch {
        // keep fallback demo content
      }
    }

    void loadWidgetConfig();
  }, [widgetKey]);

  const transcriptCount = useMemo(() => messages.length - 1, [messages.length]);

  function toggleWidget() {
    setOpen((current) => !current);
  }

  async function handleSend() {
    const message = input.trim();
    if (!message || pending) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
      createdAt: new Date().toISOString(),
    };
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setPending(true);

    try {
      const response = await sendChatMessage({
        message,
        widgetKey,
        tenantId: widgetConfig?.tenant_id,
        storeId: widgetConfig?.store_id,
        sessionId,
        metadata: {
          business_name: widgetConfig?.store_name,
          support_email: widgetConfig?.support_email,
        },
      });
      setSessionId(response.session_id ?? sessionId);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          createdAt: new Date().toISOString(),
        },
      ]);
      setSuggestions(response.suggestions.length ? response.suggestions : []);
    } catch {
      const response = fallbackReply(message);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          createdAt: new Date().toISOString(),
        },
      ]);
      setSuggestions(response.suggestions);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 pointer-events-none">
      <div className="relative flex flex-col items-end">
        {open ? (
          <Card className="pointer-events-auto mb-4 w-[380px] max-w-[calc(100vw-2rem)] overflow-hidden border-white/15 p-0 shadow-glow">
          <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-4 py-4">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold text-white">
                <Sparkles className="h-4 w-4 text-accent2" /> {widgetConfig?.assistant_name ?? "Omniweb assistant"}
              </div>
              <div className="text-xs text-slate-400">{widgetConfig?.store_name ?? "Shopify sales + support widget"}</div>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-4 p-4">
            <VoiceStatus enabled={voiceEnabled} connected={voiceConnected} onToggle={() => setVoiceEnabled((current) => !current)} />
            <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-3 text-xs text-slate-400">
              {transcriptCount} customer messages in this session
            </div>
            <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
              {messages.map((message) => (
                <MessageBubble key={message.id} role={message.role} content={message.content} />
              ))}
            </div>
            {suggestions.length ? (
              <div className="space-y-3">
                <div className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Suggested products</div>
                <div className="grid gap-3">
                  {suggestions.map((suggestion) => (
                    <ProductSuggestionCard key={suggestion.product_id} suggestion={suggestion} />
                  ))}
                </div>
              </div>
            ) : null}
            <div className="flex items-center gap-2">
              <Input
                placeholder="Ask about products, bundles, shipping, or support..."
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void handleSend();
                  }
                }}
              />
              <Button disabled={pending} onClick={() => void handleSend()}>
                {voiceEnabled ? <Mic className="mr-2 h-4 w-4" /> : null}
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
          </Card>
        ) : null}
        <Button
          aria-expanded={open}
          aria-label={open ? "Hide AI assistant" : "Open AI assistant"}
          className="pointer-events-auto h-14 rounded-full px-5 shadow-glow"
          onClick={toggleWidget}
        >
          <Sparkles className="mr-2 h-5 w-5" />
          {open ? "Hide AI assistant" : "AI assistant"}
        </Button>
      </div>
    </div>
  );
}
