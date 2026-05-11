"""Export/Import for cross-team knowledge transfer (ADR-005)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from palaia import __version__
from palaia.config import get_root
from palaia.entry import content_hash, parse_entry, serialize_entry
from palaia.scope import is_exportable
from palaia.store import Store

MANIFEST_NAME = "palaia-export.json"


def _build_manifest(entries: list[tuple[dict, str]], workspace_id: str | None = None) -> dict:
    """Build an export manifest."""
    return {
        "palaia_version": __version__,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "workspace": workspace_id or "unknown",
        "entry_count": len(entries),
        "content_hashes": [m.get("content_hash", "") for m, _ in entries],
    }


def export_entries(
    remote: str | None = None,
    branch: str | None = None,
    output_dir: str | None = None,
    agent: str | None = None,
) -> dict:
    """Export public entries.

    Args:
        remote: Git remote URL. If set, pushes to a new branch.
        branch: Branch name override (default: palaia/export/<timestamp>).
        output_dir: Local output directory (default: ./palaia-export/).

    Returns:
        dict with export stats.
    """
    root = get_root()
    store = Store(root)
    store.recover()

    # Collect public entries from all tiers
    all_entries = store.all_entries(include_cold=True, agent=agent)
    public_entries = []
    for meta, body, tier in all_entries:
        if is_exportable(meta.get("scope", "team")):
            public_entries.append((meta, body))

    if not public_entries:
        return {"exported": 0, "message": "No public entries to export."}

    # Determine workspace ID from config
    config = store.config
    workspace_id = config.get("workspace_id", str(root))

    # Build manifest
    manifest = _build_manifest(public_entries, workspace_id)

    if remote:
        return _export_to_git(public_entries, manifest, remote, branch)
    else:
        return _export_to_dir(public_entries, manifest, output_dir)


def _export_to_dir(
    entries: list[tuple[dict, str]],
    manifest: dict,
    output_dir: str | None,
) -> dict:
    """Export entries to a local directory."""
    out = Path(output_dir or "./palaia-export")
    out.mkdir(parents=True, exist_ok=True)

    # Write entries
    entries_dir = out / "entries"
    entries_dir.mkdir(exist_ok=True)
    for meta, body in entries:
        entry_id = meta.get("id", "unknown")
        path = entries_dir / f"{entry_id}.md"
        path.write_text(serialize_entry(meta, body), encoding="utf-8")

    # Write manifest
    manifest_path = out / MANIFEST_NAME
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return {
        "exported": len(entries),
        "target": str(out),
        "manifest": str(manifest_path),
    }


def _export_to_git(
    entries: list[tuple[dict, str]],
    manifest: dict,
    remote: str,
    branch: str | None,
) -> dict:
    """Export entries to a git remote branch."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    branch_name = branch or f"palaia/export/{timestamp}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Init repo and add remote
        subprocess.run(["git", "init"], cwd=tmp, capture_output=True, check=True)
        subprocess.run(
            ["git", "remote", "add", "origin", remote],
            cwd=tmp,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=tmp,
            capture_output=True,
            check=True,
        )

        # Write entries
        entries_dir = tmp / "entries"
        entries_dir.mkdir()
        for meta, body in entries:
            entry_id = meta.get("id", "unknown")
            path = entries_dir / f"{entry_id}.md"
            path.write_text(serialize_entry(meta, body), encoding="utf-8")

        # Write manifest
        manifest_path = tmp / MANIFEST_NAME
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Commit and push
        subprocess.run(["git", "add", "."], cwd=tmp, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"palaia export {timestamp}"],
            cwd=tmp,
            capture_output=True,
            check=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "palaia", "GIT_AUTHOR_EMAIL": "palaia@local"},
        )
        result = subprocess.run(
            ["git", "push", "origin", branch_name],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git push failed: {result.stderr}")

    return {
        "exported": len(entries),
        "remote": remote,
        "branch": branch_name,
    }


def import_entries(
    source: str,
    dry_run: bool = False,
) -> dict:
    """Import entries from an export directory or git URL.

    Args:
        source: Path to export directory or git URL.
        dry_run: If True, report what would be imported without writing.

    Returns:
        dict with import stats.
    """
    root = get_root()
    store = Store(root)
    store.recover()

    # Determine source type
    source_path = Path(source)
    if source_path.is_dir():
        return _import_from_dir(store, source_path, dry_run)
    elif source.startswith(("http://", "https://", "git@", "ssh://")):
        return _import_from_git(store, source, dry_run)
    elif source_path.is_dir():
        return _import_from_dir(store, source_path, dry_run)
    else:
        raise ValueError(f"Cannot determine source type: {source}")


def _read_export_dir(export_dir: Path) -> tuple[dict, list[tuple[dict, str]]]:
    """Read manifest and entries from an export directory."""
    manifest_path = export_dir / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest found at {manifest_path}")

    with open(manifest_path) as f:
        manifest = json.load(f)

    entries_dir = export_dir / "entries"
    if not entries_dir.is_dir():
        raise FileNotFoundError(f"No entries directory at {entries_dir}")

    entries = []
    for p in sorted(entries_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        meta, body = parse_entry(text)
        entries.append((meta, body))

    return manifest, entries


def _do_import(
    store: Store,
    manifest: dict,
    entries: list[tuple[dict, str]],
    dry_run: bool,
) -> dict:
    """Core import logic with scope validation and dedup."""
    imported = 0
    skipped_scope = 0
    skipped_dedup = 0
    would_import = []

    for meta, body in entries:
        scope = meta.get("scope", "team")

        # Only allow public entries from foreign workspaces
        if not is_exportable(scope):
            skipped_scope += 1
            if scope == "team":
                raise ValueError(
                    f"Refusing to import team-scoped entry '{meta.get('id', '?')}' "
                    f"from foreign workspace '{manifest.get('workspace', '?')}'. "
                    f"Only scope:public entries can be imported."
                )
            continue

        # Dedup via content hash
        h = meta.get("content_hash") or content_hash(body)
        existing = store._find_by_hash(h)
        if existing:
            skipped_dedup += 1
            continue

        if dry_run:
            would_import.append(
                {
                    "id": meta.get("id"),
                    "title": meta.get("title", "(untitled)"),
                    "scope": scope,
                }
            )
        else:
            store.write(body=body, scope=scope, agent=meta.get("agent"), tags=meta.get("tags"), title=meta.get("title"))
            imported += 1

    result = {
        "imported": imported if not dry_run else 0,
        "would_import": len(would_import) if dry_run else 0,
        "skipped_dedup": skipped_dedup,
        "skipped_scope": skipped_scope,
        "source_workspace": manifest.get("workspace", "unknown"),
    }
    if dry_run and would_import:
        result["entries"] = would_import
    return result


def _import_from_dir(store: Store, source_dir: Path, dry_run: bool) -> dict:
    """Import from a local export directory."""
    manifest, entries = _read_export_dir(source_dir)
    return _do_import(store, manifest, entries, dry_run)


def _import_from_git(store: Store, url: str, dry_run: bool) -> dict:
    """Clone a git repo and import from it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, tmpdir],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        tmp = Path(tmpdir)
        manifest, entries = _read_export_dir(tmp)
        return _do_import(store, manifest, entries, dry_run)
