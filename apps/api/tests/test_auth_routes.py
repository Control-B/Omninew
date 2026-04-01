from fastapi.testclient import TestClient

from app.api.deps import get_shopify_auth_service
from app.main import app
from app.schemas.common import ShopifySetupStatusResponse
from app.services.shopify_auth_service import OAuthCallbackResult


class FakeShopifyAuthService:
    def build_install_url(self, **kwargs):
        return "https://acme.myshopify.com/admin/oauth/authorize?client_id=test"

    def get_setup_status(self):
        return ShopifySetupStatusResponse(
            status="ready",
            app_url="https://omninew.example.com",
            api_public_url="https://omninew.example.com/backend",
            dashboard_connect_url="https://omninew.example.com/dashboard/connect",
            install_url="https://omninew.example.com/backend/api/v1/auth/shopify/install",
            callback_url="https://omninew.example.com/backend/api/v1/auth/shopify/callback",
            uninstall_webhook_url="https://omninew.example.com/backend/api/v1/webhooks/shopify/app-uninstalled",
            scopes=["read_products", "write_content"],
            app_key_configured=True,
            app_secret_configured=True,
            webhook_secret_configured=True,
            https_ready=True,
            notes=[],
        )

    async def handle_callback(self, query_params):
        return OAuthCallbackResult(
            tenant_id="00000000-0000-0000-0000-000000000101",
            store_id="00000000-0000-0000-0000-000000000202",
            widget_key="omn_test_widget_key",
            business_name="Acme Wellness",
            shop_domain="acme.myshopify.com",
            store_name="Acme Wellness",
            assistant_name="Acme Concierge",
            tone="balanced",
            welcome_message="Welcome!",
        )


def test_shopify_install_redirect() -> None:
    app.dependency_overrides[get_shopify_auth_service] = lambda: FakeShopifyAuthService()
    client = TestClient(app)

    response = client.get(
        "/api/v1/auth/shopify/install",
        params={
            "shop": "acme.myshopify.com",
            "business_name": "Acme Wellness",
            "owner_email": "owner@example.com",
            "assistant_name": "Acme Concierge",
        },
        follow_redirects=False,
    )

    app.dependency_overrides.clear()

    assert response.status_code == 302
    assert response.headers["location"].startswith("https://acme.myshopify.com/admin/oauth/authorize")


def test_shopify_callback_redirects_to_dashboard() -> None:
    app.dependency_overrides[get_shopify_auth_service] = lambda: FakeShopifyAuthService()
    client = TestClient(app)

    response = client.get(
        "/api/v1/auth/shopify/callback",
        params={"shop": "acme.myshopify.com", "code": "abc", "hmac": "valid", "state": "signed"},
        follow_redirects=False,
    )

    app.dependency_overrides.clear()

    assert response.status_code == 302
    assert "/dashboard/connect/callback?status=success" in response.headers["location"]
    assert "widgetKey=omn_test_widget_key" in response.headers["location"]


def test_shopify_setup_status_route() -> None:
    app.dependency_overrides[get_shopify_auth_service] = lambda: FakeShopifyAuthService()
    client = TestClient(app)

    response = client.get("/api/v1/auth/shopify/setup")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["callback_url"].endswith("/auth/shopify/callback")
