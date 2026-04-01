import type { LeadSummary, NavItem, ProductSuggestion, TranscriptSummary } from "@/lib/types";

export const dashboardNav: NavItem[] = [
  {
    href: "/dashboard",
    label: "Overview",
    description: "Conversion and support snapshot",
  },
  {
    href: "/dashboard/connect",
    label: "Connect Store",
    description: "Attach Shopify credentials for the MVP",
  },
  {
    href: "/dashboard/sync",
    label: "Product Sync",
    description: "Refresh products, collections, and policies",
  },
  {
    href: "/dashboard/assistant",
    label: "Assistant Config",
    description: "Tune sales voice, prompts, and lead capture",
  },
  {
    href: "/dashboard/transcripts",
    label: "Transcripts",
    description: "Review text and voice conversations",
  },
  {
    href: "/dashboard/leads",
    label: "Leads",
    description: "Track high-intent customer capture",
  },
];

export const sampleSuggestions: ProductSuggestion[] = [
  {
    product_id: "gid://shopify/Product/1",
    title: "Performance Recovery Blend",
    handle: "performance-recovery-blend",
    price: "$39.00",
    reason: "Best fit for shoppers asking about daily recovery and stress support.",
  },
  {
    product_id: "gid://shopify/Product/2",
    title: "Night Routine Bundle",
    handle: "night-routine-bundle",
    price: "$58.00",
    reason: "Pairs naturally with sleep-related support questions and bundle upsells.",
  },
];

export const sampleLeads: LeadSummary[] = [
  {
    id: "lead-1",
    name: "Maya Chen",
    email: "maya@example.com",
    intent: "bulk-order inquiry",
    productInterest: "Wholesale skincare starter kit",
    createdAt: "2026-04-01T11:22:00Z",
  },
  {
    id: "lead-2",
    name: "Trevor James",
    email: "trevor@example.com",
    intent: "high-ticket product guidance",
    productInterest: "Premium cold plunge setup",
    createdAt: "2026-04-01T09:08:00Z",
  },
];

export const sampleTranscripts: TranscriptSummary[] = [
  {
    id: "session-1",
    customer: "Ava Thompson",
    channel: "web chat",
    summary: "Asked about sizing, shipping speed, and upsell bundle eligibility.",
    createdAt: "2026-04-01T10:40:00Z",
  },
  {
    id: "session-2",
    customer: "Voice caller #204",
    channel: "livekit voice",
    summary: "Requested policy clarification and left callback number for support.",
    createdAt: "2026-03-31T18:15:00Z",
  },
];
