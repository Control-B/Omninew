from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_billing_service
from app.schemas.common import (
    BillingOverviewResponse,
    BillingPlanUpdateRequest,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
)
from app.services.billing_service import BillingService

router = APIRouter()


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def list_billing_plans(
    billing_service: BillingService = Depends(get_billing_service),
) -> list[SubscriptionPlanResponse]:
    return await billing_service.list_plans()


@router.get("/", response_model=BillingOverviewResponse)
async def get_billing_overview(
    tenant_id: str,
    store_id: str | None = None,
    billing_service: BillingService = Depends(get_billing_service),
) -> BillingOverviewResponse:
    return await billing_service.get_billing_overview(
        tenant_id=UUID(tenant_id),
        store_id=UUID(store_id) if store_id else None,
    )


@router.put("/plan", response_model=TenantSubscriptionResponse)
async def update_billing_plan(
    payload: BillingPlanUpdateRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> TenantSubscriptionResponse:
    return await billing_service.update_plan(payload.tenant_id, payload.plan_code)