create table if not exists public.widget_deployments (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid references public.shopify_stores(id) on delete cascade,
  public_key text not null unique,
  label text not null default 'Default storefront widget',
  allowed_domains text[] not null default '{}',
  status text not null default 'active',
  settings jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists widget_deployments_tenant_id_idx on public.widget_deployments(tenant_id);
create index if not exists widget_deployments_store_id_idx on public.widget_deployments(store_id);
create unique index if not exists widget_deployments_store_label_idx on public.widget_deployments(tenant_id, store_id, label);

create table if not exists public.usage_events (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  store_id uuid references public.shopify_stores(id) on delete set null,
  session_id uuid,
  metric_type text not null,
  quantity integer not null default 1,
  source text not null default 'app',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);
create index if not exists usage_events_tenant_id_idx on public.usage_events(tenant_id);
create index if not exists usage_events_store_id_idx on public.usage_events(store_id);
create index if not exists usage_events_session_id_idx on public.usage_events(session_id);

create unique index if not exists agent_configs_tenant_store_name_idx on public.agent_configs(tenant_id, store_id, name);

create trigger set_widget_deployments_updated_at before update on public.widget_deployments for each row execute function public.set_updated_at();
create trigger set_usage_events_updated_at before update on public.usage_events for each row execute function public.set_updated_at();
