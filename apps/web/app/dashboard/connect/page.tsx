import { ConnectStoreForm } from "@/components/forms/connect-store-form";
import { Card } from "@/components/ui/card";

export default function ConnectPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Connect store</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Create merchant tenant + connect Shopify</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          This SaaS onboarding flow creates a merchant tenant, stores the Shopify credentials, provisions a default assistant config, and issues a public widget key for storefront install.
        </p>
      </div>
      <ConnectStoreForm />
      <Card className="text-sm leading-7 text-slate-300">
        Once connected, OmniNew can sync products and policies, serve text and voice sessions from the shared platform, and keep tenant data isolated by store.
      </Card>
    </div>
  );
}
