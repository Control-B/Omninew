from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from app.services.shopify_auth_service import ShopifyAuthService
from app.api.deps import get_shopify_auth_service
from app.core.config import get_settings
from app.schemas.common import ShopifySetupStatusResponse

router = APIRouter()


@router.get("/")
async def auth_status() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ready" if settings.shopify_app_key and settings.shopify_app_secret else "pending",
        "message": "Shopify OAuth install flow is available when app credentials are configured.",
    }


@router.get("/shopify/setup", response_model=ShopifySetupStatusResponse)
async def shopify_setup_status(
    auth_service: ShopifyAuthService = Depends(get_shopify_auth_service),
) -> ShopifySetupStatusResponse:
    return auth_service.get_setup_status()


@router.get("/shopify/install")
async def install_shopify_app(
    shop: str = Query(..., alias="shop"),
    business_name: str = Query(..., min_length=2),
    owner_email: str = Query(...),
    assistant_name: str = Query("Omniweb assistant"),
    tone: str = Query("balanced"),
    welcome_message: str = Query("Hi! I can recommend products, answer policy questions, and help capture leads for premium items."),
    voice_enabled: bool = Query(True),
    auth_service: ShopifyAuthService = Depends(get_shopify_auth_service),
) -> RedirectResponse:
    try:
        install_url = auth_service.build_install_url(
            shop_domain=shop,
            business_name=business_name,
            owner_email=owner_email,
            assistant_name=assistant_name,
            tone=tone,
            welcome_message=welcome_message,
            voice_enabled=voice_enabled,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return RedirectResponse(install_url, status_code=302)


@router.get("/shopify/callback")
async def shopify_oauth_callback(
    request: Request,
    auth_service: ShopifyAuthService = Depends(get_shopify_auth_service),
) -> RedirectResponse:
    query_params = {key: value for key, value in request.query_params.items()}
    settings = get_settings()
    try:
        result = await auth_service.handle_callback(query_params)
        query = urlencode(
            {
                "status": "success",
                "tenantId": result.tenant_id,
                "storeId": result.store_id,
                "widgetKey": result.widget_key,
                "businessName": result.business_name,
                "shopDomain": result.shop_domain,
                "storeName": result.store_name or "",
                "assistantName": result.assistant_name,
                "tone": result.tone,
                "welcomeMessage": result.welcome_message,
            }
        )
        return RedirectResponse(f"{settings.app_url.rstrip('/')}/dashboard/connect/callback?{query}", status_code=302)
    except ValueError as error:
        query = urlencode({"status": "error", "message": str(error)})
        return RedirectResponse(f"{settings.app_url.rstrip('/')}/dashboard/connect/callback?{query}", status_code=302)
