from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_tenant_service
from app.main import app
from app.schemas.common import AssistantConfigResponse, TenantBootstrapResponse, WidgetPublicConfigResponse


class FakeTenantService:
    def __init__(self) -> None:
        self.tenant_id = uuid4()
        self.store_id = uuid4()

    async def bootstrap_tenant(self, payload):
        return TenantBootstrapResponse(
            tenant_id=self.tenant_id,
            store_id=self.store_id,
            widget_key="omn_test_widget_key",
            business_name=payload.business_name,
            shop_domain=payload.shop_domain,
            store_name="Demo Store",
            assistant_name=payload.assistant_name,
            tone=payload.tone,
            welcome_message=payload.welcome_message,
        )

    async def get_public_widget_config(self, widget_key: str):
        if widget_key != "omn_test_widget_key":
            return None
        return WidgetPublicConfigResponse(
            widget_key=widget_key,
            tenant_id=self.tenant_id,
            store_id=self.store_id,
            assistant_name="Demo Assistant",
            welcome_message="Welcome!",
            voice_enabled=True,
            theme_color="#7c3aed",
            store_name="Demo Store",
            support_email="owner@example.com",
        )

    async def get_assistant_config(self, tenant_id: UUID, store_id: UUID | None = None):
        return AssistantConfigResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            assistant_name="Demo Assistant",
            tone="balanced",
            system_prompt="Be helpful.",
            welcome_message="Welcome!",
            voice_enabled=True,
            sales_mode_enabled=True,
            support_mode_enabled=True,
            do_agent_id=None,
            theme_color="#7c3aed",
        )

    async def update_assistant_config(self, payload):
        return AssistantConfigResponse(
            tenant_id=payload.tenant_id,
            store_id=payload.store_id,
            assistant_name=payload.assistant_name,
            tone=payload.tone,
            system_prompt=payload.system_prompt,
            welcome_message=payload.welcome_message,
            voice_enabled=payload.voice_enabled,
            sales_mode_enabled=payload.sales_mode_enabled,
            support_mode_enabled=payload.support_mode_enabled,
            do_agent_id=payload.do_agent_id,
            theme_color=payload.theme_color,
        )


def test_bootstrap_tenant_route() -> None:
    fake_service = FakeTenantService()
    app.dependency_overrides[get_tenant_service] = lambda: fake_service

    client = TestClient(app)
    response = client.post(
        "/api/v1/tenants/bootstrap",
        json={
            "business_name": "Acme Wellness",
            "owner_email": "owner@example.com",
            "shop_domain": "acme.myshopify.com",
            "admin_access_token": "shpat_test",
            "assistant_name": "Acme Concierge",
            "tone": "balanced",
            "welcome_message": "Welcome!",
            "voice_enabled": True,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["widget_key"] == "omn_test_widget_key"
    assert payload["business_name"] == "Acme Wellness"


def test_assistant_config_route_roundtrip() -> None:
    fake_service = FakeTenantService()
    app.dependency_overrides[get_tenant_service] = lambda: fake_service

    client = TestClient(app)
    response = client.get(
        "/api/v1/assistant-config/",
        params={"tenant_id": str(fake_service.tenant_id), "store_id": str(fake_service.store_id)},
    )
    assert response.status_code == 200
    assert response.json()["assistant_name"] == "Demo Assistant"

    update_response = client.put(
        "/api/v1/assistant-config/",
        json={
            "tenant_id": str(fake_service.tenant_id),
            "store_id": str(fake_service.store_id),
            "assistant_name": "Updated Assistant",
            "tone": "sales",
            "system_prompt": "Sell bundles.",
            "welcome_message": "Need help choosing?",
            "voice_enabled": False,
            "sales_mode_enabled": True,
            "support_mode_enabled": True,
            "do_agent_id": None,
            "theme_color": "#06b6d4",
        },
    )

    app.dependency_overrides.clear()

    assert update_response.status_code == 200
    assert update_response.json()["assistant_name"] == "Updated Assistant"
    assert update_response.json()["voice_enabled"] is False
