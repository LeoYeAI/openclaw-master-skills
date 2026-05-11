"""Metadata index for fast entry lookup without disk scan (ADR-012).

Caches frontmatter for all entries in a single JSON file.
Lazy-loaded, atomic writes (tmp+rename+fsync — same pattern as EmbeddingCache).
Transparent fallback to disk read if index is missing or corrupt.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TIERS = ("hot", "warm", "cold")

# Fields to cache per entry
INDEXED_FIELDS = (
    "id",
    "title",
    "tags",
    "scope",
    "agent",
    "project",
    "type",
    "status",
    "priority",
    "content_hash",
    "created",
    "accessed",
    "access_count",
    "decay_score",
    "tier",
    "instance",
    "assignee",
    "due_date",
)


class MetadataIndex:
    """File-backed metadata cache for fast entry lookup.

    Stores frontmatter for all entries keyed by entry ID.
    Cache lives at .palaia/index/metadata.json.
    """

    def __init__(self, palaia_root: Path):
        self.palaia_root = palaia_root
        self.index_dir = palaia_root / "index"
        self.index_path = self.index_dir / "metadata.json"
        self._cache: dict[str, dict[str, Any]] | None = None
        self._dirty = False
        self._lock = threading.Lock()

    def _load(self) -> dict[str, dict[str, Any]]:
        """Load index from disk (lazy)."""
        if self._cache is not None:
            return self._cache
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                logger.warning("Metadata index corrupt, will rebuild on next access")
                self._cache = {}
        else:
            self._cache = {}
        return self._cache

    def _save(self) -> None:
        """Persist index to disk (atomic write, thread-safe)."""
        if self._cache is None:
            return
        self.index_dir.mkdir(parents=True, exist_ok=True)
        # Use PID+thread to avoid tmp file collisions
        tid = threading.get_ident()
        tmp = self.index_path.with_suffix(f".{os.getpid()}.{tid}.tmp")
        try:
            with open(tmp, "w") as f:
                json.dump(self._cache, f)
                f.flush()
                os.fsync(f.fileno())
            tmp.rename(self.index_path)
        except OSError:
            # Best-effort cleanup
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
        self._dirty = False

    def _extract_indexed(self, meta: dict, tier: str) -> dict[str, Any]:
        """Extract the subset of fields we cache."""
        entry = {}
        for field in INDEXED_FIELDS:
            if field == "tier":
                entry["tier"] = tier
            elif field in meta:
                entry[field] = meta[field]
        return entry

    def get(self, entry_id: str) -> dict[str, Any] | None:
        """Get cached metadata for an entry."""
        cache = self._load()
        return cache.get(entry_id)

    def update(self, entry_id: str, meta: dict, tier: str) -> None:
        """Update or insert metadata for an entry."""
        with self._lock:
            cache = self._load()
            cache[entry_id] = self._extract_indexed(meta, tier)
            self._dirty = True
            self._save()

    def remove(self, entry_id: str) -> bool:
        """Remove an entry from the index. Returns True if it existed."""
        with self._lock:
            cache = self._load()
            if entry_id in cache:
                del cache[entry_id]
                self._dirty = True
                self._save()
                return True
            return False

    def find_by_hash(self, content_hash: str) -> str | None:
        """Find entry ID by content hash (O(n) over index, not disk)."""
        cache = self._load()
        for entry_id, meta in cache.items():
            if meta.get("content_hash") == content_hash:
                return entry_id
        return None

    def all_entries(self, include_cold: bool = False) -> list[tuple[dict[str, Any], str]]:
        """Get all indexed entries as (meta_dict, tier) tuples.

        This is metadata only — no body content.
        """
        cache = self._load()
        tiers = {"hot", "warm"} | ({"cold"} if include_cold else set())
        results = []
        for _eid, meta in cache.items():
            tier = meta.get("tier", "hot")
            if tier in tiers:
                results.append((meta, tier))
        return results

    def is_populated(self) -> bool:
        """Check if the index has any entries."""
        cache = self._load()
        return len(cache) > 0

    def rebuild(self, parse_entry_fn) -> int:
        """Rebuild index from disk by scanning all tier directories.

        Args:
            parse_entry_fn: Function that parses entry text into (meta, body).

        Returns:
            Number of entries indexed.
        """
        self._cache = {}
        count = 0
        for tier in TIERS:
            tier_dir = self.palaia_root / tier
            if not tier_dir.exists():
                continue
            for p in sorted(tier_dir.glob("*.md")):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, _body = parse_entry_fn(text)
                    entry_id = meta.get("id", p.stem)
                    self._cache[entry_id] = self._extract_indexed(meta, tier)
                    count += 1
                except (OSError, UnicodeDecodeError):
                    continue
        self._dirty = True
        self._save()
        return count

    def cleanup(self, valid_ids: set[str]) -> int:
        """Remove entries not in the valid set. Returns count removed."""
        cache = self._load()
        stale = [eid for eid in cache if eid not in valid_ids]
        for eid in stale:
            del cache[eid]
        if stale:
            self._dirty = True
            self._save()
        return len(stale)

    def stats(self) -> dict:
        """Return index statistics."""
        cache = self._load()
        tiers = {}
        for meta in cache.values():
            tier = meta.get("tier", "hot")
            tiers[tier] = tiers.get(tier, 0) + 1
        return {
            "indexed_entries": len(cache),
            "by_tier": tiers,
        }
