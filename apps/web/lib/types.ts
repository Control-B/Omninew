export type NavItem = {
  href: string;
  label: string;
  description: string;
};

export type MerchantContext = {
  tenantId: string;
  storeId: string;
  widgetKey: string;
  businessName: string;
  shopDomain: string;
  storeName?: string | null;
  assistantName: string;
  tone: "sales" | "balanced" | "support";
  welcomeMessage: string;
};

export type ProductSuggestion = {
  product_id: string;
  title: string;
  handle?: string | null;
  price?: string | null;
  reason?: string | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
};

export type ChatResponse = {
  reply: string;
  suggestions: ProductSuggestion[];
  lead_capture_detected: boolean;
  session_id?: string | null;
  metadata: Record<string, unknown>;
};

export type TenantBootstrapResponse = {
  tenant_id: string;
  store_id: string;
  widget_key: string;
  business_name: string;
  shop_domain: string;
  store_name?: string | null;
  assistant_name: string;
  tone: "sales" | "balanced" | "support";
  welcome_message: string;
};

export type AssistantConfig = {
  id?: string | null;
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
};

export type PublicWidgetConfig = {
  widget_key: string;
  tenant_id: string;
  store_id?: string | null;
  assistant_name: string;
  welcome_message: string;
  voice_enabled: boolean;
  theme_color?: string | null;
  store_name?: string | null;
  support_email?: string | null;
};

export type LeadSummary = {
  id: string;
  name: string;
  email: string;
  intent: string;
  productInterest: string;
  createdAt: string;
};

export type TranscriptSummary = {
  id: string;
  customer: string;
  channel: string;
  summary: string;
  createdAt: string;
};
