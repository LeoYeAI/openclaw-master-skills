"""
Fleet management operations for Odoo.

Covers ``fleet.vehicle``, ``fleet.vehicle.odometer``, and
``fleet.vehicle.log.services`` for vehicle tracking, mileage logging,
and service/maintenance records.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_VEHICLE_LIST_FIELDS = [
    "id", "name", "model_id", "license_plate",
    "driver_id", "state_id", "company_id",
    "odometer", "active",
]

_VEHICLE_DETAIL_FIELDS = _VEHICLE_LIST_FIELDS + [
    "tag_ids", "vin_sn", "color",
    "acquisition_date", "contract_date_start",
    "model_year", "seats", "doors", "fuel_type",
    "transmission", "horsepower",
]

_ODOMETER_FIELDS = [
    "id", "vehicle_id", "date", "value",
    "unit", "driver_id",
]

_SERVICE_LOG_FIELDS = [
    "id", "vehicle_id", "service_type_id", "date",
    "amount", "description", "vendor_id",
    "odometer", "state",
]


class FleetOps:
    """High-level operations for Odoo fleet management.

    Manages vehicles, odometer readings, and service logs.

    Note:
        In Odoo 19, ``fleet.vehicle.cost`` was removed. Costs are
        tracked via ``fleet.vehicle.log.services`` instead.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    VEHICLE_MODEL = "fleet.vehicle"
    ODOMETER_MODEL = "fleet.vehicle.odometer"
    SERVICE_MODEL = "fleet.vehicle.log.services"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Vehicle CRUD ─────────────────────────────────────────────────

    def create_vehicle(
        self,
        model_id: int,
        license_plate: Optional[str] = None,
        driver_id: Optional[int] = None,
        color: Optional[str] = None,
        vin_sn: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a new vehicle record.

        Args:
            model_id: Vehicle model ID (``fleet.vehicle.model``).
            license_plate: Vehicle license/registration plate.
            driver_id: Assigned driver's partner ID.
            color: Vehicle colour.
            vin_sn: Vehicle Identification Number.
            **extra: Additional ``fleet.vehicle`` field values.

        Returns:
            The newly created vehicle record.
        """
        values: dict[str, Any] = {"model_id": model_id}
        if license_plate:
            values["license_plate"] = license_plate
        if driver_id:
            values["driver_id"] = driver_id
        if color:
            values["color"] = color
        if vin_sn:
            values["vin_sn"] = vin_sn
        values.update(extra)

        vehicle_id = self.client.create(self.VEHICLE_MODEL, values)
        logger.info("Created vehicle with model_id=%d → id=%d", model_id, vehicle_id)
        return self._read_vehicle(vehicle_id)

    def get_vehicles(self, limit: int = 50) -> list[dict]:
        """Get all active vehicles.

        Args:
            limit: Max results.

        Returns:
            List of vehicle records.
        """
        return self.client.search_read(
            self.VEHICLE_MODEL,
            [["active", "=", True]],
            fields=_VEHICLE_LIST_FIELDS, limit=limit,
            order="name asc",
        )

    def search_vehicles(
        self,
        query: Optional[str] = None,
        driver_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search vehicles by name, plate, or driver.

        Args:
            query: Text to search in vehicle name or license plate.
            driver_id: Filter by assigned driver.
            limit: Max results.

        Returns:
            List of matching vehicle records.
        """
        domain: list = [["active", "=", True]]
        if query:
            domain = [
                "&", ["active", "=", True],
                "|",
                ["name", "ilike", query],
                ["license_plate", "ilike", query],
            ]
        if driver_id:
            domain.append(["driver_id", "=", driver_id])

        return self.client.search_read(
            self.VEHICLE_MODEL, domain,
            fields=_VEHICLE_LIST_FIELDS, limit=limit,
        )

    # ── Odometer ─────────────────────────────────────────────────────

    def log_odometer(
        self,
        vehicle_id: int,
        value: float,
        date: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Log an odometer reading for a vehicle.

        Args:
            vehicle_id: The vehicle ID.
            value: Odometer value (total mileage/km).
            date: Reading date as ``YYYY-MM-DD``. Defaults to today.
            **extra: Additional field values.

        Returns:
            The newly created odometer record.
        """
        values: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "value": value,
        }
        if date:
            values["date"] = date
        values.update(extra)

        odo_id = self.client.create(self.ODOMETER_MODEL, values)
        logger.info("Logged odometer %.0f for vehicle=%d → id=%d", value, vehicle_id, odo_id)
        records = self.client.read(self.ODOMETER_MODEL, odo_id, fields=_ODOMETER_FIELDS)
        return records[0] if records else {}

    # ── Service logs (replaces fleet.vehicle.cost in Odoo 19) ────────

    def get_vehicle_costs(
        self,
        vehicle_id: int,
        limit: int = 50,
    ) -> list[dict]:
        """Get service/cost records for a vehicle.

        In Odoo 19+, vehicle costs are tracked via service logs.

        Args:
            vehicle_id: The vehicle ID.
            limit: Max results.

        Returns:
            List of service log records (newest first).
        """
        return self.client.search_read(
            self.SERVICE_MODEL,
            [["vehicle_id", "=", vehicle_id]],
            fields=_SERVICE_LOG_FIELDS, limit=limit,
            order="date desc",
        )

    def create_service_log(
        self,
        vehicle_id: int,
        service_type_id: int,
        amount: float = 0.0,
        date: Optional[str] = None,
        description: Optional[str] = None,
        vendor_id: Optional[int] = None,
        **extra: Any,
    ) -> dict:
        """Log a service/maintenance record for a vehicle.

        Args:
            vehicle_id: The vehicle ID.
            service_type_id: Service type ID (``fleet.service.type``).
            amount: Service cost.
            date: Service date as ``YYYY-MM-DD``.
            description: Service description/notes.
            vendor_id: Service provider partner ID.
            **extra: Additional field values.

        Returns:
            The newly created service log record.
        """
        values: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "service_type_id": service_type_id,
            "amount": amount,
        }
        if date:
            values["date"] = date
        if description:
            values["description"] = description
        if vendor_id:
            values["vendor_id"] = vendor_id
        values.update(extra)

        service_id = self.client.create(self.SERVICE_MODEL, values)
        logger.info("Created service log for vehicle=%d → id=%d", vehicle_id, service_id)
        records = self.client.read(self.SERVICE_MODEL, service_id, fields=_SERVICE_LOG_FIELDS)
        return records[0] if records else {}

    def get_service_types(self) -> list[dict]:
        """Get all available fleet service types.

        Returns:
            List of service type records.
        """
        return self.client.search_read(
            "fleet.service.type", [],
            fields=["id", "name"],
            order="name asc",
        )

    def get_vehicle_models(self, brand_id: Optional[int] = None) -> list[dict]:
        """Get available vehicle models, optionally filtered by brand.

        Args:
            brand_id: Filter by brand (``fleet.vehicle.model.brand``).

        Returns:
            List of vehicle model records.
        """
        domain: list = []
        if brand_id:
            domain.append(["brand_id", "=", brand_id])

        return self.client.search_read(
            "fleet.vehicle.model", domain,
            fields=["id", "name", "brand_id"],
            order="name asc",
        )

    def get_vehicle_brands(self) -> list[dict]:
        """Get all vehicle brands.

        Returns:
            List of brand records.
        """
        return self.client.search_read(
            "fleet.vehicle.model.brand", [],
            fields=["id", "name"],
            order="name asc",
        )

    # ── Internal helpers ─────────────────────────────────────────────

    def _read_vehicle(self, vehicle_id: int) -> dict:
        """Read a single vehicle by ID."""
        records = self.client.read(
            self.VEHICLE_MODEL, vehicle_id, fields=_VEHICLE_DETAIL_FIELDS,
        )
        return records[0] if records else {}
