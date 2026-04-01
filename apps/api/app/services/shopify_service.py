from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class ShopifyService:
    admin_version = "2025-10"

    def __init__(self) -> None:
        self.settings = get_settings()

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
            "query": "{ shop { name email myshopifyDomain description currencyCode } }",
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, query)
        return data.get("data", {}).get("shop", {})

    async def exchange_oauth_code(self, shop_domain: str, code: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://{shop_domain}/admin/oauth/access_token",
                json={
                    "client_id": self.settings.shopify_app_key,
                    "client_secret": self.settings.shopify_app_secret,
                    "code": code,
                },
            )
            response.raise_for_status()
            return response.json()

    async def create_storefront_access_token(
        self,
        shop_domain: str,
        admin_access_token: str,
        title: str = "OmniNew Storefront Token",
    ) -> str | None:
        payload = {
            "query": """
            mutation CreateStorefrontToken($title: String!) {
              storefrontAccessTokenCreate(input: {title: $title}) {
                storefrontAccessToken {
                  accessToken
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """,
            "variables": {"title": title},
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, payload)
        token_data = data.get("data", {}).get("storefrontAccessTokenCreate", {})
        return token_data.get("storefrontAccessToken", {}).get("accessToken")

    async def register_uninstall_webhook(
        self,
        shop_domain: str,
        admin_access_token: str,
        callback_url: str,
    ) -> dict[str, Any]:
        payload = {
            "query": """
            mutation RegisterWebhook($topic: WebhookSubscriptionTopic!, $callbackUrl: URL!) {
              webhookSubscriptionCreate(
                topic: $topic,
                webhookSubscription: {callbackUrl: $callbackUrl, format: JSON}
              ) {
                webhookSubscription {
                  id
                  endpoint {
                    __typename
                  }
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """,
            "variables": {
                "topic": "APP_UNINSTALLED",
                "callbackUrl": callback_url,
            },
        }
        return await self._admin_graphql(shop_domain, admin_access_token, payload)

    async def create_app_subscription(
        self,
        shop_domain: str,
        admin_access_token: str,
        *,
        name: str,
        price_amount: float,
        currency_code: str,
        return_url: str,
        test: bool,
    ) -> dict[str, Any]:
        payload = {
            "query": """
            mutation AppSubscriptionCreate(
              $name: String!
              $lineItems: [AppSubscriptionLineItemInput!]!
              $returnUrl: URL!
              $test: Boolean
            ) {
              appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, test: $test) {
                userErrors {
                  field
                  message
                }
                confirmationUrl
                appSubscription {
                  id
                  status
                }
              }
            }
            """,
            "variables": {
                "name": name,
                "returnUrl": return_url,
                "test": test,
                "lineItems": [
                    {
                        "plan": {
                            "appRecurringPricingDetails": {
                                "price": {
                                    "amount": price_amount,
                                    "currencyCode": currency_code,
                                },
                                "interval": "EVERY_30_DAYS",
                            }
                        }
                    }
                ],
            },
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, payload)
        result = data.get("data", {}).get("appSubscriptionCreate", {})
        self._raise_user_errors(result.get("userErrors"))
        return result

    async def get_active_app_subscriptions(
        self,
        shop_domain: str,
        admin_access_token: str,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": """
            query CurrentAppInstallationSubscriptions {
              currentAppInstallation {
                activeSubscriptions {
                  id
                  name
                  status
                  test
                  createdAt
                  currentPeriodEnd
                  lineItems {
                    id
                    plan {
                      pricingDetails {
                        __typename
                      }
                    }
                  }
                }
              }
            }
            """,
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, payload)
        return data.get("data", {}).get("currentAppInstallation", {}).get("activeSubscriptions", [])

    async def cancel_app_subscription(
        self,
        shop_domain: str,
        admin_access_token: str,
        *,
        subscription_id: str,
        prorate: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "query": """
            mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
              appSubscriptionCancel(id: $id, prorate: $prorate) {
                userErrors {
                  field
                  message
                }
                appSubscription {
                  id
                  status
                }
              }
            }
            """,
            "variables": {
                "id": subscription_id,
                "prorate": prorate,
            },
        }
        data = await self._admin_graphql(shop_domain, admin_access_token, payload)
        result = data.get("data", {}).get("appSubscriptionCancel", {})
        self._raise_user_errors(result.get("userErrors"))
        return result

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

    def _raise_user_errors(self, user_errors: list[dict[str, Any]] | None) -> None:
        if not user_errors:
            return
        messages = [error.get("message") for error in user_errors if error.get("message")]
        if messages:
            raise ValueError("; ".join(messages))
