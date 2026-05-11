"""Embedding server — long-lived subprocess for fast semantic search.

Loads the embedding model once and serves queries over stdin/stdout JSON-RPC.
Eliminates the ~3-23s model loading penalty on every CLI invocation.

Usage:
    palaia embed-server

Protocol: One JSON object per line on stdin/stdout.
Requests:
    {"method": "query", "params": {"text": "...", "top_k": 10, "agent": "...", "project": "...", "scope": "..."}}
    {"method": "warmup"}
    {"method": "ping"}
    {"method": "status"}
    {"method": "shutdown"}
"""

from __future__ import annotations

import json
import sys
import threading
import time
import traceback
from pathlib import Path

from palaia.config import get_root
from palaia.embeddings import BM25Provider
from palaia.search import SearchEngine
from palaia.store import Store


def _count_entries(store: Store) -> int:
    """Count total entries across hot+warm tiers (fast, no parsing)."""
    count = 0
    for tier in ("hot", "warm"):
        tier_dir = store.root / tier
        if tier_dir.exists():
            count += sum(1 for _ in tier_dir.glob("*.md"))
    return count


def _warmup_missing(store: Store, engine: SearchEngine) -> dict:
    """Index any entries missing from the embedding cache. Returns stats."""
    provider = engine.provider
    if isinstance(provider, BM25Provider):
        return {"indexed": 0, "new": 0, "cached": 0}

    entries = store.all_entries_unfiltered(include_cold=False)
    total = len(entries)
    if total == 0:
        return {"indexed": 0, "new": 0, "cached": 0}

    uncached = []
    cached_count = 0
    for meta, body, _tier in entries:
        entry_id = meta.get("id", "")
        if not entry_id:
            continue
        if store.embedding_cache.get_cached(entry_id) is not None:
            cached_count += 1
        else:
            title = meta.get("title", "")
            tags = " ".join(meta.get("tags", []))
            full_text = f"{title} {tags} {body}"
            uncached.append((entry_id, full_text))

    if not uncached:
        return {"indexed": total, "new": 0, "cached": cached_count}

    model_name = getattr(provider, "model_name", None) or getattr(provider, "model", "unknown")
    new_count = 0
    batch_size = 32

    for i in range(0, len(uncached), batch_size):
        batch = uncached[i : i + batch_size]
        texts = [text for _, text in batch]
        ids = [eid for eid, _ in batch]
        try:
            vectors = provider.embed(texts)
            for eid, vec in zip(ids, vectors):
                store.embedding_cache.set_cached(eid, vec, model=model_name)
                new_count += 1
        except Exception:
            break

    return {"indexed": cached_count + new_count, "new": new_count, "cached": cached_count}


class EmbedServer:
    """JSON-RPC server over stdin/stdout for embedding queries."""

    def __init__(self, root: Path):
        self.root = root
        self.store = Store(root)
        self.engine = SearchEngine(self.store)
        # BM25-only fallback engine for queries during warmup (no GIL contention)
        self._bm25_engine = SearchEngine(self.store)
        self._bm25_engine._provider = BM25Provider()
        self._last_entry_count = _count_entries(self.store)
        self._running = True
        self._warming_up = False
        self._stale_check_thread: threading.Thread | None = None

    def _start_stale_detection(self) -> None:
        """Start background thread that checks for entry count changes every 30s."""

        def _check_loop():
            while self._running:
                time.sleep(30)
                if not self._running:
                    break
                try:
                    current = _count_entries(self.store)
                    if current != self._last_entry_count:
                        self._last_entry_count = current
                        # Force BM25 index rebuild on next query by resetting the engine
                        self.engine = SearchEngine(self.store)
                        # Reload embedding cache from disk
                        self.store.embedding_cache._cache = None
                except Exception:
                    pass

        self._stale_check_thread = threading.Thread(target=_check_loop, daemon=True)
        self._stale_check_thread.start()

    def handle_request(self, request: dict) -> dict:
        """Dispatch a single JSON-RPC request. Always returns a dict."""
        method = request.get("method", "")

        if method == "ping":
            return {"result": "pong"}

        if method == "shutdown":
            self._running = False
            return {"result": "shutting_down"}

        if method == "status":
            return self._handle_status()

        if method == "warmup":
            return self._handle_warmup()

        if method == "query":
            return self._handle_query(request.get("params", {}))

        return {"error": f"Unknown method: {method}"}

    def _handle_status(self) -> dict:
        """Return entry count, cache coverage, and provider info."""
        entries = _count_entries(self.store)
        cache_stats = self.store.embedding_cache.stats()
        provider = self.engine.provider
        provider_name = getattr(provider, "name", "unknown")
        model = getattr(provider, "model_name", None) or getattr(provider, "model", None) or ""
        return {
            "result": {
                "entries": entries,
                "cached": cache_stats.get("cached_entries", 0),
                "provider": provider_name,
                "model": model,
                "has_embeddings": self.engine.has_embeddings,
                "warming_up": self._warming_up,
            }
        }

    def _handle_warmup(self) -> dict:
        """Index all missing entries."""
        stats = _warmup_missing(self.store, self.engine)
        return {"result": stats}

    def _handle_query(self, params: dict) -> dict:
        """Execute a search query using the existing SearchEngine."""
        text = params.get("text", "")
        if not text:
            return {"error": "Missing 'text' parameter"}

        top_k = params.get("top_k", 10)
        agent = params.get("agent")
        project = params.get("project")
        _scope = params.get("scope")  # reserved for future scope filtering
        entry_type = params.get("type")
        status = params.get("status")
        priority = params.get("priority")
        assignee = params.get("assignee")
        instance = params.get("instance")
        include_cold = params.get("include_cold", False)
        cross_project = params.get("cross_project", False)

        engine = self._bm25_engine if self._warming_up else self.engine
        results = engine.search(
            text,
            top_k=top_k,
            include_cold=include_cold,
            project=project,
            agent=agent,
            entry_type=entry_type,
            status=status,
            priority=priority,
            assignee=assignee,
            instance=instance,
            cross_project=cross_project,
        )

        return {"result": {"results": results}}

    def run(self) -> None:
        """Main loop: read JSON lines from stdin, write JSON responses to stdout."""
        # Start stale detection
        self._start_stale_detection()

        # Signal ready IMMEDIATELY — warmup runs in background
        # Queries arriving during warmup use BM25 fallback automatically
        self._warming_up = True
        self._write_response({"result": "ready"})

        # Background warmup thread
        def _bg_warmup():
            try:
                _warmup_missing(self.store, self.engine)
            except Exception:
                pass
            finally:
                self._warming_up = False

        warmup_thread = threading.Thread(target=_bg_warmup, daemon=True)
        warmup_thread.start()

        while self._running:
            try:
                line = sys.stdin.readline()
                if not line:
                    # EOF — parent process closed stdin
                    break
                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    self._write_response({"error": f"Invalid JSON: {e}"})
                    continue

                response = self.handle_request(request)
                self._write_response(response)

            except Exception as e:
                try:
                    self._write_response({"error": f"Internal error: {e}", "traceback": traceback.format_exc()})
                except Exception:
                    break

    def _write_response(self, response: dict) -> None:
        """Write a JSON response line to stdout."""
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def main() -> None:
    """Entry point for `palaia embed-server`."""
    root = get_root()
    server = EmbedServer(root)
    server.run()


if __name__ == "__main__":
    main()
