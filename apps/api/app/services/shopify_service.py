from __future__ import annotations

from typing import Any

import httpx


class ShopifyService:
    admin_version = "2025-10"

    async def connect_store(
        self,
        *,
        tenant_id: str,
        shop_domain: str,
        admin_access_token: str,
        storefront_access_token: str | None,
    ) -> dict[str, Any]:
        store_info = await self.get_store_info(shop_domain, admin_access_token)
        return {
            "tenant_id": tenant_id,
            "shop_domain": shop_domain,
            "admin_access_token": admin_access_token,
            "storefront_access_token": storefront_access_token,
            "store_info": store_info,
        }

    async def get_store_info(self, shop_domain: str, admin_access_token: str) -> dict[str, Any]:
        query = {
            "query": "{ shop { name email myshopifyDomain description } }",
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, query)
        return data.get("data", {}).get("shop", {})

    async def fetch_products(self, shop_domain: str, admin_access_token: str, limit: int = 50) -> list[dict[str, Any]]:
        query = {
            "query": """
            query Products($first: Int!) {
              products(first: $first) {
                nodes {
                  id
                  title
                  handle
                  description
                  totalInventory
                  tags
                  featuredImage {
                    url
                    altText
                  }
                  variants(first: 5) {
                    nodes {
                      id
                      title
                      price
                      availableForSale
                    }
                  }
                }
              }
            }
            """,
            "variables": {"first": limit},
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, query)
        return data.get("data", {}).get("products", {}).get("nodes", [])

    async def fetch_collections(self, shop_domain: str, admin_access_token: str, limit: int = 25) -> list[dict[str, Any]]:
        query = {
            "query": """
            query Collections($first: Int!) {
              collections(first: $first) {
                nodes {
                  id
                  title
                  handle
                  description
                }
              }
            }
            """,
            "variables": {"first": limit},
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, query)
        return data.get("data", {}).get("collections", {}).get("nodes", [])

    async def fetch_policies(self, shop_domain: str, admin_access_token: str) -> dict[str, Any]:
        query = {
            "query": """
            {
              shop {
                privacyPolicy { title body url }
                refundPolicy { title body url }
                shippingPolicy { title body url }
                termsOfService { title body url }
              }
            }
            """
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, query)
        return data.get("data", {}).get("shop", {})

    async def search_products(
        self,
        shop_domain: str,
        storefront_access_token: str,
        query_text: str,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        query = {
            "query": """
            query SearchProducts($query: String!, $first: Int!) {
              products(first: $first, query: $query) {
                nodes {
                  id
                  title
                  handle
                  description
                  availableForSale
                  featuredImage {
                    url
                    altText
                  }
                  priceRange {
                    minVariantPrice {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
            """,
            "variables": {"query": query_text, "first": limit},
        }
        data = await self._storefront_graphql(shop_domain, storefront_access_token, query)
        return data.get("data", {}).get("products", {}).get("nodes", [])

    async def get_product_details(
        self,
        shop_domain: str,
        storefront_access_token: str,
        product_id: str,
    ) -> dict[str, Any]:
        query = {
            "query": """
            query ProductDetails($id: ID!) {
              product(id: $id) {
                id
                title
                handle
                description
                availableForSale
                tags
                options {
                  name
                  values
                }
                variants(first: 10) {
                  nodes {
                    id
                    title
                    availableForSale
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
            """,
            "variables": {"id": product_id},
        }
        data = await self._storefront_graphql(shop_domain, storefront_access_token, query)
        return data.get("data", {}).get("product", {})

    async def recommend_products(
        self,
        shop_domain: str,
        storefront_access_token: str,
        context: str,
        limit: int = 4,
    ) -> list[dict[str, Any]]:
        return await self.search_products(
            shop_domain=shop_domain,
            storefront_access_token=storefront_access_token,
            query_text=context,
            limit=limit,
        )

    async def get_store_policies(self, shop_domain: str, admin_access_token: str) -> dict[str, Any]:
        return await self.fetch_policies(shop_domain, admin_access_token)

    async def create_support_request(
        self,
        *,
        tenant_id: str,
        customer_email: str | None,
        message: str,
    ) -> dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "customer_email": customer_email,
            "message": message,
            "status": "queued",
        }

    async def get_business_info(self, shop_domain: str, admin_access_token: str) -> dict[str, Any]:
        return await self.get_store_info(shop_domain, admin_access_token)

    async def _admin_graphql(
        self,
        shop_domain: str,
        admin_access_token: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"https://{shop_domain}/admin/api/{self.admin_version}/graphql.json"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "X-Shopify-Access-Token": admin_access_token,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def _storefront_graphql(
        self,
        shop_domain: str,
        storefront_access_token: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"https://{shop_domain}/api/{self.admin_version}/graphql.json"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "X-Shopify-Storefront-Access-Token": storefront_access_token,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()
