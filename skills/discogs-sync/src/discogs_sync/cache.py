"""File-based TTL cache for list results (wantlist, collection, marketplace)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import get_cache_ttl

CACHE_TTL_SECONDS = 86400  # 24 hours (default; overridable via cache_ttl_hours in config)


def get_cache_dir() -> Path:
    """Return the directory where cache files are stored (~/.discogs-sync)."""
    return Path.home() / ".discogs-sync"


def _cache_path(name: str) -> Path:
    return get_cache_dir() / f"{name}_cache.json"


def read_cache(name: str) -> list[dict] | None:
    """Return cached items if present and within TTL, else None.

    Args:
        name: Cache name, e.g. ``"wantlist"`` or ``"collection"``.

    Returns:
        List of raw item dicts, or ``None`` on cache miss / expiry / error.
    """
    path = _cache_path(name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cached_at = datetime.fromisoformat(data["cached_at"])
        now = datetime.now(timezone.utc)
        age = (now - cached_at).total_seconds()
        if age > get_cache_ttl():
            return None
        return data["items"]
    except (KeyError, ValueError, json.JSONDecodeError, OSError):
        return None


def write_cache(name: str, items: list[dict]) -> None:
    """Write items to the cache file with the current UTC timestamp.

    Args:
        name: Cache name, e.g. ``"wantlist"`` or ``"collection"``.
        items: List of raw item dicts (from ``to_dict()``).

    Failures are silently swallowed — a cache write error is non-fatal.
    After a successful write, attempts a best-effort cleanup of expired
    cache files so they do not accumulate indefinitely.
    """
    path = _cache_path(name)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "items": items,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass  # non-fatal
    else:
        try:
            cleanup_expired_caches()
        except Exception:
            pass  # cleanup failure is always non-fatal


def invalidate_cache(name: str) -> None:
    """Delete the cache file for *name*. Silent no-op if file does not exist.

    Args:
        name: Cache name, e.g. ``"wantlist"`` or ``"collection"``.
    """
    path = _cache_path(name)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def cleanup_expired_caches() -> int:
    """Delete all expired or unreadable cache files in the cache directory.

    A file is considered expired when its ``cached_at`` timestamp is older than
    :data:`CACHE_TTL_SECONDS`, or when the file cannot be parsed (corrupt).

    Returns:
        The number of files removed.
    """
    cache_dir = get_cache_dir()
    removed = 0
    try:
        paths = list(cache_dir.glob("*_cache.json"))
    except OSError:
        return 0
    now = datetime.now(timezone.utc)
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(data["cached_at"])
            age = (now - cached_at).total_seconds()
            if age <= get_cache_ttl():
                continue  # still valid — keep it
        except (KeyError, ValueError, json.JSONDecodeError, OSError):
            pass  # treat unreadable/corrupt files as expired
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def purge_all_caches() -> int:
    """Delete every cache file in the cache directory.

    Returns:
        The number of files removed.
    """
    cache_dir = get_cache_dir()
    removed = 0
    try:
        paths = list(cache_dir.glob("*_cache.json"))
    except OSError:
        return 0
    for path in paths:
        try:
            path.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def marketplace_cache_name(
    cache_type: str,
    *key_parts: object,
) -> str:
    """Return a stable cache name for a marketplace search.

    The name is ``marketplace_{cache_type}_{md5}`` where the MD5 is computed
    over the pipe-joined string representation of *key_parts*. This keeps
    filenames safe regardless of artist/album content.

    Args:
        cache_type: One of ``"release"``, ``"master"``, or ``"artist"``.
        *key_parts: Values that together uniquely identify the search
            (IDs, filters, flags, etc.).

    Returns:
        A string suitable for use as the *name* argument to
        :func:`read_cache`, :func:`write_cache`, and
        :func:`invalidate_cache`.
    """
    raw = "|".join(str(p) for p in key_parts)
    digest = hashlib.md5(raw.encode()).hexdigest()[:16]
    return f"marketplace_{cache_type}_{digest}"


def marketplace_resolve_cache_name(
    artist: str,
    album: str,
    threshold: float,
) -> str:
    """Return the cache name for an artist+album → master/release resolution mapping.

    Artist and album are lowercased and stripped before hashing so that
    ``"Steely Dan"`` and ``"steely dan"`` produce the same key.

    Args:
        artist: Artist name.
        album: Album title.
        threshold: Match score threshold (part of the key because different
            thresholds can resolve to different releases).

    Returns:
        A cache name string like ``marketplace_resolve_{md5}``.
    """
    raw = "|".join([
        (artist or "").strip().lower(),
        (album or "").strip().lower(),
        str(threshold),
    ])
    digest = hashlib.md5(raw.encode()).hexdigest()[:16]
    return f"marketplace_resolve_{digest}"


def read_resolve_cache(
    artist: str,
    album: str,
    threshold: float,
) -> dict | None:
    """Read a cached artist+album → master/release resolution.

    Returns:
        ``{"master_id": int|None, "release_id": int|None}`` on cache hit,
        or ``None`` on miss / expiry / error.
    """
    name = marketplace_resolve_cache_name(artist, album, threshold)
    items = read_cache(name)
    if items and len(items) == 1:
        return items[0]
    return None


def write_resolve_cache(
    artist: str,
    album: str,
    threshold: float,
    master_id: int | None,
    release_id: int | None,
) -> None:
    """Cache the resolution of artist+album to master/release IDs."""
    name = marketplace_resolve_cache_name(artist, album, threshold)
    write_cache(name, [{"master_id": master_id, "release_id": release_id}])
