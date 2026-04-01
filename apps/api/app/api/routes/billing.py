from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.deps import get_billing_service
from app.schemas.common import (
    BillingOverviewResponse,
    BillingPlanUpdateRequest,
    ShopifyBillingCheckoutRequest,
    ShopifyBillingCheckoutResponse,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
)
from app.services.billing_service import BillingService
from app.core.config import get_settings

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


@router.post("/shopify/checkout", response_model=ShopifyBillingCheckoutResponse)
async def create_shopify_billing_checkout(
    payload: ShopifyBillingCheckoutRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> ShopifyBillingCheckoutResponse:
    try:
        return await billing_service.create_shopify_checkout(
            tenant_id=payload.tenant_id,
            store_id=payload.store_id,
            plan_code=payload.plan_code,
            return_path=payload.return_path,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/shopify/callback")
async def handle_shopify_billing_callback(
    request: Request,
    billing_service: BillingService = Depends(get_billing_service),
) -> RedirectResponse:
    query_params = {key: value for key, value in request.query_params.items()}
    settings = get_settings()
    try:
        redirect_url = await billing_service.complete_shopify_checkout(query_params)
        return RedirectResponse(redirect_url, status_code=302)
    except ValueError as error:
        query = urlencode({"billing": "error", "message": str(error)})
        return RedirectResponse(f"{settings.app_url.rstrip('/')}/dashboard/connect?{query}", status_code=302)