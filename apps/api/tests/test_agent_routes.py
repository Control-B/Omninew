from uuid import uuid4
import os

from fastapi.testclient import TestClient

from app.api.deps import get_agent_tool_service
from app.core.config import get_settings
from app.main import app


class FakeAgentToolService:
    async def search_products(self, **kwargs):
        return {"items": [{"product_id": "gid://shopify/Product/1", "title": "Demo Product"}]}

    async def lookup_policies(self, **kwargs):
        return {"items": [{"policy_type": "refund", "title": "Refund Policy"}]}

    async def capture_lead(self, **kwargs):
        return {"lead": {"id": "lead-1", "status": "new"}}

    async def request_handoff(self, **kwargs):
        return {"handoff": {"status": "queued"}}


def test_agent_blueprint_route() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/agent/blueprint")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "openai/gpt-oss-120b"
    assert any(route["name"] == "product-search" for route in payload["function_routes"])


def test_agent_tool_requires_secret() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/agent-tools/product-search",
        json={"tenant_id": str(uuid4()), "query": "shoe"},
    )
    assert response.status_code in {401, 503}


def test_agent_tool_routes_with_fake_service() -> None:
    previous_secret = os.environ.get("DO_AGENT_ROUTE_SECRET")
    os.environ["DO_AGENT_ROUTE_SECRET"] = "test-secret"
    get_settings.cache_clear()

    app.dependency_overrides[get_agent_tool_service] = lambda: FakeAgentToolService()
    client = TestClient(app)

    response = client.post(
        "/api/v1/agent-tools/product-search",
        headers={"X-Agent-Route-Secret": "test-secret"},
        json={"tenant_id": str(uuid4()), "query": "shoe"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["title"] == "Demo Product"

    policy_response = client.post(
        "/api/v1/agent-tools/policy-lookup",
        headers={"X-Agent-Route-Secret": "test-secret"},
        json={"tenant_id": str(uuid4()), "policy_type": "refund"},
    )
    assert policy_response.status_code == 200

    lead_response = client.post(
        "/api/v1/agent-tools/lead-capture",
        headers={"X-Agent-Route-Secret": "test-secret"},
        json={"tenant_id": str(uuid4()), "intent": "buying_intent_detected", "email": "buyer@example.com"},
    )
    assert lead_response.status_code == 200

    handoff_response = client.post(
        "/api/v1/agent-tools/handoff",
        headers={"X-Agent-Route-Secret": "test-secret"},
        json={"tenant_id": str(uuid4()), "message": "Need human help", "customer_email": "buyer@example.com"},
    )
    assert handoff_response.status_code == 200

    app.dependency_overrides.clear()
    if previous_secret is None:
        os.environ.pop("DO_AGENT_ROUTE_SECRET", None)
    else:
        os.environ["DO_AGENT_ROUTE_SECRET"] = previous_secret
    get_settings.cache_clear()