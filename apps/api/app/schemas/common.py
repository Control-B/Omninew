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


class ShopifySetupStatusResponse(BaseModel):
    status: Literal["ready", "partial", "missing"]
    app_url: str
    api_public_url: str
    dashboard_connect_url: str
    install_url: str
    callback_url: str
    uninstall_webhook_url: str
    scopes: list[str] = Field(default_factory=list)
    app_key_configured: bool = False
    app_secret_configured: bool = False
    webhook_secret_configured: bool = False
    https_ready: bool = False
    notes: list[str] = Field(default_factory=list)


class SubscriptionPlanResponse(TimestampedResponse):
    id: UUID | None = None
    code: str
    name: str
    monthly_price_cents: int = 0
    currency_code: str = "USD"
    limits: dict[str, int | None] = Field(default_factory=dict)
    is_active: bool = True


class TenantSubscriptionResponse(TimestampedResponse):
    id: UUID | None = None
    tenant_id: UUID
    status: str
    billing_provider: str = "manual"
    plan_code: str
    plan_name: str
    monthly_price_cents: int = 0
    currency_code: str = "USD"
    limits: dict[str, int | None] = Field(default_factory=dict)
    current_period_start: datetime
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
    external_subscription_id: str | None = None
    is_test: bool = False


class UsageMetricSummary(BaseModel):
    metric_type: str
    quantity: int = 0
    limit: int | None = None
    remaining: int | None = None


class BillingOverviewResponse(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    subscription: TenantSubscriptionResponse
    usage: list[UsageMetricSummary] = Field(default_factory=list)


class BillingPlanUpdateRequest(BaseModel):
    tenant_id: UUID
    plan_code: str = Field(min_length=2, max_length=40)


class ShopifyBillingCheckoutRequest(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    plan_code: str = Field(min_length=2, max_length=40)
    return_path: str = "/dashboard/connect"


class ShopifyBillingCheckoutResponse(BaseModel):
    tenant_id: UUID
    store_id: UUID | None = None
    plan_code: str
    status: str
    requires_confirmation: bool = True
    confirmation_url: str | None = None
    redirect_url: str
    subscription_id: str | None = None
    test_mode: bool = False


class AgentBlueprintRoute(BaseModel):
    name: str
    method: str
    path: str
    purpose: str
    headers: dict[str, str] = Field(default_factory=dict)
    body_schema: dict[str, Any] = Field(default_factory=dict)


class AgentBlueprintResponse(BaseModel):
    model: str
    workspace_strategy: str
    knowledge_base_strategy: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    system_prompt: str
    agent_routes: list[AgentBlueprintRoute] = Field(default_factory=list)
    function_routes: list[AgentBlueprintRoute] = Field(default_factory=list)
    env_requirements: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AgentToolProductSearchRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    query: str = Field(min_length=2)
    limit: int = Field(default=6, ge=1, le=12)


class AgentToolPolicyLookupRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    policy_type: Literal["privacy", "refund", "shipping", "terms"] | None = None


class AgentToolLeadCaptureRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    session_id: UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    intent: str = "buying_intent_detected"
    product_interest: str | None = None
    notes: str | None = None


class AgentToolHandoffRequest(BaseModel):
    tenant_id: UUID | None = None
    store_id: UUID | None = None
    widget_key: str | None = None
    customer_email: EmailStr | None = None
    message: str = Field(min_length=3)
    session_id: UUID | None = None


class AgentToolResponse(BaseModel):
    ok: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


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
