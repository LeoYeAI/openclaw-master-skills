#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import zipfile


SUPPORTED_FILES = (
    "MEMORY.md",
    "SESSION-STATE.md",
    "working-buffer.md",
    "memory-capture.md",
)
SUPPORTED_DIRECTORIES = (
    "memory",
    "attachments",
)
ARCHIVE_VERSION = 1
SUBCOMMANDS = {"bootstrap", "export", "import", "report"}
DAILY_NOTE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def timestamp_slug(timestamp: str) -> str:
    return "".join(char for char in timestamp if char.isdigit())


def read_template(repo_root: Path, name: str) -> str:
    return (repo_root / "templates" / name).read_text(encoding="utf-8")


def ensure_file(path: Path, content: str) -> str:
    if path.exists():
        return "kept"
    path.write_text(content, encoding="utf-8")
    return "created"


def build_capture_content(repo_root: Path, generated_at: str) -> str:
    template = read_template(repo_root, "memory-capture.md").rstrip() + "\n"
    return (
        "# memory-capture.md\n\n"
        f"> Generated at: {generated_at}\n\n"
        f"{template}"
    )


def write_capture_file(
    workspace: Path,
    generated_at: str,
    repo_root: Path,
    *,
    refresh: bool,
) -> str:
    capture_path = workspace / "memory-capture.md"
    if capture_path.exists() and not refresh:
        return "kept"
    existed = capture_path.exists()
    capture_path.write_text(build_capture_content(repo_root, generated_at), encoding="utf-8")
    if refresh and existed:
        return "refreshed"
    return "created"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap, export, and import lightweight memory workspace files."
    )
    subparsers = parser.add_subparsers(dest="command")

    bootstrap = subparsers.add_parser(
        "bootstrap",
        help="Create baseline memory capture files in a workspace.",
    )
    add_workspace_arguments(bootstrap)
    bootstrap.add_argument(
        "--refresh-capture",
        action="store_true",
        help="Overwrite memory-capture.md with a regenerated capture sheet.",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="Export memory workspace files into a portable zip archive.",
    )
    add_workspace_arguments(export_parser)
    export_parser.add_argument(
        "--output",
        required=True,
        help="Output zip file path or output directory for the archive.",
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import a memory workspace archive into a target workspace.",
    )
    add_workspace_arguments(import_parser)
    import_parser.add_argument(
        "--input",
        required=True,
        help="Input zip archive path.",
    )
    import_parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove supported memory files and directories before restoring the archive.",
    )
    report_parser = subparsers.add_parser(
        "report",
        help="Summarize the workspace state and optionally emit a maintenance report.",
    )
    add_workspace_arguments(report_parser, include_generated_at=False)
    report_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report payload as JSON to stdout.",
    )
    report_parser.add_argument(
        "--output",
        help="Optional Markdown file path for the report.",
    )
    return parser


def add_workspace_arguments(parser: argparse.ArgumentParser, include_generated_at: bool = True) -> None:
    parser.add_argument(
        "--workspace",
        required=True,
        help="Target workspace directory where memory files should be created or restored.",
    )
    if include_generated_at:
        parser.add_argument(
            "--generated-at",
            help="Optional timestamp used in generated files and archive metadata.",
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in SUBCOMMANDS:
        argv = ["bootstrap", *argv]
    return build_parser().parse_args(argv)


def collect_workspace_paths(workspace: Path) -> list[Path]:
    paths: list[Path] = []
    for name in SUPPORTED_FILES:
        candidate = workspace / name
        if candidate.is_file():
            paths.append(candidate)
    for directory_name in SUPPORTED_DIRECTORIES:
        directory = workspace / directory_name
        if directory.is_dir():
            for path in sorted(item for item in directory.rglob("*") if item.is_file()):
                paths.append(path)
    return paths


@dataclass
class ReportData:
    workspace: Path
    supported_files: dict[str, bool]
    memory_note_count: int
    attachments_count: int
    latest_daily_note: Path | None
    warnings: list[str]


def collect_report_data(workspace: Path) -> ReportData:
    supported_files = {
        name: (workspace / name).is_file() for name in SUPPORTED_FILES
    }
    memory_dir = workspace / "memory"
    memory_notes: list[Path] = []
    if memory_dir.is_dir():
        memory_notes = sorted(
            item
            for item in memory_dir.rglob("*.md")
            if item.is_file() and DAILY_NOTE_PATTERN.fullmatch(item.name)
        )
    attachments_dir = workspace / "attachments"
    attachments_count = 0
    if attachments_dir.is_dir():
        attachments_count = sum(
            1 for item in attachments_dir.rglob("*") if item.is_file()
        )
    warnings: list[str] = []
    for name, exists in supported_files.items():
        if not exists:
            warnings.append(f"Missing supported file: {name}")
    if not memory_dir.is_dir():
        warnings.append("memory directory is missing")
    elif not memory_notes:
        warnings.append("memory directory has no daily notes")
    if not attachments_dir.is_dir():
        warnings.append("attachments directory is missing")
    elif attachments_count == 0:
        warnings.append("attachments directory is empty")
    latest_daily_note = memory_notes[-1] if memory_notes else None
    return ReportData(
        workspace=workspace,
        supported_files=supported_files,
        memory_note_count=len(memory_notes),
        attachments_count=attachments_count,
        latest_daily_note=latest_daily_note,
        warnings=warnings,
    )


def format_report_text(data: ReportData) -> str:
    lines: list[str] = [
        f"Memory workspace report for {data.workspace}",
        "",
        "Supported files:",
    ]
    for name in SUPPORTED_FILES:
        status = "present" if data.supported_files.get(name) else "missing"
        lines.append(f"  {name}: {status}")
    lines.extend(
        [
            "",
            "Directories:",
            f"  memory: {data.memory_note_count} daily note(s)",
            f"  attachments: {data.attachments_count} attachment(s)",
            "",
        ]
    )
    latest_note = (
        data.latest_daily_note.relative_to(data.workspace).as_posix()
        if data.latest_daily_note
        else "none"
    )
    lines.append(f"Latest daily note: {latest_note}")
    lines.append("")
    if data.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in data.warnings)
    else:
        lines.append("Warnings: none")
    return "\n".join(lines)


def format_report_markdown(data: ReportData) -> str:
    latest_note = (
        data.latest_daily_note.relative_to(data.workspace).as_posix()
        if data.latest_daily_note
        else "none"
    )
    lines: list[str] = [
        "# Memory workspace report",
        "",
        f"- Workspace: {data.workspace}",
        "",
        "## Supported files",
    ]
    for name in SUPPORTED_FILES:
        status = "present" if data.supported_files.get(name) else "missing"
        lines.append(f"- `{name}`: {status}")
    lines.extend(
        [
            "",
            "## Directories",
            f"- `memory`: {data.memory_note_count} daily note(s)",
            f"- `attachments`: {data.attachments_count} attachment(s)",
            "",
            "## Latest daily note",
            f"- {latest_note}",
            "",
            "## Warnings",
        ]
    )
    if data.warnings:
        lines.extend(f"- {warning}" for warning in data.warnings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def report_payload(data: ReportData) -> dict[str, object]:
    return {
        "workspace": str(data.workspace),
        "supported_files": data.supported_files,
        "memory_note_count": data.memory_note_count,
        "attachments_count": data.attachments_count,
        "latest_daily_note": (
            data.latest_daily_note.relative_to(data.workspace).as_posix()
            if data.latest_daily_note
            else None
        ),
        "warnings": data.warnings,
    }


def relative_archive_name(path: Path, workspace: Path) -> str:
    return path.relative_to(workspace).as_posix()


def manifest_payload(
    *,
    generated_at: str,
    workspace: Path,
    included_paths: list[str],
    archive_kind: str,
) -> dict[str, object]:
    return {
        "archive_version": ARCHIVE_VERSION,
        "archive_kind": archive_kind,
        "generated_at": generated_at,
        "source_workspace": str(workspace),
        "included_paths": included_paths,
    }


def create_archive(
    *,
    workspace: Path,
    archive_path: Path,
    entries: list[Path],
    generated_at: str,
    archive_kind: str,
) -> Path:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    included_paths = [relative_archive_name(path, workspace) for path in entries]
    payload = manifest_payload(
        generated_at=generated_at,
        workspace=workspace,
        included_paths=included_paths,
        archive_kind=archive_kind,
    )
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(payload, ensure_ascii=False, indent=2))
        for entry, archive_name in zip(entries, included_paths):
            archive.write(entry, archive_name)
    return archive_path


def resolve_output_archive(output: str, generated_at: str) -> Path:
    output_path = Path(output).expanduser().resolve()
    if output_path.suffix.lower() == ".zip":
        return output_path
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path / f"memory-backup-{timestamp_slug(generated_at)}.zip"


def safe_members_from_manifest(archive: zipfile.ZipFile) -> list[str]:
    try:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    except KeyError as error:
        raise ValueError("Archive is missing manifest.json.") from error

    included_paths = manifest.get("included_paths")
    if not isinstance(included_paths, list) or not all(isinstance(item, str) for item in included_paths):
        raise ValueError("Archive manifest has invalid included_paths.")

    archive_names = set(archive.namelist())
    safe_paths: list[str] = []
    for item in included_paths:
        pure_path = PurePosixPath(item)
        if pure_path.is_absolute() or ".." in pure_path.parts:
            raise ValueError(f"Archive contains unsafe path: {item}")
        if item not in archive_names:
            raise ValueError(f"Archive is missing expected file: {item}")
        safe_paths.append(item)
    return safe_paths


def create_bootstrap_files(workspace: Path, generated_at: str, repo_root: Path) -> None:
    session_status = ensure_file(
        workspace / "SESSION-STATE.md",
        read_template(repo_root, "SESSION-STATE.md"),
    )
    buffer_status = ensure_file(
        workspace / "working-buffer.md",
        read_template(repo_root, "working-buffer.md"),
    )

    capture_status = write_capture_file(
        workspace,
        generated_at,
        repo_root,
        refresh=False,
    )

    print(f"SESSION-STATE.md: {session_status}")
    print(f"working-buffer.md: {buffer_status}")
    print(f"memory-capture.md: {capture_status}")


def handle_bootstrap(args: argparse.Namespace, repo_root: Path) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    generated_at = args.generated_at or iso_now()
    if args.refresh_capture:
        session_status = ensure_file(
            workspace / "SESSION-STATE.md",
            read_template(repo_root, "SESSION-STATE.md"),
        )
        buffer_status = ensure_file(
            workspace / "working-buffer.md",
            read_template(repo_root, "working-buffer.md"),
        )
        capture_status = write_capture_file(
            workspace,
            generated_at,
            repo_root,
            refresh=True,
        )
        print(f"SESSION-STATE.md: {session_status}")
        print(f"working-buffer.md: {buffer_status}")
        print(f"memory-capture.md: {capture_status}")
        return 0
    create_bootstrap_files(workspace, generated_at, repo_root)
    return 0


def handle_export(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.is_dir():
        print(f"Workspace does not exist: {workspace}", file=sys.stderr)
        return 1

    generated_at = args.generated_at or iso_now()
    entries = collect_workspace_paths(workspace)
    if not entries:
        print("No supported memory files were found to export.", file=sys.stderr)
        return 1

    archive_path = resolve_output_archive(args.output, generated_at)
    create_archive(
        workspace=workspace,
        archive_path=archive_path,
        entries=entries,
        generated_at=generated_at,
        archive_kind="export",
    )
    print(f"Exported backup: {archive_path}")
    return 0


def backup_existing_workspace_state(workspace: Path, generated_at: str) -> Path | None:
    existing_entries = collect_workspace_paths(workspace)
    if not existing_entries:
        return None
    archive_path = workspace / f"memory-import-backup-{timestamp_slug(generated_at)}.zip"
    create_archive(
        workspace=workspace,
        archive_path=archive_path,
        entries=existing_entries,
        generated_at=generated_at,
        archive_kind="pre-import-backup",
    )
    return archive_path


def clear_supported_workspace_state(workspace: Path) -> None:
    for name in SUPPORTED_FILES:
        candidate = workspace / name
        if candidate.exists():
            candidate.unlink()
    for directory_name in SUPPORTED_DIRECTORIES:
        directory = workspace / directory_name
        if directory.exists():
            shutil.rmtree(directory)


def restore_archive(archive: zipfile.ZipFile, workspace: Path, members: list[str]) -> None:
    for member in members:
        target_path = workspace / PurePosixPath(member)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(archive.read(member))


def handle_import(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    archive_path = Path(args.input).expanduser().resolve()
    if not archive_path.is_file():
        print(f"Archive does not exist: {archive_path}", file=sys.stderr)
        return 1

    generated_at = args.generated_at or iso_now()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = safe_members_from_manifest(archive)
            backup_path = backup_existing_workspace_state(workspace, generated_at)
            if args.clean:
                clear_supported_workspace_state(workspace)
            restore_archive(archive, workspace, members)
    except (ValueError, zipfile.BadZipFile) as error:
        print(f"Import failed: {error}", file=sys.stderr)
        return 1

    mode = "clean" if args.clean else "conservative"
    print(f"Import mode: {mode}")
    if backup_path is None:
        print("Pre-import backup: none needed")
    else:
        print(f"Pre-import backup: {backup_path}")
    print(f"Imported backup: {archive_path}")
    return 0


def handle_report(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.is_dir():
        print(f"Workspace does not exist: {workspace}", file=sys.stderr)
        return 1
    report_data = collect_report_data(workspace)
    if args.json:
        print(json.dumps(report_payload(report_data), ensure_ascii=False, indent=2))
    else:
        print(format_report_text(report_data))
    output_path = getattr(args, "output", None)
    if output_path:
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(format_report_markdown(report_data), encoding="utf-8")
        if not args.json:
            print(f"Report written: {destination}")
    return 0


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    if args.command == "bootstrap":
        return handle_bootstrap(args, repo_root)
    if args.command == "export":
        return handle_export(args)
    if args.command == "import":
        return handle_import(args)
    if args.command == "report":
        return handle_report(args)
    print(f"Unsupported command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
