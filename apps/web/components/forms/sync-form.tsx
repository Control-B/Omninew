"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { syncShopifyStore } from "@/lib/api";

export function SyncForm() {
  const [shopDomain, setShopDomain] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");

    try {
      const response = await syncShopifyStore({
        shop_domain: shopDomain,
        admin_access_token: adminToken,
      });
      setStatus(
        `Synced ${response.products_synced ?? 0} products, ${response.collections_synced ?? 0} collections, ${response.policies_synced ?? 0} policies.`,
      );
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Sync failed.");
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
        <div className="flex items-center gap-3">
          <Button disabled={loading} type="submit">
            {loading ? "Syncing..." : "Run sync"}
          </Button>
          {status ? <span className="text-sm text-slate-300">{status}</span> : null}
        </div>
      </form>
    </Card>
  );
}
