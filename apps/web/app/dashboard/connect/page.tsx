import { ConnectStoreForm } from "@/components/forms/connect-store-form";
import { Card } from "@/components/ui/card";

export default function ConnectPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Connect store</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Attach Shopify credentials</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          For the MVP, merchants manually add Admin and Storefront tokens. OAuth can replace this later without changing the dashboard surface.
        </p>
      </div>
      <ConnectStoreForm />
      <Card className="text-sm leading-7 text-slate-300">
        Once connected, the backend can validate the shop, fetch store info, and prepare product plus policy sync jobs.
      </Card>
    </div>
  );
}
