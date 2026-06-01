"""
Change-detection poller for Odoo models.

Runs a background thread that periodically queries Odoo for records
whose ``write_date`` is newer than the last poll, then fires registered
callbacks.
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill.poller")

# Type alias for watcher callbacks: fn(model: str, changed_records: list[dict])
ChangeCallback = Callable[[str, list[dict]], None]

# Persistent state file for last-check timestamps
_STATE_FILE = Path(__file__).resolve().parent.parent.parent / ".poller_state.json"


class OdooChangePoller:
    """Polls Odoo for recent changes and dispatches callbacks.

    Usage::

        poller = OdooChangePoller(client, interval=60)
        poller.watch("res.partner", on_partner_changed, fields=["name", "email"])
        poller.watch("sale.order", on_order_changed)
        poller.start()
        # …later…
        poller.stop()

    Args:
        client: An authenticated :class:`OdooClient`.
        interval: Seconds between poll cycles (default 60).
        state_file: Path for persisting last-check timestamps.
    """

    def __init__(
        self,
        client: OdooClient,
        interval: int = 60,
        state_file: Optional[Path] = None,
    ) -> None:
        self.client = client
        self.interval = interval
        self._state_file = state_file or _STATE_FILE

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._watchers: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

        # Load persisted timestamps
        self._load_state()

    # ── Public API ───────────────────────────────────────────────────

    def watch(
        self,
        model: str,
        callback: ChangeCallback,
        fields: Optional[list[str]] = None,
        domain: Optional[list] = None,
    ) -> None:
        """Register a model to watch for changes.

        Args:
            model: Odoo model name (e.g. ``res.partner``).
            callback: Function called with ``(model, changed_records)``
                when changes are detected.
            fields: Fields to include in the change records
                (always includes ``id``, ``write_date``).
            domain: Extra domain filter applied to all polls.
        """
        base_fields = list(set(["id", "name", "write_date"] + (fields or [])))

        with self._lock:
            self._watchers[model] = {
                "callback": callback,
                "fields": base_fields,
                "domain": domain or [],
                "last_check": self._watchers.get(model, {}).get(
                    "last_check",
                    datetime.now(timezone.utc).isoformat(),
                ),
            }
        logger.info("Watching %s for changes (fields=%s)", model, base_fields)

    def unwatch(self, model: str) -> None:
        """Stop watching a model.

        Args:
            model: The Odoo model name to stop polling.
        """
        with self._lock:
            removed = self._watchers.pop(model, None)
        if removed:
            logger.info("Stopped watching %s", model)
            self._save_state()

    def start(self) -> None:
        """Start the polling loop in a daemon thread."""
        if self._running:
            logger.warning("Poller is already running")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, name="odoo-poller", daemon=True,
        )
        self._thread.start()
        logger.info("Poller started (interval=%ds, watching %d models)",
                     self.interval, len(self._watchers))

    def stop(self) -> None:
        """Stop the polling loop and persist state."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.interval + 5)
        self._save_state()
        logger.info("Poller stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def watched_models(self) -> list[str]:
        with self._lock:
            return list(self._watchers.keys())

    # ── Internals ────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        """Main polling loop — runs in the background thread."""
        while self._running:
            self._poll_all()
            # Sleep in small increments so we can stop quickly
            for _ in range(self.interval):
                if not self._running:
                    break
                time.sleep(1)

    def _poll_all(self) -> None:
        """Poll every watched model for changes."""
        with self._lock:
            snapshot = dict(self._watchers)

        for model, config in snapshot.items():
            try:
                self._poll_model(model, config)
            except Exception:
                logger.exception("Error polling %s", model)

        self._save_state()

    def _poll_model(self, model: str, config: dict) -> None:
        """Poll a single model for changes since last_check."""
        domain: list = [
            ["write_date", ">", config["last_check"]],
            *config["domain"],
        ]
        changes = self.client.search_read(
            model, domain,
            fields=config["fields"],
            order="write_date desc",
            limit=200,
        )

        if changes:
            logger.info("Detected %d changes in %s", len(changes), model)
            try:
                config["callback"](model, changes)
            except Exception:
                logger.exception("Callback error for %s", model)

        # Advance the checkpoint
        with self._lock:
            if model in self._watchers:
                self._watchers[model]["last_check"] = (
                    datetime.now(timezone.utc).isoformat()
                )

    # ── State persistence ────────────────────────────────────────────

    def _load_state(self) -> None:
        """Load last-check timestamps from disk."""
        if not self._state_file.is_file():
            return
        try:
            with open(self._state_file, "r", encoding="utf-8") as fh:
                state = json.load(fh)
            for model, ts in state.items():
                if model in self._watchers:
                    self._watchers[model]["last_check"] = ts
            logger.debug("Loaded poller state from %s", self._state_file)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load poller state: %s", exc)

    def _save_state(self) -> None:
        """Persist last-check timestamps to disk."""
        with self._lock:
            state = {
                model: cfg["last_check"]
                for model, cfg in self._watchers.items()
            }
        if not state:
            return
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._state_file, "w", encoding="utf-8") as fh:
                json.dump(state, fh, indent=2)
        except OSError as exc:
            logger.warning("Could not save poller state: %s", exc)
