from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from app.core.config import get_settings
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService


@dataclass
class OAuthCallbackResult:
    tenant_id: str
    store_id: str
    widget_key: str
    business_name: str
    shop_domain: str
    store_name: str | None
    assistant_name: str
    tone: str
    welcome_message: str


class ShopifyAuthService:
    def __init__(self, shopify_service: ShopifyService, tenant_service: TenantService) -> None:
        self.shopify_service = shopify_service
        self.tenant_service = tenant_service
        self.settings = get_settings()

    def build_install_url(
        self,
        *,
        shop_domain: str,
        business_name: str,
        owner_email: str,
        assistant_name: str,
        tone: str,
        welcome_message: str,
        voice_enabled: bool,
    ) -> str:
        if not self.settings.shopify_app_key or not self.settings.shopify_app_secret:
            raise ValueError("Shopify app credentials are not configured.")

        callback_uri = self._callback_url()
        state = self._encode_state(
            {
                "shop_domain": shop_domain,
                "business_name": business_name,
                "owner_email": owner_email,
                "assistant_name": assistant_name,
                "tone": tone,
                "welcome_message": welcome_message,
                "voice_enabled": voice_enabled,
                "ts": int(time.time()),
            }
        )
        params = urlencode(
            {
                "client_id": self.settings.shopify_app_key,
                "scope": self.settings.shopify_app_scopes,
                "redirect_uri": callback_uri,
                "state": state,
            }
        )
        return f"https://{shop_domain}/admin/oauth/authorize?{params}"

    async def handle_callback(self, query_params: dict[str, str]) -> OAuthCallbackResult:
        self._verify_shopify_hmac(query_params)
        state = query_params.get("state")
        if not state:
            raise ValueError("Missing OAuth state.")
        state_payload = self._decode_state(state)

        shop_domain = query_params.get("shop") or state_payload["shop_domain"]
        code = query_params.get("code")
        if not code or not shop_domain:
            raise ValueError("Missing Shopify callback parameters.")

        token_response = await self.shopify_service.exchange_oauth_code(shop_domain, code)
        admin_token = token_response.get("access_token")
        if not admin_token:
            raise ValueError("Shopify did not return an access token.")

        storefront_token = None
        try:
            storefront_token = await self.shopify_service.create_storefront_access_token(shop_domain, admin_token)
        except Exception:
            storefront_token = None

        install_result = await self.tenant_service.upsert_shopify_installation(
            business_name=state_payload["business_name"],
            owner_email=state_payload["owner_email"],
            shop_domain=shop_domain,
            admin_access_token=admin_token,
            storefront_access_token=storefront_token,
            assistant_name=state_payload["assistant_name"],
            tone=state_payload["tone"],
            welcome_message=state_payload["welcome_message"],
            voice_enabled=bool(state_payload.get("voice_enabled", True)),
        )

        try:
            await self.shopify_service.register_uninstall_webhook(
                shop_domain,
                admin_token,
                self._uninstall_webhook_url(),
            )
        except Exception:
            pass

        return OAuthCallbackResult(
            tenant_id=str(install_result.tenant_id),
            store_id=str(install_result.store_id),
            widget_key=install_result.widget_key,
            business_name=install_result.business_name,
            shop_domain=install_result.shop_domain,
            store_name=install_result.store_name,
            assistant_name=install_result.assistant_name,
            tone=install_result.tone,
            welcome_message=install_result.welcome_message,
        )

    def _callback_url(self) -> str:
        base = self.settings.api_public_url.rstrip("/")
        return f"{base}{self.settings.api_v1_prefix}/auth/shopify/callback"

    def _uninstall_webhook_url(self) -> str:
        base = self.settings.api_public_url.rstrip("/")
        return f"{base}{self.settings.api_v1_prefix}/webhooks/shopify/app-uninstalled"

    def _encode_state(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
        signature = hmac.new(
            self.settings.shopify_app_secret.encode("utf-8"),
            encoded.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"{encoded}.{signature}"

    def _decode_state(self, value: str) -> dict[str, Any]:
        try:
            encoded, signature = value.rsplit(".", 1)
        except ValueError as error:
            raise ValueError("Invalid OAuth state format.") from error

        expected = hmac.new(
            self.settings.shopify_app_secret.encode("utf-8"),
            encoded.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid OAuth state signature.")

        padded = encoded + "=" * (-len(encoded) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))

    def _verify_shopify_hmac(self, query_params: dict[str, str]) -> None:
        hmac_value = query_params.get("hmac")
        if not hmac_value:
            raise ValueError("Missing Shopify HMAC.")

        filtered = {key: value for key, value in query_params.items() if key != "hmac"}
        message = "&".join(f"{key}={filtered[key]}" for key in sorted(filtered))
        digest = hmac.new(
            self.settings.shopify_app_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(digest, hmac_value):
            raise ValueError("Invalid Shopify callback signature.")