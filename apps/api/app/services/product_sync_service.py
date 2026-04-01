from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.database import SupabaseGateway
from app.services.shopify_service import ShopifyService


class ProductSyncService:
    def __init__(self, shopify_service: ShopifyService, db: SupabaseGateway) -> None:
        self.shopify_service = shopify_service
        self.db = db

    async def sync_catalog(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        shop_domain: str,
        admin_access_token: str,
    ) -> dict[str, Any]:
        products = await self.shopify_service.fetch_products(shop_domain, admin_access_token)
        collections = await self.shopify_service.fetch_collections(shop_domain, admin_access_token)

        product_rows = [self._map_product(tenant_id, store_id, shop_domain, product) for product in products]
        collection_rows = [self._map_collection(tenant_id, store_id, collection) for collection in collections]

        saved_products = await self.db.upsert_many("products", product_rows, on_conflict="tenant_id,shopify_product_id")
        saved_collections = await self.db.upsert_many("collections", collection_rows, on_conflict="tenant_id,shopify_collection_id")

        return {
            "products_synced": len(saved_products) or len(product_rows),
            "collections_synced": len(saved_collections) or len(collection_rows),
        }

    def _map_product(
        self,
        tenant_id: UUID,
        store_id: UUID,
        shop_domain: str,
        product: dict[str, Any],
    ) -> dict[str, Any]:
        featured = product.get("featuredImage") or {}
        variants = product.get("variants", {}).get("nodes", [])
        primary_variant = variants[0] if variants else {}
        return {
            "tenant_id": str(tenant_id),
            "store_id": str(store_id),
            "shop_domain": shop_domain,
            "shopify_product_id": product.get("id"),
            "title": product.get("title"),
            "handle": product.get("handle"),
            "description": product.get("description"),
            "status": "active",
            "available": bool(primary_variant.get("availableForSale", True)),
            "price": primary_variant.get("price"),
            "currency_code": None,
            "image_url": featured.get("url"),
            "tags": product.get("tags", []),
            "metadata": {"raw": product},
        }

    def _map_collection(self, tenant_id: UUID, store_id: UUID, collection: dict[str, Any]) -> dict[str, Any]:
        return {
            "tenant_id": str(tenant_id),
            "store_id": str(store_id),
            "shopify_collection_id": collection.get("id"),
            "title": collection.get("title"),
            "handle": collection.get("handle"),
            "description": collection.get("description"),
            "metadata": {"raw": collection},
        }
