from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.agents.providers import BaseTextAgentProvider
from app.schemas.common import ChatRequest, LeadCapturePayload, ProductSuggestion, TranscriptRecord
from app.services.do_agent_service import DOAgentService
from app.services.lead_service import LeadService
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService
from app.services.transcript_service import TranscriptService


class ConversationService:
    def __init__(
        self,
        *,
        shopify_service: ShopifyService,
        text_agent_provider: BaseTextAgentProvider,
        transcript_service: TranscriptService,
        lead_service: LeadService,
        tenant_service: TenantService,
    ) -> None:
        self.shopify_service = shopify_service
        self.transcript_service = transcript_service
        self.lead_service = lead_service
        self.tenant_service = tenant_service
        self.agent_service = DOAgentService(text_agent_provider)

    async def handle_chat(
        self,
        chat_request: ChatRequest,
        *,
        merchant_instructions: str | None = None,
        tone: str = "balanced",
    ) -> dict[str, Any]:
        runtime_context = await self.tenant_service.resolve_runtime_context(
            widget_key=chat_request.widget_key,
            tenant_id=chat_request.tenant_id,
            store_id=chat_request.store_id,
            metadata=chat_request.metadata,
        )
        session_id = chat_request.session_id or uuid4()

        await self.transcript_service.ensure_chat_session(
            tenant_id=runtime_context.tenant_id,
            store_id=runtime_context.store_id,
            session_id=session_id,
            customer_name=chat_request.customer_name,
            customer_email=str(chat_request.customer_email) if chat_request.customer_email else None,
            channel="web_chat",
            metadata={"widget_key": chat_request.widget_key} if chat_request.widget_key else {},
        )

        history = [message.model_dump() for message in chat_request.history]
        context = {
            "store_context": {
                "business_name": runtime_context.store_name or chat_request.metadata.get("business_name"),
                "support_email": runtime_context.support_email or chat_request.metadata.get("support_email"),
                "shop_domain": runtime_context.shop_domain,
            },
            "products": runtime_context.products or chat_request.metadata.get("products", []),
            "policies": runtime_context.policies or chat_request.metadata.get("policies", []),
            "assistant": {
                "name": runtime_context.assistant_name,
                "voice_enabled": runtime_context.voice_enabled,
            },
            "session_metadata": {
                **chat_request.metadata,
                "widget_key": chat_request.widget_key,
            },
        }
        agent_response = await self.agent_service.respond(
            agent_id=runtime_context.do_agent_id,
            merchant_instructions=runtime_context.system_prompt or merchant_instructions,
            tone=runtime_context.tone or tone,
            user_message=chat_request.message,
            history=history,
            context=context,
        )

        await self.transcript_service.store_message(
            tenant_id=runtime_context.tenant_id,
            session_id=session_id,
            role="user",
            content=chat_request.message,
            metadata=chat_request.metadata,
        )
        await self.transcript_service.store_message(
            tenant_id=runtime_context.tenant_id,
            session_id=session_id,
            role="assistant",
            content=agent_response["reply"],
            metadata=agent_response.get("metadata", {}),
        )

        lead_capture_detected = agent_response.get("lead_capture_detected", False)
        if lead_capture_detected and (chat_request.customer_email or chat_request.customer_name):
            await self.lead_service.capture_lead(
                LeadCapturePayload(
                    tenant_id=runtime_context.tenant_id,
                    session_id=session_id,
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
            "session_id": session_id,
            "metadata": {
                **agent_response.get("metadata", {}),
                "assistant_name": runtime_context.assistant_name,
                "voice_enabled": runtime_context.voice_enabled,
            },
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
