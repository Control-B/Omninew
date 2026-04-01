from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.core.database import SupabaseGateway
from app.schemas.common import LeadCapturePayload
from app.services.lead_service import LeadService
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService


class AgentToolService:
    def __init__(
        self,
        db: SupabaseGateway,
        tenant_service: TenantService,
        lead_service: LeadService,
        shopify_service: ShopifyService,
    ) -> None:
        self.db = db
        self.tenant_service = tenant_service
        self.lead_service = lead_service
        self.shopify_service = shopify_service

    async def search_products(
        self,
        *,
        tenant_id: UUID | None,
        store_id: UUID | None,
        widget_key: str | None,
        query: str,
        limit: int,
    ) -> dict[str, Any]:
        runtime_context = await self.tenant_service.resolve_runtime_context(
            widget_key=widget_key,
            tenant_id=tenant_id,
            store_id=store_id,
            metadata={},
        )
        filters = {"tenant_id": str(runtime_context.tenant_id)}
        if runtime_context.store_id:
            filters["store_id"] = str(runtime_context.store_id)
        rows = await self.db.select(
            "products",
            columns="shopify_product_id,title,handle,description,price,currency_code,image_url,metadata",
            filters=filters,
            order="updated_at.desc",
            limit=50,
        )
        items = rows if isinstance(rows, list) else []
        lowered = query.lower().strip()
        ranked: list[dict[str, Any]] = []
        for item in items:
            haystack = " ".join(
                [
                    str(item.get("title") or ""),
                    str(item.get("handle") or ""),
                    str(item.get("description") or ""),
                ]
            ).lower()
            score = 0
            for token in lowered.split():
                if token in haystack:
                    score += 1
            if score > 0:
                ranked.append({**item, "score": score})
        ranked.sort(key=lambda item: (item.get("score", 0), item.get("title") or ""), reverse=True)
        return {
            "items": [
                {
                    "product_id": item.get("shopify_product_id"),
                    "title": item.get("title"),
                    "handle": item.get("handle"),
                    "price": item.get("price"),
                    "currency_code": item.get("currency_code"),
                    "image_url": item.get("image_url"),
                }
                for item in ranked[:limit]
            ]
        }

    async def lookup_policies(
        self,
        *,
        tenant_id: UUID | None,
        store_id: UUID | None,
        widget_key: str | None,
        policy_type: str | None,
    ) -> dict[str, Any]:
        runtime_context = await self.tenant_service.resolve_runtime_context(
            widget_key=widget_key,
            tenant_id=tenant_id,
            store_id=store_id,
            metadata={},
        )
        filters = {"tenant_id": str(runtime_context.tenant_id)}
        if runtime_context.store_id:
            filters["store_id"] = str(runtime_context.store_id)
        if policy_type:
            filters["policy_type"] = policy_type
        rows = await self.db.select(
            "policies",
            columns="policy_type,title,body,url,updated_at",
            filters=filters,
            order="updated_at.desc",
            limit=10,
        )
        items = rows if isinstance(rows, list) else []
        return {"items": items}

    async def capture_lead(
        self,
        *,
        tenant_id: UUID | None,
        store_id: UUID | None,
        widget_key: str | None,
        session_id: UUID | None,
        name: str | None,
        email: str | None,
        phone: str | None,
        intent: str,
        product_interest: str | None,
        notes: str | None,
    ) -> dict[str, Any]:
        runtime_context = await self.tenant_service.resolve_runtime_context(
            widget_key=widget_key,
            tenant_id=tenant_id,
            store_id=store_id,
            metadata={},
        )
        stored = await self.lead_service.capture_lead(
            LeadCapturePayload(
                tenant_id=runtime_context.tenant_id,
                session_id=session_id,
                name=name,
                email=email,
                phone=phone,
                intent=intent,
                product_interest=product_interest,
                notes=notes,
            )
        )
        return {"lead": stored}

    async def request_handoff(
        self,
        *,
        tenant_id: UUID | None,
        store_id: UUID | None,
        widget_key: str | None,
        customer_email: str | None,
        message: str,
        session_id: UUID | None,
    ) -> dict[str, Any]:
        runtime_context = await self.tenant_service.resolve_runtime_context(
            widget_key=widget_key,
            tenant_id=tenant_id,
            store_id=store_id,
            metadata={},
        )
        support_request = await self.shopify_service.create_support_request(
            tenant_id=str(runtime_context.tenant_id),
            customer_email=customer_email,
            message=message,
        )
        await self.db.insert(
            "event_logs",
            {
                "id": str(uuid4()),
                "tenant_id": str(runtime_context.tenant_id),
                "session_id": str(session_id) if session_id else None,
                "event_type": "agent_handoff_requested",
                "source": "agent_tool",
                "payload": {
                    "message": message,
                    "customer_email": customer_email,
                    "store_id": str(runtime_context.store_id) if runtime_context.store_id else None,
                },
            },
        )
        return {"handoff": support_request}