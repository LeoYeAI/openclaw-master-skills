import json
import os
import datetime


class GidCache:
    """On-disk GID cache."""

    def __init__(self, cache_file: str, ttl: int = None):
        """
        :param cache_file: Path to JSON cache (e.g. ~/.cache/kaipai/gid_cache.json)
        :param ttl: TTL in seconds; None means no expiry
        """
        self.cache_file = os.path.expanduser(cache_file)
        self.ttl = ttl
        self._cache = {}
        self._load()

    def get(self, gid: str):
        """Return cached data for gid, or None if missing or expired."""
        if gid not in self._cache:
            return None

        entry = self._cache[gid]
        created_at = entry.get("created_at", 0)
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()

        if self.ttl is not None and now - created_at > self.ttl:
            self.delete(gid)
            return None

        return entry.get("data")

    def set(self, gid: str, data: dict) -> None:
        """Store data for gid and persist to disk."""
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        self._cache[gid] = {
            "data": data,
            "created_at": now
        }
        self._save()

    def delete(self, gid: str) -> None:
        """Remove one gid from cache."""
        if gid in self._cache:
            del self._cache[gid]
            self._save()

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache = {}
        self._save()

    def _load(self) -> None:
        """Load JSON from disk into memory."""
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            self._cache = {}

    def _save(self) -> None:
        """Persist memory cache to disk."""
        try:
            cache_dir = os.path.dirname(self.cache_file)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def is_valid(self, gid: str) -> bool:
        """True if gid exists and is not expired (always True when ttl is None)."""
        if gid not in self._cache:
            return False

        if self.ttl is None:
            return True

        entry = self._cache[gid]
        created_at = entry.get("created_at", 0)
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()

        return now - created_at <= self.ttl
