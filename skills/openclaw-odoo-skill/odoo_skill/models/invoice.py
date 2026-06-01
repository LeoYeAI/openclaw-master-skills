"""
Invoice operations for Odoo ``account.move``.
"""

import logging
from datetime import date
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_INVOICE_LIST_FIELDS = [
    "id", "name", "partner_id", "move_type", "state",
    "payment_state", "invoice_date", "invoice_date_due",
    "amount_untaxed", "amount_total", "amount_residual",
    "currency_id",
]

_INVOICE_DETAIL_FIELDS = _INVOICE_LIST_FIELDS + [
    "invoice_line_ids", "ref", "narration",
    "company_id", "user_id",
]


class InvoiceOps:
    """High-level operations for Odoo invoices (``account.move``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "account.move"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_invoice(
        self,
        partner_id: int,
        lines: list[dict],
        invoice_date: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a customer invoice.

        Args:
            partner_id: Customer ID.
            lines: List of line dicts, each containing at minimum
                ``price_unit`` and optionally ``product_id``, ``quantity``,
                ``description``, ``account_id``.
            invoice_date: Invoice date as ``YYYY-MM-DD`` string.
            **extra: Additional ``account.move`` field values.

        Returns:
            The newly created invoice record.
        """
        invoice_lines = []
        for line in lines:
            il: dict[str, Any] = {
                "name": line.get("description", line.get("name", "")),
                "quantity": line.get("quantity", 1),
                "price_unit": line["price_unit"],
            }
            if "product_id" in line:
                il["product_id"] = line["product_id"]
            if "account_id" in line:
                il["account_id"] = line["account_id"]
            if "tax_ids" in line:
                il["tax_ids"] = [(6, 0, line["tax_ids"])]
            invoice_lines.append((0, 0, il))

        values: dict[str, Any] = {
            "move_type": "out_invoice",
            "partner_id": partner_id,
            "invoice_line_ids": invoice_lines,
        }
        if invoice_date:
            values["invoice_date"] = invoice_date
        values.update(extra)

        invoice_id = self.client.create(self.MODEL, values)
        logger.info("Created invoice for partner_id=%d → id=%d", partner_id, invoice_id)
        return self.get_invoice(invoice_id)

    # ── Workflow ─────────────────────────────────────────────────────

    def post_invoice(self, invoice_id: int) -> dict:
        """Post (validate) a draft invoice.

        Args:
            invoice_id: The invoice (``account.move``) ID.

        Returns:
            The updated invoice record.
        """
        self.client.execute(self.MODEL, "action_post", [invoice_id])
        logger.info("Posted invoice id=%d", invoice_id)
        return self.get_invoice(invoice_id)

    # ── Read ─────────────────────────────────────────────────────────

    def get_invoice(self, invoice_id: int) -> dict:
        """Get full details of a single invoice.

        Args:
            invoice_id: The invoice ID.

        Returns:
            Invoice record dict, or empty dict if not found.
        """
        records = self.client.read(self.MODEL, invoice_id, fields=_INVOICE_DETAIL_FIELDS)
        return records[0] if records else {}

    def get_unpaid_invoices(
        self,
        partner_id: Optional[int] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get customer invoices that are not fully paid.

        Args:
            partner_id: Optionally filter by customer.
            limit: Max results.

        Returns:
            List of unpaid invoice records, ordered by due date.
        """
        domain: list = [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["payment_state", "in", ["not_paid", "partial"]],
        ]
        if partner_id:
            domain.append(["partner_id", "=", partner_id])

        return self.client.search_read(
            self.MODEL, domain, fields=_INVOICE_LIST_FIELDS,
            limit=limit, order="invoice_date_due asc",
        )

    def get_overdue_invoices(self, limit: int = 50) -> list[dict]:
        """Get all overdue customer invoices.

        Returns invoices that are posted, not fully paid, and past
        their due date.

        Args:
            limit: Max results.

        Returns:
            List of overdue invoice records, oldest first.
        """
        today = date.today().isoformat()
        domain: list = [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["payment_state", "in", ["not_paid", "partial"]],
            ["invoice_date_due", "<", today],
        ]
        return self.client.search_read(
            self.MODEL, domain, fields=_INVOICE_LIST_FIELDS,
            limit=limit, order="invoice_date_due asc",
        )
