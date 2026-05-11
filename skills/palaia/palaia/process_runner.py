"""Process runner for executing process-type entries step by step (Issue #72).

Parses steps from process entries (numbered lists or markdown checkboxes),
tracks execution state, and persists progress.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Step parsing patterns
_NUMBERED_RE = re.compile(r"^\s*(\d+)[.)]\s+(.+)$")
_CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+(.+)$")


def parse_steps(content: str) -> list[dict]:
    """Parse steps from markdown content.

    Supports:
    - Numbered lists: "1. Do something" or "1) Do something"
    - Checkboxes: "- [ ] Do something" or "- [x] Already done"
    - Inline numbered lists: "1. Foo 2. Bar 3. Baz" (split into separate steps)

    Returns list of {"index": int, "text": str, "done": bool, "done_at": None|str}.
    """
    # Normalize inline numbered lists: "1. Foo 2. Bar" → separate lines
    # Only apply if no newlines with numbered items already exist
    lines = content.split("\n")
    has_multiline_numbers = any(_NUMBERED_RE.match(ln.strip()) for ln in lines if ln.strip())
    if not has_multiline_numbers:
        # Try to split inline: "1. Foo 2. Bar 3. Baz"
        content = re.sub(r"(?<!\n)\s+(\d+[.)]\s)", r"\n\1", content)

    steps: list[dict] = []
    for line in content.split("\n"):
        line = line.rstrip()
        if not line.strip():
            continue

        # Try checkbox first
        m = _CHECKBOX_RE.match(line)
        if m:
            checked = m.group(1).lower() == "x"
            steps.append(
                {
                    "index": len(steps),
                    "text": m.group(2).strip(),
                    "done": checked,
                    "done_at": None,
                }
            )
            continue

        # Try numbered list
        m = _NUMBERED_RE.match(line)
        if m:
            steps.append(
                {
                    "index": len(steps),
                    "text": m.group(2).strip(),
                    "done": False,
                    "done_at": None,
                }
            )
            continue

    return steps


class ProcessRun:
    """State for a single process execution run."""

    def __init__(self, entry_id: str, steps: list[dict], started_at: str | None = None):
        self.entry_id = entry_id
        self.steps = steps
        self.started_at = started_at or datetime.now(timezone.utc).isoformat()
        self.completed = all(s["done"] for s in steps) if steps else False

    def mark_done(self, step_index: int) -> bool:
        """Mark a step as done. Returns True if step existed.

        Args:
            step_index: 0-based step index.
        """
        if step_index < 0 or step_index >= len(self.steps):
            return False
        self.steps[step_index]["done"] = True
        self.steps[step_index]["done_at"] = datetime.now(timezone.utc).isoformat()
        self.completed = all(s["done"] for s in self.steps)
        return True

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "started_at": self.started_at,
            "steps": self.steps,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProcessRun":
        run = cls(
            entry_id=data["entry_id"],
            steps=data.get("steps", []),
            started_at=data.get("started_at"),
        )
        run.completed = data.get("completed", False)
        return run

    def progress_summary(self) -> str:
        """Human-readable progress summary."""
        done = sum(1 for s in self.steps if s["done"])
        total = len(self.steps)
        return f"{done}/{total} steps completed"


class ProcessRunManager:
    """Manages process run states on disk."""

    def __init__(self, palaia_root: Path):
        self.runs_dir = palaia_root / "process-runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def _run_path(self, entry_id: str) -> Path:
        return self.runs_dir / f"{entry_id}.json"

    def get(self, entry_id: str) -> ProcessRun | None:
        """Load an existing process run state."""
        path = self._run_path(entry_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ProcessRun.from_dict(data)
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def start(self, entry_id: str, content: str) -> ProcessRun:
        """Start a new process run (or return existing).

        Parses steps from the entry content and creates a run state.
        """
        existing = self.get(entry_id)
        if existing is not None:
            return existing

        steps = parse_steps(content)
        run = ProcessRun(entry_id=entry_id, steps=steps)
        self._save(run)
        return run

    def save(self, run: ProcessRun) -> None:
        """Save a process run to disk."""
        self._save(run)

    def _save(self, run: ProcessRun) -> None:
        path = self._run_path(run.entry_id)
        path.write_text(json.dumps(run.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    def list_runs(self) -> list[ProcessRun]:
        """List all process runs."""
        runs: list[ProcessRun] = []
        if not self.runs_dir.exists():
            return runs
        for p in sorted(self.runs_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                runs.append(ProcessRun.from_dict(data))
            except (json.JSONDecodeError, KeyError, OSError):
                continue
        return runs

    def delete(self, entry_id: str) -> bool:
        """Delete a process run state."""
        path = self._run_path(entry_id)
        if path.exists():
            path.unlink()
            return True
        return False
