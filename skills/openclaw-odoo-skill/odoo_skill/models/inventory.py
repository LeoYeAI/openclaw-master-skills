"""
Inventory and product operations for Odoo.

Covers ``product.product``, ``product.template``, and ``stock.quant``.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_PRODUCT_LIST_FIELDS = [
    "id", "name", "default_code", "barcode",
    "list_price", "standard_price",
    "type", "categ_id", "active",
]

_PRODUCT_DETAIL_FIELDS = _PRODUCT_LIST_FIELDS + [
    "qty_available", "virtual_available",
    "incoming_qty", "outgoing_qty",
    "description_sale",
    "uom_id", "weight", "volume",
]

_STOCK_FIELDS = [
    "id", "product_id", "location_id",
    "quantity", "reserved_quantity",
]


class InventoryOps:
    """High-level operations for Odoo products and stock levels.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    PRODUCT_MODEL = "product.product"
    QUANT_MODEL = "stock.quant"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Product search ───────────────────────────────────────────────

    def search_products(
        self,
        query: str,
        product_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search products by name or internal reference (SKU).

        Args:
            query: Search text (matched against name and default_code).
            product_type: Filter by type: ``'consu'``, ``'product'``,
                or ``'service'``. ``None`` returns all types.
            limit: Max results.

        Returns:
            List of matching product records.
        """
        domain: list = [
            "|",
            ["name", "ilike", query],
            ["default_code", "ilike", query],
        ]
        if product_type:
            domain.append(["type", "=", product_type])

        return self.client.search_read(
            self.PRODUCT_MODEL, domain,
            fields=_PRODUCT_LIST_FIELDS, limit=limit,
        )

    # ── Stock queries ────────────────────────────────────────────────

    def check_product_availability(self, product_id: int) -> dict:
        """Check stock and forecast for a single product.

        Args:
            product_id: The ``product.product`` ID.

        Returns:
            Dict with ``product``, ``sku``, ``on_hand``, ``forecasted``,
            ``incoming``, ``outgoing``.
        """
        records = self.client.read(
            self.PRODUCT_MODEL, product_id, fields=_PRODUCT_DETAIL_FIELDS,
        )
        if not records:
            return {}
        p = records[0]
        return {
            "id": p["id"],
            "product": p["name"],
            "sku": p.get("default_code") or "",
            "on_hand": p["qty_available"],
            "forecasted": p["virtual_available"],
            "incoming": p.get("incoming_qty", 0),
            "outgoing": p.get("outgoing_qty", 0),
            "unit_price": p["list_price"],
        }

    def get_stock_levels(
        self,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get current stock quantities from ``stock.quant``.

        Args:
            product_id: Filter by product.
            warehouse_id: Filter by warehouse.
            limit: Max results.

        Returns:
            List of stock quant records.
        """
        domain: list = [["location_id.usage", "=", "internal"]]
        if product_id:
            domain.append(["product_id", "=", product_id])
        if warehouse_id:
            domain.append(["warehouse_id", "=", warehouse_id])

        return self.client.search_read(
            self.QUANT_MODEL, domain, fields=_STOCK_FIELDS, limit=limit,
        )

    def get_low_stock_products(
        self,
        threshold: float = 10.0,
        limit: int = 50,
    ) -> list[dict]:
        """Find storable products whose on-hand quantity is at or below a threshold.

        Note:
            ``qty_available`` is a computed (non-stored) field in Odoo 19+,
            so we cannot filter/sort on it via domain. Instead we fetch all
            storable products and filter client-side.

        Args:
            threshold: Stock level threshold (default 10).
            limit: Max results.

        Returns:
            List of low-stock product records, sorted by qty ascending.
        """
        # Fetch all active storable products (type='product' in older Odoo,
        # but Odoo 19 uses 'consu' for consumable — fetch both)
        domain: list = [
            ["type", "in", ["product", "consu"]],
            ["active", "=", True],
        ]
        fields = ["id", "name", "default_code", "qty_available", "virtual_available", "list_price"]
        all_products = self.client.search_read(
            self.PRODUCT_MODEL, domain, fields=fields, limit=500,
        )
        # Filter client-side
        low_stock = [p for p in all_products if p.get("qty_available", 0) <= threshold]
        low_stock.sort(key=lambda p: p.get("qty_available", 0))
        return low_stock[:limit]
