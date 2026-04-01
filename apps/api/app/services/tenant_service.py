from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.core.database import SupabaseGateway
from app.schemas.common import (
    AssistantConfigPayload,
    AssistantConfigRequest,
    AssistantConfigResponse,
    TenantBootstrapRequest,
    TenantBootstrapResponse,
    WidgetPublicConfigResponse,
)
from app.services.shopify_service import ShopifyService


@dataclass
class ResolvedTenantContext:
    tenant_id: UUID
    store_id: UUID | None
    widget_key: str | None
    shop_domain: str | None
    store_name: str | None
    support_email: str | None
    assistant_name: str
    tone: str
    system_prompt: str | None
    welcome_message: str
    voice_enabled: bool
    sales_mode_enabled: bool
    support_mode_enabled: bool
    do_agent_id: str | None
    theme_color: str | None
    products: list[dict]
    policies: list[dict]


class TenantService:
    def __init__(self, db: SupabaseGateway, shopify_service: ShopifyService) -> None:
        self.db = db
        self.shopify_service = shopify_service

    async def bootstrap_tenant(self, payload: TenantBootstrapRequest) -> TenantBootstrapResponse:
        store_info = await self.shopify_service.get_store_info(payload.shop_domain, payload.admin_access_token)

        tenant_id = uuid4()
        store_id = uuid4()
        owner_id = uuid4()
        widget_id = uuid4()
        assistant_config_id = uuid4()
        widget_key = self._generate_widget_key()
        slug = self._build_slug(payload.business_name, payload.shop_domain)

        tenant_row = {
            "id": str(tenant_id),
            "name": payload.business_name,
            "slug": slug,
            "status": "active",
            "metadata": {
                "shop_domain": payload.shop_domain,
                "origin": "dashboard_bootstrap",
            },
        }
        owner_row = {
            "id": str(owner_id),
            "tenant_id": str(tenant_id),
            "email": payload.owner_email,
            "full_name": payload.business_name,
            "role": "merchant_admin",
            "metadata": {"origin": "bootstrap"},
        }
        store_row = {
            "id": str(store_id),
            "tenant_id": str(tenant_id),
            "shop_domain": payload.shop_domain,
            "store_name": store_info.get("name") or payload.business_name,
            "email": store_info.get("email"),
            "currency_code": store_info.get("currencyCode"),
            "storefront_access_token_last4": (payload.storefront_access_token or "")[-4:] or None,
            "status": "connected",
            "metadata": {"raw": store_info},
        }
        assistant_row = self._build_assistant_row(
            tenant_id=tenant_id,
            store_id=store_id,
            assistant_config_id=assistant_config_id,
            config=AssistantConfigPayload(
                assistant_name=payload.assistant_name,
                tone=payload.tone,
                welcome_message=payload.welcome_message,
                voice_enabled=payload.voice_enabled,
            ),
        )
        widget_row = {
            "id": str(widget_id),
            "tenant_id": str(tenant_id),
            "store_id": str(store_id),
            "public_key": widget_key,
            "label": "Default storefront widget",
            "allowed_domains": [f"https://{payload.shop_domain}"],
            "status": "active",
            "settings": {
                "assistant_name": payload.assistant_name,
                "welcome_message": payload.welcome_message,
                "voice_enabled": payload.voice_enabled,
            },
        }

        await self.db.insert("tenants", tenant_row)
        await self.db.insert("users", owner_row)
        await self.db.insert("shopify_stores", store_row)
        await self.db.insert(
            "shopify_tokens",
            {
                "tenant_id": str(tenant_id),
                "store_id": str(store_id),
                "token_type": "admin",
                "token_encrypted": payload.admin_access_token,
                "metadata": {"source": "dashboard_bootstrap"},
            },
        )
        if payload.storefront_access_token:
            await self.db.insert(
                "shopify_tokens",
                {
                    "tenant_id": str(tenant_id),
                    "store_id": str(store_id),
                    "token_type": "storefront",
                    "token_encrypted": payload.storefront_access_token,
                    "metadata": {"source": "dashboard_bootstrap"},
                },
            )
        await self.db.insert("agent_configs", assistant_row)
        await self.db.insert("widget_deployments", widget_row)

        return TenantBootstrapResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            widget_key=widget_key,
            business_name=payload.business_name,
            shop_domain=payload.shop_domain,
            store_name=store_row["store_name"],
            assistant_name=payload.assistant_name,
            tone=payload.tone,
            welcome_message=payload.welcome_message,
        )

    async def upsert_shopify_installation(
        self,
        *,
        business_name: str,
        owner_email: str,
        shop_domain: str,
        admin_access_token: str,
        storefront_access_token: str | None,
        assistant_name: str,
        tone: str,
        welcome_message: str,
        voice_enabled: bool,
    ) -> TenantBootstrapResponse:
        store_info = await self.shopify_service.get_store_info(shop_domain, admin_access_token)
        existing_store = await self.db.select("shopify_stores", filters={"shop_domain": shop_domain}, single=True)

        if existing_store:
            tenant_id = UUID(existing_store["tenant_id"])
            store_id = UUID(existing_store["id"])
            await self.db.update(
                "tenants",
                {
                    "name": business_name,
                    "metadata": {
                        **(await self._fetch_tenant_metadata(tenant_id)),
                        "shop_domain": shop_domain,
                        "origin": "shopify_oauth",
                    },
                },
                filters={"id": str(tenant_id)},
            )
            await self.db.update(
                "shopify_stores",
                {
                    "store_name": store_info.get("name") or business_name,
                    "email": store_info.get("email"),
                    "currency_code": store_info.get("currencyCode"),
                    "status": "connected",
                    "metadata": {"raw": store_info},
                },
                filters={"id": str(store_id)},
            )
            await self._upsert_user(tenant_id=tenant_id, owner_email=owner_email, business_name=business_name)
            await self._upsert_shopify_token(
                tenant_id=tenant_id,
                store_id=store_id,
                token_type="admin",
                token_value=admin_access_token,
            )
            if storefront_access_token:
                await self._upsert_shopify_token(
                    tenant_id=tenant_id,
                    store_id=store_id,
                    token_type="storefront",
                    token_value=storefront_access_token,
                )
            await self._upsert_assistant_config(
                tenant_id=tenant_id,
                store_id=store_id,
                assistant_name=assistant_name,
                tone=tone,
                welcome_message=welcome_message,
                voice_enabled=voice_enabled,
            )
            widget_key = await self._ensure_widget_deployment(
                tenant_id=tenant_id,
                store_id=store_id,
                assistant_name=assistant_name,
                welcome_message=welcome_message,
                voice_enabled=voice_enabled,
                shop_domain=shop_domain,
            )
            return TenantBootstrapResponse(
                tenant_id=tenant_id,
                store_id=store_id,
                widget_key=widget_key,
                business_name=business_name,
                shop_domain=shop_domain,
                store_name=store_info.get("name") or business_name,
                assistant_name=assistant_name,
                tone=tone,
                welcome_message=welcome_message,
            )

        return await self.bootstrap_tenant(
            TenantBootstrapRequest(
                business_name=business_name,
                owner_email=owner_email,
                shop_domain=shop_domain,
                admin_access_token=admin_access_token,
                storefront_access_token=storefront_access_token,
                assistant_name=assistant_name,
                tone=tone,
                welcome_message=welcome_message,
                voice_enabled=voice_enabled,
            )
        )

    async def get_assistant_config(self, tenant_id: UUID, store_id: UUID | None = None) -> AssistantConfigResponse:
        row = await self._fetch_assistant_row(tenant_id=tenant_id, store_id=store_id)
        if not row:
            return self._default_assistant_config(tenant_id=tenant_id, store_id=store_id)
        return self._row_to_assistant_config(row)

    async def update_assistant_config(self, payload: AssistantConfigRequest) -> AssistantConfigResponse:
        existing = await self._fetch_assistant_row(tenant_id=payload.tenant_id, store_id=payload.store_id)
        row = self._build_assistant_row(
            tenant_id=payload.tenant_id,
            store_id=payload.store_id,
            assistant_config_id=UUID(existing["id"]) if existing and existing.get("id") else uuid4(),
            config=payload,
        )
        if existing and existing.get("id"):
            stored = await self.db.update("agent_configs", row, filters={"id": existing["id"]})
            if isinstance(stored, list):
                stored = stored[0]
            return self._row_to_assistant_config(stored or row)

        stored = await self.db.insert("agent_configs", row)
        return self._row_to_assistant_config(stored or row)

    async def get_public_widget_config(self, widget_key: str) -> WidgetPublicConfigResponse | None:
        widget_row = await self.db.select(
            "widget_deployments",
            filters={"public_key": widget_key, "status": "active"},
            single=True,
        )
        if not widget_row:
            return None

        tenant_id = UUID(widget_row["tenant_id"])
        store_id = UUID(widget_row["store_id"]) if widget_row.get("store_id") else None
        assistant = await self.get_assistant_config(tenant_id=tenant_id, store_id=store_id)
        store = await self._fetch_store(tenant_id=tenant_id, store_id=store_id)

        return WidgetPublicConfigResponse(
            widget_key=widget_key,
            tenant_id=tenant_id,
            store_id=store_id,
            assistant_name=assistant.assistant_name,
            welcome_message=assistant.welcome_message,
            voice_enabled=assistant.voice_enabled,
            theme_color=assistant.theme_color,
            store_name=store.get("store_name") if store else None,
            support_email=store.get("email") if store else None,
        )

    async def get_store(self, *, tenant_id: UUID, store_id: UUID | None = None) -> dict | None:
        return await self._fetch_store(tenant_id=tenant_id, store_id=store_id)

    async def resolve_runtime_context(
        self,
        *,
        widget_key: str | None,
        tenant_id: UUID | None,
        store_id: UUID | None,
        metadata: dict,
    ) -> ResolvedTenantContext:
        widget_row = None
        if widget_key:
            widget_row = await self.db.select(
                "widget_deployments",
                filters={"public_key": widget_key, "status": "active"},
                single=True,
            )
            if not widget_row:
                raise ValueError("Unknown widget key.")
            tenant_id = UUID(widget_row["tenant_id"])
            store_id = UUID(widget_row["store_id"]) if widget_row.get("store_id") else store_id

        if tenant_id is None:
            raise ValueError("A widget key or tenant identifier is required.")

        assistant = await self.get_assistant_config(tenant_id=tenant_id, store_id=store_id)
        store = await self._fetch_store(tenant_id=tenant_id, store_id=store_id)
        products = await self._fetch_products(tenant_id=tenant_id, store_id=store_id)
        policies = await self._fetch_policies(tenant_id=tenant_id, store_id=store_id)

        return ResolvedTenantContext(
            tenant_id=tenant_id,
            store_id=store_id,
            widget_key=widget_key,
            shop_domain=store.get("shop_domain") if store else metadata.get("shop_domain"),
            store_name=store.get("store_name") if store else metadata.get("business_name"),
            support_email=store.get("email") if store else metadata.get("support_email"),
            assistant_name=assistant.assistant_name,
            tone=assistant.tone,
            system_prompt=assistant.system_prompt,
            welcome_message=assistant.welcome_message,
            voice_enabled=assistant.voice_enabled,
            sales_mode_enabled=assistant.sales_mode_enabled,
            support_mode_enabled=assistant.support_mode_enabled,
            do_agent_id=assistant.do_agent_id,
            theme_color=assistant.theme_color,
            products=products,
            policies=policies,
        )

    async def get_admin_token(self, *, tenant_id: UUID, store_id: UUID) -> str | None:
        row = await self.db.select(
            "shopify_tokens",
            filters={"tenant_id": str(tenant_id), "store_id": str(store_id), "token_type": "admin"},
            order="created_at.desc",
            limit=1,
            single=True,
        )
        if not row:
            return None
        return row.get("token_encrypted")

    async def create_voice_session(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None,
        room_name: str,
        identity: str,
        session_id: UUID,
    ) -> None:
        await self.db.insert(
            "voice_sessions",
            {
                "id": str(session_id),
                "tenant_id": str(tenant_id),
                "store_id": str(store_id) if store_id else None,
                "livekit_room_name": room_name,
                "livekit_identity": identity,
                "channel": "widget_voice",
                "status": "created",
                "metadata": {},
            },
        )

    async def _fetch_store(self, *, tenant_id: UUID, store_id: UUID | None) -> dict | None:
        filters = {"tenant_id": str(tenant_id)}
        if store_id:
            filters["id"] = str(store_id)
            return await self.db.select("shopify_stores", filters=filters, single=True)

        rows = await self.db.select("shopify_stores", filters=filters, order="created_at.desc", limit=1)
        if isinstance(rows, list) and rows:
            return rows[0]
        return None

    async def _fetch_tenant_metadata(self, tenant_id: UUID) -> dict:
        row = await self.db.select("tenants", columns="metadata", filters={"id": str(tenant_id)}, single=True)
        return (row or {}).get("metadata", {})

    async def _upsert_user(self, *, tenant_id: UUID, owner_email: str, business_name: str) -> None:
        existing = await self.db.select(
            "users",
            filters={"tenant_id": str(tenant_id), "email": owner_email},
            single=True,
        )
        payload = {
            "tenant_id": str(tenant_id),
            "email": owner_email,
            "full_name": business_name,
            "role": "merchant_admin",
            "metadata": {"origin": "shopify_oauth"},
        }
        if existing and existing.get("id"):
            await self.db.update("users", payload, filters={"id": existing["id"]})
        else:
            await self.db.insert("users", {"id": str(uuid4()), **payload})

    async def _upsert_shopify_token(self, *, tenant_id: UUID, store_id: UUID, token_type: str, token_value: str) -> None:
        existing = await self.db.select(
            "shopify_tokens",
            filters={"tenant_id": str(tenant_id), "store_id": str(store_id), "token_type": token_type},
            order="created_at.desc",
            limit=1,
            single=True,
        )
        payload = {
            "tenant_id": str(tenant_id),
            "store_id": str(store_id),
            "token_type": token_type,
            "token_encrypted": token_value,
            "metadata": {"source": "shopify_oauth"},
        }
        if existing and existing.get("id"):
            await self.db.update("shopify_tokens", payload, filters={"id": existing["id"]})
        else:
            await self.db.insert("shopify_tokens", {"id": str(uuid4()), **payload})

    async def _upsert_assistant_config(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        assistant_name: str,
        tone: str,
        welcome_message: str,
        voice_enabled: bool,
    ) -> None:
        await self.update_assistant_config(
            AssistantConfigRequest(
                tenant_id=tenant_id,
                store_id=store_id,
                assistant_name=assistant_name,
                tone=tone,  # type: ignore[arg-type]
                system_prompt=None,
                welcome_message=welcome_message,
                voice_enabled=voice_enabled,
                sales_mode_enabled=True,
                support_mode_enabled=True,
            )
        )

    async def _ensure_widget_deployment(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        assistant_name: str,
        welcome_message: str,
        voice_enabled: bool,
        shop_domain: str,
    ) -> str:
        existing = await self.db.select(
            "widget_deployments",
            filters={"tenant_id": str(tenant_id), "store_id": str(store_id), "label": "Default storefront widget"},
            single=True,
        )
        if existing and existing.get("public_key"):
            await self.db.update(
                "widget_deployments",
                {
                    "allowed_domains": [f"https://{shop_domain}"],
                    "status": "active",
                    "settings": {
                        "assistant_name": assistant_name,
                        "welcome_message": welcome_message,
                        "voice_enabled": voice_enabled,
                    },
                },
                filters={"id": existing["id"]},
            )
            return existing["public_key"]

        widget_key = self._generate_widget_key()
        await self.db.insert(
            "widget_deployments",
            {
                "id": str(uuid4()),
                "tenant_id": str(tenant_id),
                "store_id": str(store_id),
                "public_key": widget_key,
                "label": "Default storefront widget",
                "allowed_domains": [f"https://{shop_domain}"],
                "status": "active",
                "settings": {
                    "assistant_name": assistant_name,
                    "welcome_message": welcome_message,
                    "voice_enabled": voice_enabled,
                },
            },
        )
        return widget_key

    async def _fetch_assistant_row(self, *, tenant_id: UUID, store_id: UUID | None) -> dict | None:
        filters = {"tenant_id": str(tenant_id)}
        if store_id:
            rows = await self.db.select(
                "agent_configs",
                filters={**filters, "store_id": str(store_id)},
                order="updated_at.desc",
                limit=1,
            )
            if isinstance(rows, list) and rows:
                return rows[0]

        rows = await self.db.select(
            "agent_configs",
            filters=filters,
            order="updated_at.desc",
            limit=1,
        )
        if isinstance(rows, list) and rows:
            return rows[0]
        return None

    async def _fetch_products(self, *, tenant_id: UUID, store_id: UUID | None) -> list[dict]:
        filters = {"tenant_id": str(tenant_id)}
        if store_id:
            filters["store_id"] = str(store_id)
        rows = await self.db.select(
            "products",
            columns="shopify_product_id,title,handle,price,currency_code,metadata",
            filters=filters,
            limit=8,
            order="updated_at.desc",
        )
        return rows if isinstance(rows, list) else []

    async def _fetch_policies(self, *, tenant_id: UUID, store_id: UUID | None) -> list[dict]:
        filters = {"tenant_id": str(tenant_id)}
        if store_id:
            filters["store_id"] = str(store_id)
        rows = await self.db.select(
            "policies",
            columns="policy_type,title,body,url",
            filters=filters,
            order="updated_at.desc",
        )
        return rows if isinstance(rows, list) else []

    def _build_assistant_row(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None,
        assistant_config_id: UUID,
        config: AssistantConfigPayload,
    ) -> dict:
        return {
            "id": str(assistant_config_id),
            "tenant_id": str(tenant_id),
            "store_id": str(store_id) if store_id else None,
            "name": "storefront-default",
            "tone": config.tone,
            "system_prompt": config.system_prompt,
            "voice_enabled": config.voice_enabled,
            "sales_mode_enabled": config.sales_mode_enabled,
            "support_mode_enabled": config.support_mode_enabled,
            "config": {
                "assistant_name": config.assistant_name,
                "welcome_message": config.welcome_message,
                "do_agent_id": config.do_agent_id,
                "theme_color": config.theme_color,
            },
        }

    def _row_to_assistant_config(self, row: dict) -> AssistantConfigResponse:
        config = row.get("config") or {}
        return AssistantConfigResponse(
            id=UUID(row["id"]) if row.get("id") else None,
            tenant_id=UUID(row["tenant_id"]),
            store_id=UUID(row["store_id"]) if row.get("store_id") else None,
            assistant_name=config.get("assistant_name", "OmniNew assistant"),
            tone=row.get("tone", "balanced"),
            system_prompt=row.get("system_prompt"),
            welcome_message=config.get(
                "welcome_message",
                "Hi! I can recommend products, answer policy questions, and help capture leads for premium items.",
            ),
            voice_enabled=bool(row.get("voice_enabled", True)),
            sales_mode_enabled=bool(row.get("sales_mode_enabled", True)),
            support_mode_enabled=bool(row.get("support_mode_enabled", True)),
            do_agent_id=config.get("do_agent_id"),
            theme_color=config.get("theme_color"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def _default_assistant_config(self, *, tenant_id: UUID, store_id: UUID | None) -> AssistantConfigResponse:
        return AssistantConfigResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            assistant_name="OmniNew assistant",
            tone="balanced",
            system_prompt=None,
            welcome_message="Hi! I can recommend products, answer policy questions, and help capture leads for premium items.",
            voice_enabled=True,
            sales_mode_enabled=True,
            support_mode_enabled=True,
            do_agent_id=None,
            theme_color=None,
        )

    def _build_slug(self, business_name: str, shop_domain: str) -> str:
        source = business_name.strip() or shop_domain.split(".")[0]
        normalized = re.sub(r"[^a-z0-9]+", "-", source.lower()).strip("-")
        normalized = normalized or "merchant"
        return f"{normalized}-{secrets.token_hex(3)}"

    def _generate_widget_key(self) -> str:
        return f"omn_{secrets.token_urlsafe(18)}"
