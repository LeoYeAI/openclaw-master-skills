from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

from common import abs_path, dump_json, dump_text


FORBIDDEN_PERMISSIONS = {"debugger", "tabs"}
FORBIDDEN_HOST_PERMISSIONS = {
    "<all_urls>",
    "https://chromewebstore.google.com/*",
    "https://chrome.google.com/webstore/*",
}
MANIFEST_COMPARE_FIELDS = [
    "manifest_version",
    "name",
    "version",
    "description",
    "permissions",
    "host_permissions",
    "optional_host_permissions",
    "content_scripts",
]
FORBIDDEN_CODE_PATTERNS = [
    ("eval", re.compile(r"\beval\s*\(")),
    ("Function constructor", re.compile(r"\bnew\s+Function\s*\(")),
    ("remote script tag", re.compile(r"<script[^>]+src=[\"']https?://", re.IGNORECASE)),
]
TEXT_SUFFIXES = {".html", ".js", ".mjs", ".cjs", ".json", ".css"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_zip_manifest(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open("manifest.json") as handle:
            return json.loads(handle.read().decode("utf-8"))


def default_manifest_value(field: str) -> Any:
    if field in {"permissions", "host_permissions", "optional_host_permissions", "content_scripts"}:
        return []
    return None


def normalized(value: Any) -> Any:
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(value[key]) for key in sorted(value)}
    return value


def add_permission_findings(
    manifest: dict[str, Any],
    *,
    require_no_persistent_hosts: bool,
    blockers: list[str],
) -> None:
    permissions = set(manifest.get("permissions") or [])
    host_permissions = manifest.get("host_permissions") or []
    optional_host_permissions = manifest.get("optional_host_permissions") or []

    if manifest.get("manifest_version") != 3:
        blockers.append("manifest_version must be 3")

    for permission in sorted(permissions & FORBIDDEN_PERMISSIONS):
        blockers.append(f'forbidden permission "{permission}"')

    for host_permission in [*host_permissions, *optional_host_permissions]:
        if host_permission in FORBIDDEN_HOST_PERMISSIONS:
            blockers.append(f'forbidden host permission "{host_permission}"')

    if require_no_persistent_hosts and host_permissions:
        blockers.append("release ZIP requests persistent host_permissions; prefer activeTab plus scripting after user action")

    if require_no_persistent_hosts and optional_host_permissions:
        blockers.append("release ZIP requests optional_host_permissions; require a shipped opt-in flow and explicit justification")

    if not manifest.get("content_scripts") and "activeTab" in permissions and "scripting" not in permissions:
        blockers.append("activeTab dynamic capture requires scripting when no declarative content script is present")

    if require_no_persistent_hosts and manifest.get("content_scripts"):
        blockers.append("release ZIP declares content_scripts; this usually creates persistent host access and listing drift")


def add_manifest_drift_findings(
    source_manifest: dict[str, Any],
    zip_manifest: dict[str, Any],
    blockers: list[str],
) -> None:
    for field in MANIFEST_COMPARE_FIELDS:
        source_value = source_manifest.get(field, default_manifest_value(field))
        zip_value = zip_manifest.get(field, default_manifest_value(field))
        if normalized(source_value) != normalized(zip_value):
            blockers.append(f"release ZIP manifest {field} does not match source manifest")


def add_listing_findings(
    listing: dict[str, Any],
    manifest: dict[str, Any],
    blockers: list[str],
) -> None:
    permissions = manifest.get("permissions") or []
    host_permissions = manifest.get("host_permissions") or []
    optional_host_permissions = manifest.get("optional_host_permissions") or []
    host_justifications = listing.get("host_permission_justifications") or {}

    if manifest.get("name") and listing.get("title") and manifest["name"] != listing["title"]:
        blockers.append("listing title does not match manifest name")

    if manifest.get("description") and listing.get("summary") and manifest["description"] != listing["summary"]:
        blockers.append("listing summary does not match manifest description")

    if len(listing.get("summary") or "") > 132:
        blockers.append("listing summary exceeds Chrome Web Store 132-character limit")

    for permission in permissions:
        if not (listing.get("permission_justifications") or {}).get(permission):
            blockers.append(f"listing is missing permission justification for {permission}")

    for host_permission in [*host_permissions, *optional_host_permissions]:
        if not host_justifications.get(host_permission):
            blockers.append(f"listing is missing host permission justification for {host_permission}")

    if not host_permissions and not optional_host_permissions and host_justifications:
        blockers.append("listing has host_permission_justifications but the package requests no host permissions")

    detailed = listing.get("detailed_description") or ""
    if not host_permissions and not optional_host_permissions and not re.search(r"no persistent host permissions?", detailed, re.IGNORECASE):
        blockers.append('listing description must state "no persistent host permission(s)" when package has no host permissions')

    privacy = listing.get("privacy_practices") or {}
    if privacy.get("remote_code") is not False:
        blockers.append("privacy_practices.remote_code must be false")
    if privacy.get("limited_use_certification") is not True:
        blockers.append("privacy_practices.limited_use_certification must be true")


def add_code_findings(zip_path: Path, blockers: list[str], warnings: list[str]) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            name = info.filename
            if name.endswith("/"):
                continue
            suffix = Path(name).suffix.lower()
            if suffix == ".map":
                warnings.append(f"source map included in release ZIP: {name}")
                continue
            if suffix not in TEXT_SUFFIXES:
                continue
            try:
                text = archive.read(info).decode("utf-8", errors="ignore")
            except OSError:
                continue
            for label, pattern in FORBIDDEN_CODE_PATTERNS:
                if pattern.search(text):
                    blockers.append(f"release ZIP contains forbidden {label}: {name}")


def render_markdown(report: dict[str, Any]) -> str:
    blockers = report["blockers"]
    warnings = report["warnings"]
    lines = [
        "# CWS Package Validation",
        "",
        f"ZIP: `{report['zip']}`",
        f"Manifest: `{report['manifest']['name']}` v{report['manifest']['version']}",
        "",
        f"Blockers: **{len(blockers)}**",
        f"Warnings: **{len(warnings)}**",
        "",
    ]
    lines.append("## Blockers")
    lines.extend([f"- {item}" for item in blockers] or ["No blockers."])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {item}" for item in warnings] or ["No warnings."])
    return "\n".join(lines)


def validate(args: argparse.Namespace) -> dict[str, Any]:
    zip_path = abs_path(args.zip)
    blockers: list[str] = []
    warnings: list[str] = []
    if not zip_path.exists():
        blockers.append(f"release ZIP does not exist: {zip_path}")
        manifest: dict[str, Any] = {}
    else:
        manifest = read_zip_manifest(zip_path)
        add_permission_findings(
            manifest,
            require_no_persistent_hosts=not args.allow_host_permissions,
            blockers=blockers,
        )
        add_code_findings(zip_path, blockers, warnings)

    if args.source_manifest:
        add_manifest_drift_findings(read_json(abs_path(args.source_manifest)), manifest, blockers)

    if args.listing_json:
        add_listing_findings(read_json(abs_path(args.listing_json)), manifest, blockers)

    return {
        "ok": not blockers,
        "zip": str(zip_path),
        "manifest": {
            "name": manifest.get("name", ""),
            "version": manifest.get("version", ""),
            "permissions": manifest.get("permissions") or [],
            "host_permissions": manifest.get("host_permissions") or [],
            "optional_host_permissions": manifest.get("optional_host_permissions") or [],
            "content_scripts_count": len(manifest.get("content_scripts") or []),
        },
        "blockers": blockers,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the exact Chrome Web Store ZIP plus listing contract.")
    parser.add_argument("--zip", required=True, help="Release ZIP intended for CWS upload.")
    parser.add_argument("--source-manifest", help="Source manifest to compare against the ZIP manifest.")
    parser.add_argument("--listing-json", help="Repo-local docs/cws/listing.json contract.")
    parser.add_argument("--allow-host-permissions", action="store_true", help="Allow justified persistent/optional host permissions.")
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path.")
    args = parser.parse_args()

    report = validate(args)
    if args.json_out:
        dump_json(args.json_out, report)
    if args.markdown_out:
        dump_text(args.markdown_out, render_markdown(report))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    if not report["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
