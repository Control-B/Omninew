from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.database import SupabaseGateway
from app.schemas.common import TranscriptRecord


class TranscriptService:
    def __init__(self, db: SupabaseGateway) -> None:
        self.db = db

    async def store_transcript(self, payload: TranscriptRecord) -> dict[str, Any]:
        return await self.db.insert("transcripts", payload.model_dump(mode="json"))

    async def store_message(
        self,
        *,
        tenant_id: UUID,
        session_id: UUID | None,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self.db.insert(
            "messages",
            {
                "tenant_id": str(tenant_id),
                "session_id": str(session_id) if session_id else None,
                "role": role,
                "content": content,
                "metadata": metadata or {},
            },
        )
