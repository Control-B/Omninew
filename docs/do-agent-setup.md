# DigitalOcean AI Agent Setup

This project is designed to use **one shared DigitalOcean AI agent** for all merchants, with tenant-specific context injected from `OmniNew` at runtime.

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
- The widget should continue calling `OmniNew` backend, not DO function routes directly.
- Keep `DO_AI_AGENT_ID` shared by default; only use per-tenant `do_agent_id` where isolation is required.