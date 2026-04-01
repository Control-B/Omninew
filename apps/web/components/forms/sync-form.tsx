"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { syncShopifyStore } from "@/lib/api";
import { getMerchantContext } from "@/lib/tenant-context";

export function SyncForm() {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");

    const context = getMerchantContext();
    if (!context) {
      setStatus("Create a tenant on the Connect Store page first.");
      setLoading(false);
      return;
    }

    try {
      const response = await syncShopifyStore({
        tenant_id: context.tenantId,
        store_id: context.storeId,
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
        <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-sm text-slate-300">
          Sync uses the Shopify credentials already stored during merchant onboarding.
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
