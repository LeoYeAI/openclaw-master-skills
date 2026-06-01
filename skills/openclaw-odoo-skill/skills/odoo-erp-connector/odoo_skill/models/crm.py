"""
CRM Lead and Opportunity operations for Odoo ``crm.lead``.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_LEAD_LIST_FIELDS = [
    "id", "name", "partner_id", "email_from", "phone",
    "expected_revenue", "probability", "stage_id",
    "user_id", "type", "priority", "date_deadline",
]

_LEAD_DETAIL_FIELDS = _LEAD_LIST_FIELDS + [
    "contact_name", "partner_name", "team_id",
    "tag_ids", "description", "city", "country_id",
    "create_date", "write_date", "active",
]


class CRMOps:
    """High-level operations for the Odoo CRM pipeline (``crm.lead``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "crm.lead"
    STAGE_MODEL = "crm.stage"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_lead(
        self,
        name: str,
        contact_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        expected_revenue: Optional[float] = None,
        **extra: Any,
    ) -> dict:
        """Create a new CRM lead.

        Args:
            name: Lead title / subject.
            contact_name: Contact person name.
            email: Contact email.
            phone: Contact phone.
            expected_revenue: Estimated deal value.
            **extra: Additional ``crm.lead`` field values.

        Returns:
            The newly created lead record.
        """
        values: dict[str, Any] = {"name": name, "type": "lead"}
        if contact_name:
            values["contact_name"] = contact_name
        if email:
            values["email_from"] = email
        if phone:
            values["phone"] = phone
        if expected_revenue is not None:
            values["expected_revenue"] = expected_revenue
        values.update(extra)

        lead_id = self.client.create(self.MODEL, values)
        logger.info("Created lead %r → id=%d", name, lead_id)
        return self._read_lead(lead_id)

    def create_opportunity(
        self,
        name: str,
        partner_id: int,
        expected_revenue: Optional[float] = None,
        probability: Optional[float] = None,
        **extra: Any,
    ) -> dict:
        """Create a new CRM opportunity (linked to a partner).

        Args:
            name: Opportunity title.
            partner_id: Associated customer/partner ID.
            expected_revenue: Estimated deal value.
            probability: Win probability (0–100).
            **extra: Additional ``crm.lead`` field values.

        Returns:
            The newly created opportunity record.
        """
        values: dict[str, Any] = {
            "name": name,
            "type": "opportunity",
            "partner_id": partner_id,
        }
        if expected_revenue is not None:
            values["expected_revenue"] = expected_revenue
        if probability is not None:
            values["probability"] = probability
        values.update(extra)

        opp_id = self.client.create(self.MODEL, values)
        logger.info("Created opportunity %r → id=%d", name, opp_id)
        return self._read_lead(opp_id)

    # ── Pipeline queries ─────────────────────────────────────────────

    def get_pipeline(
        self,
        user_id: Optional[int] = None,
        team_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get the active opportunity pipeline.

        Args:
            user_id: Filter by salesperson.
            team_id: Filter by sales team.
            limit: Max results.

        Returns:
            List of opportunity records, grouped by stage.
        """
        domain: list = [["type", "=", "opportunity"], ["active", "=", True]]
        if user_id:
            domain.append(["user_id", "=", user_id])
        if team_id:
            domain.append(["team_id", "=", team_id])

        return self.client.search_read(
            self.MODEL, domain, fields=_LEAD_LIST_FIELDS,
            limit=limit, order="stage_id asc, priority desc",
        )

    # ── Stage management ─────────────────────────────────────────────

    def move_stage(self, lead_id: int, stage_id: int) -> dict:
        """Move a lead/opportunity to a different pipeline stage.

        Args:
            lead_id: The lead/opportunity ID.
            stage_id: Target ``crm.stage`` ID.

        Returns:
            The updated lead record.
        """
        self.client.write(self.MODEL, lead_id, {"stage_id": stage_id})
        logger.info("Moved lead id=%d to stage_id=%d", lead_id, stage_id)
        return self._read_lead(lead_id)

    def mark_won(self, lead_id: int) -> dict:
        """Mark an opportunity as Won.

        Args:
            lead_id: The opportunity ID.

        Returns:
            The updated lead record.
        """
        self.client.execute(self.MODEL, "action_set_won_rainbowman", [lead_id])
        logger.info("Marked opportunity id=%d as WON", lead_id)
        return self._read_lead(lead_id)

    def mark_lost(self, lead_id: int, lost_reason_id: Optional[int] = None) -> dict:
        """Mark an opportunity as Lost.

        Args:
            lead_id: The opportunity ID.
            lost_reason_id: Optional ``crm.lost.reason`` ID.

        Returns:
            The updated lead record.
        """
        # Odoo's lost action deactivates the record
        values: dict[str, Any] = {"active": False}
        if lost_reason_id:
            values["lost_reason_id"] = lost_reason_id
        self.client.write(self.MODEL, lead_id, values)
        logger.info("Marked opportunity id=%d as LOST", lead_id)
        return self._read_lead(lead_id)

    def get_stages(self) -> list[dict]:
        """Get all CRM pipeline stages.

        Returns:
            List of stage records, ordered by sequence.
        """
        return self.client.search_read(
            self.STAGE_MODEL, [],
            fields=["id", "name", "sequence", "is_won", "fold"],
            order="sequence asc",
        )

    # ── Helpers ──────────────────────────────────────────────────────

    def _read_lead(self, lead_id: int) -> dict:
        """Read a single lead/opportunity by ID."""
        records = self.client.read(
            self.MODEL, lead_id, fields=_LEAD_DETAIL_FIELDS,
        )
        return records[0] if records else {}
