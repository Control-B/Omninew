import { Suspense } from "react";

import { OAuthCallbackHandler } from "@/components/forms/oauth-callback-handler";
import { Card } from "@/components/ui/card";

export default function ShopifyOAuthCallbackPage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-16">
      <Card className="p-6 text-sm text-slate-300">
        <Suspense fallback={<div>Finalizing Shopify install...</div>}>
          <OAuthCallbackHandler />
        </Suspense>
      </Card>
    </main>
  );
}
