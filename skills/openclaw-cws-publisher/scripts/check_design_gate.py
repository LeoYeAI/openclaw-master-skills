from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import abs_path, dump_json, dump_text


REQUIRED_SCORE_FIELDS = [
    "product_clarity",
    "visual_trust",
    "evidence_integrity",
    "responsive_polish",
    "accessibility",
    "claim_alignment",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_value(surface: dict[str, Any], field: str) -> float | None:
    scores = surface.get("scores") or {}
    value = scores.get(field, surface.get(field))
    if isinstance(value, (int, float)):
        return float(value)
    return None


def validate_report(report: dict[str, Any], threshold: float) -> list[str]:
    blockers: list[str] = []
    surfaces = report.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        return ["design report must contain at least one surface"]

    for index, surface in enumerate(surfaces, start=1):
        name = surface.get("name") or f"surface #{index}"
        for field in REQUIRED_SCORE_FIELDS:
            value = score_value(surface, field)
            if value is None:
                blockers.append(f"{name}: missing {field} score")
            elif value < threshold:
                blockers.append(f"{name}: {field} score {value:g} is below {threshold:g}")
        screenshot = surface.get("screenshot") or surface.get("screenshot_path")
        if screenshot and not abs_path(screenshot).exists():
            blockers.append(f"{name}: screenshot does not exist: {screenshot}")
    return blockers


def validate_screenshot_metadata(paths: list[str]) -> list[str]:
    blockers: list[str] = []
    for raw_path in paths:
        path = abs_path(raw_path)
        if not path.exists():
            blockers.append(f"screenshot metadata does not exist: {path}")
            continue
        payload = load_json(path)
        source = payload.get("source")
        if source not in {"chrome-extension-popup", "browser-screenshot", "public-page-screenshot"}:
            blockers.append(f"{path}: unsupported screenshot source {source!r}")
        if not payload.get("captured_at"):
            blockers.append(f"{path}: missing captured_at")
        if source == "chrome-extension-popup" and not payload.get("extension_id"):
            blockers.append(f"{path}: popup screenshot metadata must include extension_id")
    return blockers


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Design And UI Gate",
        "",
        f"Threshold: **{report['threshold']:g}/10**",
        f"Blockers: **{len(report['blockers'])}**",
        "",
        "## Blockers",
    ]
    lines.extend([f"- {item}" for item in report["blockers"]] or ["No blockers."])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate recorded CWS design, UI, and UX critic scores.")
    parser.add_argument("--design-report", required=True, help="JSON report with surfaces and 0-10 critic scores.")
    parser.add_argument("--threshold", type=float, default=8.0, help="Minimum score per category.")
    parser.add_argument("--screenshot-metadata", action="append", default=[], help="Repeatable screenshot source metadata JSON.")
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path.")
    args = parser.parse_args()

    design_report_path = abs_path(args.design_report)
    source_report = load_json(design_report_path)
    blockers = [
        *validate_report(source_report, args.threshold),
        *validate_screenshot_metadata(args.screenshot_metadata),
    ]
    report = {
        "ok": not blockers,
        "design_report": str(design_report_path),
        "threshold": args.threshold,
        "blockers": blockers,
    }
    if args.json_out:
        dump_json(args.json_out, report)
    if args.markdown_out:
        dump_text(args.markdown_out, render_markdown(report))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    if blockers:
        sys.exit(1)


if __name__ == "__main__":
    main()
