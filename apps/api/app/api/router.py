from fastapi import APIRouter

from app.api.routes import assistant, auth, billing, chat, health, leads, products, shopify, tenants, transcripts, voice, webhooks

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(assistant.router, prefix="/assistant-config", tags=["assistant-config"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(shopify.router, prefix="/shopify", tags=["shopify"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
