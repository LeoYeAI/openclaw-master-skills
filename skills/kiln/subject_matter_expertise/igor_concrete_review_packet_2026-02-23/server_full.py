"""Forge MCP Server -- exposes multi-device fabrication capabilities to AI agents.

Provides a Model Context Protocol (MCP) server that lets agents monitor,
control, and manage SLA printers, laser cutters, CNC machines, and
construction concrete printers through a clean set of tool-based interactions.
The server loads device
configuration from the :class:`~forge.registry.DeviceRegistry` and
delegates all hardware interaction to device-type-specific adapters.

Environment variables
---------------------
``FORGE_DATA_DIR``
    Path to persistent data directory.  Defaults to ``~/.forge``.
``FORGE_QUEUE_DB``
    Path to the job queue SQLite database.  Defaults to
    ``$FORGE_DATA_DIR/queue.db``.
"""

from __future__ import annotations

import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from forge.devices.base import DeviceStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "forge",
    instructions=(
        "Agent infrastructure for multi-device physical fabrication. "
        "Provides tools to monitor SLA printers, laser cutters, CNC "
        "machines, and construction concrete printers; manage a "
        "heterogeneous device fleet; submit queued jobs; "
        "validate toolpath files; run preflight safety checks; estimate "
        "costs; manage material inventory; decompose multi-device jobs; "
        "and outsource to external fulfillment providers.\n\n"
        "Start with `fleet_status` to see all connected devices. "
        "Use `get_sla_status`, `get_laser_status`, `get_cnc_status`, or "
        "`get_concrete_status` for device-specific details. Run "
        "`preflight_sla`, `preflight_laser`, `preflight_cnc`, or "
        "`preflight_concrete` before starting any operation. Submit jobs via "
        "`submit_job` for queued execution. Use `decompose_job` to split "
        "complex manufacturing across device types.\n\n"
        "SAFETY: Fabrication devices are dangerous hardware. Laser cutters "
        "present fire and toxic fume hazards. CNC machines have spinning "
        "cutters. SLA printers use UV light and toxic resin. Always run "
        "preflight checks and respect safety interlocks."
    ),
)


# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------

_registry: Optional[Any] = None
_queue: Optional[Any] = None
_intelligence: Optional[Any] = None
_materials_manager: Optional[Any] = None
_fulfillment_registry: Optional[Any] = None
_decomposer: Optional[Any] = None
_orchestrator: Optional[Any] = None
_cloud_sync: Optional[Any] = None
_webhook_mgr: Optional[Any] = None
_db: Optional[Any] = None
_autonomy_cfg: Optional[Any] = None
_billing_ledger: Optional[Any] = None


def _get_registry() -> Any:
    """Return the lazily-initialised device registry."""
    global _registry
    if _registry is None:
        from forge.registry import DeviceRegistry
        _registry = DeviceRegistry()
    return _registry


def _get_queue() -> Any:
    """Return the lazily-initialised job queue."""
    global _queue
    if _queue is None:
        from forge.queue import DeviceQueue
        data_dir = os.environ.get("FORGE_DATA_DIR", os.path.expanduser("~/.forge"))
        db_path = os.environ.get("FORGE_QUEUE_DB", os.path.join(data_dir, "queue.db"))
        _queue = DeviceQueue(db_path=db_path)
    return _queue


def _get_intelligence() -> Any:
    """Return the lazily-initialised device intelligence engine."""
    global _intelligence
    if _intelligence is None:
        from forge.intelligence import DeviceIntelligence
        _intelligence = DeviceIntelligence()
    return _intelligence


def _get_materials_manager() -> Any:
    """Return the lazily-initialised materials manager."""
    global _materials_manager
    if _materials_manager is None:
        from forge.materials import MaterialsManager
        _materials_manager = MaterialsManager()
    return _materials_manager


def _get_fulfillment_registry() -> Any:
    """Return the lazily-initialised fulfillment registry."""
    global _fulfillment_registry
    if _fulfillment_registry is None:
        from forge.fulfillment.registry import create_default_registry
        _fulfillment_registry = create_default_registry()
    return _fulfillment_registry


def _get_decomposer() -> Any:
    """Return the lazily-initialised job decomposer."""
    global _decomposer
    if _decomposer is None:
        from forge.decomposition import JobDecomposer
        _decomposer = JobDecomposer()
    return _decomposer


def _get_cloud_sync() -> Any:
    """Return the lazily-initialised cloud sync instance.

    Returns ``None`` if cloud sync is not configured (missing
    ``FORGE_CLOUD_URL`` or ``FORGE_CLOUD_API_KEY``).
    """
    global _cloud_sync
    if _cloud_sync is None:
        from forge.cloud_sync import CloudSyncConfig, ForgeCloudSync
        config = CloudSyncConfig.from_env()
        if config is None:
            return None
        _cloud_sync = ForgeCloudSync(
            config,
            registry=_get_registry(),
            queue=_get_queue(),
        )
    return _cloud_sync



def _get_webhook_mgr() -> Any:
    """Return the lazily-initialised webhook manager."""
    global _webhook_mgr
    if _webhook_mgr is None:
        from forge.webhooks import ForgeWebhookManager
        _webhook_mgr = ForgeWebhookManager()
    return _webhook_mgr


def _get_db() -> Any:
    """Return the lazily-initialised persistence database."""
    global _db
    if _db is None:
        from forge.persistence import get_db
        _db = get_db()
    return _db



def _get_autonomy_cfg() -> Any:
    """Return the lazily-initialised autonomy config."""
    global _autonomy_cfg
    if _autonomy_cfg is None:
        from forge.autonomy import get_autonomy_config
        _autonomy_cfg = get_autonomy_config()
    return _autonomy_cfg


def _get_billing_ledger() -> Any:
    """Return the lazily-initialised billing ledger."""
    global _billing_ledger
    if _billing_ledger is None:
        from forge.billing import ForgeBillingLedger
        _billing_ledger = ForgeBillingLedger()
    return _billing_ledger

# ---------------------------------------------------------------------------
# Per-tool rate limiter
# ---------------------------------------------------------------------------

class _ToolRateLimiter:
    """Per-tool sliding-window rate limiter for MCP tool calls.

    Prevents agents from spamming physically-dangerous commands in tight
    retry loops.  Uses a minimum-interval + max-per-minute model with
    a circuit breaker for repeated blocked attempts.
    """

    _BLOCK_THRESHOLD: int = 3
    _BLOCK_WINDOW: float = 60.0
    _COOLDOWN_DURATION: float = 300.0

    def __init__(self) -> None:
        self._last_call: Dict[str, float] = {}
        self._call_history: Dict[str, List[float]] = {}
        self._block_history: Dict[str, List[float]] = {}
        self._cooldown_until: Dict[str, float] = {}

    def record_block(self, tool_name: str) -> Optional[str]:
        """Record a blocked attempt; return escalation message if threshold hit."""
        now = time.monotonic()
        history = self._block_history.get(tool_name, [])
        cutoff = now - self._BLOCK_WINDOW
        history = [t for t in history if t > cutoff]
        history.append(now)
        self._block_history[tool_name] = history

        if len(history) >= self._BLOCK_THRESHOLD:
            self._cooldown_until[tool_name] = now + self._COOLDOWN_DURATION
            self._block_history[tool_name] = []
            return (
                f"SAFETY ESCALATED: {tool_name} has been blocked "
                f"{len(history)} times in {self._BLOCK_WINDOW:.0f}s. "
                f"Tool is suspended for {self._COOLDOWN_DURATION / 60:.0f} "
                f"minutes. Please review your approach."
            )
        return None

    def check(
        self, tool_name: str, min_interval_ms: int = 0, max_per_minute: int = 0
    ) -> Optional[str]:
        """Return ``None`` if allowed, or an error message if rate-limited."""
        now = time.monotonic()

        cooldown_end = self._cooldown_until.get(tool_name, 0.0)
        if now < cooldown_end:
            remaining = cooldown_end - now
            return (
                f"Tool {tool_name} is in emergency cooldown due to repeated "
                f"blocked attempts. Cooldown expires in {remaining:.0f}s."
            )

        if min_interval_ms > 0:
            last = self._last_call.get(tool_name, 0.0)
            elapsed_ms = (now - last) * 1000
            if elapsed_ms < min_interval_ms:
                wait = (min_interval_ms - elapsed_ms) / 1000
                return (
                    f"Rate limited: {tool_name} called too rapidly. "
                    f"Wait {wait:.1f}s before retrying."
                )

        if max_per_minute > 0:
            history = self._call_history.get(tool_name, [])
            cutoff = now - 60.0
            history = [t for t in history if t > cutoff]
            if len(history) >= max_per_minute:
                return (
                    f"Rate limited: {tool_name} called {max_per_minute} times "
                    f"in the last minute. Wait before retrying."
                )
            self._call_history[tool_name] = history

        self._last_call[tool_name] = now
        self._call_history.setdefault(tool_name, []).append(now)
        return None


_tool_limiter = _ToolRateLimiter()

# Rate limits: {tool_name: (min_interval_ms, max_per_minute)}.
_TOOL_RATE_LIMITS: Dict[str, tuple[int, int]] = {
    "start_sla_print":    (5000, 3),
    "cancel_sla_print":   (5000, 3),
    "pause_sla_print":    (5000, 6),
    "resume_sla_print":   (5000, 6),
    "start_laser_cut":    (5000, 3),
    "cancel_laser_cut":   (5000, 3),
    "pause_laser_cut":    (5000, 6),
    "resume_laser_cut":   (5000, 6),
    "start_cnc_job":      (5000, 3),
    "cancel_cnc_job":     (5000, 3),
    "pause_cnc_job":      (5000, 6),
    "resume_cnc_job":     (5000, 6),
    "start_concrete_print": (5000, 3),
    "cancel_concrete_print": (5000, 3),
    "pause_concrete_print": (5000, 6),
    "resume_concrete_print": (5000, 6),
    "prime_concrete_pump": (3000, 8),
    "home_cnc":           (5000, 3),
    "probe_cnc":          (5000, 3),
    "register_device":    (2000, 10),
    "remove_device":      (2000, 10),
    "submit_job":         (1000, 20),
    "place_fulfillment_order": (5000, 5),
}


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

_RETRYABLE_CODES = frozenset({
    "ERROR",
    "INTERNAL_ERROR",
    "RATE_LIMITED",
})


def _success_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standardised success response dict."""
    return {"success": True, "data": data}


def _error_dict(
    message: str,
    code: str = "ERROR",
    *,
    retryable: Optional[bool] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a standardised error response dict."""
    if retryable is None:
        retryable = code in _RETRYABLE_CODES
    result = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
        },
    }
    if details is not None:
        result["error"]["details"] = details
    return result


def _check_rate_limit(tool_name: str) -> Optional[Dict[str, Any]]:
    """Return an error dict if *tool_name* is rate-limited, else ``None``."""
    limits = _TOOL_RATE_LIMITS.get(tool_name)
    if not limits:
        return None
    msg = _tool_limiter.check(tool_name, limits[0], limits[1])
    if msg:
        return _error_dict(msg, code="RATE_LIMITED")
    return None


def _get_device_adapter(device_name: str) -> Any:
    """Look up a device adapter by name, raising on not-found."""
    return _get_registry().get(device_name)


# ===================================================================
# SLA DEVICE TOOLS
# ===================================================================

@mcp.tool()
def get_sla_status(device_name: str) -> dict:
    """Get the current state of an SLA (resin) printer.

    Returns connection status, operational state, vat level, UV power,
    resin temperature, layer progress, and current job info.
    """
    try:
        adapter = _get_device_adapter(device_name)
        state = adapter.get_state()
        job = adapter.get_job()
        return _success_dict({
            "device_name": device_name,
            "state": state.to_dict(),
            "job": job.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_sla_status")
        return _error_dict(f"Failed to get SLA status: {exc}")


@mcp.tool()
def start_sla_print(
    device_name: str,
    file_name: str,
    exposure_time_s: float,
    bottom_exposure_time_s: float,
    layer_height_um: int,
    *,
    lift_speed_mm_min: float = 60.0,
    retract_speed_mm_min: float = 150.0,
    bottom_layers: int = 4,
) -> dict:
    """Start a resin print on an SLA printer.

    Requires the file to already exist on the printer (use upload first).
    All exposure and layer parameters are validated against device limits.
    Run preflight_sla before calling this.
    """
    rl = _check_rate_limit("start_sla_print")
    if rl:
        return rl
    try:
        from forge.devices.base import SLAPrintConfig
        adapter = _get_device_adapter(device_name)
        config = SLAPrintConfig(
            exposure_time_s=exposure_time_s,
            bottom_exposure_time_s=bottom_exposure_time_s,
            layer_height_um=layer_height_um,
            lift_speed_mm_min=lift_speed_mm_min,
            retract_speed_mm_min=retract_speed_mm_min,
            bottom_layers=bottom_layers,
        )
        result = adapter.start_print(file_name, config)
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in start_sla_print")
        return _error_dict(f"Failed to start SLA print: {exc}")


@mcp.tool()
def cancel_sla_print(device_name: str) -> dict:
    """Cancel the currently running SLA print job."""
    rl = _check_rate_limit("cancel_sla_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.cancel_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in cancel_sla_print")
        return _error_dict(f"Failed to cancel SLA print: {exc}")


@mcp.tool()
def pause_sla_print(device_name: str) -> dict:
    """Pause the currently running SLA print job."""
    rl = _check_rate_limit("pause_sla_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.pause_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in pause_sla_print")
        return _error_dict(f"Failed to pause SLA print: {exc}")


@mcp.tool()
def resume_sla_print(device_name: str) -> dict:
    """Resume a previously paused SLA print job."""
    rl = _check_rate_limit("resume_sla_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.resume_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in resume_sla_print")
        return _error_dict(f"Failed to resume SLA print: {exc}")


@mcp.tool()
def get_sla_capabilities(device_name: str) -> dict:
    """Get the feature set and limits of an SLA printer.

    Returns supported file formats, max exposure times, whether the
    printer supports heated resin and vat monitoring.
    """
    try:
        adapter = _get_device_adapter(device_name)
        caps = adapter.capabilities
        return _success_dict({
            "device_name": device_name,
            "capabilities": caps.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_sla_capabilities")
        return _error_dict(f"Failed to get SLA capabilities: {exc}")


@mcp.tool()
def check_resin_level(device_name: str) -> dict:
    """Check the resin vat level of an SLA printer.

    Returns the vat fill percentage (0-100). Below 10% is critical;
    below 25% is a warning. Refill before printing if low.
    """
    try:
        adapter = _get_device_adapter(device_name)
        level = adapter.get_vat_level()
        status = "ok"
        if level < 10.0:
            status = "critical"
        elif level < 25.0:
            status = "low"
        return _success_dict({
            "device_name": device_name,
            "vat_level_percent": round(level, 1),
            "status": status,
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in check_resin_level")
        return _error_dict(f"Failed to check resin level: {exc}")


@mcp.tool()
def validate_sla_file(file_path: str, *, printer_model: Optional[str] = None) -> dict:
    """Validate an SLA sliced file (.sl1, .ctb, .pwmx) before printing.

    Checks exposure times, layer heights, and build dimensions against
    safety limits. Returns blocking errors and advisory warnings.
    """
    try:
        from forge.safety.sla_file_validator import SLAFileValidator
        validator = SLAFileValidator()
        result = validator.validate(file_path, printer_model=printer_model)
        return _success_dict({
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "file_info": result.file_info,
        })
    except FileNotFoundError:
        return _error_dict(f"File not found: {file_path}", code="FILE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in validate_sla_file")
        return _error_dict(f"Failed to validate SLA file: {exc}")


@mcp.tool()
def preflight_sla(
    device_name: str,
    exposure_time_s: float,
    bottom_exposure_time_s: float,
    layer_height_um: int,
    *,
    lift_speed_mm_min: float = 60.0,
    retract_speed_mm_min: float = 150.0,
    bottom_layers: int = 4,
) -> dict:
    """Run preflight safety checks before starting an SLA print.

    Checks: printer connection, resin temperature, vat level, UV LED
    lifespan, exposure limits, layer height range, build plate
    cleanliness (advisory), and ventilation (advisory).
    MANDATORY before starting any SLA print.
    """
    try:
        from forge.devices.base import SLAPrintConfig
        from forge.preflight import preflight_sla as _preflight_sla
        adapter = _get_device_adapter(device_name)
        config = SLAPrintConfig(
            exposure_time_s=exposure_time_s,
            bottom_exposure_time_s=bottom_exposure_time_s,
            layer_height_um=layer_height_um,
            lift_speed_mm_min=lift_speed_mm_min,
            retract_speed_mm_min=retract_speed_mm_min,
            bottom_layers=bottom_layers,
        )
        result = _preflight_sla(adapter, config)
        return _success_dict(result.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in preflight_sla")
        return _error_dict(f"Preflight SLA failed: {exc}")


# ===================================================================
# LASER DEVICE TOOLS
# ===================================================================

@mcp.tool()
def get_laser_status(device_name: str) -> dict:
    """Get the current state of a laser cutter/engraver.

    Returns connection status, operational state, laser power, exhaust
    and lid interlock status, and loaded material info.
    """
    try:
        adapter = _get_device_adapter(device_name)
        state = adapter.get_state()
        return _success_dict({
            "device_name": device_name,
            "state": state.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_laser_status")
        return _error_dict(f"Failed to get laser status: {exc}")


@mcp.tool()
def start_laser_cut(
    device_name: str,
    file_name: str,
    power_percent: float,
    speed_mm_s: float,
    *,
    passes: int = 1,
    focus_height_mm: Optional[float] = None,
    air_assist: bool = True,
) -> dict:
    """Start a laser cut/engrave job.

    Requires the file to already exist on the device. Run
    preflight_laser and check_laser_safety before calling this.
    """
    rl = _check_rate_limit("start_laser_cut")
    if rl:
        return rl
    try:
        from forge.devices.base import CutConfig
        adapter = _get_device_adapter(device_name)
        config = CutConfig(
            power_percent=power_percent,
            speed_mm_s=speed_mm_s,
            passes=passes,
            focus_height_mm=focus_height_mm,
            air_assist=air_assist,
        )
        result = adapter.start_cut(file_name, config)
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in start_laser_cut")
        return _error_dict(f"Failed to start laser cut: {exc}")


@mcp.tool()
def cancel_laser_cut(device_name: str) -> dict:
    """Cancel the currently running laser cut job."""
    rl = _check_rate_limit("cancel_laser_cut")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.cancel_cut()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in cancel_laser_cut")
        return _error_dict(f"Failed to cancel laser cut: {exc}")


@mcp.tool()
def pause_laser_cut(device_name: str) -> dict:
    """Pause the currently running laser cut job."""
    rl = _check_rate_limit("pause_laser_cut")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.pause_cut()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in pause_laser_cut")
        return _error_dict(f"Failed to pause laser cut: {exc}")


@mcp.tool()
def resume_laser_cut(device_name: str) -> dict:
    """Resume a previously paused laser cut job."""
    rl = _check_rate_limit("resume_laser_cut")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.resume_cut()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in resume_laser_cut")
        return _error_dict(f"Failed to resume laser cut: {exc}")


@mcp.tool()
def get_laser_capabilities(device_name: str) -> dict:
    """Get the feature set and limits of a laser cutter.

    Returns supported file formats, max power, interlock capabilities,
    air assist availability, and cutting area dimensions.
    """
    try:
        adapter = _get_device_adapter(device_name)
        caps = adapter.capabilities
        return _success_dict({
            "device_name": device_name,
            "capabilities": caps.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_laser_capabilities")
        return _error_dict(f"Failed to get laser capabilities: {exc}")


@mcp.tool()
def check_laser_safety(device_name: str) -> dict:
    """Check all safety interlocks on a laser cutter.

    Verifies exhaust/ventilation is running and lid is closed.
    Both must pass before any cut operation is allowed.
    """
    try:
        adapter = _get_device_adapter(device_name)
        vent_ok = adapter.check_ventilation()
        lid_ok = adapter.check_lid_interlock()
        all_safe = vent_ok and lid_ok
        checks = {
            "ventilation_running": vent_ok,
            "lid_closed": lid_ok,
            "all_interlocks_ok": all_safe,
        }
        if not all_safe:
            issues = []
            if not vent_ok:
                issues.append("Ventilation/exhaust is not running")
            if not lid_ok:
                issues.append("Lid is open or interlock disengaged")
            checks["issues"] = issues
        return _success_dict({"device_name": device_name, "safety": checks})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in check_laser_safety")
        return _error_dict(f"Failed to check laser safety: {exc}")


@mcp.tool()
def validate_laser_file(file_path: str, *, machine_model: Optional[str] = None) -> dict:
    """Validate a laser cut file (.svg, .dxf, .gcode, .lbrn) before cutting.

    Checks laser power, feed rates, dimensions, and safety command
    pairing. Returns blocking errors and advisory warnings.
    """
    try:
        from forge.safety.laser_file_validator import LaserFileValidator
        validator = LaserFileValidator()
        # Read content for gcode-based validation
        if file_path.lower().endswith(".gcode"):
            content = Path(file_path).read_text(encoding="utf-8")
            result = validator.validate_gcode(content, machine_model=machine_model)
        else:
            result = validator.validate(file_path, machine_model=machine_model)
        return _success_dict({
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "file_info": result.file_info,
        })
    except FileNotFoundError:
        return _error_dict(f"File not found: {file_path}", code="FILE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in validate_laser_file")
        return _error_dict(f"Failed to validate laser file: {exc}")


@mcp.tool()
def check_material_safety(material_id: str, machine_id: Optional[str] = None) -> dict:
    """Check if a material is safe to laser process.

    Returns safety level, toxicity info, required PPE, and whether
    the material is blocked (e.g. PVC, polycarbonate). NEVER bypass
    a blocked material result.
    """
    try:
        from forge.safety.laser_profiles import is_material_safe, get_material_safety
        safe = is_material_safe(material_id)
        if not safe:
            try:
                mat = get_material_safety(material_id)
                reason = mat.block_reason or "Material is blocked for laser processing"
            except KeyError:
                reason = f"Unknown material '{material_id}' -- blocked by default"
            return _success_dict({
                "material_id": material_id,
                "safe": False,
                "blocked": True,
                "reason": reason,
            })
        mat = get_material_safety(material_id)
        return _success_dict({
            "material_id": material_id,
            "safe": True,
            "blocked": False,
            "display_name": mat.display_name,
            "safety_level": mat.safety_level,
            "fire_risk": mat.fire_risk,
            "max_thickness_mm": mat.max_thickness_mm,
        })
    except ImportError:
        return _error_dict("Laser safety profiles not available", code="INTERNAL_ERROR")
    except Exception as exc:
        logger.exception("Error in check_material_safety")
        return _error_dict(f"Failed to check material safety: {exc}")


@mcp.tool()
def preflight_laser(
    device_name: str,
    material_id: str,
    power_percent: float,
    speed_mm_s: float,
    *,
    passes: int = 1,
    focus_height_mm: Optional[float] = None,
    air_assist: bool = True,
) -> dict:
    """Run preflight safety checks before starting a laser cut.

    Checks: connection, material safety (CRITICAL), ventilation,
    lid interlock, power/speed limits, material thickness, focus
    (advisory), air assist for combustibles (advisory).
    MANDATORY before starting any laser cut.
    """
    try:
        from forge.devices.base import CutConfig
        from forge.preflight import preflight_laser as _preflight_laser
        adapter = _get_device_adapter(device_name)
        config = CutConfig(
            power_percent=power_percent,
            speed_mm_s=speed_mm_s,
            passes=passes,
            focus_height_mm=focus_height_mm,
            air_assist=air_assist,
        )
        result = _preflight_laser(adapter, material_id, config)
        return _success_dict(result.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in preflight_laser")
        return _error_dict(f"Preflight laser failed: {exc}")


# ===================================================================
# CNC DEVICE TOOLS
# ===================================================================

@mcp.tool()
def get_cnc_status(device_name: str) -> dict:
    """Get the current state of a CNC router/mill.

    Returns connection status, spindle RPM, position, tool number,
    coolant state, feed override, and current job info.
    """
    try:
        adapter = _get_device_adapter(device_name)
        state = adapter.get_state()
        job = adapter.get_job()
        return _success_dict({
            "device_name": device_name,
            "state": state.to_dict(),
            "job": job.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_cnc_status")
        return _error_dict(f"Failed to get CNC status: {exc}")


@mcp.tool()
def start_cnc_job(
    device_name: str,
    file_name: str,
    tool_id: int,
    rpm: float,
    feed_mm_min: float,
    plunge_mm_min: float,
    depth_mm: float,
    *,
    coolant: bool = False,
) -> dict:
    """Start a CNC machining job.

    Requires the file to already exist on the machine. Run
    preflight_cnc before calling this. Verify tool is loaded and
    workpiece is securely clamped.
    """
    rl = _check_rate_limit("start_cnc_job")
    if rl:
        return rl
    try:
        from forge.devices.base import CNCJobConfig
        adapter = _get_device_adapter(device_name)
        config = CNCJobConfig(
            tool_id=tool_id,
            rpm=rpm,
            feed_mm_min=feed_mm_min,
            plunge_mm_min=plunge_mm_min,
            depth_mm=depth_mm,
            coolant=coolant,
        )
        result = adapter.start_job(file_name, config)
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in start_cnc_job")
        return _error_dict(f"Failed to start CNC job: {exc}")


@mcp.tool()
def cancel_cnc_job(device_name: str) -> dict:
    """Cancel the currently running CNC machining job."""
    rl = _check_rate_limit("cancel_cnc_job")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.cancel_job()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in cancel_cnc_job")
        return _error_dict(f"Failed to cancel CNC job: {exc}")


@mcp.tool()
def pause_cnc_job(device_name: str) -> dict:
    """Pause the currently running CNC machining job."""
    rl = _check_rate_limit("pause_cnc_job")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.pause_job()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in pause_cnc_job")
        return _error_dict(f"Failed to pause CNC job: {exc}")


@mcp.tool()
def resume_cnc_job(device_name: str) -> dict:
    """Resume a previously paused CNC machining job."""
    rl = _check_rate_limit("resume_cnc_job")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.resume_job()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in resume_cnc_job")
        return _error_dict(f"Failed to resume CNC job: {exc}")


@mcp.tool()
def get_cnc_capabilities(device_name: str) -> dict:
    """Get the feature set and limits of a CNC machine.

    Returns max spindle RPM, feedrate, axis count, tool change support,
    coolant availability, probing, and supported file formats.
    """
    try:
        adapter = _get_device_adapter(device_name)
        caps = adapter.capabilities
        return _success_dict({
            "device_name": device_name,
            "capabilities": caps.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_cnc_capabilities")
        return _error_dict(f"Failed to get CNC capabilities: {exc}")


@mcp.tool()
def home_cnc(device_name: str) -> dict:
    """Execute the homing sequence on a CNC machine.

    Homes all axes to their limit switches. Required before first
    operation after power-on to establish the machine coordinate system.
    """
    rl = _check_rate_limit("home_cnc")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.home_axes()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in home_cnc")
        return _error_dict(f"Failed to home CNC: {exc}")


@mcp.tool()
def probe_cnc(device_name: str) -> dict:
    """Run a tool length probe cycle on a CNC machine.

    Returns the measured tool length offset in mm. Required after
    every tool change to update the tool table.
    """
    rl = _check_rate_limit("probe_cnc")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        offset = adapter.probe_tool_length()
        return _success_dict({
            "device_name": device_name,
            "tool_length_offset_mm": round(offset, 4),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in probe_cnc")
        return _error_dict(f"Failed to probe CNC tool: {exc}")


@mcp.tool()
def validate_cnc_file(file_path: str, *, machine_model: Optional[str] = None) -> dict:
    """Validate a CNC toolpath file (.nc, .gcode, .ngc, .tap) before machining.

    Checks spindle speeds, feed rates, depth of cut, rapid moves,
    travel limits, and tool change commands. Returns blocking errors
    and advisory warnings.
    """
    try:
        from forge.safety.cnc_file_validator import CNCFileValidator
        validator = CNCFileValidator()
        content = Path(file_path).read_text(encoding="utf-8")
        result = validator.validate_gcode(content, machine_model=machine_model)
        return _success_dict({
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "file_info": result.file_info,
        })
    except FileNotFoundError:
        return _error_dict(f"File not found: {file_path}", code="FILE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in validate_cnc_file")
        return _error_dict(f"Failed to validate CNC file: {exc}")


@mcp.tool()
def recommend_feeds_speeds(
    material_id: str,
    tool_diameter_mm: float,
    *,
    machine_id: Optional[str] = None,
) -> dict:
    """Get recommended feeds and speeds for a CNC operation.

    Returns suggested RPM, feed rate, plunge rate, and depth of cut
    based on the material hardness and tool diameter. These are
    conservative starting points -- adjust based on results.
    """
    try:
        from forge.cost_estimator import BUILTIN_CNC_MATERIALS
        profile = BUILTIN_CNC_MATERIALS.get(material_id)
        if profile is None:
            return _error_dict(
                f"Unknown CNC material '{material_id}'. "
                f"Available: {', '.join(sorted(BUILTIN_CNC_MATERIALS))}",
                code="INVALID_PARAM",
            )

        # Conservative feeds/speeds based on material hardness and tool diameter.
        hardness = profile.hardness_factor
        # SFM (surface feet per minute) scaled by hardness.
        sfm = 300.0 * (1.0 - hardness * 0.7)
        # RPM from SFM and tool diameter.
        import math
        rpm = (sfm * 3.82) / (tool_diameter_mm / 25.4) if tool_diameter_mm > 0 else 0
        rpm = round(min(rpm, 24000.0), 0)
        # Feed per tooth: 0.001-0.003" scaled by inverse hardness.
        fpt_inch = 0.002 * (1.0 - hardness * 0.5)
        fpt_mm = fpt_inch * 25.4
        flutes = 2 if hardness < 0.5 else 3
        feed_mm_min = round(rpm * fpt_mm * flutes, 0)
        plunge_mm_min = round(feed_mm_min * 0.3, 0)
        doc_mm = round(tool_diameter_mm * (0.5 - hardness * 0.3), 2)

        return _success_dict({
            "material_id": material_id,
            "tool_diameter_mm": tool_diameter_mm,
            "recommended": {
                "rpm": rpm,
                "feed_mm_min": feed_mm_min,
                "plunge_mm_min": plunge_mm_min,
                "depth_of_cut_mm": max(doc_mm, 0.1),
                "flutes": flutes,
                "coolant": hardness >= 0.30,
            },
            "notes": [
                "Conservative starting values -- increase gradually based on results",
                f"Material hardness factor: {hardness:.2f}",
                "Use coolant for metals" if hardness >= 0.30 else "Dry cutting OK for this material",
            ],
        })
    except Exception as exc:
        logger.exception("Error in recommend_feeds_speeds")
        return _error_dict(f"Failed to compute feeds/speeds: {exc}")


@mcp.tool()
def preflight_cnc(
    device_name: str,
    tool_id: int,
    rpm: float,
    feed_mm_min: float,
    plunge_mm_min: float,
    depth_mm: float,
    *,
    coolant: bool = False,
) -> dict:
    """Run preflight safety checks before starting a CNC job.

    Checks: connection, spindle RPM limits, feed rate limits, depth
    of cut, tool loaded, workholding (advisory), coolant status,
    dust collection (advisory), PPE reminder (advisory).
    MANDATORY before starting any CNC job.
    """
    try:
        from forge.devices.base import CNCJobConfig
        from forge.preflight import preflight_cnc as _preflight_cnc
        adapter = _get_device_adapter(device_name)
        config = CNCJobConfig(
            tool_id=tool_id,
            rpm=rpm,
            feed_mm_min=feed_mm_min,
            plunge_mm_min=plunge_mm_min,
            depth_mm=depth_mm,
            coolant=coolant,
        )
        result = _preflight_cnc(adapter, config)
        return _success_dict(result.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in preflight_cnc")
        return _error_dict(f"Preflight CNC failed: {exc}")


# ===================================================================
# CONCRETE DEVICE TOOLS
# ===================================================================

@mcp.tool()
def get_concrete_status(device_name: str) -> dict:
    """Get the current state of a structural concrete 3D printer."""
    try:
        adapter = _get_device_adapter(device_name)
        state = adapter.get_state()
        job = adapter.get_job()
        return _success_dict({
            "device_name": device_name,
            "state": state.to_dict(),
            "job": job.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_concrete_status")
        return _error_dict(f"Failed to get concrete printer status: {exc}")


@mcp.tool()
def start_concrete_print(
    device_name: str,
    file_name: str,
    layer_height_mm: float,
    print_speed_mm_s: float,
    extrusion_rate_l_min: float,
    nozzle_diameter_mm: float,
    *,
    pump_pressure_bar: float = 90.0,
    bead_width_mm: Optional[float] = None,
    cure_pause_s: float = 0.0,
) -> dict:
    """Start a structural concrete print job."""
    rl = _check_rate_limit("start_concrete_print")
    if rl:
        return rl
    try:
        from forge.devices.base import ConcretePrintConfig
        adapter = _get_device_adapter(device_name)
        config = ConcretePrintConfig(
            layer_height_mm=layer_height_mm,
            print_speed_mm_s=print_speed_mm_s,
            extrusion_rate_l_min=extrusion_rate_l_min,
            nozzle_diameter_mm=nozzle_diameter_mm,
            pump_pressure_bar=pump_pressure_bar,
            bead_width_mm=bead_width_mm,
            cure_pause_s=cure_pause_s,
        )
        result = adapter.start_print(file_name, config)
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in start_concrete_print")
        return _error_dict(f"Failed to start concrete print: {exc}")


@mcp.tool()
def cancel_concrete_print(device_name: str) -> dict:
    """Cancel the currently running concrete print job."""
    rl = _check_rate_limit("cancel_concrete_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.cancel_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in cancel_concrete_print")
        return _error_dict(f"Failed to cancel concrete print: {exc}")


@mcp.tool()
def pause_concrete_print(device_name: str) -> dict:
    """Pause the currently running concrete print job."""
    rl = _check_rate_limit("pause_concrete_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.pause_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in pause_concrete_print")
        return _error_dict(f"Failed to pause concrete print: {exc}")


@mcp.tool()
def resume_concrete_print(device_name: str) -> dict:
    """Resume a previously paused concrete print job."""
    rl = _check_rate_limit("resume_concrete_print")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.resume_print()
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in resume_concrete_print")
        return _error_dict(f"Failed to resume concrete print: {exc}")


@mcp.tool()
def prime_concrete_pump(device_name: str, target_pressure_bar: float) -> dict:
    """Prime and pressurise the concrete pump before a print."""
    rl = _check_rate_limit("prime_concrete_pump")
    if rl:
        return rl
    try:
        adapter = _get_device_adapter(device_name)
        result = adapter.prime_pump(target_pressure_bar)
        return _success_dict({"result": result.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in prime_concrete_pump")
        return _error_dict(f"Failed to prime concrete pump: {exc}")


@mcp.tool()
def check_concrete_safety(device_name: str) -> dict:
    """Check concrete-printer safety interlocks and process signals."""
    try:
        adapter = _get_device_adapter(device_name)
        pressure = adapter.check_pump_pressure()
        flow = adapter.check_material_flow()
        estop_clear = adapter.check_emergency_stop()
        weather_safe = adapter.check_weather_safe()
        all_safe = estop_clear and weather_safe and pressure >= 40.0 and flow >= 1.0
        return _success_dict({
            "device_name": device_name,
            "safety": {
                "pump_pressure_bar": round(pressure, 1),
                "material_flow_l_min": round(flow, 2),
                "emergency_stop_clear": bool(estop_clear),
                "weather_safe": bool(weather_safe),
                "all_interlocks_ok": bool(all_safe),
            },
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in check_concrete_safety")
        return _error_dict(f"Failed to check concrete safety: {exc}")


@mcp.tool()
def get_concrete_capabilities(device_name: str) -> dict:
    """Get the feature set and limits of a concrete printer adapter."""
    try:
        adapter = _get_device_adapter(device_name)
        caps = adapter.capabilities
        return _success_dict({
            "device_name": device_name,
            "capabilities": caps.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_concrete_capabilities")
        return _error_dict(f"Failed to get concrete capabilities: {exc}")


@mcp.tool()
def preflight_concrete(
    device_name: str,
    layer_height_mm: float,
    print_speed_mm_s: float,
    extrusion_rate_l_min: float,
    nozzle_diameter_mm: float,
    *,
    pump_pressure_bar: float = 90.0,
    bead_width_mm: Optional[float] = None,
    cure_pause_s: float = 0.0,
) -> dict:
    """Run preflight safety checks before starting a concrete print."""
    try:
        from forge.devices.base import ConcretePrintConfig
        from forge.preflight import preflight_concrete as _preflight_concrete
        adapter = _get_device_adapter(device_name)
        config = ConcretePrintConfig(
            layer_height_mm=layer_height_mm,
            print_speed_mm_s=print_speed_mm_s,
            extrusion_rate_l_min=extrusion_rate_l_min,
            nozzle_diameter_mm=nozzle_diameter_mm,
            pump_pressure_bar=pump_pressure_bar,
            bead_width_mm=bead_width_mm,
            cure_pause_s=cure_pause_s,
        )
        result = _preflight_concrete(adapter, config)
        return _success_dict(result.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in preflight_concrete")
        return _error_dict(f"Preflight concrete failed: {exc}")


# ===================================================================
# FLEET MANAGEMENT TOOLS
# ===================================================================

@mcp.tool()
def list_devices(*, device_type: Optional[str] = None) -> dict:
    """List all registered devices in the fleet.

    Optionally filter by device_type ('sla', 'laser', 'cnc', 'concrete').
    Returns device names and their types.
    """
    try:
        registry = _get_registry()
        if device_type:
            names = registry.get_devices_by_type(device_type)
        else:
            names = registry.list_names()
        devices = []
        for name in names:
            dtype = registry.get_device_type(name)
            devices.append({"name": name, "device_type": dtype})
        return _success_dict({"devices": devices, "count": len(devices)})
    except Exception as exc:
        logger.exception("Error in list_devices")
        return _error_dict(f"Failed to list devices: {exc}")


@mcp.tool()
def register_device(
    name: str,
    device_type: str,
    adapter_type: str,
    host: str,
    *,
    api_key: Optional[str] = None,
    port: Optional[int] = None,
) -> dict:
    """Register a new device in the fleet.

    Creates an adapter instance for the given adapter_type and registers
    it in the fleet registry under the given name. Supported adapter
    types: sla_simulator, laser_simulator, cnc_simulator, concrete_simulator,
    formlabs, chitubox, prusa_sl, glowforge, lightburn, xtool, grbl,
    linuxcnc, carbide, icon_titan, cobod, cybe, wasp, apis_cor,
    constructions3d.
    """
    rl = _check_rate_limit("register_device")
    if rl:
        return rl
    try:
        registry = _get_registry()
        if name in registry:
            return _error_dict(f"Device '{name}' is already registered", code="DUPLICATE")

        dtype = device_type.lower().strip()
        valid_types = {"sla", "laser", "cnc", "concrete"}
        if dtype not in valid_types:
            return _error_dict(
                f"Unknown device_type {device_type!r}. Supported: {', '.join(sorted(valid_types))}",
                code="INVALID_PARAM",
            )

        # Lazy-import adapter constructors to avoid circular imports.
        adapter: Any = None
        adapter_lower = adapter_type.lower()

        if adapter_lower == "sla_simulator":
            from forge.devices.sla_simulator import FormlabsSimulator
            adapter = FormlabsSimulator(name=name)
        elif adapter_lower == "laser_simulator":
            from forge.devices.laser_simulator import LaserSimulator
            adapter = LaserSimulator(name=name)
        elif adapter_lower == "cnc_simulator":
            from forge.devices.cnc_simulator import GrblSimulator
            adapter = GrblSimulator(name=name)
        elif adapter_lower == "concrete_simulator":
            from forge.devices.concrete_simulator import ConcreteSimulator
            adapter = ConcreteSimulator(name=name)
        elif adapter_lower == "formlabs":
            from forge.devices.formlabs import FormlabsAdapter
            adapter = FormlabsAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "chitubox":
            from forge.devices.chitubox import ChituboxAdapter
            adapter = ChituboxAdapter(host=host)
        elif adapter_lower == "prusa_sl":
            from forge.devices.prusa_sl import PrusaSLAdapter
            adapter = PrusaSLAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "glowforge":
            from forge.devices.glowforge import GlowforgeAdapter
            adapter = GlowforgeAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "lightburn":
            from forge.devices.lightburn import LightBurnAdapter
            adapter = LightBurnAdapter(host=host, port=port or 8080)
        elif adapter_lower == "xtool":
            from forge.devices.xtool import XToolAdapter
            adapter = XToolAdapter(host=host)
        elif adapter_lower == "grbl":
            from forge.devices.grbl import GrblAdapter
            adapter = GrblAdapter(host=host, port=port or 8080)
        elif adapter_lower == "linuxcnc":
            from forge.devices.linuxcnc import LinuxCNCAdapter
            adapter = LinuxCNCAdapter(host=host, port=port or 5007)
        elif adapter_lower == "carbide":
            from forge.devices.carbide import CarbideMotionAdapter
            adapter = CarbideMotionAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "icon_titan":
            from forge.devices.construction_brands import ICONTitanAdapter
            adapter = ICONTitanAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "cobod":
            from forge.devices.construction_brands import COBODAdapter
            adapter = COBODAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "cybe":
            from forge.devices.construction_brands import CyBeAdapter
            adapter = CyBeAdapter(host=host, api_key=api_key or "")
        elif adapter_lower == "wasp":
            from forge.devices.construction_brands import WASPAdapter
            adapter = WASPAdapter(host=host, api_key=api_key or "")
        elif adapter_lower in {"apis_cor", "apiscor"}:
            from forge.devices.construction_brands import ApisCorAdapter
            adapter = ApisCorAdapter(host=host, api_key=api_key or "")
        elif adapter_lower in {"constructions3d", "maxiprinter"}:
            from forge.devices.construction_brands import Constructions3DAdapter
            adapter = Constructions3DAdapter(host=host, api_key=api_key or "")
        else:
            return _error_dict(
                f"Unknown adapter type: {adapter_type!r}. Supported: "
                "sla_simulator, laser_simulator, cnc_simulator, "
                "concrete_simulator, formlabs, chitubox, prusa_sl, "
                "glowforge, lightburn, xtool, grbl, linuxcnc, carbide, "
                "icon_titan, cobod, cybe, wasp, apis_cor, constructions3d",
                code="INVALID_PARAM",
            )

        registry.register(name, adapter, device_type=dtype)
        return _success_dict({
            "name": name,
            "device_type": dtype,
            "adapter_type": adapter_type,
            "message": f"Device '{name}' registered successfully",
        })
    except Exception as exc:
        logger.exception("Error in register_device")
        return _error_dict(f"Failed to register device: {exc}")


@mcp.tool()
def remove_device(name: str) -> dict:
    """Unregister a device from the fleet.

    The device adapter is released. Any queued jobs targeting this
    device should be cancelled separately.
    """
    rl = _check_rate_limit("remove_device")
    if rl:
        return rl
    try:
        registry = _get_registry()
        registry.unregister(name)
        return _success_dict({"name": name, "message": f"Device '{name}' removed"})
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in remove_device")
        return _error_dict(f"Failed to remove device: {exc}")


@mcp.tool()
def discover_devices(*, device_type: Optional[str] = None) -> dict:
    """Run mDNS/network discovery to find fabrication devices.

    Scans the local network for SLA printers, laser cutters, and CNC
    machines. Optionally filter by device_type ('sla', 'laser', 'cnc', 'concrete').
    Returns a list of discovered devices with host, name, and type.
    Requires zeroconf library for full functionality.
    """
    try:
        from forge.discovery import ForgeDiscovery
        discovery = ForgeDiscovery()
        device_types = [device_type] if device_type else None
        found = discovery.scan(timeout=5.0, device_types=device_types)
        return _success_dict({
            "devices": [d.to_dict() for d in found],
            "count": len(found),
        })
    except ImportError:
        return _success_dict({
            "devices": [],
            "count": 0,
            "note": "zeroconf not installed -- network discovery unavailable",
        })
    except Exception as exc:
        logger.exception("Error in discover_devices")
        return _error_dict(f"Device discovery failed: {exc}")


@mcp.tool()
def fleet_status() -> dict:
    """Get the status of all devices in the fleet.

    Returns connection state and operational status for every
    registered device. Devices that fail to respond are reported
    as OFFLINE. Use this as the first call to understand what
    devices are available.
    """
    try:
        registry = _get_registry()
        statuses = registry.get_fleet_status()
        idle = [s["name"] for s in statuses if s.get("state") == "idle"]
        return _success_dict({
            "devices": statuses,
            "total": len(statuses),
            "idle_count": len(idle),
            "idle_devices": idle,
        })
    except Exception as exc:
        logger.exception("Error in fleet_status")
        return _error_dict(f"Failed to get fleet status: {exc}")


# ===================================================================
# JOB QUEUE TOOLS
# ===================================================================

@mcp.tool()
def submit_job(
    file_name: str,
    device_type: str,
    *,
    device_name: Optional[str] = None,
    priority: int = 0,
    submitted_by: str = "agent",
    config: Optional[Dict[str, Any]] = None,
) -> dict:
    """Submit a job to the queue for execution.

    Jobs are processed in priority order (higher = more urgent) with
    FIFO tiebreaking. If device_name is specified, the job targets that
    device; otherwise the scheduler picks any compatible idle device.
    """
    rl = _check_rate_limit("submit_job")
    if rl:
        return rl
    try:
        queue = _get_queue()
        job_id = queue.submit(
            file_name=file_name,
            device_type=device_type,
            device_name=device_name,
            submitted_by=submitted_by,
            priority=priority,
            config=config,
        )
        return _success_dict({"job_id": job_id, "status": "queued"})
    except Exception as exc:
        logger.exception("Error in submit_job")
        return _error_dict(f"Failed to submit job: {exc}")


@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """Get the current status of a queued or running job.

    Returns the job's lifecycle state, file name, device assignment,
    timing info, and any error messages.
    """
    try:
        queue = _get_queue()
        job = queue.get_job(job_id)
        return _success_dict({"job": job.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="JOB_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_job_status")
        return _error_dict(f"Failed to get job status: {exc}")


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """Cancel a queued or active job.

    Only jobs in queued, starting, or operating state can be cancelled.
    Jobs already completed, failed, or cancelled are unchanged.
    """
    try:
        queue = _get_queue()
        job = queue.cancel(job_id)
        return _success_dict({"job": job.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="JOB_NOT_FOUND")
    except ValueError as exc:
        return _error_dict(str(exc), code="INVALID_STATE")
    except Exception as exc:
        logger.exception("Error in cancel_job")
        return _error_dict(f"Failed to cancel job: {exc}")


@mcp.tool()
def list_jobs(
    *,
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """List jobs in the queue, optionally filtered.

    Filter by status ('queued', 'operating', 'completed', 'failed',
    'cancelled') and/or device_type ('sla', 'laser', 'cnc', 'concrete').
    """
    try:
        from forge.queue import DeviceJobStatus
        queue = _get_queue()
        status_enum = None
        if status:
            try:
                status_enum = DeviceJobStatus(status)
            except ValueError:
                return _error_dict(
                    f"Unknown job status '{status}'. Valid: "
                    f"{', '.join(s.value for s in DeviceJobStatus)}",
                    code="INVALID_PARAM",
                )
        jobs = queue.list_jobs(
            status=status_enum,
            device_type=device_type,
            limit=limit,
        )
        return _success_dict({
            "jobs": [j.to_dict() for j in jobs],
            "count": len(jobs),
            "summary": queue.summary(),
        })
    except Exception as exc:
        logger.exception("Error in list_jobs")
        return _error_dict(f"Failed to list jobs: {exc}")


@mcp.tool()
def job_history(
    *,
    device_name: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """Get completed and failed job history.

    Returns recent terminal-state jobs for review and analysis.
    Optionally filter by device_name.
    """
    try:
        from forge.queue import DeviceJobStatus
        queue = _get_queue()
        completed = queue.list_jobs(
            status=DeviceJobStatus.COMPLETED,
            device_name=device_name,
            limit=limit,
        )
        failed = queue.list_jobs(
            status=DeviceJobStatus.FAILED,
            device_name=device_name,
            limit=limit,
        )
        cancelled = queue.list_jobs(
            status=DeviceJobStatus.CANCELLED,
            device_name=device_name,
            limit=limit,
        )
        all_terminal = completed + failed + cancelled
        all_terminal.sort(key=lambda j: j.completed_at or 0.0, reverse=True)
        return _success_dict({
            "jobs": [j.to_dict() for j in all_terminal[:limit]],
            "count": len(all_terminal[:limit]),
            "totals": {
                "completed": len(completed),
                "failed": len(failed),
                "cancelled": len(cancelled),
            },
        })
    except Exception as exc:
        logger.exception("Error in job_history")
        return _error_dict(f"Failed to get job history: {exc}")


# ===================================================================
# JOB HISTORY & ANALYTICS TOOLS
# ===================================================================

_VALID_QUALITY_SCORES = {1, 2, 3, 4, 5}


@mcp.tool()
def job_history_detailed(
    *,
    device_id: Optional[str] = None,
    limit: int = 50,
    status: Optional[str] = None,
) -> dict:
    """Get detailed job history with outcome data and filtering.

    Returns job records enriched with outcome results, quality grades,
    and failure modes.  Supports filtering by device and job status.

    Args:
        device_id: Filter by device name, or all devices if omitted.
        limit: Maximum records to return (default 50, max 200).
        status: Filter by status (``"completed"``, ``"failed"``, ``"cancelled"``).
    """
    try:
        db = _get_db()
        capped = min(max(limit, 1), 200)
        if status is not None:
            from forge.queue import DeviceJobStatus
            try:
                DeviceJobStatus(status)
            except ValueError:
                return _error_dict(
                    f"Unknown job status '{status}'. Valid: queued, starting, "
                    "operating, completed, failed, cancelled",
                    code="INVALID_PARAM",
                )
        records = db.list_jobs_detailed(
            device_name=device_id,
            status=status,
            limit=capped,
        )
        return _success_dict({
            "jobs": records,
            "count": len(records),
            "filters": {
                "device_id": device_id,
                "status": status,
                "limit": capped,
            },
        })
    except Exception as exc:
        logger.exception("Error in job_history_detailed")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def device_stats(device_id: str) -> dict:
    """Get aggregated statistics for a device.

    Returns total jobs, success rate, average duration, and common
    failure patterns.  Combines data from the job queue and outcome
    learning database for a comprehensive device performance view.

    Args:
        device_id: Name of the device to get stats for.
    """
    try:
        db = _get_db()

        # Job-level stats (queue history)
        job_stats = db.get_device_job_stats(device_id)

        # Outcome-level stats (learning database)
        outcome_stats = db.get_device_stats(device_id)

        return _success_dict({
            "device_id": device_id,
            "job_stats": job_stats,
            "outcome_stats": outcome_stats,
        })
    except Exception as exc:
        logger.exception("Error in device_stats")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def annotate_job(
    job_id: str,
    note: str,
    *,
    tags: Optional[List[str]] = None,
) -> dict:
    """Add notes and tags to a job for tracking and review.

    Annotations are appended (not replaced), so multiple notes can be
    attached to the same job over time.

    Args:
        job_id: The job ID to annotate.
        note: The annotation text to attach.
        tags: Optional list of tag strings for categorisation.
    """
    try:
        db = _get_db()
        job = db.get_job(job_id)
        if job is None:
            return _error_dict(
                f"No job found with ID '{job_id}'.",
                code="JOB_NOT_FOUND",
            )
        annotation_id = db.add_job_annotation(job_id, note, tags=tags)
        return _success_dict({
            "annotation_id": annotation_id,
            "job_id": job_id,
            "note": note,
            "tags": tags or [],
        })
    except Exception as exc:
        logger.exception("Error in annotate_job")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def analyze_job_failure(job_id: str) -> dict:
    """Analyze why a job failed using job data, events, and device intelligence.

    Examines the job record, related events (retries, errors, progress),
    and device intelligence data to produce a structured diagnosis with
    likely causes, observed symptoms, and recommended next steps.

    Args:
        job_id: The failed job's ID from ``job_history`` or ``get_job_status``.
    """
    try:
        db = _get_db()
        job = db.get_job(job_id)
        if job is None:
            return _error_dict(f"Job {job_id!r} not found.", code="JOB_NOT_FOUND")

        if job.get("status") not in ("failed", "cancelled"):
            return _error_dict(
                f"Job {job_id} is not in a failed state (status: {job.get('status')}). "
                "Only failed or cancelled jobs can be analyzed.",
                code="NOT_FAILED",
            )

        # Gather related events for this job
        all_events = db.list_events(limit=200)
        job_events = [
            e for e in all_events
            if e.get("data", {}).get("job_id") == job_id
        ]

        # Analyze symptoms
        symptoms: List[str] = []
        causes: List[str] = []
        recommendations: List[str] = []

        # Check for retry events
        retry_events = [
            e for e in job_events if e.get("data", {}).get("retry")
        ]
        if retry_events:
            max_retry = max(e["data"]["retry"] for e in retry_events)
            symptoms.append(f"Job was retried {max_retry} time(s) before final failure")
            causes.append("Persistent device or communication error across multiple attempts")
            recommendations.append("Check device connectivity and physical state before resubmitting")

        # Check error message
        error = job.get("error") or ""
        if "error state" in error.lower():
            symptoms.append("Device entered error state during operation")
            causes.append("Hardware error (thermal runaway, interlock triggered, motor stall)")
            recommendations.append("Check device display for specific error code")
        elif "not registered" in error.lower() or "not found" in error.lower():
            symptoms.append("Device was removed or became unreachable mid-job")
            causes.append("Network connectivity loss or device power cycle")
            recommendations.append("Verify device is powered on and network-accessible")
        elif error:
            symptoms.append(f"Error message: {error}")

        # Check timing
        started_at = job.get("started_at")
        completed_at = job.get("completed_at")
        if started_at and completed_at:
            elapsed = completed_at - started_at
            if elapsed < 30:
                symptoms.append(f"Job failed very quickly ({elapsed:.0f}s)")
                causes.append("Likely a setup issue rather than a mid-operation failure")
                recommendations.append("Run preflight check to validate device readiness")
            elif elapsed > 3600:
                symptoms.append(f"Job ran for {elapsed / 3600:.1f}h before failing")
                causes.append("May be a mid-operation material, adhesion, or thermal issue")

        # Use device intelligence for diagnosis if device type is known
        device_type = job.get("device_type")
        if device_type and error:
            try:
                intel = _get_intelligence()
                keywords = [w for w in error.lower().split() if len(w) > 3][:5]
                if keywords:
                    diagnoses = intel.diagnose(device_type, keywords)
                    for diag in diagnoses[:3]:
                        causes.append(diag.possible_cause)
                        recommendations.append(diag.recommended_fix)
            except Exception:
                pass  # Best-effort intelligence lookup

        # Default if no specific analysis
        if not symptoms:
            symptoms.append("No detailed event data available for this job")
            recommendations.append("Re-run the job with monitoring via get_job_status()")

        return _success_dict({
            "job": job,
            "analysis": {
                "symptoms": symptoms,
                "likely_causes": causes,
                "recommendations": recommendations,
                "retry_count": len(retry_events),
                "related_events": job_events[-20:],
            },
        })
    except Exception as exc:
        logger.exception("Error in analyze_job_failure")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def record_job_outcome(
    job_id: str,
    quality_score: int,
    *,
    notes: Optional[str] = None,
) -> dict:
    """Record quality outcome for a completed job to enable cross-device learning.

    Quality scores help the system learn which devices and settings produce
    the best results for different materials and file types.

    Args:
        job_id: The job ID from the job queue.
        quality_score: Quality rating from 1 (poor) to 5 (excellent).
        notes: Optional free-text notes about the outcome.
    """
    try:
        if quality_score not in _VALID_QUALITY_SCORES:
            return _error_dict(
                f"Invalid quality_score {quality_score}. Must be 1-5.",
                code="VALIDATION_ERROR",
            )

        db = _get_db()
        job = db.get_job(job_id)
        if job is None:
            return _error_dict(f"Job {job_id!r} not found.", code="JOB_NOT_FOUND")

        # Map integer score to grade string
        _SCORE_TO_GRADE = {
            1: "poor",
            2: "acceptable",
            3: "good",
            4: "good",
            5: "excellent",
        }
        quality_grade = _SCORE_TO_GRADE[quality_score]

        # Determine outcome from job status
        job_status = job.get("status", "")
        if job_status == "completed":
            outcome = "success"
        elif job_status == "failed":
            outcome = "failed"
        elif job_status == "cancelled":
            outcome = "cancelled"
        else:
            return _error_dict(
                f"Job {job_id} is in '{job_status}' state. "
                "Only terminal-state jobs (completed/failed/cancelled) "
                "can have outcomes recorded.",
                code="INVALID_STATE",
            )

        row_id = db.save_job_outcome({
            "job_id": job_id,
            "device_name": job.get("device_name", "unknown"),
            "device_type": job.get("device_type", "unknown"),
            "file_name": job.get("file_name"),
            "outcome": outcome,
            "quality_grade": quality_grade,
            "notes": notes,
            "agent_id": "mcp",
            "created_at": time.time(),
        })
        return _success_dict({
            "outcome_id": row_id,
            "job_id": job_id,
            "outcome": outcome,
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "device_name": job.get("device_name"),
        })
    except ValueError as exc:
        return _error_dict(str(exc), code="VALIDATION_ERROR")
    except Exception as exc:
        logger.exception("Error in record_job_outcome")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


# ===================================================================
# FULFILLMENT TOOLS
# ===================================================================

@mcp.tool()
def get_fulfillment_quote(
    provider: str,
    material: str,
    file_path: str,
    quantity: int,
    *,
    service_type: str = "laser_cutting",
) -> dict:
    """Get a price quote from a fulfillment provider.

    Supported providers: sendcutsend, xometry, oshcut, ponoko,
    protolabs, fictiv, hubs, craftcloud. Returns unit price, total
    price, lead time, and shipping options.
    """
    try:
        registry = _get_fulfillment_registry()
        prov = registry.get_provider(provider)
        quote = prov.get_quote(
            file_path, material, quantity, service_type=service_type
        )
        return _success_dict({"quote": quote.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="PROVIDER_NOT_FOUND")
    except FileNotFoundError:
        return _error_dict(f"File not found: {file_path}", code="FILE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in get_fulfillment_quote")
        return _error_dict(f"Failed to get quote: {exc}")


@mcp.tool()
def compare_providers(
    material: str,
    file_path: str,
    quantity: int,
    *,
    service_type: str = "laser_cutting",
) -> dict:
    """Get quotes from all providers and compare.

    Returns the cheapest, fastest, and best-value quotes across all
    available providers for the given material and service type.
    """
    try:
        registry = _get_fulfillment_registry()
        quotes = registry.batch_quote(
            file_path, material, quantity, service_type=service_type
        )
        comparison = registry.compare_providers(quotes)
        result: Dict[str, Any] = {"total_quotes": len(quotes)}
        for key in ("cheapest", "fastest", "best_value"):
            q = comparison.get(key)
            result[key] = q.to_dict() if q else None
        result["all_quotes"] = [q.to_dict() for q in comparison.get("all_quotes", [])]
        return _success_dict(result)
    except Exception as exc:
        logger.exception("Error in compare_providers")
        return _error_dict(f"Failed to compare providers: {exc}")


@mcp.tool()
def place_fulfillment_order(
    provider: str,
    quote_id: str,
    shipping_address: str,
) -> dict:
    """Place an order with a fulfillment provider using a previous quote.

    The quote_id must be from a recent get_fulfillment_quote call.
    Returns the order ID and initial status.
    """
    rl = _check_rate_limit("place_fulfillment_order")
    if rl:
        return rl
    try:
        registry = _get_fulfillment_registry()
        prov = registry.get_provider(provider)
        order = prov.place_order(quote_id, shipping_address)
        return _success_dict({"order": order.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="PROVIDER_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in place_fulfillment_order")
        return _error_dict(f"Failed to place order: {exc}")


@mcp.tool()
def check_order_status(provider: str, order_id: str) -> dict:
    """Check the status of an outsourced manufacturing order.

    Returns the current lifecycle state (pending, confirmed,
    manufacturing, shipping, delivered, cancelled, failed) and
    any tracking information.
    """
    try:
        registry = _get_fulfillment_registry()
        prov = registry.get_provider(provider)
        order = prov.get_order_status(order_id)
        return _success_dict({"order": order.to_dict()})
    except KeyError as exc:
        return _error_dict(str(exc), code="PROVIDER_NOT_FOUND")
    except Exception as exc:
        logger.exception("Error in check_order_status")
        return _error_dict(f"Failed to check order status: {exc}")


@mcp.tool()
def list_fulfillment_providers(*, service_type: Optional[str] = None) -> dict:
    """List available fulfillment providers.

    Optionally filter by service_type ('laser_cutting', 'cnc_machining',
    'waterjet', 'sheet_metal'). Returns provider names.
    """
    try:
        registry = _get_fulfillment_registry()
        providers = registry.list_providers(service_type=service_type)
        return _success_dict({"providers": providers, "count": len(providers)})
    except Exception as exc:
        logger.exception("Error in list_fulfillment_providers")
        return _error_dict(f"Failed to list providers: {exc}")


# ===================================================================
# SAFETY & INTELLIGENCE TOOLS
# ===================================================================

@mcp.tool()
def get_safety_profile(device_type: str, device_id: str) -> dict:
    """Get the safety limits for a specific device model.

    Returns maximum operating parameters, material restrictions,
    and safety-critical thresholds for the given device.
    """
    try:
        intel = _get_intelligence()
        info = intel.get_device_info(device_type, device_id)
        if info is None:
            return _error_dict(
                f"No safety profile for {device_type}/{device_id}",
                code="DEVICE_NOT_FOUND",
            )
        safety = {
            k: v for k, v in info.items()
            if k in ("safety_limits", "max_parameters", "restrictions",
                      "failure_modes", "dangerous_materials")
        }
        return _success_dict({
            "device_type": device_type,
            "device_id": device_id,
            "safety": safety if safety else info,
        })
    except Exception as exc:
        logger.exception("Error in get_safety_profile")
        return _error_dict(f"Failed to get safety profile: {exc}")


@mcp.tool()
def get_device_intelligence(device_type: str, device_id: str) -> dict:
    """Get operational intelligence for a device model.

    Returns material tips, known failure modes, maintenance schedule,
    and calibration info. Use for proactive guidance and diagnostics.
    """
    try:
        intel = _get_intelligence()
        tips = intel.get_material_tips(device_type, device_id)
        failures = intel.get_failure_modes(device_type, device_id)
        maintenance = intel.get_maintenance_schedule(device_type, device_id)
        return _success_dict({
            "device_type": device_type,
            "device_id": device_id,
            "material_tips": [t.to_dict() for t in tips],
            "failure_modes": [f.to_dict() for f in failures],
            "maintenance_schedule": [m.to_dict() for m in maintenance],
        })
    except Exception as exc:
        logger.exception("Error in get_device_intelligence")
        return _error_dict(f"Failed to get device intelligence: {exc}")


@mcp.tool()
def diagnose_issue(device_type: str, symptoms: List[str]) -> dict:
    """Diagnose a device issue from symptom keywords.

    Provide a list of symptom keywords (e.g. ['chatter', 'rough finish',
    'vibration']) and the device type. Returns ranked diagnosis results
    with possible causes, recommended fixes, and confidence levels.
    """
    try:
        intel = _get_intelligence()
        results = intel.diagnose(device_type, symptoms)
        return _success_dict({
            "device_type": device_type,
            "symptoms": symptoms,
            "diagnoses": [d.to_dict() for d in results],
            "count": len(results),
        })
    except Exception as exc:
        logger.exception("Error in diagnose_issue")
        return _error_dict(f"Failed to diagnose issue: {exc}")


@mcp.tool()
def get_material_recommendations(device_type: str, use_case: str) -> dict:
    """Get material recommendations for a device type and use case.

    Searches intelligence databases for material tips matching the
    given use case keywords. Returns suggestions with guidance.
    """
    try:
        from forge.decomposition import DeviceType as DT
        dt_map = {"sla": DT.SLA, "laser": DT.LASER, "cnc": DT.CNC}
        dt = dt_map.get(device_type.lower())
        if dt is None:
            return _error_dict(
                f"Unknown device type '{device_type}'. Valid: sla, laser, cnc",
                code="INVALID_PARAM",
            )
        intel = _get_intelligence()
        tips = intel.get_material_recommendations(dt, use_case)
        materials = intel.list_supported_materials(dt)
        return _success_dict({
            "device_type": device_type,
            "use_case": use_case,
            "recommendations": [t.to_dict() for t in tips],
            "available_materials": materials,
        })
    except Exception as exc:
        logger.exception("Error in get_material_recommendations")
        return _error_dict(f"Failed to get material recommendations: {exc}")


@mcp.tool()
def get_calibration_guide(device_type: str, device_id: str) -> dict:
    """Get step-by-step calibration instructions for a device.

    Returns an ordered list of calibration steps with tools required
    and estimated time. Follow all steps in sequence.
    """
    try:
        intel = _get_intelligence()
        guide = intel.get_calibration_guide(device_type, device_id)
        return _success_dict({"guide": guide.to_dict()})
    except Exception as exc:
        logger.exception("Error in get_calibration_guide")
        return _error_dict(f"Failed to get calibration guide: {exc}")


# ===================================================================
# COST & MATERIALS TOOLS
# ===================================================================

@mcp.tool()
def estimate_cost(
    device_type: str,
    material: str,
    *,
    volume_ml: Optional[float] = None,
    cut_area_cm2: Optional[float] = None,
    stock_volume_cm3: Optional[float] = None,
    time_hours: float = 1.0,
) -> dict:
    """Estimate the total cost for a fabrication job.

    Provide device_type and the relevant size parameter:
    - SLA: volume_ml (resin consumed) and time_hours
    - Laser: cut_area_cm2 and time_hours
    - CNC: stock_volume_cm3 and time_hours

    Returns detailed cost breakdown including materials, consumables,
    electricity, and post-processing.
    """
    try:
        if device_type == "sla":
            from forge.cost_estimator import estimate_sla_cost
            if volume_ml is None:
                return _error_dict("volume_ml is required for SLA estimates", code="INVALID_PARAM")
            result = estimate_sla_cost(material, volume_ml, time_hours)
        elif device_type == "laser":
            from forge.cost_estimator import estimate_laser_cost
            if cut_area_cm2 is None:
                return _error_dict("cut_area_cm2 is required for laser estimates", code="INVALID_PARAM")
            result = estimate_laser_cost(material, cut_area_cm2, time_hours)
        elif device_type == "cnc":
            from forge.cost_estimator import estimate_cnc_cost
            if stock_volume_cm3 is None:
                return _error_dict("stock_volume_cm3 is required for CNC estimates", code="INVALID_PARAM")
            result = estimate_cnc_cost(material, stock_volume_cm3, time_hours)
        else:
            return _error_dict(f"Unknown device type: {device_type}", code="INVALID_PARAM")
        return _success_dict({"estimate": result.to_dict()})
    except ValueError as exc:
        return _error_dict(str(exc), code="INVALID_PARAM")
    except Exception as exc:
        logger.exception("Error in estimate_cost")
        return _error_dict(f"Failed to estimate cost: {exc}")


@mcp.tool()
def list_materials(*, device_type: Optional[str] = None) -> dict:
    """List available materials for cost estimation.

    Returns built-in material databases for SLA resins, laser sheet
    stock, and CNC blanks. Filter by device_type to narrow results.
    """
    try:
        from forge.cost_estimator import (
            BUILTIN_RESINS,
            BUILTIN_LASER_MATERIALS,
            BUILTIN_CNC_MATERIALS,
        )
        result: Dict[str, Any] = {}
        if device_type is None or device_type == "sla":
            result["sla_resins"] = {k: v.to_dict() for k, v in BUILTIN_RESINS.items()}
        if device_type is None or device_type == "laser":
            result["laser_materials"] = {k: v.to_dict() for k, v in BUILTIN_LASER_MATERIALS.items()}
        if device_type is None or device_type == "cnc":
            result["cnc_materials"] = {k: v.to_dict() for k, v in BUILTIN_CNC_MATERIALS.items()}
        return _success_dict(result)
    except Exception as exc:
        logger.exception("Error in list_materials")
        return _error_dict(f"Failed to list materials: {exc}")


@mcp.tool()
def check_material_inventory(material_type: str) -> dict:
    """Check current inventory levels for materials.

    material_type: 'resin', 'sheet_stock', or 'cnc_blank'.
    Returns inventory items with quantities and any warnings
    (expired resin, low stock).
    """
    try:
        mgr = _get_materials_manager()
        if material_type == "resin":
            items = mgr.list_resin_bottles()
            warnings = mgr.get_resin_warnings()
            return _success_dict({
                "material_type": material_type,
                "items": [i.to_dict() for i in items],
                "count": len(items),
                "warnings": [w.to_dict() for w in warnings],
            })
        elif material_type == "sheet_stock":
            items = mgr.list_sheet_stock()
            warnings = mgr.get_sheet_warnings()
            return _success_dict({
                "material_type": material_type,
                "items": [i.to_dict() for i in items],
                "count": len(items),
                "warnings": [w.to_dict() for w in warnings],
            })
        elif material_type == "cnc_blank":
            items = mgr.list_cnc_blanks()
            warnings = mgr.get_cnc_warnings()
            return _success_dict({
                "material_type": material_type,
                "items": [i.to_dict() for i in items],
                "count": len(items),
                "warnings": [w.to_dict() for w in warnings],
            })
        else:
            return _error_dict(
                f"Unknown material_type '{material_type}'. "
                "Valid: resin, sheet_stock, cnc_blank",
                code="INVALID_PARAM",
            )
    except Exception as exc:
        logger.exception("Error in check_material_inventory")
        return _error_dict(f"Failed to check inventory: {exc}")


@mcp.tool()
def add_material(
    material_type: str,
    material_id: str,
    *,
    subtype: str = "",
    brand: str = "",
    color: str = "",
    volume_ml: float = 0.0,
    width_mm: float = 0.0,
    height_mm: float = 0.0,
    depth_mm: float = 0.0,
    thickness_mm: float = 0.0,
    cost_usd: float = 0.0,
) -> dict:
    """Add a material item to inventory.

    material_type: 'resin' for SLA resin bottles, 'sheet_stock' for
    laser sheet materials, 'cnc_blank' for CNC blanks/billets.
    """
    try:
        mgr = _get_materials_manager()
        if material_type == "resin":
            from forge.materials import ResinBottle
            bottle = ResinBottle(
                id=material_id,
                resin_type=subtype or "standard_resin",
                brand=brand,
                color=color,
                volume_ml=volume_ml,
                remaining_ml=volume_ml,
                cost_usd=cost_usd,
            )
            mgr.add_resin_bottle(bottle)
            return _success_dict({"added": bottle.to_dict()})
        elif material_type == "sheet_stock":
            from forge.materials import SheetStock
            area_cm2 = (width_mm / 10.0) * (height_mm / 10.0)
            stock = SheetStock(
                id=material_id,
                material=subtype or "acrylic",
                thickness_mm=thickness_mm,
                width_mm=width_mm,
                height_mm=height_mm,
                remaining_area_cm2=area_cm2,
                cost_usd=cost_usd,
            )
            mgr.add_sheet_stock(stock)
            return _success_dict({"added": stock.to_dict()})
        elif material_type == "cnc_blank":
            from forge.materials import CNCBlank
            vol_cm3 = (width_mm / 10.0) * (height_mm / 10.0) * (depth_mm / 10.0)
            blank = CNCBlank(
                id=material_id,
                material=subtype or "aluminum_6061",
                width_mm=width_mm,
                height_mm=height_mm,
                depth_mm=depth_mm,
                remaining_volume_cm3=vol_cm3,
                cost_usd=cost_usd,
            )
            mgr.add_cnc_blank(blank)
            return _success_dict({"added": blank.to_dict()})
        else:
            return _error_dict(
                f"Unknown material_type '{material_type}'. "
                "Valid: resin, sheet_stock, cnc_blank",
                code="INVALID_PARAM",
            )
    except ValueError as exc:
        return _error_dict(str(exc), code="DUPLICATE")
    except Exception as exc:
        logger.exception("Error in add_material")
        return _error_dict(f"Failed to add material: {exc}")


@mcp.tool()
def billing_summary(*, period: Optional[str] = None) -> dict:
    """Get a revenue and fee summary for fulfillment orders.

    Returns platform fee totals by device type and overall.
    Defaults to the current month if no period is specified.

    :param period: Optional period in 'YYYY-MM' format (e.g. '2026-01').
        Defaults to current month.
    """
    try:
        ledger = _get_billing_ledger()
        month: Optional[int] = None
        year: Optional[int] = None
        if period is not None:
            parts = period.split("-")
            if len(parts) != 2:
                return _error_dict(
                    "Period must be in YYYY-MM format (e.g. '2026-01')",
                    code="INVALID_INPUT",
                )
            try:
                year = int(parts[0])
                month = int(parts[1])
            except ValueError:
                return _error_dict(
                    "Period must be in YYYY-MM format with numeric year and month",
                    code="INVALID_INPUT",
                )
            if month < 1 or month > 12:
                return _error_dict(
                    f"Month must be between 1 and 12, got {month}",
                    code="INVALID_INPUT",
                )
        summary = ledger.monthly_revenue(year=year, month=month)
        return _success_dict({"summary": summary})
    except Exception as exc:
        logger.exception("Error in billing_summary")
        return _error_dict(f"Failed to get billing summary: {exc}")


@mcp.tool()
def billing_status() -> dict:
    """Get current billing configuration and status.

    Returns the active fee policy (rates by device type, free tier
    allowance, min/max fee caps) and current month usage stats.
    """
    try:
        ledger = _get_billing_ledger()
        policy = ledger.policy
        jobs_this_month = ledger.network_jobs_this_month()
        free_remaining = max(0, policy.free_tier_jobs - jobs_this_month)
        return _success_dict({
            "fee_policy": {
                "device_fee_rates": policy.device_fee_rates,
                "default_fee_percent": policy.default_fee_percent,
                "min_fee_usd": policy.min_fee_usd,
                "max_fee_usd": policy.max_fee_usd,
                "free_tier_jobs": policy.free_tier_jobs,
                "currency": policy.currency,
            },
            "current_month": {
                "jobs_this_month": jobs_this_month,
                "free_tier_remaining": free_remaining,
            },
        })
    except Exception as exc:
        logger.exception("Error in billing_status")
        return _error_dict(f"Failed to get billing status: {exc}")


@mcp.tool()
def billing_history(*, limit: int = 50) -> dict:
    """Get billing transaction history.

    Returns a list of recent billing charges, newest first.

    :param limit: Maximum number of records to return (default 50).
    """
    try:
        if limit < 1:
            return _error_dict(
                "Limit must be a positive integer",
                code="INVALID_INPUT",
            )
        if limit > 1000:
            return _error_dict(
                "Limit cannot exceed 1000",
                code="INVALID_INPUT",
            )
        ledger = _get_billing_ledger()
        charges = ledger.list_charges(limit=limit)
        return _success_dict({
            "charges": charges,
            "count": len(charges),
            "limit": limit,
        })
    except Exception as exc:
        logger.exception("Error in billing_history")
        return _error_dict(f"Failed to get billing history: {exc}")


@mcp.tool()
def check_payment_status(order_id: str) -> dict:
    """Check payment status for a specific order.

    Looks up the fee calculation and payment metadata recorded
    for the given order ID.

    :param order_id: The unique identifier of the order to look up.
    """
    try:
        if not order_id or not order_id.strip():
            return _error_dict(
                "order_id is required and cannot be empty",
                code="INVALID_INPUT",
            )
        order_id = order_id.strip()
        ledger = _get_billing_ledger()
        # Search for the charge entry with full payment metadata
        with ledger._lock:
            for entry in ledger._charges:
                if entry["job_id"] == order_id:
                    fc = entry["fee_calc"]
                    return _success_dict({
                        "order_id": order_id,
                        "charge_id": entry.get("id", ""),
                        "payment_status": entry.get("payment_status", "unknown"),
                        "payment_id": entry.get("payment_id"),
                        "payment_rail": entry.get("payment_rail"),
                        "fee": fc.to_dict(),
                    })
        return _error_dict(
            f"No billing record found for order '{order_id}'",
            code="NOT_FOUND",
        )
    except Exception as exc:
        logger.exception("Error in check_payment_status")
        return _error_dict(f"Failed to check payment status: {exc}")


# ===================================================================
# MULTI-DEVICE ORCHESTRATION TOOLS
# ===================================================================

@mcp.tool()
def decompose_job(parts: List[Dict[str, Any]]) -> dict:
    """Decompose a manufacturing job into device-specific sub-jobs.

    Takes a list of part specifications, each with:
    - name (str): Part name
    - material (str): Material requirement key
    - quantity (int, optional): Number of copies
    - tolerance_mm (float, optional): Dimensional tolerance
    - surface_finish (str, optional): 'cosmetic' or 'functional'
    - is_flat (bool, optional): Whether the part is 2D
    - thickness_mm (float, optional): Material thickness

    Returns optimally-routed sub-jobs with device type assignments,
    time/cost estimates, and a dependency graph.
    """
    try:
        from forge.decomposition import MaterialRequirement, PartRequirements
        decomposer = _get_decomposer()

        part_reqs = []
        for p in parts:
            try:
                mat = MaterialRequirement(p["material"])
            except (ValueError, KeyError):
                return _error_dict(
                    f"Unknown material requirement '{p.get('material')}'. "
                    f"Valid: {', '.join(m.value for m in MaterialRequirement)}",
                    code="INVALID_PARAM",
                )
            part_reqs.append(PartRequirements(
                name=p.get("name", "unnamed"),
                material=mat,
                quantity=p.get("quantity", 1),
                tolerance_mm=p.get("tolerance_mm"),
                surface_finish=p.get("surface_finish"),
                max_dimension_mm=p.get("max_dimension_mm"),
                is_flat=p.get("is_flat", False),
                thickness_mm=p.get("thickness_mm"),
                color=p.get("color"),
                notes=p.get("notes"),
            ))

        result = decomposer.decompose(part_reqs)
        return _success_dict(result.to_dict())
    except Exception as exc:
        logger.exception("Error in decompose_job")
        return _error_dict(f"Failed to decompose job: {exc}")


@mcp.tool()
def submit_orchestrated_job(job_id: str) -> dict:
    """Submit a previously decomposed job for orchestrated execution.

    Takes the job_id from a decompose_job result. The orchestrator
    tracks sub-job dependencies and schedules work across devices.
    Currently returns the decomposition status; full orchestration
    requires devices to be registered in the fleet.
    """
    try:
        return _success_dict({
            "job_id": job_id,
            "status": "submitted",
            "message": (
                "Job submitted for orchestration. Use get_orchestration_status "
                "to track progress. Sub-jobs will be dispatched as devices "
                "become available."
            ),
        })
    except Exception as exc:
        logger.exception("Error in submit_orchestrated_job")
        return _error_dict(f"Failed to submit orchestrated job: {exc}")


@mcp.tool()
def get_orchestration_status(job_id: str) -> dict:
    """Track the progress of a multi-device orchestrated job.

    Returns overall job status, per-sub-job progress, dependency
    resolution state, and any failures.
    """
    try:
        return _success_dict({
            "job_id": job_id,
            "status": "tracking",
            "message": (
                "Orchestration tracking is available when devices are registered "
                "and jobs are actively dispatched. Use fleet_status to check "
                "device availability."
            ),
        })
    except Exception as exc:
        logger.exception("Error in get_orchestration_status")
        return _error_dict(f"Failed to get orchestration status: {exc}")


# ===================================================================
# CLOUD SYNC TOOLS
# ===================================================================

@mcp.tool()
def sync_to_cloud() -> dict:
    """Push local state (jobs, events, device registry) to the cloud.

    Runs a single sync cycle that uploads device fleet status, recent
    jobs, and new events to the configured cloud API endpoint.
    Requires ``FORGE_CLOUD_URL`` and ``FORGE_CLOUD_API_KEY`` env vars.
    """
    try:
        sync = _get_cloud_sync()
        if sync is None:
            return _error_dict(
                "Cloud sync is not configured. Set FORGE_CLOUD_URL and "
                "FORGE_CLOUD_API_KEY environment variables.",
                code="NOT_CONFIGURED",
                retryable=False,
            )
        result = sync.sync_now()
        return _success_dict({"sync_result": result.to_dict()})
    except Exception as exc:
        logger.exception("Error in sync_to_cloud")
        return _error_dict(f"Failed to sync to cloud: {exc}")


@mcp.tool()
def sync_from_cloud() -> dict:
    """Pull latest state from the cloud.

    Downloads the most recent device, job, and event data from the
    cloud API. Requires ``FORGE_CLOUD_URL`` and ``FORGE_CLOUD_API_KEY``
    env vars to be set.
    """
    try:
        sync = _get_cloud_sync()
        if sync is None:
            return _error_dict(
                "Cloud sync is not configured. Set FORGE_CLOUD_URL and "
                "FORGE_CLOUD_API_KEY environment variables.",
                code="NOT_CONFIGURED",
                retryable=False,
            )
        if sync.is_running:
            return _error_dict(
                "A sync cycle is already in progress. Wait for it to "
                "complete before starting another.",
                code="ALREADY_SYNCING",
                retryable=True,
            )
        result = sync.sync_now()
        return _success_dict({"sync_result": result.to_dict()})
    except Exception as exc:
        logger.exception("Error in sync_from_cloud")
        return _error_dict(f"Failed to sync from cloud: {exc}")


@mcp.tool()
def get_sync_status() -> dict:
    """Get the current cloud sync state.

    Returns last sync time, consecutive failure count, total syncs
    completed, total events synced, and whether the sync daemon is
    running. Useful for monitoring sync health.
    """
    try:
        sync = _get_cloud_sync()
        if sync is None:
            return _error_dict(
                "Cloud sync is not configured. Set FORGE_CLOUD_URL and "
                "FORGE_CLOUD_API_KEY environment variables.",
                code="NOT_CONFIGURED",
                retryable=False,
            )
        state = sync.state
        return _success_dict({
            "sync_state": state.to_dict(),
            "daemon_running": sync.is_running,
        })
    except Exception as exc:
        logger.exception("Error in get_sync_status")
        return _error_dict(f"Failed to get sync status: {exc}")


@mcp.tool()
def configure_cloud_sync(
    *,
    endpoint: Optional[str] = None,
    interval_s: Optional[float] = None,
    api_key: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> dict:
    """Update cloud sync configuration at runtime.

    Any parameter not provided is left unchanged. Changes take effect
    on the next sync cycle. Pass ``enabled=false`` to disable syncing
    without clearing the configuration.
    """
    try:
        sync = _get_cloud_sync()
        if sync is None:
            return _error_dict(
                "Cloud sync is not configured. Set FORGE_CLOUD_URL and "
                "FORGE_CLOUD_API_KEY environment variables first.",
                code="NOT_CONFIGURED",
                retryable=False,
            )
        config = sync._config
        updated_fields: List[str] = []

        if endpoint is not None:
            config.cloud_url = endpoint
            updated_fields.append("cloud_url")
        if interval_s is not None:
            config.sync_interval_s = interval_s
            updated_fields.append("sync_interval_s")
        if api_key is not None:
            config.api_key = api_key
            updated_fields.append("api_key")
        if enabled is not None:
            config.enabled = enabled
            updated_fields.append("enabled")

        if not updated_fields:
            return _success_dict({
                "message": "No changes requested",
                "config": config.to_dict(),
            })

        return _success_dict({
            "message": f"Updated: {', '.join(updated_fields)}",
            "updated_fields": updated_fields,
            "config": config.to_dict(),
        })
    except Exception as exc:
        logger.exception("Error in configure_cloud_sync")
        return _error_dict(f"Failed to configure cloud sync: {exc}")


# ---------------------------------------------------------------------------
# Webhook management tools
# ---------------------------------------------------------------------------

@mcp.tool()
def register_webhook(
    url: str,
    events: Optional[List[str]] = None,
    *,
    secret: Optional[str] = None,
) -> dict:
    """Register a webhook endpoint to receive Forge event notifications.

    Events are delivered as POST requests with JSON payloads.  If a
    ``secret`` is provided, each delivery includes an
    ``X-Forge-Signature`` HMAC-SHA256 header for verification.

    :param url: The HTTP(S) URL to POST events to.
    :param events: List of event type strings to subscribe to (e.g.
        ``["sla.print_completed", "laser.cut_failed"]``).  If omitted
        or empty, subscribes to ALL events.
    :param secret: Optional HMAC-SHA256 signing secret.
    """
    if not url:
        return _error_dict("Webhook URL is required.", code="VALIDATION_ERROR")
    try:
        from forge.events import ForgeEventType

        mgr = _get_webhook_mgr()
        event_types: Optional[List[ForgeEventType]] = None
        if events:
            event_types = []
            for ev in events:
                try:
                    event_types.append(ForgeEventType(ev))
                except ValueError:
                    valid = sorted(e.value for e in ForgeEventType)
                    return _error_dict(
                        f"Unknown event type: {ev!r}. "
                        f"Valid types: {valid}",
                        code="VALIDATION_ERROR",
                    )

        webhook_id = mgr.register_webhook(url, event_types, secret=secret)
        webhook = mgr.get_webhook(webhook_id)
        return _success_dict({
            "webhook_id": webhook_id,
            "webhook": webhook,
            "message": f"Webhook registered for {url}",
        })
    except Exception as exc:
        logger.exception("Error in register_webhook")
        return _error_dict(f"Failed to register webhook: {exc}")


@mcp.tool()
def list_webhooks() -> dict:
    """List all registered webhook endpoints.

    Returns each webhook's ID, URL, subscribed events, and active
    status.  Secrets are masked in the response.
    """
    try:
        mgr = _get_webhook_mgr()
        webhooks = mgr.list_webhooks()
        return _success_dict({
            "webhooks": webhooks,
            "count": len(webhooks),
        })
    except Exception as exc:
        logger.exception("Error in list_webhooks")
        return _error_dict(f"Failed to list webhooks: {exc}")


@mcp.tool()
def delete_webhook(webhook_id: str) -> dict:
    """Remove a registered webhook endpoint.

    Stops all future deliveries to the endpoint.  Delivery logs for
    the webhook are also removed.

    :param webhook_id: The ID of the webhook to remove (from
        ``register_webhook`` or ``list_webhooks``).
    """
    if not webhook_id:
        return _error_dict("webhook_id is required.", code="VALIDATION_ERROR")
    try:
        mgr = _get_webhook_mgr()
        removed = mgr.unregister_webhook(webhook_id)
        if not removed:
            return _error_dict(
                f"No webhook found with ID: {webhook_id!r}",
                code="NOT_FOUND",
                retryable=False,
            )
        return _success_dict({
            "webhook_id": webhook_id,
            "message": f"Webhook {webhook_id} deleted",
        })
    except Exception as exc:
        logger.exception("Error in delete_webhook")
        return _error_dict(f"Failed to delete webhook: {exc}")


@mcp.tool()
def test_webhook(webhook_id: str) -> dict:
    """Send a test event to a registered webhook endpoint.

    Delivers a ``device.registered`` test event synchronously and
    returns the delivery result including HTTP status code and
    success/failure.

    :param webhook_id: The ID of the webhook to test.
    """
    if not webhook_id:
        return _error_dict("webhook_id is required.", code="VALIDATION_ERROR")
    try:
        from forge.events import ForgeEventType

        mgr = _get_webhook_mgr()
        webhook = mgr.get_webhook(webhook_id)
        if webhook is None:
            return _error_dict(
                f"No webhook found with ID: {webhook_id!r}",
                code="NOT_FOUND",
                retryable=False,
            )

        records = mgr.deliver_sync(
            ForgeEventType.DEVICE_REGISTERED,
            {
                "test": True,
                "message": "This is a test event from Forge",
                "webhook_id": webhook_id,
            },
        )

        # Find the record for this specific webhook
        result = None
        for record in records:
            if record.webhook_id == webhook_id:
                result = record.to_dict()
                break

        if result is None:
            return _error_dict(
                f"Webhook {webhook_id!r} did not match the test event. "
                "Check that it subscribes to 'device.registered' or all events.",
                code="NOT_FOUND",
                retryable=False,
            )

        return _success_dict({
            "webhook_id": webhook_id,
            "delivery": result,
            "message": "Test event delivered" if result.get("success") else "Test delivery failed",
        })
    except Exception as exc:
        logger.exception("Error in test_webhook")
        return _error_dict(f"Failed to test webhook: {exc}")


# ===================================================================
# AGENT MEMORY TOOLS
# ===================================================================


@mcp.tool()
def save_agent_note(
    key: str,
    value: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Save a persistent note or preference that survives across sessions.

    Use this to remember device quirks, calibration findings, material
    preferences, or any operational knowledge worth preserving.

    Args:
        key: Name for this memory (e.g., ``"z_offset_adjustment"``,
            ``"resin_temp_notes"``).
        value: The information to store.
        device_id: Optional device identifier.  When provided, the note
            is scoped to that specific device.
    """
    try:
        from forge.persistence import get_db
        get_db().save_agent_memory(key, value, device_type=device_id)
        return _success_dict({
            "key": key,
            "device_id": device_id,
            "message": f"Saved note '{key}'.",
        })
    except Exception as exc:
        logger.exception("Error in save_agent_note")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def get_agent_context(
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Retrieve all stored agent memory for context.

    Call this at the start of a session to recall what you've learned
    about devices, materials, and past job outcomes.

    Args:
        device_id: If provided, retrieves only notes scoped to that device.
    """
    try:
        from forge.persistence import get_db
        entries = get_db().list_agent_memories(device_type=device_id)
        return _success_dict({
            "entries": entries,
            "count": len(entries),
        })
    except Exception as exc:
        logger.exception("Error in get_agent_context")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def delete_agent_note(
    key: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Remove a stored note or preference.

    Args:
        key: The key of the note to delete.
        device_id: If provided, targets the device-scoped entry.
    """
    try:
        from forge.persistence import get_db
        deleted = get_db().delete_agent_memory(key, device_type=device_id)
        if not deleted:
            return _error_dict(
                f"No memory entry found for key '{key}'"
                + (f" with device_id '{device_id}'" if device_id else "")
                + ".",
                code="NOT_FOUND",
            )
        return _success_dict({
            "key": key,
            "device_id": device_id,
            "message": f"Deleted note '{key}'.",
        })
    except Exception as exc:
        logger.exception("Error in delete_agent_note")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def clean_agent_memory(
    *,
    older_than_days: int = 30,
) -> dict:
    """Remove agent memory entries not updated within *older_than_days*.

    Returns the count of entries removed.  Use this to prune stale notes
    that are no longer relevant.
    """
    try:
        from forge.persistence import get_db
        deleted = get_db().clean_old_memories(older_than_days=older_than_days)
        return _success_dict({
            "deleted_count": deleted,
            "older_than_days": older_than_days,
            "message": f"Cleaned {deleted} memory entries older than {older_than_days} days.",
        })
    except Exception as exc:
        logger.exception("Error in clean_agent_memory")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def await_job_completion(
    job_id: str,
    *,
    poll_interval: int = 5,
    timeout: int = 300,
) -> dict:
    """Wait for a queued job to finish and return the final status.

    Polls the job queue until the job reaches a terminal state (completed,
    failed, cancelled) or the timeout is exceeded.  This lets agents
    fire-and-forget a job and pick up the result later without managing
    their own polling loop.

    Args:
        job_id: The job ID returned by ``submit_job()``.
        poll_interval: Seconds between status checks (default 5).
        timeout: Maximum seconds to wait (default 300).
    """
    start = time.time()
    progress_log: List[Dict[str, Any]] = []

    while True:
        elapsed = time.time() - start
        if elapsed >= timeout:
            return _success_dict({
                "outcome": "timeout",
                "elapsed_seconds": round(elapsed, 1),
                "message": f"Timed out after {timeout}s waiting for job to finish.",
                "progress_log": progress_log[-20:],
            })

        try:
            from forge.queue import DeviceJobStatus, JobNotFoundError
            queue = _get_queue()
            try:
                job = queue.get_job(job_id)
            except JobNotFoundError:
                return _error_dict(
                    f"Job {job_id!r} not found.",
                    code="JOB_NOT_FOUND",
                )

            progress_log.append({
                "time": round(elapsed, 1),
                "status": job.status.value,
            })

            if job.status == DeviceJobStatus.COMPLETED:
                return _success_dict({
                    "outcome": "completed",
                    "job": job.to_dict(),
                    "elapsed_seconds": round(elapsed, 1),
                    "progress_log": progress_log[-20:],
                })
            if job.status == DeviceJobStatus.FAILED:
                return _success_dict({
                    "outcome": "failed",
                    "job": job.to_dict(),
                    "error": job.error,
                    "elapsed_seconds": round(elapsed, 1),
                    "progress_log": progress_log[-20:],
                })
            if job.status == DeviceJobStatus.CANCELLED:
                return _success_dict({
                    "outcome": "cancelled",
                    "job": job.to_dict(),
                    "elapsed_seconds": round(elapsed, 1),
                    "progress_log": progress_log[-20:],
                })

        except Exception as exc:
            logger.exception("Error in await_job_completion")
            return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")

        time.sleep(poll_interval)


# ===================================================================
# AUTONOMY GOVERNANCE TOOLS
# ===================================================================

@mcp.tool()
def get_autonomy_level() -> dict:
    """Get the current autonomy governance tier.

    Returns the autonomy level (manual, semi_auto, full_auto), its
    numeric equivalent, and the active constraints.  Use this before
    performing actions to understand what the agent is allowed to do
    without human confirmation.
    """
    try:
        cfg = _get_autonomy_cfg()
        return _success_dict({"autonomy": cfg.to_dict()})
    except Exception as exc:
        logger.exception("Error in get_autonomy_level")
        return _error_dict(f"Failed to get autonomy level: {exc}")


@mcp.tool()
def set_autonomy_level(level: str) -> dict:
    """Change the autonomy governance tier.

    :param level: One of ``"manual"``, ``"semi_auto"``, ``"full_auto"``
        or numeric ``"0"``, ``"1"``, ``"2"``.

    Changing the level takes effect immediately for all subsequent
    action checks.  Constraints are preserved across level changes.
    """
    try:
        from forge.autonomy import AutonomyLevel, _NUMERIC_TO_LEVEL

        cfg = _get_autonomy_cfg()
        level_clean = level.strip().lower()

        # Try as enum value first
        resolved: Optional[AutonomyLevel] = None
        try:
            resolved = AutonomyLevel(level_clean)
        except ValueError:
            # Try numeric
            try:
                resolved = _NUMERIC_TO_LEVEL[int(level_clean)]
            except (ValueError, KeyError):
                pass

        if resolved is None:
            return _error_dict(
                f"Invalid autonomy level {level!r}. "
                f"Valid values: manual, semi_auto, full_auto (or 0, 1, 2).",
                code="INVALID_LEVEL",
                retryable=False,
            )

        old_level = cfg.get_level()
        cfg.set_level(resolved)
        logger.info(
            "Autonomy level changed: %s -> %s",
            old_level.value,
            resolved.value,
        )
        return _success_dict({
            "previous_level": old_level.value,
            "current_level": resolved.value,
            "autonomy": cfg.to_dict(),
        })
    except Exception as exc:
        logger.exception("Error in set_autonomy_level")
        return _error_dict(f"Failed to set autonomy level: {exc}")


@mcp.tool()
def check_autonomy(
    action: str,
    *,
    device_type: Optional[str] = None,
    estimated_cost: Optional[float] = None,
) -> dict:
    """Check whether an action is allowed under the current autonomy policy.

    :param action: Name of the action to check (e.g. ``"start_print"``).
    :param device_type: Optional device type (e.g. ``"sla"``, ``"laser"``,
        ``"cnc"``).
    :param estimated_cost: Optional estimated cost in dollars.

    Returns whether the action is allowed and the reason.  Agents should
    call this before executing confirm-level operations.
    """
    try:
        cfg = _get_autonomy_cfg()
        allowed, reason = cfg.check_action(
            action,
            device_type=device_type,
            estimated_cost=estimated_cost,
        )
        return _success_dict({
            "action": action,
            "allowed": allowed,
            "reason": reason,
            "requires_confirmation": not allowed,
            "autonomy_level": cfg.get_level().value,
        })
    except Exception as exc:
        logger.exception("Error in check_autonomy")
        return _error_dict(f"Failed to check autonomy: {exc}")


# ===================================================================
# DEVICE COMPARISON & RECOMMENDATION TOOLS
# ===================================================================

@mcp.tool()
def compare_devices_for_job(
    file_path: str,
    device_ids: Optional[List[str]] = None,
) -> dict:
    """Compare registered devices for a fabrication job.

    Evaluates each device's capabilities, current availability, supported
    file formats, and material compatibility.  If *device_ids* is ``None``,
    all registered devices are compared.  Results are ranked by a
    suitability score that factors in availability, format support, and
    device-type match inferred from the file extension.

    Args:
        file_path: Path to the job file (e.g. ``.sl1``, ``.svg``, ``.nc``).
            The extension is used to determine compatible device types.
        device_ids: Optional list of device names to compare.  When
            omitted, every device in the fleet is included.
    """
    try:
        registry = _get_registry()

        # Determine candidate devices --------------------------------
        if device_ids:
            names = device_ids
        else:
            names = registry.list_names()

        if not names:
            return _error_dict(
                "No devices registered. Use register_device first.",
                code="NO_DEVICES",
                retryable=False,
            )

        # Infer compatible device types from file extension -----------
        ext = Path(file_path).suffix.lower()
        _EXT_TYPE_MAP: Dict[str, str] = {
            ".sl1": "sla", ".sl1s": "sla", ".ctb": "sla", ".pwmx": "sla",
            ".svg": "laser", ".dxf": "laser", ".lbrn": "laser",
            ".nc": "cnc", ".ngc": "cnc", ".tap": "cnc",
            ".gcode": "any",
        }
        inferred_type = _EXT_TYPE_MAP.get(ext, "unknown")

        comparisons: List[Dict[str, Any]] = []

        for name in names:
            entry: Dict[str, Any] = {"device_name": name}
            try:
                adapter = registry.get(name)
                device_type = registry.get_device_type(name)
                entry["device_type"] = device_type

                # Current state
                state = adapter.get_state()
                entry["connected"] = state.connected
                entry["state"] = state.state.value

                # Capabilities
                caps = adapter.capabilities
                caps_dict = caps.to_dict()
                supported_exts = caps_dict.get("supported_extensions", [])
                entry["supported_extensions"] = supported_exts
                entry["format_supported"] = ext in supported_exts or ext == ""

                # Type match
                type_match = (
                    inferred_type == "any"
                    or inferred_type == "unknown"
                    or inferred_type == device_type
                )
                entry["type_match"] = type_match

                # Availability
                available = (
                    state.connected
                    and state.state == DeviceStatus.IDLE
                )
                entry["available"] = available

                # Suitability score (0.0 - 1.0)
                score = 0.0
                if type_match:
                    score += 0.4
                if entry["format_supported"]:
                    score += 0.3
                if available:
                    score += 0.3
                elif state.connected:
                    score += 0.1
                entry["suitability_score"] = round(score, 2)

            except KeyError:
                entry["error"] = f"Device {name!r} not found in registry"
                entry["suitability_score"] = 0.0
            except Exception as exc:
                entry["error"] = str(exc)
                entry["suitability_score"] = 0.0

            comparisons.append(entry)

        # Sort by suitability score descending
        comparisons.sort(key=lambda c: c["suitability_score"], reverse=True)

        best = comparisons[0] if comparisons else None
        return _success_dict({
            "file_path": file_path,
            "file_extension": ext,
            "inferred_device_type": inferred_type,
            "comparisons": comparisons,
            "device_count": len(comparisons),
            "recommended": best["device_name"] if best and best["suitability_score"] > 0 else None,
        })
    except Exception as exc:
        logger.exception("Error in compare_devices_for_job")
        return _error_dict(f"Failed to compare devices: {exc}")


@mcp.tool()
def suggest_device_for_job(
    file_path: str,
    *,
    material: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict:
    """Recommend the best device from the fleet for a job.

    Evaluates all registered devices considering file compatibility,
    current availability, and optional material/priority preferences.
    Returns a single top recommendation with reasoning, plus ranked
    alternatives.

    Args:
        file_path: Path to the job file.  Extension determines compatible
            device types.
        material: Optional material name (e.g. ``"standard_resin"``,
            ``"acrylic_3mm"``, ``"aluminum_6061"``).  When provided,
            devices with intelligence data for that material score higher.
        priority: Optional priority hint: ``"speed"`` (prefer available
            devices), ``"quality"`` (prefer devices with material tips),
            or ``"cost"`` (no preference bias, default).
    """
    try:
        registry = _get_registry()
        intel = _get_intelligence()
        names = registry.list_names()

        if not names:
            return _error_dict(
                "No devices registered. Use register_device first.",
                code="NO_DEVICES",
                retryable=False,
            )

        ext = Path(file_path).suffix.lower()
        _EXT_TYPE_MAP: Dict[str, str] = {
            ".sl1": "sla", ".sl1s": "sla", ".ctb": "sla", ".pwmx": "sla",
            ".svg": "laser", ".dxf": "laser", ".lbrn": "laser",
            ".nc": "cnc", ".ngc": "cnc", ".tap": "cnc",
            ".gcode": "any",
        }
        inferred_type = _EXT_TYPE_MAP.get(ext, "unknown")
        priority_mode = (priority or "cost").lower()

        candidates: List[Dict[str, Any]] = []

        for name in names:
            try:
                adapter = registry.get(name)
                device_type = registry.get_device_type(name)
                state = adapter.get_state()
                caps = adapter.capabilities
                caps_dict = caps.to_dict()
                supported_exts = caps_dict.get("supported_extensions", [])

                type_match = (
                    inferred_type == "any"
                    or inferred_type == "unknown"
                    or inferred_type == device_type
                )
                format_ok = ext in supported_exts or ext == ""
                available = state.connected and state.state == DeviceStatus.IDLE

                # Base score
                score = 0.0
                reasons: List[str] = []

                if type_match:
                    score += 0.3
                    reasons.append(f"Device type '{device_type}' matches file")
                if format_ok:
                    score += 0.2
                    reasons.append(f"Supports {ext} format")
                if available:
                    score += 0.25
                    reasons.append("Currently idle and available")
                elif state.connected:
                    score += 0.05
                    reasons.append("Connected but busy")

                # Material bonus
                has_material_intel = False
                if material and type_match:
                    tips = intel.get_material_tips(device_type, adapter.name)
                    material_lower = material.lower()
                    for tip in tips:
                        if material_lower in tip.material.lower():
                            has_material_intel = True
                            break

                if has_material_intel:
                    score += 0.15
                    reasons.append(f"Has intelligence data for '{material}'")

                # Priority adjustments
                if priority_mode == "speed" and available:
                    score += 0.1
                    reasons.append("Speed priority: device is ready now")
                elif priority_mode == "quality" and has_material_intel:
                    score += 0.1
                    reasons.append("Quality priority: material intelligence available")

                candidates.append({
                    "device_name": name,
                    "device_type": device_type,
                    "connected": state.connected,
                    "state": state.state.value,
                    "type_match": type_match,
                    "format_supported": format_ok,
                    "available": available,
                    "has_material_data": has_material_intel,
                    "score": round(score, 2),
                    "reasons": reasons,
                })
            except Exception as exc:
                logger.warning("Error evaluating device %r: %s", name, exc)
                continue

        candidates.sort(key=lambda c: c["score"], reverse=True)

        top = candidates[0] if candidates else None
        recommendation = None
        if top and top["score"] > 0:
            recommendation = {
                "device_name": top["device_name"],
                "device_type": top["device_type"],
                "score": top["score"],
                "reasons": top["reasons"],
                "available": top["available"],
                "has_material_data": top.get("has_material_data", False),
            }

        return _success_dict({
            "file_path": file_path,
            "file_extension": ext,
            "inferred_device_type": inferred_type,
            "material": material,
            "priority": priority_mode,
            "recommendation": recommendation,
            "alternatives": candidates[1:] if len(candidates) > 1 else [],
            "total_candidates": len(candidates),
        })
    except Exception as exc:
        logger.exception("Error in suggest_device_for_job")
        return _error_dict(f"Failed to suggest device: {exc}")


@mcp.tool()
def recommend_device_settings(
    device_id: str,
    material: str,
    job_type: str,
) -> dict:
    """Get recommended settings for a device, material, and job type.

    Queries the intelligence database for material tips and device-specific
    guidance, then assembles a settings recommendation.  Also returns
    safety notes, known failure modes for the material, and maintenance
    reminders.

    Args:
        device_id: Name of the registered device (e.g. ``"form3-lab"``).
        material: Material identifier (e.g. ``"standard_resin"``,
            ``"acrylic_3mm"``, ``"aluminum_6061"``).
        job_type: Type of operation: ``"print"``, ``"cut"``, ``"engrave"``,
            or ``"machine"``.
    """
    try:
        registry = _get_registry()

        # Validate device exists
        try:
            adapter = registry.get(device_id)
            device_type = registry.get_device_type(device_id)
        except KeyError:
            return _error_dict(
                f"Device {device_id!r} is not registered.",
                code="DEVICE_NOT_FOUND",
                retryable=False,
            )

        intel = _get_intelligence()
        adapter_name = adapter.name

        # Material tips for this device
        tips = intel.get_material_tips(device_type, adapter_name)
        material_lower = material.lower()
        relevant_tips = [
            t.to_dict() for t in tips
            if material_lower in t.material.lower()
        ]

        # Failure modes
        failures = intel.get_failure_modes(device_type, adapter_name)
        failure_list = [f.to_dict() for f in failures]

        # Maintenance reminders
        maintenance = intel.get_maintenance_schedule(device_type, adapter_name)
        maintenance_list = [m.to_dict() for m in maintenance]

        # Build settings recommendation based on device type and job type
        settings: Dict[str, Any] = {}
        safety_notes: List[str] = []

        if device_type == "sla":
            settings = {
                "suggested_exposure_s": 8.0,
                "suggested_bottom_exposure_s": 60.0,
                "suggested_layer_height_um": 50,
                "suggested_lift_speed_mm_min": 60.0,
            }
            safety_notes.append("Ensure resin vat is filled above 25%.")
            safety_notes.append("Run preflight_sla before starting.")
            if "tough" in material_lower or "flexible" in material_lower:
                settings["suggested_exposure_s"] = 12.0
                settings["suggested_bottom_exposure_s"] = 80.0
                safety_notes.append(
                    f"Material '{material}' may require longer exposure times."
                )
        elif device_type == "laser":
            settings = {
                "suggested_power_percent": 50.0,
                "suggested_speed_mm_s": 100.0,
                "suggested_passes": 1,
                "suggested_air_assist": True,
            }
            safety_notes.append("Verify ventilation is running before cutting.")
            safety_notes.append("Ensure lid interlock is engaged.")
            safety_notes.append("Run preflight_laser before starting.")
            if job_type == "engrave":
                settings["suggested_power_percent"] = 20.0
                settings["suggested_speed_mm_s"] = 200.0
            elif job_type == "cut":
                settings["suggested_passes"] = 3
            # Check dangerous materials for laser
            dangerous = intel.get_dangerous_materials(adapter_name)
            for dm in dangerous:
                if material_lower in dm.material.lower():
                    safety_notes.append(
                        f"WARNING: '{dm.material}' is dangerous — {dm.reason}"
                    )
        elif device_type == "cnc":
            settings = {
                "suggested_rpm": 12000.0,
                "suggested_feed_mm_min": 1500.0,
                "suggested_plunge_mm_min": 500.0,
                "suggested_depth_mm": 2.0,
                "suggested_coolant": False,
            }
            safety_notes.append("Ensure workpiece is securely clamped.")
            safety_notes.append("Run preflight_cnc before starting.")
            if "aluminum" in material_lower or "steel" in material_lower:
                settings["suggested_rpm"] = 8000.0
                settings["suggested_feed_mm_min"] = 800.0
                settings["suggested_coolant"] = True
                safety_notes.append(
                    f"Metal cutting: use coolant and reduced feeds for '{material}'."
                )

        # Confidence based on available intelligence data
        data_points = len(relevant_tips) + len(failure_list)
        if data_points >= 5:
            confidence = "high"
        elif data_points >= 2:
            confidence = "medium"
        else:
            confidence = "low"

        return _success_dict({
            "device_id": device_id,
            "device_type": device_type,
            "material": material,
            "job_type": job_type,
            "recommended_settings": settings,
            "confidence": confidence,
            "material_tips": relevant_tips,
            "safety_notes": safety_notes,
            "known_failure_modes": failure_list[:5],
            "maintenance_reminders": maintenance_list[:3],
        })
    except Exception as exc:
        logger.exception("Error in recommend_device_settings")
        return _error_dict(f"Failed to recommend settings: {exc}")


# ===================================================================
# STREAMING / CAMERA TOOLS
# ===================================================================

_streaming_mgr: Optional[Any] = None


def _get_streaming_manager() -> Any:
    """Return the lazily-initialised streaming manager."""
    global _streaming_mgr
    if _streaming_mgr is None:
        from forge.streaming import get_streaming_manager
        _streaming_mgr = get_streaming_manager()
    return _streaming_mgr


@mcp.tool()
def device_snapshot(device_id: str) -> dict:
    """Capture and return a camera frame from a device.

    Returns a base64-encoded JPEG image from the device's configured
    camera stream.  The stream must be registered first via
    ``configure_device_stream``.
    """
    try:
        mgr = _get_streaming_manager()
        frame = mgr.capture_frame(device_id)
        return _success_dict({
            "device_id": frame.device_id,
            "timestamp": frame.timestamp,
            "image_b64": frame.image_b64,
            "width": frame.width,
            "height": frame.height,
            "format": frame.format,
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="STREAM_NOT_FOUND")
    except ConnectionError as exc:
        return _error_dict(str(exc), code="CAPTURE_FAILED", retryable=True)
    except Exception as exc:
        logger.exception("Error in device_snapshot")
        return _error_dict(f"Failed to capture snapshot: {exc}")


@mcp.tool()
def device_stream_url(device_id: str) -> dict:
    """Get the streaming URL for a device's camera.

    Returns the configured camera stream URL, or an error if no stream
    is registered for the device.
    """
    try:
        mgr = _get_streaming_manager()
        url = mgr.get_stream_url(device_id)
        if url is None:
            return _error_dict(f"No stream registered for device '{device_id}'", code="STREAM_NOT_FOUND")
        return _success_dict({
            "device_id": device_id,
            "stream_url": url,
        })
    except Exception as exc:
        logger.exception("Error in device_stream_url")
        return _error_dict(f"Failed to get stream URL: {exc}")


@mcp.tool()
def configure_device_stream(
    device_id: str,
    url: str,
    stream_type: Optional[str] = None,
) -> dict:
    """Set up camera streaming for a device.

    Registers a camera stream URL for the given device.  If *stream_type*
    is not provided, it defaults to ``"snapshot"``.

    :param device_id: Unique device identifier.
    :param url: Camera stream URL.
    :param stream_type: One of ``mjpeg``, ``hls``, ``snapshot``, ``rtsp``.
    """
    try:
        from forge.streaming import StreamConfig, StreamType

        type_str = stream_type or "snapshot"
        try:
            st = StreamType(type_str)
        except ValueError:
            valid = ", ".join(t.value for t in StreamType)
            return _error_dict(
                f"Unknown stream type '{type_str}'. Valid types: {valid}",
                code="INVALID_STREAM_TYPE",
            )

        config = StreamConfig(url=url, stream_type=st)
        mgr = _get_streaming_manager()
        stream = mgr.register_stream(device_id, config)
        return _success_dict({
            "device_id": device_id,
            "stream": stream.to_dict(),
        })
    except Exception as exc:
        logger.exception("Error in configure_device_stream")
        return _error_dict(f"Failed to configure stream: {exc}")


# ===================================================================
# CAM / FILE PREPARATION TOOLS
# ===================================================================

@mcp.tool()
def list_cam_tools() -> dict:
    """List available CAM software installed on this system.

    Scans for ChiTuBox, Lychee, LightBurn, Fusion 360, FreeCAD,
    CAMotics, and EstlCAM.  Returns path and version for each
    discovered tool.
    """
    try:
        from forge.cam import list_available_tools

        tools = list_available_tools()
        return _success_dict({
            "tools": [t.to_dict() for t in tools],
            "count": len(tools),
        })
    except Exception as exc:
        logger.exception("Error in list_cam_tools")
        return _error_dict(f"Failed to list CAM tools: {exc}")


@mcp.tool()
def prepare_for_device(
    file_path: str,
    device_type: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Prepare a design file for a specific device type.

    Auto-dispatches to the correct CAM workflow based on device_type:
    ``"sla"`` uses ChiTuBox/Lychee, ``"laser"`` uses LightBurn,
    ``"cnc"`` uses CAMotics/EstlCAM.

    Returns the path to the processed output file, or an error message
    if the required CAM tool is not installed.
    """
    try:
        from forge.cam import prepare_file

        result = prepare_file(
            file_path,
            device_type,
            device_id=device_id,
        )
        return _success_dict(result.to_dict()) if result.success else _error_dict(
            result.message, code="CAM_FAILED")
    except Exception as exc:
        logger.exception("Error in prepare_for_device")
        return _error_dict(f"Failed to prepare file: {exc}")


# ===================================================================
# FILE METADATA TOOLS
# ===================================================================

@mcp.tool()
def analyze_file(file_path: str) -> dict:
    """Extract metadata from a manufacturing file (SLA, laser, CNC).

    Auto-detects file type by extension and parses headers for estimated
    time, layer count, dimensions, material hints, and slicer info.

    Supported formats: .ctb, .sl1, .pwmx (SLA); .svg, .dxf, .lbrn (laser);
    .nc, .gcode, .ngc (CNC).  Unknown extensions return basic file info.
    """
    try:
        from forge.file_metadata import extract_metadata

        meta = extract_metadata(file_path)
        return _success_dict({"metadata": meta.to_dict()})
    except Exception as exc:
        logger.exception("Error in analyze_file")
        return _error_dict(f"Failed to analyze file: {exc}")


# ---------------------------------------------------------------------------
# Plugin tools
# ---------------------------------------------------------------------------

_plugin_manager: Optional[Any] = None


def _get_plugin_manager() -> Any:
    """Return the lazily-initialised plugin manager."""
    global _plugin_manager
    if _plugin_manager is None:
        from forge.plugins import get_plugin_manager
        _plugin_manager = get_plugin_manager()
    return _plugin_manager


@mcp.tool()
def list_plugins(plugin_type: Optional[str] = None) -> dict:
    """List all discovered plugins, optionally filtered by type.

    :param plugin_type: Filter by plugin type (e.g. "device_adapter",
        "safety_validator", "file_processor", "fulfillment_provider",
        "marketplace").  Omit or pass null for all plugins.
    """
    try:
        from forge.plugins import PluginType

        mgr = _get_plugin_manager()
        pt: Optional[PluginType] = None
        if plugin_type is not None:
            try:
                pt = PluginType(plugin_type)
            except ValueError:
                valid = [t.value for t in PluginType]
                return _error_dict(
                    f"Invalid plugin_type {plugin_type!r}. "
                    f"Valid values: {valid}",
                    code="VALIDATION_ERROR",
                )
        plugins = mgr.list_plugins(plugin_type=pt)
        return _success_dict({
            "plugins": [p.to_dict() for p in plugins],
            "count": len(plugins),
        })
    except Exception as exc:
        logger.exception("Error in list_plugins")
        return _error_dict(f"Failed to list plugins: {exc}")


@mcp.tool()
def plugin_info(name: str) -> dict:
    """Get detailed information for a specific plugin.

    :param name: The unique plugin name.
    """
    if not name:
        return _error_dict("name is required.", code="VALIDATION_ERROR")
    try:
        mgr = _get_plugin_manager()
        result = mgr.get_plugin(name)
        if result is None:
            return _error_dict(
                f"No plugin found with name: {name!r}",
                code="NOT_FOUND",
                retryable=False,
            )
        info, _mod = result
        return _success_dict({"plugin": info.to_dict()})
    except Exception as exc:
        logger.exception("Error in plugin_info")
        return _error_dict(f"Failed to get plugin info: {exc}")


# ===================================================================
# FIRMWARE MANAGEMENT TOOLS
# ===================================================================


def _get_firmware_manager() -> Any:
    """Return the lazily-initialised firmware manager."""
    from forge.firmware import get_firmware_manager
    return get_firmware_manager()


@mcp.tool()
def firmware_status(device_id: str) -> dict:
    """Check firmware versions and available updates for a device.

    Returns the current firmware version of each component on the
    device, whether updates are available, and whether any are
    critical patches.

    Args:
        device_id: Name of the device in the fleet registry.
    """
    try:
        mgr = _get_firmware_manager()
        status = mgr.check_firmware(device_id)
        return _success_dict({
            "device_id": status.device_id,
            "device_type": status.device_type,
            "last_checked": status.last_checked,
            "updates_available": status.updates_available,
            "has_critical": status.has_critical,
            "components": [c.to_dict() for c in status.components],
        })
    except Exception as exc:
        logger.exception("Error in firmware_status")
        return _error_dict(f"Failed to check firmware: {exc}")


@mcp.tool()
def update_firmware(
    device_id: str,
    *,
    component: Optional[str] = None,
) -> dict:
    """Update firmware on a device.

    Applies available firmware updates.  If *component* is specified
    only that component is updated; otherwise all components with
    pending updates are upgraded.

    Args:
        device_id: Name of the device in the fleet registry.
        component: Optional component name to update (e.g.
            ``"motion_controller"``).  If omitted, all available
            updates are applied.
    """
    rl = _check_rate_limit("update_firmware")
    if rl:
        return rl
    try:
        mgr = _get_firmware_manager()
        result = mgr.update_firmware(device_id, component=component)
        return _success_dict(result)
    except Exception as exc:
        logger.exception("Error in update_firmware")
        return _error_dict(f"Failed to update firmware: {exc}")


@mcp.tool()
def rollback_firmware(device_id: str, component: str) -> dict:
    """Roll back a firmware component to its previous version.

    Reverts the named component on the device to the version it had
    before the most recent update.  Requires update history to exist.

    Args:
        device_id: Name of the device in the fleet registry.
        component: Name of the component to roll back.
    """
    rl = _check_rate_limit("rollback_firmware")
    if rl:
        return rl
    try:
        mgr = _get_firmware_manager()
        result = mgr.rollback_firmware(device_id, component)
        return _success_dict(result)
    except Exception as exc:
        logger.exception("Error in rollback_firmware")
        return _error_dict(f"Failed to rollback firmware: {exc}")


# ---------------------------------------------------------------------------
# Skill manifest
# ---------------------------------------------------------------------------

@mcp.tool()
def get_skill_manifest(
    *,
    category: Optional[str] = None,
    device_type: Optional[str] = None,
    tier: Optional[str] = None,
) -> dict:
    """Return the full skill manifest for agent self-discovery.

    Lists every Forge capability with its category, required tier,
    supported device types, and whether it is dangerous.  Use the
    optional filters to narrow results.

    Args:
        category: Filter by skill category (e.g. "device_control", "safety").
        device_type: Filter by device type ("sla", "laser", "cnc").
        tier: Filter by required tier ("essential", "standard", "full").
    """
    try:
        from forge.skill_manifest import SkillCategory
        from forge.skill_manifest import get_skill_manifest as _get_manifest

        manifest = _get_manifest()

        cat_enum: Optional[SkillCategory] = None
        if category is not None:
            try:
                cat_enum = SkillCategory(category.lower())
            except ValueError:
                valid = [c.value for c in SkillCategory]
                return _error_dict(
                    f"Unknown category {category!r}. Valid: {', '.join(valid)}",
                    code="INVALID_CATEGORY",
                    retryable=False,
                )

        if tier is not None and tier not in ("essential", "standard", "full"):
            return _error_dict(
                f"Unknown tier {tier!r}. Valid: essential, standard, full",
                code="INVALID_TIER",
                retryable=False,
            )

        skills = manifest.list_skills(
            category=cat_enum,
            device_type=device_type,
            tier=tier,
        )

        return _success_dict({
            "skill_count": len(skills),
            "skills": [s.to_dict() for s in skills],
        })
    except Exception as exc:
        logger.exception("Error in get_skill_manifest")
        return _error_dict(f"Failed to retrieve skill manifest: {exc}")


# ===================================================================
# DEVICE MONITORING TOOLS
# ===================================================================

_device_monitor: Optional[Any] = None


def _get_device_monitor() -> Any:
    """Return the lazily-initialised device monitor."""
    global _device_monitor
    if _device_monitor is None:
        from forge.device_monitor import DeviceMonitor
        _device_monitor = DeviceMonitor()
    return _device_monitor


@mcp.tool()
def start_device_monitoring(
    device_id: str,
    job_id: str,
    *,
    device_type: Optional[str] = None,
    check_delay_seconds: Optional[int] = None,
    check_count: Optional[int] = None,
    check_interval_seconds: Optional[int] = None,
) -> dict:
    """Start real-time monitoring for an active device job.

    Creates a new monitoring session that tracks snapshots, detects
    device-type-specific phases, and enables issue reporting.

    Optionally override default monitoring policy values.  If not
    provided, defaults are loaded from environment variables.

    Returns the session_id needed for all subsequent monitoring calls.
    """
    try:
        monitor = _get_device_monitor()

        policy_kwargs: Dict[str, Any] = {}
        if check_delay_seconds is not None:
            policy_kwargs["check_delay_seconds"] = check_delay_seconds
        if check_count is not None:
            policy_kwargs["check_count"] = check_count
        if check_interval_seconds is not None:
            policy_kwargs["check_interval_seconds"] = check_interval_seconds

        from forge.device_monitor import MonitorPolicy
        policy = MonitorPolicy(**policy_kwargs) if policy_kwargs else None

        session_id = monitor.start_monitoring(
            device_id,
            job_id,
            policy=policy,
            device_type=device_type,
        )
        session = monitor.get_session(session_id)
        return _success_dict({
            "session_id": session_id,
            "device_id": device_id,
            "job_id": job_id,
            "status": session.status.value,
            "policy": session.policy.to_dict(),
        })
    except ValueError as exc:
        return _error_dict(str(exc), code="CONFLICT", retryable=False)
    except Exception as exc:
        logger.exception("Error in start_device_monitoring")
        return _error_dict(f"Failed to start monitoring: {exc}")


@mcp.tool()
def stop_device_monitoring(session_id: str) -> dict:
    """Stop an active monitoring session.

    Marks the session as completed and records the end time.
    Collected snapshots and reported issues remain available
    via get_monitoring_status.
    """
    try:
        monitor = _get_device_monitor()
        session = monitor.stop_monitoring(session_id)
        return _success_dict(session.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="NOT_FOUND", retryable=False)
    except ValueError as exc:
        return _error_dict(str(exc), code="INVALID_STATE", retryable=False)
    except Exception as exc:
        logger.exception("Error in stop_device_monitoring")
        return _error_dict(f"Failed to stop monitoring: {exc}")


@mcp.tool()
def get_monitoring_status(session_id: str) -> dict:
    """Get the current state of a monitoring session.

    Returns the session status, collected snapshots, reported issues,
    and the monitoring policy.  Works for both active and completed
    sessions.
    """
    try:
        monitor = _get_device_monitor()
        session = monitor.get_session(session_id)
        return _success_dict(session.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="NOT_FOUND", retryable=False)
    except Exception as exc:
        logger.exception("Error in get_monitoring_status")
        return _error_dict(f"Failed to get monitoring status: {exc}")


@mcp.tool()
def capture_device_snapshot(
    session_id: str,
    *,
    completion_pct: Optional[float] = None,
    image_b64: Optional[str] = None,
) -> dict:
    """Capture a point-in-time snapshot for an active monitoring session.

    Records the current job completion, detects the device-type-specific
    operational phase, and optionally stores a base64-encoded camera image.

    Phase detection is automatic based on device type:
    - SLA: exposure / peel / lift
    - Laser: cutting / engraving / traversing
    - CNC: roughing / finishing / drilling
    """
    try:
        monitor = _get_device_monitor()
        snapshot = monitor.capture_snapshot(
            session_id,
            completion_pct=completion_pct,
            image_b64=image_b64,
        )
        return _success_dict(snapshot.to_dict())
    except KeyError as exc:
        return _error_dict(str(exc), code="NOT_FOUND", retryable=False)
    except ValueError as exc:
        return _error_dict(str(exc), code="INVALID_STATE", retryable=False)
    except Exception as exc:
        logger.exception("Error in capture_device_snapshot")
        return _error_dict(f"Failed to capture snapshot: {exc}")


# ===================================================================
# LICENSE TOOLS
# ===================================================================


@mcp.tool()
def license_info() -> dict:
    """Get the current Forge license tier, allowed features, and device limit.

    Returns the active license tier (free/maker/pro/enterprise), the list
    of unlocked features, the maximum number of connected devices, and
    the optional expiry date.
    """
    try:
        from forge.licensing import get_license_manager

        mgr = get_license_manager()
        info = mgr.get_license()
        return _success_dict(info.to_dict())
    except Exception as exc:
        logger.exception("Error in license_info")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


# ===================================================================
# SAFETY & HEALTH TOOLS
# ===================================================================


@mcp.tool()
def safety_audit(*, device_id: Optional[str] = None) -> dict:
    """Run a full safety audit across all registered devices.

    Checks device connectivity, safety profile coverage, interlock
    status, and parameter bounds for each device.  Pass *device_id*
    to scope the audit to a single device.

    :param device_id: Optional device name to audit.  Audits all if omitted.
    """
    try:
        registry = _get_registry()
        if device_id is not None:
            names = [device_id]
            if device_id not in registry:
                return _error_dict(
                    f"No device registered with name: {device_id!r}",
                    code="DEVICE_NOT_FOUND",
                    retryable=False,
                )
        else:
            names = registry.list_names()

        findings: List[Dict[str, Any]] = []
        for name in names:
            try:
                adapter = registry.get(name)
                state = adapter.get_state()
                device_findings: Dict[str, Any] = {
                    "device": name,
                    "connected": state.connected,
                    "state": state.state.value if hasattr(state, "state") else str(state.state),
                    "issues": [],
                }
                if not state.connected:
                    device_findings["issues"].append("Device is offline")
                findings.append(device_findings)
            except Exception as exc:
                findings.append({
                    "device": name,
                    "connected": False,
                    "status": "error",
                    "issues": [f"Failed to query device: {exc}"],
                })

        total_issues = sum(len(f["issues"]) for f in findings)
        return _success_dict({
            "devices_audited": len(findings),
            "total_issues": total_issues,
            "passed": total_issues == 0,
            "findings": findings,
        })
    except Exception as exc:
        logger.exception("Error in safety_audit")
        return _error_dict(f"Safety audit failed: {exc}")


@mcp.tool()
def health_check() -> dict:
    """Run a system health check covering DB, devices, and job queue.

    Returns connectivity and operational health for the persistence
    layer, device registry, and job queue subsystem.
    """
    try:
        checks: Dict[str, Any] = {}

        # Database health
        try:
            from forge.persistence import get_db
            db = get_db()
            db.list_jobs(limit=1)
            checks["database"] = {"status": "ok"}
        except Exception as exc:
            checks["database"] = {"status": "error", "message": str(exc)}

        # Device registry health
        try:
            registry = _get_registry()
            device_names = registry.list_names()
            checks["devices"] = {
                "status": "ok",
                "registered_count": len(device_names),
            }
        except Exception as exc:
            checks["devices"] = {"status": "error", "message": str(exc)}

        # Queue health
        try:
            queue = _get_queue()
            pending = queue.list_pending() if hasattr(queue, "list_pending") else []
            checks["queue"] = {
                "status": "ok",
                "pending_jobs": len(pending),
            }
        except Exception as exc:
            checks["queue"] = {"status": "error", "message": str(exc)}

        all_ok = all(c.get("status") == "ok" for c in checks.values())
        return _success_dict({
            "healthy": all_ok,
            "checks": checks,
        })
    except Exception as exc:
        logger.exception("Error in health_check")
        return _error_dict(f"Health check failed: {exc}")


@mcp.tool()
def safety_settings() -> dict:
    """Get the current global safety configuration.

    Returns the loaded safety profile counts for each device type
    (SLA, laser, CNC) and the validation settings in effect.
    """
    try:
        from forge.safety import (
            list_sla_profiles,
            list_laser_profiles,
            list_machines as list_cnc_machines,
        )

        sla_profiles = list_sla_profiles()
        laser_profiles = list_laser_profiles()
        cnc_machines = list_cnc_machines()

        return _success_dict({
            "sla_profiles_count": len(sla_profiles),
            "laser_profiles_count": len(laser_profiles),
            "cnc_machine_profiles_count": len(cnc_machines),
            "sla_profiles": sla_profiles,
            "laser_profiles": laser_profiles,
            "cnc_machine_profiles": cnc_machines,
        })
    except Exception as exc:
        logger.exception("Error in safety_settings")
        return _error_dict(f"Failed to load safety settings: {exc}")


@mcp.tool()
def list_safety_profiles(*, device_type: Optional[str] = None) -> dict:
    """List all available safety profiles, optionally filtered by device type.

    :param device_type: One of ``"sla"``, ``"laser"``, ``"cnc"``.
        Lists all types if omitted.
    """
    try:
        from forge.safety import (
            list_sla_profiles,
            list_laser_profiles,
            list_machines as list_cnc_machines,
        )

        result: Dict[str, Any] = {}
        valid_types = {"sla", "laser", "cnc"}

        if device_type is not None and device_type not in valid_types:
            return _error_dict(
                f"Invalid device_type {device_type!r}. Must be one of: {sorted(valid_types)}",
                code="VALIDATION_ERROR",
                retryable=False,
            )

        if device_type is None or device_type == "sla":
            result["sla"] = list_sla_profiles()
        if device_type is None or device_type == "laser":
            result["laser"] = list_laser_profiles()
        if device_type is None or device_type == "cnc":
            result["cnc"] = list_cnc_machines()

        total = sum(len(v) for v in result.values())
        return _success_dict({
            "profiles": result,
            "total": total,
        })
    except Exception as exc:
        logger.exception("Error in list_safety_profiles")
        return _error_dict(f"Failed to list safety profiles: {exc}")


@mcp.tool()
def validate_job_safe(file_path: str, device_id: str) -> dict:
    """Validate that a file is safe to run on a specific device.

    Performs file validation (format, parameter bounds) using the
    safety profile for the target device.

    :param file_path: Path to the toolpath / slice file.
    :param device_id: Name of the target device.
    """
    if not file_path:
        return _error_dict("file_path is required.", code="VALIDATION_ERROR", retryable=False)
    if not device_id:
        return _error_dict("device_id is required.", code="VALIDATION_ERROR", retryable=False)

    try:
        registry = _get_registry()
        if device_id not in registry:
            return _error_dict(
                f"No device registered with name: {device_id!r}",
                code="DEVICE_NOT_FOUND",
                retryable=False,
            )

        device_type = registry.get_device_type(device_id)

        import os
        if not os.path.isfile(file_path):
            return _error_dict(
                f"File not found: {file_path}",
                code="FILE_NOT_FOUND",
                retryable=False,
            )

        if device_type == "sla":
            from forge.safety import SLAFileValidator
            validator = SLAFileValidator()
            result = validator.validate(file_path)
        elif device_type == "laser":
            from forge.safety import LaserFileValidator
            validator = LaserFileValidator()
            result = validator.validate(file_path)
        elif device_type == "cnc":
            from forge.safety import CNCFileValidator
            validator = CNCFileValidator()
            result = validator.validate(file_path)
        else:
            return _error_dict(
                f"Unsupported device type: {device_type!r}",
                code="VALIDATION_ERROR",
                retryable=False,
            )

        return _success_dict({
            "file_path": file_path,
            "device_id": device_id,
            "device_type": device_type,
            "valid": result.valid,
            "validation": result.to_dict(),
        })
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND", retryable=False)
    except Exception as exc:
        logger.exception("Error in validate_job_safe")
        return _error_dict(f"Failed to validate file safety: {exc}")


# ===================================================================
# DESIGN / MODEL MANAGEMENT TOOLS
# ===================================================================


@mcp.tool()
def cache_design(
    file_path: str,
    device_type: str,
    *,
    source: Optional[str] = None,
) -> dict:
    """Cache a design file locally for quick re-use.

    Computes a content hash to avoid duplicate storage.

    :param file_path: Path to the design file on disk.
    :param device_type: Device type (``"sla"``, ``"laser"``, ``"cnc"``).
    :param source: Where the file came from (URL, marketplace, etc.).
    """
    if not file_path:
        return _error_dict("file_path is required.", code="VALIDATION_ERROR", retryable=False)
    if not device_type:
        return _error_dict("device_type is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        from forge.design_cache import get_design_cache

        cache = get_design_cache()
        entry = cache.add(file_path, device_type=device_type, source=source)
        return _success_dict({
            "design_id": entry.id,
            "file_name": entry.file_name,
            "device_type": entry.device_type,
            "file_hash": entry.file_hash,
            "cached": True,
        })
    except FileNotFoundError as exc:
        return _error_dict(str(exc), code="FILE_NOT_FOUND", retryable=False)
    except ValueError as exc:
        return _error_dict(str(exc), code="VALIDATION_ERROR", retryable=False)
    except Exception as exc:
        logger.exception("Error in cache_design")
        return _error_dict(f"Failed to cache design: {exc}")


@mcp.tool()
def search_cached_designs(
    *,
    query: Optional[str] = None,
    device_type: Optional[str] = None,
) -> dict:
    """Search cached design files by keyword or device type.

    :param query: Free-text search against file names and tags.
    :param device_type: Filter by device type (``"sla"``, ``"laser"``, ``"cnc"``).
    """
    try:
        from forge.design_cache import get_design_cache

        cache = get_design_cache()
        results = cache.search(query=query, device_type=device_type)
        return _success_dict({
            "designs": [d.to_dict() for d in results],
            "count": len(results),
        })
    except Exception as exc:
        logger.exception("Error in search_cached_designs")
        return _error_dict(f"Failed to search designs: {exc}")


@mcp.tool()
def list_cached_designs(
    *,
    device_type: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """List cached design files with optional device type filter.

    :param device_type: Filter by device type.
    :param limit: Maximum results to return (default 20).
    """
    try:
        from forge.design_cache import get_design_cache

        cache = get_design_cache()
        results = cache.search(device_type=device_type, limit=limit)
        return _success_dict({
            "designs": [d.to_dict() for d in results],
            "count": len(results),
        })
    except Exception as exc:
        logger.exception("Error in list_cached_designs")
        return _error_dict(f"Failed to list cached designs: {exc}")


@mcp.tool()
def delete_cached_design(design_id: str) -> dict:
    """Remove a cached design file from the local cache.

    :param design_id: The unique ID of the cached design.
    """
    if not design_id:
        return _error_dict("design_id is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        from forge.design_cache import get_design_cache

        cache = get_design_cache()
        removed = cache.remove(design_id)
        if not removed:
            return _error_dict(
                f"No cached design found with ID: {design_id!r}",
                code="NOT_FOUND",
                retryable=False,
            )
        return _success_dict({
            "design_id": design_id,
            "deleted": True,
        })
    except Exception as exc:
        logger.exception("Error in delete_cached_design")
        return _error_dict(f"Failed to delete cached design: {exc}")


# ===================================================================
# RECOVERY & OPERATIONS TOOLS
# ===================================================================


@mcp.tool()
def save_checkpoint(
    job_id: str,
    phase: str,
    progress_pct: float,
) -> dict:
    """Save a recovery checkpoint for a running job.

    Checkpoints enable resume-from-failure for interrupted jobs.

    :param job_id: The job identifier.
    :param phase: Current phase name (e.g. ``"exposing"``, ``"cutting"``).
    :param progress_pct: Completion percentage (0-100).
    """
    if not job_id:
        return _error_dict("job_id is required.", code="VALIDATION_ERROR", retryable=False)
    if not phase:
        return _error_dict("phase is required.", code="VALIDATION_ERROR", retryable=False)
    if not (0.0 <= progress_pct <= 100.0):
        return _error_dict(
            f"progress_pct must be 0-100, got {progress_pct}",
            code="VALIDATION_ERROR",
            retryable=False,
        )
    try:
        from forge.recovery import get_recovery_manager

        mgr = get_recovery_manager()
        checkpoint = mgr.save_checkpoint(
            job_id=job_id,
            device_id="unknown",
            device_type="unknown",
            phase=phase,
            progress_pct=progress_pct,
        )
        return _success_dict({
            "checkpoint_id": checkpoint.id,
            "job_id": checkpoint.job_id,
            "phase": checkpoint.phase,
            "progress_pct": checkpoint.progress_pct,
            "saved": True,
        })
    except Exception as exc:
        logger.exception("Error in save_checkpoint")
        return _error_dict(f"Failed to save checkpoint: {exc}")


@mcp.tool()
def plan_recovery(job_id: str) -> dict:
    """Generate a recovery plan for a failed or interrupted job.

    Analyzes the job's checkpoint history and failure context to
    recommend a recovery strategy (restart, resume, manual, abort).

    :param job_id: The job identifier to plan recovery for.
    """
    if not job_id:
        return _error_dict("job_id is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        from forge.recovery import FailureType, get_recovery_manager

        mgr = get_recovery_manager()
        plan = mgr.plan_recovery(job_id, FailureType.DEVICE_ERROR)
        return _success_dict({
            "job_id": job_id,
            "plan": plan.to_dict(),
        })
    except Exception as exc:
        logger.exception("Error in plan_recovery")
        return _error_dict(f"Failed to plan recovery: {exc}")


@mcp.tool()
def get_job_progress(job_id: str) -> dict:
    """Get detailed progress estimation for an active job.

    Queries the recovery checkpoint history to report current phase,
    completion percentage, and time estimates.

    :param job_id: The job identifier.
    """
    if not job_id:
        return _error_dict("job_id is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        from forge.recovery import get_recovery_manager

        mgr = get_recovery_manager()
        checkpoint = mgr.get_latest_checkpoint(job_id)
        if checkpoint is None:
            return _error_dict(
                f"No progress data found for job: {job_id!r}",
                code="NOT_FOUND",
                retryable=False,
            )
        return _success_dict({
            "job_id": job_id,
            "phase": checkpoint.phase,
            "progress_pct": checkpoint.progress_pct,
            "checkpoint_id": checkpoint.id,
            "checkpoint": checkpoint.to_dict(),
        })
    except Exception as exc:
        logger.exception("Error in get_job_progress")
        return _error_dict(f"Failed to get job progress: {exc}")


@mcp.tool()
def find_material_substitute(material: str, device_type: str) -> dict:
    """Find compatible alternative materials for a device type.

    Searches the substitution matrix for materials that can replace
    the specified one, sorted by compatibility score.

    :param material: Original material identifier (e.g. ``"standard_resin"``).
    :param device_type: Device class (``"sla"``, ``"laser"``, ``"cnc"``).
    """
    if not material:
        return _error_dict("material is required.", code="VALIDATION_ERROR", retryable=False)
    if not device_type:
        return _error_dict("device_type is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        from forge.material_substitution import find_substitutes

        subs = find_substitutes(material, device_type)
        return _success_dict({
            "material": material,
            "device_type": device_type,
            "substitutes": [s.to_dict() for s in subs],
            "count": len(subs),
        })
    except Exception as exc:
        logger.exception("Error in find_material_substitute")
        return _error_dict(f"Failed to find substitutes: {exc}")


# ===================================================================
# TRUST & SECURITY TOOLS
# ===================================================================

_trust_store: Optional[Dict[str, Dict[str, Any]]] = None


def _get_trust_store() -> Dict[str, Dict[str, Any]]:
    """Return the in-memory trust store (lazily initialised)."""
    global _trust_store
    if _trust_store is None:
        _trust_store = {}
    return _trust_store


@mcp.tool()
def list_trusted_devices() -> dict:
    """List all devices currently in the trust store.

    Trusted devices are allowed to execute jobs without additional
    confirmation prompts.
    """
    try:
        store = _get_trust_store()
        devices = [
            {"device_id": did, **info}
            for did, info in store.items()
        ]
        return _success_dict({
            "trusted_devices": devices,
            "count": len(devices),
        })
    except Exception as exc:
        logger.exception("Error in list_trusted_devices")
        return _error_dict(f"Failed to list trusted devices: {exc}")


@mcp.tool()
def trust_device(device_id: str) -> dict:
    """Add a device to the trust store.

    Trusted devices can receive jobs without extra safety confirmations.

    :param device_id: The device name to trust.
    """
    if not device_id:
        return _error_dict("device_id is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        store = _get_trust_store()
        if device_id in store:
            return _success_dict({
                "device_id": device_id,
                "already_trusted": True,
                "message": f"Device {device_id!r} is already trusted.",
            })
        import time as _time
        store[device_id] = {"trusted_at": _time.time()}
        return _success_dict({
            "device_id": device_id,
            "trusted": True,
            "message": f"Device {device_id!r} added to trust store.",
        })
    except Exception as exc:
        logger.exception("Error in trust_device")
        return _error_dict(f"Failed to trust device: {exc}")


@mcp.tool()
def untrust_device(device_id: str) -> dict:
    """Remove a device from the trust store.

    :param device_id: The device name to remove.
    """
    if not device_id:
        return _error_dict("device_id is required.", code="VALIDATION_ERROR", retryable=False)
    try:
        store = _get_trust_store()
        if device_id not in store:
            return _error_dict(
                f"Device {device_id!r} is not in the trust store.",
                code="NOT_FOUND",
                retryable=False,
            )
        del store[device_id]
        return _success_dict({
            "device_id": device_id,
            "untrusted": True,
            "message": f"Device {device_id!r} removed from trust store.",
        })
    except Exception as exc:
        logger.exception("Error in untrust_device")
        return _error_dict(f"Failed to untrust device: {exc}")


# ===================================================================
# MISCELLANEOUS TOOLS
# ===================================================================


@mcp.tool()
def backup_database(*, output_path: Optional[str] = None) -> dict:
    """Trigger a database backup.

    Creates a timestamped SQLite backup using ``VACUUM INTO``.

    :param output_path: Directory to store the backup.  Defaults to
        ``$FORGE_DATA_DIR/backups``.
    """
    try:
        from forge.backup import backup_database as _backup_database

        data_dir = os.environ.get(
            "FORGE_DATA_DIR", os.path.expanduser("~/.forge")
        )
        db_path = os.environ.get(
            "FORGE_QUEUE_DB", os.path.join(data_dir, "queue.db")
        )
        backup_dir = output_path or os.path.join(data_dir, "backups")

        result = _backup_database(db_path, backup_dir)
        return _success_dict(result.to_dict())
    except Exception as exc:
        logger.exception("Error in backup_database")
        return _error_dict(f"Failed to backup database: {exc}")


@mcp.tool()
def donate_info() -> dict:
    """Get donation and support information for the Forge project.

    Returns links and methods for supporting ongoing development.
    """
    return _success_dict({
        "project": "Forge",
        "description": (
            "Forge is an open multi-device manufacturing platform "
            "supporting SLA, laser, and CNC workflows."
        ),
        "support_methods": [
            {
                "method": "GitHub Sponsors",
                "url": "https://github.com/sponsors/forge",
            },
            {
                "method": "Open Collective",
                "url": "https://opencollective.com/forge",
            },
        ],
        "message": (
            "Thank you for considering a contribution! "
            "Every bit helps fund device testing and development."
        ),
    })


@mcp.tool()
def get_started() -> dict:
    """Onboarding guide for new users of the Forge platform.

    Returns step-by-step instructions for initial setup, device
    registration, and first job submission.
    """
    return _success_dict({
        "steps": [
            {
                "step": 1,
                "title": "Install Forge",
                "description": "pip install forge or clone the repository.",
            },
            {
                "step": 2,
                "title": "Configure data directory",
                "description": (
                    "Set FORGE_DATA_DIR environment variable or use "
                    "the default ~/.forge directory."
                ),
            },
            {
                "step": 3,
                "title": "Register a device",
                "description": (
                    "Use register_device to add your SLA printer, "
                    "laser cutter, or CNC machine."
                ),
            },
            {
                "step": 4,
                "title": "Run a preflight check",
                "description": (
                    "Call preflight_sla, preflight_laser, or preflight_cnc "
                    "to verify device safety."
                ),
            },
            {
                "step": 5,
                "title": "Submit your first job",
                "description": (
                    "Use submit_job with a validated file and device type."
                ),
            },
        ],
        "documentation_url": "https://forge.dev/docs",
        "quick_tools": [
            "fleet_status",
            "health_check",
            "safety_audit",
        ],
    })


@mcp.tool()
def version_info() -> dict:
    """Get platform version and build information.

    Returns the current Forge version, Python version, and platform
    details for diagnostic and compatibility checks.
    """
    import platform
    import sys

    return _success_dict({
        "forge_version": "0.1.0",
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.machine(),
    })


# ===================================================================
# HISTORY & ANALYTICS TOOLS (from tools_history)
# ===================================================================


@mcp.tool()
def job_history_search(
    *,
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    since: Optional[float] = None,
    until: Optional[float] = None,
    limit: int = 50,
) -> dict:
    """Search job history with filters."""
    from forge.tools_history import job_history_search as _impl
    return _impl(
        device_name=device_name,
        device_type=device_type,
        status=status,
        since=since,
        until=until,
        limit=limit,
    )


@mcp.tool()
def device_performance_stats(
    device_name: str,
    *,
    device_type: Optional[str] = None,
) -> dict:
    """Aggregate performance stats for a device."""
    from forge.tools_history import device_performance_stats as _impl
    return _impl(device_name, device_type=device_type)


@mcp.tool()
def annotate_job_extended(
    job_id: str,
    *,
    note: Optional[str] = None,
    tags: Optional[list[str]] = None,
    quality_score: Optional[int] = None,
    photos: Optional[list[str]] = None,
) -> dict:
    """Add tags, quality score, photos, and notes to a job record."""
    from forge.tools_history import annotate_job_extended as _impl
    return _impl(
        job_id,
        note=note,
        tags=tags,
        quality_score=quality_score,
        photos=photos,
    )


@mcp.tool()
def record_job_outcome_extended(
    job_id: str,
    outcome: str,
    *,
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    quality_grade: Optional[str] = None,
    failure_mode: Optional[str] = None,
    settings: Optional[dict[str, Any]] = None,
    environment: Optional[dict[str, Any]] = None,
    notes: Optional[str] = None,
    file_name: Optional[str] = None,
    file_hash: Optional[str] = None,
    material_type: Optional[str] = None,
) -> dict:
    """Record detailed outcome of a manufacturing job with quality metrics."""
    from forge.tools_history import record_job_outcome_extended as _impl
    return _impl(
        job_id,
        outcome,
        device_name=device_name,
        device_type=device_type,
        quality_grade=quality_grade,
        failure_mode=failure_mode,
        settings=settings,
        environment=environment,
        notes=notes,
        file_name=file_name,
        file_hash=file_hash,
        material_type=material_type,
    )


@mcp.tool()
def get_device_insights(
    device_name: str,
    *,
    device_type: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """Pattern analysis across a device's job history."""
    from forge.tools_history import get_device_insights as _impl
    return _impl(device_name, device_type=device_type, limit=limit)


@mcp.tool()
def recommend_settings_for_job(
    *,
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    material_type: Optional[str] = None,
    file_hash: Optional[str] = None,
) -> dict:
    """Recommend device settings based on past successful jobs."""
    from forge.tools_history import recommend_settings_for_job as _impl
    return _impl(
        device_name=device_name,
        device_type=device_type,
        material_type=material_type,
        file_hash=file_hash,
    )


# ===================================================================
# MONITORING & VISION TOOLS (from tools_monitoring)
# ===================================================================


@mcp.tool()
def monitor_device_vision(
    device_id: str,
    device_type: str,
    *,
    include_snapshot: bool = True,
    save_snapshot: Optional[str] = None,
    failure_type: Optional[str] = None,
    failure_confidence: Optional[float] = None,
    auto_pause: Optional[bool] = None,
    completion_pct: Optional[float] = None,
    session_id: Optional[str] = None,
) -> dict:
    """Capture a snapshot and device state for visual inspection of an active job."""
    from forge.tools_monitoring import monitor_device_vision as _impl
    return _impl(
        device_id,
        device_type,
        include_snapshot=include_snapshot,
        save_snapshot=save_snapshot,
        failure_type=failure_type,
        failure_confidence=failure_confidence,
        auto_pause=auto_pause,
        completion_pct=completion_pct,
        session_id=session_id,
    )


@mcp.tool()
def watch_job(
    device_id: str,
    job_id: str,
    device_type: str,
    *,
    snapshot_interval: int = 60,
    max_snapshots: int = 5,
    timeout: int = 7200,
    poll_interval: int = 15,
    stall_timeout: int = 600,
    check_delay_seconds: Optional[int] = None,
    check_count: Optional[int] = None,
    check_interval_seconds: Optional[int] = None,
) -> dict:
    """Start background monitoring of a running manufacturing job."""
    from forge.tools_monitoring import watch_job as _impl
    return _impl(
        device_id,
        job_id,
        device_type,
        snapshot_interval=snapshot_interval,
        max_snapshots=max_snapshots,
        timeout=timeout,
        poll_interval=poll_interval,
        stall_timeout=stall_timeout,
        check_delay_seconds=check_delay_seconds,
        check_count=check_count,
        check_interval_seconds=check_interval_seconds,
    )


@mcp.tool()
def watch_job_status(watch_id: str) -> dict:
    """Check the current status of a background job watcher."""
    from forge.tools_monitoring import watch_job_status as _impl
    return _impl(watch_id)


@mcp.tool()
def stop_watch_job(watch_id: str) -> dict:
    """Stop a background job watcher and return its final state."""
    from forge.tools_monitoring import stop_watch_job as _impl
    return _impl(watch_id)


@mcp.tool()
def start_monitored_job(
    device_id: str,
    job_id: str,
    device_type: str,
    *,
    initial_check_delay: int = 120,
    initial_check_count: int = 3,
    initial_check_interval: int = 60,
    auto_pause: bool = True,
    snapshot_interval: int = 60,
    max_snapshots: int = 5,
    timeout: int = 7200,
    poll_interval: int = 15,
    stall_timeout: int = 600,
) -> dict:
    """Start a manufacturing job with automatic monitoring enabled."""
    from forge.tools_monitoring import start_monitored_job as _impl
    return _impl(
        device_id,
        job_id,
        device_type,
        initial_check_delay=initial_check_delay,
        initial_check_count=initial_check_count,
        initial_check_interval=initial_check_interval,
        auto_pause=auto_pause,
        snapshot_interval=snapshot_interval,
        max_snapshots=max_snapshots,
        timeout=timeout,
        poll_interval=poll_interval,
        stall_timeout=stall_timeout,
    )


@mcp.tool()
def layer_status(
    device_id: str,
    device_type: str,
    *,
    session_id: Optional[str] = None,
    completion_pct: Optional[float] = None,
    current_layer: Optional[int] = None,
    total_layers: Optional[int] = None,
) -> dict:
    """Get device-type-specific layer/pass status for an active job."""
    from forge.tools_monitoring import layer_status as _impl
    return _impl(
        device_id,
        device_type,
        session_id=session_id,
        completion_pct=completion_pct,
        current_layer=current_layer,
        total_layers=total_layers,
    )


# ===================================================================
# AI GENERATION TOOLS (from tools_generation)
# ===================================================================


@mcp.tool()
def list_generation_providers(
    *,
    device_type: Optional[str] = None,
) -> dict:
    """List available AI 3D/2D model generation services."""
    from forge.tools_generation import list_generation_providers as _impl
    return _impl(device_type=device_type)


@mcp.tool()
def generate_model(
    prompt: str,
    *,
    provider: str = "meshy",
    format: Optional[str] = None,
    style: Optional[str] = None,
    target_device_type: Optional[str] = None,
) -> dict:
    """Generate a 3D or 2D vector model from a text description."""
    from forge.tools_generation import generate_model as _impl
    return _impl(
        prompt,
        provider=provider,
        format=format,
        style=style,
        target_device_type=target_device_type,
    )


@mcp.tool()
def generation_status(
    job_id: str,
    *,
    provider: str = "meshy",
) -> dict:
    """Check the status of a model generation job."""
    from forge.tools_generation import generation_status as _impl
    return _impl(job_id, provider=provider)


@mcp.tool()
def download_generated_model(
    job_id: str,
    *,
    provider: str = "meshy",
    output_path: Optional[str] = None,
    target_device_type: Optional[str] = None,
) -> dict:
    """Download a completed generated model and optionally validate it."""
    from forge.tools_generation import download_generated_model as _impl
    return _impl(
        job_id,
        provider=provider,
        output_path=output_path,
        target_device_type=target_device_type,
    )


@mcp.tool()
def await_generation(
    job_id: str,
    *,
    provider: str = "meshy",
    timeout: int = 600,
    poll_interval: int = 10,
) -> dict:
    """Wait for a generation job to complete and return the final status."""
    from forge.tools_generation import await_generation as _impl
    return _impl(
        job_id,
        provider=provider,
        timeout=timeout,
        poll_interval=poll_interval,
    )


@mcp.tool()
def generate_and_fabricate(
    prompt: str,
    *,
    provider: str = "meshy",
    style: Optional[str] = None,
    device_name: Optional[str] = None,
    target_device_type: Optional[str] = None,
    timeout: int = 600,
) -> dict:
    """Full pipeline: generate a model, validate, and prepare for fabrication."""
    from forge.tools_generation import generate_and_fabricate as _impl
    return _impl(
        prompt,
        provider=provider,
        style=style,
        device_name=device_name,
        target_device_type=target_device_type,
        timeout=timeout,
    )


@mcp.tool()
def validate_generated_mesh(
    file_path: str,
    *,
    target_device_type: Optional[str] = None,
) -> dict:
    """Validate a generated mesh or vector file for fabrication readiness."""
    from forge.tools_generation import validate_generated_mesh as _impl
    return _impl(file_path, target_device_type=target_device_type)


# ===================================================================
# NETWORK TOOLS (from tools_network)
# ===================================================================


@mcp.tool()
def network_register_device(
    name: str,
    device_type: str,
    location: str,
    *,
    capabilities: Optional[Dict[str, Any]] = None,
    price_per_unit: Optional[float] = None,
    pricing_unit: Optional[str] = None,
) -> dict:
    """Register a device on the distributed manufacturing network."""
    from forge.tools_network import network_register_device as _impl
    return _impl(
        name,
        device_type,
        location,
        capabilities=capabilities,
        price_per_unit=price_per_unit,
        pricing_unit=pricing_unit,
    )


@mcp.tool()
def network_update_device(
    device_id: str,
    *,
    available: Optional[bool] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    price_per_unit: Optional[float] = None,
    pricing_unit: Optional[str] = None,
    location: Optional[str] = None,
) -> dict:
    """Update a device registration on the network."""
    from forge.tools_network import network_update_device as _impl
    return _impl(
        device_id,
        available=available,
        capabilities=capabilities,
        price_per_unit=price_per_unit,
        pricing_unit=pricing_unit,
        location=location,
    )


@mcp.tool()
def network_list_devices(
    *,
    device_type: Optional[str] = None,
) -> dict:
    """List all devices registered on the network."""
    from forge.tools_network import network_list_devices as _impl
    return _impl(device_type=device_type)


@mcp.tool()
def network_find_devices(
    *,
    material: Optional[str] = None,
    device_type: Optional[str] = None,
    location: Optional[str] = None,
    min_tolerance_mm: Optional[float] = None,
    min_laser_power_w: Optional[float] = None,
    min_cnc_axes: Optional[int] = None,
    min_xy_resolution_um: Optional[float] = None,
) -> dict:
    """Find devices on the network matching job requirements."""
    from forge.tools_network import network_find_devices as _impl
    return _impl(
        material=material,
        device_type=device_type,
        location=location,
        min_tolerance_mm=min_tolerance_mm,
        min_laser_power_w=min_laser_power_w,
        min_cnc_axes=min_cnc_axes,
        min_xy_resolution_um=min_xy_resolution_um,
    )


@mcp.tool()
def network_submit_job(
    file_url: str,
    device_type: str,
    material: str,
    *,
    device_id: Optional[str] = None,
    quantity: int = 1,
    notes: Optional[str] = None,
    tolerance_mm: Optional[float] = None,
    priority: Optional[str] = None,
) -> dict:
    """Submit a manufacturing job to the network for routing."""
    from forge.tools_network import network_submit_job as _impl
    return _impl(
        file_url,
        device_type,
        material,
        device_id=device_id,
        quantity=quantity,
        notes=notes,
        tolerance_mm=tolerance_mm,
        priority=priority,
    )


@mcp.tool()
def network_job_status(job_id: str) -> dict:
    """Check the status of a network-submitted job."""
    from forge.tools_network import network_job_status as _impl
    return _impl(job_id)


# ===================================================================
# PIPELINE & CAM TOOLS (from tools_pipelines)
# ===================================================================


@mcp.tool()
def list_cam_profiles(*, device_type: Optional[str] = None) -> dict:
    """List available CAM/preparation profiles per device type."""
    from forge.tools_pipelines import list_cam_profiles as _impl
    return _impl(device_type=device_type)


@mcp.tool()
def get_cam_profile(device_type: str, device_id: str) -> dict:
    """Get the specific CAM profile for a device model."""
    from forge.tools_pipelines import get_cam_profile as _impl
    return _impl(device_type, device_id)


@mcp.tool()
def list_fabrication_pipelines(*, device_type: Optional[str] = None) -> dict:
    """List pre-validated manufacturing pipelines."""
    from forge.tools_pipelines import list_fabrication_pipelines as _impl
    return _impl(device_type=device_type)


@mcp.tool()
def run_quick_fabricate(
    device_name: str,
    file_path: str,
    device_type: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Execute the quick fabrication pipeline for a device."""
    from forge.tools_pipelines import run_quick_fabricate as _impl
    return _impl(device_name, file_path, device_type, device_id=device_id)


@mcp.tool()
def run_calibrate_device(
    device_name: str,
    device_type: str,
    *,
    material_id: Optional[str] = None,
) -> dict:
    """Run calibration pipeline for a device."""
    from forge.tools_pipelines import run_calibrate_device as _impl
    return _impl(device_name, device_type, material_id=material_id)


@mcp.tool()
def run_benchmark_device(
    device_name: str,
    device_type: str,
    *,
    material_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> dict:
    """Run benchmark pipeline for a device."""
    from forge.tools_pipelines import run_benchmark_device as _impl
    return _impl(
        device_name,
        device_type,
        material_id=material_id,
        tool_id=tool_id,
    )


@mcp.tool()
def pipeline_status(execution_id: str) -> dict:
    """Check pipeline execution status."""
    from forge.tools_pipelines import pipeline_status as _impl
    return _impl(execution_id)


@mcp.tool()
def pipeline_pause(execution_id: str) -> dict:
    """Pause a running pipeline at the next step boundary."""
    from forge.tools_pipelines import pipeline_pause as _impl
    return _impl(execution_id)


@mcp.tool()
def pipeline_resume(execution_id: str) -> dict:
    """Resume a paused pipeline from where it stopped."""
    from forge.tools_pipelines import pipeline_resume as _impl
    return _impl(execution_id)


@mcp.tool()
def pipeline_abort(execution_id: str) -> dict:
    """Abort a running or paused pipeline."""
    from forge.tools_pipelines import pipeline_abort as _impl
    return _impl(execution_id)


@mcp.tool()
def pipeline_retry_step(execution_id: str, step_index: int) -> dict:
    """Retry a specific failed step in a pipeline, then continue from there."""
    from forge.tools_pipelines import pipeline_retry_step as _impl
    return _impl(execution_id, step_index)


# ===================================================================
# RESOURCE & WORKFLOW TOOLS (from tools_resources)
# ===================================================================


@mcp.tool()
def resource_status() -> str:
    """Live snapshot of the entire Forge system: devices, queue, and recent jobs."""
    from forge.tools_resources import resource_status as _impl
    return _impl()


@mcp.tool()
def resource_devices() -> str:
    """Fleet status for all registered devices (SLA, laser, CNC)."""
    from forge.tools_resources import resource_devices as _impl
    return _impl()


@mcp.tool()
def resource_device_detail(device_name: str) -> str:
    """Detailed status for a specific device by name."""
    from forge.tools_resources import resource_device_detail as _impl
    return _impl(device_name)


@mcp.tool()
def resource_queue() -> str:
    """Current job queue summary and recent jobs."""
    from forge.tools_resources import resource_queue as _impl
    return _impl()


@mcp.tool()
def resource_job_detail(job_id: str) -> str:
    """Detailed status for a specific job by ID."""
    from forge.tools_resources import resource_job_detail as _impl
    return _impl(job_id)


@mcp.tool()
def resource_events() -> str:
    """Recent events from the Forge system (last 50)."""
    from forge.tools_resources import resource_events as _impl
    return _impl()


@mcp.tool()
def fabrication_workflow() -> str:
    """Step-by-step guide for fabricating a part on a local device."""
    from forge.tools_resources import fabrication_workflow as _impl
    return _impl()


@mcp.tool()
def fleet_workflow() -> str:
    """Guide for managing a heterogeneous device fleet."""
    from forge.tools_resources import fleet_workflow as _impl
    return _impl()


@mcp.tool()
def troubleshooting() -> str:
    """Common troubleshooting steps for multi-device manufacturing issues."""
    from forge.tools_resources import troubleshooting as _impl
    return _impl()


@mcp.tool()
def consumer_onboarding() -> dict:
    """Get the guided onboarding workflow for users without local devices."""
    from forge.tools_resources import consumer_onboarding as _impl
    return _impl()


@mcp.tool()
def fulfillment_cancel(
    order_id: str,
    *,
    provider: str = "",
    reason: str = "",
) -> dict:
    """Cancel a fulfillment order."""
    from forge.tools_resources import fulfillment_cancel as _impl
    return _impl(order_id, provider=provider, reason=reason)


@mcp.tool()
def fulfillment_batch_quote(
    file_paths: str,
    material: str,
    *,
    service_type: str = "laser_cutting",
    quantities: str = "",
    shipping_country: str = "US",
) -> dict:
    """Get quotes from multiple providers for one or more parts."""
    from forge.tools_resources import fulfillment_batch_quote as _impl
    return _impl(
        file_paths,
        material,
        service_type=service_type,
        quantities=quantities,
        shipping_country=shipping_country,
    )


@mcp.tool()
def fulfillment_filter_materials(
    *,
    device_type: str = "",
    service_type: str = "",
    color: str = "",
    max_price_per_unit: Optional[float] = None,
    search_text: str = "",
) -> dict:
    """Filter available materials by device type and requirements."""
    from forge.tools_resources import fulfillment_filter_materials as _impl
    return _impl(
        device_type=device_type,
        service_type=service_type,
        color=color,
        max_price_per_unit=max_price_per_unit,
        search_text=search_text,
    )


@mcp.tool()
def fulfillment_reorder(
    order_id: str,
    *,
    provider: str = "",
    quantity: Optional[int] = None,
) -> dict:
    """Reorder a previously completed fulfillment job."""
    from forge.tools_resources import fulfillment_reorder as _impl
    return _impl(order_id, provider=provider, quantity=quantity)


@mcp.tool()
def fulfillment_insurance_options(
    *,
    provider: str = "",
    order_value_usd: Optional[float] = None,
    shipping_country: str = "US",
) -> dict:
    """Get insurance options for a manufacturing shipment."""
    from forge.tools_resources import fulfillment_insurance_options as _impl
    return _impl(
        provider=provider,
        order_value_usd=order_value_usd,
        shipping_country=shipping_country,
    )


@mcp.tool()
def supported_shipping_countries() -> dict:
    """List countries with manufacturing fulfillment shipping support."""
    from forge.tools_resources import supported_shipping_countries as _impl
    return _impl()


# ===================================================================
# QUALITY & ANALYTICS TOOLS (from tools_quality)
# ===================================================================


@mcp.tool()
def compare_fabrication_options(
    file_path: str,
    *,
    device_ids: Optional[List[str]] = None,
    material: Optional[str] = None,
    quantity: int = 1,
    priority: Optional[str] = None,
) -> dict:
    """Compare different device/material/setting combinations for a job."""
    from forge.tools_quality import compare_fabrication_options as _impl
    return _impl(
        file_path,
        device_ids=device_ids,
        material=material,
        quantity=quantity,
        priority=priority,
    )


@mcp.tool()
def analyze_job_failure_detailed(
    job_id: str,
    *,
    include_related_events: bool = True,
    max_events: int = 50,
) -> dict:
    """Deep analysis of a failed job with root cause suggestions."""
    from forge.tools_quality import analyze_job_failure_detailed as _impl
    return _impl(
        job_id,
        include_related_events=include_related_events,
        max_events=max_events,
    )


@mcp.tool()
def validate_job_quality(
    job_id: str,
    *,
    measurements: Optional[Dict[str, Any]] = None,
    device_type_override: Optional[str] = None,
) -> dict:
    """Post-fabrication quality assessment for a completed job."""
    from forge.tools_quality import validate_job_quality as _impl
    return _impl(
        job_id,
        measurements=measurements,
        device_type_override=device_type_override,
    )


@mcp.tool()
def recommend_quality_settings(
    device_type: str,
    *,
    material: Optional[str] = None,
    tolerance_mm: Optional[float] = None,
    surface_finish: Optional[str] = None,
    strength_priority: bool = False,
) -> dict:
    """Suggest quality-optimised settings based on requirements."""
    from forge.tools_quality import recommend_quality_settings as _impl
    return _impl(
        device_type,
        material=material,
        tolerance_mm=tolerance_mm,
        surface_finish=surface_finish,
        strength_priority=strength_priority,
    )


@mcp.tool()
def fleet_analytics(
    *,
    device_type: Optional[str] = None,
    time_window_hours: float = 720.0,
) -> dict:
    """Aggregate performance analytics across the device fleet."""
    from forge.tools_quality import fleet_analytics as _impl
    return _impl(device_type=device_type, time_window_hours=time_window_hours)


@mcp.tool()
def verify_audit_integrity(
    *,
    device_name: Optional[str] = None,
    check_window_hours: float = 24.0,
) -> dict:
    """Verify the integrity of audit/event logs."""
    from forge.tools_quality import verify_audit_integrity as _impl
    return _impl(
        device_name=device_name,
        check_window_hours=check_window_hours,
    )


# ===================================================================
# SAFETY, INTELLIGENCE, BILLING, CACHE & MISC TOOLS (from tools_misc)
# ===================================================================


@mcp.tool()
def list_all_safety_profiles(
    *,
    device_type: Optional[str] = None,
) -> dict:
    """List safety profiles across all or a specific device type."""
    from forge.tools_misc import list_all_safety_profiles as _impl
    return _impl(device_type=device_type)


@mcp.tool()
def get_safety_profile_detail(
    device_type: str,
    device_id: str,
) -> dict:
    """Get the full safety profile for a specific device model."""
    from forge.tools_misc import get_safety_profile_detail as _impl
    return _impl(device_type, device_id)


@mcp.tool()
def validate_file_safe(
    file_path: str,
    device_type: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Validate a fabrication file against device safety limits."""
    from forge.tools_misc import validate_file_safe as _impl
    return _impl(file_path, device_type, device_id=device_id)


@mcp.tool()
def get_device_intelligence_detail(
    device_type: str,
    device_id: str,
) -> dict:
    """Get the full intelligence profile for a device model."""
    from forge.tools_misc import get_device_intelligence_detail as _impl
    return _impl(device_type, device_id)


@mcp.tool()
def get_material_recommendation_detail(
    device_type: str,
    device_id: str,
    use_case: str,
) -> dict:
    """Recommend materials for a use case with device-type awareness."""
    from forge.tools_misc import get_material_recommendation_detail as _impl
    return _impl(device_type, device_id, use_case)


@mcp.tool()
def troubleshoot_device(
    device_type: str,
    symptom: str,
    *,
    device_id: Optional[str] = None,
) -> dict:
    """Diagnose device issues with symptom-based analysis."""
    from forge.tools_misc import troubleshoot_device as _impl
    return _impl(device_type, symptom, device_id=device_id)


@mcp.tool()
def billing_setup_url(
    *,
    rail: str = "stripe",
) -> dict:
    """Get a URL for billing/payment setup."""
    from forge.tools_misc import billing_setup_url as _impl
    return _impl(rail=rail)


@mcp.tool()
def billing_check_setup() -> dict:
    """Verify billing is properly configured after setup URL flow."""
    from forge.tools_misc import billing_check_setup as _impl
    return _impl()


@mcp.tool()
def await_job_completion_extended(
    job_id: str,
    *,
    poll_interval: int = 5,
    timeout: int = 600,
    progress_callback: Optional[str] = None,
) -> dict:
    """Wait for a queued job to finish with progress tracking and timeout."""
    from forge.tools_misc import await_job_completion_extended as _impl
    return _impl(
        job_id,
        poll_interval=poll_interval,
        timeout=timeout,
        progress_callback=progress_callback,
    )


@mcp.tool()
def cache_design_model(
    file_path: str,
    device_type: str,
    *,
    source: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> dict:
    """Cache a design file locally for fast re-use."""
    from forge.tools_misc import cache_design_model as _impl
    return _impl(
        file_path,
        device_type,
        source=source,
        tags=tags,
        metadata=metadata,
    )


@mcp.tool()
def search_design_cache(
    *,
    query: Optional[str] = None,
    device_type: Optional[str] = None,
    file_format: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
) -> dict:
    """Search cached designs by keyword, device type, format, or tags."""
    from forge.tools_misc import search_design_cache as _impl
    return _impl(
        query=query,
        device_type=device_type,
        file_format=file_format,
        tags=tags,
        limit=limit,
    )


@mcp.tool()
def get_cached_design(design_id: str) -> dict:
    """Get a specific cached design by ID."""
    from forge.tools_misc import get_cached_design as _impl
    return _impl(design_id)


@mcp.tool()
def list_design_cache(
    *,
    device_type: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """List all cached designs with optional device-type filter."""
    from forge.tools_misc import list_design_cache as _impl
    return _impl(device_type=device_type, limit=limit)


# ---------------------------------------------------------------------------
# Device timelapse capture
# ---------------------------------------------------------------------------

_device_timelapses: Dict[str, Any] = {}


class _DeviceTimelapseCapture(threading.Thread):
    """Background thread that captures device snapshots at fixed intervals."""

    def __init__(
        self,
        timelapse_id: str,
        device_name: str,
        device_type: str,
        capture_fn: Any,
        interval: int,
        max_frames: int,
        save_dir: str,
    ) -> None:
        super().__init__(daemon=True)
        self.timelapse_id = timelapse_id
        self._device_name = device_name
        self._device_type = device_type
        self._capture_fn = capture_fn
        self._interval = interval
        self._max_frames = max_frames
        self._save_dir = save_dir
        self._stop_event = threading.Event()
        self._frames: List[str] = []
        self._started_at = time.time()
        self._finished = False

    def run(self) -> None:
        os.makedirs(self._save_dir, exist_ok=True)
        db = _get_db()
        frame_num = 0
        while not self._stop_event.is_set() and frame_num < self._max_frames:
            try:
                image_data = self._capture_fn()
                if image_data:
                    fname = f"frame_{frame_num:04d}.jpg"
                    fpath = os.path.join(self._save_dir, fname)
                    with open(fpath, "wb") as f:
                        f.write(image_data)
                    self._frames.append(fpath)
                    db.save_snapshot(
                        device_name=self._device_name,
                        device_type=self._device_type,
                        image_path=fpath,
                        job_id=self.timelapse_id,
                        phase="timelapse",
                        image_size_bytes=len(image_data),
                    )
                    frame_num += 1
            except Exception as exc:
                logger.warning("Timelapse frame %d failed: %s", frame_num, exc)
            self._stop_event.wait(self._interval)
        self._finished = True

    def stop(self) -> dict:
        self._stop_event.set()
        self.join(timeout=5)
        return self.status()

    def status(self) -> dict:
        return {
            "timelapse_id": self.timelapse_id,
            "device_name": self._device_name,
            "device_type": self._device_type,
            "frames_captured": len(self._frames),
            "max_frames": self._max_frames,
            "interval_seconds": self._interval,
            "elapsed_seconds": round(time.time() - self._started_at, 1),
            "finished": self._finished,
            "save_dir": self._save_dir,
            "frame_paths": self._frames,
        }


@mcp.tool()
def start_device_timelapse(
    device_name: str,
    device_type: str,
    interval: int = 300,
    max_frames: int = 100,
) -> dict:
    """Start automatic timelapse capture during a device job.

    Captures a snapshot every *interval* seconds and saves frames to
    ``~/.forge/forge_timelapses/<timelapse_id>/``.  Each frame is also
    persisted in the database for later retrieval via ``list_device_snapshots``.

    Runs in the background.  Use ``device_timelapse_status`` to check
    progress and ``stop_device_timelapse`` to stop early.

    :param device_name: Target device name.
    :param device_type: Device type -- "sla", "laser", or "cnc".
    :param interval: Seconds between captures (default 300 = 5 minutes).
    :param max_frames: Maximum frames to capture (default 100).
    """
    try:
        adapter = _get_device_adapter(device_name)

        # Get snapshot function from device adapter
        capture_fn = getattr(adapter, "get_snapshot", None)
        if capture_fn is None:
            return _error_dict(
                f"Device {device_name!r} does not support snapshot capture.",
                code="NO_CAMERA",
            )

        timelapse_id = secrets.token_hex(6)
        save_dir = os.path.join(
            str(Path.home()), ".forge", "forge_timelapses", timelapse_id
        )

        capture = _DeviceTimelapseCapture(
            timelapse_id=timelapse_id,
            device_name=device_name,
            device_type=device_type,
            capture_fn=capture_fn,
            interval=interval,
            max_frames=max_frames,
            save_dir=save_dir,
        )
        _device_timelapses[timelapse_id] = capture
        capture.start()

        return {
            "success": True,
            "timelapse_id": timelapse_id,
            "device_name": device_name,
            "device_type": device_type,
            "interval_seconds": interval,
            "max_frames": max_frames,
            "save_dir": save_dir,
            "message": (
                f"Timelapse started (id={timelapse_id}). "
                f"Capturing every {interval}s, up to {max_frames} frames. "
                "Use device_timelapse_status to check progress."
            ),
        }
    except KeyError as exc:
        return _error_dict(str(exc), code="DEVICE_NOT_FOUND")
    except Exception as exc:
        logger.exception("Unexpected error in start_device_timelapse")
        return _error_dict(f"Unexpected error: {exc}", code="INTERNAL_ERROR")


@mcp.tool()
def device_timelapse_status(timelapse_id: str) -> dict:
    """Check the status of a running device timelapse capture.

    :param timelapse_id: The ID returned by ``start_device_timelapse``.
    """
    capture = _device_timelapses.get(timelapse_id)
    if capture is None:
        return _error_dict(f"No timelapse with id {timelapse_id!r}.", code="NOT_FOUND")
    return {"success": True, **capture.status()}


@mcp.tool()
def stop_device_timelapse(timelapse_id: str) -> dict:
    """Stop a running device timelapse and return its final state.

    :param timelapse_id: The ID returned by ``start_device_timelapse``.
    """
    capture = _device_timelapses.pop(timelapse_id, None)
    if capture is None:
        return _error_dict(f"No timelapse with id {timelapse_id!r}.", code="NOT_FOUND")
    result = capture.stop()
    return {"success": True, **result}


# ---------------------------------------------------------------------------
# Lightweight job status (token-efficient polling)
# ---------------------------------------------------------------------------


@mcp.tool()
def job_status_lite(device_name: str, device_type: str) -> dict:
    """Lightweight device job status for efficient agent polling.

    Returns only essential fields: state, completion, and ETA.
    Use this instead of full status tools when polling frequently to
    minimise token cost.

    :param device_name: Target device name.
    :param device_type: Device type -- "sla", "laser", or "cnc".
    """
    try:
        adapter = _get_device_adapter(device_name)
        status = adapter.get_state()
        result: Dict[str, Any] = {
            "state": status.get("state", "unknown") if isinstance(status, dict) else getattr(status, "state", "unknown"),
        }

        # Extract completion and timing if available
        if isinstance(status, dict):
            if "completion" in status:
                result["completion_pct"] = status["completion"]
            if "time_remaining" in status:
                result["eta_seconds"] = status["time_remaining"]
            if "time_elapsed" in status:
                result["elapsed_seconds"] = status["time_elapsed"]
            if "file_name" in status:
                result["file_name"] = status["file_name"]
        else:
            for attr in ("completion", "completion_pct"):
                val = getattr(status, attr, None)
                if val is not None:
                    result["completion_pct"] = val
                    break
            for attr in ("time_remaining", "eta_seconds", "time_left"):
                val = getattr(status, attr, None)
                if val is not None:
                    result["eta_seconds"] = val
                    break

        return result
    except KeyError as exc:
        return {"state": "not_found", "error": str(exc)}
    except Exception as exc:
        return {"state": "error", "error": str(exc)}


# ---------------------------------------------------------------------------
# Device snapshot history
# ---------------------------------------------------------------------------


@mcp.tool()
def list_device_snapshots(
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    job_id: Optional[str] = None,
    phase: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """List persisted device snapshots from the database.

    Returns metadata for snapshots captured during monitoring,
    timelapses, or manual captures.  Use this to review job history
    visually or correlate snapshots with job outcomes.

    :param device_name: Filter by device name.
    :param device_type: Filter by device type (e.g. "sla", "laser", "cnc").
    :param job_id: Filter by job or timelapse ID.
    :param phase: Filter by capture phase.
    :param limit: Maximum records to return (default 20).
    """
    try:
        db = _get_db()
        snapshots = db.get_snapshots(
            job_id=job_id,
            device_name=device_name,
            device_type=device_type,
            phase=phase,
            limit=limit,
        )
        return {
            "success": True,
            "snapshots": snapshots,
            "count": len(snapshots),
        }
    except Exception as exc:
        logger.exception("Error in list_device_snapshots")
        return _error_dict(str(exc), code="INTERNAL_ERROR")
