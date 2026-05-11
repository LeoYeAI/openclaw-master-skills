"""Write-Ahead Log (ADR-003)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


class WALEntry:
    """A single WAL entry."""

    def __init__(
        self,
        operation: str,
        target: str,
        payload_hash: str,
        entry_id: str | None = None,
        status: str = "pending",
        timestamp: str | None = None,
        payload: str | None = None,
    ):
        self.id = entry_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.operation = operation
        self.target = target
        self.payload_hash = payload_hash
        self.status = status
        self.payload = payload

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "target": self.target,
            "payload_hash": self.payload_hash,
            "status": self.status,
        }
        if self.payload is not None:
            d["payload"] = self.payload
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "WALEntry":
        return cls(
            entry_id=data["id"],
            timestamp=data["timestamp"],
            operation=data["operation"],
            target=data["target"],
            payload_hash=data["payload_hash"],
            status=data.get("status", "pending"),
            payload=data.get("payload"),
        )


class WAL:
    """Write-Ahead Log manager."""

    def __init__(self, palaia_root: Path):
        self.wal_dir = palaia_root / "wal"
        self.wal_dir.mkdir(parents=True, exist_ok=True)

    def _entry_path(self, entry: WALEntry) -> Path:
        ts = entry.timestamp.replace(":", "-").replace("+", "p")
        return self.wal_dir / f"{ts}-{entry.id}.json"

    def log(self, entry: WALEntry) -> Path:
        """Write a pending WAL entry to disk."""
        path = self._entry_path(entry)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(entry.to_dict(), f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        tmp.rename(path)
        return path

    def commit(self, entry: WALEntry) -> None:
        """Mark a WAL entry as committed."""
        entry.status = "committed"
        path = self._entry_path(entry)
        if path.exists():
            with open(path, "w") as f:
                json.dump(entry.to_dict(), f, indent=2)
                f.flush()
                os.fsync(f.fileno())

    def get_pending(self) -> list[WALEntry]:
        """Return all pending (uncommitted) WAL entries."""
        pending = []
        for p in sorted(self.wal_dir.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                if data.get("status") == "pending":
                    pending.append(WALEntry.from_dict(data))
            except (json.JSONDecodeError, KeyError):
                continue
        return pending

    def recover(self, store) -> int:
        """Replay pending entries. Returns count of recovered entries."""
        pending = self.get_pending()
        recovered = 0
        for entry in pending:
            if entry.operation == "write" and entry.payload:
                store.write_raw(entry.target, entry.payload)
                self.commit(entry)
                recovered += 1
            elif entry.operation == "delete":
                store.delete_raw(entry.target)
                self.commit(entry)
                recovered += 1
            else:
                # Can't recover without payload, mark rolled back
                entry.status = "rolled_back"
                path = self._entry_path(entry)
                if path.exists():
                    with open(path, "w") as f:
                        json.dump(entry.to_dict(), f, indent=2)
        return recovered

    def cleanup(self, max_age_days: int = 7) -> int:
        """Remove old committed/rolled_back WAL entries."""
        now = datetime.now(timezone.utc)
        removed = 0
        for p in self.wal_dir.glob("*.json"):
            try:
                with open(p) as f:
                    data = json.load(f)
                if data.get("status") in ("committed", "rolled_back"):
                    ts = datetime.fromisoformat(data["timestamp"])
                    if (now - ts).days >= max_age_days:
                        p.unlink()
                        removed += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return removed
