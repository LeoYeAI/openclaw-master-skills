#!/usr/bin/env python3
"""Refresh polymarket watchlist + rollover suggestions.

Supports custom workspace paths via args/env:
- SIGNALRADAR_WORKSPACE_ROOT
- --workspace-root
- --output-watchlist / --output-rollover / --state
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
import os
import re
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

BASE = "https://gamma-api.polymarket.com/markets"
EVENT_BASE = "https://gamma-api.polymarket.com/events"
HEAD = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

DEFAULT_KEYWORDS: dict[str, list[str]] = {
    "AI Releases": [
        "claude 5",
        "grok 5",
        "grok 4.20",
        "grok-4pt20",
        "gpt-6",
        "deepseek",
        "deepseek v4",
        "deepseek-v4",
        "gemini 3.5",
        "gemini-3pt5",
        "chatbot arena 1500",
    ],
    "AI Leaders": ["best ai model", "top ai model"],
    "OpenAI IPO": ["openai ipo", "openai's market cap", "openai not ipo by december 31, 2026"],
    "SpaceX IPO": ["spacex ipo", "no ipo before 2028", "spacex market cap"],
    "SpaceX Missions": ["starship flight test", "spacex starship"],
}

DEFAULT_MANUAL_MARKETS: list[dict[str, Any]] = [
    {
        "category": "SpaceX IPO",
        "question": "SpaceX IPO Closing Market Cap（手动跟踪）",
        "yes": 0.0,
        "vol24h": 0.0,
        "totalVol": 0.0,
        "endDate": "2027-12-31",
        "slug": "spacex-ipo-closing-market-cap",
        "watch_level": "normal",
        "threshold_abs_pp": None,
    },
    {
        "category": "AI Releases",
        "question": "Gemini 3.5 released by June 30?（手动跟踪）",
        "yes": 0.0,
        "vol24h": 0.0,
        "totalVol": 0.0,
        "endDate": "2026-06-30",
        "slug": "gemini-3pt5-released-by-june-30",
        "watch_level": "normal",
        "threshold_abs_pp": None,
    },
]


def default_workspace_root() -> str:
    env_root = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env_root:
        return env_root
    try:
        script_root = Path(__file__).resolve().parent.parent.parent.parent
        if (script_root / "skills" / "signalradar" / "scripts").exists():
            return str(script_root)
    except Exception:
        pass
    return str(Path.cwd())


def load_keywords_config(path: Path | None) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    """Load keywords and manual_markets from external config file.

    Returns (keywords, manual_markets). Falls back to defaults if file
    does not exist or is invalid.
    """
    if path is None or not path.exists():
        return dict(DEFAULT_KEYWORDS), list(DEFAULT_MANUAL_MARKETS)
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_KEYWORDS), list(DEFAULT_MANUAL_MARKETS)
    if not isinstance(obj, dict):
        return dict(DEFAULT_KEYWORDS), list(DEFAULT_MANUAL_MARKETS)
    keywords = obj.get("keywords", DEFAULT_KEYWORDS)
    if not isinstance(keywords, dict):
        keywords = dict(DEFAULT_KEYWORDS)
    manual = obj.get("manual_markets", DEFAULT_MANUAL_MARKETS)
    if not isinstance(manual, list):
        manual = list(DEFAULT_MANUAL_MARKETS)
    return keywords, manual

STOPWORDS = set("will the a an by on before after between and or be released release at of for in to".split())


def fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all(limit: int = 500, max_pages: int = 6) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(max_pages):
        q = urllib.parse.urlencode({"active": "true", "closed": "false", "limit": str(limit), "offset": str(i * limit)})
        arr = fetch_json(f"{BASE}?{q}")
        if not arr:
            break
        rows.extend([x for x in arr if isinstance(x, dict)])
    return rows


def fetch_events(limit: int = 200, max_pages: int = 10) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(max_pages):
        q = urllib.parse.urlencode({"active": "true", "closed": "false", "limit": str(limit), "offset": str(i * limit)})
        arr = fetch_json(f"{EVENT_BASE}?{q}")
        if not arr:
            break
        rows.extend([x for x in arr if isinstance(x, dict)])
    return rows


def yes_prob(m: dict[str, Any]) -> float:
    try:
        return float(json.loads(m.get("outcomePrices", '["0","0"]'))[0]) * 100
    except Exception:
        return 0.0


def norm_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\b\d{4}\b", " ", s)
    s = re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    toks = [t for t in s.split() if t not in STOPWORDS and len(t) > 2]
    return " ".join(toks)


def parse_date(s: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat((s or "")[:10])
    except Exception:
        return None


def extract_signature(q: str) -> dict[str, set[str]]:
    ql = (q or "").lower()
    tokens = set(norm_text(ql).split())
    entities = {k for k in ["claude", "grok", "gpt", "deepseek", "gemini", "openai", "spacex", "starship", "ipo"] if k in ql}
    horizon = {k for k in ["feb", "march", "april", "june", "december", "2026", "2027"] if k in ql}
    return {"tokens": tokens, "entities": entities, "horizon": horizon}


def rollover_score(prev_item: dict[str, Any], cand_q: str, cand_end: str, cand_cat: str) -> float:
    p_sig = extract_signature(str(prev_item.get("question", "")))
    c_sig = extract_signature(cand_q)
    text_sim = SequenceMatcher(None, norm_text(str(prev_item.get("question", ""))), norm_text(cand_q)).ratio()
    tok_j = 0.0
    if p_sig["tokens"] or c_sig["tokens"]:
        inter = len(p_sig["tokens"] & c_sig["tokens"])
        uni = max(1, len(p_sig["tokens"] | c_sig["tokens"]))
        tok_j = inter / uni
    ent_bonus = 0.15 if (p_sig["entities"] & c_sig["entities"]) else 0.0
    hor_bonus = 0.05 if (p_sig["horizon"] & c_sig["horizon"]) else 0.0
    cat_bonus = 0.08 if str(prev_item.get("category")) == cand_cat else 0.0
    date_bonus = 0.0
    pd = parse_date(str(prev_item.get("endDate", "")))
    cd = parse_date(cand_end)
    if pd and cd:
        delta = abs((cd - pd).days)
        if delta <= 45:
            date_bonus = 0.08
        elif delta <= 120:
            date_bonus = 0.04
    return 0.45 * text_sim + 0.35 * tok_j + ent_bonus + hor_bonus + cat_bonus + date_bonus


def add_item(cat: str, m: dict[str, Any], seen: set[str], cat_items: list[dict[str, Any]]) -> None:
    text = (str(m.get("question", "")) + " " + str(m.get("description", ""))).lower()
    q = str(m.get("question", "")).strip()
    if not q or q in seen:
        return
    if "gemini 3" in text and "feb" in text:
        return
    ed = str(m.get("endDate") or "")[:10]
    if ed:
        try:
            if datetime.date.fromisoformat(ed) < datetime.datetime.now(datetime.timezone.utc).date():
                return
        except Exception:
            pass
    if cat in ("SpaceX IPO", "SpaceX Missions") and "spacex" not in text:
        return
    if cat == "OpenAI IPO" and "openai" not in text:
        return
    cat_items.append(
        {
            "category": cat,
            "question": q,
            "yes": round(yes_prob(m), 2),
            "vol24h": float(m.get("volume24hr") or 0),
            "totalVol": float(m.get("volumeNum") or 0),
            "endDate": ed,
            "slug": str(m.get("slug", "")),
            "watch_level": "normal",
            "threshold_abs_pp": None,
        }
    )
    seen.add(q)


def pick(
    markets: list[dict[str, Any]],
    events: list[dict[str, Any]],
    keywords: dict[str, list[str]] | None = None,
    manual_markets: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    kw = keywords if keywords is not None else DEFAULT_KEYWORDS
    mm = manual_markets if manual_markets is not None else DEFAULT_MANUAL_MARKETS
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cat, terms in kw.items():
        cat_items: list[dict[str, Any]] = []
        for m in markets:
            text = (str(m.get("question", "")) + " " + str(m.get("description", ""))).lower()
            if any(t in text for t in terms):
                add_item(cat, m, seen, cat_items)
        for e in events:
            etext = (str(e.get("title", "")) + " " + str(e.get("description", "")) + " " + str(e.get("slug", ""))).lower()
            if any(t in etext for t in terms):
                for m in (e.get("markets") or []):
                    if isinstance(m, dict):
                        add_item(cat, m, seen, cat_items)
        cat_items.sort(key=lambda x: float(x.get("vol24h", 0)), reverse=True)
        selected.extend(cat_items[:20])
    existing_slugs = {str(i.get("slug", "")) for i in selected}
    for m in mm:
        if str(m.get("slug", "")) not in existing_slugs:
            selected.append(dict(m))
    return selected


def render(items: list[dict[str, Any]]) -> str:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    lines = [
        "# Polymarket 2026 科技主题监控清单",
        "",
        f"- 更新时间(UTC): {now}",
        "- 规则：列表变化时触发提醒；无变化不提醒。",
        "- 说明：已移除 Gemini 3 2月底相关旧市场（若已接近结算/失真）。",
        "",
        "| 分类 | 问题 | Yes概率 | 24h成交额 | 总成交额 | 截止日 | WatchLevel | ThresholdPP |",
        "|---|---|---:|---:|---:|---|---|---:|",
    ]
    for x in items:
        watch_level = str(x.get("watch_level", "normal")).lower()
        threshold = x.get("threshold_abs_pp")
        threshold_text = ""
        if isinstance(threshold, (int, float)) and float(threshold) > 0:
            threshold_text = f"{float(threshold):.2f}"
        lines.append(
            f"| {x.get('category')} | {str(x.get('question','')).replace('|','/')} | {float(x.get('yes',0)):.2f}% | "
            f"${float(x.get('vol24h',0)):,.0f} | ${float(x.get('totalVol',0)):,.0f} | {x.get('endDate','')} | {watch_level} | {threshold_text} |"
        )
    return "\n".join(lines) + "\n"


def build_rollover(prev_items: list[dict[str, Any]], new_items: list[dict[str, Any]], pool: list[dict[str, Any]]) -> str:
    prev = {(i.get("slug") or i.get("question")): i for i in prev_items if isinstance(i, dict)}
    new_keys = {(i.get("slug") or i.get("question")) for i in new_items}
    removed = [v for k, v in prev.items() if k not in new_keys]
    lines = [
        "# Polymarket 关闭/迁移继任建议",
        "",
        f"- 更新时间(UTC): {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        "",
    ]
    if not removed:
        lines.append("无关闭/迁移候选。")
        return "\n".join(lines) + "\n"
    for r in removed[:20]:
        q = str(r.get("question", ""))
        cat = str(r.get("category", "Unknown"))
        cands: list[tuple[float, str, str, str]] = []
        for m in pool:
            qq = str(m.get("question", ""))
            if not qq:
                continue
            score = rollover_score(r, qq, str(m.get("endDate") or "")[:10], cat)
            if score >= 0.52:
                cands.append((score, qq, str(m.get("slug", "")), str(m.get("endDate") or "")[:10]))
        cands = sorted(cands, key=lambda x: x[0], reverse=True)[:5]
        lines.append(f"## 关闭/移除: {q}")
        lines.append(f"- 分类: {cat}")
        if not cands:
            lines.append("- 继任候选: 未找到（保留手动跟踪）")
        else:
            lines.append("- 继任候选:")
            for s, qq, slug, ed in cands:
                lines.append(f"  - ({s:.2f}) {qq} | end={ed} | slug={slug}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh polymarket watchlist + rollover")
    parser.add_argument("--workspace-root", default=default_workspace_root())
    parser.add_argument("--output-watchlist", default="")
    parser.add_argument("--output-rollover", default="")
    parser.add_argument("--state", default="")
    parser.add_argument("--market-limit", type=int, default=500)
    parser.add_argument("--market-max-pages", type=int, default=6)
    parser.add_argument("--event-limit", type=int, default=200)
    parser.add_argument("--event-max-pages", type=int, default=10)
    parser.add_argument("--keywords-config", default="", help="Path to watchlist_keywords.json (optional, falls back to defaults)")
    parser.add_argument("--dry-run", action="store_true", help="Preview entries without writing files")
    args = parser.parse_args()

    root = Path(args.workspace_root)
    out_md = Path(args.output_watchlist) if args.output_watchlist else root / "memory" / "polymarket_watchlist_2026.md"
    rollover_md = Path(args.output_rollover) if args.output_rollover else root / "memory" / "polymarket_rollover_2026.md"
    state = Path(args.state) if args.state else root / "cache" / "polymarket" / "watchlist_state.json"

    kw_path = Path(args.keywords_config) if args.keywords_config else None
    keywords, manual_markets = load_keywords_config(kw_path)

    out_md.parent.mkdir(parents=True, exist_ok=True)
    rollover_md.parent.mkdir(parents=True, exist_ok=True)
    state.parent.mkdir(parents=True, exist_ok=True)

    markets = fetch_all(limit=args.market_limit, max_pages=args.market_max_pages)
    events = fetch_events(limit=args.event_limit, max_pages=args.event_max_pages)
    items = pick(markets, events, keywords=keywords, manual_markets=manual_markets)

    # Show count per category for transparency
    cat_counts: dict[str, int] = {}
    for item in items:
        cat = str(item.get("category", "Unknown"))
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    breakdown = ", ".join(f"{c}: {n}" for c, n in sorted(cat_counts.items()))
    print(f"Watchlist will contain {len(items)} entries ({breakdown})", file=sys.stderr)

    if args.dry_run:
        print(f"DRY_RUN count={len(items)}")
        for item in items:
            print(f"  [{item.get('category')}] {item.get('question')} ({item.get('yes', 0):.1f}%)")
        return 0

    pool = list(markets)
    for e in events:
        for m in (e.get("markets") or []):
            if isinstance(m, dict):
                pool.append(m)

    old_hash = ""
    prev_items: list[dict[str, Any]] = []
    if state.exists():
        try:
            st = json.loads(state.read_text(encoding="utf-8"))
            old_hash = str(st.get("hash", ""))
            prev_items = st.get("items", []) if isinstance(st.get("items", []), list) else []
        except Exception:
            pass

    md = render(items)
    rollover = build_rollover(prev_items, items, pool)
    out_md.write_text(md, encoding="utf-8")
    rollover_md.write_text(rollover, encoding="utf-8")

    new_hash = hashlib.md5((md + "\n---\n" + rollover).encode()).hexdigest()
    state.write_text(
        json.dumps(
            {
                "hash": new_hash,
                "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if new_hash == old_hash:
        print("NO_CHANGE")
    else:
        print(f"CHANGED count={len(items)} file={out_md} rollover={rollover_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
