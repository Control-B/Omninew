create table if not exists public.subscription_plans (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  monthly_price_cents integer not null default 0,
  currency_code text not null default 'USD',
  limits jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.tenant_subscriptions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  plan_id uuid references public.subscription_plans(id) on delete set null,
  status text not null default 'trialing',
  billing_provider text not null default 'manual',
  external_customer_id text,
  external_subscription_id text,
  current_period_start timestamptz not null default timezone('utc', now()),
  current_period_end timestamptz,
  cancel_at_period_end boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists tenant_subscriptions_tenant_id_idx on public.tenant_subscriptions(tenant_id);
create index if not exists tenant_subscriptions_plan_id_idx on public.tenant_subscriptions(plan_id);

insert into public.subscription_plans (code, name, monthly_price_cents, currency_code, limits, metadata)
values
  (
    'starter',
    'Starter',
    0,
    'USD',
    '{"chat_messages": 300, "voice_sessions": 25, "sync_runs": 10}'::jsonb,
    '{"origin": "migration_seed"}'::jsonb
  ),
  (
    'growth',
    'Growth',
    9900,
    'USD',
    '{"chat_messages": 3000, "voice_sessions": 250, "sync_runs": 100}'::jsonb,
    '{"origin": "migration_seed"}'::jsonb
  ),
  (
    'scale',
    'Scale',
    29900,
    'USD',
    '{"chat_messages": null, "voice_sessions": null, "sync_runs": null}'::jsonb,
    '{"origin": "migration_seed"}'::jsonb
  )
on conflict (code) do nothing;

create trigger set_subscription_plans_updated_at before update on public.subscription_plans for each row execute function public.set_updated_at();
create trigger set_tenant_subscriptions_updated_at before update on public.tenant_subscriptions for each row execute function public.set_updated_at();