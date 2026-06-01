"""
Partner (Customer/Contact) operations for Odoo ``res.partner``.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

# Fields we commonly read for partner summaries
_PARTNER_LIST_FIELDS = [
    "id", "name", "email", "phone", "city",
    "country_id", "is_company", "customer_rank",
]

_PARTNER_DETAIL_FIELDS = _PARTNER_LIST_FIELDS + [
    "street", "street2", "zip", "state_id", "vat",
    "website", "parent_id", "comment",
]


class PartnerOps:
    """High-level CRUD for Odoo contacts / customers (``res.partner``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "res.partner"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_customer(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_company: bool = True,
        **extra: Any,
    ) -> dict:
        """Create a new customer in Odoo.

        Args:
            name: Customer / company name.
            email: Contact email address.
            phone: Phone number.
            is_company: ``True`` for companies, ``False`` for individuals.
            **extra: Any additional ``res.partner`` fields.

        Returns:
            The newly created partner record (dict).
        """
        values: dict[str, Any] = {
            "name": name,
            "is_company": is_company,
            "customer_rank": 1,
        }
        if email:
            values["email"] = email
        if phone:
            values["phone"] = phone
        values.update(extra)

        partner_id = self.client.create(self.MODEL, values)
        logger.info("Created customer %r (id=%d)", name, partner_id)
        return self.client.read(self.MODEL, partner_id, fields=_PARTNER_DETAIL_FIELDS)[0]

    # ── Search ───────────────────────────────────────────────────────

    def find_customer(self, query: str, limit: int = 10) -> list[dict]:
        """Search customers by name, email, or phone.

        Args:
            query: Free-text search string.
            limit: Max results to return.

        Returns:
            List of matching partner records.
        """
        domain: list = [
            "&", ["customer_rank", ">", 0],
            "|", "|",
            ["name", "ilike", query],
            ["email", "ilike", query],
            ["phone", "ilike", query],
        ]
        return self.client.search_read(
            self.MODEL, domain, fields=_PARTNER_LIST_FIELDS, limit=limit,
        )

    # ── Read ─────────────────────────────────────────────────────────

    def get_customer_summary(self, partner_id: int) -> Optional[dict]:
        """Get a customer's full summary including sales statistics.

        Args:
            partner_id: The partner record ID.

        Returns:
            Partner dict or ``None`` if not found.
        """
        records = self.client.read(
            self.MODEL, partner_id, fields=_PARTNER_DETAIL_FIELDS,
        )
        return records[0] if records else None

    # ── Update ───────────────────────────────────────────────────────

    def update_customer(self, partner_id: int, **values: Any) -> dict:
        """Update a customer's fields.

        Args:
            partner_id: The partner record ID.
            **values: Field values to update.

        Returns:
            The updated partner record.
        """
        self.client.write(self.MODEL, partner_id, values)
        logger.info("Updated customer id=%d: %s", partner_id, list(values.keys()))
        return self.client.read(self.MODEL, partner_id, fields=_PARTNER_DETAIL_FIELDS)[0]

    # ── Delete ───────────────────────────────────────────────────────

    def delete_customer(self, partner_id: int) -> bool:
        """Delete (archive) a customer.

        Note:
            Odoo may prevent deletion if the partner has linked
            transactions. In that case, this deactivates the record.

        Args:
            partner_id: The partner record ID.

        Returns:
            ``True`` on success.
        """
        try:
            result = self.client.unlink(self.MODEL, partner_id)
            logger.info("Deleted customer id=%d", partner_id)
            return result
        except Exception:
            # If deletion fails (linked records), archive instead
            logger.warning(
                "Cannot delete customer id=%d — archiving instead", partner_id
            )
            self.client.write(self.MODEL, partner_id, {"active": False})
            return True
