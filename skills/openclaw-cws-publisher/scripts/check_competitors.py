from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from common import abs_path, dump_json, dump_text


FORBIDDEN_MARKETING_CLAIMS = [
    re.compile(r"\b#\s*1\b", re.IGNORECASE),
    re.compile(r"\bbest\b", re.IGNORECASE),
    re.compile(r"\bofficial\b", re.IGNORECASE),
    re.compile(r"\bguaranteed\b", re.IGNORECASE),
]


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            attr_map = {key.lower(): value or "" for key, value in attrs}
            if attr_map.get("name", "").lower() == "description" or attr_map.get("property", "").lower() == "og:description":
                self.description = self.description or attr_map.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def load_listing(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(abs_path(path).read_text(encoding="utf-8"))


def load_competitors(args: argparse.Namespace) -> list[dict[str, Any]]:
    competitors: list[dict[str, Any]] = []
    if args.competitors_json:
        payload = json.loads(abs_path(args.competitors_json).read_text(encoding="utf-8"))
        competitors.extend(payload.get("competitors", payload if isinstance(payload, list) else []))
    for url in args.competitor_url:
        competitors.append({"url": url})
    return competitors


def fetch_metadata(url: str, timeout: int) -> dict[str, str]:
    request = urllib.request.Request(url, headers={"user-agent": "openclaw-cws-publisher/0.3"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        html = response.read(300_000).decode("utf-8", errors="ignore")
    parser = MetaParser()
    parser.feed(html)
    return {"title": " ".join(parser.title.split()), "description": " ".join(parser.description.split())}


def words(value: str) -> set[str]:
    return {part.lower() for part in re.findall(r"[a-zA-Z][a-zA-Z0-9]{2,}", value)}


def similarity(left: str, right: str) -> float:
    left_words = words(left)
    right_words = words(right)
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / len(left_words | right_words)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# CWS Competitor Check",
        "",
        f"Competitors: **{len(report['competitors'])}**",
        f"Blockers: **{len(report['blockers'])}**",
        f"Warnings: **{len(report['warnings'])}**",
        "",
        "| Name | URL | Similarity |",
        "| --- | --- | --- |",
    ]
    for competitor in report["competitors"]:
        lines.append(
            f"| {competitor.get('name') or competitor.get('title') or 'competitor'} | {competitor.get('url', '')} | {competitor.get('similarity', 0):.2f} |"
        )
    lines.extend(["", "## Blockers"])
    lines.extend([f"- {item}" for item in report["blockers"]] or ["No blockers."])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {item}" for item in report["warnings"]] or ["No warnings."])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight CWS competitor/listing differentiation check.")
    parser.add_argument("--listing-json", help="Own CWS listing contract.")
    parser.add_argument("--competitors-json", help="JSON list or {competitors:[...]} file.")
    parser.add_argument("--competitor-url", action="append", default=[], help="Competitor/product URL to fetch. Repeatable.")
    parser.add_argument("--min-competitors", type=int, default=3)
    parser.add_argument("--fetch", action="store_true", help="Fetch competitor page metadata when title/description is missing.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--json-out", help="Optional JSON report output path.")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path.")
    args = parser.parse_args()

    listing = load_listing(args.listing_json)
    own_text = " ".join([listing.get("title", ""), listing.get("summary", ""), listing.get("detailed_description", "")])
    competitors = load_competitors(args)
    blockers: list[str] = []
    warnings: list[str] = []

    if len(competitors) < args.min_competitors:
        blockers.append(f"at least {args.min_competitors} competitors are required for a launch differentiation check")

    for pattern in FORBIDDEN_MARKETING_CLAIMS:
        if pattern.search(own_text):
            warnings.append(f"listing contains high-risk marketing claim matching {pattern.pattern}")

    enriched: list[dict[str, Any]] = []
    for competitor in competitors:
        item = dict(competitor)
        if args.fetch and item.get("url") and not item.get("title"):
            try:
                item.update(fetch_metadata(item["url"], args.timeout))
            except Exception as exc:  # noqa: BLE001 - competitor pages often block bots; report and continue.
                warnings.append(f"{item['url']}: failed to fetch competitor metadata: {exc}")
        competitor_text = " ".join([item.get("name", ""), item.get("title", ""), item.get("description", ""), item.get("positioning", "")])
        item["similarity"] = similarity(own_text, competitor_text)
        if item["similarity"] >= 0.72:
            warnings.append(f"{item.get('name') or item.get('url')}: listing may be too similar to a competitor")
        enriched.append(item)

    report = {
        "ok": not blockers,
        "listing": args.listing_json or "",
        "competitors": enriched,
        "blockers": blockers,
        "warnings": warnings,
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
