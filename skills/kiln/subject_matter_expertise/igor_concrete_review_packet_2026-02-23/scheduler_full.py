"""Multi-device job scheduler — dispatches queued jobs to available devices.

The scheduler runs in a background thread, periodically checking for:
1. Queued jobs that need to be dispatched
2. Idle devices that can accept work
3. Running jobs that need progress monitoring

It bridges the gap between the job queue (where agents submit work)
and the device registry (where physical devices live).  Unlike kiln's
:class:`JobScheduler`, this scheduler is device-type-aware: SLA jobs
are only dispatched to SLA devices, laser jobs to laser devices, CNC
jobs to CNC devices, and concrete jobs to concrete printers.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from forge.devices.base import (
    CNCAdapter,
    ConcreteAdapter,
    DeviceError,
    DeviceStatus,
    LaserAdapter,
    SLAAdapter,
)
from forge.events import ForgeEventType
from forge.queue import DeviceJobStatus, DeviceQueue
from forge.registry import DeviceAdapter, DeviceNotFoundError, DeviceRegistry

logger = logging.getLogger(__name__)


# Default stuck job timeout per device type (seconds).
_STUCK_JOB_TIMEOUTS: dict[str, float] = {
    "sla": 28800.0,   # 8 hours — SLA prints are slow
    "laser": 7200.0,  # 2 hours
    "cnc": 7200.0,    # 2 hours
    "concrete": 21600.0,  # 6 hours
}
_DEFAULT_STUCK_TIMEOUT: float = 7200.0  # fallback: 2 hours


class DeviceScheduler:
    """Background scheduler that dispatches jobs to heterogeneous devices.

    Lifecycle::

        scheduler = DeviceScheduler(queue, registry, event_bus)
        scheduler.start()   # launches background thread
        ...
        scheduler.stop()    # graceful shutdown

    The scheduler polls every ``poll_interval`` seconds (default 5).
    Jobs stuck in OPERATING state beyond the device-type-specific timeout
    are auto-failed.
    """

    def __init__(
        self,
        queue: DeviceQueue,
        registry: DeviceRegistry,
        event_bus: Any | None = None,
        *,
        poll_interval: float = 5.0,
        max_retries: int = 2,
        retry_backoff_base: float = 30.0,
        stuck_timeouts: dict[str, float] | None = None,
    ) -> None:
        self._queue = queue
        self._registry = registry
        self._event_bus = event_bus
        self._poll_interval = poll_interval
        self._max_retries = max_retries
        self._retry_backoff_base = retry_backoff_base
        self._stuck_timeouts = stuck_timeouts or dict(_STUCK_JOB_TIMEOUTS)
        self._running = False
        self._thread: threading.Thread | None = None
        self._active_jobs: dict[str, str] = {}  # job_id -> device_name
        self._retry_counts: dict[str, int] = {}  # job_id -> attempts
        self._retry_not_before: dict[str, float] = {}  # job_id -> earliest retry
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Whether the scheduler background thread is running."""
        return self._running

    @property
    def active_jobs(self) -> dict[str, str]:
        """Return a copy of the active job -> device mapping."""
        with self._lock:
            return dict(self._active_jobs)

    def start(self) -> None:
        """Start the scheduler background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="forge-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Device scheduler started (poll every %.1fs)", self._poll_interval
        )

    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=self._poll_interval * 2)
            self._thread = None
        logger.info("Device scheduler stopped")

    # ------------------------------------------------------------------
    # Event publishing helper
    # ------------------------------------------------------------------

    def _publish(
        self,
        event_type: ForgeEventType,
        data: dict[str, Any],
        *,
        source: str = "scheduler",
    ) -> None:
        """Publish an event if an event bus is configured."""
        if self._event_bus is None:
            return
        try:
            self._event_bus.publish(event_type, data, source=source)
        except Exception:
            logger.warning(
                "Failed to publish event %s for job %s (non-fatal)",
                event_type.value,
                data.get("job_id", "unknown"),
                exc_info=True,
            )

    # ------------------------------------------------------------------
    # Retry logic
    # ------------------------------------------------------------------

    def _requeue_or_fail(
        self,
        job_id: str,
        error_msg: str,
        failed_list: list[dict[str, str]],
        *,
        device_name: str | None = None,
        device_type: str | None = None,
    ) -> bool:
        """Try to re-queue a failed job if retries remain.

        Returns ``True`` if the job was re-queued, ``False`` if it was
        permanently marked as failed (appended to *failed_list*).
        """
        count = self._retry_counts.get(job_id, 0)
        if count < self._max_retries:
            self._retry_counts[job_id] = count + 1
            # Exponential backoff: 30s, 60s, 120s, ...
            delay = self._retry_backoff_base * (2 ** count)
            self._retry_not_before[job_id] = time.time() + delay
            # Reset the job back to QUEUED for future dispatch
            with self._lock:
                job = self._queue.get_job(job_id)
                job.status = DeviceJobStatus.QUEUED
                job.started_at = None
                job.error = None
            logger.info(
                "Re-queued job %s (retry %d/%d, backoff %.0fs): %s",
                job_id,
                count + 1,
                self._max_retries,
                delay,
                error_msg,
            )
            return True

        # Retries exhausted — mark permanently failed
        self._retry_counts.pop(job_id, None)
        self._retry_not_before.pop(job_id, None)
        self._queue.mark_failed(job_id, error_msg)
        fail_event = (
            self._get_event_type_for_fail(device_type)
            if device_type
            else ForgeEventType.MULTI_JOB_FAILED
        )
        self._publish(
            fail_event,
            {"job_id": job_id, "error": error_msg},
        )
        failed_list.append({"job_id": job_id, "error": error_msg})
        return False

    # ------------------------------------------------------------------
    # Device-type-aware dispatch
    # ------------------------------------------------------------------

    def _start_device_job(
        self,
        adapter: DeviceAdapter,
        device_type: str,
        file_name: str,
    ) -> Any:
        """Call the correct start method based on device type.

        SLA -> start_print, laser -> start_cut, CNC -> start_job,
        concrete -> start_print.
        A minimal default config is provided when the job has none.
        """
        if device_type == "sla" and isinstance(adapter, SLAAdapter):
            from forge.devices.base import SLAPrintConfig
            config = SLAPrintConfig(
                exposure_time_s=8.0,
                bottom_exposure_time_s=50.0,
                layer_height_um=50,
                lift_speed_mm_min=60.0,
                retract_speed_mm_min=150.0,
            )
            return adapter.start_print(file_name, config)
        elif device_type == "laser" and isinstance(adapter, LaserAdapter):
            from forge.devices.base import CutConfig
            config = CutConfig(
                power_percent=50.0,
                speed_mm_s=10.0,
                passes=1,
            )
            return adapter.start_cut(file_name, config)
        elif device_type == "cnc" and isinstance(adapter, CNCAdapter):
            from forge.devices.base import CNCJobConfig
            config = CNCJobConfig(
                tool_id=1,
                rpm=12000.0,
                feed_mm_min=1000.0,
                plunge_mm_min=500.0,
                depth_mm=5.0,
            )
            return adapter.start_job(file_name, config)
        elif device_type == "concrete" and isinstance(adapter, ConcreteAdapter):
            from forge.devices.base import ConcretePrintConfig
            config = ConcretePrintConfig(
                layer_height_mm=20.0,
                print_speed_mm_s=250.0,
                extrusion_rate_l_min=25.0,
                nozzle_diameter_mm=25.0,
                pump_pressure_bar=90.0,
            )
            return adapter.start_print(file_name, config)
        else:
            raise DeviceError(
                f"Unsupported device type {device_type!r} for adapter "
                f"{type(adapter).__name__}"
            )

    def _get_event_type_for_start(self, device_type: str) -> ForgeEventType:
        """Return the appropriate started event for the device type."""
        _map = {
            "sla": ForgeEventType.SLA_PRINT_STARTED,
            "laser": ForgeEventType.LASER_CUT_STARTED,
            "cnc": ForgeEventType.CNC_JOB_STARTED,
            "concrete": ForgeEventType.CONCRETE_PRINT_STARTED,
        }
        return _map.get(device_type, ForgeEventType.MULTI_JOB_STARTED)

    def _get_event_type_for_complete(self, device_type: str) -> ForgeEventType:
        """Return the appropriate completed event for the device type."""
        _map = {
            "sla": ForgeEventType.SLA_PRINT_COMPLETED,
            "laser": ForgeEventType.LASER_CUT_COMPLETED,
            "cnc": ForgeEventType.CNC_JOB_COMPLETED,
            "concrete": ForgeEventType.CONCRETE_PRINT_COMPLETED,
        }
        return _map.get(device_type, ForgeEventType.MULTI_JOB_COMPLETED)

    def _get_event_type_for_fail(self, device_type: str) -> ForgeEventType:
        """Return the appropriate failed event for the device type."""
        _map = {
            "sla": ForgeEventType.SLA_PRINT_FAILED,
            "laser": ForgeEventType.LASER_CUT_FAILED,
            "cnc": ForgeEventType.CNC_JOB_FAILED,
            "concrete": ForgeEventType.CONCRETE_PRINT_FAILED,
        }
        return _map.get(device_type, ForgeEventType.MULTI_JOB_FAILED)

    def _stuck_timeout_for(self, device_type: str) -> float:
        """Return the stuck-job timeout for the given device type."""
        return self._stuck_timeouts.get(device_type, _DEFAULT_STUCK_TIMEOUT)

    # ------------------------------------------------------------------
    # Core scheduling loop
    # ------------------------------------------------------------------

    def tick(self) -> dict[str, Any]:
        """Run one scheduling cycle.  Can be called manually for testing.

        Returns a dict summarising what happened::

            {
                "dispatched": [{"job_id": ..., "device_name": ..., "file_name": ...}],
                "completed": ["job_id", ...],
                "failed": [{"job_id": ..., "error": ...}],
                "checked": <int>,
            }
        """
        dispatched: list[dict[str, Any]] = []
        completed: list[str] = []
        failed: list[dict[str, str]] = []
        checked = 0

        # Phase 1: Check active jobs for completion / failure
        with self._lock:
            active_snapshot = dict(self._active_jobs)

        for job_id, device_name in active_snapshot.items():
            checked += 1
            try:
                job = self._queue.get_job(job_id)
                adapter = self._registry.get(device_name)
                state = adapter.get_state()

                # Device returned to idle — job is done
                if state.state == DeviceStatus.IDLE:
                    self._queue.mark_completed(job_id)
                    with self._lock:
                        self._active_jobs.pop(job_id, None)
                        self._retry_counts.pop(job_id, None)
                        self._retry_not_before.pop(job_id, None)
                    self._publish(
                        self._get_event_type_for_complete(job.device_type),
                        {"job_id": job_id, "device_name": device_name},
                    )
                    completed.append(job_id)

                elif state.state == DeviceStatus.ERROR:
                    error_msg = f"Device {device_name} entered error state"
                    with self._lock:
                        self._active_jobs.pop(job_id, None)
                    self._requeue_or_fail(
                        job_id, error_msg, failed,
                        device_name=device_name,
                        device_type=job.device_type,
                    )

                elif state.state == DeviceStatus.OPERATING:
                    # Promote STARTING -> OPERATING when device confirms
                    try:
                        if job.status == DeviceJobStatus.STARTING:
                            self._queue.mark_operating(job_id)
                    except Exception:
                        pass

                    # Stuck job detection
                    if (
                        job.started_at is not None
                        and (time.time() - job.started_at)
                        > self._stuck_timeout_for(job.device_type)
                    ):
                        timeout_h = (
                            self._stuck_timeout_for(job.device_type) / 3600.0
                        )
                        error_msg = (
                            f"Job timed out after {timeout_h:.0f}h "
                            f"-- device may be disconnected or hung"
                        )
                        logger.warning(
                            "Stuck job detected: %s on %s (%.0f min)",
                            job_id,
                            device_name,
                            (time.time() - job.started_at) / 60,
                        )
                        with self._lock:
                            self._active_jobs.pop(job_id, None)
                        self._requeue_or_fail(
                            job_id, error_msg, failed,
                            device_name=device_name,
                            device_type=job.device_type,
                        )

            except DeviceNotFoundError:
                error_msg = f"Device {device_name} no longer registered"
                with self._lock:
                    self._active_jobs.pop(job_id, None)
                self._requeue_or_fail(
                    job_id, error_msg, failed,
                    device_name=device_name,
                    device_type=job.device_type,
                )
            except Exception as exc:
                logger.warning(
                    "Error checking job %s on %s: %s",
                    job_id,
                    device_name,
                    exc,
                )

        # Phase 2: Dispatch queued jobs to idle devices
        # Group idle devices by type for efficient routing
        device_types_to_check = {"sla", "laser", "cnc", "concrete"}
        with self._lock:
            busy_devices = set(self._active_jobs.values())

        for dtype in device_types_to_check:
            idle_devices = self._registry.get_idle_devices(device_type=dtype)
            available = [d for d in idle_devices if d not in busy_devices]

            for device_name in available:
                next_job = self._queue.next_job(
                    device_name=device_name, device_type=dtype
                )
                if next_job is None:
                    continue

                # Respect exponential backoff for retried jobs
                not_before = self._retry_not_before.get(next_job.id)
                if not_before is not None and time.time() < not_before:
                    continue

                # Clear the backoff gate once past it
                self._retry_not_before.pop(next_job.id, None)

                # Acquire per-device lock to prevent concurrent ops
                device_mutex = self._registry.device_lock(device_name)
                if not device_mutex.acquire(blocking=False):
                    logger.debug(
                        "Device %s locked, skipping dispatch", device_name
                    )
                    continue
                try:
                    adapter = self._registry.get(device_name)
                    self._queue.mark_starting(next_job.id)

                    result = self._start_device_job(
                        adapter, next_job.device_type, next_job.file_name
                    )
                    if result.success:
                        self._queue.mark_operating(next_job.id)
                        with self._lock:
                            self._active_jobs[next_job.id] = device_name
                        # Update busy set so same device isn't reused this tick
                        busy_devices.add(device_name)
                        self._publish(
                            self._get_event_type_for_start(next_job.device_type),
                            {
                                "job_id": next_job.id,
                                "device_name": device_name,
                                "file_name": next_job.file_name,
                            },
                        )
                        dispatched.append({
                            "job_id": next_job.id,
                            "device_name": device_name,
                            "file_name": next_job.file_name,
                        })
                    else:
                        error_msg = (
                            result.message or "start operation returned failure"
                        )
                        self._requeue_or_fail(
                            next_job.id, error_msg, failed,
                            device_type=next_job.device_type,
                        )

                except DeviceError as exc:
                    error_msg = (
                        f"Failed to start job on {device_name}: {exc}"
                    )
                    self._requeue_or_fail(
                        next_job.id, error_msg, failed,
                        device_type=next_job.device_type,
                    )
                except Exception as exc:
                    logger.exception(
                        "Unexpected error dispatching job %s", next_job.id
                    )
                    self._requeue_or_fail(
                        next_job.id, str(exc), failed,
                        device_type=next_job.device_type,
                    )
                finally:
                    device_mutex.release()

        return {
            "dispatched": dispatched,
            "completed": completed,
            "failed": failed,
            "checked": checked,
        }

    def _run_loop(self) -> None:
        """Background polling loop."""
        while self._running:
            try:
                self.tick()
            except Exception:
                logger.exception("Scheduler tick failed")
            time.sleep(self._poll_interval)
