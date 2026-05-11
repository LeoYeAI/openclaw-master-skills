"""Inter-Agent Messaging Subsystem (ADR-010).

Memos are lightweight messages between agents stored as markdown files
in `.palaia/memos/`. They are NOT entries — they have their own lifecycle:
no tiering, auto-expire via TTL, read/unread state, and GC cleanup.
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

DEFAULT_TTL_HOURS = 72


def _parse_yaml_simple(text: str) -> dict:
    """Minimal YAML-like parser for memo frontmatter."""
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "true":
            result[key] = True
        elif value == "false":
            result[key] = False
        elif value == "null":
            result[key] = None
        elif value.isdigit():
            result[key] = int(value)
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            result[key] = value[1:-1]
        else:
            result[key] = value
    return result


def _to_yaml_simple(data: dict) -> str:
    """Minimal dict -> YAML-like frontmatter string."""
    lines = []
    for k, v in data.items():
        if v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


def _parse_memo(text: str) -> tuple[dict, str]:
    """Parse a memo file into (metadata, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text.strip()
    meta = _parse_yaml_simple(m.group(1))
    body = text[m.end() :].strip()
    return meta, body


def _serialize_memo(meta: dict, body: str) -> str:
    """Serialize memo metadata and body to file format."""
    fm = _to_yaml_simple(meta)
    return f"---\n{fm}\n---\n\n{body}\n"


def _detect_agent() -> str | None:
    """Detect current agent from PALAIA_AGENT env var.

    Note: CLI layer resolves agent from config (palaia init --agent).
    This function is the low-level fallback for programmatic use.
    """
    return os.environ.get("PALAIA_AGENT")


class MemoManager:
    """Manages inter-agent memos in .palaia/memos/."""

    def __init__(self, palaia_root: Path):
        self.root = palaia_root
        self.memos_dir = palaia_root / "memos"
        self.memos_dir.mkdir(exist_ok=True)

    def send(
        self,
        to: str,
        message: str,
        from_agent: str | None = None,
        priority: str = "normal",
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> dict:
        """Send a memo to a specific agent. Returns memo metadata."""
        if not to:
            raise ValueError("Recipient ('to') is required")
        if not message:
            raise ValueError("Message body is required")
        if priority not in ("normal", "high"):
            raise ValueError(f"Invalid priority: {priority}. Must be 'normal' or 'high'")

        sender = from_agent or _detect_agent() or "unknown"
        now = datetime.now(timezone.utc)
        memo_id = str(uuid.uuid4())
        expires = now + timedelta(hours=ttl_hours)

        meta = {
            "id": memo_id,
            "from": sender,
            "to": to,
            "sent": now.isoformat(),
            "read": False,
            "read_at": None,
            "priority": priority,
            "expires": expires.isoformat(),
        }

        content = _serialize_memo(meta, message)
        memo_path = self.memos_dir / f"{memo_id}.md"
        memo_path.write_text(content, encoding="utf-8")

        return meta

    def broadcast(
        self,
        message: str,
        from_agent: str | None = None,
        priority: str = "normal",
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> dict:
        """Broadcast a memo to all agents. Uses '_broadcast' as recipient."""
        return self.send(
            to="_broadcast",
            message=message,
            from_agent=from_agent,
            priority=priority,
            ttl_hours=ttl_hours,
        )

    def get(self, memo_id: str) -> tuple[dict, str] | None:
        """Read a single memo by ID. Returns (meta, body) or None."""
        memo_path = self.memos_dir / f"{memo_id}.md"
        if not memo_path.exists():
            return None
        text = memo_path.read_text(encoding="utf-8")
        return _parse_memo(text)

    def inbox(
        self,
        agent: str | None = None,
        include_read: bool = False,
        aliases: dict[str, str] | None = None,
    ) -> list[tuple[dict, str]]:
        """List memos for an agent (including broadcasts).

        Args:
            agent: Agent name. If None, uses PALAIA_AGENT env var.
            include_read: If True, include already-read memos.
            aliases: Optional agent alias mapping for expanded matching.

        Returns:
            List of (meta, body) tuples sorted by sent time (newest first).
        """
        target = agent or _detect_agent()
        if not target:
            raise ValueError("Agent name required. Use --agent flag or set PALAIA_AGENT env var.")

        # Build set of all names that should match
        target_names = {target}
        if aliases:
            from palaia.config import resolve_agent_with_aliases

            target_names = resolve_agent_with_aliases(target, aliases)

        now = datetime.now(timezone.utc)
        results = []

        for memo_file in self.memos_dir.glob("*.md"):
            text = memo_file.read_text(encoding="utf-8")
            meta, body = _parse_memo(text)
            if not meta.get("id"):
                continue

            # Check expiry
            expires_str = meta.get("expires")
            if expires_str:
                try:
                    expires_dt = datetime.fromisoformat(expires_str)
                    if expires_dt < now:
                        continue
                except (ValueError, TypeError):
                    pass

            # Check recipient: must be addressed to agent (or alias) or broadcast
            to = meta.get("to", "")
            if to not in target_names and to != "_broadcast":
                continue

            # Filter read/unread
            if not include_read and meta.get("read") is True:
                continue

            results.append((meta, body))

        # Sort: high priority first, then by sent time descending
        high = [r for r in results if r[0].get("priority") == "high"]
        normal = [r for r in results if r[0].get("priority") != "high"]
        high.sort(key=lambda x: x[0].get("sent", ""), reverse=True)
        normal.sort(key=lambda x: x[0].get("sent", ""), reverse=True)
        return high + normal

    def ack(self, memo_id: str) -> bool:
        """Mark a memo as read. Returns True if memo was found and updated."""
        memo_path = self.memos_dir / f"{memo_id}.md"
        if not memo_path.exists():
            return False

        text = memo_path.read_text(encoding="utf-8")
        meta, body = _parse_memo(text)
        meta["read"] = True
        meta["read_at"] = datetime.now(timezone.utc).isoformat()

        memo_path.write_text(_serialize_memo(meta, body), encoding="utf-8")
        return True

    def ack_all(self, agent: str | None = None) -> int:
        """Mark all unread memos for agent as read. Returns count of acked memos."""
        unread = self.inbox(agent=agent, include_read=False)
        count = 0
        for meta, _body in unread:
            if self.ack(meta["id"]):
                count += 1
        return count

    def gc(self) -> dict:
        """Remove expired and read memos. Returns stats."""
        now = datetime.now(timezone.utc)
        removed_expired = 0
        removed_read = 0

        for memo_file in list(self.memos_dir.glob("*.md")):
            text = memo_file.read_text(encoding="utf-8")
            meta, _body = _parse_memo(text)

            # Remove expired
            expires_str = meta.get("expires")
            if expires_str:
                try:
                    expires_dt = datetime.fromisoformat(expires_str)
                    if expires_dt < now:
                        memo_file.unlink()
                        removed_expired += 1
                        continue
                except (ValueError, TypeError):
                    pass

            # Remove read
            if meta.get("read") is True:
                memo_file.unlink()
                removed_read += 1

        return {
            "removed_expired": removed_expired,
            "removed_read": removed_read,
            "total_removed": removed_expired + removed_read,
        }

    def _all_memos(self) -> list[tuple[dict, str]]:
        """List ALL memos (no filtering). For orchestrator use."""
        results = []
        for memo_file in self.memos_dir.glob("*.md"):
            text = memo_file.read_text(encoding="utf-8")
            meta, body = _parse_memo(text)
            if meta.get("id"):
                results.append((meta, body))
        results.sort(key=lambda x: x[0].get("sent", ""), reverse=True)
        return results
