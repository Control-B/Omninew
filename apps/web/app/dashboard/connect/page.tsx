import { ConnectStoreForm } from "@/components/forms/connect-store-form";
import { Card } from "@/components/ui/card";

export default function ConnectPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Connect store</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Create merchant tenant + connect Shopify</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          Use Shopify OAuth for the production install flow, or keep the manual token bootstrap for local testing and early migrations.
        </p>
      </div>
      <ConnectStoreForm />
      <Card className="text-sm leading-7 text-slate-300">
        Once connected, Omniweb can sync products and policies, serve text and voice sessions from the shared platform, register uninstall webhooks, and keep tenant data isolated by store.
      </Card>
    </div>
  );
}
