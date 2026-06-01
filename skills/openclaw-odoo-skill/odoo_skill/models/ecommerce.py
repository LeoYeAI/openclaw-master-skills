"""
Website / eCommerce operations for Odoo.

Provides read-only access to website orders and product publishing
controls via ``sale.order`` (website context) and ``product.template``.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_WEBSITE_ORDER_FIELDS = [
    "id", "name", "partner_id", "state", "date_order",
    "amount_total", "website_id", "cart_quantity",
    "order_line",
]

_PRODUCT_PUBLISH_FIELDS = [
    "id", "name", "default_code", "website_published",
    "website_url", "list_price", "type",
]


class EcommerceOps:
    """High-level operations for Odoo Website / eCommerce.

    Provides website order querying and product publishing controls.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    ORDER_MODEL = "sale.order"
    PRODUCT_TEMPLATE_MODEL = "product.template"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Website orders ───────────────────────────────────────────────

    def get_website_orders(
        self,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get orders placed through the website.

        Args:
            state: Filter by state (``draft`` for carts, ``sale`` for
                confirmed orders, etc.).
            limit: Max results.

        Returns:
            List of website order records, newest first.
        """
        domain: list = [["website_id", "!=", False]]
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.ORDER_MODEL, domain,
            fields=_WEBSITE_ORDER_FIELDS, limit=limit,
            order="date_order desc",
        )

    def get_cart_info(self, order_id: int) -> dict:
        """Get details of a specific website cart/order.

        Args:
            order_id: The sale order ID.

        Returns:
            Order dict with line items, or empty dict if not found.
        """
        records = self.client.read(
            self.ORDER_MODEL, order_id,
            fields=_WEBSITE_ORDER_FIELDS + ["partner_id", "amount_untaxed", "amount_tax"],
        )
        if not records:
            return {}

        order = records[0]
        # Fetch line items
        if order.get("order_line"):
            order["lines"] = self.client.read(
                "sale.order.line", order["order_line"],
                fields=["product_id", "name", "product_uom_qty", "price_unit", "price_subtotal"],
            )
        return order

    # ── Product publishing ───────────────────────────────────────────

    def publish_product(self, product_tmpl_id: int) -> dict:
        """Publish a product on the website.

        Args:
            product_tmpl_id: The product template ID.

        Returns:
            The updated product template record.
        """
        self.client.write(
            self.PRODUCT_TEMPLATE_MODEL, product_tmpl_id,
            {"website_published": True},
        )
        logger.info("Published product template id=%d on website", product_tmpl_id)
        records = self.client.read(
            self.PRODUCT_TEMPLATE_MODEL, product_tmpl_id,
            fields=_PRODUCT_PUBLISH_FIELDS,
        )
        return records[0] if records else {}

    def unpublish_product(self, product_tmpl_id: int) -> dict:
        """Unpublish (hide) a product from the website.

        Args:
            product_tmpl_id: The product template ID.

        Returns:
            The updated product template record.
        """
        self.client.write(
            self.PRODUCT_TEMPLATE_MODEL, product_tmpl_id,
            {"website_published": False},
        )
        logger.info("Unpublished product template id=%d from website", product_tmpl_id)
        records = self.client.read(
            self.PRODUCT_TEMPLATE_MODEL, product_tmpl_id,
            fields=_PRODUCT_PUBLISH_FIELDS,
        )
        return records[0] if records else {}

    def get_published_products(self, limit: int = 100) -> list[dict]:
        """Get all products currently published on the website.

        Args:
            limit: Max results.

        Returns:
            List of published product template records.
        """
        return self.client.search_read(
            self.PRODUCT_TEMPLATE_MODEL,
            [["website_published", "=", True]],
            fields=_PRODUCT_PUBLISH_FIELDS, limit=limit,
            order="name asc",
        )
