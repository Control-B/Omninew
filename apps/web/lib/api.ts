import type { ChatResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const DEFAULT_TENANT_ID = process.env.NEXT_PUBLIC_DEFAULT_TENANT_ID ?? "00000000-0000-0000-0000-000000000001";
const DEFAULT_STORE_ID = process.env.NEXT_PUBLIC_DEFAULT_STORE_ID ?? "00000000-0000-0000-0000-000000000001";

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export async function connectShopifyStore(input: {
  shop_domain: string;
  admin_access_token: string;
  storefront_access_token?: string;
  tenant_id?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/shopify/connect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      tenant_id: input.tenant_id ?? DEFAULT_TENANT_ID,
      shop_domain: input.shop_domain,
      admin_access_token: input.admin_access_token,
      storefront_access_token: input.storefront_access_token || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Connect failed with status ${response.status}`);
  }

  return response.json();
}

export async function syncShopifyStore(input: {
  shop_domain: string;
  admin_access_token: string;
  tenant_id?: string;
  store_id?: string;
  include_products?: boolean;
  include_collections?: boolean;
  include_policies?: boolean;
}) {
  const response = await fetch(`${API_BASE_URL}/shopify/sync`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      tenant_id: input.tenant_id ?? DEFAULT_TENANT_ID,
      store_id: input.store_id ?? DEFAULT_STORE_ID,
      shop_domain: input.shop_domain,
      admin_access_token: input.admin_access_token,
      include_products: input.include_products ?? true,
      include_collections: input.include_collections ?? true,
      include_policies: input.include_policies ?? true,
    }),
  });

  if (!response.ok) {
    throw new Error(`Sync failed with status ${response.status}`);
  }

  return response.json();
}

export async function sendChatMessage(input: {
  message: string;
  sessionId?: string | null;
  customerName?: string;
  customerEmail?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      tenant_id: DEFAULT_TENANT_ID,
      store_id: DEFAULT_STORE_ID,
      session_id: input.sessionId ?? null,
      customer_name: input.customerName ?? null,
      customer_email: input.customerEmail ?? null,
      message: input.message,
      history: [],
      metadata: {
        business_name: "OmniNew Demo Store",
        support_email: "support@example.com",
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat failed with status ${response.status}`);
  }

  return (await response.json()) as ChatResponse;
}

export async function createVoiceToken(input: { identity: string; roomName: string }) {
  const response = await fetch(`${API_BASE_URL}/voice/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      tenant_id: DEFAULT_TENANT_ID,
      store_id: DEFAULT_STORE_ID,
      identity: input.identity,
      room_name: input.roomName,
      can_publish: true,
      can_subscribe: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`Voice token failed with status ${response.status}`);
  }

  return response.json() as Promise<{ token: string; ws_url: string; room_name: string }>;
}
