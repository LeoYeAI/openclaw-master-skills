"""Brand-specific concrete printer adapters built on ConcreteHTTPAdapter.

These are integration shells for mainstream construction 3D printing vendors.
Endpoint maps are intentionally overridable because many APIs are private.
"""

from __future__ import annotations

from typing import Dict, Optional

from forge.devices.base import ConcreteCapabilities
from forge.devices.concrete_http import ConcreteHTTPAdapter


class ICONTitanAdapter(ConcreteHTTPAdapter):
    """Adapter shell for ICON Titan systems."""

    SUPPORTED_MODELS = ("Titan", "Phoenix (legacy)", "Vulcan (legacy)")

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "Titan",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="ICON",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                can_upload=True,
                can_pause=True,
                can_prime_pump=True,
                has_pump_pressure_sensor=True,
                has_material_flow_sensor=True,
                has_weather_station=True,
                max_print_speed_mm_s=500.0,
                max_layer_height_mm=50.0,
                max_pump_pressure_bar=240.0,
                supported_extensions=(".gcode", ".iconjob", ".json", ".nc"),
            ),
        )


class COBODAdapter(ConcreteHTTPAdapter):
    """Adapter shell for COBOD BOD series systems."""

    SUPPORTED_MODELS = ("BOD2", "BOD3")

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "BOD3",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="COBOD",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                max_print_speed_mm_s=1000.0,
                max_layer_height_mm=100.0,
                max_pump_pressure_bar=260.0,
                supported_extensions=(".gcode", ".nc", ".cobod", ".json"),
            ),
        )


class CyBeAdapter(ConcreteHTTPAdapter):
    """Adapter shell for CyBe Construction printer platforms."""

    SUPPORTED_MODELS = ("RC 3Dp", "Robot Crawler")

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "RC 3Dp",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="CyBe",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                max_print_speed_mm_s=900.0,
                max_layer_height_mm=60.0,
                max_pump_pressure_bar=250.0,
                supported_extensions=(".gcode", ".json", ".nc"),
            ),
        )


class WASPAdapter(ConcreteHTTPAdapter):
    """Adapter shell for WASP crane construction printers."""

    SUPPORTED_MODELS = ("Crane WASP", "Crane WASP Scara")

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "Crane WASP",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="WASP",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                max_print_speed_mm_s=450.0,
                max_layer_height_mm=80.0,
                max_pump_pressure_bar=210.0,
                supported_extensions=(".gcode", ".json", ".nc"),
            ),
        )


class ApisCorAdapter(ConcreteHTTPAdapter):
    """Adapter shell for Apis Cor construction printer systems."""

    SUPPORTED_MODELS = ("Apis Cor Construction Printer",)

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "Apis Cor Construction Printer",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="Apis Cor",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                max_print_speed_mm_s=350.0,
                max_layer_height_mm=80.0,
                max_pump_pressure_bar=230.0,
                supported_extensions=(".gcode", ".json", ".nc"),
            ),
        )


class Constructions3DAdapter(ConcreteHTTPAdapter):
    """Adapter shell for Constructions-3D MaxiPrinter systems."""

    SUPPORTED_MODELS = ("MaxiPrinter",)

    def __init__(
        self,
        *,
        host: str,
        api_key: str = "",
        model: str = "MaxiPrinter",
        endpoints: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            host=host,
            vendor="Constructions-3D",
            model=model,
            api_key=api_key,
            endpoints=endpoints,
            capabilities=ConcreteCapabilities(
                max_print_speed_mm_s=600.0,
                max_layer_height_mm=60.0,
                max_pump_pressure_bar=220.0,
                supported_extensions=(".gcode", ".json", ".nc"),
            ),
        )
