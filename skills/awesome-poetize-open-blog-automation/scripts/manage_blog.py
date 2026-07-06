#!/usr/bin/env python3
"""Manage Poetize articles, themes, analytics, and SEO through the public API."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import urllib.parse
from typing import Any

from blog_strategy import StrategyValidationError, apply_ops_strategy, load_json_object
from publish_post import die, extract_task_id, normalize_base_url, poll_task, request_json


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage Poetize articles, themes, analytics, and SEO through the public API."
    )
    parser.add_argument("--base-url", default=os.getenv("POETIZE_BASE_URL"), help="Poetize base URL.")
    parser.add_argument("--api-key", default=os.getenv("POETIZE_API_KEY"), help="Poetize API key.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-articles", help="List articles with filters.")
    list_parser.add_argument("--current", type=int, default=1)
    list_parser.add_argument("--size", type=int, default=10)
    list_parser.add_argument("--search-key")
    list_parser.add_argument("--sort-id", type=int)
    list_parser.add_argument("--sort-name")
    list_parser.add_argument("--label-id", type=int)
    list_parser.add_argument("--label-name")
    list_parser.add_argument("--exact-title")

    article_parser = subparsers.add_parser("get-article", help="Get article detail.")
    add_article_target_args(article_parser)

    update_parser = subparsers.add_parser("update-article", help="Update an existing article.")
    add_article_target_args(update_parser)
    update_parser.add_argument("--payload-file", required=True, help="JSON payload file for article update.")
    update_parser.add_argument("--brief-file", required=True, help="JSON brief file for strategy validation.")
    update_parser.add_argument("--wait", action="store_true", help="Poll async task until completion.")
    update_parser.add_argument("--poll-interval", type=float, default=2.0)
    update_parser.add_argument("--timeout", type=int, default=900)
    update_parser.add_argument("--print-payload", action="store_true")

    hide_parser = subparsers.add_parser("hide-article", help="Hide an article by setting viewStatus=false.")
    add_article_target_args(hide_parser)
    hide_parser.add_argument("--brief-file", required=True, help="JSON brief file for strategy validation.")
    hide_parser.add_argument("--password", help="Password for hidden article.")
    hide_parser.add_argument("--tips", help="Preview tip for hidden article.")
    hide_parser.add_argument("--wait", action="store_true", help="Poll async task until completion.")
    hide_parser.add_argument("--poll-interval", type=float, default=2.0)
    hide_parser.add_argument("--timeout", type=int, default=900)

    analytics_parser = subparsers.add_parser("article-analytics", help="Get article analytics.")
    add_article_target_args(analytics_parser)

    visits_parser = subparsers.add_parser("site-visits", help="Get site visit trends.")
    visits_parser.add_argument("--days", type=int, choices=[7, 30], default=7)

    subparsers.add_parser("theme-status", help="Get article theme status.")

    activate_theme_parser = subparsers.add_parser("activate-theme", help="Activate a global article theme.")
    activate_theme_parser.add_argument("--plugin-key", required=True)

    subparsers.add_parser("seo-status", help="Get SEO status.")
    subparsers.add_parser("seo-get-config", help="Get controlled SEO config.")

    seo_set_parser = subparsers.add_parser("seo-set-config", help="Update controlled SEO config.")
    seo_set_parser.add_argument("--config-file", required=True, help="JSON file with allowed SEO fields.")

    subparsers.add_parser("sitemap-update", help="Trigger sitemap update.")

    return parser.parse_args()


def add_article_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--article-id", type=int, help="Target article ID.")
    parser.add_argument("--article-title-exact", help="Resolve target article by exact title.")


def ensure_base_args(args: argparse.Namespace) -> None:
    if not args.base_url:
        die("Missing --base-url or POETIZE_BASE_URL.")
    if not args.api_key:
        die("Missing --api-key or POETIZE_API_KEY.")


def read_json_file(path: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        die(f"JSON file does not exist: {path}")
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON in file {path}: {exc}")

    if not isinstance(data, dict):
        die(f"JSON file must contain an object: {path}")
    return data


def list_articles(
    args: argparse.Namespace,
    *,
    search_key: str | None = None,
    current: int = 1,
    size: int = 10,
    sort_id: int | None = None,
    sort_name: str | None = None,
    label_id: int | None = None,
    label_name: str | None = None,
) -> dict[str, Any]:
    resolved_sort_id = resolve_sort_id(args, sort_id, sort_name)
    resolved_label_id = resolve_label_id(args, label_id, label_name, resolved_sort_id)
    params: dict[str, Any] = {"current": current, "size": size}
    if search_key:
        params["searchKey"] = search_key
    if resolved_sort_id is not None:
        params["sortId"] = resolved_sort_id
    if resolved_label_id is not None:
        params["labelId"] = resolved_label_id
    return request_json("GET", build_url(args.base_url, "/api/api/article/list", params), args.api_key)


def build_url(base_url: str, path: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return f"{base_url.rstrip('/')}{path}"
    filtered_params = {
        key: value for key, value in params.items()
        if value is not None and value != ""
    }
    suffix = f"?{urllib.parse.urlencode(filtered_params)}" if filtered_params else ""
    return f"{base_url.rstrip('/')}{path}{suffix}"


def extract_records(response: dict[str, Any]) -> list[dict[str, Any]]:
    data = response.get("data")
    if not isinstance(data, dict):
        return []
    records = data.get("records")
    if not isinstance(records, list):
        return []
    return [item for item in records if isinstance(item, dict)]


def fetch_categories(args: argparse.Namespace) -> list[dict[str, Any]]:
    response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/categories", args.api_key)
    if response.get("code") != 200:
        die(json.dumps(response, ensure_ascii=False, indent=2))
    data = response.get("data")
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def fetch_tags(args: argparse.Namespace) -> list[dict[str, Any]]:
    response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/tags", args.api_key)
    if response.get("code") != 200:
        die(json.dumps(response, ensure_ascii=False, indent=2))
    data = response.get("data")
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def suggest_taxonomy_candidates(
    items: list[dict[str, Any]],
    query: str,
    name_key: str,
    *,
    scope_sort_id: int | None = None,
) -> list[str]:
    query_normalized = query.strip()
    if not query_normalized:
        return []

    scoped_items = items
    if scope_sort_id is not None:
        scoped_items = [item for item in items if item.get("sortId") == scope_sort_id]

    ranked: list[tuple[float, str]] = []
    seen: set[str] = set()
    lowered_query = query_normalized.casefold()

    for item in scoped_items:
        name = str(item.get(name_key, "")).strip()
        if not name:
            continue
        lowered_name = name.casefold()
        ratio = difflib.SequenceMatcher(None, lowered_query, lowered_name).ratio()
        if lowered_query in lowered_name or lowered_name in lowered_query:
            ratio = max(ratio, 0.8)
        if ratio < 0.45:
            continue

        preview = f"{item.get('id')}:{name}"
        if item.get("sortId") is not None and name_key == "labelName":
            preview += f"@sortId={item.get('sortId')}"
        if preview in seen:
            continue
        seen.add(preview)
        ranked.append((ratio, preview))

    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    return [preview for _, preview in ranked[:5]]


def resolve_sort_id(args: argparse.Namespace, sort_id: int | None, sort_name: str | None) -> int | None:
    if sort_id is not None:
        return sort_id
    if not sort_name:
        return None

    categories = fetch_categories(args)
    matches = [
        item for item in categories
        if str(item.get("sortName", "")).strip() == sort_name.strip()
    ]
    if not matches:
        suggestions = suggest_taxonomy_candidates(categories, sort_name, "sortName")
        die(
            f"Category not found by exact name: {sort_name}\n"
            f"Closest matches: {', '.join(suggestions) if suggestions else 'none'}\n"
            "Confirm one of the candidates before continuing."
        )
    if len(matches) > 1:
        preview = ", ".join(f"{item.get('id')}:{item.get('sortName')}" for item in matches[:10])
        die(f"Multiple category matches found: {sort_name}\nMatches: {preview}")

    sort_value = matches[0].get("id")
    if not isinstance(sort_value, int):
        die(f"Resolved category does not contain a valid id: {sort_name}")
    return sort_value


def resolve_label_id(
    args: argparse.Namespace,
    label_id: int | None,
    label_name: str | None,
    sort_id: int | None = None,
) -> int | None:
    if label_id is not None:
        return label_id
    if not label_name:
        return None

    tags = fetch_tags(args)
    matches = [
        item for item in tags
        if (sort_id is None or item.get("sortId") == sort_id)
        if str(item.get("labelName", "")).strip() == label_name.strip()
    ]
    if not matches:
        suggestions = suggest_taxonomy_candidates(tags, label_name, "labelName", scope_sort_id=sort_id)
        scope = f" within sortId={sort_id}" if sort_id is not None else ""
        die(
            f"Tag not found by exact name{scope}: {label_name}\n"
            f"Closest matches: {', '.join(suggestions) if suggestions else 'none'}\n"
            "Confirm one of the candidates before continuing."
        )
    if len(matches) > 1:
        preview = ", ".join(f"{item.get('id')}:{item.get('labelName')}" for item in matches[:10])
        die(
            f"Multiple exact tag matches found: {label_name}\nMatches: {preview}\n"
            "Use --sort-id or --sort-name to narrow the scope."
        )

    label_value = matches[0].get("id")
    if not isinstance(label_value, int):
        die(f"Resolved tag does not contain a valid id: {label_name}")
    return label_value


def resolve_article_id(args: argparse.Namespace) -> int:
    if args.article_id:
        return int(args.article_id)

    title = getattr(args, "article_title_exact", None)
    if not title:
        die("Provide --article-id or --article-title-exact.")

    current = 1
    size = 50
    matches: list[dict[str, Any]] = []
    candidates: list[str] = []

    while True:
        response = list_articles(args, search_key=title, current=current, size=size)
        if response.get("code") != 200:
            die(json.dumps(response, ensure_ascii=False, indent=2))

        data = response.get("data") or {}
        records = extract_records(response)
        for item in records:
            article_title = str(item.get("articleTitle", "")).strip()
            if article_title:
                candidates.append(f"{item.get('id')}:{article_title}")
            if article_title == title.strip():
                matches.append(item)

        pages = int(data.get("pages") or 1)
        if current >= pages:
            break
        current += 1

    if not matches:
        preview = ", ".join(candidates[:10]) if candidates else "none"
        die(f"Article not found by exact title: {title}\nCandidates: {preview}")

    if len(matches) > 1:
        preview = ", ".join(
            f"{item.get('id')}:{item.get('articleTitle')}" for item in matches[:10]
        )
        die(f"Multiple exact-title matches found: {title}\nMatches: {preview}")

    article_id = matches[0].get("id")
    if not isinstance(article_id, int):
        die(f"Resolved article does not contain a valid id: {title}")
    return article_id


def post_async_update(
    args: argparse.Namespace,
    payload: dict[str, Any],
) -> None:
    response = request_json(
        "POST",
        f"{args.base_url.rstrip('/')}/api/api/article/updateAsync",
        args.api_key,
        payload,
    )
    if response.get("code") != 200:
        die(json.dumps(response, ensure_ascii=False, indent=2))

    if not getattr(args, "wait", False):
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    task_id = extract_task_id(response)
    if not task_id:
        die("Async update did not return taskId.")

    final_response = poll_task(args.base_url, args.api_key, task_id, args.poll_interval, args.timeout)
    print(json.dumps(final_response, ensure_ascii=False, indent=2))


def main() -> None:
    configure_stdio()
    args = parse_args()
    args.base_url = normalize_base_url(str(args.base_url or ""))
    ensure_base_args(args)

    if args.command == "list-articles":
        response = list_articles(
            args,
            search_key=args.search_key,
            current=args.current,
            size=args.size,
            sort_id=args.sort_id,
            sort_name=args.sort_name,
            label_id=args.label_id,
            label_name=args.label_name,
        )
        if args.exact_title:
            records = [
                item for item in extract_records(response)
                if str(item.get("articleTitle", "")).strip() == args.exact_title.strip()
            ]
            response = {
                "code": response.get("code"),
                "message": response.get("message"),
                "data": {
                    "records": records,
                    "matched": len(records)
                }
            }
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "get-article":
        article_id = resolve_article_id(args)
        response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/article/{article_id}", args.api_key)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "update-article":
        try:
            article_id = resolve_article_id(args)
            payload = read_json_file(args.payload_file)
            brief = load_json_object(args.brief_file, label="Brief file")
            payload["id"] = article_id
            payload = apply_ops_strategy(brief, payload, expected_task_type="update_article")
            if args.print_payload:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return
            post_async_update(args, payload)
            return
        except StrategyValidationError as exc:
            die(exc.render())

    if args.command == "hide-article":
        try:
            article_id = resolve_article_id(args)
            brief = load_json_object(args.brief_file, label="Brief file")
            payload = {
                "id": article_id,
                "viewStatus": False,
                "password": args.password or f"hidden-{article_id}",
                "tips": args.tips or "文章已隐藏，仅供受控预览"
            }
            payload = apply_ops_strategy(brief, payload, expected_task_type="hide_article")
            post_async_update(args, payload)
            return
        except StrategyValidationError as exc:
            die(exc.render())

    if args.command == "article-analytics":
        article_id = resolve_article_id(args)
        response = request_json(
            "GET",
            f"{args.base_url.rstrip('/')}/api/api/article/analytics/{article_id}",
            args.api_key,
        )
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "site-visits":
        response = request_json(
            "GET",
            build_url(args.base_url, "/api/api/analytics/site/visits", {"days": args.days}),
            args.api_key,
        )
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "theme-status":
        response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/article-theme/status", args.api_key)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "activate-theme":
        response = request_json(
            "POST",
            f"{args.base_url.rstrip('/')}/api/api/article-theme/activate",
            args.api_key,
            {"pluginKey": args.plugin_key},
        )
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "seo-status":
        response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/seo/status", args.api_key)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "seo-get-config":
        response = request_json("GET", f"{args.base_url.rstrip('/')}/api/api/seo/config", args.api_key)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "seo-set-config":
        payload = read_json_file(args.config_file)
        response = request_json(
            "POST",
            f"{args.base_url.rstrip('/')}/api/api/seo/config",
            args.api_key,
            payload,
        )
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    if args.command == "sitemap-update":
        response = request_json(
            "POST",
            f"{args.base_url.rstrip('/')}/api/api/seo/sitemap/update",
            args.api_key,
            {},
        )
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    die(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
