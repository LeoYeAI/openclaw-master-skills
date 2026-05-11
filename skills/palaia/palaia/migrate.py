"""Migration from external memory formats into Palaia (palaia migrate)."""

from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path

from palaia.entry import content_hash
from palaia.store import Store

# System files that agents read at runtime — must never be deleted after migration.
SYSTEM_FILE_PATTERNS = {
    "CONTEXT.md",
    "SOUL.md",
    "MEMORY.md",
    "AGENTS.md",
    "TOOLS.md",
    "USER.md",
    "IDENTITY.md",
}


def is_system_file(path_str: str) -> bool:
    """Check if a path refers to an agent system file."""
    basename = Path(path_str).name
    return basename in SYSTEM_FILE_PATTERNS


class MigrationEntry:
    """A single entry extracted by an adapter."""

    def __init__(
        self,
        body: str,
        scope: str = "team",
        tier: str = "hot",
        title: str | None = None,
        tags: list[str] | None = None,
        agent: str | None = None,
        source_file: str | None = None,
    ):
        self.body = body
        self.scope = scope
        self.tier = tier
        self.title = title
        self.tags = tags
        self.agent = agent
        self.source_file = source_file

    def __repr__(self) -> str:
        return f"MigrationEntry(title={self.title!r}, scope={self.scope}, tier={self.tier})"


class BaseAdapter(ABC):
    """Base class for migration adapters."""

    name: str = "base"

    @classmethod
    @abstractmethod
    def detect(cls, source: Path) -> bool:
        """Return True if source matches this format."""
        ...

    @classmethod
    @abstractmethod
    def extract(cls, source: Path) -> list[MigrationEntry]:
        """Extract entries from source."""
        ...


class SmartMemoryAdapter(BaseAdapter):
    """Reads OpenClaw smart-memory 5-layer architecture."""

    name = "smart-memory"

    @classmethod
    def detect(cls, source: Path) -> bool:
        if not source.is_dir():
            return False
        has_memory_md = (source / "MEMORY.md").is_file()
        has_active = (source / "memory" / "active-context.md").is_file()
        return has_memory_md and has_active

    @classmethod
    def extract(cls, source: Path) -> list[MigrationEntry]:
        entries: list[MigrationEntry] = []

        # MEMORY.md → 1 entry, scope=team, tier=HOT
        memory_md = source / "MEMORY.md"
        if memory_md.is_file():
            body = memory_md.read_text(encoding="utf-8").strip()
            if body:
                entries.append(
                    MigrationEntry(
                        body=body,
                        scope="team",
                        tier="hot",
                        title="MEMORY.md",
                        source_file="MEMORY.md",
                    )
                )

        # memory/active-context.md → per ## [OPEN] block
        active = source / "memory" / "active-context.md"
        if active.is_file():
            entries.extend(cls._parse_active_context(active))

        # memory/projects/*/CONTEXT.md → 1 entry per file
        projects_dir = source / "memory" / "projects"
        if projects_dir.is_dir():
            for proj_dir in sorted(projects_dir.iterdir()):
                if proj_dir.is_dir():
                    ctx = proj_dir / "CONTEXT.md"
                    if ctx.is_file():
                        body = ctx.read_text(encoding="utf-8").strip()
                        if body:
                            proj_name = proj_dir.name
                            entries.append(
                                MigrationEntry(
                                    body=body,
                                    scope=f"shared:{proj_name}",
                                    tier="hot",
                                    title=f"Project: {proj_name}",
                                    source_file=str(ctx.relative_to(source)),
                                )
                            )

        # memory/agents/*.md → 1 entry per file, scope=team, tier=WARM
        agents_dir = source / "memory" / "agents"
        if agents_dir.is_dir():
            for md in sorted(agents_dir.glob("*.md")):
                body = md.read_text(encoding="utf-8").strip()
                if body:
                    entries.append(
                        MigrationEntry(
                            body=body,
                            scope="team",
                            tier="warm",
                            title=f"Agent: {md.stem}",
                            source_file=str(md.relative_to(source)),
                        )
                    )

        # memory/YYYY-MM-DD.md → 1 entry per file, scope=team, tier=COLD
        memory_dir = source / "memory"
        if memory_dir.is_dir():
            date_re = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
            for md in sorted(memory_dir.glob("*.md")):
                if date_re.match(md.name):
                    body = md.read_text(encoding="utf-8").strip()
                    if body:
                        entries.append(
                            MigrationEntry(
                                body=body,
                                scope="team",
                                tier="cold",
                                title=f"Daily: {md.stem}",
                                source_file=str(md.relative_to(source)),
                            )
                        )

        return entries

    @classmethod
    def _parse_active_context(cls, path: Path) -> list[MigrationEntry]:
        """Split active-context.md by ## [OPEN] blocks."""
        text = path.read_text(encoding="utf-8")
        entries: list[MigrationEntry] = []
        blocks = re.split(r"(?=^## \[OPEN\])", text, flags=re.MULTILINE)
        for block in blocks:
            block = block.strip()
            if not block.startswith("## [OPEN]"):
                continue
            # Extract title from first line
            first_line = block.split("\n", 1)[0]
            title = first_line.replace("## [OPEN]", "").strip()
            entries.append(
                MigrationEntry(
                    body=block,
                    scope="team",
                    tier="hot",
                    title=title or "Active Context",
                    source_file=str(path.name),
                )
            )
        return entries


class FlatFileAdapter(BaseAdapter):
    """Single .md file or file with --- separators."""

    name = "flat-file"

    @classmethod
    def detect(cls, source: Path) -> bool:
        return source.is_file() and source.suffix == ".md"

    @classmethod
    def extract(cls, source: Path) -> list[MigrationEntry]:
        text = source.read_text(encoding="utf-8").strip()
        if not text:
            return []

        # Split by --- separator (only if between content, not frontmatter)
        # Skip frontmatter-style --- at very start
        sections = re.split(r"\n---\n", text)
        entries = []
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            title = None
            # Try to extract first heading as title
            m = re.match(r"^#+ (.+)", section)
            if m:
                title = m.group(1).strip()
            if not title:
                title = f"{source.stem} (part {i + 1})" if len(sections) > 1 else source.stem
            entries.append(
                MigrationEntry(
                    body=section,
                    scope="team",
                    tier="hot",
                    title=title,
                    source_file=source.name,
                )
            )
        return entries


class JsonMemoryAdapter(BaseAdapter):
    """JSON array of memory objects."""

    name = "json-memory"

    @classmethod
    def detect(cls, source: Path) -> bool:
        if source.is_file() and source.suffix == ".json":
            return cls._is_memory_json(source)
        if source.is_dir():
            for f in source.glob("*.json"):
                if cls._is_memory_json(f):
                    return True
        return False

    @classmethod
    def _is_memory_json(cls, path: Path) -> bool:
        try:
            with open(path) as f:
                data = json.load(f)
            return isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "content" in data[0]
        except (json.JSONDecodeError, OSError, IndexError):
            return False

    @classmethod
    def extract(cls, source: Path) -> list[MigrationEntry]:
        files = [source] if source.is_file() else sorted(source.glob("*.json"))
        entries = []
        for f in files:
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    continue
                for item in data:
                    if not isinstance(item, dict) or "content" not in item:
                        continue
                    meta = item.get("metadata", {})
                    entries.append(
                        MigrationEntry(
                            body=item["content"],
                            scope=meta.get("scope", "team"),
                            tier="hot",
                            title=item.get("title") or meta.get("title"),
                            tags=meta.get("tags"),
                            agent=meta.get("agent"),
                            source_file=f.name,
                        )
                    )
            except (json.JSONDecodeError, OSError):
                continue
        return entries


class GenericMarkdownAdapter(BaseAdapter):
    """Fallback: each .md file in directory → 1 entry."""

    name = "generic-md"

    DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

    @classmethod
    def detect(cls, source: Path) -> bool:
        if source.is_dir():
            return any(source.glob("*.md"))
        return source.is_file() and source.suffix == ".md"

    @classmethod
    def extract(cls, source: Path) -> list[MigrationEntry]:
        if source.is_file():
            return cls._extract_file(source)
        entries = []
        for md in sorted(source.rglob("*.md")):
            entries.extend(cls._extract_file(md, base=source))
        return entries

    @classmethod
    def _extract_file(cls, path: Path, base: Path | None = None) -> list[MigrationEntry]:
        body = path.read_text(encoding="utf-8").strip()
        if not body:
            return []
        name_lower = path.stem.lower()
        tier = cls._guess_tier(path, name_lower)
        scope = cls._guess_scope(name_lower)
        title_match = re.match(r"^#+ (.+)", body)
        title = title_match.group(1).strip() if title_match else path.stem
        rel = str(path.relative_to(base)) if base else path.name
        return [MigrationEntry(body=body, scope=scope, tier=tier, title=title, source_file=rel)]

    @classmethod
    def _guess_tier(cls, path: Path, name_lower: str) -> str:
        if cls.DATE_RE.match(name_lower):
            return "cold"
        for kw in ("active", "current", "hot"):
            if kw in name_lower:
                return "hot"
        for kw in ("archive", "old", "cold"):
            if kw in name_lower:
                return "cold"
        # Fall back to mtime
        try:
            mtime = path.stat().st_mtime
            days = (time.time() - mtime) / 86400
            if days < 7:
                return "hot"
            if days < 30:
                return "warm"
            return "cold"
        except OSError:
            return "warm"

    @classmethod
    def _guess_scope(cls, name_lower: str) -> str:
        if "private" in name_lower:
            return "private"
        if "public" in name_lower:
            return "public"
        return "team"


# Adapter registry — order matters (most specific first)
ADAPTERS: list[type[BaseAdapter]] = [
    SmartMemoryAdapter,
    JsonMemoryAdapter,
    FlatFileAdapter,
    GenericMarkdownAdapter,
]


def detect_format(source_path: Path) -> str:
    """Auto-detect source format. Returns adapter name."""
    for adapter_cls in ADAPTERS:
        if adapter_cls.detect(source_path):
            return adapter_cls.name
    return "generic-md"


def get_adapter(name: str) -> type[BaseAdapter]:
    """Get adapter class by name."""
    for adapter_cls in ADAPTERS:
        if adapter_cls.name == name:
            return adapter_cls
    raise ValueError(f"Unknown format: {name}. Available: {[a.name for a in ADAPTERS]}")


def migrate(
    source: str | Path,
    store: Store,
    format_name: str | None = None,
    scope_override: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Run migration.

    Args:
        source: Path to source directory or file.
        store: Target Palaia store.
        format_name: Force a specific format (None = auto-detect).
        scope_override: Override scope for all entries.
        dry_run: If True, report what would be imported.

    Returns:
        dict with migration stats.
    """
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    # Detect or use forced format
    detected = format_name or detect_format(source)
    adapter = get_adapter(detected)

    # Extract
    entries = adapter.extract(source)

    # Apply scope override
    if scope_override:
        for e in entries:
            e.scope = scope_override

    # Count stats
    tier_counts = {"hot": 0, "warm": 0, "cold": 0}
    scope_counts: dict[str, int] = {}
    files_seen: set[str] = set()
    system_files_detected: list[str] = []
    for e in entries:
        tier_counts[e.tier] = tier_counts.get(e.tier, 0) + 1
        scope_counts[e.scope] = scope_counts.get(e.scope, 0) + 1
        if e.source_file:
            files_seen.add(e.source_file)
            if is_system_file(e.source_file) and e.source_file not in system_files_detected:
                system_files_detected.append(e.source_file)

    result = {
        "format": detected,
        "total_entries": len(entries),
        "files_scanned": len(files_seen),
        "tiers": tier_counts,
        "scopes": scope_counts,
        "imported": 0,
        "skipped_dedup": 0,
        "dry_run": dry_run,
        "system_files_detected": system_files_detected,
    }

    if dry_run:
        result["entries"] = [
            {"title": e.title, "scope": e.scope, "tier": e.tier, "source": e.source_file} for e in entries
        ]
        return result

    # Import entries
    imported = 0
    skipped = 0
    for e in entries:
        h = content_hash(e.body)
        existing = store._find_by_hash(h)
        if existing:
            skipped += 1
            continue
        store.write(
            body=e.body,
            scope=e.scope,
            agent=e.agent,
            tags=e.tags,
            title=e.title,
        )
        imported += 1

    result["imported"] = imported
    result["skipped_dedup"] = skipped
    return result


def format_result(result: dict) -> str:
    """Format migration result for CLI output."""
    lines = [f"Detected format: {result['format']}"]
    lines.append(f"Found {result['total_entries']} entries across {result['files_scanned']} files")

    tiers = result["tiers"]
    lines.append(f"  → {tiers.get('hot', 0)} HOT, {tiers.get('warm', 0)} WARM, {tiers.get('cold', 0)} COLD")

    scopes = result["scopes"]
    scope_parts = [f"{k} ({v})" for k, v in sorted(scopes.items(), key=lambda x: -x[1])]
    lines.append(f"  → scope: {', '.join(scope_parts)}")

    if result["dry_run"]:
        lines.append("")
        lines.append("Dry run — nothing written.")
        if result.get("entries"):
            for e in result["entries"]:
                lines.append(f"  {e['tier'].upper():5} [{e['scope']}] {e['title']} ← {e['source']}")
    else:
        lines.append("")
        lines.append(f"Done. {result['imported']} entries imported, {result['skipped_dedup']} duplicates skipped.")

    # Warn about system files that were processed
    system_files = result.get("system_files_detected", [])
    if system_files:
        lines.append("")
        for sf in system_files:
            lines.append(f"Warning: System file detected: {sf}")
            lines.append("    This file is used at runtime by agents. It was copied to Palaia but NOT deleted.")
            lines.append("    Do not remove it manually.")
        lines.append("")
        lines.append("See: https://github.com/iret77/palaia/blob/main/docs/migration-guide.md")

    return "\n".join(lines)
