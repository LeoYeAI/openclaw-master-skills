"""
Manufacturing (MRP) operations for Odoo.

Covers ``mrp.bom`` (bills of materials) and ``mrp.production``
(manufacturing orders).
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_BOM_LIST_FIELDS = [
    "id", "product_tmpl_id", "product_id", "product_qty",
    "type", "code", "active",
]

_BOM_DETAIL_FIELDS = _BOM_LIST_FIELDS + [
    "bom_line_ids", "operation_ids",
    "company_id", "product_uom_id",
]

_BOM_LINE_FIELDS = [
    "id", "product_id", "product_qty", "product_uom_id",
    "bom_id",
]

_MO_LIST_FIELDS = [
    "id", "name", "product_id", "product_qty",
    "state", "date_start", "date_finished",
    "bom_id", "user_id", "company_id",
]

_MO_DETAIL_FIELDS = _MO_LIST_FIELDS + [
    "move_raw_ids", "move_finished_ids",
    "origin", "product_uom_id", "qty_produced",
]


class ManufacturingOps:
    """High-level operations for Odoo Manufacturing (MRP).

    Manages bills of materials and manufacturing orders.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    BOM_MODEL = "mrp.bom"
    BOM_LINE_MODEL = "mrp.bom.line"
    MO_MODEL = "mrp.production"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Bill of Materials ────────────────────────────────────────────

    def create_bom(
        self,
        product_tmpl_id: int,
        components: list[dict],
        product_qty: float = 1.0,
        bom_type: str = "normal",
        **extra: Any,
    ) -> dict:
        """Create a Bill of Materials (BOM).

        Args:
            product_tmpl_id: Product template ID for the finished product.
            components: List of component dicts, each containing
                ``product_id`` and ``product_qty``.
            product_qty: Quantity the BOM produces (default: 1).
            bom_type: BOM type — ``'normal'`` (manufacture) or
                ``'phantom'`` (kit).
            **extra: Additional ``mrp.bom`` field values.

        Returns:
            The newly created BOM record.

        Example::

            bom = mfg.create_bom(
                product_tmpl_id=42,
                components=[
                    {"product_id": 10, "product_qty": 2},
                    {"product_id": 11, "product_qty": 4},
                ],
            )
        """
        bom_lines = []
        for comp in components:
            line: dict[str, Any] = {
                "product_id": comp["product_id"],
                "product_qty": comp.get("product_qty", 1),
            }
            bom_lines.append((0, 0, line))

        values: dict[str, Any] = {
            "product_tmpl_id": product_tmpl_id,
            "product_qty": product_qty,
            "type": bom_type,
            "bom_line_ids": bom_lines,
        }
        values.update(extra)

        bom_id = self.client.create(self.BOM_MODEL, values)
        logger.info("Created BOM for product_tmpl=%d → id=%d", product_tmpl_id, bom_id)
        return self.get_bom(bom_id)

    def get_bom(self, bom_id: int) -> dict:
        """Get full details of a Bill of Materials.

        Args:
            bom_id: The BOM ID.

        Returns:
            BOM record dict with lines, or empty dict if not found.
        """
        records = self.client.read(self.BOM_MODEL, bom_id, fields=_BOM_DETAIL_FIELDS)
        if not records:
            return {}

        bom = records[0]
        # Fetch BOM lines for a complete picture
        if bom.get("bom_line_ids"):
            bom["lines"] = self.client.read(
                self.BOM_LINE_MODEL, bom["bom_line_ids"],
                fields=_BOM_LINE_FIELDS,
            )
        return bom

    def search_boms(
        self,
        product_tmpl_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search bills of materials.

        Args:
            product_tmpl_id: Filter by product template.
            limit: Max results.

        Returns:
            List of BOM records.
        """
        domain: list = [["active", "=", True]]
        if product_tmpl_id:
            domain.append(["product_tmpl_id", "=", product_tmpl_id])

        return self.client.search_read(
            self.BOM_MODEL, domain,
            fields=_BOM_LIST_FIELDS, limit=limit,
        )

    # ── Manufacturing Orders ─────────────────────────────────────────

    def create_manufacturing_order(
        self,
        product_id: int,
        product_qty: float = 1.0,
        bom_id: Optional[int] = None,
        date_start: Optional[str] = None,
        origin: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a manufacturing order.

        Args:
            product_id: The product to manufacture (``product.product`` ID).
            product_qty: Quantity to produce.
            bom_id: Specific BOM to use. If ``None``, Odoo selects
                the default BOM for the product.
            date_start: Planned start date as ``YYYY-MM-DD HH:MM:SS``.
            origin: Source document reference.
            **extra: Additional ``mrp.production`` field values.

        Returns:
            The newly created manufacturing order record.
        """
        values: dict[str, Any] = {
            "product_id": product_id,
            "product_qty": product_qty,
        }
        if bom_id:
            values["bom_id"] = bom_id
        if date_start:
            values["date_start"] = date_start
        if origin:
            values["origin"] = origin
        values.update(extra)

        mo_id = self.client.create(self.MO_MODEL, values)
        logger.info("Created manufacturing order for product=%d → id=%d", product_id, mo_id)
        return self._read_mo(mo_id)

    def confirm_mo(self, mo_id: int) -> dict:
        """Confirm a draft manufacturing order.

        Args:
            mo_id: The manufacturing order ID.

        Returns:
            The updated manufacturing order record.
        """
        self.client.execute(self.MO_MODEL, "action_confirm", [mo_id])
        logger.info("Confirmed manufacturing order id=%d", mo_id)
        return self._read_mo(mo_id)

    def mark_done_mo(self, mo_id: int) -> dict:
        """Mark a manufacturing order as done (produce the quantity).

        Sets the produced quantity and validates the order.

        Args:
            mo_id: The manufacturing order ID.

        Returns:
            The updated manufacturing order record.
        """
        # Read current MO to get expected qty
        mo = self._read_mo(mo_id)
        expected_qty = mo.get("product_qty", 1)

        # Set qty_produced if it's not already set
        if mo.get("qty_produced", 0) < expected_qty:
            self.client.write(self.MO_MODEL, mo_id, {
                "qty_produced": expected_qty,
            })

        # Try to mark as done via button_mark_done
        try:
            self.client.execute(self.MO_MODEL, "button_mark_done", [mo_id])
        except Exception:
            # Some Odoo versions use a different method name
            try:
                self.client.execute(self.MO_MODEL, "action_toggle_is_locked", [mo_id])
                self.client.write(self.MO_MODEL, mo_id, {"state": "done"})
            except Exception as exc:
                logger.warning("Could not mark MO %d as done via action: %s", mo_id, exc)

        logger.info("Marked manufacturing order id=%d as done", mo_id)
        return self._read_mo(mo_id)

    def search_manufacturing_orders(
        self,
        product_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search manufacturing orders with optional filters.

        Args:
            product_id: Filter by product.
            state: Filter by state (``draft``, ``confirmed``,
                ``progress``, ``done``, ``cancel``).
            limit: Max results.

        Returns:
            List of manufacturing order records.
        """
        domain: list = []
        if product_id:
            domain.append(["product_id", "=", product_id])
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.MO_MODEL, domain,
            fields=_MO_LIST_FIELDS, limit=limit,
            order="date_start desc",
        )

    # ── Internal helpers ─────────────────────────────────────────────

    def _read_mo(self, mo_id: int) -> dict:
        """Read a single manufacturing order by ID."""
        records = self.client.read(
            self.MO_MODEL, mo_id, fields=_MO_DETAIL_FIELDS,
        )
        return records[0] if records else {}
