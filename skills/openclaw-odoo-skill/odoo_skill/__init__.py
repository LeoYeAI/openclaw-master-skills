"""
OdooConnector — OpenClaw Skill for Odoo ERP integration.

Provides a unified interface to Odoo's CRM, Sales, Invoicing,
Inventory, Purchase, Project, HR, Manufacturing, Calendar, Fleet,
and eCommerce modules via XML-RPC.

Usage::

    from odoo_skill import OdooClient, SmartActionHandler

    client = OdooClient.from_env()
    smart = SmartActionHandler(client)
    result = smart.smart_create_quotation(
        customer_name="Rocky",
        product_lines=[{"name": "Rock", "quantity": 5}],
    )
"""

__version__ = "2.0.0"

from .client import OdooClient
from .config import OdooConfig, load_config
from .errors import (
    OdooError,
    OdooConnectionError,
    OdooAuthenticationError,
    OdooAccessError,
    OdooValidationError,
    OdooRecordNotFoundError,
)
from .models import (
    PartnerOps,
    SaleOrderOps,
    InvoiceOps,
    InventoryOps,
    CRMOps,
    PurchaseOrderOps,
    ProjectOps,
    HROps,
    ManufacturingOps,
    CalendarOps,
    FleetOps,
    EcommerceOps,
)
from .smart_actions import SmartActionHandler
from .sync import OdooChangePoller, OdooWebhookServer

__all__ = [
    # Core
    "OdooClient",
    "OdooConfig",
    "load_config",
    # Errors
    "OdooError",
    "OdooConnectionError",
    "OdooAuthenticationError",
    "OdooAccessError",
    "OdooValidationError",
    "OdooRecordNotFoundError",
    # Model Ops
    "PartnerOps",
    "SaleOrderOps",
    "InvoiceOps",
    "InventoryOps",
    "CRMOps",
    "PurchaseOrderOps",
    "ProjectOps",
    "HROps",
    "ManufacturingOps",
    "CalendarOps",
    "FleetOps",
    "EcommerceOps",
    # Smart Actions
    "SmartActionHandler",
    # Sync
    "OdooChangePoller",
    "OdooWebhookServer",
]
