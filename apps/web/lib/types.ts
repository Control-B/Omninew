export type NavItem = {
  href: string;
  label: string;
  description: string;
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
