from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings


class BaseTextAgentProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        *,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict[str, str]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError


class DOTextAgentProvider(BaseTextAgentProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(
            self.settings.do_ai_agent_base_url
            and self.settings.do_ai_agent_key
            and self.settings.do_ai_agent_id
        )

    async def generate_response(
        self,
        *,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict[str, str]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.is_configured:
            return {
                "reply": "I can help with products, policies, and support questions once the DigitalOcean AI agent is configured.",
                "suggestions": [],
                "lead_capture_detected": False,
                "metadata": {"provider": "do", "configured": False},
            }

        payload = {
            "agent_id": self.settings.do_ai_agent_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message},
            ],
            "context": context,
            "temperature": self.settings.default_model_temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.do_ai_agent_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{self.settings.do_ai_agent_base_url.rstrip('/')}/responses",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return {
            "reply": data.get("output_text") or data.get("reply") or "How can I help further?",
            "suggestions": data.get("suggestions", []),
            "lead_capture_detected": bool(data.get("lead_capture_detected", False)),
            "metadata": {"provider": "do", "raw": data},
        }
