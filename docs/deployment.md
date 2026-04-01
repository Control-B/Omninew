# Deployment Guide

This project is designed for:
- `apps/web` on DigitalOcean App Platform
- `apps/api` on DigitalOcean App Platform
- Supabase on a dedicated one-click DigitalOcean droplet

## 1. GitHub repository

This workspace is ready to push to a GitHub repo named `Omninew`.

If `gh` is authenticated on your machine, run:

```bash
cd /root/OmniNew
gh auth login
git init
git branch -M main
git add .
git commit -m "Initial OmniNew MVP scaffold"
gh repo create Omninew --private --source=. --remote=origin --push
```

If you prefer manual GitHub creation:

```bash
cd /root/OmniNew
git init
git branch -M main
git add .
git commit -m "Initial OmniNew MVP scaffold"
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/Omninew.git
git push -u origin main
```

## 2. Supabase one-click droplet

Create the one-click Supabase droplet in DigitalOcean and note:
- public base URL for Kong / REST API
- anon key
- service role key
- database connection details if you want direct SQL access later

Then apply the migration in `supabase/migrations/20260401_000001_init_shopify_ai.sql` using the Supabase SQL editor or psql.

## 3. App Platform

This repo includes `.do/app-platform.yaml` with two services:
- `web` for `apps/web`
- `api` for `apps/api`

You can either:
- create one App Platform app with both services, or
- create two separate App Platform apps and split the spec manually

Before deploy, replace these placeholders in `.do/app-platform.yaml`:
- `YOUR_GITHUB_USERNAME/Omninew`
- `${APP_URL}`
- `${API_URL}`
- `${SUPABASE_URL}`
- `${SUPABASE_ANON_KEY}`
- `${SUPABASE_SERVICE_ROLE_KEY}`
- `${DO_AI_AGENT_BASE_URL}`
- `${DO_AI_AGENT_KEY}`
- `${DO_AI_AGENT_ID}`
- `${LIVEKIT_API_KEY}`
- `${LIVEKIT_API_SECRET}`
- `${LIVEKIT_WS_URL}`

## 4. Web envs

Set these on the `web` service:
- `NEXT_PUBLIC_APP_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_LIVEKIT_WS_URL`
- `NEXT_PUBLIC_DEFAULT_TENANT_ID`
- `NEXT_PUBLIC_DEFAULT_STORE_ID`

## 5. API envs

Set these on the `api` service:
- `APP_NAME`
- `ENVIRONMENT=production`
- `API_V1_PREFIX=/api/v1`
- `CORS_ORIGINS=["https://YOUR_WEB_DOMAIN"]`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `DO_AI_AGENT_BASE_URL`
- `DO_AI_AGENT_KEY`
- `DO_AI_AGENT_ID`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `LIVEKIT_WS_URL`

## 6. Widget install snippet

After the web app is deployed, host the embed loader from:
- `https://YOUR_WEB_DOMAIN/widget.js`

Then give merchants this snippet:

```html
<script>
  window.OmniNewWidget = {
    appUrl: "https://YOUR_WEB_DOMAIN",
    apiBaseUrl: "https://YOUR_API_DOMAIN/api/v1",
    tenantId: "YOUR_TENANT_ID",
    storeId: "YOUR_STORE_ID",
    livekitWsUrl: "wss://YOUR_PROJECT.livekit.cloud"
  };
</script>
<script async src="https://YOUR_WEB_DOMAIN/widget.js"></script>
```

The loader injects an iframe pointing to `/embed/widget`.

## 7. Recommended order

1. Push repo to GitHub
2. Create Supabase droplet
3. Apply SQL migration
4. Create App Platform app(s)
5. Set web and api environment variables
6. Deploy `web` and `api`
7. Verify `/api/v1/health`
8. Test `/widget-demo`
9. Install `widget.js` into a Shopify theme

## 8. What still requires your account access

I cannot directly:
- log into your GitHub account
- create the GitHub repo without your auth
- create the DigitalOcean App Platform app
- provision the one-click Supabase droplet

I can prepare everything locally and guide each step, which this repo now supports.
