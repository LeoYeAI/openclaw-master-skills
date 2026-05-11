"""Memory store with tier routing (ADR-004)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from palaia.config import get_aliases, load_config, resolve_agent_with_aliases
from palaia.decay import classify_tier, days_since, decay_score
from palaia.entry import (
    content_hash,
    create_entry,
    extract_title_from_content,
    parse_entry,
    serialize_entry,
    update_access,
    validate_entry_type,
    validate_priority,
    validate_status,
)
from palaia.index import EmbeddingCache
from palaia.lock import PalaiaLock
from palaia.metadata_index import MetadataIndex
from palaia.scope import can_access, normalize_scope
from palaia.wal import WAL, WALEntry

TIERS = ("hot", "warm", "cold")


class Store:
    """Memory store with WAL, locking, and tier management."""

    def __init__(self, palaia_root: Path):
        self.root = palaia_root
        self.config = load_config(palaia_root)
        self.wal = WAL(palaia_root)
        self.lock = PalaiaLock(palaia_root, self.config["lock_timeout_seconds"])
        self.embedding_cache = EmbeddingCache(palaia_root)
        self.metadata_index = MetadataIndex(palaia_root)
        self._aliases = get_aliases(palaia_root)

        # Ensure tier directories
        for tier in TIERS:
            (self.root / tier).mkdir(parents=True, exist_ok=True)

    def _resolve_names(self, agent: str | None) -> set[str] | None:
        """Resolve agent to all matching names via aliases."""
        if agent is None:
            return None
        if self._aliases:
            return resolve_agent_with_aliases(agent, self._aliases)
        return {agent}

    def recover(self) -> int:
        """Run WAL recovery on startup."""
        return self.wal.recover(self)

    def write(
        self,
        body: str,
        scope: str | None = None,
        agent: str | None = None,
        tags: list[str] | None = None,
        title: str | None = None,
        project: str | None = None,
        entry_type: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        due_date: str | None = None,
        instance: str | None = None,
    ) -> str:
        """Write a new memory entry. Returns the entry ID.

        Scope cascade:
        1. Explicit --scope argument wins always
        2. Project default_scope if entry is in a project
        3. Global default_scope from config
        4. Hardcoded fallback: 'team'
        """
        if not body or not body.strip():
            raise ValueError("Cannot write empty content. Provide a non-empty text body.")

        # Scope cascade
        if scope is not None:
            # Explicit scope always wins
            scope = normalize_scope(scope)
        elif project:
            # Auto-create project if it doesn't exist, then use its default scope
            from palaia.project import ProjectManager

            pm = ProjectManager(self.root)
            proj = pm.ensure(project, default_scope=self.config["default_scope"])
            scope = normalize_scope(proj.default_scope)
        else:
            scope = normalize_scope(None, self.config["default_scope"])

        # Dedup check
        h = content_hash(body)
        existing = self._find_by_hash(h)
        if existing:
            return existing  # Already stored, return existing ID

        entry_text = create_entry(
            body,
            scope,
            agent,
            tags,
            title,
            project,
            entry_type=entry_type,
            status=status,
            priority=priority,
            assignee=assignee,
            due_date=due_date,
            instance=instance,
        )
        meta, _ = parse_entry(entry_text)
        entry_id = meta["id"]
        filename = f"{entry_id}.md"
        target = f"hot/{filename}"

        with self.lock:
            # WAL: log intent with payload for recovery
            wal_entry = WALEntry(
                operation="write",
                target=target,
                payload_hash=h,
                payload=entry_text,
            )
            self.wal.log(wal_entry)

            # Write the actual file
            self.write_raw(target, entry_text)

            # Commit WAL
            self.wal.commit(wal_entry)

        # Invalidate any stale embedding cache for this entry
        self.embedding_cache.invalidate(entry_id)

        # Update metadata index
        self.metadata_index.update(entry_id, meta, "hot")

        # Incremental embedding indexing: compute embedding for the new entry
        # Fire-and-forget — write must not fail because of embedding errors
        try:
            self._index_single_entry(entry_id, meta, body)
        except Exception:
            pass

        return entry_id

    def _index_single_entry(self, entry_id: str, meta: dict, body: str) -> bool:
        """Compute and cache embedding for a single entry.

        Returns True if embedding was computed, False if skipped/failed.
        Only indexes when a semantic embedding provider is available (not BM25-only).
        """
        from palaia.embeddings import BM25Provider, build_embedding_chain

        chain = build_embedding_chain(self.config)
        # Skip if no semantic providers available (BM25-only)
        if not chain.providers:
            return False

        provider = chain.providers[0]
        if isinstance(provider, BM25Provider):
            return False

        title = meta.get("title", "")
        tags = " ".join(meta.get("tags", []))
        full_text = f"{title} {tags} {body}"

        vectors, provider_name = chain.embed([full_text])
        if vectors and provider_name != "bm25":
            model_name = getattr(provider, "model_name", None) or getattr(provider, "model", provider_name)
            self.embedding_cache.set_cached(entry_id, vectors[0], model=model_name)
            return True
        return False

    def edit(
        self,
        entry_id: str,
        body: str | None = None,
        agent: str | None = None,
        tags: list[str] | None = None,
        title: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        due_date: str | None = None,
        entry_type: str | None = None,
    ) -> dict:
        """Edit an existing entry. Returns updated metadata.

        Enforces scope: agent in narrower scope cannot edit broader-scope entries.
        WAL-backed for crash safety.
        """
        path = self._find_entry(entry_id)
        if path is None:
            raise ValueError(f"Entry not found: {entry_id}")

        text = path.read_text(encoding="utf-8")
        meta, old_body = parse_entry(text)

        # Scope enforcement: agent must be able to access the entry
        entry_scope = meta.get("scope", "team")
        entry_agent = meta.get("agent")

        resolved = self._resolve_names(agent)
        if not can_access(entry_scope, agent, entry_agent, agent_names=resolved):
            raise PermissionError(
                f"Scope violation: agent '{agent}' cannot edit entry with scope '{entry_scope}' "
                f"(owned by '{entry_agent}')"
            )

        # Private entries: only the owning agent (or alias) can edit
        if entry_scope == "private" and agent != entry_agent:
            if not (resolved and entry_agent in resolved):
                raise PermissionError(
                    f"Scope violation: agent '{agent}' cannot edit private entry owned by '{entry_agent}'"
                )

        # Apply changes
        content_changed = False

        if body is not None:
            old_body = body
            meta["content_hash"] = content_hash(body)
            content_changed = True

        if tags is not None:
            meta["tags"] = tags

        if title is not None:
            meta["title"] = title
        elif content_changed:
            # Auto-update title from new content if no explicit title was set
            auto_title = extract_title_from_content(body)
            if auto_title:
                meta["title"] = auto_title

        if entry_type is not None:
            meta["type"] = validate_entry_type(entry_type)

        # Task-specific field updates
        if status is not None:
            validate_status(status)
            meta["status"] = status

        if priority is not None:
            validate_priority(priority)
            meta["priority"] = priority

        if assignee is not None:
            meta["assignee"] = assignee

        if due_date is not None:
            meta["due_date"] = due_date

        # Update access metadata
        meta["accessed"] = datetime.now(timezone.utc).isoformat()

        new_text = serialize_entry(meta, old_body)
        relative = str(path.relative_to(self.root))

        with self.lock:
            wal_entry = WALEntry(
                operation="write",
                target=relative,
                payload_hash=meta.get("content_hash", ""),
                payload=new_text,
            )
            self.wal.log(wal_entry)
            self.write_raw(relative, new_text)
            self.wal.commit(wal_entry)

        # Re-index embeddings if content changed
        if content_changed:
            self.embedding_cache.invalidate(entry_id)
            # Recompute embedding for updated content (fire-and-forget)
            try:
                self._index_single_entry(entry_id, meta, old_body)
            except Exception:
                pass

        # Update metadata index (determine tier from path)
        tier = path.parent.name
        self.metadata_index.update(entry_id, meta, tier)

        return meta

    def write_raw(self, target: str, content: str) -> None:
        """Write content to a target path (relative to palaia root). Used by WAL recovery."""
        path = self.root / target
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        tmp.rename(path)

    def delete_raw(self, target: str) -> None:
        """Delete a target path (relative to palaia root)."""
        path = self.root / target
        if path.exists():
            path.unlink()

    def read(
        self, entry_id: str, agent: str | None = None, projects: list[str] | None = None
    ) -> tuple[dict, str] | None:
        """Read a memory entry by ID. Updates access metadata."""
        path = self._find_entry(entry_id)
        if path is None:
            return None

        text = path.read_text(encoding="utf-8")
        meta, body = parse_entry(text)

        # Scope check
        resolved = self._resolve_names(agent)
        if not can_access(meta.get("scope", "team"), agent, meta.get("agent"), projects, resolved):
            return None

        # Update access
        meta = update_access(meta)
        new_text = serialize_entry(meta, body)

        with self.lock:
            self.write_raw(str(path.relative_to(self.root)), new_text)

        return meta, body

    def list_entries(
        self, tier: str = "hot", agent: str | None = None, projects: list[str] | None = None
    ) -> list[tuple[dict, str]]:
        """List all entries in a tier."""
        tier_dir = self.root / tier
        if not tier_dir.exists():
            return []

        resolved = self._resolve_names(agent)
        results = []
        for p in sorted(tier_dir.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8")
                meta, body = parse_entry(text)
                if can_access(meta.get("scope", "team"), agent, meta.get("agent"), projects, resolved):
                    results.append((meta, body))
            except (OSError, UnicodeDecodeError):
                continue
        return results

    def all_entries(
        self, include_cold: bool = False, agent: str | None = None, projects: list[str] | None = None
    ) -> list[tuple[dict, str, str]]:
        """Get all entries across tiers. Returns (meta, body, tier)."""
        tiers = ["hot", "warm"] + (["cold"] if include_cold else [])
        results = []
        for tier in tiers:
            for meta, body in self.list_entries(tier, agent, projects):
                results.append((meta, body, tier))
        return results

    def all_entries_unfiltered(self, include_cold: bool = False) -> list[tuple[dict, str, str]]:
        """Get ALL entries across tiers WITHOUT scope filtering.

        Used for indexing/warmup where every entry needs an embedding
        regardless of scope. Scope filtering happens at query time, not
        at index time.

        Returns list of (meta, body, tier).
        """
        tiers = ["hot", "warm"] + (["cold"] if include_cold else [])
        results = []
        for tier in tiers:
            tier_dir = self.root / tier
            if not tier_dir.exists():
                continue
            for p in sorted(tier_dir.glob("*.md")):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, body = parse_entry(text)
                    results.append((meta, body, tier))
                except (OSError, UnicodeDecodeError):
                    continue
        return results

    def gc_score_entry(self, meta: dict, body: str, config: dict | None = None) -> float:
        """Calculate the holistic GC score for an entry.

        Formula (Issue #33, #70, #71):
            gc_score = decay_score * hit_rate_bonus * significance_weight * type_weight

        Higher gc_score = more important = survives GC longer.
        Lowest gc_score = first pruning candidate.
        """
        from palaia.significance import significance_weight as sig_weight

        if config is None:
            config = self.config

        accessed = meta.get("accessed", meta.get("created", ""))
        if not accessed:
            return 0.0

        d = days_since(accessed)
        ac = meta.get("access_count", 1)
        base_score = decay_score(d, ac, config["decay_lambda"])

        # Significance weight from tags
        tags = meta.get("tags", [])
        sw = sig_weight(tags)

        # Type weight
        type_weights = config.get("gc_type_weights", {"process": 2.0, "task": 1.5, "memory": 1.0})
        if isinstance(type_weights, dict):
            entry_type = meta.get("type", "memory")
            tw = type_weights.get(entry_type, 1.0)
        else:
            tw = 1.0

        return round(base_score * sw * tw, 6)

    def gc(self, dry_run: bool = False, budget: bool = False) -> dict:
        """Garbage collect: rotate tiers based on decay scores.

        Args:
            dry_run: If True, report what would happen without changing anything.
            budget: If True, prune entries to meet configured budget limits.
        """
        moves = {"hot_to_warm": 0, "warm_to_cold": 0, "cold_to_warm": 0, "warm_to_hot": 0}
        config = self.config
        pruned_entries: list[dict] = []  # For dry-run and budget reporting

        if dry_run:
            # Collect all entries with scores for dry-run report
            candidates = []
            for tier in TIERS:
                tier_dir = self.root / tier
                if not tier_dir.exists():
                    continue
                for p in tier_dir.glob("*.md"):
                    try:
                        text = p.read_text(encoding="utf-8")
                        meta, body = parse_entry(text)
                    except (OSError, UnicodeDecodeError):
                        continue
                    gc_s = self.gc_score_entry(meta, body, config)
                    reason_parts = []
                    if gc_s < 0.1:
                        reason_parts.append("low decay")
                    if meta.get("access_count", 1) <= 1:
                        reason_parts.append("no hits")
                    from palaia.significance import SIGNIFICANCE_TAGS

                    tags = meta.get("tags", [])
                    if not any(t in SIGNIFICANCE_TAGS for t in tags):
                        reason_parts.append("no significance")
                    candidates.append(
                        {
                            "id": meta.get("id", p.stem)[:8],
                            "title": meta.get("title", "(untitled)"),
                            "score": gc_s,
                            "tier": tier,
                            "reason": ", ".join(reason_parts) if reason_parts else "ok",
                        }
                    )
            candidates.sort(key=lambda x: x["score"])
            return {"dry_run": True, "candidates": candidates}

        with self.lock:
            for tier in TIERS:
                tier_dir = self.root / tier
                if not tier_dir.exists():
                    continue
                for p in tier_dir.glob("*.md"):
                    try:
                        text = p.read_text(encoding="utf-8")
                        meta, body = parse_entry(text)
                    except (OSError, UnicodeDecodeError):
                        continue

                    accessed = meta.get("accessed", meta.get("created", ""))
                    if not accessed:
                        continue

                    d = days_since(accessed)
                    ac = meta.get("access_count", 1)
                    score = decay_score(d, ac, config["decay_lambda"])
                    meta["decay_score"] = score

                    # Store holistic GC score as well
                    gc_s = self.gc_score_entry(meta, body, config)
                    meta["gc_score"] = gc_s

                    new_tier = classify_tier(
                        d,
                        score,
                        config["hot_threshold_days"],
                        config["warm_threshold_days"],
                        config["hot_min_score"],
                        config["warm_min_score"],
                    )

                    # Update the score in file
                    new_text = serialize_entry(meta, body)

                    if new_tier != tier:
                        new_target = f"{new_tier}/{p.name}"
                        # WAL: log the move with payload for crash recovery
                        wal_entry = WALEntry(
                            operation="write",
                            target=new_target,
                            payload_hash=meta.get("content_hash", ""),
                            payload=new_text,
                        )
                        self.wal.log(wal_entry)
                        self.write_raw(new_target, new_text)
                        p.unlink()
                        self.wal.commit(wal_entry)
                        # Update metadata index with new tier
                        entry_id = meta.get("id", p.stem)
                        self.metadata_index.update(entry_id, meta, new_tier)
                        key = f"{tier}_to_{new_tier}"
                        moves[key] = moves.get(key, 0) + 1
                    else:
                        with open(p, "w") as f:
                            f.write(new_text)
                        # Update metadata index (score may have changed)
                        entry_id = meta.get("id", p.stem)
                        self.metadata_index.update(entry_id, meta, tier)

            # Budget enforcement (Issue #71)
            if budget:
                pruned_entries = self._enforce_budget(config)

        # WAL cleanup
        wal_cleaned = self.wal.cleanup(config["wal_retention_days"])
        moves["wal_cleaned"] = wal_cleaned

        # Embedding cache cleanup: remove entries for deleted IDs
        valid_ids = set()
        for tier in TIERS:
            tier_dir = self.root / tier
            if tier_dir.exists():
                for p in tier_dir.glob("*.md"):
                    valid_ids.add(p.stem)
        stale = self.embedding_cache.cleanup(valid_ids)
        if stale:
            moves["embeddings_cleaned"] = stale

        # Metadata index cleanup
        meta_stale = self.metadata_index.cleanup(valid_ids)
        if meta_stale:
            moves["metadata_cleaned"] = meta_stale

        if pruned_entries:
            moves["pruned"] = len(pruned_entries)
            moves["pruned_entries"] = pruned_entries

        return moves

    def _enforce_budget(self, config: dict) -> list[dict]:
        """Prune entries to meet budget limits. Returns list of pruned entry info.

        Must be called inside a lock context.
        """
        max_per_tier = config.get("max_entries_per_tier")
        max_chars = config.get("max_total_chars")

        if max_per_tier is None and max_chars is None:
            return []

        pruned: list[dict] = []

        # Collect all entries with GC scores
        all_entries: list[tuple[Path, dict, str, float]] = []
        for tier in TIERS:
            tier_dir = self.root / tier
            if not tier_dir.exists():
                continue
            for p in tier_dir.glob("*.md"):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, body = parse_entry(text)
                except (OSError, UnicodeDecodeError):
                    continue
                gc_s = self.gc_score_entry(meta, body, config)
                all_entries.append((p, meta, body, gc_s))

        # Sort by gc_score ascending (lowest first = prune first)
        all_entries.sort(key=lambda x: x[3])

        # Enforce max_entries_per_tier
        if max_per_tier is not None:
            for tier in TIERS:
                tier_entries = [(p, m, b, s) for p, m, b, s in all_entries if str(p).startswith(str(self.root / tier))]
                if len(tier_entries) > max_per_tier:
                    # Already sorted by gc_score asc, prune from the front
                    to_prune = tier_entries[: len(tier_entries) - max_per_tier]
                    for p, meta, _body, gc_s in to_prune:
                        pruned.append(
                            {
                                "id": meta.get("id", p.stem)[:8],
                                "title": meta.get("title", "(untitled)"),
                                "score": gc_s,
                                "reason": "budget:max_entries_per_tier",
                            }
                        )
                        rel = str(p.relative_to(self.root))
                        self.delete_raw(rel)
                        entry_id = meta.get("id", p.stem)
                        self.embedding_cache.invalidate(entry_id)
                        self.metadata_index.remove(entry_id)
                        all_entries = [(ep, em, eb, es) for ep, em, eb, es in all_entries if ep != p]

        # Enforce max_total_chars
        if max_chars is not None:
            total_chars = sum(len(b) for _, _, b, _ in all_entries)
            while total_chars > max_chars and all_entries:
                p, meta, body, gc_s = all_entries[0]
                pruned.append(
                    {
                        "id": meta.get("id", p.stem)[:8],
                        "title": meta.get("title", "(untitled)"),
                        "score": gc_s,
                        "reason": "budget:max_total_chars",
                    }
                )
                rel = str(p.relative_to(self.root))
                self.delete_raw(rel)
                entry_id = meta.get("id", p.stem)
                self.embedding_cache.invalidate(entry_id)
                self.metadata_index.remove(entry_id)
                total_chars -= len(body)
                all_entries = all_entries[1:]

        return pruned

    def status(self) -> dict:
        """Get system status info."""
        counts = {}
        total_chars = 0
        for tier in TIERS:
            tier_dir = self.root / tier
            if tier_dir.exists():
                entries = list(tier_dir.glob("*.md"))
                counts[tier] = len(entries)
                for p in entries:
                    try:
                        text = p.read_text(encoding="utf-8")
                        _, body = parse_entry(text)
                        total_chars += len(body)
                    except (OSError, UnicodeDecodeError):
                        pass
            else:
                counts[tier] = 0

        wal_dir = self.root / "wal"
        pending = len(self.wal.get_pending()) if wal_dir.exists() else 0

        result = {
            "palaia_root": str(self.root),
            "entries": counts,
            "total": sum(counts.values()),
            "total_chars": total_chars,
            "wal_pending": pending,
            "config": self.config,
        }

        # Budget info (Issue #71)
        max_per_tier = self.config.get("max_entries_per_tier")
        max_total_chars = self.config.get("max_total_chars")
        if max_per_tier is not None or max_total_chars is not None:
            budget = {}
            if max_per_tier is not None:
                budget["max_entries_per_tier"] = max_per_tier
                budget["tier_usage"] = {t: f"{counts.get(t, 0)}/{max_per_tier}" for t in TIERS}
            if max_total_chars is not None:
                budget["max_total_chars"] = max_total_chars
                budget["chars_usage"] = f"{total_chars}/{max_total_chars}"
            result["budget"] = budget

        return result

    def _find_entry(self, entry_id: str) -> Path | None:
        """Find an entry file across tiers."""
        filename = f"{entry_id}.md"
        for tier in TIERS:
            path = self.root / tier / filename
            if path.exists():
                return path
        return None

    def _find_by_hash(self, h: str) -> str | None:
        """Find entry ID by content hash (dedup).

        Uses metadata index for O(n-in-memory) lookup instead of O(n) disk scan.
        Falls back to disk scan if index is empty (cold start).
        """
        # Try index first
        if self.metadata_index.is_populated():
            result = self.metadata_index.find_by_hash(h)
            if result is not None:
                return result
            return None

        # Fallback: disk scan (index not yet built)
        for tier in TIERS:
            tier_dir = self.root / tier
            if not tier_dir.exists():
                continue
            for p in tier_dir.glob("*.md"):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, _ = parse_entry(text)
                    if meta.get("content_hash") == h:
                        return meta.get("id")
                except (OSError, UnicodeDecodeError):
                    continue
        return None
