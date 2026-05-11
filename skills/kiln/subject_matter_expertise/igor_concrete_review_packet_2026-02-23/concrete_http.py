"""Generic HTTP adapter for structural concrete 3D printers.

Many construction-printer OEMs expose private/proprietary APIs. This adapter
provides a configurable REST contract so Forge can integrate quickly when an
endpoint map and credentials are available.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.exceptions import ConnectionError as ReqConnectionError
from requests.exceptions import RequestException, Timeout

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

_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({408, 425, 429, 500, 502, 503, 504})

_STATUS_MAP: Dict[str, DeviceStatus] = {
    "idle": DeviceStatus.IDLE,
    "ready": DeviceStatus.IDLE,
    "operating": DeviceStatus.OPERATING,
    "printing": DeviceStatus.OPERATING,
    "paused": DeviceStatus.PAUSED,
    "error": DeviceStatus.ERROR,
    "offline": DeviceStatus.OFFLINE,
    "busy": DeviceStatus.BUSY,
    "starting": DeviceStatus.BUSY,
}

_DEFAULT_ENDPOINTS: Dict[str, str] = {
    "state": "/api/v1/state",
    "job": "/api/v1/job",
    "upload": "/api/v1/files",
    "start": "/api/v1/prints/start",
    "cancel": "/api/v1/prints/cancel",
    "pause": "/api/v1/prints/pause",
    "resume": "/api/v1/prints/resume",
    "estop": "/api/v1/prints/emergency-stop",
    "pressure": "/api/v1/pump/pressure",
    "flow": "/api/v1/pump/flow",
    "estop_status": "/api/v1/safety/estop",
    "weather": "/api/v1/safety/weather",
    "prime": "/api/v1/pump/prime",
}


def _status(raw: Any) -> DeviceStatus:
    if not isinstance(raw, str):
        return DeviceStatus.UNKNOWN
    return _STATUS_MAP.get(raw.lower().strip(), DeviceStatus.UNKNOWN)


def _safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    cur = data
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key, default)
    return cur


class ConcreteHTTPAdapter(ConcreteAdapter):
    """ConcreteAdapter backed by configurable HTTP endpoints."""

    def __init__(
        self,
        *,
        host: str,
        vendor: str,
        model: str,
        api_key: str = "",
        timeout: float = 10.0,
        retries: int = 2,
        endpoints: Optional[Dict[str, str]] = None,
        capabilities: Optional[ConcreteCapabilities] = None,
    ) -> None:
        if not host or not host.strip():
            raise ValueError("host must not be empty")
        if not vendor.strip():
            raise ValueError("vendor must not be empty")
        if not model.strip():
            raise ValueError("model must not be empty")

        self._host: str = host.rstrip("/")
        self._vendor: str = vendor.strip()
        self._model: str = model.strip()
        self._timeout: float = timeout
        self._retries: int = max(1, retries)
        self._endpoints: Dict[str, str] = dict(_DEFAULT_ENDPOINTS)
        if endpoints:
            self._endpoints.update(endpoints)
        self._caps: ConcreteCapabilities = capabilities or ConcreteCapabilities()

        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        if api_key:
            self._session.headers.update({"Authorization": f"Bearer {api_key}"})

    @property
    def name(self) -> str:
        return f"{self._vendor} {self._model}"

    @property
    def capabilities(self) -> ConcreteCapabilities:
        return self._caps

    def _url(self, endpoint_key: str) -> str:
        endpoint = self._endpoints.get(endpoint_key)
        if not endpoint:
            raise DeviceError(f"Endpoint mapping missing for {endpoint_key!r}.")
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self._host}{endpoint}"

    def _request(
        self,
        method: str,
        endpoint_key: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = self._url(endpoint_key)
        last_exc: Optional[Exception] = None

        for attempt in range(self._retries):
            try:
                response = self._session.request(
                    method,
                    url,
                    json=json,
                    files=files,
                    data=data,
                    timeout=self._timeout,
                )
                if response.ok:
                    return response
                if response.status_code not in _RETRYABLE_STATUS_CODES:
                    raise DeviceError(
                        f"{self.name} API returned HTTP {response.status_code} "
                        f"for {method} {endpoint_key}: {response.text[:240]}"
                    )
                last_exc = DeviceError(
                    f"{self.name} API returned retryable HTTP {response.status_code} "
                    f"for {method} {endpoint_key} (attempt {attempt + 1}/{self._retries})"
                )
            except Timeout as exc:
                last_exc = DeviceError(
                    f"Timeout calling {self.name} endpoint {endpoint_key}",
                    cause=exc,
                )
            except ReqConnectionError as exc:
                last_exc = DeviceError(
                    f"Connection error talking to {self.name} at {self._host}",
                    cause=exc,
                )
            except RequestException as exc:
                raise DeviceError(f"Request error for {self.name}: {exc}", cause=exc) from exc

            if attempt < self._retries - 1:
                time.sleep(2 ** attempt)

        assert last_exc is not None
        raise last_exc

    def _json(self, method: str, endpoint_key: str, **kwargs: Any) -> Dict[str, Any]:
        resp = self._request(method, endpoint_key, **kwargs)
        try:
            return resp.json()  # type: ignore[no-any-return]
        except ValueError as exc:
            raise DeviceError(
                f"Invalid JSON in {self.name} response for endpoint {endpoint_key}",
                cause=exc,
            ) from exc

    def get_state(self) -> ConcreteState:
        payload = self._json("GET", "state")
        return ConcreteState(
            connected=bool(payload.get("connected", True)),
            state=_status(payload.get("status")),
            device_type="concrete_printer",
            firmware_version=payload.get("firmware_version"),
            error_message=payload.get("error_message"),
            pump_pressure_bar=float(payload.get("pump_pressure_bar"))
            if payload.get("pump_pressure_bar") is not None
            else None,
            material_flow_l_min=float(payload.get("material_flow_l_min"))
            if payload.get("material_flow_l_min") is not None
            else None,
            nozzle_height_mm=float(payload.get("nozzle_height_mm"))
            if payload.get("nozzle_height_mm") is not None
            else None,
            layer_height_mm=float(payload.get("layer_height_mm"))
            if payload.get("layer_height_mm") is not None
            else None,
            gantry_position=payload.get("gantry_position"),
            emergency_stop_clear=bool(payload.get("emergency_stop_clear", True)),
            weather_safe=payload.get("weather_safe"),
        )

    def get_job(self) -> JobProgress:
        payload = self._json("GET", "job")
        return JobProgress(
            file_name=payload.get("file_name"),
            completion=float(payload.get("completion"))
            if payload.get("completion") is not None
            else None,
            time_seconds=int(payload.get("time_seconds"))
            if payload.get("time_seconds") is not None
            else None,
            time_left_seconds=int(payload.get("time_left_seconds"))
            if payload.get("time_left_seconds") is not None
            else None,
        )

    def upload_file(self, file_path: str) -> OperationResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)
        with path.open("rb") as fh:
            payload = self._json(
                "POST",
                "upload",
                files={"file": (path.name, fh)},
            )
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", f"Uploaded '{path.name}'.")),
            job_id=payload.get("job_id"),
        )

    def start_print(self, file_name: str, config: ConcretePrintConfig) -> OperationResult:
        payload = self._json(
            "POST",
            "start",
            json={"file_name": file_name, "config": config.to_dict()},
        )
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", f"Started print '{file_name}'.")),
            job_id=payload.get("job_id"),
        )

    def cancel_print(self) -> OperationResult:
        payload = self._json("POST", "cancel", json={})
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", "Concrete print cancelled.")),
            job_id=payload.get("job_id"),
        )

    def pause_print(self) -> OperationResult:
        payload = self._json("POST", "pause", json={})
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", "Concrete print paused.")),
            job_id=payload.get("job_id"),
        )

    def resume_print(self) -> OperationResult:
        payload = self._json("POST", "resume", json={})
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", "Concrete print resumed.")),
            job_id=payload.get("job_id"),
        )

    def emergency_stop(self) -> OperationResult:
        payload = self._json("POST", "estop", json={})
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(payload.get("message", "Emergency stop executed.")),
            job_id=payload.get("job_id"),
        )

    def check_pump_pressure(self) -> float:
        payload = self._json("GET", "pressure")
        value = _safe_get(payload, "pump_pressure_bar", default=payload.get("value"))
        if value is None:
            raise DeviceError(f"{self.name} did not return a pump pressure value.")
        return float(value)

    def check_material_flow(self) -> float:
        payload = self._json("GET", "flow")
        value = _safe_get(payload, "material_flow_l_min", default=payload.get("value"))
        if value is None:
            raise DeviceError(f"{self.name} did not return a material flow value.")
        return float(value)

    def check_emergency_stop(self) -> bool:
        payload = self._json("GET", "estop_status")
        if "emergency_stop_clear" in payload:
            return bool(payload["emergency_stop_clear"])
        if "engaged" in payload:
            return not bool(payload["engaged"])
        return bool(payload.get("ok", True))

    def check_weather_safe(self) -> bool:
        payload = self._json("GET", "weather")
        if "weather_safe" in payload:
            return bool(payload["weather_safe"])
        if "ok" in payload:
            return bool(payload["ok"])
        return True

    def prime_pump(self, target_pressure_bar: float) -> OperationResult:
        payload = self._json(
            "POST",
            "prime",
            json={"target_pressure_bar": target_pressure_bar},
        )
        return OperationResult(
            success=bool(payload.get("success", True)),
            message=str(
                payload.get(
                    "message",
                    f"Pump primed to {target_pressure_bar:.1f} bar.",
                )
            ),
            job_id=payload.get("job_id"),
        )
