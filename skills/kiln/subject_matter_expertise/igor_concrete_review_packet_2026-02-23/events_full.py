"""Event types for multi-device manufacturing operations.

Extends the event type catalog for SLA, laser, and CNC operations.
These integrate with kiln's EventBus when forge is connected to
the main system.
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any


class ForgeEventType(str, enum.Enum):
    """All event types emitted by the Forge multi-device system.

    Values follow the ``category.action`` convention used by kiln's
    :class:`~kiln.events.EventType`, with device-specific prefixes
    to avoid collisions.
    """

    # -- SLA / Resin printer events ----------------------------------------

    SLA_PRINT_STARTED = "sla.print_started"
    SLA_PRINT_COMPLETED = "sla.print_completed"
    SLA_PRINT_FAILED = "sla.print_failed"
    SLA_PRINT_CANCELLED = "sla.print_cancelled"
    SLA_LAYER_COMPLETED = "sla.layer_completed"
    SLA_EXPOSURE_WARNING = "sla.exposure_warning"
    SLA_VAT_LOW = "sla.vat_low"
    SLA_VAT_EMPTY = "sla.vat_empty"
    SLA_RESIN_TEMP_WARNING = "sla.resin_temp_warning"
    SLA_UV_LIFESPAN_WARNING = "sla.uv_lifespan_warning"
    SLA_WASH_NEEDED = "sla.wash_needed"
    SLA_CURE_NEEDED = "sla.cure_needed"

    # -- Laser cutter / engraver events ------------------------------------

    LASER_CUT_STARTED = "laser.cut_started"
    LASER_CUT_COMPLETED = "laser.cut_completed"
    LASER_CUT_FAILED = "laser.cut_failed"
    LASER_CUT_CANCELLED = "laser.cut_cancelled"
    LASER_MATERIAL_BLOCKED = "laser.material_blocked"
    LASER_VENTILATION_FAILED = "laser.ventilation_failed"
    LASER_LID_OPEN = "laser.lid_open"
    LASER_POWER_WARNING = "laser.power_warning"
    LASER_FIRE_RISK = "laser.fire_risk"
    LASER_TUBE_LIFESPAN_WARNING = "laser.tube_lifespan_warning"

    # -- CNC router / mill events ------------------------------------------

    CNC_JOB_STARTED = "cnc.job_started"
    CNC_JOB_COMPLETED = "cnc.job_completed"
    CNC_JOB_FAILED = "cnc.job_failed"
    CNC_JOB_CANCELLED = "cnc.job_cancelled"
    CNC_TOOL_CHANGE = "cnc.tool_change"
    CNC_SPINDLE_OVERLOAD = "cnc.spindle_overload"
    CNC_COOLANT_LOW = "cnc.coolant_low"
    CNC_FEED_OVERRIDE_CHANGED = "cnc.feed_override_changed"
    CNC_PROBE_COMPLETED = "cnc.probe_completed"
    CNC_EMERGENCY_STOP = "cnc.emergency_stop"
    CNC_TOOL_BREAKAGE_DETECTED = "cnc.tool_breakage_detected"

    # -- Structural concrete printer events -------------------------------

    CONCRETE_PRINT_STARTED = "concrete.print_started"
    CONCRETE_PRINT_COMPLETED = "concrete.print_completed"
    CONCRETE_PRINT_FAILED = "concrete.print_failed"
    CONCRETE_PRINT_CANCELLED = "concrete.print_cancelled"
    CONCRETE_PUMP_PRESSURE_LOW = "concrete.pump_pressure_low"
    CONCRETE_FLOW_INTERRUPTED = "concrete.flow_interrupted"
    CONCRETE_WEATHER_UNSAFE = "concrete.weather_unsafe"
    CONCRETE_EMERGENCY_STOP = "concrete.emergency_stop"

    # -- Cross-device events -----------------------------------------------

    DEVICE_REGISTERED = "device.registered"
    DEVICE_DISCONNECTED = "device.disconnected"
    DEVICE_ERROR = "device.error"
    DEVICE_STALL_DETECTED = "device.stall_detected"
    MULTI_JOB_STARTED = "multi_job.started"
    MULTI_JOB_COMPLETED = "multi_job.completed"
    MULTI_JOB_FAILED = "multi_job.failed"
    SUBJOB_STARTED = "subjob.started"
    SUBJOB_COMPLETED = "subjob.completed"
    SUBJOB_FAILED = "subjob.failed"

    # -- Calibration / surface probing events ---------------------------------

    CALIBRATION_NEEDED = "calibration.needed"
    CALIBRATION_TRIGGERED = "calibration.triggered"
    CALIBRATION_COMPLETED = "calibration.completed"
    CALIBRATION_FAILED = "calibration.failed"

    # -- Cloud sync events -------------------------------------------------

    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"


@dataclass
class Event:
    """A single event in the forge multi-device system.

    :param event_type: The :class:`ForgeEventType` that occurred.
    :param timestamp: Unix timestamp (defaults to ``time.time()``).
    :param data: Arbitrary payload dict for event-specific details.
    :param source: Originating component (e.g. ``"sla:formlabs_form3"``).
    :param device_type: High-level device category —
        ``"sla"``, ``"laser"``, ``"cnc"``, or ``"multi"`` for
        cross-device orchestration events.
    """

    event_type: ForgeEventType
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    device_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary.

        Enum values are converted to their string representation so
        the result can be passed directly to ``json.dumps``.
        """
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "source": self.source,
            "device_type": self.device_type,
        }
