from __future__ import annotations

from typing import Any

from app.agents.providers import BaseTextAgentProvider
from app.prompts.system_prompt import build_system_prompt


class DOAgentService:
    def __init__(self, provider: BaseTextAgentProvider) -> None:
        self.provider = provider

    async def respond(
        self,
        *,
        agent_id: str | None,
        merchant_instructions: str | None,
        tone: str,
        user_message: str,
        history: list[dict[str, str]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        system_prompt = build_system_prompt(
            merchant_instructions=merchant_instructions,
            tone=tone,
            store_context=context.get("store_context"),
        )
        return await self.provider.generate_response(
            agent_id=agent_id,
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=history,
            context=context,
        )
