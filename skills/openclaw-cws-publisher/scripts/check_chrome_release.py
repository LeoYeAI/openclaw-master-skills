from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any

from common import dump_json, dump_text


CHROME_FOR_TESTING_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
LEGACY_PLATFORM_ALIASES = {
    "Mac": ["mac-arm64", "mac-x64"],
    "Windows": ["win32", "win64"],
    "Linux": ["linux64"],
}


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(".") if part.isdigit())


def fetch_last_known_good(timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(CHROME_FOR_TESTING_URL, headers={"user-agent": "openclaw-cws-publisher/0.3"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("channels"), dict):
        raise ValueError("unexpected Chrome for Testing last-known-good response")
    return payload


def latest_release(releases: list[dict[str, Any]]) -> dict[str, Any]:
    stable = [release for release in releases if release.get("version")]
    if not stable:
        raise ValueError("no stable releases with versions found")
    return max(stable, key=lambda release: version_tuple(str(release["version"])))


def stable_channel(payload: dict[str, Any]) -> dict[str, Any]:
    stable = (payload.get("channels") or {}).get("Stable")
    if not isinstance(stable, dict) or not stable.get("version"):
        raise ValueError("Chrome for Testing feed did not include a Stable channel version")
    return stable


def expand_platforms(platforms: list[str]) -> set[str]:
    requested: set[str] = set()
    for platform in platforms:
        requested.update(LEGACY_PLATFORM_ALIASES.get(platform, [platform]))
    return requested


def chrome_downloads(stable: dict[str, Any], requested_platforms: set[str]) -> list[dict[str, Any]]:
    downloads = ((stable.get("downloads") or {}).get("chrome") or [])
    if requested_platforms:
        downloads = [item for item in downloads if item.get("platform") in requested_platforms]
    return downloads


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Chrome Stable Release Check",
        "",
        f"Source: `{report['source']}`",
        f"Feed timestamp: `{report.get('feed_timestamp', '')}`",
        f"Stable: **{report['stable']['version']}**",
        "",
        f"Blockers: **{len(report['blockers'])}**",
        f"Warnings: **{len(report['warnings'])}**",
        "",
        "| Download platform | Version | URL |",
        "| --- | --- | --- |",
    ]
    for item in report["downloads"]:
        lines.append(f"| {item['platform']} | {item['version']} | {item['url']} |")
    lines.extend(["", "## Blockers"])
    lines.extend([f"- {item}" for item in report["blockers"]] or ["No blockers."])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {item}" for item in report["warnings"]] or ["No warnings."])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check current Chrome Stable from the Chrome for Testing last-known-good feed.")
    parser.add_argument(
        "--platform",
        action="append",
        default=[],
        help=(
            "Repeatable Chrome for Testing download platform, such as mac-arm64, mac-x64, linux64, win32, or win64. "
            "Legacy Mac/Windows/Linux aliases are accepted."
        ),
    )
    parser.add_argument("--min-milestone", type=int, help="Fail if any checked Stable milestone is older.")
    parser.add_argument("--tested-chrome-version", help="Chrome version used for local E2E; warns when behind latest Stable milestone.")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds.")
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path.")
    args = parser.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []
    payload: dict[str, Any] = {}
    stable: dict[str, Any] = {}
    downloads: list[dict[str, Any]] = []

    try:
        payload = fetch_last_known_good(args.timeout)
        stable = stable_channel(payload)
        stable_version = str(stable["version"])
        stable_milestone = version_tuple(stable_version)[0]
        downloads = chrome_downloads(stable, expand_platforms(args.platform))
        if not downloads:
            blockers.append("no Chrome download entries matched the requested platform filter")
        if args.min_milestone and stable_milestone < args.min_milestone:
            blockers.append(f"Stable milestone {stable_milestone} is below required {args.min_milestone}")
    except Exception as exc:  # noqa: BLE001 - report feed failures as release blockers.
        blockers.append(f"failed to fetch Chrome Stable release data: {exc}")

    if args.tested_chrome_version and stable.get("version"):
        tested_milestone = version_tuple(args.tested_chrome_version)[0]
        stable_milestone = version_tuple(str(stable["version"]))[0]
        if tested_milestone < stable_milestone:
            warnings.append(
                f"local E2E used Chrome {args.tested_chrome_version}, behind current Stable milestone {stable_milestone}"
            )

    report = {
        "ok": not blockers,
        "source": CHROME_FOR_TESTING_URL,
        "feed_timestamp": payload.get("timestamp", ""),
        "stable": {
            "channel": stable.get("channel", "Stable"),
            "version": stable.get("version", ""),
            "milestone": version_tuple(str(stable.get("version", "0")))[0] if stable.get("version") else 0,
        },
        "tested_chrome_version": args.tested_chrome_version or "",
        "downloads": [
            {"platform": item.get("platform", ""), "version": stable.get("version", ""), "url": item.get("url", "")}
            for item in downloads
        ],
        "blockers": blockers,
        "warnings": warnings,
        "references": [
            CHROME_FOR_TESTING_URL,
            "https://chromiumdash.appspot.com/fetch_releases",
            "https://chromereleases.googleblog.com/",
            "https://developer.chrome.com/release-notes/",
        ],
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
