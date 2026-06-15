#!/usr/bin/env python3
"""
LinkFoxAgent CLI - Cross-border e-commerce AI Agent.

Submit tasks to LinkFoxAgent and retrieve structured results.
Supports 41 tools for product research, competitor analysis, keyword tracking,
review insights, patent detection, and more.

Default mode is background: submit task and return messageId immediately,
so the caller can continue while the task runs (tasks typically take 1-5 min).
Use --poll to check the result later, or --wait to block until done.

Usage:
    linkfox.py "<task>"                       # Submit in background, return messageId (default)
    linkfox.py --wait "<task>"               # Submit and wait for result (blocking)
    linkfox.py --poll <messageId>             # Poll result for a messageId
    linkfox.py --timeout 600 --poll <id>     # Custom timeout when polling (seconds)
    linkfox.py --format json --poll <id>     # Output raw JSON

Environment:
    LINKFOXAGENT_API_KEY - Required API key for LinkFoxAgent
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


LINKFOXAGENT_BASE_URL = "https://agent-api.linkfox.com/"
SUBMIT_ENDPOINT = "chat/saveMessageForApi"
POLL_ENDPOINT = "chat/getMessageForApi"

TERMINAL_STATUSES = {"finished", "error", "cancel"}


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "Error: LINKFOXAGENT_API_KEY environment variable not set.\n"
            "Get your API key from: https://yxgb3sicy7.feishu.cn/wiki/IlkawdQP9ifKv9k22xcc7rjmnkb\n"
            "Then set it:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def api_request(endpoint: str, payload: dict) -> dict:
    """Make a POST request to the LinkFoxAgent API."""
    api_key = get_api_key()
    url = f"{LINKFOXAGENT_BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")

    req = Request(
        url,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFoxAgent-Skill/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def submit_task(text: str) -> dict:
    """Submit a task to LinkFoxAgent. Returns response with messageId."""
    return api_request(SUBMIT_ENDPOINT, {"text": text})


def poll_result(message_id: str, max_wait: int = 300, interval: int = 5) -> dict:
    """Poll for task result until terminal status or timeout."""
    elapsed = 0
    while elapsed < max_wait:
        result = api_request(POLL_ENDPOINT, {"id": message_id})

        if "error" in result:
            return result

        status = result.get("status", "")
        if status in TERMINAL_STATUSES:
            return result

        # Still working, wait and retry
        time.sleep(interval)
        elapsed += interval

        if elapsed % 30 == 0:
            print(f"... still working ({elapsed}s elapsed)", file=sys.stderr)

    return {"error": f"Timeout after {max_wait}s. messageId: {message_id}. Use --poll {message_id} to check later."}


def json_to_csv(parsed, result_name: str, result_index: int) -> str | None:
    """Convert a JSON result to a CSV file.

    Handles these payload shapes:
    - Object with 'columns' (field→title map) + data array in 'data', 'products',
      'items', etc.  columns[].title is used as Chinese column header.
    - Plain array of objects: headers derived from field names in first-appearance
      order; no Chinese title mapping.
    - Wrapper object whose first list-of-dicts value is the data array (fallback).

    If 'columns' is absent, raw English field names are used as headers.

    Returns the absolute path of the written CSV, or None if not a tabular shape.
    """
    col_map: dict[str, str] = {}
    ordered_fields: list[str] = []
    data = None

    if isinstance(parsed, dict):
        # Extract columns mapping when present (field → Chinese title)
        columns = parsed.get("columns")
        if isinstance(columns, list):
            col_map = {
                col["field"]: col["title"]
                for col in columns
                if isinstance(col, dict) and "field" in col and "title" in col
            }
            ordered_fields = [col["field"] for col in columns if isinstance(col, dict) and "field" in col]

        # Locate data array: prefer common keys first, then any list-of-dicts
        for candidate_key in ("data", "products", "items", "list"):
            v = parsed.get(candidate_key)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                data = v
                break
        if data is None:
            for v in parsed.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    data = v
                    break
        if data is None:
            return None

        # Append any extra fields from data rows not already in ordered_fields
        seen: set[str] = set(ordered_fields)
        for row in data:
            for key in row:
                if key not in seen:
                    ordered_fields.append(key)
                    seen.add(key)

    elif isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        data = parsed
        seen_b: set[str] = set()
        for row in data:
            for key in row:
                if key not in seen_b:
                    ordered_fields.append(key)
                    seen_b.add(key)

    else:
        return None

    if not data or not ordered_fields:
        return None

    # Ensure output directory exists next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    safe_name = "".join(c if (c.isalnum() or c in "-_") else "_" for c in result_name)
    filename = f"result_{result_index}_{safe_name}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        # Header: Chinese title if available, otherwise raw field name
        writer.writerow([col_map.get(field, field) for field in ordered_fields])
        for row in data:
            writer.writerow([row.get(field, "") for field in ordered_fields])

    return filepath


def format_result(result: dict) -> str:
    """Format a poll result as human-readable text.

    JSON results that contain both 'columns' and 'data' are automatically
    exported to a CSV file (with Chinese column headers from columns[].title).
    The output reports the local CSV path instead of dumping raw JSON, so the
    LLM can decide whether to read and forward the file to the user.
    """
    if "error" in result:
        return f"Error: {result['error']}"

    lines = []
    status = result.get("status", "unknown")
    lines.append(f"Status: {status}")

    share_url = result.get("shareUrl")
    if share_url:
        lines.append(f"ShareURL: {share_url}")

    reflection = result.get("reflection")
    if reflection:
        lines.append(f"\n{reflection}")

    results = result.get("results", [])
    for i, item in enumerate(results, 1):
        content_type = item.get("type", "unknown")
        content = item.get("content", "")
        name = item.get("name", f"result_{i}")

        if content_type == "html":
            lines.append(f"\n--- Result {i} (HTML URL) ---")
            lines.append(content)
        elif content_type == "json":
            try:
                parsed = json.loads(content) if isinstance(content, str) else content
            except (json.JSONDecodeError, TypeError):
                parsed = None

            if parsed is not None:
                # Save raw JSON first: {yyyymmddhh24}-{name_slug}.json
                script_dir = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.join(script_dir, "output")
                os.makedirs(output_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d%H")
                safe_name = "".join(c if (c.isalnum() or c in "-_") else "_" for c in name)
                json_filename = f"{ts}-{safe_name}.json"
                json_path = os.path.join(output_dir, json_filename)
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(parsed, jf, indent=2, ensure_ascii=False)

                # tablesListWorkbenches: multiple tables → multiple CSVs
                if isinstance(parsed, dict) and parsed.get("type") == "tablesListWorkbenches":
                    tables = parsed.get("tables", [])
                    lines.append(f"\n--- Result {i} (JSON → {len(tables)} CSV) ---")
                    lines.append(f"Name: {name}")
                    lines.append(f"JSON saved to: {json_path}")
                    for j, table in enumerate(tables, 1):
                        tname = table.get("name", f"{name}_table{j}")
                        csv_path = json_to_csv(table, tname, i * 100 + j)
                        if csv_path:
                            lines.append(f"CSV[{j}] ({tname}) saved to: {csv_path}")
                        else:
                            lines.append(f"CSV[{j}] ({tname}): 无法转换")
                else:
                    csv_path = json_to_csv(parsed, name, i)
                    if csv_path:
                        lines.append(f"\n--- Result {i} (JSON → CSV) ---")
                        lines.append(f"Name: {name}")
                        lines.append(f"JSON saved to: {json_path}")
                        lines.append(f"CSV saved to: {csv_path}")
                    else:
                        lines.append(f"\n--- Result {i} (JSON Data) ---")
                        lines.append(f"JSON saved to: {json_path}")
                        lines.append(json.dumps(parsed, indent=2, ensure_ascii=False))
            else:
                lines.append(f"\n--- Result {i} (JSON Data, unparseable) ---")
                lines.append(str(content))
        else:
            lines.append(f"\n--- Result {i} ({content_type}) ---")
            lines.append(str(content))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="LinkFoxAgent - Cross-border e-commerce AI Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("task", nargs="?", help="Task description to submit")
    parser.add_argument(
        "--stdin", action="store_true",
        help="Read task from stdin instead of positional argument (safe against shell injection)",
    )
    parser.add_argument(
        "--wait", action="store_true",
        help="Block until task completes and return the result (default: background, return messageId immediately)",
    )
    parser.add_argument(
        "--poll", dest="poll_id", metavar="MESSAGE_ID",
        help="Poll result for an existing messageId",
    )
    parser.add_argument(
        "--timeout", type=int, default=300,
        help="Max wait time in seconds (default: 300)",
    )
    parser.add_argument(
        "--interval", type=int, default=5,
        help="Poll interval in seconds (default: 5)",
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "text"], default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Mode: poll existing messageId
    if args.poll_id:
        result = poll_result(args.poll_id, max_wait=args.timeout, interval=args.interval)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_result(result))
        return

    # Require task for submit modes
    if args.stdin:
        task_text = sys.stdin.read().strip()
        if not task_text:
            parser.error("stdin was empty")
    elif args.task:
        task_text = args.task
    else:
        parser.error("task is required (or use --stdin or --poll MESSAGE_ID)")

    response = submit_task(task_text)
    if "error" in response:
        error_msg = response["error"]
        print(f"Error: {error_msg}", file=sys.stderr)
        if response.get("details"):
            print(f"Details: {response['details']}", file=sys.stderr)
        # HTTP 401/403 almost always means a bad or missing API key
        if "401" in error_msg or "403" in error_msg or "Unauthorized" in error_msg or "Forbidden" in error_msg:
            print(
                "\nHint: 任务发起失败，请检查 LINKFOXAGENT_API_KEY 是否正确。\n"
                "  当前值: " + (os.environ.get("LINKFOXAGENT_API_KEY") or "(未设置)") + "\n"
                "  获取 API Key: https://yxgb3sicy7.feishu.cn/wiki/IlkawdQP9ifKv9k22xcc7rjmnkb",
                file=sys.stderr,
            )
        sys.exit(1)

    message_id = response.get("messageId") or ""
    if not message_id:
        print(
            "Error: 任务发起失败，服务器未返回 messageId。\n"
            "请检查 LINKFOXAGENT_API_KEY 是否正确。\n"
            "  当前值: " + (os.environ.get("LINKFOXAGENT_API_KEY") or "(未设置)") + "\n"
            "  获取 API Key: https://yxgb3sicy7.feishu.cn/wiki/IlkawdQP9ifKv9k22xcc7rjmnkb\n"
            f"  服务器原始响应: {response}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Mode: background (default) — return messageId immediately so the caller can continue
    if not args.wait:
        print(json.dumps({"messageId": message_id}, indent=2))
        return

    # Mode: --wait — block until task completes
    print(f"Task submitted. messageId: {message_id}", file=sys.stderr)
    print("Waiting for result...", file=sys.stderr)

    result = poll_result(message_id, max_wait=args.timeout, interval=args.interval)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_result(result))

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
