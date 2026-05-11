"""Knowledge Packages — export/import project knowledge (Issue #73)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from palaia import __version__
from palaia.entry import content_hash
from palaia.store import Store

PACKAGE_FORMAT_VERSION = "1.0"
PACKAGE_EXTENSION = ".palaia-pkg.json"


class PackageManager:
    """Export and import knowledge packages for projects."""

    def __init__(self, store: Store):
        self.store = store

    def export_package(
        self,
        project: str,
        output_path: str | None = None,
        include_types: list[str] | None = None,
    ) -> dict:
        """Export all entries of a project as a knowledge package.

        Args:
            project: Project name to export.
            output_path: Output file path. Defaults to <project>.palaia-pkg.json.
            include_types: Optional list of entry types to include (e.g. ["memory", "process"]).

        Returns:
            Package metadata dict with keys: path, entry_count, project.
        """
        # Collect entries for this project across all tiers
        all_entries = self.store.all_entries(include_cold=True)
        project_entries = [(meta, body, tier) for meta, body, tier in all_entries if meta.get("project") == project]

        # Filter by type if requested
        if include_types:
            project_entries = [
                (meta, body, tier)
                for meta, body, tier in project_entries
                if meta.get("type", "memory") in include_types
            ]

        # Build entries array
        entries = []
        for meta, body, _tier in project_entries:
            entry_data: dict = {"content": body}
            # Copy relevant metadata (including agent for attribution preservation, Issue #85)
            for key in ("type", "tags", "scope", "title", "created", "significance_tags", "agent"):
                if key in meta and meta[key]:
                    entry_data[key] = meta[key]
            # Ensure type is always present
            if "type" not in entry_data:
                entry_data["type"] = "memory"
            entries.append(entry_data)

        # Build package
        package = {
            "palaia_package": PACKAGE_FORMAT_VERSION,
            "palaia_version": __version__,
            "project": project,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
            "entries": entries,
        }

        # Write to file
        if output_path is None:
            output_path = f"{project}{PACKAGE_EXTENSION}"
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "path": str(out),
            "entry_count": len(entries),
            "project": project,
        }

    def import_package(
        self,
        input_path: str,
        target_project: str | None = None,
        merge_strategy: str = "skip",
        agent: str | None = None,
    ) -> dict:
        """Import entries from a knowledge package.

        Args:
            input_path: Path to the .palaia-pkg.json file.
            target_project: Override project name (default: use package's project).
            merge_strategy: "skip" (skip duplicates), "overwrite" (overwrite duplicates),
                          "append" (always create new entries).

        Returns:
            Import stats dict.
        """
        if merge_strategy not in ("skip", "overwrite", "append"):
            raise ValueError(f"Invalid merge strategy: {merge_strategy}. Use: skip, overwrite, append")

        pkg_path = Path(input_path)
        if not pkg_path.exists():
            raise FileNotFoundError(f"Package file not found: {input_path}")

        package = json.loads(pkg_path.read_text(encoding="utf-8"))

        if "palaia_package" not in package:
            raise ValueError(f"Not a valid Palaia package: {input_path}")

        project = target_project or package.get("project", "imported")
        entries = package.get("entries", [])

        # Build a set of existing content hashes for dedup
        existing_hashes: dict[str, str] = {}  # hash -> entry_id
        if merge_strategy in ("skip", "overwrite"):
            all_entries = self.store.all_entries(include_cold=True)
            for meta, body, _tier in all_entries:
                if meta.get("project") == project:
                    h = meta.get("content_hash") or content_hash(body)
                    existing_hashes[h] = meta.get("id", "")

        imported = 0
        skipped = 0
        overwritten = 0

        for entry_data in entries:
            content = entry_data.get("content", "")
            if not content or not content.strip():
                skipped += 1
                continue

            h = content_hash(content)

            if h in existing_hashes:
                if merge_strategy == "skip":
                    skipped += 1
                    continue
                elif merge_strategy == "overwrite":
                    # Delete existing entry, then write new one
                    existing_id = existing_hashes[h]
                    if existing_id:
                        path = self.store._find_entry(existing_id)
                        if path:
                            rel = str(path.relative_to(self.store.root))
                            self.store.delete_raw(rel)
                    overwritten += 1
                # append: fall through to write

            # Write the entry
            tags = entry_data.get("tags")
            entry_type = entry_data.get("type")
            scope = entry_data.get("scope")
            title = entry_data.get("title")
            # Issue #85: preserve original agent from package, fall back to --agent flag
            effective_agent = agent or entry_data.get("agent")

            self.store.write(
                body=content,
                scope=scope,
                tags=tags,
                title=title,
                project=project,
                entry_type=entry_type,
                agent=effective_agent,
            )
            imported += 1

        return {
            "imported": imported,
            "skipped": skipped,
            "overwritten": overwritten,
            "project": project,
            "total_in_package": len(entries),
        }

    def package_info(self, input_path: str) -> dict:
        """Show package metadata without importing.

        Args:
            input_path: Path to the .palaia-pkg.json file.

        Returns:
            Package metadata dict.
        """
        pkg_path = Path(input_path)
        if not pkg_path.exists():
            raise FileNotFoundError(f"Package file not found: {input_path}")

        package = json.loads(pkg_path.read_text(encoding="utf-8"))

        if "palaia_package" not in package:
            raise ValueError(f"Not a valid Palaia package: {input_path}")

        # Type breakdown
        type_counts: dict[str, int] = {}
        for entry in package.get("entries", []):
            t = entry.get("type", "memory")
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "palaia_package": package.get("palaia_package"),
            "palaia_version": package.get("palaia_version"),
            "project": package.get("project"),
            "exported_at": package.get("exported_at"),
            "entry_count": package.get("entry_count", 0),
            "type_breakdown": type_counts,
        }
