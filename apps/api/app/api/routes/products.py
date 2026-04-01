from fastapi import APIRouter, Depends

from app.api.deps import get_shopify_service
from app.schemas.common import ProductDetailsRequest, ProductRecommendationRequest, ProductSearchRequest
from app.services.shopify_service import ShopifyService

router = APIRouter()


@router.post("/search")
async def search_products(
    payload: ProductSearchRequest,
    shopify_service: ShopifyService = Depends(get_shopify_service),
) -> dict:
    items = await shopify_service.search_products(
        shop_domain=payload.shop_domain,
        storefront_access_token=payload.storefront_access_token,
        query_text=payload.query,
        limit=payload.limit,
    )
    return {"items": items}


@router.post("/details")
async def product_details(
    payload: ProductDetailsRequest,
    shopify_service: ShopifyService = Depends(get_shopify_service),
) -> dict:
    item = await shopify_service.get_product_details(
        shop_domain=payload.shop_domain,
        storefront_access_token=payload.storefront_access_token,
        product_id=payload.product_id,
    )
    return {"item": item}


@router.post("/recommendations")
async def recommend_products(
    payload: ProductRecommendationRequest,
    shopify_service: ShopifyService = Depends(get_shopify_service),
) -> dict:
    items = await shopify_service.recommend_products(
        shop_domain=payload.shop_domain,
        storefront_access_token=payload.storefront_access_token,
        context=payload.context,
        limit=payload.limit,
    )
    return {"items": items}
