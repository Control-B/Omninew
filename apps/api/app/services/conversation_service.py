from __future__ import annotations

from typing import Any
from uuid import UUID

from app.agents.providers import BaseTextAgentProvider
from app.schemas.common import ChatRequest, LeadCapturePayload, ProductSuggestion, TranscriptRecord
from app.services.do_agent_service import DOAgentService
from app.services.lead_service import LeadService
from app.services.shopify_service import ShopifyService
from app.services.transcript_service import TranscriptService


class ConversationService:
    def __init__(
        self,
        *,
        shopify_service: ShopifyService,
        text_agent_provider: BaseTextAgentProvider,
        transcript_service: TranscriptService,
        lead_service: LeadService,
    ) -> None:
        self.shopify_service = shopify_service
        self.transcript_service = transcript_service
        self.lead_service = lead_service
        self.agent_service = DOAgentService(text_agent_provider)

    async def handle_chat(
        self,
        chat_request: ChatRequest,
        *,
        merchant_instructions: str | None = None,
        tone: str = "balanced",
    ) -> dict[str, Any]:
        history = [message.model_dump() for message in chat_request.history]
        context = {
            "store_context": {
                "business_name": chat_request.metadata.get("business_name"),
                "support_email": chat_request.metadata.get("support_email"),
            },
            "products": chat_request.metadata.get("products", []),
            "policies": chat_request.metadata.get("policies", []),
            "session_metadata": chat_request.metadata,
        }
        agent_response = await self.agent_service.respond(
            merchant_instructions=merchant_instructions,
            tone=tone,
            user_message=chat_request.message,
            history=history,
            context=context,
        )

        await self.transcript_service.store_message(
            tenant_id=chat_request.tenant_id,
            session_id=chat_request.session_id,
            role="user",
            content=chat_request.message,
            metadata=chat_request.metadata,
        )
        await self.transcript_service.store_message(
            tenant_id=chat_request.tenant_id,
            session_id=chat_request.session_id,
            role="assistant",
            content=agent_response["reply"],
            metadata=agent_response.get("metadata", {}),
        )

        lead_capture_detected = agent_response.get("lead_capture_detected", False)
        if lead_capture_detected and (chat_request.customer_email or chat_request.customer_name):
            await self.lead_service.capture_lead(
                LeadCapturePayload(
                    tenant_id=chat_request.tenant_id,
                    session_id=chat_request.session_id,
                    name=chat_request.customer_name,
                    email=chat_request.customer_email,
                    intent="buying_intent_detected",
                    product_interest=chat_request.metadata.get("product_interest"),
                    notes=chat_request.message,
                )
            )

        suggestions = [ProductSuggestion(**item) for item in agent_response.get("suggestions", [])]
        return {
            "reply": agent_response["reply"],
            "suggestions": suggestions,
            "lead_capture_detected": lead_capture_detected,
            "session_id": chat_request.session_id,
            "metadata": agent_response.get("metadata", {}),
        }

    async def store_voice_transcript(
        self,
        *,
        tenant_id: UUID,
        session_id: UUID,
        transcript: str,
        summary: str | None,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return await self.transcript_service.store_transcript(
            TranscriptRecord(
                tenant_id=tenant_id,
                session_id=session_id,
                transcript=transcript,
                summary=summary,
                metadata=metadata,
            )
        )
