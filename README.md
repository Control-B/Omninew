# Omninew

Multi-tenant Shopify AI assistant built with a `Next.js` frontend in `apps/web` and a `FastAPI` backend in `apps/api`.

## Local Run

- `apps/api`: copy `apps/api/.env.example` to `.env`, then run `uv run uvicorn app.main:app --reload`
- `apps/web`: copy `apps/web/.env.example` to `.env.local`, then run `npm install && npm run dev`

## Shopify OAuth Setup

- **Readiness endpoint**: `GET /api/v1/auth/shopify/setup`
- **Install route**: `/api/v1/auth/shopify/install`
- **Callback URL**: `https://<your-app-domain>/backend/api/v1/auth/shopify/callback`
- **Uninstall webhook**: `https://<your-app-domain>/backend/api/v1/webhooks/shopify/app-uninstalled`
- **Dashboard flow**: open `/dashboard/connect` and use the Shopify OAuth button

## DigitalOcean App Platform

- **Web route**: `/`
- **API route**: `/backend`
- **Required API envs**: `APP_URL`, `API_PUBLIC_URL`, `SHOPIFY_APP_KEY`, `SHOPIFY_APP_SECRET`, `SHOPIFY_APP_SCOPES`, `SHOPIFY_WEBHOOK_SECRET`

## Billing Foundation

- **Plans**: `starter`, `growth`, `scale`
- **Billing API**: `GET /api/v1/billing/plans`, `GET /api/v1/billing`, `PUT /api/v1/billing/plan`
- **Shopify checkout**: `POST /api/v1/billing/shopify/checkout`, then Shopify returns to `GET /api/v1/billing/shopify/callback`
- **Metered usage**: `chat_messages`, `voice_sessions`, `sync_runs`
- **Enforcement**: chat, voice, and store sync now check current plan limits before proceeding
- **Test mode**: set `SHOPIFY_BILLING_TEST_MODE=true` for development stores and `false` in production

## DigitalOcean AI Agent

- **Blueprint endpoint**: `GET /api/v1/agent/blueprint`
- **Dashboard guide**: `docs/do-agent-setup.md`
- **Recommended model**: `openai/gpt-oss-120b`
- **Function routes**: `POST /api/v1/agent-tools/product-search`, `POST /api/v1/agent-tools/policy-lookup`, `POST /api/v1/agent-tools/lead-capture`, `POST /api/v1/agent-tools/handoff`
- **Route auth**: set `DO_AGENT_ROUTE_SECRET` and pass it as `X-Agent-Route-Secret` from DigitalOcean agent tool configuration

## Quick Validation

```bash
cd /root/OmniNew/apps/api
uv run pytest -q

cd /root/OmniNew/apps/web
npm run build
```
