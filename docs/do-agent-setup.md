# DigitalOcean AI Agent Setup

This project is designed to use **one shared DigitalOcean AI agent** for all merchants, with tenant-specific context injected from `Omniweb` at runtime.

## Recommended model

- **Model**: `openai/gpt-oss-120b`
- **Reason**: strong general reasoning and instruction following for storefront chat, while keeping one shared agent manageable for a multi-tenant SaaS.

## Recommended architecture

- **One shared agent** in DigitalOcean AI
- **No separate agent per shopper**
- **No separate agent per merchant initially**
- **Per-tenant behavior** comes from:
  - assistant name
  - tone
  - merchant instructions
  - synced products
  - synced policies
  - store metadata

## Dashboard values

- **Blueprint endpoint**: `GET /api/v1/agent/blueprint`
- **Function route secret header**: `X-Agent-Route-Secret`
- **Required API env**: `DO_AGENT_ROUTE_SECRET`

## What to do in each DigitalOcean section

### Knowledge Bases

- **For now**: leave this empty.
- **Why**: the first secure version should use synced Shopify products and policies from `Omniweb` as the source of truth.
- **Add one later only if**: you want to upload extra merchant documents like shipping SOPs, sizing PDFs, warranty docs, or sales scripts.

### Guardrails

- **Add guardrails if the UI supports custom text/policies**:
  - Do not invent prices, discounts, stock levels, delivery timelines, or policy exceptions.
  - Do not collect payment card details.
  - Do not claim refunds, order changes, or account access unless a tool confirms it.
  - Escalate to human handoff when confidence is low.
- **If DO guardrails are limited**: keep this protection in the system instruction and tool design; that is already built into the app.

### Agent Routes

- **For now**: leave this empty.
- **Why**: agent routes are for routing to other agents, and this setup uses one shared agent only.
- **Use later only if**: you create specialist agents like `returns-agent`, `sales-agent`, or `b2b-agent`.

## Function routes to add in DigitalOcean

Use the values from `GET /api/v1/agent/blueprint`, or configure these manually:

- `POST /api/v1/agent-tools/product-search`
- `POST /api/v1/agent-tools/policy-lookup`
- `POST /api/v1/agent-tools/lead-capture`
- `POST /api/v1/agent-tools/handoff`

Each route must include:

- header `X-Agent-Route-Secret: <your-secret>`

## Guardrails

- Never invent product availability, policy exceptions, pricing, discounts, or delivery timelines.
- Never collect full payment card data.
- Use tool routes for any store-specific claims.
- Escalate to handoff if the shopper requests a person or the answer is uncertain.

## Knowledge base strategy

- Start with **app-managed knowledge** from synced Shopify data.
- Avoid one DO knowledge base per merchant at MVP stage.
- Add merchant-specific knowledge bases later only for premium tenants with unique document sets.

## Secure setup notes

- Do not expose `DO_AGENT_ROUTE_SECRET` in the browser.
- Keep all function routes server-to-server only.
- The widget should continue calling `Omniweb` backend, not DO function routes directly.
- Keep `DO_AI_AGENT_ID` shared by default; only use per-tenant `do_agent_id` where isolation is required.