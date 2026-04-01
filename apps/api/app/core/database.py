from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

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

    def _build_query_params(
        self,
        *,
        filters: dict[str, Any] | None = None,
        columns: str | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> str:
        params: list[tuple[str, str]] = []
        if columns:
            params.append(("select", columns))
        if filters:
            for key, raw_value in filters.items():
                operator = "eq"
                value = raw_value
                if isinstance(raw_value, tuple) and len(raw_value) == 2:
                    operator, value = raw_value
                params.append((key, f"{operator}.{value}"))
        if limit is not None:
            params.append(("limit", str(limit)))
        if order:
            params.append(("order", order))
        return urlencode(params, doseq=True)

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

    async def upsert(self, table: str, payload: dict[str, Any], on_conflict: str) -> dict[str, Any]:
        if not self.is_configured:
            return {"table": table, "payload": payload, "persisted": False, "upserted": True}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/{table}?on_conflict={on_conflict}",
                headers={**self._headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) and data else payload

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

    async def select(
        self,
        table: str,
        *,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        order: str | None = None,
        single: bool = False,
        use_service_role: bool = True,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        if not self.is_configured:
            return None if single else []

        query = self._build_query_params(filters=filters, columns=columns, limit=limit, order=order)
        headers = self._headers(use_service_role=use_service_role)
        if single:
            headers = {**headers, "Accept": "application/vnd.pgrst.object+json"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/rest/v1/{table}?{query}", headers=headers)
            if single and response.status_code == 406:
                return None
            response.raise_for_status()
            return response.json()

    async def update(
        self,
        table: str,
        payload: dict[str, Any],
        *,
        filters: dict[str, Any],
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if not self.is_configured:
            return {"table": table, "payload": payload, "updated": False}

        query = self._build_query_params(filters=filters)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.patch(
                f"{self.base_url}/rest/v1/{table}?{query}",
                headers={**self._headers(), "Prefer": "return=representation"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data[0] if len(data) == 1 else data
            return data

    async def delete(self, table: str, *, filters: dict[str, Any]) -> None:
        if not self.is_configured:
            return

        query = self._build_query_params(filters=filters)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.delete(
                f"{self.base_url}/rest/v1/{table}?{query}",
                headers={**self._headers(), "Prefer": "return=minimal"},
            )
            response.raise_for_status()


def get_supabase_gateway() -> SupabaseGateway:
    return SupabaseGateway()
