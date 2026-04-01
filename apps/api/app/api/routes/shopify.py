from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_policy_sync_service, get_product_sync_service, get_shopify_service, get_tenant_service
from app.schemas.common import ShopifyConnectRequest, ShopifySyncRequest
from app.services.policy_sync_service import PolicySyncService
from app.services.product_sync_service import ProductSyncService
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService

router = APIRouter()


@router.post("/connect")
async def connect_shopify_store(
    payload: ShopifyConnectRequest,
    shopify_service: ShopifyService = Depends(get_shopify_service),
) -> dict:
    return await shopify_service.connect_store(
        tenant_id=str(payload.tenant_id),
        shop_domain=payload.shop_domain,
        admin_access_token=payload.admin_access_token,
        storefront_access_token=payload.storefront_access_token,
    )


@router.post("/sync")
async def sync_shopify_store(
    payload: ShopifySyncRequest,
    product_sync_service: ProductSyncService = Depends(get_product_sync_service),
    policy_sync_service: PolicySyncService = Depends(get_policy_sync_service),
    tenant_service: TenantService = Depends(get_tenant_service),
) -> dict:
    store = await tenant_service.get_store(tenant_id=payload.tenant_id, store_id=payload.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found for tenant.")

    shop_domain = payload.shop_domain or store.get("shop_domain")
    admin_access_token = payload.admin_access_token or await tenant_service.get_admin_token(
        tenant_id=payload.tenant_id,
        store_id=payload.store_id,
    )

    if not shop_domain or not admin_access_token:
        raise HTTPException(status_code=400, detail="Stored Shopify credentials are incomplete for this store.")

    results: dict[str, int] = {}

    if payload.include_products or payload.include_collections:
        results.update(
            await product_sync_service.sync_catalog(
                tenant_id=payload.tenant_id,
                store_id=payload.store_id,
                shop_domain=shop_domain,
                admin_access_token=admin_access_token,
            )
        )
    if payload.include_policies:
        results.update(
            await policy_sync_service.sync_policies(
                tenant_id=payload.tenant_id,
                store_id=payload.store_id,
                shop_domain=shop_domain,
                admin_access_token=admin_access_token,
            )
        )
    return results
