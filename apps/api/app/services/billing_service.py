from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

from app.core.config import get_settings
from app.core.database import SupabaseGateway
from app.schemas.common import (
    BillingOverviewResponse,
    ShopifyBillingCheckoutResponse,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
    UsageMetricSummary,
)
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService


class BillingService:
    DEFAULT_PLANS: dict[str, dict[str, Any]] = {
        "starter": {
            "name": "Starter",
            "monthly_price_cents": 0,
            "currency_code": "USD",
            "limits": {"chat_messages": 300, "voice_sessions": 25, "sync_runs": 10},
        },
        "growth": {
            "name": "Growth",
            "monthly_price_cents": 9900,
            "currency_code": "USD",
            "limits": {"chat_messages": 3000, "voice_sessions": 250, "sync_runs": 100},
        },
        "scale": {
            "name": "Scale",
            "monthly_price_cents": 29900,
            "currency_code": "USD",
            "limits": {"chat_messages": None, "voice_sessions": None, "sync_runs": None},
        },
    }

    def __init__(self, db: SupabaseGateway, tenant_service: TenantService, shopify_service: ShopifyService) -> None:
        self.db = db
        self.tenant_service = tenant_service
        self.shopify_service = shopify_service
        self.settings = get_settings()

    async def list_plans(self) -> list[SubscriptionPlanResponse]:
        rows = await self.db.select("subscription_plans", order="monthly_price_cents.asc")
        if isinstance(rows, list) and rows:
            return [self._plan_from_row(row) for row in rows]
        return [self._default_plan_response(code) for code in self.DEFAULT_PLANS]

    async def get_billing_overview(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None = None,
    ) -> BillingOverviewResponse:
        subscription = await self.get_or_create_subscription(tenant_id)
        usage = await self.get_usage_summary(
            tenant_id=tenant_id,
            store_id=store_id,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            limits=subscription.limits,
        )
        return BillingOverviewResponse(
            tenant_id=tenant_id,
            store_id=store_id,
            subscription=subscription,
            usage=usage,
        )

    async def get_or_create_subscription(self, tenant_id: UUID) -> TenantSubscriptionResponse:
        row = await self.db.select(
            "tenant_subscriptions",
            filters={"tenant_id": str(tenant_id)},
            order="created_at.desc",
            limit=1,
            single=True,
        )
        if row:
            return await self._subscription_from_row(row, tenant_id)

        fallback = self._default_subscription_response(tenant_id, "starter")
        plan_row = await self.db.select(
            "subscription_plans",
            filters={"code": "starter"},
            limit=1,
            order="created_at.asc",
            single=True,
        )
        if plan_row:
            payload = {
                "tenant_id": str(tenant_id),
                "plan_id": plan_row["id"],
                "status": "trialing",
                "billing_provider": "manual",
                "current_period_start": fallback.current_period_start.isoformat(),
                "current_period_end": fallback.current_period_end.isoformat() if fallback.current_period_end else None,
                "cancel_at_period_end": False,
                "metadata": {"origin": "auto_default_subscription"},
            }
            stored = await self.db.insert("tenant_subscriptions", payload)
            if stored:
                return await self._subscription_from_row(stored, tenant_id)

        return fallback

    async def update_plan(self, tenant_id: UUID, plan_code: str) -> TenantSubscriptionResponse:
        normalized_plan = plan_code.strip().lower()
        if normalized_plan not in self.DEFAULT_PLANS:
            raise ValueError(f"Unknown billing plan '{plan_code}'.")

        now = datetime.now(UTC)
        period_end = now + timedelta(days=30)
        existing = await self.db.select(
            "tenant_subscriptions",
            filters={"tenant_id": str(tenant_id)},
            order="created_at.desc",
            limit=1,
            single=True,
        )
        plan_row = await self.db.select(
            "subscription_plans",
            filters={"code": normalized_plan},
            limit=1,
            order="created_at.asc",
            single=True,
        )

        if existing and plan_row:
            stored = await self.db.update(
                "tenant_subscriptions",
                {
                    "plan_id": plan_row["id"],
                    "status": "active",
                    "billing_provider": "manual",
                    "current_period_start": now.isoformat(),
                    "current_period_end": period_end.isoformat(),
                    "cancel_at_period_end": False,
                    "metadata": {**(existing.get("metadata") or {}), "updated_plan_code": normalized_plan},
                },
                filters={"id": existing["id"]},
            )
            if isinstance(stored, list):
                stored = stored[0]
            if stored:
                return await self._subscription_from_row(stored, tenant_id)

        if plan_row:
            stored = await self.db.insert(
                "tenant_subscriptions",
                {
                    "tenant_id": str(tenant_id),
                    "plan_id": plan_row["id"],
                    "status": "active",
                    "billing_provider": "manual",
                    "current_period_start": now.isoformat(),
                    "current_period_end": period_end.isoformat(),
                    "cancel_at_period_end": False,
                    "metadata": {"updated_plan_code": normalized_plan},
                },
            )
            if stored:
                return await self._subscription_from_row(stored, tenant_id)

        return self._default_subscription_response(tenant_id, normalized_plan, status="active")

    async def create_shopify_checkout(
        self,
        *,
        tenant_id: UUID,
        plan_code: str,
        store_id: UUID | None = None,
        return_path: str = "/dashboard/connect",
    ) -> ShopifyBillingCheckoutResponse:
        normalized_plan = plan_code.strip().lower()
        if normalized_plan not in self.DEFAULT_PLANS:
            raise ValueError(f"Unknown billing plan '{plan_code}'.")

        store = await self.tenant_service.get_store(tenant_id=tenant_id, store_id=store_id)
        if not store:
            raise ValueError("A connected Shopify store is required before starting app billing.")

        resolved_store_id = UUID(store["id"])
        shop_domain = store.get("shop_domain")
        admin_token = await self.tenant_service.get_admin_token(tenant_id=tenant_id, store_id=resolved_store_id)
        if not shop_domain or not admin_token:
            raise ValueError("Stored Shopify admin credentials are incomplete for this store.")

        if normalized_plan == "starter":
            subscription = await self.update_plan(tenant_id, normalized_plan)
            return ShopifyBillingCheckoutResponse(
                tenant_id=tenant_id,
                store_id=resolved_store_id,
                plan_code=normalized_plan,
                status=subscription.status,
                requires_confirmation=False,
                confirmation_url=None,
                redirect_url=f"{self.settings.app_url.rstrip('/')}{self._sanitize_return_path(return_path)}?billing=free-plan",
                subscription_id=subscription.external_subscription_id,
                test_mode=self.settings.shopify_billing_test_mode,
            )

        active_subscriptions = await self.shopify_service.get_active_app_subscriptions(shop_domain, admin_token)
        current_active = self._find_subscription_for_plan(active_subscriptions, normalized_plan)
        if current_active:
            synced = await self._sync_subscription_record(
                tenant_id=tenant_id,
                store_id=resolved_store_id,
                plan_code=normalized_plan,
                subscription=current_active,
                shop_domain=shop_domain,
            )
            return ShopifyBillingCheckoutResponse(
                tenant_id=tenant_id,
                store_id=resolved_store_id,
                plan_code=normalized_plan,
                status=synced.status,
                requires_confirmation=False,
                confirmation_url=None,
                redirect_url=f"{self.settings.app_url.rstrip('/')}{self._sanitize_return_path(return_path)}?billing=already-active&planCode={normalized_plan}",
                subscription_id=synced.external_subscription_id,
                test_mode=bool(current_active.get("test")),
            )

        plan = self.DEFAULT_PLANS[normalized_plan]
        return_url = self._build_callback_url(
            tenant_id=tenant_id,
            store_id=resolved_store_id,
            plan_code=normalized_plan,
            return_path=return_path,
        )
        result = await self.shopify_service.create_app_subscription(
            shop_domain,
            admin_token,
            name=plan["name"],
            price_amount=plan["monthly_price_cents"] / 100,
            currency_code=plan["currency_code"],
            return_url=return_url,
            test=self.settings.shopify_billing_test_mode,
        )
        subscription = result.get("appSubscription") or {}
        plan_row = await self.db.select(
            "subscription_plans",
            filters={"code": normalized_plan},
            limit=1,
            order="created_at.asc",
            single=True,
        )
        await self._upsert_subscription_record(
            tenant_id=tenant_id,
            plan_row=plan_row,
            status=(subscription.get("status") or "PENDING").lower(),
            billing_provider="shopify",
            current_period_start=datetime.now(UTC),
            current_period_end=None,
            external_subscription_id=subscription.get("id"),
            metadata={
                "updated_plan_code": normalized_plan,
                "shop_domain": shop_domain,
                "store_id": str(resolved_store_id),
                "confirmation_url": result.get("confirmationUrl"),
                "test": self.settings.shopify_billing_test_mode,
            },
        )
        return ShopifyBillingCheckoutResponse(
            tenant_id=tenant_id,
            store_id=resolved_store_id,
            plan_code=normalized_plan,
            status=(subscription.get("status") or "PENDING").lower(),
            requires_confirmation=True,
            confirmation_url=result.get("confirmationUrl"),
            redirect_url=result.get("confirmationUrl") or return_url,
            subscription_id=subscription.get("id"),
            test_mode=self.settings.shopify_billing_test_mode,
        )

    async def complete_shopify_checkout(self, query_params: dict[str, str]) -> str:
        self._verify_shopify_hmac(query_params)
        tenant_id = query_params.get("tenant_id")
        if not tenant_id:
            raise ValueError("Missing tenant identifier in Shopify billing callback.")
        plan_code = query_params.get("plan_code")
        if not plan_code:
            raise ValueError("Missing billing plan code in Shopify billing callback.")

        subscription = await self.sync_shopify_subscription(
            tenant_id=UUID(tenant_id),
            store_id=UUID(query_params["store_id"]) if query_params.get("store_id") else None,
            expected_plan_code=plan_code,
        )
        return_path = self._sanitize_return_path(query_params.get("return_path") or "/dashboard/connect")
        redirect_query = urlencode(
            {
                "billing": "success",
                "planCode": subscription.plan_code,
                "tenantId": str(subscription.tenant_id),
                "subscriptionStatus": subscription.status,
            }
        )
        return f"{self.settings.app_url.rstrip('/')}{return_path}?{redirect_query}"

    async def sync_shopify_subscription(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None = None,
        expected_plan_code: str | None = None,
    ) -> TenantSubscriptionResponse:
        store = await self.tenant_service.get_store(tenant_id=tenant_id, store_id=store_id)
        if not store:
            raise ValueError("Unable to resolve the Shopify store for this tenant.")

        resolved_store_id = UUID(store["id"])
        shop_domain = store.get("shop_domain")
        admin_token = await self.tenant_service.get_admin_token(tenant_id=tenant_id, store_id=resolved_store_id)
        if not shop_domain or not admin_token:
            raise ValueError("Stored Shopify admin credentials are incomplete for this store.")

        active_subscriptions = await self.shopify_service.get_active_app_subscriptions(shop_domain, admin_token)
        if not active_subscriptions:
            raise ValueError("No active Shopify app subscription was found for this installation.")

        subscription = self._find_subscription_for_plan(active_subscriptions, expected_plan_code)
        if not subscription:
            subscription = sorted(
                active_subscriptions,
                key=lambda item: item.get("createdAt") or "",
                reverse=True,
            )[0]

        plan_code = self._plan_code_from_subscription(subscription)
        return await self._sync_subscription_record(
            tenant_id=tenant_id,
            store_id=resolved_store_id,
            plan_code=plan_code,
            subscription=subscription,
            shop_domain=shop_domain,
        )

    async def enforce_allowance(self, *, tenant_id: UUID, metric_type: str, quantity: int = 1) -> None:
        subscription = await self.get_or_create_subscription(tenant_id)
        limit_value = subscription.limits.get(metric_type)
        if limit_value is None:
            return

        usage = await self.get_usage_summary(
            tenant_id=tenant_id,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            limits=subscription.limits,
        )
        current = next((item.quantity for item in usage if item.metric_type == metric_type), 0)
        if current + quantity > limit_value:
            raise ValueError(
                f"Plan limit reached for {metric_type.replace('_', ' ')}. Upgrade the tenant plan to continue."
            )

    async def record_usage(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None,
        session_id: UUID | None,
        metric_type: str,
        quantity: int = 1,
        source: str = "app",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "tenant_id": str(tenant_id),
            "store_id": str(store_id) if store_id else None,
            "session_id": str(session_id) if session_id else None,
            "metric_type": metric_type,
            "quantity": quantity,
            "source": source,
            "metadata": metadata or {},
        }
        return await self.db.insert("usage_events", payload)

    async def get_usage_summary(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID | None = None,
        current_period_start: datetime | None = None,
        current_period_end: datetime | None = None,
        limits: dict[str, int | None] | None = None,
    ) -> list[UsageMetricSummary]:
        start = current_period_start or (datetime.now(UTC) - timedelta(days=30))
        end = current_period_end
        rows = await self.db.select(
            "usage_events",
            filters={"tenant_id": str(tenant_id), "created_at": ("gte", start.isoformat())},
            order="created_at.asc",
            limit=5000,
        )
        totals: dict[str, int] = {}
        if isinstance(rows, list):
            for row in rows:
                if store_id and row.get("store_id") not in {None, str(store_id)}:
                    continue
                created_at = self._coerce_datetime(row.get("created_at"))
                if end and created_at and created_at > end:
                    continue
                metric_type = row.get("metric_type") or "unknown"
                totals[metric_type] = totals.get(metric_type, 0) + int(row.get("quantity") or 0)

        effective_limits = limits or self.DEFAULT_PLANS["starter"]["limits"]
        metric_types = set(effective_limits.keys()) | set(totals.keys())
        return [
            UsageMetricSummary(
                metric_type=metric_type,
                quantity=totals.get(metric_type, 0),
                limit=effective_limits.get(metric_type),
                remaining=None
                if effective_limits.get(metric_type) is None
                else max(effective_limits.get(metric_type, 0) - totals.get(metric_type, 0), 0),
            )
            for metric_type in sorted(metric_types)
        ]

    async def _subscription_from_row(self, row: dict[str, Any], tenant_id: UUID) -> TenantSubscriptionResponse:
        plan = await self._get_plan_for_subscription_row(row)
        metadata = row.get("metadata") or {}
        return TenantSubscriptionResponse(
            id=self._uuid_or_none(row.get("id")),
            tenant_id=tenant_id,
            status=row.get("status") or "trialing",
            billing_provider=row.get("billing_provider") or "manual",
            plan_code=plan.code,
            plan_name=plan.name,
            monthly_price_cents=plan.monthly_price_cents,
            currency_code=plan.currency_code,
            limits=plan.limits,
            current_period_start=self._coerce_datetime(row.get("current_period_start")) or datetime.now(UTC),
            current_period_end=self._coerce_datetime(row.get("current_period_end")),
            cancel_at_period_end=bool(row.get("cancel_at_period_end", False)),
            external_subscription_id=row.get("external_subscription_id"),
            is_test=bool(metadata.get("test", False)),
            created_at=self._coerce_datetime(row.get("created_at")),
            updated_at=self._coerce_datetime(row.get("updated_at")),
        )

    async def _get_plan_for_subscription_row(self, row: dict[str, Any]) -> SubscriptionPlanResponse:
        plan_id = row.get("plan_id")
        if plan_id:
            plan_row = await self.db.select("subscription_plans", filters={"id": plan_id}, single=True)
            if plan_row:
                return self._plan_from_row(plan_row)

        metadata = row.get("metadata") or {}
        updated_code = metadata.get("updated_plan_code")
        if updated_code in self.DEFAULT_PLANS:
            return self._default_plan_response(updated_code)
        return self._default_plan_response("starter")

    def _plan_from_row(self, row: dict[str, Any]) -> SubscriptionPlanResponse:
        return SubscriptionPlanResponse(
            id=self._uuid_or_none(row.get("id")),
            code=row.get("code") or "starter",
            name=row.get("name") or "Starter",
            monthly_price_cents=int(row.get("monthly_price_cents") or 0),
            currency_code=row.get("currency_code") or "USD",
            limits=row.get("limits") or {},
            is_active=bool(row.get("is_active", True)),
            created_at=self._coerce_datetime(row.get("created_at")),
            updated_at=self._coerce_datetime(row.get("updated_at")),
        )

    def _default_plan_response(self, code: str) -> SubscriptionPlanResponse:
        plan = self.DEFAULT_PLANS[code]
        return SubscriptionPlanResponse(
            code=code,
            name=plan["name"],
            monthly_price_cents=plan["monthly_price_cents"],
            currency_code=plan["currency_code"],
            limits=plan["limits"],
            is_active=True,
        )

    def _default_subscription_response(
        self,
        tenant_id: UUID,
        plan_code: str,
        *,
        status: str = "trialing",
    ) -> TenantSubscriptionResponse:
        now = datetime.now(UTC)
        period_end = now + timedelta(days=30)
        plan = self.DEFAULT_PLANS[plan_code]
        return TenantSubscriptionResponse(
            tenant_id=tenant_id,
            status=status,
            billing_provider="manual",
            plan_code=plan_code,
            plan_name=plan["name"],
            monthly_price_cents=plan["monthly_price_cents"],
            currency_code=plan["currency_code"],
            limits=plan["limits"],
            current_period_start=now,
            current_period_end=period_end,
            cancel_at_period_end=False,
            external_subscription_id=None,
            is_test=False,
        )

    async def _sync_subscription_record(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        plan_code: str,
        subscription: dict[str, Any],
        shop_domain: str,
    ) -> TenantSubscriptionResponse:
        plan_row = await self.db.select(
            "subscription_plans",
            filters={"code": plan_code},
            limit=1,
            order="created_at.asc",
            single=True,
        )
        stored = await self._upsert_subscription_record(
            tenant_id=tenant_id,
            plan_row=plan_row,
            status=(subscription.get("status") or "ACTIVE").lower(),
            billing_provider="shopify",
            current_period_start=self._coerce_datetime(subscription.get("createdAt")) or datetime.now(UTC),
            current_period_end=self._coerce_datetime(subscription.get("currentPeriodEnd")),
            external_subscription_id=subscription.get("id"),
            metadata={
                "updated_plan_code": plan_code,
                "shop_domain": shop_domain,
                "store_id": str(store_id),
                "test": bool(subscription.get("test", False)),
                "name": subscription.get("name"),
            },
        )
        return await self._subscription_from_row(stored, tenant_id)

    async def _upsert_subscription_record(
        self,
        *,
        tenant_id: UUID,
        plan_row: dict[str, Any] | None,
        status: str,
        billing_provider: str,
        current_period_start: datetime,
        current_period_end: datetime | None,
        external_subscription_id: str | None,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        existing = await self.db.select(
            "tenant_subscriptions",
            filters={"tenant_id": str(tenant_id)},
            order="created_at.desc",
            limit=1,
            single=True,
        )
        payload = {
            "tenant_id": str(tenant_id),
            "plan_id": plan_row.get("id") if plan_row else None,
            "status": status,
            "billing_provider": billing_provider,
            "external_subscription_id": external_subscription_id,
            "current_period_start": current_period_start.isoformat(),
            "current_period_end": current_period_end.isoformat() if current_period_end else None,
            "cancel_at_period_end": False,
            "metadata": metadata,
        }
        if existing and existing.get("id"):
            updated = await self.db.update("tenant_subscriptions", payload, filters={"id": existing["id"]})
            if isinstance(updated, list):
                updated = updated[0]
            return updated or payload
        inserted = await self.db.insert("tenant_subscriptions", payload)
        return inserted or payload

    def _plan_code_from_subscription(self, subscription: dict[str, Any]) -> str:
        name = (subscription.get("name") or "").strip().lower()
        for code, plan in self.DEFAULT_PLANS.items():
            if plan["name"].lower() == name:
                return code
        return "starter"

    def _find_subscription_for_plan(
        self,
        subscriptions: list[dict[str, Any]],
        plan_code: str | None,
    ) -> dict[str, Any] | None:
        if not subscriptions:
            return None
        if plan_code:
            for subscription in subscriptions:
                if self._plan_code_from_subscription(subscription) == plan_code:
                    return subscription
        return None

    def _build_callback_url(
        self,
        *,
        tenant_id: UUID,
        store_id: UUID,
        plan_code: str,
        return_path: str,
    ) -> str:
        query = urlencode(
            {
                "tenant_id": str(tenant_id),
                "store_id": str(store_id),
                "plan_code": plan_code,
                "return_path": self._sanitize_return_path(return_path),
            }
        )
        return f"{self.settings.api_public_url.rstrip('/')}{self.settings.api_v1_prefix}/billing/shopify/callback?{query}"

    def _sanitize_return_path(self, return_path: str) -> str:
        if not return_path.startswith("/"):
            return "/dashboard/connect"
        if return_path.startswith("//"):
            return "/dashboard/connect"
        return return_path if return_path.startswith("/dashboard") else "/dashboard/connect"

    def _verify_shopify_hmac(self, query_params: dict[str, str]) -> None:
        import hashlib
        import hmac

        hmac_value = query_params.get("hmac")
        if not hmac_value:
            raise ValueError("Missing Shopify callback signature.")
        filtered = {key: value for key, value in query_params.items() if key not in {"hmac", "signature"}}
        message = "&".join(f"{key}={filtered[key]}" for key in sorted(filtered))
        digest = hmac.new(
            self.settings.shopify_app_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(digest, hmac_value):
            raise ValueError("Invalid Shopify billing callback signature.")

    def _uuid_or_none(self, value: Any) -> UUID | None:
        if not value:
            return None
        return UUID(str(value))

    def _coerce_datetime(self, value: Any) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None