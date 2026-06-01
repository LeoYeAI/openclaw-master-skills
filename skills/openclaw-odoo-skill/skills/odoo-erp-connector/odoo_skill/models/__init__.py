"""Model operation modules for Odoo."""

from .partner import PartnerOps
from .sale_order import SaleOrderOps
from .invoice import InvoiceOps
from .inventory import InventoryOps
from .crm import CRMOps
from .purchase import PurchaseOrderOps
from .project import ProjectOps
from .hr import HROps
from .manufacturing import ManufacturingOps
from .calendar_ops import CalendarOps
from .fleet import FleetOps
from .ecommerce import EcommerceOps

__all__ = [
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
]
