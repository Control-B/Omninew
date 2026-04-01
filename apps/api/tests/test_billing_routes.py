from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_billing_service
from app.main import app
from app.schemas.common import (
    BillingOverviewResponse,
    ShopifyBillingCheckoutResponse,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
    UsageMetricSummary,
)


class FakeBillingService:
    def __init__(self) -> None:
        self.tenant_id = uuid4()
        self.store_id = uuid4()

    async def list_plans(self):
        return [
            SubscriptionPlanResponse(
                code="starter",
                name="Starter",
                monthly_price_cents=0,
                currency_code="USD",
                limits={"chat_messages": 300, "voice_sessions": 25, "sync_runs": 10},
                is_active=True,
            )
        ]

    async def get_billing_overview(self, *, tenant_id, store_id=None):
        return BillingOverviewResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            subscription=TenantSubscriptionResponse(
                tenant_id=tenant_id,
                status="trialing",
                billing_provider="manual",
                plan_code="starter",
                plan_name="Starter",
                monthly_price_cents=0,
                currency_code="USD",
                limits={"chat_messages": 300, "voice_sessions": 25, "sync_runs": 10},
                current_period_start="2026-04-01T00:00:00+00:00",
                current_period_end="2026-05-01T00:00:00+00:00",
                cancel_at_period_end=False,
            ),
            usage=[
                UsageMetricSummary(metric_type="chat_messages", quantity=12, limit=300, remaining=288),
                UsageMetricSummary(metric_type="voice_sessions", quantity=1, limit=25, remaining=24),
            ],
        )

    async def update_plan(self, tenant_id, plan_code):
        return TenantSubscriptionResponse(
            tenant_id=tenant_id,
            status="active",
            billing_provider="manual",
            plan_code=plan_code,
            plan_name=plan_code.title(),
            monthly_price_cents=9900,
            currency_code="USD",
            limits={"chat_messages": 3000, "voice_sessions": 250, "sync_runs": 100},
            current_period_start="2026-04-01T00:00:00+00:00",
            current_period_end="2026-05-01T00:00:00+00:00",
            cancel_at_period_end=False,
        )

    async def create_shopify_checkout(self, *, tenant_id, store_id=None, plan_code, return_path="/dashboard/connect"):
        return ShopifyBillingCheckoutResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            plan_code=plan_code,
            status="pending",
            requires_confirmation=True,
            confirmation_url="https://admin.shopify.com/confirm_charge",
            redirect_url="https://admin.shopify.com/confirm_charge",
            subscription_id="gid://shopify/AppSubscription/1",
            test_mode=True,
        )

    async def complete_shopify_checkout(self, query_params):
        return "https://omninew.example.com/dashboard/connect?billing=success&planCode=growth"


def test_billing_plans_route() -> None:
    app.dependency_overrides[get_billing_service] = lambda: FakeBillingService()
    client = TestClient(app)

    response = client.get("/api/v1/billing/plans")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["code"] == "starter"


def test_billing_overview_route() -> None:
    fake_service = FakeBillingService()
    app.dependency_overrides[get_billing_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/billing/",
        params={"tenant_id": str(fake_service.tenant_id), "store_id": str(fake_service.store_id)},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["subscription"]["plan_code"] == "starter"
    assert response.json()["usage"][0]["metric_type"] == "chat_messages"


def test_billing_plan_update_route() -> None:
    fake_service = FakeBillingService()
    app.dependency_overrides[get_billing_service] = lambda: fake_service
    client = TestClient(app)

    response = client.put(
        "/api/v1/billing/plan",
        json={"tenant_id": str(fake_service.tenant_id), "plan_code": "growth"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["plan_code"] == "growth"
    assert response.json()["status"] == "active"


def test_shopify_billing_checkout_route() -> None:
    fake_service = FakeBillingService()
    app.dependency_overrides[get_billing_service] = lambda: fake_service
    client = TestClient(app)

    response = client.post(
        "/api/v1/billing/shopify/checkout",
        json={
            "tenant_id": str(fake_service.tenant_id),
            "store_id": str(fake_service.store_id),
            "plan_code": "growth",
            "return_path": "/dashboard/connect",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["plan_code"] == "growth"
    assert response.json()["requires_confirmation"] is True


def test_shopify_billing_callback_route() -> None:
    app.dependency_overrides[get_billing_service] = lambda: FakeBillingService()
    client = TestClient(app)

    response = client.get(
        "/api/v1/billing/shopify/callback",
        params={"shop": "acme.myshopify.com", "hmac": "valid"},
        follow_redirects=False,
    )

    app.dependency_overrides.clear()

    assert response.status_code == 302
    assert "billing=success" in response.headers["location"]