"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { setMerchantContext } from "@/lib/tenant-context";
import type { MerchantContext } from "@/lib/types";

export function OAuthCallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("Finalizing Shopify install...");

  useEffect(() => {
    const status = searchParams.get("status");
    if (status === "error") {
      const detail = searchParams.get("message") ?? "Shopify install failed.";
      setMessage(detail);
      return;
    }

    const tenantId = searchParams.get("tenantId");
    const storeId = searchParams.get("storeId");
    const widgetKey = searchParams.get("widgetKey");
    const businessName = searchParams.get("businessName");
    const shopDomain = searchParams.get("shopDomain");
    const assistantName = searchParams.get("assistantName");
    const tone = searchParams.get("tone") as MerchantContext["tone"] | null;
    const welcomeMessage = searchParams.get("welcomeMessage");

    if (!tenantId || !storeId || !widgetKey || !businessName || !shopDomain || !assistantName || !tone || !welcomeMessage) {
      setMessage("Shopify install is missing required tenant context.");
      return;
    }

    setMerchantContext({
      tenantId,
      storeId,
      widgetKey,
      businessName,
      shopDomain,
      storeName: searchParams.get("storeName"),
      assistantName,
      tone,
      welcomeMessage,
    });

    router.replace("/dashboard/connect?oauth=success");
  }, [router, searchParams]);

  return <div>{message}</div>;
}
