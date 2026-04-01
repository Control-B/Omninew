from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


ToolHandler = Callable[..., Awaitable[dict[str, Any] | list[dict[str, Any]]]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        self._tools[name] = handler

    def get(self, name: str) -> ToolHandler:
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())


async def create_shopify_tool_registry(service: Any, lead_service: Any) -> ToolRegistry:
    registry = ToolRegistry()

    registry.register("search_products", service.search_products)
    registry.register("get_product_details", service.get_product_details)
    registry.register("recommend_products", service.recommend_products)
    registry.register("get_store_policies", service.get_store_policies)
    registry.register("capture_lead", lead_service.capture_lead)
    registry.register("create_support_request", service.create_support_request)
    registry.register("get_business_info", service.get_business_info)

    return registry
