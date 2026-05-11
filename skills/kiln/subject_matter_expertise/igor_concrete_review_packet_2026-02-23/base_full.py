"""Abstract device adapter interfaces for SLA, laser, CNC, and concrete devices.

Mirrors kiln.printers.base.PrinterAdapter but specialized for each
device category.  All adapters share a common DeviceState model and
the same lifecycle (connect -> configure -> operate -> monitor).
"""


# MERGE NOTE: OperationResult is intentionally NOT renamed to PrintResult.
# Both have identical fields (success, message, job_id). PrintResult stays
# for FDM adapters in kiln.printers; OperationResult serves SLA/Laser/CNC/Concrete.
from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DeviceError(Exception):
    """Base exception for all device-related errors.

    Adapter implementations should raise this (or a subclass) whenever
    an operation fails in a way the caller can reasonably handle --
    e.g. connection timeouts, interlock violations, or unexpected
    firmware responses.
    """

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DeviceStatus(enum.Enum):
    """High-level operational state of a non-FDM device."""

    IDLE = "idle"
    OPERATING = "operating"
    PAUSED = "paused"
    ERROR = "error"
    OFFLINE = "offline"
    BUSY = "busy"
    CANCELLING = "cancelling"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Shared dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DeviceState:
    """Snapshot of a device's current connection and operational state."""

    connected: bool
    state: DeviceStatus
    device_type: str
    firmware_version: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary.

        The :attr:`state` enum is converted to its string value so the
        result can be passed directly to ``json.dumps``.
        """
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass
class JobProgress:
    """Progress information for the currently active (or most recent) job."""

    file_name: str | None = None
    completion: float | None = None  # 0.0 -- 100.0
    time_seconds: int | None = None
    time_left_seconds: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


@dataclass
class OperationResult:
    """Outcome of a device control operation (start / cancel / pause / resume)."""

    success: bool
    message: str
    job_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


# ---------------------------------------------------------------------------
# SLA-specific types
# ---------------------------------------------------------------------------

@dataclass
class SLAState(DeviceState):
    """Extended state snapshot for an SLA (resin) printer."""

    vat_level_percent: float | None = None
    uv_power_percent: float | None = None
    resin_temp_c: float | None = None
    current_layer: int | None = None
    total_layers: int | None = None
    light_source_hours: float | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass
class SLAPrintConfig:
    """Configuration parameters for an SLA print job."""

    exposure_time_s: float
    bottom_exposure_time_s: float
    layer_height_um: int
    lift_speed_mm_min: float
    retract_speed_mm_min: float
    bottom_layers: int = 4

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


@dataclass
class SLACapabilities:
    """Declares what a specific SLA adapter can do."""

    can_upload: bool = True
    can_pause: bool = True
    can_heat_resin: bool = False
    can_monitor_vat: bool = False
    can_snapshot: bool = False
    max_exposure_s: float = 120.0
    max_bottom_exposure_s: float = 300.0
    device_type: str = "sla_printer"
    supported_extensions: tuple[str, ...] = (".sl1", ".sl1s", ".ctb", ".pwmx")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["supported_extensions"] = list(self.supported_extensions)
        return data


# ---------------------------------------------------------------------------
# Laser-specific types
# ---------------------------------------------------------------------------

@dataclass
class LaserState(DeviceState):
    """Extended state snapshot for a laser cutter / engraver."""

    laser_power_percent: float | None = None
    laser_active: bool = False
    exhaust_running: bool = False
    lid_closed: bool = True
    material_loaded: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass
class CutConfig:
    """Configuration parameters for a laser cut / engrave job."""

    power_percent: float
    speed_mm_s: float
    passes: int = 1
    focus_height_mm: float | None = None
    air_assist: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


@dataclass
class LaserCapabilities:
    """Declares what a specific laser adapter can do."""

    can_upload: bool = True
    can_pause: bool = True
    can_snapshot: bool = False
    has_exhaust_interlock: bool = True
    has_lid_interlock: bool = True
    has_air_assist: bool = True
    max_power_watts: float = 40.0
    device_type: str = "laser_cutter"
    supported_extensions: tuple[str, ...] = (".svg", ".dxf", ".gcode", ".lbrn")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["supported_extensions"] = list(self.supported_extensions)
        return data


# ---------------------------------------------------------------------------
# CNC-specific types
# ---------------------------------------------------------------------------

@dataclass
class CNCState(DeviceState):
    """Extended state snapshot for a CNC router / mill / lathe."""

    spindle_rpm: float | None = None
    spindle_load_percent: float | None = None
    position: dict[str, float] | None = None
    coolant_active: bool = False
    tool_number: int | None = None
    feed_override_percent: float = 100.0
    # Lathe / turning center extensions
    sub_spindle_rpm: float | None = None
    sub_spindle_load_percent: float | None = None
    c_axis_deg: float | None = None
    chuck_clamped: bool | None = None
    tailstock_extended: bool | None = None
    turret_position: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass
class CNCJobConfig:
    """Configuration parameters for a CNC machining job."""

    tool_id: int
    rpm: float
    feed_mm_min: float
    plunge_mm_min: float
    depth_mm: float
    coolant: bool = False
    # Lathe-specific optional parameters
    sub_spindle_rpm: float | None = None
    c_axis_position_deg: float | None = None
    constant_surface_speed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


@dataclass
class CNCCapabilities:
    """Declares what a specific CNC adapter can do."""

    can_upload: bool = True
    can_pause: bool = True
    can_snapshot: bool = False
    can_probe: bool = True
    can_home: bool = True
    has_coolant: bool = False
    max_spindle_rpm: float = 24000.0
    max_feedrate_mm_min: float = 5000.0
    axis_count: int = 3
    device_type: str = "cnc_router"
    supported_extensions: tuple[str, ...] = (".nc", ".gcode", ".ngc", ".tap")
    # Lathe / turning center capabilities
    has_sub_spindle: bool = False
    sub_spindle_max_rpm: float = 0.0
    has_live_tooling: bool = False
    live_tool_max_rpm: float = 0.0
    has_y_axis: bool = False
    has_c_axis: bool = False
    has_tailstock: bool = False
    turret_stations: int = 0
    max_turning_diameter_mm: float = 0.0
    max_turning_length_mm: float = 0.0
    bar_capacity_mm: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["supported_extensions"] = list(self.supported_extensions)
        return data


# ---------------------------------------------------------------------------
# Concrete (construction 3D printing)-specific types
# ---------------------------------------------------------------------------

@dataclass
class ConcreteState(DeviceState):
    """Extended state snapshot for a structural concrete 3D printer."""

    pump_pressure_bar: Optional[float] = None
    material_flow_l_min: Optional[float] = None
    nozzle_height_mm: Optional[float] = None
    layer_height_mm: Optional[float] = None
    gantry_position: Optional[Dict[str, float]] = None
    emergency_stop_clear: bool = True
    weather_safe: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass
class ConcretePrintConfig:
    """Configuration parameters for a structural concrete print job."""

    layer_height_mm: float
    print_speed_mm_s: float
    extrusion_rate_l_min: float
    nozzle_diameter_mm: float
    pump_pressure_bar: float = 80.0
    bead_width_mm: Optional[float] = None
    cure_pause_s: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary."""
        return asdict(self)


@dataclass
class ConcreteCapabilities:
    """Declares what a specific concrete printing adapter can do."""

    can_upload: bool = True
    can_pause: bool = True
    can_prime_pump: bool = True
    has_pump_pressure_sensor: bool = True
    has_material_flow_sensor: bool = True
    has_weather_station: bool = False
    max_print_speed_mm_s: float = 500.0
    max_layer_height_mm: float = 75.0
    max_pump_pressure_bar: float = 250.0
    device_type: str = "concrete_printer"
    supported_extensions: Tuple[str, ...] = (
        ".gcode", ".nc", ".3mf", ".json", ".iconjob", ".cobod",
    )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["supported_extensions"] = list(self.supported_extensions)
        return data


# ---------------------------------------------------------------------------
# Abstract base classes
# ---------------------------------------------------------------------------

class SLAAdapter(ABC):
    """Abstract base for SLA (resin) printer adapters.

    Concrete subclasses must implement every abstract method and property
    listed below.  The forge orchestration layer relies on this contract
    to drive any supported SLA printer through a single, uniform API.
    """

    # -- identity & feature discovery -----------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this adapter."""

    @property
    @abstractmethod
    def capabilities(self) -> SLACapabilities:
        """Return the set of capabilities this adapter supports."""

    # -- state queries --------------------------------------------------

    @abstractmethod
    def get_state(self) -> SLAState:
        """Retrieve the current printer state and sensor readings.

        :raises DeviceError: If communication with the printer fails.
        """

    @abstractmethod
    def get_job(self) -> JobProgress:
        """Retrieve progress info for the active (or last) print job.

        :raises DeviceError: If communication with the printer fails.
        """

    # -- file management ------------------------------------------------

    @abstractmethod
    def upload_file(self, file_path: str) -> OperationResult:
        """Upload a sliced file to the printer.

        :param file_path: Absolute or relative path to the local file.
        :raises DeviceError: If the upload fails.
        :raises FileNotFoundError: If *file_path* does not exist locally.
        """

    # -- print control --------------------------------------------------

    @abstractmethod
    def start_print(self, file_name: str, config: SLAPrintConfig) -> OperationResult:
        """Begin printing a file that already exists on the printer.

        :param file_name: Name of the file as known by the printer.
        :param config: Exposure and layer parameters.
        :raises DeviceError: If the printer cannot start the job.
        """

    @abstractmethod
    def cancel_print(self) -> OperationResult:
        """Cancel the currently running print job.

        :raises DeviceError: If the cancellation fails.
        """

    @abstractmethod
    def pause_print(self) -> OperationResult:
        """Pause the currently running print job.

        :raises DeviceError: If the printer cannot pause.
        """

    @abstractmethod
    def resume_print(self) -> OperationResult:
        """Resume a previously paused print job.

        :raises DeviceError: If the printer cannot resume.
        """

    @abstractmethod
    def emergency_stop(self) -> OperationResult:
        """Perform an immediate emergency stop.

        Cuts UV exposure and halts the build platform.  Unlike
        :meth:`cancel_print`, this does **not** allow a graceful
        wind-down sequence.

        :raises DeviceError: If the e-stop command cannot be delivered.
        """

    # -- SLA-specific operations ----------------------------------------

    @abstractmethod
    def get_vat_level(self) -> float:
        """Return the current resin vat level as a percentage (0--100).

        :raises DeviceError: If the sensor reading fails.
        """

    @abstractmethod
    def set_resin_temp(self, target: float) -> None:
        """Set the target resin temperature in degrees Celsius.

        :param target: Desired temperature.  Pass ``0`` to disable heating.
        :raises DeviceError: If the command fails or target is out of range.
        """

    # -- webcam snapshot (optional) ------------------------------------

    def get_snapshot(self) -> bytes | None:
        """Capture a webcam snapshot from the device.

        Returns raw JPEG/PNG image bytes, or ``None`` if webcam is not
        available or not supported by this adapter.  This is an optional
        method -- the default implementation returns ``None``.
        """
        return None

    # -- webcam streaming (optional) -----------------------------------

    def get_stream_url(self) -> str | None:
        """Return the MJPEG stream URL for the device's webcam.

        Returns the full URL to the live video stream, or ``None`` if
        streaming is not available.  This is an optional method -- the
        default implementation returns ``None``.
        """
        return None

    # -- convenience / dunder helpers -----------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} name={self.name!r}>"


class LaserAdapter(ABC):
    """Abstract base for laser cutter / engraver adapters.

    Concrete subclasses must implement every abstract method and property.
    Safety interlocks (ventilation, lid) are first-class operations, not
    optional -- laser devices MUST expose interlock state.
    """

    # -- identity & feature discovery -----------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this adapter."""

    @property
    @abstractmethod
    def capabilities(self) -> LaserCapabilities:
        """Return the set of capabilities this adapter supports."""

    # -- state queries --------------------------------------------------

    @abstractmethod
    def get_state(self) -> LaserState:
        """Retrieve the current device state and sensor readings.

        :raises DeviceError: If communication with the device fails.
        """

    @abstractmethod
    def get_job(self) -> JobProgress:
        """Retrieve progress info for the active (or last) cut/engrave job.

        :raises DeviceError: If communication with the device fails.
        """

    # -- file management ------------------------------------------------

    @abstractmethod
    def upload_file(self, file_path: str) -> OperationResult:
        """Upload a cut/engrave file to the device.

        :param file_path: Absolute or relative path to the local file.
        :raises DeviceError: If the upload fails.
        :raises FileNotFoundError: If *file_path* does not exist locally.
        """

    # -- cut control ----------------------------------------------------

    @abstractmethod
    def start_cut(self, file_name: str, config: CutConfig) -> OperationResult:
        """Begin cutting/engraving a file already on the device.

        :param file_name: Name of the file as known by the device.
        :param config: Power, speed, and pass parameters.
        :raises DeviceError: If the device cannot start the job.
        """

    @abstractmethod
    def cancel_cut(self) -> OperationResult:
        """Cancel the currently running cut job.

        :raises DeviceError: If the cancellation fails.
        """

    @abstractmethod
    def pause_cut(self) -> OperationResult:
        """Pause the currently running cut job.

        :raises DeviceError: If the device cannot pause.
        """

    @abstractmethod
    def resume_cut(self) -> OperationResult:
        """Resume a previously paused cut job.

        :raises DeviceError: If the device cannot resume.
        """

    @abstractmethod
    def emergency_stop(self) -> OperationResult:
        """Perform an immediate emergency stop.

        Disables the laser and halts all motion.

        :raises DeviceError: If the e-stop command cannot be delivered.
        """

    # -- laser-specific operations --------------------------------------

    @abstractmethod
    def set_laser_power(self, percent: float) -> None:
        """Set the laser output power as a percentage (0--100).

        :param percent: Target power level.
        :raises DeviceError: If the value is out of range or the command fails.
        """

    @abstractmethod
    def check_ventilation(self) -> bool:
        """Return ``True`` if the exhaust / ventilation system is running."""

    @abstractmethod
    def check_lid_interlock(self) -> bool:
        """Return ``True`` if the lid is closed and the interlock is engaged."""

    # -- webcam snapshot (optional) ------------------------------------

    def get_snapshot(self) -> bytes | None:
        """Capture a webcam snapshot from the device.

        Returns raw JPEG/PNG image bytes, or ``None`` if webcam is not
        available or not supported by this adapter.  This is an optional
        method -- the default implementation returns ``None``.
        """
        return None

    # -- webcam streaming (optional) -----------------------------------

    def get_stream_url(self) -> str | None:
        """Return the MJPEG stream URL for the device's webcam.

        Returns the full URL to the live video stream, or ``None`` if
        streaming is not available.  This is an optional method -- the
        default implementation returns ``None``.
        """
        return None

    # -- convenience / dunder helpers -----------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} name={self.name!r}>"


class CNCAdapter(ABC):
    """Abstract base for CNC router / mill adapters.

    Concrete subclasses must implement every abstract method and property.
    CNC adapters are responsible for spindle control, position tracking,
    tool management, and feed-rate overrides.
    """

    # -- identity & feature discovery -----------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this adapter."""

    @property
    @abstractmethod
    def capabilities(self) -> CNCCapabilities:
        """Return the set of capabilities this adapter supports."""

    # -- state queries --------------------------------------------------

    @abstractmethod
    def get_state(self) -> CNCState:
        """Retrieve the current machine state and sensor readings.

        :raises DeviceError: If communication with the machine fails.
        """

    @abstractmethod
    def get_job(self) -> JobProgress:
        """Retrieve progress info for the active (or last) machining job.

        :raises DeviceError: If communication with the machine fails.
        """

    # -- file management ------------------------------------------------

    @abstractmethod
    def upload_file(self, file_path: str) -> OperationResult:
        """Upload a G-code / toolpath file to the machine.

        :param file_path: Absolute or relative path to the local file.
        :raises DeviceError: If the upload fails.
        :raises FileNotFoundError: If *file_path* does not exist locally.
        """

    # -- job control ----------------------------------------------------

    @abstractmethod
    def start_job(self, file_name: str, config: CNCJobConfig) -> OperationResult:
        """Begin machining a file already on the device.

        :param file_name: Name of the file as known by the device.
        :param config: Tool, speed, and depth parameters.
        :raises DeviceError: If the machine cannot start the job.
        """

    @abstractmethod
    def cancel_job(self) -> OperationResult:
        """Cancel the currently running machining job.

        :raises DeviceError: If the cancellation fails.
        """

    @abstractmethod
    def pause_job(self) -> OperationResult:
        """Pause the currently running machining job.

        :raises DeviceError: If the machine cannot pause.
        """

    @abstractmethod
    def resume_job(self) -> OperationResult:
        """Resume a previously paused machining job.

        :raises DeviceError: If the machine cannot resume.
        """

    @abstractmethod
    def emergency_stop(self) -> OperationResult:
        """Perform an immediate emergency stop.

        Disables the spindle and halts all axis motion.

        :raises DeviceError: If the e-stop command cannot be delivered.
        """

    # -- CNC-specific operations ----------------------------------------

    @abstractmethod
    def set_spindle_speed(self, rpm: float) -> None:
        """Set the spindle speed in revolutions per minute.

        :param rpm: Target RPM.  Pass ``0`` to stop the spindle.
        :raises DeviceError: If the value exceeds machine limits.
        """

    @abstractmethod
    def home_axes(self) -> OperationResult:
        """Execute the machine's homing sequence on all axes.

        :raises DeviceError: If homing fails or a limit switch is not found.
        """

    @abstractmethod
    def probe_tool_length(self) -> float:
        """Run a tool-length probe cycle and return the offset in mm.

        :raises DeviceError: If probing fails or the probe is not detected.
        """

    @abstractmethod
    def get_position(self) -> dict[str, float]:
        """Return the current tool position as ``{"x": ..., "y": ..., "z": ...}``.

        :raises DeviceError: If the position cannot be read.
        """

    @abstractmethod
    def set_feed_override(self, percent: float) -> None:
        """Set the feed-rate override as a percentage of programmed speed.

        :param percent: Override value (typically 10--200 %).
        :raises DeviceError: If the value is out of range.
        """

    # -- webcam snapshot (optional) ------------------------------------

    def get_snapshot(self) -> bytes | None:
        """Capture a webcam snapshot from the device.

        Returns raw JPEG/PNG image bytes, or ``None`` if webcam is not
        available or not supported by this adapter.  This is an optional
        method -- the default implementation returns ``None``.
        """
        return None

    # -- webcam streaming (optional) -----------------------------------

    def get_stream_url(self) -> str | None:
        """Return the MJPEG stream URL for the device's webcam.

        Returns the full URL to the live video stream, or ``None`` if
        streaming is not available.  This is an optional method -- the
        default implementation returns ``None``.
        """
        return None

    # -- convenience / dunder helpers -----------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} name={self.name!r}>"


class ConcreteAdapter(ABC):
    """Abstract base for structural concrete construction printers.

    Concrete adapters represent large-format robotic systems used to print
    structural walls and architectural elements with cementitious material.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this adapter."""

    @property
    @abstractmethod
    def capabilities(self) -> ConcreteCapabilities:
        """Return the set of capabilities this adapter supports."""

    @abstractmethod
    def get_state(self) -> ConcreteState:
        """Retrieve the current machine state and safety-relevant telemetry.

        :raises DeviceError: If communication with the machine fails.
        """

    @abstractmethod
    def get_job(self) -> JobProgress:
        """Retrieve progress info for the active (or last) print job.

        :raises DeviceError: If communication with the machine fails.
        """

    @abstractmethod
    def upload_file(self, file_path: str) -> OperationResult:
        """Upload a print program file to the machine controller.

        :param file_path: Absolute or relative path to the local file.
        :raises DeviceError: If the upload fails.
        :raises FileNotFoundError: If *file_path* does not exist locally.
        """

    @abstractmethod
    def start_print(
        self,
        file_name: str,
        config: ConcretePrintConfig,
    ) -> OperationResult:
        """Start a concrete print program already available on the machine.

        :param file_name: Name of the file as known by the machine.
        :param config: Layer, speed, flow, and pump pressure parameters.
        :raises DeviceError: If the machine cannot start the job.
        """

    @abstractmethod
    def cancel_print(self) -> OperationResult:
        """Cancel the currently running concrete print.

        :raises DeviceError: If cancellation fails.
        """

    @abstractmethod
    def pause_print(self) -> OperationResult:
        """Pause the currently running concrete print.

        :raises DeviceError: If pause fails.
        """

    @abstractmethod
    def resume_print(self) -> OperationResult:
        """Resume a previously paused concrete print.

        :raises DeviceError: If resume fails.
        """

    @abstractmethod
    def emergency_stop(self) -> OperationResult:
        """Execute an immediate emergency stop on pump + motion systems.

        :raises DeviceError: If e-stop command delivery fails.
        """

    @abstractmethod
    def check_pump_pressure(self) -> float:
        """Return current pump pressure in bar.

        :raises DeviceError: If pressure cannot be read.
        """

    @abstractmethod
    def check_material_flow(self) -> float:
        """Return current material flow rate in litres per minute.

        :raises DeviceError: If flow cannot be read.
        """

    @abstractmethod
    def check_emergency_stop(self) -> bool:
        """Return ``True`` when emergency-stop circuit is clear/safe."""

    @abstractmethod
    def check_weather_safe(self) -> bool:
        """Return ``True`` when weather conditions are within print limits."""

    @abstractmethod
    def prime_pump(self, target_pressure_bar: float) -> OperationResult:
        """Prime the pump and pressurise line before printing.

        :param target_pressure_bar: Target pressure to reach before start.
        :raises DeviceError: If priming fails or target exceeds limits.
        """

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} name={self.name!r}>"
