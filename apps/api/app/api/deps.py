from app.agents.providers import BaseTextAgentProvider, DOTextAgentProvider
from app.core.database import SupabaseGateway, get_supabase_gateway
from app.services.conversation_service import ConversationService
from app.services.agent_tool_service import AgentToolService
from app.services.billing_service import BillingService
from app.services.lead_service import LeadService
from app.services.livekit_service import LiveKitService
from app.services.policy_sync_service import PolicySyncService
from app.services.product_sync_service import ProductSyncService
from app.services.shopify_auth_service import ShopifyAuthService
from app.services.shopify_service import ShopifyService
from app.services.tenant_service import TenantService
from app.services.transcript_service import TranscriptService


def get_text_agent_provider() -> BaseTextAgentProvider:
    return DOTextAgentProvider()


def get_shopify_service() -> ShopifyService:
    return ShopifyService()


def get_tenant_service() -> TenantService:
    return TenantService(get_supabase_gateway(), get_shopify_service())


def get_shopify_auth_service() -> ShopifyAuthService:
    return ShopifyAuthService(get_shopify_service(), get_tenant_service())


def get_billing_service() -> BillingService:
    return BillingService(
        get_supabase_gateway(),
        get_tenant_service(),
        get_shopify_service(),
    )


def get_product_sync_service() -> ProductSyncService:
    return ProductSyncService(get_shopify_service(), get_supabase_gateway())


def get_policy_sync_service() -> PolicySyncService:
    return PolicySyncService(get_shopify_service(), get_supabase_gateway())


def get_livekit_service() -> LiveKitService:
    return LiveKitService()


def get_transcript_service() -> TranscriptService:
    return TranscriptService(get_supabase_gateway())


def get_lead_service() -> LeadService:
    return LeadService(get_supabase_gateway())


def get_agent_tool_service() -> AgentToolService:
    return AgentToolService(
        get_supabase_gateway(),
        get_tenant_service(),
        get_lead_service(),
        get_shopify_service(),
    )


def get_conversation_service() -> ConversationService:
    return ConversationService(
        shopify_service=get_shopify_service(),
        text_agent_provider=get_text_agent_provider(),
        transcript_service=get_transcript_service(),
        lead_service=get_lead_service(),
        tenant_service=get_tenant_service(),
        billing_service=get_billing_service(),
    )


def get_database_gateway() -> SupabaseGateway:
    return get_supabase_gateway()
