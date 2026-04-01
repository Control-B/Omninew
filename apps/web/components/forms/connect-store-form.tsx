"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { connectShopifyStore } from "@/lib/api";

export function ConnectStoreForm() {
  const [shopDomain, setShopDomain] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [storefrontToken, setStorefrontToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string>("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResult("");
    setError("");

    try {
      const response = await connectShopifyStore({
        shop_domain: shopDomain,
        admin_access_token: adminToken,
        storefront_access_token: storefrontToken || undefined,
      });
      setResult(`Connected ${response.store_info?.name ?? shopDomain} successfully.`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Connection failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <form className="space-y-4" onSubmit={onSubmit}>
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
        <div className="flex items-center gap-3">
          <Button disabled={loading} type="submit">
            {loading ? "Connecting..." : "Connect store"}
          </Button>
          {result ? <span className="text-sm text-green-300">{result}</span> : null}
          {error ? <span className="text-sm text-rose-300">{error}</span> : null}
        </div>
      </form>
    </Card>
  );
}
