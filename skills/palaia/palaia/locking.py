"""Project-level locking for multi-agent coordination (ADR-011).

Provides advisory locks so multiple agents don't work on the same
project simultaneously. Lock files live in .palaia/locks/<project>.lock.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 1800  # 30 minutes


class ProjectLockError(Exception):
    """Raised when a lock cannot be acquired."""

    pass


class ProjectLockManager:
    """Manage project-level advisory locks."""

    def __init__(self, palaia_root: Path):
        self.palaia_root = palaia_root
        self.locks_dir = palaia_root / "locks"

    def _lock_path(self, project: str) -> Path:
        return self.locks_dir / f"{project}.lock"

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _read_lock(self, project: str) -> dict | None:
        """Read lock file, return dict or None if missing/corrupt."""
        path = self._lock_path(project)
        if not path.exists():
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _is_expired(self, lock_data: dict) -> bool:
        """Check if a lock has expired based on its expires field."""
        expires_str = lock_data.get("expires")
        if not expires_str:
            return True
        expires = datetime.fromisoformat(expires_str)
        return self._now() >= expires

    def acquire(
        self,
        project: str,
        agent: str,
        reason: str = "",
        ttl: int | None = None,
    ) -> dict:
        """Acquire a project lock. Returns lock data on success.

        Raises ProjectLockError if already locked by another agent.
        """
        if ttl is None:
            ttl = DEFAULT_TTL_SECONDS

        existing = self._read_lock(project)
        if existing and not self._is_expired(existing):
            if existing.get("agent") == agent:
                # Same agent re-acquiring — just renew
                return self.renew(project, ttl=ttl)
            raise ProjectLockError(
                f"Project '{project}' is locked by {existing['agent']} "
                f"since {existing['acquired']} — reason: {existing.get('reason', 'n/a')}"
            )

        # Acquire
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        now = self._now()
        lock_data = {
            "project": project,
            "agent": agent,
            "reason": reason,
            "acquired": now.isoformat(),
            "ttl_seconds": ttl,
            "expires": (now + timedelta(seconds=ttl)).isoformat(),
        }
        with open(self._lock_path(project), "w") as f:
            json.dump(lock_data, f, ensure_ascii=False, indent=2)
        return lock_data

    def release(self, project: str) -> bool:
        """Release a project lock. Returns True if removed, False if not found."""
        path = self._lock_path(project)
        if path.exists():
            path.unlink()
            return True
        return False

    def status(self, project: str) -> dict | None:
        """Get lock status for a project. Returns lock data or None.

        Expired locks return None (treated as unlocked).
        """
        lock_data = self._read_lock(project)
        if lock_data is None:
            return None
        if self._is_expired(lock_data):
            return None
        # Add computed fields
        acquired = datetime.fromisoformat(lock_data["acquired"])
        age_seconds = (self._now() - acquired).total_seconds()
        lock_data["active"] = True
        lock_data["age_seconds"] = int(age_seconds)
        return lock_data

    def renew(self, project: str, ttl: int | None = None) -> dict:
        """Extend the TTL of an existing lock.

        Raises ProjectLockError if no active lock exists.
        """
        lock_data = self._read_lock(project)
        if lock_data is None:
            raise ProjectLockError(f"No lock found for project '{project}'")
        if self._is_expired(lock_data):
            raise ProjectLockError(f"Lock for project '{project}' has expired")

        if ttl is None:
            ttl = lock_data.get("ttl_seconds", DEFAULT_TTL_SECONDS)

        now = self._now()
        lock_data["ttl_seconds"] = ttl
        lock_data["expires"] = (now + timedelta(seconds=ttl)).isoformat()

        with open(self._lock_path(project), "w") as f:
            json.dump(lock_data, f, ensure_ascii=False, indent=2)
        return lock_data

    def break_lock(self, project: str) -> dict | None:
        """Force-remove a lock with warning log. Returns old lock data."""
        lock_data = self._read_lock(project)
        path = self._lock_path(project)
        if path.exists():
            path.unlink()
        if lock_data:
            logger.warning(
                "Lock for project '%s' force-broken (was held by %s since %s)",
                project,
                lock_data.get("agent", "unknown"),
                lock_data.get("acquired", "unknown"),
            )
        return lock_data

    def is_locked(self, project: str) -> bool:
        """Check if a project is currently locked (non-expired)."""
        return self.status(project) is not None

    def list_locks(self) -> list[dict]:
        """List all active (non-expired) locks."""
        if not self.locks_dir.exists():
            return []
        locks = []
        for lock_file in sorted(self.locks_dir.glob("*.lock")):
            project = lock_file.stem
            info = self.status(project)
            if info is not None:
                locks.append(info)
        return locks

    def gc(self) -> list[str]:
        """Remove expired lock files. Returns list of cleaned project names."""
        if not self.locks_dir.exists():
            return []
        cleaned = []
        for lock_file in list(self.locks_dir.glob("*.lock")):
            lock_data = self._read_lock(lock_file.stem)
            if lock_data and self._is_expired(lock_data):
                lock_file.unlink()
                cleaned.append(lock_file.stem)
        return cleaned
