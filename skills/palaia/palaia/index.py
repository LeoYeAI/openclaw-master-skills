"""Embedding cache for Tier 2/3 search (ADR-001).

Cache-only infrastructure. Actual embedding computation is not yet implemented.
# TODO: ollama/API integration for real embeddings.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class EmbeddingCache:
    """File-backed embedding vector cache.

    Stores pre-computed embedding vectors keyed by entry ID.
    Cache lives at .palaia/index/embeddings.json.
    """

    def __init__(self, palaia_root: Path):
        self.index_dir = palaia_root / "index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.index_dir / "embeddings.json"
        self._cache: dict[str, dict[str, Any]] | None = None

    def _load(self) -> dict[str, dict[str, Any]]:
        """Load cache from disk (lazy)."""
        if self._cache is not None:
            return self._cache
        if self.cache_path.exists():
            try:
                with open(self.cache_path) as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._cache = {}
        else:
            self._cache = {}
        return self._cache

    def _save(self) -> None:
        """Persist cache to disk (atomic write)."""
        if self._cache is None:
            return
        tmp = self.cache_path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(self._cache, f)
            f.flush()
            os.fsync(f.fileno())
        tmp.rename(self.cache_path)

    def get_cached(self, entry_id: str) -> list[float] | None:
        """Get cached embedding vector for an entry.

        Returns:
            The embedding vector as a list of floats, or None if not cached.
        """
        cache = self._load()
        entry = cache.get(entry_id)
        if entry is None:
            return None
        return entry.get("vector")

    def set_cached(self, entry_id: str, vector: list[float], model: str = "unknown") -> None:
        """Store an embedding vector in the cache.

        Args:
            entry_id: The memory entry ID.
            vector: The embedding vector.
            model: Name of the model that generated the embedding.
        """
        cache = self._load()
        cache[entry_id] = {
            "vector": vector,
            "model": model,
            "dim": len(vector),
        }
        self._save()

    def invalidate(self, entry_id: str) -> bool:
        """Remove a cached embedding for an entry.

        Returns:
            True if an entry was removed, False if not found.
        """
        cache = self._load()
        if entry_id in cache:
            del cache[entry_id]
            self._save()
            return True
        return False

    def cleanup(self, valid_ids: set[str]) -> int:
        """Remove cache entries for IDs not in the valid set.

        Used by GC to prune embeddings for deleted entries.

        Returns:
            Number of stale cache entries removed.
        """
        cache = self._load()
        stale = [eid for eid in cache if eid not in valid_ids]
        for eid in stale:
            del cache[eid]
        if stale:
            self._save()
        return len(stale)

    def stats(self) -> dict:
        """Return cache statistics."""
        cache = self._load()
        models = set()
        for entry in cache.values():
            models.add(entry.get("model", "unknown"))
        return {
            "cached_entries": len(cache),
            "models": sorted(models) if models else [],
        }
