"""
Smart Action Handler — fuzzy, natural-language-friendly operations.

This is the *key* module for OpenClaw integration. It translates
high-level, imprecise commands ("create a quotation for Rocky with
5 Rocks") into the precise multi-step Odoo workflows:
  1. Find-or-create the partner "Rocky"
  2. Find-or-create each product ("Rock")
  3. Build the quotation with resolved IDs

All smart actions are resilient: they search first, create only
when necessary, and provide clear feedback about what was found
vs. what was created.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from .client import OdooClient
from .models.partner import PartnerOps
from .models.sale_order import SaleOrderOps
from .models.invoice import InvoiceOps
from .models.inventory import InventoryOps
from .models.crm import CRMOps
from .models.purchase import PurchaseOrderOps
from .models.project import ProjectOps
from .models.hr import HROps
from .models.calendar_ops import CalendarOps

logger = logging.getLogger("odoo_skill")


class SmartActionHandler:
    """Handles fuzzy, natural-language-style Odoo operations.

    Wraps the lower-level Ops classes and adds find-or-create logic,
    name-based lookups, and resilient multi-step workflows.

    Args:
        client: An authenticated :class:`OdooClient` instance.

    Example::

        smart = SmartActionHandler(client)
        result = smart.smart_create_quotation(
            customer_name="Rocky",
            product_lines=[{"name": "Rock", "quantity": 5}],
        )
    """

    def __init__(self, client: OdooClient) -> None:
        self.client = client
        self.partners = PartnerOps(client)
        self.sales = SaleOrderOps(client)
        self.invoices = InvoiceOps(client)
        self.inventory = InventoryOps(client)
        self.crm = CRMOps(client)
        self.purchase = PurchaseOrderOps(client)
        self.projects = ProjectOps(client)
        self.hr = HROps(client)
        self.calendar = CalendarOps(client)

    # ── Find-or-Create primitives ────────────────────────────────────

    def find_or_create_partner(
        self,
        name: str,
        is_company: bool = True,
        supplier: bool = False,
        **defaults: Any,
    ) -> dict:
        """Search for a partner by name. Create if not found.

        Uses case-insensitive ``ilike`` matching. If multiple matches,
        returns the best match (exact name match preferred).

        Args:
            name: Partner/company name to search for.
            is_company: Whether to create as a company (if creating).
            supplier: If ``True``, set ``supplier_rank=1`` on creation.
            **defaults: Additional fields to set when creating.

        Returns:
            Dict with ``partner`` (record), ``created`` (bool), and
            ``matched`` (list of all matches found).
        """
        # Search existing partners
        results = self.client.search_read(
            "res.partner",
            [["name", "ilike", name], ["active", "=", True]],
            fields=["id", "name", "email", "phone", "is_company",
                    "customer_rank", "supplier_rank"],
            limit=10,
        )

        if results:
            # Prefer exact name match (case-insensitive)
            exact = [r for r in results if r["name"].lower() == name.lower()]
            best = exact[0] if exact else results[0]
            logger.info("Found existing partner %r (id=%d)", best["name"], best["id"])
            return {
                "partner": best,
                "created": False,
                "matched": results,
            }

        # Not found — create
        create_vals: dict[str, Any] = {
            "name": name,
            "is_company": is_company,
            "customer_rank": 1,
        }
        if supplier:
            create_vals["supplier_rank"] = 1
        create_vals.update(defaults)

        partner_id = self.client.create("res.partner", create_vals)
        partner = self.client.read(
            "res.partner", partner_id,
            fields=["id", "name", "email", "phone", "is_company"],
        )[0]
        logger.info("Created new partner %r (id=%d)", name, partner_id)

        return {
            "partner": partner,
            "created": True,
            "matched": [],
        }

    def find_or_create_product(
        self,
        name: str,
        **defaults: Any,
    ) -> dict:
        """Search for a product by name or internal reference. Create if not found.

        Args:
            name: Product name or SKU to search for.
            **defaults: Additional fields to set when creating
                (e.g. ``list_price``, ``type``).

        Returns:
            Dict with ``product`` (record), ``created`` (bool), and
            ``matched`` (list of all matches found).
        """
        # Search by name or internal reference (SKU)
        results = self.client.search_read(
            "product.product",
            ["|", ["name", "ilike", name], ["default_code", "ilike", name]],
            fields=["id", "name", "default_code", "list_price", "type"],
            limit=10,
        )

        if results:
            # Prefer exact name match
            exact = [r for r in results if r["name"].lower() == name.lower()]
            best = exact[0] if exact else results[0]
            logger.info("Found existing product %r (id=%d)", best["name"], best["id"])
            return {
                "product": best,
                "created": False,
                "matched": results,
            }

        # Not found — create a basic product
        create_vals: dict[str, Any] = {
            "name": name,
            "type": defaults.pop("type", "consu"),
            "list_price": defaults.pop("list_price", 0.0),
        }
        create_vals.update(defaults)

        product_id = self.client.create("product.product", create_vals)
        product = self.client.read(
            "product.product", product_id,
            fields=["id", "name", "default_code", "list_price", "type"],
        )[0]
        logger.info("Created new product %r (id=%d)", name, product_id)

        return {
            "product": product,
            "created": True,
            "matched": [],
        }

    def _find_or_create_project(self, name: str, **defaults: Any) -> dict:
        """Search for a project by name. Create if not found.

        Args:
            name: Project name.
            **defaults: Additional fields for creation.

        Returns:
            Dict with ``project`` (record) and ``created`` (bool).
        """
        results = self.client.search_read(
            "project.project",
            [["name", "ilike", name], ["active", "=", True]],
            fields=["id", "name", "user_id", "partner_id"],
            limit=5,
        )

        if results:
            exact = [r for r in results if r["name"].lower() == name.lower()]
            best = exact[0] if exact else results[0]
            return {"project": best, "created": False}

        project = self.projects.create_project(name, **defaults)
        return {"project": project, "created": True}

    # ── Smart composite actions ──────────────────────────────────────

    def smart_create_quotation(
        self,
        customer_name: str,
        product_lines: list[dict],
        notes: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a quotation from names (not IDs).

        Resolves customer and products by name, creating them if needed,
        then builds the sales quotation.

        Args:
            customer_name: Customer/company name.
            product_lines: List of dicts with ``name`` (product name),
                and optionally ``quantity``, ``price_unit``, ``discount``.
            notes: Optional order notes.
            **kwargs: Additional ``sale.order`` field values.

        Returns:
            Dict with ``order`` (the created quotation), ``customer`` info,
            and ``products`` info (showing what was found vs created).

        Example::

            result = smart.smart_create_quotation(
                customer_name="Rocky",
                product_lines=[
                    {"name": "Rock", "quantity": 5},
                    {"name": "Pebble", "quantity": 20, "price_unit": 1.50},
                ],
            )
        """
        # Step 1: Resolve customer
        customer_result = self.find_or_create_partner(customer_name)
        partner_id = customer_result["partner"]["id"]

        # Step 2: Resolve products and build order lines
        resolved_lines = []
        products_info = []
        for line in product_lines:
            product_name = line.get("name", line.get("product_name", ""))
            if not product_name and "product_id" in line:
                # Already have a product ID — use directly
                resolved_lines.append(line)
                products_info.append({"product_id": line["product_id"], "created": False})
                continue

            price_default = {}
            if "price_unit" in line:
                price_default["list_price"] = line["price_unit"]

            product_result = self.find_or_create_product(product_name, **price_default)
            product = product_result["product"]

            order_line: dict[str, Any] = {
                "product_id": product["id"],
                "quantity": line.get("quantity", line.get("qty", 1)),
            }
            if "price_unit" in line:
                order_line["price_unit"] = line["price_unit"]
            if "discount" in line:
                order_line["discount"] = line["discount"]

            resolved_lines.append(order_line)
            products_info.append({
                "product": product,
                "created": product_result["created"],
            })

        # Step 3: Create the quotation
        order = self.sales.create_quotation(
            partner_id=partner_id,
            lines=resolved_lines,
            notes=notes,
            **kwargs,
        )

        return {
            "order": order,
            "customer": customer_result,
            "products": products_info,
            "summary": (
                f"Quotation {order.get('name', '')} created for "
                f"{customer_result['partner']['name']} with "
                f"{len(resolved_lines)} line(s)"
            ),
        }

    def smart_create_invoice(
        self,
        customer_name: str,
        lines: list[dict],
        invoice_date: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Create an invoice from names (not IDs).

        Args:
            customer_name: Customer/company name.
            lines: List of dicts with ``name`` or ``description``,
                ``price_unit``, and optionally ``quantity``, ``product_name``.
            invoice_date: Invoice date as ``YYYY-MM-DD``.
            **kwargs: Additional ``account.move`` field values.

        Returns:
            Dict with ``invoice``, ``customer`` info, and ``products`` info.
        """
        # Resolve customer
        customer_result = self.find_or_create_partner(customer_name)
        partner_id = customer_result["partner"]["id"]

        # Resolve products in lines (if product names are provided)
        resolved_lines = []
        products_info = []
        for line in lines:
            il: dict[str, Any] = {
                "price_unit": line.get("price_unit", 0),
                "quantity": line.get("quantity", 1),
                "name": line.get("description", line.get("name", "")),
            }

            product_name = line.get("product_name", line.get("product", ""))
            if product_name:
                product_result = self.find_or_create_product(product_name)
                il["product_id"] = product_result["product"]["id"]
                products_info.append({
                    "product": product_result["product"],
                    "created": product_result["created"],
                })
            elif "product_id" in line:
                il["product_id"] = line["product_id"]

            resolved_lines.append(il)

        # Create the invoice
        invoice = self.invoices.create_invoice(
            partner_id=partner_id,
            lines=resolved_lines,
            invoice_date=invoice_date,
            **kwargs,
        )

        return {
            "invoice": invoice,
            "customer": customer_result,
            "products": products_info,
            "summary": (
                f"Invoice {invoice.get('name', '')} created for "
                f"{customer_result['partner']['name']}"
            ),
        }

    def smart_create_lead(
        self,
        name: str,
        contact_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        expected_revenue: Optional[float] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a CRM lead with optional partner linking.

        If ``contact_name`` is provided, attempts to find and link
        an existing partner.

        Args:
            name: Lead title.
            contact_name: Contact person name.
            email: Contact email.
            phone: Contact phone.
            expected_revenue: Estimated deal value.
            **kwargs: Additional ``crm.lead`` field values.

        Returns:
            Dict with ``lead`` and optionally ``partner`` info.
        """
        extra: dict[str, Any] = dict(kwargs)

        # Try to link to existing partner if contact name is given
        partner_info = None
        if contact_name:
            partner_result = self.find_or_create_partner(
                contact_name, is_company=False,
            )
            extra["partner_id"] = partner_result["partner"]["id"]
            partner_info = partner_result

        lead = self.crm.create_lead(
            name=name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            expected_revenue=expected_revenue,
            **extra,
        )

        return {
            "lead": lead,
            "partner": partner_info,
            "summary": f"Lead '{name}' created (id={lead.get('id', '?')})",
        }

    def smart_create_purchase(
        self,
        vendor_name: str,
        product_lines: list[dict],
        date_planned: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a purchase order from names (not IDs).

        Args:
            vendor_name: Vendor/supplier name.
            product_lines: List of dicts with ``name`` (product name),
                and optionally ``quantity``, ``price_unit``.
            date_planned: Expected receipt date.
            **kwargs: Additional ``purchase.order`` field values.

        Returns:
            Dict with ``purchase_order``, ``vendor`` info, and ``products`` info.
        """
        # Resolve vendor
        vendor_result = self.find_or_create_partner(
            vendor_name, supplier=True,
        )
        partner_id = vendor_result["partner"]["id"]

        # Ensure supplier_rank is set
        if not vendor_result["created"]:
            partner = vendor_result["partner"]
            if not partner.get("supplier_rank"):
                self.client.write("res.partner", partner_id, {"supplier_rank": 1})

        # Resolve products
        resolved_lines = []
        products_info = []
        for line in product_lines:
            product_name = line.get("name", line.get("product_name", ""))
            if product_name:
                product_result = self.find_or_create_product(product_name)
                product = product_result["product"]
                products_info.append({
                    "product": product,
                    "created": product_result["created"],
                })

                order_line: dict[str, Any] = {
                    "product_id": product["id"],
                    "quantity": line.get("quantity", line.get("qty", 1)),
                }
                if "price_unit" in line:
                    order_line["price_unit"] = line["price_unit"]
                resolved_lines.append(order_line)

        # Create the purchase order
        po = self.purchase.create_purchase_order(
            partner_id=partner_id,
            lines=resolved_lines,
            date_planned=date_planned,
            **kwargs,
        )

        return {
            "purchase_order": po,
            "vendor": vendor_result,
            "products": products_info,
            "summary": (
                f"Purchase Order {po.get('name', '')} created for "
                f"vendor {vendor_result['partner']['name']}"
            ),
        }

    def smart_create_task(
        self,
        project_name: str,
        task_name: str,
        description: Optional[str] = None,
        date_deadline: Optional[str] = None,
        assignee_name: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a task in a project, resolving project by name.

        Args:
            project_name: Name of the project (found or created).
            task_name: Task title.
            description: Task description.
            date_deadline: Due date as ``YYYY-MM-DD``.
            assignee_name: Name of the user to assign (searches ``res.users``).
            **kwargs: Additional ``project.task`` field values.

        Returns:
            Dict with ``task``, ``project`` info, and optionally ``assignee``.
        """
        # Resolve project
        project_result = self._find_or_create_project(project_name)
        project_id = project_result["project"]["id"]

        # Resolve assignee if provided
        assignee_info = None
        user_ids = None
        if assignee_name:
            users = self.client.search_read(
                "res.users",
                [["name", "ilike", assignee_name], ["active", "=", True]],
                fields=["id", "name"],
                limit=5,
            )
            if users:
                user_ids = [users[0]["id"]]
                assignee_info = users[0]

        task = self.projects.create_task(
            project_id=project_id,
            name=task_name,
            user_ids=user_ids,
            description=description,
            date_deadline=date_deadline,
            **kwargs,
        )

        return {
            "task": task,
            "project": project_result,
            "assignee": assignee_info,
            "summary": (
                f"Task '{task_name}' created in project "
                f"'{project_result['project']['name']}'"
            ),
        }

    def smart_create_employee(
        self,
        name: str,
        job_title: Optional[str] = None,
        department_name: Optional[str] = None,
        work_email: Optional[str] = None,
        work_phone: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """Create an employee, resolving department by name.

        Args:
            name: Employee's full name.
            job_title: Job title/position.
            department_name: Department name (found or created).
            work_email: Work email address.
            work_phone: Work phone number.
            **kwargs: Additional ``hr.employee`` field values.

        Returns:
            Dict with ``employee`` and optionally ``department`` info.
        """
        # Check if employee already exists by name
        existing = self.client.search_read(
            "hr.employee",
            [["name", "ilike", name], ["active", "=", True]],
            fields=["id", "name", "job_title", "department_id"],
            limit=5,
        )
        if existing:
            exact = [e for e in existing if e["name"].lower() == name.lower()]
            if exact:
                return {
                    "employee": exact[0],
                    "created": False,
                    "summary": f"Employee '{name}' already exists (id={exact[0]['id']})",
                }

        # Resolve department if provided
        department_info = None
        department_id = kwargs.pop("department_id", None)
        if department_name and not department_id:
            depts = self.client.search_read(
                "hr.department",
                [["name", "ilike", department_name]],
                fields=["id", "name"],
                limit=5,
            )
            if depts:
                department_id = depts[0]["id"]
                department_info = {"department": depts[0], "created": False}
            else:
                dept = self.hr.create_department(department_name)
                department_id = dept["id"]
                department_info = {"department": dept, "created": True}

        employee = self.hr.create_employee(
            name=name,
            job_title=job_title,
            department_id=department_id,
            work_email=work_email,
            work_phone=work_phone,
            **kwargs,
        )

        return {
            "employee": employee,
            "department": department_info,
            "created": True,
            "summary": f"Employee '{name}' created (id={employee.get('id', '?')})",
        }

    def smart_create_event(
        self,
        name: str,
        start: str,
        end: Optional[str] = None,
        location: Optional[str] = None,
        attendee_names: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a calendar event, resolving attendees by name.

        Args:
            name: Event title.
            start: Start datetime as ``YYYY-MM-DD HH:MM:SS`` or
                ``YYYY-MM-DD`` for all-day events.
            end: End datetime. Defaults to 1 hour after start.
            location: Event location.
            attendee_names: List of partner/contact names to invite.
            **kwargs: Additional ``calendar.event`` field values.

        Returns:
            Dict with ``event`` and ``attendees`` info.
        """
        # Resolve attendees by name
        partner_ids = []
        attendees_info = []
        if attendee_names:
            for att_name in attendee_names:
                result = self.find_or_create_partner(att_name, is_company=False)
                partner_ids.append(result["partner"]["id"])
                attendees_info.append(result)

        # Detect all-day event
        allday = len(start) == 10  # Just a date, no time

        event = self.calendar.create_event(
            name=name,
            start=start,
            stop=end,
            allday=allday,
            location=location,
            partner_ids=partner_ids if partner_ids else None,
            **kwargs,
        )

        return {
            "event": event,
            "attendees": attendees_info,
            "summary": (
                f"Event '{name}' created at {start}"
                + (f" with {len(attendees_info)} attendee(s)" if attendees_info else "")
            ),
        }
