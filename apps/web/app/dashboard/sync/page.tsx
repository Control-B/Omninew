import { SyncForm } from "@/components/forms/sync-form";
import { Card } from "@/components/ui/card";

export default function SyncPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Product sync</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Sync products, collections, and policies</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          This surface triggers Omniweb to pull your Shopify catalog data for tenant-specific recommendations, grounded policy answers, and storefront assistant context.
        </p>
      </div>
      <SyncForm />
      <Card className="grid gap-4 md:grid-cols-3">
        <div>
          <div className="text-sm font-medium text-white">Products</div>
          <p className="mt-2 text-sm text-slate-400">Used for recommendation, search, and upsell suggestions.</p>
        </div>
        <div>
          <div className="text-sm font-medium text-white">Collections</div>
          <p className="mt-2 text-sm text-slate-400">Useful for contextual selling and landing-page-based guidance.</p>
        </div>
        <div>
          <div className="text-sm font-medium text-white">Policies</div>
          <p className="mt-2 text-sm text-slate-400">Powers grounded shipping, refund, and support responses.</p>
        </div>
      </Card>
    </div>
  );
}
