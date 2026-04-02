"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { bootstrapTenant, buildShopifyInstallUrl } from "@/lib/api";
import { setMerchantContext } from "@/lib/tenant-context";
import type { MerchantContext } from "@/lib/types";

export function ConnectStoreForm() {
  const [businessName, setBusinessName] = useState("");
  const [ownerEmail, setOwnerEmail] = useState("");
  const [assistantName, setAssistantName] = useState("Omniweb assistant");
  const [shopDomain, setShopDomain] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [storefrontToken, setStorefrontToken] = useState("");
  const [tone] = useState<"sales" | "balanced" | "support">("balanced");
  const [welcomeMessage, setWelcomeMessage] = useState(
    "Hi! I can recommend products, answer policy questions, and help capture leads for premium items.",
  );
  const [loading, setLoading] = useState(false);
  const [merchantContext, setSavedMerchantContext] = useState<MerchantContext | null>(null);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string>("");

  const embedSnippet = merchantContext
    ? `<script>\n  window.OmniwebWidget = {\n    appUrl: "${typeof window !== "undefined" ? window.location.origin : "https://your-app.example.com"}",\n    widgetKey: "${merchantContext.widgetKey}"\n  };\n</script>\n<script src="${typeof window !== "undefined" ? window.location.origin : "https://your-app.example.com"}/widget.js" async></script>`
    : "";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResult("");
    setError("");

    try {
      const response = await bootstrapTenant({
        business_name: businessName,
        owner_email: ownerEmail,
        shop_domain: shopDomain,
        admin_access_token: adminToken,
        storefront_access_token: storefrontToken || undefined,
        assistant_name: assistantName,
        tone: "balanced",
        welcome_message: welcomeMessage,
        voice_enabled: true,
      });
      const context: MerchantContext = {
        tenantId: response.tenant_id,
        storeId: response.store_id,
        widgetKey: response.widget_key,
        businessName: response.business_name,
        shopDomain: response.shop_domain,
        storeName: response.store_name,
        assistantName: response.assistant_name,
        tone: response.tone,
        welcomeMessage: response.welcome_message,
      };
      setMerchantContext(context);
      setSavedMerchantContext(context);
      setResult(`Created SaaS tenant for ${response.store_name ?? response.shop_domain}. Widget key issued successfully.`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Connection failed.");
    } finally {
      setLoading(false);
    }
  }

  function startOAuthInstall() {
    setError("");
    setResult("");

    if (!businessName || !ownerEmail || !assistantName || !shopDomain) {
      setError("Business name, owner email, assistant name, and shop domain are required for OAuth install.");
      return;
    }

    window.location.href = buildShopifyInstallUrl({
      shop: shopDomain,
      businessName,
      ownerEmail,
      assistantName,
      tone,
      welcomeMessage,
      voiceEnabled: true,
    });
  }

  return (
    <Card>
      <div className="mb-6 rounded-2xl border border-indigo-400/20 bg-indigo-500/10 p-4 text-sm text-slate-200">
        <div className="font-medium text-white">Recommended: Shopify OAuth install</div>
        <p className="mt-2 text-slate-300">
          OAuth is the production SaaS path. It installs Omniweb on the merchant store, exchanges the admin token securely, provisions the tenant, and redirects back here with a widget key.
        </p>
      </div>
      <form className="space-y-4" onSubmit={onSubmit}>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Business name</label>
          <Input placeholder="Acme Wellness" value={businessName} onChange={(event) => setBusinessName(event.target.value)} required />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Owner email</label>
          <Input placeholder="owner@acme.com" type="email" value={ownerEmail} onChange={(event) => setOwnerEmail(event.target.value)} required />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Assistant name</label>
          <Input placeholder="Acme concierge" value={assistantName} onChange={(event) => setAssistantName(event.target.value)} required />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Shop domain</label>
          <Input
            placeholder="your-store.myshopify.com"
            value={shopDomain}
            onChange={(event) => setShopDomain(event.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Admin API token</label>
          <Input
            placeholder="shpat_..."
            value={adminToken}
            onChange={(event) => setAdminToken(event.target.value)}
            required
            type="password"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Storefront API token</label>
          <Input
            placeholder="Optional for widget product search"
            value={storefrontToken}
            onChange={(event) => setStorefrontToken(event.target.value)}
            type="password"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm text-slate-300">Welcome message</label>
          <Textarea value={welcomeMessage} onChange={(event) => setWelcomeMessage(event.target.value)} />
        </div>
        <div className="flex items-center gap-3">
          <Button type="button" onClick={startOAuthInstall} variant="primary">
            Connect with Shopify OAuth
          </Button>
          <Button disabled={loading} type="submit">
            {loading ? "Creating SaaS tenant..." : "Manual token bootstrap"}
          </Button>
          {result ? <span className="text-sm text-green-300">{result}</span> : null}
          {error ? <span className="text-sm text-rose-300">{error}</span> : null}
        </div>
      </form>

      {merchantContext ? (
        <div className="mt-6 space-y-4 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
          <div>
            <div className="text-sm font-medium text-white">Tenant ready</div>
            <div className="mt-1 text-sm text-slate-400">
              Widget key: <span className="font-mono text-slate-200">{merchantContext.widgetKey}</span>
            </div>
          </div>
          <div>
            <div className="mb-2 text-sm text-slate-300">Embed snippet</div>
            <Textarea readOnly value={embedSnippet} className="min-h-40 font-mono text-xs" />
          </div>
        </div>
      ) : null}
    </Card>
  );
}
