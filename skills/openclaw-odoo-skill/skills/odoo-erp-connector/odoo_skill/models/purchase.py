"""
Purchase Order operations for Odoo ``purchase.order`` and ``purchase.order.line``.

Covers creation, confirmation, searching, and receipt validation for
purchase orders from vendors/suppliers.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_PO_LIST_FIELDS = [
    "id", "name", "partner_id", "state", "date_order",
    "date_planned", "amount_untaxed", "amount_tax", "amount_total",
    "user_id", "currency_id",
]

_PO_DETAIL_FIELDS = _PO_LIST_FIELDS + [
    "order_line", "invoice_ids", "picking_ids",
    "note", "payment_term_id", "company_id",
    "receipt_status", "invoice_status",
]

_PO_LINE_FIELDS = [
    "id", "product_id", "name", "product_qty",
    "price_unit", "price_subtotal",
    "date_planned", "qty_received", "qty_invoiced",
]


class PurchaseOrderOps:
    """High-level operations for Odoo purchase orders (``purchase.order``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "purchase.order"
    LINE_MODEL = "purchase.order.line"
    PICKING_MODEL = "stock.picking"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_purchase_order(
        self,
        partner_id: int,
        lines: list[dict],
        date_planned: Optional[str] = None,
        notes: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a new purchase order (RFQ).

        Args:
            partner_id: Vendor/supplier partner ID.
            lines: List of line dicts, each containing at minimum
                ``product_id`` and optionally ``quantity``, ``price_unit``,
                ``date_planned``.
            date_planned: Expected receipt date as ``YYYY-MM-DD`` string.
            notes: Optional order notes.
            **extra: Additional ``purchase.order`` field values.

        Returns:
            The newly created purchase order record.

        Example::

            po = purchase.create_purchase_order(
                partner_id=42,
                lines=[
                    {"product_id": 7, "quantity": 100, "price_unit": 12.50},
                ],
                date_planned="2025-03-01",
            )
        """
        order_lines = []
        for line in lines:
            ol: dict[str, Any] = {
                "product_id": line["product_id"],
                "product_qty": line.get("quantity", 1),
            }
            if "price_unit" in line:
                ol["price_unit"] = line["price_unit"]
            if "name" in line:
                ol["name"] = line["name"]
            if "date_planned" in line:
                ol["date_planned"] = line["date_planned"]
            elif date_planned:
                ol["date_planned"] = date_planned
            order_lines.append((0, 0, ol))

        values: dict[str, Any] = {
            "partner_id": partner_id,
            "order_line": order_lines,
        }
        if date_planned:
            values["date_planned"] = date_planned
        if notes:
            values["note"] = notes
        values.update(extra)

        po_id = self.client.create(self.MODEL, values)
        logger.info("Created purchase order for vendor=%d → id=%d", partner_id, po_id)
        return self.get_po(po_id)

    # ── Workflow actions ─────────────────────────────────────────────

    def confirm_po(self, po_id: int) -> dict:
        """Confirm a draft RFQ → purchase order.

        Args:
            po_id: The purchase order ID.

        Returns:
            The updated purchase order record (state should be ``purchase``).
        """
        self.client.execute(self.MODEL, "button_confirm", [po_id])
        logger.info("Confirmed purchase order id=%d", po_id)
        return self.get_po(po_id)

    def cancel_po(self, po_id: int) -> dict:
        """Cancel a purchase order.

        Args:
            po_id: The purchase order ID.

        Returns:
            The updated purchase order record.
        """
        self.client.execute(self.MODEL, "button_cancel", [po_id])
        logger.info("Cancelled purchase order id=%d", po_id)
        return self.get_po(po_id)

    # ── Read ─────────────────────────────────────────────────────────

    def get_po(self, po_id: int) -> dict:
        """Get full details of a single purchase order.

        Args:
            po_id: The purchase order ID.

        Returns:
            Purchase order record dict, or empty dict if not found.
        """
        records = self.client.read(self.MODEL, po_id, fields=_PO_DETAIL_FIELDS)
        return records[0] if records else {}

    def search_pos(
        self,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Search purchase orders with optional filters.

        Args:
            partner_id: Filter by vendor.
            state: Filter by state (``draft``, ``sent``, ``purchase``,
                ``done``, ``cancel``).
            limit: Max results.
            offset: Pagination offset.

        Returns:
            List of purchase order records.
        """
        domain: list = []
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.MODEL, domain, fields=_PO_LIST_FIELDS,
            limit=limit, offset=offset, order="date_order desc",
        )

    def get_po_lines(self, po_id: int) -> list[dict]:
        """Get the line items for a specific purchase order.

        Args:
            po_id: The purchase order ID.

        Returns:
            List of purchase order line dicts.
        """
        return self.client.search_read(
            self.LINE_MODEL,
            [["order_id", "=", po_id]],
            fields=_PO_LINE_FIELDS,
        )

    # ── Receipt handling ─────────────────────────────────────────────

    def receive_products(self, po_id: int) -> list[dict]:
        """Validate (receive) all pending receipts for a purchase order.

        Finds all incoming stock pickings associated with the PO and
        validates them, marking products as received.

        Args:
            po_id: The purchase order ID.

        Returns:
            List of validated picking records.

        Raises:
            OdooValidationError: If there are no pickings to validate.
        """
        # Get the PO to find associated pickings
        po = self.get_po(po_id)
        picking_ids = po.get("picking_ids", [])

        if not picking_ids:
            logger.warning("No pickings found for PO id=%d", po_id)
            return []

        validated = []
        for picking_id in picking_ids:
            picking = self.client.read(
                self.PICKING_MODEL, picking_id,
                fields=["id", "name", "state", "move_ids"],
            )
            if not picking:
                continue
            pick = picking[0]

            # Only validate pickings that are ready (assigned state)
            if pick["state"] in ("assigned", "confirmed"):
                # Set quantities done on all move lines
                for move_id in pick.get("move_ids", []):
                    move = self.client.read(
                        "stock.move", move_id,
                        fields=["id", "product_uom_qty", "quantity"],
                    )
                    if move:
                        self.client.write(
                            "stock.move", move_id,
                            {"quantity": move[0]["product_uom_qty"]},
                        )

                # Validate the picking
                try:
                    self.client.execute(
                        self.PICKING_MODEL, "button_validate", [picking_id],
                    )
                    logger.info("Validated picking %s (id=%d)", pick["name"], picking_id)
                    validated.append(pick)
                except Exception as exc:
                    logger.warning("Could not validate picking %d: %s", picking_id, exc)

        return validated
