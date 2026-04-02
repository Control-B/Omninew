import type { MerchantContext } from "@/lib/types";

const STORAGE_KEY = "omniweb.merchant-context";

export function getMerchantContext(): MerchantContext | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as MerchantContext;
  } catch {
    return null;
  }
}

export function setMerchantContext(context: MerchantContext) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(context));
}

export function clearMerchantContext() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(STORAGE_KEY);
}
