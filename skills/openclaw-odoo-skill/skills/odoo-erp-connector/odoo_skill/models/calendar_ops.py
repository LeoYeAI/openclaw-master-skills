"""
Calendar event operations for Odoo ``calendar.event``.

Provides creation, search, update, and deletion of calendar events
including attendee management and date-range queries.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_EVENT_LIST_FIELDS = [
    "id", "name", "start", "stop", "allday",
    "user_id", "partner_ids", "location",
    "description", "privacy", "show_as",
]

_EVENT_DETAIL_FIELDS = _EVENT_LIST_FIELDS + [
    "attendee_ids", "recurrency", "duration",
    "alarm_ids", "categ_ids",
]


class CalendarOps:
    """High-level operations for Odoo calendar events (``calendar.event``).

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    MODEL = "calendar.event"
    ATTENDEE_MODEL = "calendar.attendee"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Create ───────────────────────────────────────────────────────

    def create_event(
        self,
        name: str,
        start: str,
        stop: Optional[str] = None,
        allday: bool = False,
        location: Optional[str] = None,
        description: Optional[str] = None,
        partner_ids: Optional[list[int]] = None,
        **extra: Any,
    ) -> dict:
        """Create a calendar event.

        Args:
            name: Event title/subject.
            start: Start datetime as ``YYYY-MM-DD HH:MM:SS`` or
                ``YYYY-MM-DD`` for all-day events.
            stop: End datetime. If ``None``, defaults to 1 hour after start
                (or same day for all-day events).
            allday: Whether this is an all-day event.
            location: Event location.
            description: Event description.
            partner_ids: List of partner IDs to invite as attendees.
            **extra: Additional ``calendar.event`` field values.

        Returns:
            The newly created event record.
        """
        values: dict[str, Any] = {
            "name": name,
            "start": start,
            "allday": allday,
        }

        if stop:
            values["stop"] = stop
        elif allday:
            # All-day: stop = same day
            values["stop"] = start
        else:
            # Default: 1 hour duration
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                stop_dt = start_dt + timedelta(hours=1)
                values["stop"] = stop_dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                values["stop"] = start

        if location:
            values["location"] = location
        if description:
            values["description"] = description
        if partner_ids:
            values["partner_ids"] = [(6, 0, partner_ids)]
        values.update(extra)

        event_id = self.client.create(self.MODEL, values)
        logger.info("Created calendar event %r → id=%d", name, event_id)
        return self._read_event(event_id)

    # ── Read ─────────────────────────────────────────────────────────

    def get_events(
        self,
        limit: int = 50,
        upcoming_only: bool = True,
    ) -> list[dict]:
        """Get calendar events.

        Args:
            limit: Max results.
            upcoming_only: If ``True``, only return future events.

        Returns:
            List of event records, ordered by start date.
        """
        domain: list = []
        if upcoming_only:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            domain.append(["start", ">=", now])

        return self.client.search_read(
            self.MODEL, domain,
            fields=_EVENT_LIST_FIELDS, limit=limit,
            order="start asc",
        )

    def search_events_by_date(
        self,
        date_from: str,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search events within a date range.

        Args:
            date_from: Start date as ``YYYY-MM-DD`` or ``YYYY-MM-DD HH:MM:SS``.
            date_to: End date (inclusive). Defaults to end of ``date_from`` day.
            limit: Max results.

        Returns:
            List of events within the date range.
        """
        if not date_to:
            # Default to end of the given day
            date_to = date_from.split(" ")[0] + " 23:59:59"

        # Normalise date_from to include time if not present
        if len(date_from) == 10:
            date_from = date_from + " 00:00:00"

        domain: list = [
            ["start", "<=", date_to],
            ["stop", ">=", date_from],
        ]

        return self.client.search_read(
            self.MODEL, domain,
            fields=_EVENT_LIST_FIELDS, limit=limit,
            order="start asc",
        )

    # ── Update ───────────────────────────────────────────────────────

    def update_event(self, event_id: int, **values: Any) -> dict:
        """Update a calendar event.

        Args:
            event_id: The event ID.
            **values: Field values to update (e.g. ``name``, ``start``,
                ``stop``, ``location``).

        Returns:
            The updated event record.
        """
        self.client.write(self.MODEL, event_id, values)
        logger.info("Updated calendar event id=%d: %s", event_id, list(values.keys()))
        return self._read_event(event_id)

    # ── Delete ───────────────────────────────────────────────────────

    def delete_event(self, event_id: int) -> bool:
        """Delete a calendar event.

        Args:
            event_id: The event ID.

        Returns:
            ``True`` on success.
        """
        result = self.client.unlink(self.MODEL, event_id)
        logger.info("Deleted calendar event id=%d", event_id)
        return result

    # ── Internal helpers ─────────────────────────────────────────────

    def _read_event(self, event_id: int) -> dict:
        """Read a single event by ID."""
        records = self.client.read(
            self.MODEL, event_id, fields=_EVENT_DETAIL_FIELDS,
        )
        return records[0] if records else {}
