"""Concrete print parameter validator for structural 3D printing jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from forge.safety.concrete_profiles import ConcreteSafetyProfile


@dataclass(frozen=True)
class ConcreteValidationResult:
    """Result of validating concrete print parameters and interlocks."""

    valid: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    blocked_params: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "blocked_params": list(self.blocked_params),
        }


def _float(config: Dict[str, Any], key: str, default: float) -> float:
    value = config.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def validate_concrete_params(
    config: Dict[str, Any],
    *,
    profile: Optional[ConcreteSafetyProfile] = None,
    emergency_stop_clear: bool = True,
    weather_safe: bool = True,
) -> ConcreteValidationResult:
    """Validate a concrete print config against profile limits.

    When no profile is provided, a conservative fallback envelope is used.
    """
    warnings: list[str] = []
    errors: list[str] = []
    blocked: list[str] = []

    min_speed = 50.0
    max_speed = 500.0
    min_layer = 8.0
    max_layer = 60.0
    min_pressure = 40.0
    max_pressure = 230.0
    min_flow = 2.0
    max_flow = 80.0

    if profile is not None:
        min_speed = profile.min_print_speed_mm_s
        max_speed = profile.max_print_speed_mm_s
        min_layer = profile.min_layer_height_mm
        max_layer = profile.max_layer_height_mm
        min_pressure = profile.min_pump_pressure_bar
        max_pressure = profile.max_pump_pressure_bar
        min_flow = profile.min_material_flow_l_min
        max_flow = profile.max_material_flow_l_min

    layer_height = _float(config, "layer_height_mm", min_layer)
    speed = _float(config, "print_speed_mm_s", min_speed)
    pressure = _float(config, "pump_pressure_bar", min_pressure)
    flow = _float(config, "extrusion_rate_l_min", min_flow)

    if not emergency_stop_clear:
        errors.append("Emergency-stop is engaged.")
        blocked.append("emergency_stop")
    if not weather_safe:
        errors.append("Weather interlock reports unsafe conditions.")
        blocked.append("weather_safe")

    if layer_height < min_layer or layer_height > max_layer:
        errors.append(
            f"layer_height_mm {layer_height} out of range ({min_layer}-{max_layer})"
        )
        blocked.append("layer_height_mm")
    elif layer_height > max_layer * 0.9:
        warnings.append(
            f"layer_height_mm {layer_height} is near profile maximum ({max_layer})."
        )

    if speed < min_speed or speed > max_speed:
        errors.append(f"print_speed_mm_s {speed} out of range ({min_speed}-{max_speed})")
        blocked.append("print_speed_mm_s")
    elif speed > max_speed * 0.9:
        warnings.append(
            f"print_speed_mm_s {speed} is near profile maximum ({max_speed})."
        )

    if pressure < min_pressure or pressure > max_pressure:
        errors.append(
            f"pump_pressure_bar {pressure} out of range ({min_pressure}-{max_pressure})"
        )
        blocked.append("pump_pressure_bar")

    if flow < min_flow or flow > max_flow:
        errors.append(
            f"extrusion_rate_l_min {flow} out of range ({min_flow}-{max_flow})"
        )
        blocked.append("extrusion_rate_l_min")
    elif flow > max_flow * 0.9:
        warnings.append(
            f"extrusion_rate_l_min {flow} is near profile maximum ({max_flow})."
        )

    return ConcreteValidationResult(
        valid=len(errors) == 0,
        warnings=warnings,
        errors=errors,
        blocked_params=blocked,
    )
