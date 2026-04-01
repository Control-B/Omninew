from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class SupabaseGateway:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.supabase_url.rstrip("/")
        self.service_role_key = settings.supabase_service_role_key
        self.anon_key = settings.supabase_anon_key

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and (self.service_role_key or self.anon_key))

    def _headers(self, use_service_role: bool = True) -> dict[str, str]:
        token = self.service_role_key if use_service_role else self.anon_key
        return {
            "apikey": token,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured:
            return {"table": table, "payload": payload, "persisted": False}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/{table}",
                headers={**self._headers(), "Prefer": "return=representation"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) and data else {"persisted": True}

    async def upsert_many(self, table: str, payload: list[dict[str, Any]], on_conflict: str) -> list[dict[str, Any]]:
        if not payload:
            return []
        if not self.is_configured:
            return payload

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/{table}?on_conflict={on_conflict}",
                headers={**self._headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []


def get_supabase_gateway() -> SupabaseGateway:
    return SupabaseGateway()
