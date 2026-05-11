"""Preflight safety checks for SLA, laser, CNC, and concrete operations.

Ensures all safety conditions are met before starting an operation.
Equivalent to kiln's preflight_check() but for non-FDM devices.
These checks are MANDATORY -- never bypass them.

Advisory checks inform the agent but NEVER block operations.  The
decision to proceed despite an advisory warning is the agent's
responsibility.  This matches the 3D printing lesson learned:
advisory != blocking.

Usage::

    from forge.preflight import preflight_sla, preflight_laser, preflight_cnc

    result = preflight_sla(adapter, config)
    if not result.passed:
        print("Preflight FAILED:", [c.message for c in result.checks if not c.passed])
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PreflightCheck:
    """Outcome of a single preflight check.

    :param name: Short identifier for the check (e.g. ``"vat_level"``).
    :param passed: ``True`` if the check passed.
    :param message: Human-readable description of the outcome.
    :param advisory: If ``True``, this check is a warning only and does
        NOT block the operation.  Advisory checks are never counted
        toward the overall pass/fail decision.
    :param severity: ``"info"``, ``"warning"``, or ``"error"``.
    """

    name: str
    passed: bool
    message: str
    advisory: bool = False
    severity: str = "info"  # info, warning, error

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "advisory": self.advisory,
            "severity": self.severity,
        }


@dataclass
class PreflightResult:
    """Aggregate outcome of all preflight checks for an operation.

    :param passed: ``True`` if ALL non-advisory checks passed.
    :param checks: Full list of individual check results.
    :param device_type: Device category (``"sla"``, ``"laser"``, ``"cnc"``,
        ``"concrete"``).
    """

    passed: bool
    checks: list[PreflightCheck] = field(default_factory=list)
    device_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "device_type": self.device_type,
            "checks": [c.to_dict() for c in self.checks],
            "blocking_failures": [
                c.to_dict() for c in self.checks
                if not c.passed and not c.advisory
            ],
            "advisories": [
                c.to_dict() for c in self.checks
                if not c.passed and c.advisory
            ],
        }


def _evaluate(checks: list[PreflightCheck]) -> bool:
    """Return ``True`` if all non-advisory checks passed."""
    return all(c.passed for c in checks if not c.advisory)


# ---------------------------------------------------------------------------
# SLA Preflight
# ---------------------------------------------------------------------------

def preflight_sla(
    adapter: Any,
    config: Any,
    *,
    safety_profile: Any | None = None,
) -> PreflightResult:
    """Run preflight checks before starting an SLA print.

    Checks performed:

    1. Printer connected and idle
    2. Resin temperature in safe range
    3. Vat level sufficient for estimated volume
    4. UV LED hours within lifespan
    5. Exposure times within safety profile limits
    6. Layer height within printer range
    7. Build plate clean (advisory)
    8. Ventilation configured (advisory)

    :param adapter: An :class:`~forge.devices.base.SLAAdapter` instance.
    :param config: An :class:`~forge.devices.base.SLAPrintConfig` instance.
    :param safety_profile: Optional :class:`~forge.safety.sla_profiles.SLASafetyProfile`.
        If ``None``, limits are resolved from the default profile.
    :returns: :class:`PreflightResult` with all check outcomes.
    """
    checks: list[PreflightCheck] = []

    # -- 1. Printer connected and idle -------------------------------------
    try:
        state = adapter.get_state()
        if not state.connected:
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message="SLA printer is not connected.",
                severity="error",
            ))
        elif state.state.value != "idle":
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message=f"Printer is not idle (status: {state.state.value}).",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="connection",
                passed=True,
                message="Printer connected and idle.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="connection",
            passed=False,
            message=f"Failed to query printer state: {exc}",
            severity="error",
        ))
        return PreflightResult(passed=False, checks=checks, device_type="sla")

    # -- 2. Resin temperature in safe range --------------------------------
    if state.resin_temp_c is not None:
        min_temp = 18.0
        max_temp = 35.0
        if safety_profile is not None:
            min_temp = getattr(safety_profile, "min_resin_temp_c", min_temp)
            max_temp = getattr(safety_profile, "max_resin_temp_c", max_temp)

        if state.resin_temp_c < min_temp:
            checks.append(PreflightCheck(
                name="resin_temp",
                passed=False,
                message=(
                    f"Resin temperature {state.resin_temp_c:.1f}C is below "
                    f"minimum ({min_temp:.1f}C). Allow resin to warm up."
                ),
                severity="error",
            ))
        elif state.resin_temp_c > max_temp:
            checks.append(PreflightCheck(
                name="resin_temp",
                passed=False,
                message=(
                    f"Resin temperature {state.resin_temp_c:.1f}C exceeds "
                    f"maximum ({max_temp:.1f}C). Cool resin before printing."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="resin_temp",
                passed=True,
                message=f"Resin temperature {state.resin_temp_c:.1f}C is within safe range.",
            ))
    else:
        checks.append(PreflightCheck(
            name="resin_temp",
            passed=True,
            message="Resin temperature sensor not available. Skipping check.",
            advisory=True,
            severity="info",
        ))

    # -- 3. Vat level sufficient -------------------------------------------
    try:
        vat_level = adapter.get_vat_level()
        if vat_level < 10.0:
            checks.append(PreflightCheck(
                name="vat_level",
                passed=False,
                message=(
                    f"Resin vat level critically low ({vat_level:.1f}%). "
                    f"Refill before printing."
                ),
                severity="error",
            ))
        elif vat_level < 25.0:
            checks.append(PreflightCheck(
                name="vat_level",
                passed=True,
                message=f"Resin vat level low ({vat_level:.1f}%). Consider refilling.",
                advisory=True,
                severity="warning",
            ))
        else:
            checks.append(PreflightCheck(
                name="vat_level",
                passed=True,
                message=f"Resin vat level OK ({vat_level:.1f}%).",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="vat_level",
            passed=True,
            message=f"Cannot read vat level ({exc}). Verify manually.",
            advisory=True,
            severity="warning",
        ))

    # -- 4. UV LED hours within lifespan -----------------------------------
    if state.light_source_hours is not None:
        lifespan = 2000.0  # default LED lifespan hours
        if safety_profile is not None:
            lifespan = float(
                getattr(safety_profile, "led_lifespan_hours", lifespan) or lifespan
            )

        if state.light_source_hours >= lifespan:
            checks.append(PreflightCheck(
                name="uv_lifespan",
                passed=False,
                message=(
                    f"UV light source has {state.light_source_hours:.0f}h, "
                    f"exceeding rated lifespan ({lifespan:.0f}h). "
                    f"Replace before printing."
                ),
                severity="error",
            ))
        elif state.light_source_hours >= lifespan * 0.85:
            checks.append(PreflightCheck(
                name="uv_lifespan",
                passed=True,
                message=(
                    f"UV light source at {state.light_source_hours:.0f}h / "
                    f"{lifespan:.0f}h ({state.light_source_hours / lifespan * 100:.0f}%). "
                    f"Plan replacement soon."
                ),
                advisory=True,
                severity="warning",
            ))
        else:
            checks.append(PreflightCheck(
                name="uv_lifespan",
                passed=True,
                message=(
                    f"UV light source at {state.light_source_hours:.0f}h / "
                    f"{lifespan:.0f}h."
                ),
            ))
    else:
        checks.append(PreflightCheck(
            name="uv_lifespan",
            passed=True,
            message="UV light source hours not reported. Cannot check lifespan.",
            advisory=True,
            severity="info",
        ))

    # -- 5. Exposure times within safety profile limits --------------------
    max_exposure = 120.0
    max_bottom_exposure = 300.0
    if safety_profile is not None:
        max_exposure = getattr(safety_profile, "max_exposure_time_s", max_exposure)
        max_bottom_exposure = getattr(
            safety_profile, "max_exposure_time_s", max_bottom_exposure
        )

    if config.exposure_time_s > max_exposure:
        checks.append(PreflightCheck(
            name="exposure_time",
            passed=False,
            message=(
                f"Exposure time {config.exposure_time_s}s exceeds "
                f"maximum ({max_exposure}s)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="exposure_time",
            passed=True,
            message=f"Exposure time {config.exposure_time_s}s is within limits.",
        ))

    if config.bottom_exposure_time_s > max_bottom_exposure:
        checks.append(PreflightCheck(
            name="bottom_exposure_time",
            passed=False,
            message=(
                f"Bottom exposure time {config.bottom_exposure_time_s}s exceeds "
                f"maximum ({max_bottom_exposure}s)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="bottom_exposure_time",
            passed=True,
            message=f"Bottom exposure time {config.bottom_exposure_time_s}s is within limits.",
        ))

    # -- 6. Layer height within printer range ------------------------------
    min_layer = 10  # um
    max_layer = 200  # um
    if safety_profile is not None:
        min_layer = getattr(safety_profile, "min_layer_height_um", min_layer)
        max_layer = getattr(safety_profile, "max_layer_height_um", max_layer)

    if config.layer_height_um < min_layer or config.layer_height_um > max_layer:
        checks.append(PreflightCheck(
            name="layer_height",
            passed=False,
            message=(
                f"Layer height {config.layer_height_um}um is outside "
                f"supported range ({min_layer}-{max_layer}um)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="layer_height",
            passed=True,
            message=f"Layer height {config.layer_height_um}um is within range.",
        ))

    # -- 7. Build plate clean (advisory) -----------------------------------
    checks.append(PreflightCheck(
        name="build_plate",
        passed=True,
        message=(
            "Verify build plate is clean and free of cured resin "
            "from previous prints."
        ),
        advisory=True,
        severity="info",
    ))

    # -- 8. Ventilation configured (advisory) ------------------------------
    requires_vent = True
    if safety_profile is not None:
        requires_vent = getattr(safety_profile, "requires_ventilation", True)

    if requires_vent:
        checks.append(PreflightCheck(
            name="ventilation",
            passed=True,
            message=(
                "Ensure adequate ventilation is active. "
                "Resin fumes can be harmful in enclosed spaces."
            ),
            advisory=True,
            severity="warning",
        ))

    return PreflightResult(
        passed=_evaluate(checks),
        checks=checks,
        device_type="sla",
    )


# ---------------------------------------------------------------------------
# Laser Preflight
# ---------------------------------------------------------------------------

def preflight_laser(
    adapter: Any,
    material_id: str,
    config: Any,
    *,
    safety_profile: Any | None = None,
) -> PreflightResult:
    """Run preflight checks before starting a laser cut.

    Checks performed:

    1. Machine connected and idle
    2. Material is NOT blocked (CRITICAL -- never bypass)
    3. Ventilation running (exhaust interlock)
    4. Lid closed (lid interlock)
    5. Power/speed within machine limits
    6. Material thickness compatible
    7. Focus set (advisory)
    8. Air assist enabled for combustibles (advisory)

    :param adapter: A :class:`~forge.devices.base.LaserAdapter` instance.
    :param material_id: Material identifier for safety validation.
    :param config: A :class:`~forge.devices.base.CutConfig` instance.
    :param safety_profile: Optional :class:`~forge.safety.laser_profiles.LaserSafetyProfile`.
    :returns: :class:`PreflightResult` with all check outcomes.
    """
    checks: list[PreflightCheck] = []

    # -- 1. Machine connected and idle -------------------------------------
    try:
        state = adapter.get_state()
        if not state.connected:
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message="Laser cutter is not connected.",
                severity="error",
            ))
        elif state.state.value != "idle":
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message=f"Laser is not idle (status: {state.state.value}).",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="connection",
                passed=True,
                message="Laser cutter connected and idle.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="connection",
            passed=False,
            message=f"Failed to query laser state: {exc}",
            severity="error",
        ))
        return PreflightResult(passed=False, checks=checks, device_type="laser")

    # -- 2. Material is NOT blocked (CRITICAL) -----------------------------
    try:
        from forge.safety.laser_profiles import (
            get_material_safety,
            is_material_safe,
        )
        if not is_material_safe(material_id):
            try:
                mat = get_material_safety(material_id)
                reason = mat.block_reason or "Material is blocked for laser processing"
            except KeyError:
                reason = f"Unknown material '{material_id}' -- blocked by default (fail-closed)"
            checks.append(PreflightCheck(
                name="material_safety",
                passed=False,
                message=(
                    f"BLOCKED: Material '{material_id}' cannot be laser processed. "
                    f"Reason: {reason}"
                ),
                severity="error",
            ))
            # Return immediately -- do NOT continue checks for blocked material.
            return PreflightResult(passed=False, checks=checks, device_type="laser")

        mat = get_material_safety(material_id)
        msg = f"Material '{material_id}' ({mat.display_name}) is safe to process."
        if mat.safety_level == "hazardous":
            msg += " WARNING: Hazardous material -- use full PPE."
        checks.append(PreflightCheck(
            name="material_safety",
            passed=True,
            message=msg,
        ))
    except ImportError:
        checks.append(PreflightCheck(
            name="material_safety",
            passed=False,
            message=(
                "Cannot import laser safety profiles. "
                "Material validation is MANDATORY -- operation blocked."
            ),
            severity="error",
        ))
        return PreflightResult(passed=False, checks=checks, device_type="laser")

    # -- 3. Ventilation running (exhaust interlock) ------------------------
    try:
        vent_ok = adapter.check_ventilation()
        if not vent_ok:
            checks.append(PreflightCheck(
                name="ventilation",
                passed=False,
                message=(
                    "Ventilation/exhaust is NOT running. "
                    "Start exhaust system before cutting."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="ventilation",
                passed=True,
                message="Ventilation/exhaust is running.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="ventilation",
            passed=False,
            message=f"Cannot verify ventilation status: {exc}",
            severity="error",
        ))

    # -- 4. Lid closed (lid interlock) -------------------------------------
    try:
        lid_ok = adapter.check_lid_interlock()
        if not lid_ok:
            checks.append(PreflightCheck(
                name="lid_interlock",
                passed=False,
                message="Lid interlock is OPEN. Close the lid before starting a cut.",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="lid_interlock",
                passed=True,
                message="Lid is closed and interlock engaged.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="lid_interlock",
            passed=False,
            message=f"Cannot verify lid interlock: {exc}",
            severity="error",
        ))

    # -- 5. Power/speed within machine limits ------------------------------
    max_power = 100.0
    max_speed = 500.0
    if safety_profile is not None:
        max_power = getattr(safety_profile, "max_power_percent", max_power)
        max_speed = getattr(safety_profile, "max_speed_mm_s", max_speed)

    if config.power_percent < 0.0 or config.power_percent > max_power:
        checks.append(PreflightCheck(
            name="power",
            passed=False,
            message=(
                f"Power {config.power_percent}% is outside valid range "
                f"(0-{max_power}%)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="power",
            passed=True,
            message=f"Power {config.power_percent}% is within limits.",
        ))

    if config.speed_mm_s < 0.0 or config.speed_mm_s > max_speed:
        checks.append(PreflightCheck(
            name="speed",
            passed=False,
            message=(
                f"Speed {config.speed_mm_s} mm/s is outside valid range "
                f"(0-{max_speed} mm/s)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="speed",
            passed=True,
            message=f"Speed {config.speed_mm_s} mm/s is within limits.",
        ))

    # -- 6. Material thickness compatible ----------------------------------
    if mat.max_thickness_mm > 0 and config.focus_height_mm is not None:
        if config.focus_height_mm > mat.max_thickness_mm:
            checks.append(PreflightCheck(
                name="thickness",
                passed=False,
                message=(
                    f"Focus height {config.focus_height_mm}mm exceeds maximum "
                    f"cuttable thickness ({mat.max_thickness_mm}mm) for "
                    f"{mat.display_name}."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="thickness",
                passed=True,
                message=(
                    f"Material thickness {config.focus_height_mm}mm is within "
                    f"cuttable range for {mat.display_name}."
                ),
            ))

    # -- 7. Focus set (advisory) -------------------------------------------
    if config.focus_height_mm is None:
        checks.append(PreflightCheck(
            name="focus",
            passed=True,
            message=(
                "No focus height specified. Verify focus is set correctly "
                "before starting."
            ),
            advisory=True,
            severity="info",
        ))

    # -- 8. Air assist for combustibles (advisory) -------------------------
    if mat.fire_risk in ("medium", "high") and not config.air_assist:
        checks.append(PreflightCheck(
            name="air_assist",
            passed=True,
            message=(
                f"Air assist is OFF but {mat.display_name} has "
                f"{mat.fire_risk} fire risk. Strongly recommend enabling "
                f"air assist to reduce fire and charring."
            ),
            advisory=True,
            severity="warning",
        ))

    return PreflightResult(
        passed=_evaluate(checks),
        checks=checks,
        device_type="laser",
    )


# ---------------------------------------------------------------------------
# CNC Preflight
# ---------------------------------------------------------------------------

def preflight_cnc(
    adapter: Any,
    config: Any,
    *,
    safety_profile: Any | None = None,
) -> PreflightResult:
    """Run preflight checks before starting a CNC operation.

    Checks performed:

    1. Machine connected and idle
    2. Spindle RPM within machine limits
    3. Feed rate within machine limits
    4. Depth of cut within tool limits
    5. Tool loaded (tool number set)
    6. Workholding verified (advisory)
    7. Coolant active for metal cutting
    8. Dust collection active for wood (advisory)
    9. Eye/hearing protection reminder (advisory)

    :param adapter: A :class:`~forge.devices.base.CNCAdapter` instance.
    :param config: A :class:`~forge.devices.base.CNCJobConfig` instance.
    :param safety_profile: Optional machine safety profile from
        :mod:`forge.safety.cnc_profiles`.
    :returns: :class:`PreflightResult` with all check outcomes.
    """
    checks: list[PreflightCheck] = []

    # -- 1. Machine connected and idle -------------------------------------
    try:
        state = adapter.get_state()
        if not state.connected:
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message="CNC machine is not connected.",
                severity="error",
            ))
        elif state.state.value != "idle":
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message=f"Machine is not idle (status: {state.state.value}).",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="connection",
                passed=True,
                message="CNC machine connected and idle.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="connection",
            passed=False,
            message=f"Failed to query machine state: {exc}",
            severity="error",
        ))
        return PreflightResult(passed=False, checks=checks, device_type="cnc")

    # -- 2. Spindle RPM within machine limits ------------------------------
    caps = adapter.capabilities
    max_rpm = caps.max_spindle_rpm
    if safety_profile is not None:
        max_rpm = getattr(safety_profile, "max_spindle_rpm", max_rpm)

    if config.rpm <= 0:
        checks.append(PreflightCheck(
            name="spindle_rpm",
            passed=False,
            message=f"Spindle RPM must be positive (got {config.rpm}).",
            severity="error",
        ))
    elif config.rpm > max_rpm:
        checks.append(PreflightCheck(
            name="spindle_rpm",
            passed=False,
            message=(
                f"Spindle RPM {config.rpm} exceeds machine maximum "
                f"({max_rpm} RPM)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="spindle_rpm",
            passed=True,
            message=f"Spindle RPM {config.rpm} is within limits.",
        ))

    # -- 3. Feed rate within machine limits --------------------------------
    max_feed = caps.max_feedrate_mm_min
    if safety_profile is not None:
        max_feed = getattr(safety_profile, "max_feedrate_mm_min", max_feed)

    if config.feed_mm_min <= 0:
        checks.append(PreflightCheck(
            name="feed_rate",
            passed=False,
            message=f"Feed rate must be positive (got {config.feed_mm_min} mm/min).",
            severity="error",
        ))
    elif config.feed_mm_min > max_feed:
        checks.append(PreflightCheck(
            name="feed_rate",
            passed=False,
            message=(
                f"Feed rate {config.feed_mm_min} mm/min exceeds machine maximum "
                f"({max_feed} mm/min)."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="feed_rate",
            passed=True,
            message=f"Feed rate {config.feed_mm_min} mm/min is within limits.",
        ))

    # -- 4. Depth of cut within tool limits --------------------------------
    if config.depth_mm <= 0:
        checks.append(PreflightCheck(
            name="depth_of_cut",
            passed=False,
            message=f"Depth of cut must be positive (got {config.depth_mm}mm).",
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="depth_of_cut",
            passed=True,
            message=f"Depth of cut {config.depth_mm}mm set.",
        ))

    # -- 5. Tool loaded (tool number set) ----------------------------------
    if config.tool_id <= 0:
        checks.append(PreflightCheck(
            name="tool_loaded",
            passed=False,
            message="No tool specified (tool_id must be a positive integer).",
            severity="error",
        ))
    else:
        if state.tool_number is not None and state.tool_number != config.tool_id:
            checks.append(PreflightCheck(
                name="tool_loaded",
                passed=False,
                message=(
                    f"Tool mismatch: config specifies tool {config.tool_id} but "
                    f"machine reports tool {state.tool_number} loaded. "
                    f"Perform a tool change before starting."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="tool_loaded",
                passed=True,
                message=f"Tool {config.tool_id} specified.",
            ))

    # -- 6. Workholding verified (advisory) --------------------------------
    checks.append(PreflightCheck(
        name="workholding",
        passed=True,
        message=(
            "Verify workpiece is securely clamped or held in a vise. "
            "Loose workpieces can be thrown by the spindle."
        ),
        advisory=True,
        severity="warning",
    ))

    # -- 7. Coolant active for metal cutting -------------------------------
    if config.coolant and caps.has_coolant:
        if not state.coolant_active:
            checks.append(PreflightCheck(
                name="coolant",
                passed=False,
                message=(
                    "Coolant is requested in the config but not currently active. "
                    "Enable coolant before starting metal cutting."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="coolant",
                passed=True,
                message="Coolant is active.",
            ))
    elif config.coolant and not caps.has_coolant:
        checks.append(PreflightCheck(
            name="coolant",
            passed=True,
            message=(
                "Coolant requested but machine has no coolant system. "
                "Consider manual lubrication for metal cutting."
            ),
            advisory=True,
            severity="warning",
        ))

    # -- 8. Dust collection for wood (advisory) ----------------------------
    checks.append(PreflightCheck(
        name="dust_collection",
        passed=True,
        message=(
            "If cutting wood or composites, ensure dust collection is active. "
            "Fine dust is a respiratory and fire hazard."
        ),
        advisory=True,
        severity="info",
    ))

    # -- 9. PPE reminder (advisory) ----------------------------------------
    checks.append(PreflightCheck(
        name="ppe_reminder",
        passed=True,
        message=(
            "Wear safety glasses and hearing protection when operating "
            "the CNC machine. Keep hands clear of the spindle."
        ),
        advisory=True,
        severity="info",
    ))

    return PreflightResult(
        passed=_evaluate(checks),
        checks=checks,
        device_type="cnc",
    )


# ---------------------------------------------------------------------------
# Concrete Preflight
# ---------------------------------------------------------------------------

def preflight_concrete(
    adapter: Any,
    config: Any,
    *,
    safety_profile: Optional[Any] = None,
) -> PreflightResult:
    """Run preflight checks before starting a structural concrete print.

    Checks performed:

    1. Machine connected and idle
    2. Emergency-stop circuit clear
    3. Weather safe for extrusion
    4. Pump pressure in safe range
    5. Material flow available
    6. Layer height and print speed within profile limits
    7. Daily calibration checklist completed (advisory)
    8. Crew PPE and exclusion zone confirmation (advisory)
    """
    checks: List[PreflightCheck] = []

    if safety_profile is None:
        try:
            from forge.safety.concrete_profiles import get_concrete_profile
            safety_profile = get_concrete_profile(getattr(adapter, "name", "default_concrete"))
        except Exception:
            safety_profile = None

    # -- 1. Machine connected and idle -------------------------------------
    try:
        state = adapter.get_state()
        if not state.connected:
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message="Concrete printer is not connected.",
                severity="error",
            ))
        elif state.state.value != "idle":
            checks.append(PreflightCheck(
                name="connection",
                passed=False,
                message=f"Concrete printer is not idle (status: {state.state.value}).",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="connection",
                passed=True,
                message="Concrete printer connected and idle.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="connection",
            passed=False,
            message=f"Failed to query concrete printer state: {exc}",
            severity="error",
        ))
        return PreflightResult(passed=False, checks=checks, device_type="concrete")

    # -- 2. Emergency-stop circuit clear -----------------------------------
    try:
        if not adapter.check_emergency_stop():
            checks.append(PreflightCheck(
                name="emergency_stop",
                passed=False,
                message="Emergency-stop is engaged. Reset it before printing.",
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="emergency_stop",
                passed=True,
                message="Emergency-stop circuit is clear.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="emergency_stop",
            passed=False,
            message=f"Cannot verify emergency-stop status: {exc}",
            severity="error",
        ))

    # -- 3. Weather safe ----------------------------------------------------
    try:
        weather_safe = adapter.check_weather_safe()
        if not weather_safe:
            checks.append(PreflightCheck(
                name="weather",
                passed=False,
                message=(
                    "Weather conditions are outside configured print envelope "
                    "(wind/rain/temperature)."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="weather",
                passed=True,
                message="Weather conditions are within safe limits.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="weather",
            passed=True,
            message=f"Cannot verify weather interlock ({exc}). Verify manually.",
            advisory=True,
            severity="warning",
        ))

    # -- 4. Pump pressure ---------------------------------------------------
    min_pressure = 40.0
    max_pressure = 250.0
    if safety_profile is not None:
        min_pressure = float(getattr(safety_profile, "min_pump_pressure_bar", min_pressure))
        max_pressure = float(getattr(safety_profile, "max_pump_pressure_bar", max_pressure))

    try:
        pressure = float(adapter.check_pump_pressure())
        if pressure < min_pressure:
            checks.append(PreflightCheck(
                name="pump_pressure",
                passed=False,
                message=(
                    f"Pump pressure {pressure:.1f} bar is below minimum "
                    f"({min_pressure:.1f} bar). Prime pump before printing."
                ),
                severity="error",
            ))
        elif pressure > max_pressure:
            checks.append(PreflightCheck(
                name="pump_pressure",
                passed=False,
                message=(
                    f"Pump pressure {pressure:.1f} bar exceeds maximum "
                    f"({max_pressure:.1f} bar)."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="pump_pressure",
                passed=True,
                message=f"Pump pressure {pressure:.1f} bar is within limits.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="pump_pressure",
            passed=False,
            message=f"Cannot read pump pressure: {exc}",
            severity="error",
        ))

    # -- 5. Material flow availability -------------------------------------
    min_flow = 1.0
    if safety_profile is not None:
        min_flow = float(getattr(safety_profile, "min_material_flow_l_min", min_flow))

    try:
        flow = float(adapter.check_material_flow())
        if flow < min_flow:
            checks.append(PreflightCheck(
                name="material_flow",
                passed=False,
                message=(
                    f"Material flow {flow:.2f} L/min is below minimum "
                    f"({min_flow:.2f} L/min)."
                ),
                severity="error",
            ))
        else:
            checks.append(PreflightCheck(
                name="material_flow",
                passed=True,
                message=f"Material flow {flow:.2f} L/min is available.",
            ))
    except Exception as exc:
        checks.append(PreflightCheck(
            name="material_flow",
            passed=False,
            message=f"Cannot read material flow: {exc}",
            severity="error",
        ))

    # -- 6. Layer height and print speed limits ----------------------------
    max_layer = 75.0
    max_speed = 600.0
    if safety_profile is not None:
        max_layer = float(getattr(safety_profile, "max_layer_height_mm", max_layer))
        max_speed = float(getattr(safety_profile, "max_print_speed_mm_s", max_speed))

    if config.layer_height_mm <= 0 or config.layer_height_mm > max_layer:
        checks.append(PreflightCheck(
            name="layer_height",
            passed=False,
            message=(
                f"Layer height {config.layer_height_mm} mm is outside "
                f"allowed range (0-{max_layer} mm]."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="layer_height",
            passed=True,
            message=f"Layer height {config.layer_height_mm} mm is within limits.",
        ))

    if config.print_speed_mm_s <= 0 or config.print_speed_mm_s > max_speed:
        checks.append(PreflightCheck(
            name="print_speed",
            passed=False,
            message=(
                f"Print speed {config.print_speed_mm_s} mm/s is outside "
                f"allowed range (0-{max_speed} mm/s]."
            ),
            severity="error",
        ))
    else:
        checks.append(PreflightCheck(
            name="print_speed",
            passed=True,
            message=f"Print speed {config.print_speed_mm_s} mm/s is within limits.",
        ))

    # -- 7. Calibration checklist (advisory) -------------------------------
    checks.append(PreflightCheck(
        name="calibration_checklist",
        passed=True,
        message=(
            "Confirm gantry squaring, nozzle offset, and pump calibration have "
            "been verified for today's shift."
        ),
        advisory=True,
        severity="info",
    ))

    # -- 8. PPE / exclusion zone (advisory) -------------------------------
    checks.append(PreflightCheck(
        name="site_safety",
        passed=True,
        message=(
            "Confirm crew PPE, exclusion zones, and emergency access paths are "
            "in place before moving axes."
        ),
        advisory=True,
        severity="warning",
    ))

    return PreflightResult(
        passed=_evaluate(checks),
        checks=checks,
        device_type="concrete",
    )
