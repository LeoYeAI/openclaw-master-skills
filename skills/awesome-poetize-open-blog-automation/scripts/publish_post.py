#!/usr/bin/env python3
"""Create or update Poetize articles through the public API."""

from __future__ import annotations

import argparse
import difflib
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from blog_strategy import StrategyValidationError, apply_article_strategy, load_json_object

MISSING = object()
HTML_IMAGE_SRC_PATTERN = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(?P<src>.+?)(\2)',
    re.IGNORECASE,
)


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update a Poetize article from Markdown front matter."
    )
    parser.add_argument("--markdown-file", required=True, help="Path to a Markdown file.")
    parser.add_argument("--article-id", type=int, help="Existing article ID to update.")
    parser.add_argument("--brief-file", required=True, help="JSON brief file for strategy validation.")
    parser.add_argument("--base-url", default=os.getenv("POETIZE_BASE_URL"), help="Poetize base URL.")
    parser.add_argument("--api-key", default=os.getenv("POETIZE_API_KEY"), help="Poetize API key.")
    parser.add_argument("--publish", action="store_true", help="Force public publish.")
    parser.add_argument("--draft", action="store_true", help="Force draft/private save.")
    parser.add_argument("--cover-file", help="Optional local cover file path.")
    parser.add_argument("--payment-plugin-key", help="Optional payment plugin key to target for paid articles.")
    parser.add_argument("--payment-config-file", help="Optional JSON file used to configure the payment plugin.")
    parser.add_argument("--require-paid", action="store_true", help="Fail instead of downgrading when paid publishing is not available.")
    parser.add_argument("--allow-create-taxonomy", action="store_true", help="Allow creating missing categories and tags.")
    parser.add_argument("--allow-create-sort", action="store_true", help="Allow creating a missing category.")
    parser.add_argument("--allow-create-label", action="store_true", help="Allow creating a missing tag.")
    parser.add_argument("--print-payload", action="store_true", help="Print the JSON payload before sending.")
    parser.add_argument("--wait", action="store_true", help="Poll the async task until the article finishes processing.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Task polling interval in seconds.")
    parser.add_argument("--timeout", type=int, default=900, help="Maximum wait time in seconds when --wait is set.")
    return parser.parse_args()


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def normalize_base_url(base_url: str) -> str:
    sanitized = base_url.strip()
    if not sanitized:
        return ""

    sanitized = sanitized.rstrip("/")
    if sanitized.lower().endswith("/api/api"):
        sanitized = sanitized[:-8].rstrip("/")
    elif sanitized.lower().endswith("/api"):
        sanitized = sanitized[:-4].rstrip("/")
    return sanitized


def meta_string(meta: dict[str, Any], key: str) -> str | None:
    value = meta.get(key)
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""

    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text

    meta: dict[str, Any] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        meta[key.strip()] = parse_scalar(raw_value)

    body = "\n".join(lines[end_index + 1 :]).lstrip()
    return meta, body


def extract_title_from_body(body: str) -> tuple[str | None, str]:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            remaining = "\n".join(lines[index + 1 :]).lstrip()
            return title, remaining
        return None, body
    return None, body


def strip_matching_title_heading(body: str, title: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == f"# {title}".strip():
            return "\n".join(lines[index + 1 :]).lstrip()
        return body
    return body


def request_json(
    method: str,
    url: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    data: bytes | None = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=UTF-8"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url=url, method=method, headers=headers, data=data)

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            content = response.read().decode(charset)
            return json.loads(content)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        die(f"HTTP {exc.code} calling {url}\n{body}")
    except urllib.error.URLError as exc:
        die(f"Network error calling {url}: {exc}")
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON response from {url}: {exc}")


def read_json_file(path: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        die(f"Payment config file does not exist: {path}")
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON in payment config file {path}: {exc}")

    if not isinstance(data, dict):
        die(f"Payment config file must contain a JSON object: {path}")
    return data


def normalize_name(value: str) -> str:
    return value.strip().casefold()


def fetch_taxonomy(base_url: str, api_key: str, endpoint: str) -> list[dict[str, Any]]:
    response = request_json("GET", f"{base_url.rstrip('/')}{endpoint}", api_key)
    if response.get("code") != 200:
        message = response.get("message") or f"Failed to fetch taxonomy from {endpoint}."
        die(message)

    data = response.get("data")
    if not isinstance(data, list):
        die(f"Invalid taxonomy response from {endpoint}.")

    return [item for item in data if isinstance(item, dict)]


def format_name_suggestions(items: list[str], empty_message: str) -> str:
    if not items:
        return empty_message
    preview = ", ".join(items[:10])
    if len(items) > 10:
        preview += ", ..."
    return preview


def suggest_name_suggestions(
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

    lowered_query = query_normalized.casefold()
    ranked: list[tuple[float, str]] = []
    seen: set[str] = set()

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

        preview = str(item.get(name_key))
        if item.get("sortId") is not None and name_key == "labelName":
            preview += f"@sortId={item.get('sortId')}"
        if preview in seen:
            continue
        seen.add(preview)
        ranked.append((ratio, preview))

    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    return [preview for _, preview in ranked[:5]]


def truthy_meta(meta: dict[str, Any], key: str) -> bool:
    value = meta.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def ensure_taxonomy_ready(
    payload: dict[str, Any],
    meta: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    if payload.get("sortId") is not None and payload.get("labelId") is not None:
        return payload

    allow_create_taxonomy = bool(args.allow_create_taxonomy or truthy_meta(meta, "allowCreateTaxonomy"))
    allow_create_sort = bool(allow_create_taxonomy or args.allow_create_sort or truthy_meta(meta, "allowCreateSort"))
    allow_create_label = bool(allow_create_taxonomy or args.allow_create_label or truthy_meta(meta, "allowCreateLabel"))

    sort_name = payload.get("sortName")
    label_name = payload.get("labelName")

    sorts = fetch_taxonomy(args.base_url, args.api_key, "/api/api/categories")
    labels = fetch_taxonomy(args.base_url, args.api_key, "/api/api/tags")

    resolved_sort_id = payload.get("sortId")
    new_sort_pending = False

    if resolved_sort_id is None and isinstance(sort_name, str) and sort_name.strip():
        matched_sort = next(
            (
                item for item in sorts
                if normalize_name(str(item.get("sortName", ""))) == normalize_name(sort_name)
            ),
            None,
        )
        if matched_sort is not None:
            resolved_sort_id = matched_sort.get("id")
            payload["sortId"] = resolved_sort_id
            payload.pop("sortName", None)
        elif allow_create_sort:
            new_sort_pending = True
        else:
            suggested_sorts = suggest_name_suggestions(sorts, sort_name, "sortName")
            die(
                "Category does not exist and auto-create is disabled: "
                f"{sort_name}\nClosest matches: {format_name_suggestions(suggested_sorts, 'none')}\n"
                "Ask OpenClaw/user to confirm creation, or set allowCreateSort: true / --allow-create-sort."
            )

    if payload.get("labelId") is None and isinstance(label_name, str) and label_name.strip():
        matched_label: dict[str, Any] | None = None
        if isinstance(resolved_sort_id, int):
            matched_label = next(
                (
                    item for item in labels
                    if item.get("sortId") == resolved_sort_id
                    and normalize_name(str(item.get("labelName", ""))) == normalize_name(label_name)
                ),
                None,
            )
        elif not new_sort_pending:
            label_matches = [
                item for item in labels
                if normalize_name(str(item.get("labelName", ""))) == normalize_name(label_name)
            ]
            if len(label_matches) == 1:
                matched_label = label_matches[0]
            elif len(label_matches) > 1 and not allow_create_label:
                candidate_names = []
                for item in label_matches:
                    candidate_names.append(f"{item.get('labelName')}@sortId={item.get('sortId')}")
                die(
                    "Tag name is ambiguous across categories: "
                    f"{label_name}\nMatches: {format_name_suggestions(candidate_names, 'none')}\n"
                    "Provide labelId, specify an existing category, or explicitly allow tag creation."
                )

        if matched_label is not None:
            payload["labelId"] = matched_label.get("id")
            payload.pop("labelName", None)
        elif allow_create_label:
            pass
        else:
            if isinstance(resolved_sort_id, int):
                suggested_labels = suggest_name_suggestions(
                    labels,
                    label_name,
                    "labelName",
                    scope_sort_id=resolved_sort_id,
                )
                scope = f"sortId={resolved_sort_id}"
            elif new_sort_pending:
                suggested_labels = []
                scope = "new category"
            else:
                suggested_labels = suggest_name_suggestions(labels, label_name, "labelName")
                scope = "all categories"
            die(
                "Tag does not exist and auto-create is disabled: "
                f"{label_name}\nScope: {scope}\nClosest matches: {format_name_suggestions(suggested_labels, 'none')}\n"
                "Ask OpenClaw/user to confirm creation, or set allowCreateLabel: true / --allow-create-label."
            )

    return payload


def is_task_completed(status: str | None) -> bool:
    return status in {"success", "failed", "partial_success"}


def extract_task_id(response: dict[str, Any]) -> str | None:
    data = response.get("data")
    if isinstance(data, str) and data:
        return data
    if isinstance(data, dict):
        task_id = data.get("taskId")
        if isinstance(task_id, str) and task_id:
            return task_id
    return None


def poll_task(
    base_url: str,
    api_key: str,
    task_id: str,
    interval_seconds: float,
    timeout_seconds: int,
) -> dict[str, Any]:
    status_url = f"{base_url.rstrip('/')}/api/api/article/task/{urllib.parse.quote(task_id, safe='')}"
    deadline = time.time() + timeout_seconds

    while True:
        response = request_json("GET", status_url, api_key)
        if response.get("code") != 200:
            die(json.dumps(response, ensure_ascii=False, indent=2))

        data = response.get("data")
        if isinstance(data, dict):
            status = data.get("status")
            completed = data.get("completed")
            if completed is True or is_task_completed(status if isinstance(status, str) else None):
                return response

        if time.time() >= deadline:
            die(f"Timed out waiting for task {task_id} after {timeout_seconds} seconds.")

        time.sleep(max(interval_seconds, 0.2))


def encode_multipart(fields: dict[str, str], file_field: str, file_path: str) -> tuple[bytes, str]:
    boundary = f"----PoetizeBoundary{uuid.uuid4().hex}"
    file_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )

    with open(file_path, "rb") as handle:
        file_bytes = handle.read()

    chunks.append(f"--{boundary}\r\n".encode("utf-8"))
    chunks.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    chunks.append(file_bytes)
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))

    return b"".join(chunks), boundary


def upload_resource(
    base_url: str,
    api_key: str,
    file_path: str,
    *,
    resource_type: str,
    store_type: str | None = None,
) -> str:
    if not os.path.isfile(file_path):
        die(f"Upload file does not exist: {file_path}")

    fields = {"type": resource_type}
    if store_type:
        fields["storeType"] = store_type

    upload_url = f"{base_url.rstrip('/')}/api/api/resource/upload"
    body, boundary = encode_multipart(fields, "file", file_path)
    request = urllib.request.Request(
        url=upload_url,
        method="POST",
        headers={
            "X-API-KEY": api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        data=body,
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            content = response.read().decode(response.headers.get_content_charset() or "utf-8")
            data = json.loads(content)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        die(f"HTTP {exc.code} uploading resource\n{body}")
    except urllib.error.URLError as exc:
        die(f"Network error uploading resource: {exc}")

    if data.get("code") != 200 or not data.get("data"):
        die(json.dumps(data, ensure_ascii=False, indent=2))

    upload_data = data["data"]
    if not isinstance(upload_data, dict):
        die("Upload API returned an invalid response payload.")

    uploaded_url = upload_data.get("url") or upload_data.get("path") or ""
    if not isinstance(uploaded_url, str) or not uploaded_url:
        die("Upload API did not return a usable URL.")
    return uploaded_url


def upload_cover(base_url: str, api_key: str, cover_file: str, store_type: str | None = None) -> str:
    return upload_resource(
        base_url,
        api_key,
        cover_file,
        resource_type="articleCover",
        store_type=store_type,
    )


def split_markdown_link_target(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    if not target:
        return "", ""

    if target.startswith("<"):
        closing = target.find(">")
        if closing != -1:
            return target[1:closing], target[closing + 1 :]

    for index, char in enumerate(target):
        if not char.isspace():
            continue
        suffix = target[index:]
        suffix_stripped = suffix.lstrip()
        if suffix_stripped and suffix_stripped[0] not in {'"', "'", "("}:
            return target, ""
        return target[:index], suffix

    return target, ""


def iter_markdown_inline_images(markdown_text: str) -> list[tuple[int, int, str, str]]:
    results: list[tuple[int, int, str, str]] = []
    cursor = 0
    length = len(markdown_text)

    while cursor < length:
        start = markdown_text.find("![", cursor)
        if start < 0:
            break

        alt_start = start + 2
        alt_end = markdown_text.find("]", alt_start)
        if alt_end < 0:
            break

        if alt_end + 1 >= length or markdown_text[alt_end + 1] != "(":
            cursor = alt_end + 1
            continue

        target_start = alt_end + 2
        depth = 1
        index = target_start
        escaped = False
        in_angle = False

        while index < length:
            char = markdown_text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "<" and depth == 1:
                in_angle = True
            elif char == ">" and in_angle:
                in_angle = False
            elif char == "(" and not in_angle:
                depth += 1
            elif char == ")" and not in_angle:
                depth -= 1
                if depth == 0:
                    break
            index += 1

        if depth != 0:
            cursor = alt_end + 1
            continue

        results.append(
            (
                start,
                index + 1,
                markdown_text[alt_start:alt_end],
                markdown_text[target_start:index],
            )
        )
        cursor = index + 1

    return results


def is_remote_or_embedded_reference(reference: str) -> bool:
    lowered = reference.strip().lower()
    if not lowered:
        return False
    return lowered.startswith(
        ("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:", "#")
    )


def is_probably_local_file_reference(reference: str) -> bool:
    candidate = reference.strip()
    if not candidate or is_remote_or_embedded_reference(candidate):
        return False
    if candidate.lower().startswith("file://"):
        return True

    decoded = urllib.parse.unquote(candidate)
    if os.path.isabs(decoded):
        return True

    return not decoded.startswith("/")


def resolve_local_file_path(reference: str, markdown_file: str) -> Path | None:
    candidate = reference.strip()
    if not candidate or is_remote_or_embedded_reference(candidate):
        return None

    decoded = urllib.parse.unquote(candidate)
    if candidate.lower().startswith("file://"):
        parsed = urllib.parse.urlparse(candidate)
        path_text = urllib.request.url2pathname(urllib.parse.unquote(parsed.path or ""))
        if os.name == "nt" and path_text.startswith("/") and len(path_text) > 2 and path_text[2] == ":":
            path_text = path_text[1:]
        if parsed.netloc and parsed.netloc not in {"", "localhost"}:
            path_text = f"//{parsed.netloc}{path_text}"
        target = Path(path_text)
    else:
        target = Path(decoded).expanduser()
        if not target.is_absolute():
            target = Path(markdown_file).resolve().parent / target

    resolved = target.resolve(strict=False)
    if resolved.is_file():
        return resolved
    return None


def should_auto_upload_local_images(meta: dict[str, Any]) -> bool:
    for key in ("uploadLocalImages", "uploadMarkdownImages"):
        if key in meta:
            return truthy_meta(meta, key)
    return True


def upload_local_article_asset(
    reference: str,
    markdown_file: str,
    base_url: str,
    api_key: str,
    meta: dict[str, Any],
    upload_cache: dict[str, str],
) -> str | None:
    resolved_path = resolve_local_file_path(reference, markdown_file)
    if resolved_path is None:
        if is_probably_local_file_reference(reference):
            die(
                "Local article asset was referenced but not found: "
                f"{reference}\nMarkdown file: {markdown_file}"
            )
        return None

    cache_key = os.path.normcase(str(resolved_path))
    if cache_key in upload_cache:
        return upload_cache[cache_key]

    store_type = meta_string(meta, "markdownImageStoreType") or meta_string(meta, "imageStoreType")
    resource_type = meta_string(meta, "markdownImageType") or "articlePicture"
    print(f"Uploading local article asset: {resolved_path}", file=sys.stderr)
    uploaded_url = upload_resource(
        base_url,
        api_key,
        str(resolved_path),
        resource_type=resource_type,
        store_type=store_type,
    )
    upload_cache[cache_key] = uploaded_url
    return uploaded_url


def replace_local_markdown_images(
    markdown_text: str,
    markdown_file: str,
    base_url: str,
    api_key: str,
    meta: dict[str, Any],
) -> str:
    if not should_auto_upload_local_images(meta):
        return markdown_text

    upload_cache: dict[str, str] = {}
    parts: list[str] = []
    cursor = 0
    changed = False

    for start, end, alt_text, raw_target in iter_markdown_inline_images(markdown_text):
        parts.append(markdown_text[cursor:start])
        destination, suffix = split_markdown_link_target(raw_target)
        uploaded_url = upload_local_article_asset(
            destination,
            markdown_file,
            base_url,
            api_key,
            meta,
            upload_cache,
        )
        if uploaded_url:
            parts.append(f"![{alt_text}]({uploaded_url}{suffix})")
            changed = True
        else:
            parts.append(markdown_text[start:end])
        cursor = end

    parts.append(markdown_text[cursor:])
    updated = "".join(parts)

    def replace_html(match: re.Match[str]) -> str:
        nonlocal changed
        source = match.group("src")
        uploaded_url = upload_local_article_asset(
            source,
            markdown_file,
            base_url,
            api_key,
            meta,
            upload_cache,
        )
        if not uploaded_url:
            return match.group(0)
        changed = True
        return f"{match.group(1)}{match.group(2)}{uploaded_url}{match.group(2)}"

    updated = HTML_IMAGE_SRC_PATTERN.sub(replace_html, updated)
    return updated if changed else markdown_text


def downgrade_paid_payload(payload: dict[str, Any], reason: str) -> dict[str, Any]:
    print(f"Paid publishing unavailable. Downgrading to free article: {reason}", file=sys.stderr)
    payload["payType"] = 0
    payload.pop("payAmount", None)
    payload.pop("freePercent", None)
    return payload


def ensure_payment_plugin_ready(
    payload: dict[str, Any],
    meta: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    pay_type = payload.get("payType")
    if not isinstance(pay_type, int) or pay_type <= 0:
        return payload

    requested_plugin_key = args.payment_plugin_key or meta.get("paymentPluginKey")
    strict_paid = bool(args.require_paid or meta.get("requirePaid"))
    status_url = f"{args.base_url.rstrip('/')}/api/api/payment/plugin/status"
    if isinstance(requested_plugin_key, str) and requested_plugin_key:
        status_url = (
            f"{status_url}?pluginKey="
            f"{urllib.parse.quote(requested_plugin_key, safe='')}"
        )

    status_response = request_json("GET", status_url, args.api_key)
    if status_response.get("code") != 200:
        message = status_response.get("message") or "Failed to inspect payment plugin status."
        if strict_paid:
            die(message)
        return downgrade_paid_payload(payload, message)

    status_data = status_response.get("data")
    target_plugin = status_data.get("targetPlugin") if isinstance(status_data, dict) else None
    if not isinstance(target_plugin, dict):
        message = "No usable payment plugin is installed."
        if strict_paid:
            die(message)
        return downgrade_paid_payload(payload, message)

    plugin_key = target_plugin.get("pluginKey")
    if not isinstance(plugin_key, str) or not plugin_key:
        message = "Payment plugin status did not include a pluginKey."
        if strict_paid:
            die(message)
        return downgrade_paid_payload(payload, message)

    if target_plugin.get("enabled") is not True:
        message = f"Payment plugin '{plugin_key}' is not enabled."
        if strict_paid:
            die(message)
        return downgrade_paid_payload(payload, message)

    configured = target_plugin.get("configured") is True
    payment_config_file = args.payment_config_file or meta.get("paymentConfigFile")
    if not configured and payment_config_file:
        config_payload = read_json_file(str(payment_config_file))
        configure_response = request_json(
            "POST",
            f"{args.base_url.rstrip('/')}/api/api/payment/plugin/configure",
            args.api_key,
            {
                "pluginKey": plugin_key,
                "pluginConfig": config_payload,
                "activate": True,
            },
        )
        if configure_response.get("code") == 200:
            configured = True
        else:
            message = configure_response.get("message") or "Payment plugin configuration failed."
            if strict_paid:
                die(json.dumps(configure_response, ensure_ascii=False, indent=2))
            return downgrade_paid_payload(payload, message)

    if not configured:
        missing_fields = target_plugin.get("missingFields")
        if isinstance(missing_fields, list) and missing_fields:
            message = f"Payment plugin '{plugin_key}' is missing fields: {', '.join(map(str, missing_fields))}"
        else:
            message = f"Payment plugin '{plugin_key}' is not configured."
        if strict_paid:
            die(message)
        return downgrade_paid_payload(payload, message)

    if target_plugin.get("active") is not True:
        activation_response = request_json(
            "POST",
            f"{args.base_url.rstrip('/')}/api/api/payment/plugin/configure",
            args.api_key,
            {
                "pluginKey": plugin_key,
                "pluginConfig": {},
                "activate": True,
            },
        )
        if activation_response.get("code") != 200:
            message = activation_response.get("message") or "Failed to activate the payment plugin."
            if strict_paid:
                die(json.dumps(activation_response, ensure_ascii=False, indent=2))
            return downgrade_paid_payload(payload, message)

    test_response = request_json(
        "POST",
        f"{args.base_url.rstrip('/')}/api/api/payment/plugin/testConnection",
        args.api_key,
        {"pluginKey": plugin_key},
    )
    if test_response.get("code") != 200:
        message = test_response.get("message") or "Payment plugin connection test failed."
        if strict_paid:
            die(json.dumps(test_response, ensure_ascii=False, indent=2))
        return downgrade_paid_payload(payload, message)

    test_data = test_response.get("data")
    if not isinstance(test_data, dict) or test_data.get("connectionOk") is not True:
        message = "Payment plugin connection test did not succeed."
        if strict_paid:
            die(json.dumps(test_response, ensure_ascii=False, indent=2))
        return downgrade_paid_payload(payload, message)

    return payload


def resolve_cover(meta: dict[str, Any], args: argparse.Namespace) -> str | None:
    cover_blank = meta.get("coverBlank")
    if isinstance(cover_blank, bool) and cover_blank:
        return " "

    store_type = meta_string(meta, "coverStoreType") or meta_string(meta, "storeType")
    candidate = args.cover_file or meta.get("coverFile")
    if candidate:
        return upload_cover(args.base_url, args.api_key, str(candidate), store_type)

    cover = meta.get("cover")
    if isinstance(cover, str) and cover == " ":
        return " "
    if isinstance(cover, str) and cover and os.path.isfile(cover):
        return upload_cover(args.base_url, args.api_key, cover, store_type)

    return cover if isinstance(cover, str) and cover else None


def meta_value(meta: dict[str, Any], key: str, default: Any = MISSING) -> Any:
    if key in meta:
        return meta[key]
    return default


def build_payload(markdown_text: str, args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    meta, body = parse_front_matter(markdown_text)
    is_update = args.article_id is not None

    title = meta.get("title")
    if not title:
        title, body = extract_title_from_body(body)

    if not title:
        die("Missing title. Set front matter 'title' or start the body with a single H1.")

    body = strip_matching_title_heading(body, str(title))
    if not body.strip():
        die("Article content is empty after parsing Markdown.")

    body = replace_local_markdown_images(
        body,
        args.markdown_file,
        args.base_url,
        args.api_key,
        meta,
    )

    if args.publish and args.draft:
        die("Use only one of --publish or --draft.")

    view_status_explicit = False
    if args.publish:
        view_status = True
        view_status_explicit = True
    elif args.draft:
        view_status = False
        view_status_explicit = True
    elif "viewStatus" in meta:
        view_status = bool(meta.get("viewStatus"))
        view_status_explicit = True
    elif not is_update:
        view_status = False
        view_status_explicit = True
    else:
        view_status = None

    cover = resolve_cover(meta, args)

    payload: dict[str, Any] = {
        "title": str(title),
        "content": body.strip(),
    }

    sort_id = meta.get("sortId")
    sort_name = meta.get("sort") or meta.get("sortName")
    label_id = meta.get("labelId")
    label_name = meta.get("label") or meta.get("labelName")

    if sort_id is not None:
        payload["sortId"] = sort_id
    elif sort_name:
        payload["sortName"] = sort_name
    elif not is_update:
        die("Missing category. Provide front matter 'sort' or 'sortId'.")

    if label_id is not None:
        payload["labelId"] = label_id
    elif label_name:
        payload["labelName"] = label_name
    elif not is_update:
        die("Missing label. Provide front matter 'label' or 'labelId'.")

    if cover is not None:
        payload["cover"] = cover

    video_url = meta_value(meta, "video")
    if video_url is not MISSING:
        payload["videoUrl"] = video_url

    if view_status_explicit:
        payload["viewStatus"] = view_status

    comment_status = meta_value(meta, "commentStatus", True if not is_update else MISSING)
    if comment_status is not MISSING:
        payload["commentStatus"] = bool(comment_status)

    recommend_status = meta_value(meta, "recommendStatus", False if not is_update else MISSING)
    if recommend_status is not MISSING:
        payload["recommendStatus"] = bool(recommend_status)

    submit_default = bool(view_status) if view_status_explicit else (False if not is_update else MISSING)
    submit_to_search = meta_value(meta, "submitToSearchEngine", submit_default)
    if submit_to_search is not MISSING:
        payload["submitToSearchEngine"] = bool(submit_to_search)

    password = meta_value(meta, "password")
    tips = meta_value(meta, "tips")
    if view_status is False:
        if password is MISSING or not isinstance(password, str) or not password.strip():
            password = f"draft-{uuid.uuid4().hex[:8]}"
        if tips is MISSING or not isinstance(tips, str) or not tips.strip():
            tips = "自动保存的草稿预览"
    if password is not MISSING:
        payload["password"] = password
    if tips is not MISSING:
        payload["tips"] = tips

    skip_ai_translation = meta_value(meta, "skipAiTranslation", False)
    if skip_ai_translation is not MISSING:
        payload["skipAiTranslation"] = bool(skip_ai_translation)

    pending_translation_language = meta_value(meta, "pendingTranslationLanguage")
    pending_translation_title = meta_value(meta, "pendingTranslationTitle")
    pending_translation_content = meta_value(meta, "pendingTranslationContent")
    if pending_translation_language is not MISSING:
        payload["pendingTranslationLanguage"] = pending_translation_language
    if pending_translation_title is not MISSING:
        payload["pendingTranslationTitle"] = pending_translation_title
    if pending_translation_content is not MISSING:
        payload["pendingTranslationContent"] = pending_translation_content

    pay_type = meta_value(meta, "payType")
    pay_amount = meta_value(meta, "payAmount")
    free_percent = meta_value(meta, "freePercent")
    if pay_type is not MISSING:
        payload["payType"] = pay_type
    if pay_amount is not MISSING:
        payload["payAmount"] = pay_amount
    if free_percent is not MISSING:
        payload["freePercent"] = free_percent

    if args.article_id is not None:
        payload["id"] = args.article_id

    if payload.get("viewStatus") is False and (not payload.get("password") or not payload.get("tips")):
        die("Draft/private article requires both 'password' and 'tips'.")

    return {key: value for key, value in payload.items() if value is not None}, meta


def main() -> None:
    configure_stdio()
    args = parse_args()
    args.base_url = normalize_base_url(str(args.base_url or ""))

    if not args.base_url:
        die("Missing --base-url or POETIZE_BASE_URL.")
    if not args.api_key:
        die("Missing --api-key or POETIZE_API_KEY.")

    try:
        brief = load_json_object(args.brief_file, label="Brief file")

        with open(args.markdown_file, "r", encoding="utf-8") as handle:
            markdown_text = handle.read()

        payload, meta = build_payload(markdown_text, args)
        payload = apply_article_strategy(
            brief,
            payload,
            is_update=args.article_id is not None,
            cli_publish=args.publish,
            cli_draft=args.draft,
        )
        payload = ensure_taxonomy_ready(payload, meta, args)
        payload = ensure_payment_plugin_ready(payload, meta, args)
        if args.print_payload:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        endpoint = "/api/api/article/updateAsync" if args.article_id is not None else "/api/api/article/createAsync"
        response = request_json("POST", f"{args.base_url.rstrip('/')}{endpoint}", args.api_key, payload)

        if response.get("code") != 200:
            die(json.dumps(response, ensure_ascii=False, indent=2))

        if not args.wait:
            print(json.dumps(response, ensure_ascii=False, indent=2))
            return

        task_id = extract_task_id(response)
        if not task_id:
            die("Async article API did not return a taskId.")

        final_response = poll_task(args.base_url, args.api_key, task_id, args.poll_interval, args.timeout)
        final_data = final_response.get("data")
        if isinstance(final_data, dict) and final_data.get("status") == "failed":
            die(json.dumps(final_response, ensure_ascii=False, indent=2))

        print(json.dumps(final_response, ensure_ascii=False, indent=2))
    except StrategyValidationError as exc:
        die(exc.render())


if __name__ == "__main__":
    main()
