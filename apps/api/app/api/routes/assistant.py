from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_tenant_service
from app.schemas.common import AssistantConfigRequest, AssistantConfigResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.get("/", response_model=AssistantConfigResponse)
async def get_assistant_config(
    tenant_id: UUID,
    store_id: UUID | None = None,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> AssistantConfigResponse:
    return await tenant_service.get_assistant_config(tenant_id=tenant_id, store_id=store_id)


@router.put("/", response_model=AssistantConfigResponse)
async def update_assistant_config(
    payload: AssistantConfigRequest,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> AssistantConfigResponse:
    return await tenant_service.update_assistant_config(payload)
