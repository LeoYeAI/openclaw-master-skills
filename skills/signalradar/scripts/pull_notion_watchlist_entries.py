#!/usr/bin/env python3
"""Pull manual watchlist entries from a Notion page and merge into watchlist markdown.

Expected manual line formats in Notion page:
- Category | Question
- Category | Question | EndDate(YYYY-MM-DD)
- Question
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from error_utils import emit_error


DEFAULT_TITLE_CANDIDATES = [
    "SignalRadar_Manual_Entries",
    "SignalRadar Manual Entries",
    "Polymarket_Manual_Entries",
    "Polymarket Manual Entries",
]
DEFAULT_ROOT_TITLE_CANDIDATES = [
    "SignalRadar",
    "Signal Radar",
    "signalradar",
]
LEGACY_TOP_LEVEL_PAGE_TITLES = {
    "SignalRadar_系统目录",
    "polymarket_watchlist_2026",
    "polymarket_rollover_2026",
    "signalradar_monitor_jobs",
}
TEXT_BLOCK_TYPES = {
    "paragraph",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "quote",
    "toggle",
}

ALLOWED_CATEGORIES = {
    "AI Releases",
    "AI Leaders",
    "OpenAI IPO",
    "SpaceX IPO",
    "SpaceX Missions",
    "Crypto",
    "Geopolitics",
}
WATCH_LEVELS = {"normal", "important"}
POLYMARKET_URL_RE = re.compile(r"https?://[^\s|]+")
POLYMARKET_SLUG_RE = re.compile(r"/(?:event|market)/([a-z0-9-]+)")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def notion_headers() -> dict[str, str]:
    api_key = os.environ.get("NOTION_API_KEY", "").strip()
    if not api_key:
        raise ValueError("NOTION_API_KEY is not set")
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": os.environ.get("NOTION_API_VERSION", "2022-06-28"),
        "Content-Type": "application/json",
    }


def api_request(method: str, url: str, headers: dict[str, str], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        msg = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"notion http error {exc.code}: {msg}") from exc


def api_get(url: str, headers: dict[str, str]) -> dict[str, Any]:
    return api_request("GET", url, headers, None)


def fetch_public_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "signalradar/1.0"}, method="GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_block_children(block_id: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = ""
    while True:
        url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        payload = api_get(url, headers)
        rows = payload.get("results", [])
        if isinstance(rows, list):
            out.extend([x for x in rows if isinstance(x, dict)])
        if not payload.get("has_more"):
            break
        cursor = str(payload.get("next_cursor", "")).strip()
        if not cursor:
            break
    return out


def code_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": "plain text",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text},
                }
            ],
        },
    }


def manual_page_seed_children() -> list[dict[str, Any]]:
    return [
        code_block(
            "\n".join(
                [
                    "signalradar.page = SignalRadar_Manual_Entries",
                    "purpose = 用户手动新增监测条目（会回流到 watchlist）",
                    "editable = yes",
                    "format = 每行一个，格式如下：",
                    "  Category | Question | EndDate | WatchLevel | ThresholdPP",
                    "  （后三项可选；也支持直接粘贴 Polymarket URL）",
                    "notes = 乱格式行会被跳过；已存在条目不会重复新增",
                ]
            )
        ),
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "AI Releases | Will GPT-6 be released by June 30, 2026? | 2026-06-30 | important | 4.0"
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "https://polymarket.com/event/will-openai-release-gpt-6-before-july-2026"},
                    }
                ]
            },
        },
    ]


def root_page_seed_children() -> list[dict[str, Any]]:
    return [
        code_block(
            "\n".join(
                [
                    "signalradar.page = SignalRadar",
                    "purpose = SignalRadar 目录页",
                    "editable = limited",
                    "notes = 建议保留目录结构，不要随意删除子页面",
                ]
            )
        ),
    ]


def append_children(page_id: str, headers: dict[str, str], children: list[dict[str, Any]]) -> None:
    if not children:
        return
    payload = {"children": children}
    api_request("PATCH", f"https://api.notion.com/v1/blocks/{page_id}/children", headers, payload)


def archive_block(block_id: str, headers: dict[str, str]) -> None:
    api_request("PATCH", f"https://api.notion.com/v1/blocks/{block_id}", headers, {"archived": True})


def bulleted_item_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text},
                }
            ]
        },
    }


def create_child_page(parent_page_id: str, headers: dict[str, str], title: str) -> str:
    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]},
        },
    }
    created = api_request("POST", "https://api.notion.com/v1/pages", headers, payload)
    return str(created.get("id", "")).strip()


def create_manual_page(parent_page_id: str, headers: dict[str, str], title: str) -> str:
    page_id = create_child_page(parent_page_id, headers, title)
    if not page_id:
        return ""
    try:
        append_children(page_id, headers, manual_page_seed_children())
    except Exception:
        pass
    return page_id


def seed_manual_page_if_empty(page_id: str, headers: dict[str, str]) -> bool:
    blocks = list_block_children(page_id, headers)
    if blocks:
        return False
    append_children(page_id, headers, manual_page_seed_children())
    return True


def seed_root_page_if_empty(page_id: str, headers: dict[str, str]) -> bool:
    blocks = list_block_children(page_id, headers)
    if blocks:
        return False
    append_children(page_id, headers, root_page_seed_children())
    return True


def has_signalradar_code_header(block: dict[str, Any]) -> bool:
    if str(block.get("type", "")) != "code":
        return False
    code_obj = block.get("code")
    if not isinstance(code_obj, dict):
        return False
    text = rich_text_to_plain(code_obj.get("rich_text"))
    return "signalradar.page" in text.lower()


def ensure_manual_page_header(page_id: str, headers: dict[str, str]) -> bool:
    blocks = list_block_children(page_id, headers)
    if not blocks:
        return False
    if has_signalradar_code_header(blocks[0]):
        return False

    existing_lines = [extract_line_from_block(b) for b in blocks]
    cleaned_lines: list[str] = []
    seen: set[str] = set()
    for raw in existing_lines:
        line = raw.strip()
        if not line:
            continue
        if parse_line_to_entry(line) is None and not POLYMARKET_URL_RE.search(line):
            continue
        lowered = line.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned_lines.append(line)

    for block in blocks:
        block_id = str(block.get("id", "")).strip()
        if not block_id:
            continue
        try:
            archive_block(block_id, headers)
        except Exception:
            continue

    children = [manual_page_seed_children()[0]]
    if cleaned_lines:
        children.extend([bulleted_item_block(x) for x in cleaned_lines[:100]])
    else:
        children.extend(manual_page_seed_children()[1:])
    append_children(page_id, headers, children)
    return True


def rich_text_to_plain(rt: Any) -> str:
    if not isinstance(rt, list):
        return ""
    parts: list[str] = []
    for node in rt:
        if not isinstance(node, dict):
            continue
        text = node.get("plain_text")
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts).strip()


def extract_line_from_block(block: dict[str, Any]) -> str:
    btype = str(block.get("type", ""))
    if not btype:
        return ""
    if btype not in TEXT_BLOCK_TYPES:
        return ""
    obj = block.get(btype)
    if not isinstance(obj, dict):
        return ""
    if "rich_text" in obj:
        return rich_text_to_plain(obj.get("rich_text"))
    return ""


def find_child_page_id(parent_page_id: str, headers: dict[str, str], title_candidates: list[str]) -> str:
    children = list_block_children(parent_page_id, headers)
    normalized = {c.lower().strip() for c in title_candidates if c and c.strip()}
    for block in children:
        if block.get("type") != "child_page":
            continue
        cp = block.get("child_page", {})
        title = str(cp.get("title", "")).strip()
        if title.lower() in normalized:
            return str(block.get("id", ""))
    return ""


def move_page_to_parent(page_id: str, new_parent_page_id: str, headers: dict[str, str]) -> bool:
    payload = {"parent": {"page_id": new_parent_page_id}}
    try:
        api_request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", headers, payload)
    except Exception:
        return False
    try:
        page = api_get(f"https://api.notion.com/v1/pages/{page_id}", headers)
        parent = page.get("parent", {})
        if isinstance(parent, dict) and str(parent.get("page_id", "")).strip() == new_parent_page_id:
            return True
        return False
    except Exception:
        return False


def archive_page(page_id: str, headers: dict[str, str]) -> bool:
    try:
        api_request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", headers, {"archived": True})
    except Exception:
        return False
    return True


def extract_manual_candidate_lines(page_id: str, headers: dict[str, str]) -> list[str]:
    blocks = list_block_children(page_id, headers)
    out: list[str] = []
    seen: set[str] = set()
    for block in blocks:
        line = extract_line_from_block(block).strip()
        if not line:
            continue
        if parse_line_to_entry(line) is None and not POLYMARKET_URL_RE.search(line):
            continue
        lowered = line.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        out.append(line)
    return out


def append_manual_entry_lines(page_id: str, headers: dict[str, str], lines: list[str]) -> None:
    if not lines:
        return
    children = [bulleted_item_block(x) for x in lines[:100]]
    append_children(page_id, headers, children)


def archive_legacy_top_level_pages(
    parent_page_id: str,
    root_page_id: str,
    headers: dict[str, str],
    manual_title_candidates: list[str],
) -> None:
    if parent_page_id == root_page_id:
        return
    keep_titles = {x.strip().lower() for x in manual_title_candidates if x and x.strip()}
    legacy_titles = {x.lower() for x in LEGACY_TOP_LEVEL_PAGE_TITLES}
    for block in list_block_children(parent_page_id, headers):
        if block.get("type") != "child_page":
            continue
        page_id = str(block.get("id", "")).strip()
        if not page_id or page_id == root_page_id:
            continue
        cp = block.get("child_page", {})
        title = str(cp.get("title", "")).strip()
        lowered = title.lower()
        if lowered in legacy_titles or lowered in keep_titles:
            archive_page(page_id, headers)


def normalize_category(raw: str) -> str:
    text = raw.strip()
    if text in ALLOWED_CATEGORIES:
        return text
    lowered = text.lower()
    if "ai release" in lowered:
        return "AI Releases"
    if "ai leader" in lowered or "top ai" in lowered or "best ai" in lowered:
        return "AI Leaders"
    if "openai" in lowered and "ipo" in lowered:
        return "OpenAI IPO"
    if "spacex" in lowered and "mission" in lowered:
        return "SpaceX Missions"
    if "spacex" in lowered and "ipo" in lowered:
        return "SpaceX IPO"
    if "crypto" in lowered:
        return "Crypto"
    if "geo" in lowered or "politic" in lowered:
        return "Geopolitics"
    return "AI Releases"


def infer_category_from_question(question: str) -> str:
    q = question.lower()
    if "spacex" in q and ("launch" in q or "starship" in q or "mission" in q):
        return "SpaceX Missions"
    if "spacex" in q and "ipo" in q:
        return "SpaceX IPO"
    if "openai" in q and "ipo" in q:
        return "OpenAI IPO"
    if any(k in q for k in ["best ai", "top ai model", "ai leader"]):
        return "AI Leaders"
    if any(k in q for k in ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana"]):
        return "Crypto"
    if any(k in q for k in ["ukraine", "russia", "israel", "gaza", "taiwan", "election", "war"]):
        return "Geopolitics"
    return "AI Releases"


def parse_slug_from_url(url: str) -> str:
    m = POLYMARKET_SLUG_RE.search(url.lower())
    if not m:
        return ""
    return m.group(1).strip()


def fetch_market_by_slug(slug: str) -> dict[str, Any] | None:
    if not slug:
        return None
    candidates = [
        f"https://gamma-api.polymarket.com/markets?slug={slug}",
        f"https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=2000",
    ]
    for url in candidates:
        try:
            payload = fetch_public_json(url)
        except Exception:
            continue
        if not isinstance(payload, list):
            continue
        row = None
        if "slug=" in url:
            row = payload[0] if payload else None
        else:
            for item in payload:
                if not isinstance(item, dict):
                    continue
                if str(item.get("slug", "")).strip().lower() == slug.lower():
                    row = item
                    break
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "") or row.get("title", "")).strip()
        if not question:
            continue
        end_date = str(row.get("endDate", "") or row.get("closeTime", "") or "")[:10]
        category = infer_category_from_question(question)
        return {
            "category": category,
            "question": question,
            "end_date": end_date,
            "watch_level": "normal",
            "threshold_abs_pp": None,
        }
    return None


def parse_line_to_entry(line: str) -> dict[str, Any] | None:
    text = line.strip().replace("｜", "|").strip()
    text = text.strip("“”\"'").lstrip("-•*").strip()
    if not text:
        return None
    if text.startswith("#"):
        return None
    lowered = text.lower()
    if "format:" in lowered or "格式：" in text or "每行一个" in text:
        return None
    parts = [p.strip() for p in text.strip("|").split("|")]
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        category = normalize_category(parts[0])
        question = parts[1]
        end_date = parts[2] if len(parts) >= 3 else ""
        watch_level = parts[3] if len(parts) >= 4 else "normal"
        threshold_raw = parts[4] if len(parts) >= 5 else ""
    else:
        category = "AI Releases"
        question = parts[0]
        end_date = ""
        watch_level = "normal"
        threshold_raw = ""
    if not question:
        return None
    if re.match(r"(?i)^question$", question):
        return None
    if question.startswith("http://") or question.startswith("https://"):
        category = "AI Releases"
    end_date = end_date.strip()
    if end_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", end_date):
        end_date = ""
    watch_level = watch_level.strip().lower()
    if watch_level not in WATCH_LEVELS:
        watch_level = "normal"
    threshold_abs_pp = None
    threshold_text = threshold_raw.strip().replace("%", "")
    if threshold_text:
        try:
            threshold_val = float(threshold_text)
            if threshold_val > 0:
                threshold_abs_pp = threshold_val
        except ValueError:
            threshold_abs_pp = None
    return {
        "category": category,
        "question": question,
        "end_date": end_date,
        "watch_level": watch_level,
        "threshold_abs_pp": threshold_abs_pp,
    }


def parse_manual_entries(lines: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in lines:
        entry = parse_line_to_entry(line)
        if entry is None:
            continue
        # Allow users to paste Polymarket URL directly.
        url_match = POLYMARKET_URL_RE.search(entry["question"])
        if url_match:
            slug = parse_slug_from_url(url_match.group(0))
            resolved = fetch_market_by_slug(slug)
            if resolved is not None:
                entry = resolved
            else:
                continue
        key = entry["question"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


def parse_existing_questions(watchlist_lines: list[str]) -> set[str]:
    out: set[str] = set()
    for line in watchlist_lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        question = parts[1].strip()
        if question and question.lower() != "问题":
            out.add(question.lower())
    return out


def merge_entries_to_watchlist(watchlist_path: Path, entries: list[dict[str, Any]]) -> dict[str, Any]:
    if not watchlist_path.exists():
        raise FileNotFoundError(f"watchlist file not found: {watchlist_path}")
    lines = watchlist_path.read_text(encoding="utf-8").splitlines()
    existing = parse_existing_questions(lines)
    appended: list[str] = []
    merged_questions: list[str] = []
    skipped_questions: list[str] = []
    for e in entries:
        q = e["question"].strip()
        if q.lower() in existing:
            skipped_questions.append(q)
            continue
        category = e["category"]
        end_date = e["end_date"]
        watch_level = str(e.get("watch_level", "normal")).strip().lower()
        threshold_abs_pp = e.get("threshold_abs_pp")
        threshold_text = ""
        if isinstance(threshold_abs_pp, (int, float)) and float(threshold_abs_pp) > 0:
            threshold_text = f"{float(threshold_abs_pp):.2f}"
        row = (
            f"| {category} | {q.replace('|', '/')} | 0.00% | $0 | $0 | {end_date} | "
            f"{watch_level} | {threshold_text} |"
        )
        appended.append(row)
        existing.add(q.lower())
        merged_questions.append(q)
    if not merged_questions:
        return {
            "merged_count": 0,
            "skipped_count": len(skipped_questions),
            "merged_questions": [],
            "skipped_questions": skipped_questions,
        }
    content = "\n".join(lines) + "\n\n" + "\n".join(appended) + "\n"
    watchlist_path.write_text(content, encoding="utf-8")
    return {
        "merged_count": len(merged_questions),
        "skipped_count": len(skipped_questions),
        "merged_questions": merged_questions,
        "skipped_questions": skipped_questions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull Notion manual watchlist entries")
    parser.add_argument("--parent-page-id", required=True, help="Notion parent page id")
    parser.add_argument("--root-page-title", default="SignalRadar", help="SignalRadar directory page title")
    parser.add_argument("--title-hint", default="SignalRadar_Manual_Entries", help="Manual entries child page title")
    parser.add_argument("--watchlist", required=True, help="Watchlist markdown path")
    parser.add_argument("--out-json", default="", help="Optional output json path")
    parser.add_argument("--auto-create-page", action="store_true", help="Auto create manual entry page when missing")
    args = parser.parse_args()

    watchlist_path = Path(args.watchlist)
    out_json_path = Path(args.out_json) if args.out_json else None

    try:
        headers = notion_headers()
    except ValueError as exc:
        return emit_error(
            "SR_PERMISSION_DENIED",
            f"notion auth missing: {exc}",
            retryable=False,
            details={"script": "pull_notion_watchlist_entries.py"},
        )

    try:
        root_title_candidates = [args.root_page_title] if args.root_page_title else []
        root_title_candidates.extend(DEFAULT_ROOT_TITLE_CANDIDATES)
        root_page_id = find_child_page_id(args.parent_page_id, headers, root_title_candidates)
        if not root_page_id and args.auto_create_page:
            root_page_id = create_child_page(args.parent_page_id, headers, args.root_page_title)
            if root_page_id:
                try:
                    seed_root_page_if_empty(root_page_id, headers)
                except Exception:
                    pass
        if not root_page_id:
            root_page_id = args.parent_page_id

        manual_title_candidates = [args.title_hint] if args.title_hint else []
        manual_title_candidates.extend(DEFAULT_TITLE_CANDIDATES)
        manual_page_id = find_child_page_id(root_page_id, headers, manual_title_candidates)
        migration_note = ""
        if not manual_page_id and root_page_id != args.parent_page_id:
            legacy_page_id = find_child_page_id(args.parent_page_id, headers, manual_title_candidates)
            if legacy_page_id:
                if move_page_to_parent(legacy_page_id, root_page_id, headers):
                    manual_page_id = legacy_page_id
                    migration_note = f" MIGRATED={legacy_page_id}"
                elif args.auto_create_page:
                    legacy_lines = extract_manual_candidate_lines(legacy_page_id, headers)
                    manual_page_id = create_manual_page(root_page_id, headers, args.title_hint)
                    if manual_page_id:
                        if legacy_lines:
                            try:
                                append_manual_entry_lines(manual_page_id, headers, legacy_lines)
                            except Exception:
                                pass
                        archive_page(legacy_page_id, headers)
                        migration_note = f" MIGRATED={legacy_page_id}"

        if not manual_page_id:
            if args.auto_create_page:
                manual_page_id = create_manual_page(root_page_id, headers, args.title_hint)
                if manual_page_id:
                    print(f"DIRECTORY_PAGE={root_page_id} SOURCE_PAGE_CREATED:{manual_page_id}")
                    return 0
            print(f"DIRECTORY_PAGE={root_page_id} NO_SOURCE_PAGE")
            return 0

        try:
            archive_legacy_top_level_pages(args.parent_page_id, root_page_id, headers, manual_title_candidates)
        except Exception:
            pass

        if args.auto_create_page:
            try:
                if seed_manual_page_if_empty(manual_page_id, headers):
                    print(f"DIRECTORY_PAGE={root_page_id} SOURCE_PAGE_SEEDED:{manual_page_id}")
                    return 0
            except Exception:
                pass
            try:
                ensure_manual_page_header(manual_page_id, headers)
            except Exception:
                pass

        blocks = list_block_children(manual_page_id, headers)
        lines = [extract_line_from_block(b) for b in blocks]
        lines = [x for x in lines if x]
        entries = parse_manual_entries(lines)
        if not entries:
            if out_json_path is not None:
                payload = {
                    "ts": utc_now(),
                    "parent_page_id": args.parent_page_id,
                    "root_page_id": root_page_id,
                    "manual_page_id": manual_page_id,
                    "title_hint": args.title_hint,
                    "entries_total": 0,
                    "entries_merged": 0,
                    "entries_skipped_existing": 0,
                    "entries": [],
                    "merged_questions": [],
                    "skipped_questions": [],
                    "watchlist": str(watchlist_path),
                    "status": "NO_VALID_LINES",
                }
                out_json_path.parent.mkdir(parents=True, exist_ok=True)
                out_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"DIRECTORY_PAGE={root_page_id} MANUAL_PAGE={manual_page_id}{migration_note} NO_VALID_LINES")
            return 0

        merge_result = merge_entries_to_watchlist(watchlist_path, entries)
        merged = int(merge_result["merged_count"])
        skipped = int(merge_result["skipped_count"])
        payload = {
            "ts": utc_now(),
            "parent_page_id": args.parent_page_id,
            "root_page_id": root_page_id,
            "manual_page_id": manual_page_id,
            "title_hint": args.title_hint,
            "entries_total": len(entries),
            "entries_merged": merged,
            "entries_skipped_existing": skipped,
            "entries": entries,
            "merged_questions": merge_result["merged_questions"],
            "skipped_questions": merge_result["skipped_questions"],
            "watchlist": str(watchlist_path),
        }
        if out_json_path is not None:
            out_json_path.parent.mkdir(parents=True, exist_ok=True)
            out_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        skip_hint = ""
        if skipped > 0:
            hint_list = merge_result["skipped_questions"][:3]
            skip_hint = f" SKIPPED={skipped} EXISTING={'; '.join(hint_list)}"
        print(
            f"DIRECTORY_PAGE={root_page_id} MANUAL_PAGE={manual_page_id}{migration_note} "
            f"MERGED={merged} TOTAL={len(entries)}{skip_hint}"
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_SOURCE_UNAVAILABLE",
            f"notion pull failed: {exc}",
            retryable=True,
            details={"script": "pull_notion_watchlist_entries.py", "parent_page_id": args.parent_page_id},
        )


if __name__ == "__main__":
    raise SystemExit(main())
