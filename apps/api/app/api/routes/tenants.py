from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_tenant_service
from app.schemas.common import TenantBootstrapRequest, TenantBootstrapResponse, WidgetPublicConfigResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.get("/")
async def list_tenants() -> dict[str, list[dict[str, str]]]:
    return {"items": []}


@router.post("/bootstrap", response_model=TenantBootstrapResponse)
async def bootstrap_tenant(
    payload: TenantBootstrapRequest,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> TenantBootstrapResponse:
    return await tenant_service.bootstrap_tenant(payload)


@router.get("/widget/{widget_key}", response_model=WidgetPublicConfigResponse)
async def get_widget_config(
    widget_key: str,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> WidgetPublicConfigResponse:
    config = await tenant_service.get_public_widget_config(widget_key)
    if not config:
        raise HTTPException(status_code=404, detail="Widget key not found.")
    return config
