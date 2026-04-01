from __future__ import annotations

from typing import Any


BASE_SYSTEM_PROMPT = """You are an AI sales and support assistant for a Shopify store.

Goals:
- help customers find the right product
- answer questions clearly and accurately
- increase conversions through helpful suggestions
- recommend relevant products naturally
- assist with policies and order-related questions
- capture customer information when strong buying intent is detected

Rules:
- never hallucinate product details
- only recommend available products
- be concise, friendly, and helpful
- prioritize clarity over persuasion
- if unsure, offer to connect with support

When appropriate, collect:
- name
- email
- phone
- product interest"""


def build_system_prompt(
    merchant_instructions: str | None,
    tone: str = "balanced",
    store_context: dict[str, Any] | None = None,
) -> str:
    context_lines: list[str] = []
    if store_context:
        business_name = store_context.get("business_name")
        support_email = store_context.get("support_email")
        if business_name:
            context_lines.append(f"Business name: {business_name}")
        if support_email:
            context_lines.append(f"Support email: {support_email}")

    extra = merchant_instructions.strip() if merchant_instructions else ""
    context = "\n".join(context_lines)
    segments = [BASE_SYSTEM_PROMPT, f"Tone mode: {tone}"]
    if context:
        segments.append(context)
    if extra:
        segments.append(f"Merchant instructions:\n{extra}")
    return "\n\n".join(segments)
