from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.database import SupabaseGateway
from app.services.shopify_service import ShopifyService


class PolicySyncService:
    def __init__(self, shopify_service: ShopifyService, db: SupabaseGateway) -> None:
        self.shopify_service = shopify_service
        self.db = db

    async def sync_policies(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        shop_domain: str,
        admin_access_token: str,
    ) -> dict[str, Any]:
        shop_data = await self.shopify_service.fetch_policies(shop_domain, admin_access_token)
        rows = self._map_policies(tenant_id, store_id, shop_data)
        saved = await self.db.upsert_many("policies", rows, on_conflict="tenant_id,store_id,policy_type")
        return {"policies_synced": len(saved) or len(rows)}

    def _map_policies(self, tenant_id: UUID, store_id: UUID, shop_data: dict[str, Any]) -> list[dict[str, Any]]:
        policy_map = {
            "privacy": shop_data.get("privacyPolicy"),
            "refund": shop_data.get("refundPolicy"),
            "shipping": shop_data.get("shippingPolicy"),
            "terms": shop_data.get("termsOfService"),
        }
        rows: list[dict[str, Any]] = []
        for policy_type, policy in policy_map.items():
            if not policy:
                continue
            rows.append(
                {
                    "tenant_id": str(tenant_id),
                    "store_id": str(store_id),
                    "policy_type": policy_type,
                    "title": policy.get("title"),
                    "body": policy.get("body"),
                    "url": policy.get("url"),
                    "metadata": {"raw": policy},
                }
            )
        return rows
