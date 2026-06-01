"""
Sales order operations for Odoo ``sale.order`` and ``sale.order.line``.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_ORDER_LIST_FIELDS = [
    "id", "name", "partner_id", "state", "date_order",
    "amount_untaxed", "amount_tax", "amount_total",
    "user_id", "team_id",
]

_ORDER_DETAIL_FIELDS = _ORDER_LIST_FIELDS + [
    "order_line", "invoice_ids", "note",
    "payment_term_id", "pricelist_id",
    "currency_id", "company_id",
]

_LINE_FIELDS = [
    "id", "product_id", "name", "product_uom_qty",
    "price_unit", "discount", "price_subtotal", "tax_ids",
]


class SaleOrderOps:
    """High-level operations for Odoo sales orders (``sale.order``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "sale.order"
    LINE_MODEL = "sale.order.line"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_quotation(
        self,
        partner_id: int,
        lines: list[dict],
        notes: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a new sales quotation.

        Args:
            partner_id: Customer ID.
            lines: List of line dicts, each containing at minimum
                ``product_id`` and optionally ``quantity``, ``price_unit``,
                ``discount``.
            notes: Optional order notes.
            **extra: Additional ``sale.order`` field values.

        Returns:
            The newly created order record.

        Example::

            order = sales.create_quotation(
                partner_id=42,
                lines=[
                    {"product_id": 7, "quantity": 10, "price_unit": 49.99},
                    {"product_id": 8, "quantity": 5},
                ],
            )
        """
        order_lines = []
        for line in lines:
            ol: dict[str, Any] = {
                "product_id": line["product_id"],
                "product_uom_qty": line.get("quantity", 1),
            }
            if "price_unit" in line:
                ol["price_unit"] = line["price_unit"]
            if "discount" in line:
                ol["discount"] = line["discount"]
            if "name" in line:
                ol["name"] = line["name"]
            # (0, 0, vals) = create new linked record
            order_lines.append((0, 0, ol))

        values: dict[str, Any] = {
            "partner_id": partner_id,
            "order_line": order_lines,
        }
        if notes:
            values["note"] = notes
        values.update(extra)

        order_id = self.client.create(self.MODEL, values)
        logger.info("Created quotation for partner_id=%d → id=%d", partner_id, order_id)
        return self.get_order(order_id)

    # ── Workflow actions ─────────────────────────────────────────────

    def confirm_order(self, order_id: int) -> dict:
        """Confirm a draft quotation → sales order.

        Args:
            order_id: The sale order ID.

        Returns:
            The updated order record (state should be ``sale``).
        """
        self.client.execute(self.MODEL, "action_confirm", [order_id])
        logger.info("Confirmed order id=%d", order_id)
        return self.get_order(order_id)

    def cancel_order(self, order_id: int) -> dict:
        """Cancel a sales order.

        Args:
            order_id: The sale order ID.

        Returns:
            The updated order record (state should be ``cancel``).
        """
        self.client.execute(self.MODEL, "action_cancel", [order_id])
        logger.info("Cancelled order id=%d", order_id)
        return self.get_order(order_id)

    # ── Read ─────────────────────────────────────────────────────────

    def get_order(self, order_id: int) -> dict:
        """Get full details of a single sales order.

        Args:
            order_id: The sale order ID.

        Returns:
            Order record dict.
        """
        records = self.client.read(self.MODEL, order_id, fields=_ORDER_DETAIL_FIELDS)
        return records[0] if records else {}

    def search_orders(
        self,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Search sales orders with optional filters.

        Args:
            partner_id: Filter by customer.
            state: Filter by state (``draft``, ``sent``, ``sale``, ``done``, ``cancel``).
            limit: Max results.
            offset: Pagination offset.

        Returns:
            List of order records.
        """
        domain: list = []
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.MODEL, domain, fields=_ORDER_LIST_FIELDS,
            limit=limit, offset=offset, order="date_order desc",
        )

    def get_order_lines(self, order_id: int) -> list[dict]:
        """Get the line items for a specific order.

        Args:
            order_id: The sale order ID.

        Returns:
            List of order line dicts.
        """
        return self.client.search_read(
            self.LINE_MODEL,
            [["order_id", "=", order_id]],
            fields=_LINE_FIELDS,
        )
