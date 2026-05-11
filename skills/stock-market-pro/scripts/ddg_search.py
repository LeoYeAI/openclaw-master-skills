#!/usr/bin/env python3
"""DuckDuckGo search helper (ddgs).

This is vendored into the skill so the published package is self-contained.

Dependency
- pip install -U ddgs

Usage examples
- python3 scripts/ddg_search.py "NVDA latest news" --kind news --max 8 --out md
- python3 scripts/ddg_search.py "Tesla stock ticker" --kind text --max 5 --out md
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterable, List


def _load_ddgs():
    try:
        from ddgs import DDGS  # type: ignore

        return DDGS
    except Exception:
        # Back-compat fallback (older name)
        try:
            from duckduckgo_search import DDGS  # type: ignore

            return DDGS
        except Exception as e:
            raise RuntimeError("Missing dependency. Install with: pip3 install -U ddgs") from e


def _iter_results(ddgs: Any, kind: str, query: str, **kwargs) -> Iterable[dict]:
    if kind == "text":
        return ddgs.text(query, **kwargs)
    if kind == "news":
        return ddgs.news(query, **kwargs)
    if kind == "images":
        return ddgs.images(query, **kwargs)
    if kind == "videos":
        return ddgs.videos(query, **kwargs)
    if kind == "books":
        return ddgs.books(query, **kwargs)
    raise ValueError(f"Unknown kind: {kind}")


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="DuckDuckGo search helper (ddgs)")
    p.add_argument("query", help="Search query")
    p.add_argument(
        "--kind",
        choices=["text", "news", "images", "videos", "books"],
        default="text",
        help="Search type",
    )
    p.add_argument("--max", type=int, default=8, dest="max_results")
    p.add_argument("--region", default="kr-kr")
    p.add_argument("--safesearch", default="moderate", choices=["on", "moderate", "off"])
    p.add_argument("--timelimit", default=None, help="d|w|m|y (optional)")
    p.add_argument(
        "--backend",
        default="auto",
        help='ddgs backend (text/news). e.g. "duckduckgo" or "auto"',
    )
    p.add_argument(
        "--proxy",
        default=None,
        help='Proxy URL (http/https/socks5). For Tor Browser: "tb" (socks5://127.0.0.1:9150) if supported by ddgs.',
    )
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--verify", default="true", choices=["true", "false"], help="TLS verify")
    p.add_argument(
        "--out",
        choices=["json", "jsonl", "md"],
        default="json",
        help="Output format",
    )

    args = p.parse_args(argv)

    DDGS = _load_ddgs()

    verify: Any = args.verify == "true"

    ddgs = DDGS(proxy=args.proxy, timeout=args.timeout, verify=verify)

    kwargs: dict[str, Any] = {
        "region": args.region,
        "safesearch": args.safesearch,
        "timelimit": args.timelimit,
        "max_results": args.max_results,
    }

    if args.kind in ("text", "news"):
        kwargs["backend"] = args.backend

    results = list(_iter_results(ddgs, args.kind, args.query, **kwargs))

    if args.out == "json":
        sys.stdout.write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
        return 0

    if args.out == "jsonl":
        for r in results:
            sys.stdout.write(json.dumps(r, ensure_ascii=False) + "\n")
        return 0

    # md
    for i, r in enumerate(results, 1):
        title = r.get("title") or r.get("name") or "(no title)"
        href = r.get("href") or r.get("url") or ""
        body = r.get("body") or r.get("snippet") or ""
        sys.stdout.write(f"{i}. [{title}]({href})\n")
        if body:
            sys.stdout.write(f"   - {body.strip()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
