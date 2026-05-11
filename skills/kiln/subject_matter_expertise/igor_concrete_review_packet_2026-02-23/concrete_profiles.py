"""Safety profiles for structural concrete 3D printers.

Provides conservative machine envelopes for common construction-printing
platforms so Forge can enforce fail-closed safety bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ConcreteSafetyProfile:
    """Safety limits for a concrete printing machine."""

    id: str
    display_name: str
    min_print_speed_mm_s: float
    max_print_speed_mm_s: float
    min_layer_height_mm: float
    max_layer_height_mm: float
    min_pump_pressure_bar: float
    max_pump_pressure_bar: float
    min_material_flow_l_min: float
    max_material_flow_l_min: float
    max_wind_speed_m_s: float
    min_ambient_temp_c: float
    max_ambient_temp_c: float
    requires_exclusion_zone: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "min_print_speed_mm_s": self.min_print_speed_mm_s,
            "max_print_speed_mm_s": self.max_print_speed_mm_s,
            "min_layer_height_mm": self.min_layer_height_mm,
            "max_layer_height_mm": self.max_layer_height_mm,
            "min_pump_pressure_bar": self.min_pump_pressure_bar,
            "max_pump_pressure_bar": self.max_pump_pressure_bar,
            "min_material_flow_l_min": self.min_material_flow_l_min,
            "max_material_flow_l_min": self.max_material_flow_l_min,
            "max_wind_speed_m_s": self.max_wind_speed_m_s,
            "min_ambient_temp_c": self.min_ambient_temp_c,
            "max_ambient_temp_c": self.max_ambient_temp_c,
            "requires_exclusion_zone": self.requires_exclusion_zone,
            "notes": self.notes,
        }


_PROFILES: Dict[str, ConcreteSafetyProfile] = {
    "default_concrete": ConcreteSafetyProfile(
        id="default_concrete",
        display_name="Default Concrete Printer",
        min_print_speed_mm_s=50.0,
        max_print_speed_mm_s=500.0,
        min_layer_height_mm=8.0,
        max_layer_height_mm=60.0,
        min_pump_pressure_bar=40.0,
        max_pump_pressure_bar=230.0,
        min_material_flow_l_min=2.0,
        max_material_flow_l_min=80.0,
        max_wind_speed_m_s=8.0,
        min_ambient_temp_c=5.0,
        max_ambient_temp_c=38.0,
        requires_exclusion_zone=True,
        notes="Conservative baseline profile for unknown concrete printer models.",
    ),
    "icon_titan": ConcreteSafetyProfile(
        id="icon_titan",
        display_name="ICON Titan",
        min_print_speed_mm_s=60.0,
        max_print_speed_mm_s=450.0,
        min_layer_height_mm=10.0,
        max_layer_height_mm=40.0,
        min_pump_pressure_bar=50.0,
        max_pump_pressure_bar=220.0,
        min_material_flow_l_min=3.0,
        max_material_flow_l_min=65.0,
        max_wind_speed_m_s=7.0,
        min_ambient_temp_c=5.0,
        max_ambient_temp_c=38.0,
        requires_exclusion_zone=True,
    ),
    "cobod_bod3": ConcreteSafetyProfile(
        id="cobod_bod3",
        display_name="COBOD BOD3",
        min_print_speed_mm_s=70.0,
        max_print_speed_mm_s=900.0,
        min_layer_height_mm=8.0,
        max_layer_height_mm=100.0,
        min_pump_pressure_bar=45.0,
        max_pump_pressure_bar=250.0,
        min_material_flow_l_min=3.0,
        max_material_flow_l_min=100.0,
        max_wind_speed_m_s=9.0,
        min_ambient_temp_c=2.0,
        max_ambient_temp_c=40.0,
        requires_exclusion_zone=True,
    ),
    "cybe_rc_3dp": ConcreteSafetyProfile(
        id="cybe_rc_3dp",
        display_name="CyBe RC 3Dp",
        min_print_speed_mm_s=60.0,
        max_print_speed_mm_s=700.0,
        min_layer_height_mm=8.0,
        max_layer_height_mm=60.0,
        min_pump_pressure_bar=45.0,
        max_pump_pressure_bar=240.0,
        min_material_flow_l_min=2.0,
        max_material_flow_l_min=70.0,
        max_wind_speed_m_s=8.0,
        min_ambient_temp_c=2.0,
        max_ambient_temp_c=38.0,
        requires_exclusion_zone=True,
    ),
    "wasp_crane": ConcreteSafetyProfile(
        id="wasp_crane",
        display_name="WASP Crane",
        min_print_speed_mm_s=40.0,
        max_print_speed_mm_s=400.0,
        min_layer_height_mm=10.0,
        max_layer_height_mm=80.0,
        min_pump_pressure_bar=30.0,
        max_pump_pressure_bar=200.0,
        min_material_flow_l_min=2.0,
        max_material_flow_l_min=60.0,
        max_wind_speed_m_s=7.0,
        min_ambient_temp_c=5.0,
        max_ambient_temp_c=36.0,
        requires_exclusion_zone=True,
    ),
    "apis_cor": ConcreteSafetyProfile(
        id="apis_cor",
        display_name="Apis Cor Construction Printer",
        min_print_speed_mm_s=40.0,
        max_print_speed_mm_s=350.0,
        min_layer_height_mm=10.0,
        max_layer_height_mm=80.0,
        min_pump_pressure_bar=35.0,
        max_pump_pressure_bar=230.0,
        min_material_flow_l_min=2.0,
        max_material_flow_l_min=60.0,
        max_wind_speed_m_s=7.0,
        min_ambient_temp_c=5.0,
        max_ambient_temp_c=36.0,
        requires_exclusion_zone=True,
    ),
    "constructions3d_maxiprinter": ConcreteSafetyProfile(
        id="constructions3d_maxiprinter",
        display_name="Constructions-3D MaxiPrinter",
        min_print_speed_mm_s=50.0,
        max_print_speed_mm_s=600.0,
        min_layer_height_mm=8.0,
        max_layer_height_mm=60.0,
        min_pump_pressure_bar=40.0,
        max_pump_pressure_bar=220.0,
        min_material_flow_l_min=2.0,
        max_material_flow_l_min=75.0,
        max_wind_speed_m_s=8.0,
        min_ambient_temp_c=4.0,
        max_ambient_temp_c=38.0,
        requires_exclusion_zone=True,
    ),
}


def _normalise(name: str) -> str:
    return name.lower().replace("-", "_").replace(" ", "_").strip()


def get_concrete_profile(printer_id: str) -> ConcreteSafetyProfile:
    """Return a concrete profile by ID, with fallback to default."""
    key = _normalise(printer_id)
    if key in _PROFILES:
        return _PROFILES[key]

    for cand in _PROFILES:
        if cand in key or key in cand:
            return _PROFILES[cand]

    return _PROFILES["default_concrete"]


def list_concrete_profiles() -> List[str]:
    """Return all known concrete profile IDs."""
    return sorted(_PROFILES.keys())


def get_all_concrete_profiles() -> Dict[str, ConcreteSafetyProfile]:
    """Return all concrete profiles keyed by ID."""
    return dict(_PROFILES)


def profile_to_dict(profile: ConcreteSafetyProfile) -> Dict[str, object]:
    """Convert a concrete profile to a serializable dict."""
    return profile.to_dict()


def resolve_limits(printer_id: str) -> Dict[str, float]:
    """Return a compact dict of key numeric limits for *printer_id*."""
    p = get_concrete_profile(printer_id)
    return {
        "min_print_speed_mm_s": p.min_print_speed_mm_s,
        "max_print_speed_mm_s": p.max_print_speed_mm_s,
        "min_layer_height_mm": p.min_layer_height_mm,
        "max_layer_height_mm": p.max_layer_height_mm,
        "min_pump_pressure_bar": p.min_pump_pressure_bar,
        "max_pump_pressure_bar": p.max_pump_pressure_bar,
        "min_material_flow_l_min": p.min_material_flow_l_min,
        "max_material_flow_l_min": p.max_material_flow_l_min,
    }
