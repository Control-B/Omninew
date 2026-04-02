from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Omniweb Shopify AI API"
    environment: Literal["local", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    app_url: str = "http://localhost:3000"
    api_public_url: str = "http://localhost:8000"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    shopify_app_key: str = ""
    shopify_app_secret: str = ""
    shopify_app_scopes: str = (
        "read_products,read_content,read_orders,read_customers,"
        "write_content,write_script_tags,unauthenticated_read_product_listings"
    )
    shopify_webhook_secret: str = ""
    shopify_billing_test_mode: bool = True

    do_ai_agent_base_url: str = ""
    do_ai_agent_key: str = ""
    do_ai_agent_id: str = ""
    do_agent_route_secret: str = ""

    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    livekit_ws_url: str = ""

    default_model_temperature: float = 0.2
    default_recommendation_limit: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
