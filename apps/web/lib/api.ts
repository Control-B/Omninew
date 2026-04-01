import type { AssistantConfig, ChatResponse, PublicWidgetConfig, TenantBootstrapResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export function getApiBaseUrl() {
  return API_BASE_URL;
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) {
        detail = data.detail;
      }
    } catch {
      // ignore JSON parsing failure
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export async function bootstrapTenant(input: {
  business_name: string;
  owner_email: string;
  shop_domain: string;
  admin_access_token: string;
  storefront_access_token?: string;
  assistant_name: string;
  tone: "sales" | "balanced" | "support";
  welcome_message: string;
  voice_enabled: boolean;
}) {
  const response = await fetch(`${API_BASE_URL}/tenants/bootstrap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  return parseJson<TenantBootstrapResponse>(response);
}

export async function getAssistantConfig(input: { tenantId: string; storeId?: string | null }) {
  const search = new URLSearchParams({ tenant_id: input.tenantId });
  if (input.storeId) {
    search.set("store_id", input.storeId);
  }

  const response = await fetch(`${API_BASE_URL}/assistant-config/?${search.toString()}`);
  return parseJson<AssistantConfig>(response);
}

export async function updateAssistantConfig(input: {
  tenant_id: string;
  store_id?: string | null;
  assistant_name: string;
  tone: "sales" | "balanced" | "support";
  system_prompt?: string | null;
  welcome_message: string;
  voice_enabled: boolean;
  sales_mode_enabled: boolean;
  support_mode_enabled: boolean;
  do_agent_id?: string | null;
  theme_color?: string | null;
}) {
  const response = await fetch(`${API_BASE_URL}/assistant-config/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  return parseJson<AssistantConfig>(response);
}

export async function getWidgetPublicConfig(widgetKey: string) {
  const response = await fetch(`${API_BASE_URL}/tenants/widget/${encodeURIComponent(widgetKey)}`);
  return parseJson<PublicWidgetConfig>(response);
}

export async function syncShopifyStore(input: {
  tenant_id: string;
  store_id: string;
  shop_domain?: string;
  admin_access_token?: string;
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
      tenant_id: input.tenant_id,
      store_id: input.store_id,
      shop_domain: input.shop_domain ?? null,
      admin_access_token: input.admin_access_token ?? null,
      include_products: input.include_products ?? true,
      include_collections: input.include_collections ?? true,
      include_policies: input.include_policies ?? true,
    }),
  });

  return parseJson<{ products_synced?: number; collections_synced?: number; policies_synced?: number }>(response);
}

export async function sendChatMessage(input: {
  message: string;
  widgetKey?: string | null;
  tenantId?: string | null;
  storeId?: string | null;
  sessionId?: string | null;
  customerName?: string;
  customerEmail?: string;
  metadata?: Record<string, unknown>;
}) {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      widget_key: input.widgetKey ?? null,
      tenant_id: input.tenantId ?? null,
      store_id: input.storeId ?? null,
      session_id: input.sessionId ?? null,
      customer_name: input.customerName ?? null,
      customer_email: input.customerEmail ?? null,
      message: input.message,
      history: [],
      metadata: input.metadata ?? {},
    }),
  });

  return parseJson<ChatResponse>(response);
}

export async function createVoiceToken(input: {
  identity: string;
  roomName?: string | null;
  sessionId?: string | null;
  widgetKey?: string | null;
  tenantId?: string | null;
  storeId?: string | null;
}) {
  const response = await fetch(`${API_BASE_URL}/voice/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      widget_key: input.widgetKey ?? null,
      tenant_id: input.tenantId ?? null,
      store_id: input.storeId ?? null,
      session_id: input.sessionId ?? null,
      identity: input.identity,
      room_name: input.roomName ?? null,
      can_publish: true,
      can_subscribe: true,
    }),
  });

  return parseJson<{ token: string; ws_url: string; room_name: string }>(response);
}
