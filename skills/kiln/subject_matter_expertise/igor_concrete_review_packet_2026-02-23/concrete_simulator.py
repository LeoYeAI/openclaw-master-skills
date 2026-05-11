"""Simulated structural concrete printer for development without hardware.

Models a gantry-style construction printer with pump pressure, material flow,
weather gating, and emergency-stop behavior.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Dict, List, Optional

from forge.devices.base import (
    ConcreteAdapter,
    ConcreteCapabilities,
    ConcretePrintConfig,
    ConcreteState,
    DeviceError,
    DeviceStatus,
    JobProgress,
    OperationResult,
)

logger = logging.getLogger(__name__)

_MIN_LAYER_HEIGHT_MM: float = 5.0
_MAX_LAYER_HEIGHT_MM: float = 75.0
_MIN_SPEED_MM_S: float = 10.0
_MAX_SPEED_MM_S: float = 650.0
_MIN_EXTRUSION_L_MIN: float = 0.5
_MAX_EXTRUSION_L_MIN: float = 120.0
_MIN_NOZZLE_DIAMETER_MM: float = 10.0
_MAX_NOZZLE_DIAMETER_MM: float = 80.0
_MIN_PUMP_PRESSURE_BAR: float = 20.0
_MAX_PUMP_PRESSURE_BAR: float = 250.0


class _ConcreteJob:
    """Tracks progress for a running simulated concrete print."""

    def __init__(
        self,
        file_name: str,
        config: ConcretePrintConfig,
        *,
        total_segments: int = 300,
        job_id: Optional[str] = None,
    ) -> None:
        self.job_id: str = job_id or uuid.uuid4().hex[:12]
        self.file_name: str = file_name
        self.config: ConcretePrintConfig = config
        self.total_segments: int = total_segments
        self.current_segment: int = 0
        self.started_at: float = time.monotonic()
        self.paused: bool = False
        self._pause_offset: float = 0.0
        self._pause_start: float = 0.0

    @property
    def elapsed_s(self) -> float:
        if self.paused:
            return self._pause_start - self.started_at - self._pause_offset
        return time.monotonic() - self.started_at - self._pause_offset

    @property
    def completion(self) -> float:
        if self.total_segments <= 0:
            return 0.0
        return min(100.0, (self.current_segment / self.total_segments) * 100.0)

    @property
    def time_left_s(self) -> int:
        if self.current_segment <= 0:
            return 0
        per_segment = self.elapsed_s / self.current_segment
        remaining = self.total_segments - self.current_segment
        return int(per_segment * remaining)

    def pause(self) -> None:
        if not self.paused:
            self.paused = True
            self._pause_start = time.monotonic()

    def resume(self) -> None:
        if self.paused:
            self._pause_offset += time.monotonic() - self._pause_start
            self.paused = False

    def advance(self) -> None:
        if not self.paused and self.current_segment < self.total_segments:
            self.current_segment += 1


class ConcreteSimulator(ConcreteAdapter):
    """Simulated gantry concrete printer.

    Calling :meth:`tick` advances the simulation by one or more path segments.
    """

    def __init__(
        self,
        *,
        name: str = "concrete-sim",
        build_volume_mm: tuple[float, float, float] = (10000.0, 3000.0, 3200.0),
    ) -> None:
        self._name: str = name
        self._build_volume_mm: tuple[float, float, float] = build_volume_mm

        self._connected: bool = True
        self._status: DeviceStatus = DeviceStatus.IDLE
        self._pump_pressure_bar: float = 0.0
        self._material_flow_l_min: float = 0.0
        self._nozzle_height_mm: float = 0.0
        self._layer_height_mm: float = 20.0
        self._gantry_position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._emergency_stop_clear: bool = True
        self._weather_safe: bool = True
        self._error_message: Optional[str] = None

        self._current_job: Optional[_ConcreteJob] = None
        self._files: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> ConcreteCapabilities:
        return ConcreteCapabilities(
            can_upload=True,
            can_pause=True,
            can_prime_pump=True,
            has_pump_pressure_sensor=True,
            has_material_flow_sensor=True,
            has_weather_station=True,
            max_print_speed_mm_s=_MAX_SPEED_MM_S,
            max_layer_height_mm=_MAX_LAYER_HEIGHT_MM,
            max_pump_pressure_bar=_MAX_PUMP_PRESSURE_BAR,
        )

    def get_state(self) -> ConcreteState:
        return ConcreteState(
            connected=self._connected,
            state=self._status,
            device_type="concrete_printer",
            pump_pressure_bar=round(self._pump_pressure_bar, 1),
            material_flow_l_min=round(self._material_flow_l_min, 2),
            nozzle_height_mm=round(self._nozzle_height_mm, 1),
            layer_height_mm=round(self._layer_height_mm, 1),
            gantry_position=dict(self._gantry_position),
            emergency_stop_clear=self._emergency_stop_clear,
            weather_safe=self._weather_safe,
            error_message=self._error_message,
        )

    def get_job(self) -> JobProgress:
        if self._current_job is None:
            return JobProgress()
        return JobProgress(
            file_name=self._current_job.file_name,
            completion=round(self._current_job.completion, 2),
            time_seconds=int(self._current_job.elapsed_s),
            time_left_seconds=self._current_job.time_left_s,
        )

    def upload_file(self, file_path: str) -> OperationResult:
        file_name = file_path.rsplit("/", 1)[-1] if "/" in file_path else file_path
        if file_name not in self._files:
            self._files.append(file_name)
        return OperationResult(success=True, message=f"Uploaded '{file_name}'.")

    def start_print(
        self,
        file_name: str,
        config: ConcretePrintConfig,
    ) -> OperationResult:
        if self._status == DeviceStatus.OPERATING:
            raise DeviceError("Cannot start concrete print: another job is running.")
        if self._status == DeviceStatus.ERROR:
            raise DeviceError(
                f"Cannot start concrete print: machine error ({self._error_message})."
            )
        if not self._emergency_stop_clear:
            raise DeviceError("Cannot start concrete print: emergency stop is engaged.")
        if not self._weather_safe:
            raise DeviceError("Cannot start concrete print: weather interlock is unsafe.")
        if file_name not in self._files:
            raise DeviceError(f"File '{file_name}' not found on machine.")

        self._validate_config(config)
        if self._pump_pressure_bar < max(_MIN_PUMP_PRESSURE_BAR, config.pump_pressure_bar * 0.6):
            raise DeviceError(
                "Cannot start concrete print: pump not primed to target pressure."
            )

        self._layer_height_mm = config.layer_height_mm
        self._material_flow_l_min = config.extrusion_rate_l_min
        self._pump_pressure_bar = config.pump_pressure_bar
        self._nozzle_height_mm = config.layer_height_mm

        job = _ConcreteJob(file_name=file_name, config=config, total_segments=400)
        self._current_job = job
        self._status = DeviceStatus.OPERATING
        self._error_message = None
        logger.info("Concrete sim: started print '%s' at %.1f mm/s", file_name, config.print_speed_mm_s)
        return OperationResult(
            success=True,
            message=f"Concrete print started: {file_name}.",
            job_id=job.job_id,
        )

    def cancel_print(self) -> OperationResult:
        if self._current_job is None:
            raise DeviceError("No active concrete print to cancel.")
        job_id = self._current_job.job_id
        self._current_job = None
        self._status = DeviceStatus.IDLE
        self._material_flow_l_min = 0.0
        self._pump_pressure_bar = 0.0
        return OperationResult(success=True, message=f"Concrete print {job_id} cancelled.", job_id=job_id)

    def pause_print(self) -> OperationResult:
        if self._current_job is None or self._status != DeviceStatus.OPERATING:
            raise DeviceError("No active concrete print to pause.")
        self._current_job.pause()
        self._status = DeviceStatus.PAUSED
        self._material_flow_l_min = 0.0
        return OperationResult(
            success=True,
            message=f"Concrete print {self._current_job.job_id} paused.",
            job_id=self._current_job.job_id,
        )

    def resume_print(self) -> OperationResult:
        if self._current_job is None or self._status != DeviceStatus.PAUSED:
            raise DeviceError("No paused concrete print to resume.")
        if not self._emergency_stop_clear:
            raise DeviceError("Cannot resume: emergency stop is engaged.")
        if not self._weather_safe:
            raise DeviceError("Cannot resume: weather interlock is unsafe.")
        self._current_job.resume()
        self._status = DeviceStatus.OPERATING
        self._material_flow_l_min = self._current_job.config.extrusion_rate_l_min
        return OperationResult(
            success=True,
            message=f"Concrete print {self._current_job.job_id} resumed.",
            job_id=self._current_job.job_id,
        )

    def emergency_stop(self) -> OperationResult:
        job_id = self._current_job.job_id if self._current_job is not None else None
        self._current_job = None
        self._status = DeviceStatus.IDLE
        self._material_flow_l_min = 0.0
        self._pump_pressure_bar = 0.0
        self._emergency_stop_clear = False
        self._error_message = "Emergency stop triggered"
        logger.warning("Concrete sim: EMERGENCY STOP")
        return OperationResult(
            success=True,
            message="Emergency stop executed. Pump depressurised and motion halted.",
            job_id=job_id,
        )

    def check_pump_pressure(self) -> float:
        return round(self._pump_pressure_bar, 1)

    def check_material_flow(self) -> float:
        return round(self._material_flow_l_min, 2)

    def check_emergency_stop(self) -> bool:
        return self._emergency_stop_clear

    def check_weather_safe(self) -> bool:
        return self._weather_safe

    def prime_pump(self, target_pressure_bar: float) -> OperationResult:
        if target_pressure_bar < _MIN_PUMP_PRESSURE_BAR or target_pressure_bar > _MAX_PUMP_PRESSURE_BAR:
            raise DeviceError(
                f"Pump pressure {target_pressure_bar} bar is outside supported range "
                f"({_MIN_PUMP_PRESSURE_BAR}--{_MAX_PUMP_PRESSURE_BAR})."
            )
        if not self._emergency_stop_clear:
            raise DeviceError("Cannot prime pump while emergency stop is engaged.")
        self._pump_pressure_bar = target_pressure_bar
        return OperationResult(
            success=True,
            message=f"Pump primed to {target_pressure_bar:.1f} bar.",
        )

    def tick(self, *, segments: int = 1) -> None:
        """Advance the simulation by *segments* path segments."""
        if self._current_job is None or self._status != DeviceStatus.OPERATING:
            return
        for _ in range(max(1, segments)):
            self._current_job.advance()
            self._gantry_position["x"] = min(
                self._build_volume_mm[0],
                self._gantry_position["x"] + 25.0,
            )
            if self._current_job.current_segment >= self._current_job.total_segments:
                self._status = DeviceStatus.IDLE
                self._material_flow_l_min = 0.0
                self._pump_pressure_bar = 0.0
                self._nozzle_height_mm = 0.0
                self._current_job = None
                break

    def set_connected(self, connected: bool) -> None:
        self._connected = connected
        if not connected:
            self._status = DeviceStatus.OFFLINE
        elif self._status == DeviceStatus.OFFLINE:
            self._status = DeviceStatus.IDLE

    def set_weather_safe(self, safe: bool) -> None:
        self._weather_safe = safe

    def clear_emergency_stop(self) -> None:
        self._emergency_stop_clear = True
        if self._status == DeviceStatus.ERROR:
            self._status = DeviceStatus.IDLE
        if self._error_message == "Emergency stop triggered":
            self._error_message = None

    def inject_error(self, message: str) -> None:
        self._status = DeviceStatus.ERROR
        self._error_message = message
        self._current_job = None
        self._material_flow_l_min = 0.0

    def clear_error(self) -> None:
        self._status = DeviceStatus.IDLE
        self._error_message = None

    def _validate_config(self, config: ConcretePrintConfig) -> None:
        if config.layer_height_mm < _MIN_LAYER_HEIGHT_MM or config.layer_height_mm > _MAX_LAYER_HEIGHT_MM:
            raise DeviceError(
                f"Layer height {config.layer_height_mm} mm is outside "
                f"{_MIN_LAYER_HEIGHT_MM}--{_MAX_LAYER_HEIGHT_MM} mm."
            )
        if config.print_speed_mm_s < _MIN_SPEED_MM_S or config.print_speed_mm_s > _MAX_SPEED_MM_S:
            raise DeviceError(
                f"Print speed {config.print_speed_mm_s} mm/s is outside "
                f"{_MIN_SPEED_MM_S}--{_MAX_SPEED_MM_S} mm/s."
            )
        if (
            config.extrusion_rate_l_min < _MIN_EXTRUSION_L_MIN
            or config.extrusion_rate_l_min > _MAX_EXTRUSION_L_MIN
        ):
            raise DeviceError(
                f"Extrusion rate {config.extrusion_rate_l_min} L/min is outside "
                f"{_MIN_EXTRUSION_L_MIN}--{_MAX_EXTRUSION_L_MIN} L/min."
            )
        if (
            config.nozzle_diameter_mm < _MIN_NOZZLE_DIAMETER_MM
            or config.nozzle_diameter_mm > _MAX_NOZZLE_DIAMETER_MM
        ):
            raise DeviceError(
                f"Nozzle diameter {config.nozzle_diameter_mm} mm is outside "
                f"{_MIN_NOZZLE_DIAMETER_MM}--{_MAX_NOZZLE_DIAMETER_MM} mm."
            )
        if (
            config.pump_pressure_bar < _MIN_PUMP_PRESSURE_BAR
            or config.pump_pressure_bar > _MAX_PUMP_PRESSURE_BAR
        ):
            raise DeviceError(
                f"Pump pressure {config.pump_pressure_bar} bar is outside "
                f"{_MIN_PUMP_PRESSURE_BAR}--{_MAX_PUMP_PRESSURE_BAR}."
            )
