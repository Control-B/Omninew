from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.deps import get_agent_tool_service
from app.core.config import get_settings
from app.schemas.common import (
    AgentToolHandoffRequest,
    AgentToolLeadCaptureRequest,
    AgentToolPolicyLookupRequest,
    AgentToolProductSearchRequest,
    AgentToolResponse,
)
from app.services.agent_tool_service import AgentToolService

router = APIRouter()


def require_agent_route_secret(x_agent_route_secret: str | None = Header(default=None)) -> None:
    settings = get_settings()
    configured_secret = settings.do_agent_route_secret
    if not configured_secret:
        raise HTTPException(status_code=503, detail="Agent route secret is not configured.")
    if x_agent_route_secret != configured_secret:
        raise HTTPException(status_code=401, detail="Invalid agent route secret.")


@router.post("/product-search", response_model=AgentToolResponse, dependencies=[Depends(require_agent_route_secret)])
async def product_search_tool(
    payload: AgentToolProductSearchRequest,
    service: AgentToolService = Depends(get_agent_tool_service),
) -> AgentToolResponse:
    data = await service.search_products(
        tenant_id=payload.tenant_id,
        store_id=payload.store_id,
        widget_key=payload.widget_key,
        query=payload.query,
        limit=payload.limit,
    )
    return AgentToolResponse(data=data)


@router.post("/policy-lookup", response_model=AgentToolResponse, dependencies=[Depends(require_agent_route_secret)])
async def policy_lookup_tool(
    payload: AgentToolPolicyLookupRequest,
    service: AgentToolService = Depends(get_agent_tool_service),
) -> AgentToolResponse:
    data = await service.lookup_policies(
        tenant_id=payload.tenant_id,
        store_id=payload.store_id,
        widget_key=payload.widget_key,
        policy_type=payload.policy_type,
    )
    return AgentToolResponse(data=data)


@router.post("/lead-capture", response_model=AgentToolResponse, dependencies=[Depends(require_agent_route_secret)])
async def lead_capture_tool(
    payload: AgentToolLeadCaptureRequest,
    service: AgentToolService = Depends(get_agent_tool_service),
) -> AgentToolResponse:
    data = await service.capture_lead(
        tenant_id=payload.tenant_id,
        store_id=payload.store_id,
        widget_key=payload.widget_key,
        session_id=payload.session_id,
        name=payload.name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        intent=payload.intent,
        product_interest=payload.product_interest,
        notes=payload.notes,
    )
    return AgentToolResponse(data=data)


@router.post("/handoff", response_model=AgentToolResponse, dependencies=[Depends(require_agent_route_secret)])
async def handoff_tool(
    payload: AgentToolHandoffRequest,
    service: AgentToolService = Depends(get_agent_tool_service),
) -> AgentToolResponse:
    data = await service.request_handoff(
        tenant_id=payload.tenant_id,
        store_id=payload.store_id,
        widget_key=payload.widget_key,
        customer_email=str(payload.customer_email) if payload.customer_email else None,
        message=payload.message,
        session_id=payload.session_id,
    )
    return AgentToolResponse(data=data)