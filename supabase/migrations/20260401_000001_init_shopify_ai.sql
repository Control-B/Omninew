create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

create table if not exists public.tenants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  status text not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  email text not null,
  full_name text,
  role text not null default 'merchant_admin',
  auth_user_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create unique index if not exists users_tenant_email_idx on public.users(tenant_id, email);
create index if not exists users_tenant_id_idx on public.users(tenant_id);

create table if not exists public.shopify_stores (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  shop_domain text not null unique,
  store_name text,
  email text,
  currency_code text,
  storefront_access_token_last4 text,
  status text not null default 'connected',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists shopify_stores_tenant_id_idx on public.shopify_stores(tenant_id);

create table if not exists public.shopify_tokens (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid not null references public.shopify_stores(id) on delete cascade,
  token_type text not null,
  token_encrypted text not null,
  scopes text[] not null default '{}',
  expires_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists shopify_tokens_tenant_id_idx on public.shopify_tokens(tenant_id);
create index if not exists shopify_tokens_store_id_idx on public.shopify_tokens(store_id);

create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid not null references public.shopify_stores(id) on delete cascade,
  shop_domain text not null,
  shopify_product_id text not null,
  title text not null,
  handle text,
  description text,
  status text not null default 'active',
  available boolean not null default true,
  price text,
  currency_code text,
  image_url text,
  tags text[] not null default '{}',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create unique index if not exists products_tenant_shopify_product_idx on public.products(tenant_id, shopify_product_id);
create index if not exists products_tenant_id_idx on public.products(tenant_id);
create index if not exists products_store_id_idx on public.products(store_id);

create table if not exists public.collections (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid not null references public.shopify_stores(id) on delete cascade,
  shopify_collection_id text not null,
  title text not null,
  handle text,
  description text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create unique index if not exists collections_tenant_shopify_collection_idx on public.collections(tenant_id, shopify_collection_id);
create index if not exists collections_tenant_id_idx on public.collections(tenant_id);
create index if not exists collections_store_id_idx on public.collections(store_id);

create table if not exists public.policies (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid not null references public.shopify_stores(id) on delete cascade,
  policy_type text not null,
  title text,
  body text,
  url text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create unique index if not exists policies_tenant_store_type_idx on public.policies(tenant_id, store_id, policy_type);
create index if not exists policies_tenant_id_idx on public.policies(tenant_id);
create index if not exists policies_store_id_idx on public.policies(store_id);

create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid references public.shopify_stores(id) on delete set null,
  channel text not null default 'web_chat',
  customer_name text,
  customer_email text,
  customer_phone text,
  status text not null default 'open',
  summary text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists chat_sessions_tenant_id_idx on public.chat_sessions(tenant_id);
create index if not exists chat_sessions_store_id_idx on public.chat_sessions(store_id);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  session_id uuid references public.chat_sessions(id) on delete cascade,
  role text not null,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists messages_tenant_id_idx on public.messages(tenant_id);
create index if not exists messages_session_id_idx on public.messages(session_id);

create table if not exists public.voice_sessions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid references public.shopify_stores(id) on delete set null,
  livekit_room_name text not null,
  livekit_identity text not null,
  channel text not null default 'widget_voice',
  status text not null default 'created',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists voice_sessions_tenant_id_idx on public.voice_sessions(tenant_id);
create index if not exists voice_sessions_store_id_idx on public.voice_sessions(store_id);

create table if not exists public.transcripts (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  session_id uuid not null,
  transcript text not null,
  summary text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists transcripts_tenant_id_idx on public.transcripts(tenant_id);
create index if not exists transcripts_session_id_idx on public.transcripts(session_id);

create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  session_id uuid,
  name text,
  email text,
  phone text,
  intent text not null,
  product_interest text,
  status text not null default 'new',
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists leads_tenant_id_idx on public.leads(tenant_id);
create index if not exists leads_session_id_idx on public.leads(session_id);

create table if not exists public.agent_configs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid references public.shopify_stores(id) on delete set null,
  name text not null default 'default',
  tone text not null default 'balanced',
  system_prompt text,
  voice_enabled boolean not null default false,
  sales_mode_enabled boolean not null default true,
  support_mode_enabled boolean not null default true,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists agent_configs_tenant_id_idx on public.agent_configs(tenant_id);
create index if not exists agent_configs_store_id_idx on public.agent_configs(store_id);

create table if not exists public.event_logs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  session_id uuid,
  event_type text not null,
  source text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists event_logs_tenant_id_idx on public.event_logs(tenant_id);
create index if not exists event_logs_session_id_idx on public.event_logs(session_id);

create trigger set_tenants_updated_at before update on public.tenants for each row execute function public.set_updated_at();
create trigger set_users_updated_at before update on public.users for each row execute function public.set_updated_at();
create trigger set_shopify_stores_updated_at before update on public.shopify_stores for each row execute function public.set_updated_at();
create trigger set_shopify_tokens_updated_at before update on public.shopify_tokens for each row execute function public.set_updated_at();
create trigger set_products_updated_at before update on public.products for each row execute function public.set_updated_at();
create trigger set_collections_updated_at before update on public.collections for each row execute function public.set_updated_at();
create trigger set_policies_updated_at before update on public.policies for each row execute function public.set_updated_at();
create trigger set_chat_sessions_updated_at before update on public.chat_sessions for each row execute function public.set_updated_at();
create trigger set_messages_updated_at before update on public.messages for each row execute function public.set_updated_at();
create trigger set_voice_sessions_updated_at before update on public.voice_sessions for each row execute function public.set_updated_at();
create trigger set_transcripts_updated_at before update on public.transcripts for each row execute function public.set_updated_at();
create trigger set_leads_updated_at before update on public.leads for each row execute function public.set_updated_at();
create trigger set_agent_configs_updated_at before update on public.agent_configs for each row execute function public.set_updated_at();
create trigger set_event_logs_updated_at before update on public.event_logs for each row execute function public.set_updated_at();
