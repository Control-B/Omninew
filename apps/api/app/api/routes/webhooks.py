from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/livekit")
async def livekit_webhook(event: dict) -> dict:
    return {"received": True, "event_type": event.get("type")}


@router.post("/shopify/app-uninstalled")
async def shopify_app_uninstalled(request: Request) -> dict:
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")
    return {"received": True, "topic": "app/uninstalled", "shop_domain": shop_domain}
