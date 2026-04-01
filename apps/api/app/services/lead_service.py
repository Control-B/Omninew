from __future__ import annotations

from typing import Any

from app.core.database import SupabaseGateway
from app.schemas.common import LeadCapturePayload


class LeadService:
    def __init__(self, db: SupabaseGateway) -> None:
        self.db = db

    async def capture_lead(self, payload: LeadCapturePayload) -> dict[str, Any]:
        lead = payload.model_dump(mode="json")
        lead.setdefault("status", "new")
        return await self.db.insert("leads", lead)
