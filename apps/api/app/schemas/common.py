from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TimestampedResponse(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TenantScopedModel(BaseModel):
    tenant_id: UUID | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str = "0.1.0"


class ShopifyConnectRequest(BaseModel):
    tenant_id: UUID
    shop_domain: str
    admin_access_token: str
    storefront_access_token: str | None = None


class ShopifySyncRequest(BaseModel):
    tenant_id: UUID
    store_id: UUID
    shop_domain: str | None = None
    admin_access_token: str | None = None
    include_products: bool = True
    include_collections: bool = True
    include_policies: bool = True


class ProductSearchRequest(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    shop_domain: str
    storefront_access_token: str
    query: str = Field(min_length=2)
    limit: int = Field(default=8, ge=1, le=20)


class ProductDetailsRequest(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    shop_domain: str
    storefront_access_token: str
    product_id: str


class ProductRecommendationRequest(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    shop_domain: str
    storefront_access_token: str
    context: str = Field(min_length=2)
    limit: int = Field(default=4, ge=1, le=12)


class ChatMessageInput(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    session_id: UUID | None = None
    customer_name: str | None = None
    customer_email: EmailStr | None = None
    message: str
    history: list[ChatMessageInput] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductSuggestion(BaseModel):
    product_id: str
    title: str
    handle: str | None = None
    price: str | None = None
    reason: str | None = None


class LeadCapturePayload(BaseModel):
    tenant_id: UUID
    session_id: UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    intent: str
    product_interest: str | None = None
    notes: str | None = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[ProductSuggestion] = Field(default_factory=list)
    lead_capture_detected: bool = False
    session_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoiceTokenRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    session_id: UUID | None = None
    identity: str
    room_name: str | None = None
    can_publish: bool = True
    can_subscribe: bool = True


class VoiceTokenResponse(BaseModel):
    token: str
    ws_url: str
    room_name: str


class AssistantConfigPayload(BaseModel):
    assistant_name: str = "OmniNew assistant"
    tone: Literal["sales", "balanced", "support"] = "balanced"
    system_prompt: str | None = None
    welcome_message: str = "Hi! I can recommend products, answer policy questions, and help capture leads for premium items."
    voice_enabled: bool = True
    sales_mode_enabled: bool = True
    support_mode_enabled: bool = True
    do_agent_id: str | None = None
    theme_color: str | None = None


class AssistantConfigRequest(AssistantConfigPayload):
    tenant_id: UUID
    store_id: UUID | None = None


class AssistantConfigResponse(TimestampedResponse, AssistantConfigPayload):
    id: UUID | None = None
    tenant_id: UUID
    store_id: UUID | None = None


class WidgetPublicConfigResponse(BaseModel):
    widget_key: str
    tenant_id: UUID
    store_id: UUID | None = None
    assistant_name: str
    welcome_message: str
    voice_enabled: bool = True
    theme_color: str | None = None
    store_name: str | None = None
    support_email: str | None = None


class TenantBootstrapRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=120)
    owner_email: EmailStr
    shop_domain: str
    admin_access_token: str
    storefront_access_token: str | None = None
    assistant_name: str = "OmniNew assistant"
    tone: Literal["sales", "balanced", "support"] = "balanced"
    welcome_message: str = "Hi! I can recommend products, answer policy questions, and help capture leads for premium items."
    voice_enabled: bool = True


class TenantBootstrapResponse(BaseModel):
    tenant_id: UUID
    store_id: UUID
    widget_key: str
    business_name: str
    shop_domain: str
    store_name: str | None = None
    assistant_name: str
    tone: Literal["sales", "balanced", "support"]
    welcome_message: str


class TranscriptRecord(BaseModel):
    tenant_id: UUID
    session_id: UUID
    transcript: str
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeadRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID
    session_id: UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    intent: str
    product_interest: str | None = None
    notes: str | None = None
