#!/usr/bin/env python3
"""AI-Shifu Course CLI - Unified tool for course CRUD operations."""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key

# ── Constants ──────────────────────────────────────────────────────────────────
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

REGION_URLS = {
    "cn": "https://app.ai-shifu.cn",
    "global": "https://app.ai-shifu.com",
}


# ── Shared Infrastructure ──────────────────────────────────────────────────────
def load_env():
    """Load environment variables from the skill's .env file."""
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=False)


def save_env(token, base_url=None):
    """Persist token (and optionally base_url) to the skill's .env file."""
    env_path = str(ENV_FILE)
    if not ENV_FILE.exists():
        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        ENV_FILE.touch(mode=0o600)
    set_key(env_path, "SHIFU_TOKEN", token)
    if base_url:
        set_key(env_path, "SHIFU_BASE_URL", base_url)
    os.chmod(env_path, 0o600)


def resolve_auth(args):
    """Resolve base_url and token from CLI args or .env, exit on failure."""
    base_url = getattr(args, "base_url", None) or os.environ.get("SHIFU_BASE_URL")
    if not base_url:
        print("Error: --base-url is required (or set SHIFU_BASE_URL in .env)")
        sys.exit(1)

    token = getattr(args, "token", None) or os.environ.get("SHIFU_TOKEN")
    if not token:
        print("Error: no token available. Run 'shifu-cli.py login' first, "
              "or use --token / set SHIFU_TOKEN in .env")
        sys.exit(1)

    return base_url.rstrip("/"), token


def api(base_url, token, method, path, **kwargs):
    """Make an API call, exit on error."""
    url = f"{base_url}/api/shifu{path}"
    headers = {"Cookie": f"token={token}", "Content-Type": "application/json"}
    kwargs.setdefault("timeout", 30)
    resp = getattr(requests, method)(url, headers=headers, **kwargs)
    if not resp.ok:
        print(f"API error: {method.upper()} {path} (HTTP {resp.status_code})")
        print(f"  Response: {resp.text[:500]}")
        sys.exit(1)
    data = resp.json()
    if data.get("code") != 0:
        print(f"API error: {method.upper()} {path}")
        print(f"  Response: {json.dumps(data, ensure_ascii=False)}")
        sys.exit(1)
    return data.get("data")


def api_safe(base_url, token, method, path, **kwargs):
    """Make an API call, return None on error instead of exiting."""
    url = f"{base_url}/api/shifu{path}"
    headers = {"Cookie": f"token={token}", "Content-Type": "application/json"}
    kwargs.setdefault("timeout", 30)
    try:
        resp = getattr(requests, method)(url, headers=headers, **kwargs)
        if not resp.ok:
            return None
        data = resp.json()
        if data.get("code") != 0:
            return None
        return data.get("data")
    except (requests.RequestException, json.JSONDecodeError):
        return None


def safe_join_path(base_dir, filename):
    """Safely join base_dir and filename, preventing path traversal attacks."""
    joined = os.path.realpath(os.path.join(base_dir, filename))
    base = os.path.realpath(base_dir)
    if not joined.startswith(base + os.sep) and joined != base:
        print(f"Warning: path traversal detected, rejecting: {filename}")
        return None
    return joined


def fmt_time(ts):
    """Format an ISO timestamp for display, return '' if missing."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts[:16] if len(ts) >= 16 else ts


# ── Login ──────────────────────────────────────────────────────────────────────
def _login_post(base_url, path, payload, error_prefix):
    """POST to a user-auth endpoint and return parsed JSON, exit on failure."""
    resp = requests.post(
        f"{base_url}{path}",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if not resp.ok:
        print(f"{error_prefix} (HTTP {resp.status_code}): {resp.text[:200]}")
        sys.exit(1)
    data = resp.json()
    if data.get("code") != 0:
        print(f"{error_prefix}: {data}")
        sys.exit(1)
    return data


def cmd_login(args):
    """SMS login and save token (non-interactive two-step flow)."""
    # Global region does not support SMS login via CLI
    if args.region == "global":
        print("Error: CLI login is not supported for the global region.")
        print("Please log in manually at https://app.ai-shifu.com,")
        print("then set SHIFU_TOKEN and SHIFU_BASE_URL in .env or use --token.")
        sys.exit(1)

    # Resolve base_url: --base-url > --region mapping > env
    base_url = args.base_url
    if not base_url and args.region:
        base_url = REGION_URLS.get(args.region)
    if not base_url:
        base_url = os.environ.get("SHIFU_BASE_URL", "")
    base_url = base_url.rstrip("/")
    if not base_url:
        print("Error: --region or --base-url is required for login")
        sys.exit(1)

    phone = args.phone
    if not phone:
        print("Error: --phone is required for login")
        sys.exit(1)

    sms_code = args.sms_code
    masked = phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone

    if sms_code:
        # Step 2: Verify code and save token
        print("Verifying code...")
        data = _login_post(base_url, "/api/user/verify_sms_code",
                           {"mobile": phone, "sms_code": sms_code}, "Verification failed")

        token = data.get("data")
        if not token:
            print(f"No token in response: {data}")
            sys.exit(1)
        # API may return token as a dict (e.g. {"token": "..."}) or a plain string
        if isinstance(token, dict):
            token = token.get("token", "")
        if not token:
            print(f"No token string found in response data: {data}")
            sys.exit(1)

        save_env(token, base_url)
        print(f"Login successful! Token saved to {ENV_FILE}")
    else:
        # Step 1: Send SMS code only, then exit
        print(f"Sending SMS code to {masked}...")
        _login_post(base_url, "/api/user/send_sms_code",
                    {"mobile": phone}, "Failed to send SMS")
        print(f"SMS code sent to {masked}. "
              f"Run again with --sms-code <code> to complete login.")


# ── List ───────────────────────────────────────────────────────────────────────
def cmd_list(args):
    """List all courses."""
    base_url, token = resolve_auth(args)
    result = api(base_url, token, "get", "/shifus")

    if not result:
        print("No courses found.")
        return

    courses = result if isinstance(result, list) else result.get("items", [])
    if not courses:
        print("No courses found.")
        return

    # Table output
    print(f"{'BID':<34} {'Name':<30} {'Status':<10} {'Updated':<18}")
    print("-" * 94)
    for c in courses:
        bid = c.get("bid", c.get("shifu_bid", ""))
        name = c.get("name", c.get("title", ""))[:28]
        status = c.get("status", "")
        updated = fmt_time(c.get("updated_at", ""))
        print(f"{bid:<34} {name:<30} {status:<10} {updated:<18}")

    print(f"\nTotal: {len(courses)} courses")


# ── Show ───────────────────────────────────────────────────────────────────────
def cmd_show(args):
    """Show course detail / outline tree / MDF content."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid
    outline_bid = args.outline_bid

    if outline_bid:
        # Show MDF content for a specific lesson
        result = api(base_url, token, "get",
                     f"/shifus/{shifu_bid}/outlines/{outline_bid}/mdflow")
        content = result.get("data", "") if isinstance(result, dict) else result
        revision = result.get("revision", "") if isinstance(result, dict) else ""
        if revision:
            print(f"# Revision: {revision}\n")
        print(content)
    else:
        # Show course detail + outline tree
        detail = api_safe(base_url, token, "get", f"/shifus/{shifu_bid}/detail")
        if detail:
            print(f"Course: {detail.get('name', '')}")
            print(f"BID:    {shifu_bid}")
            desc = detail.get("description", "")
            if desc:
                print(f"Desc:   {desc}")
            model = detail.get("model", "")
            if model:
                print(f"Model:  {model}")
            print()

        tree = api(base_url, token, "get", f"/shifus/{shifu_bid}/outlines")
        if not tree:
            print("No outlines found.")
            return

        def print_tree(items, indent=0):
            for item in items:
                prefix = "  " * indent
                bid = item.get("bid", "")
                name = item.get("name", "")
                print(f"{prefix}- [{bid}] {name}")
                children = item.get("children", [])
                if children:
                    print_tree(children, indent + 1)

        print("Outline tree:")
        print_tree(tree if isinstance(tree, list) else [tree])


# ── History ────────────────────────────────────────────────────────────────────
def cmd_history(args):
    """Show MDF revision history for a lesson."""
    base_url, token = resolve_auth(args)
    result = api(base_url, token, "get",
                 f"/shifus/{args.shifu_bid}/outlines/{args.outline_bid}/mdflow/history")

    if not result:
        print("No history found.")
        return

    items = result if isinstance(result, list) else result.get("items", [])
    for item in items:
        rev = item.get("revision", "")
        ts = fmt_time(item.get("created_at", ""))
        user = item.get("created_user_bid", "")
        print(f"  {rev}  {ts}  by {user}")


# ── Export ─────────────────────────────────────────────────────────────────────
def cmd_export(args):
    """Export a course to JSON via backend export API."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid

    # Backend export API returns a file download (not standard JSON envelope)
    url = f"{base_url}/api/shifu/shifus/{shifu_bid}/export"
    headers = {"Cookie": f"token={token}"}
    resp = requests.get(url, headers=headers, timeout=60)

    if resp.status_code != 200:
        print(f"Export failed (HTTP {resp.status_code})")
        try:
            print(f"  Response: {resp.json()}")
        except Exception:
            print(f"  Response: {resp.text[:200]}")
        sys.exit(1)

    if args.output:
        outpath = args.output
        os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)
        with open(outpath, "wb") as f:
            f.write(resp.content)
        # Count lessons from exported data
        try:
            data = resp.json()
            count = len(data.get("outline_items", []))
            print(f"Exported to {outpath} ({count} lessons)")
        except Exception:
            print(f"Exported to {outpath}")
    else:
        # Pretty-print to stdout
        try:
            data = resp.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            print(resp.text)


# ── Create ─────────────────────────────────────────────────────────────────────
def cmd_create(args):
    """Create a new empty course."""
    base_url, token = resolve_auth(args)
    result = api(base_url, token, "put", "/shifus",
                 json={"name": args.name,
                       "description": args.description or ""})
    bid = result.get("bid") or result.get("shifu_bid")
    print(f"Created course: {bid}")
    print(f"  Name: {args.name}")
    print(f"  URL:  {base_url}/shifu/{bid}")


# ── Update Meta ────────────────────────────────────────────────────────────────
def cmd_update_meta(args):
    """Update course metadata (name, description, system prompt, etc.)."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid

    # Fetch current detail to preserve unchanged fields
    current = api(base_url, token, "get", f"/shifus/{shifu_bid}/detail")

    system_prompt = current.get("system_prompt", "")
    if args.system_prompt_file:
        with open(args.system_prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()

    keywords = current.get("keywords", "")
    if isinstance(keywords, list):
        pass  # already a list
    elif isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    payload = {
        "name": args.name if args.name is not None else current.get("name", ""),
        "description": args.description if args.description is not None
                       else current.get("description", ""),
        "avatar": current.get("avatar", ""),
        "keywords": keywords,
        "model": current.get("model", ""),
        "temperature": current.get("temperature", 0.3),
        "system_prompt": system_prompt,
        "tts_enabled": current.get("tts_enabled", False),
        "tts_provider": current.get("tts_provider", "minimax"),
        "tts_model": current.get("tts_model", ""),
        "tts_voice_id": current.get("tts_voice_id", ""),
        "tts_speed": current.get("tts_speed", 1.0),
        "tts_pitch": current.get("tts_pitch", 0),
        "tts_emotion": current.get("tts_emotion", ""),
        "use_learner_language": current.get("use_learner_language", False),
    }
    price = current.get("price")
    if price and price > 0:
        payload["price"] = price

    api(base_url, token, "post", f"/shifus/{shifu_bid}/detail", json=payload)
    print(f"Updated metadata for {shifu_bid}")


# ── Add Chapter ────────────────────────────────────────────────────────────────
def cmd_add_chapter(args):
    """Add a new top-level chapter to a course."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid

    result = api(base_url, token, "put", f"/shifus/{shifu_bid}/outlines",
                 json={"name": args.name})
    outline_bid = result.get("bid") or result.get("outline_item_bid")
    if not outline_bid:
        print(f"Error: chapter created but response did not include a BID", file=sys.stderr)
        print(f"  Response: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    print(f"Created chapter: {outline_bid} ({args.name})")


# ── Add Lesson ─────────────────────────────────────────────────────────────────
def cmd_add_lesson(args):
    """Add a new lesson to a course."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid

    # Create outline
    outline_payload = {"name": args.name}
    if args.parent_bid:
        outline_payload["parent_bid"] = args.parent_bid

    result = api(base_url, token, "put", f"/shifus/{shifu_bid}/outlines",
                 json=outline_payload)
    outline_bid = result.get("bid") or result.get("outline_item_bid")
    parent_label = f" under {args.parent_bid}" if args.parent_bid else ""
    print(f"Created lesson: {outline_bid} ({args.name}){parent_label}")

    # Write MDF content if provided
    if args.mdf_file:
        with open(args.mdf_file, "r", encoding="utf-8") as f:
            content = f.read()
        api(base_url, token, "post",
            f"/shifus/{shifu_bid}/outlines/{outline_bid}/mdflow",
            json={"data": content})
        print(f"  MDF saved ({len(content)} chars)")


# ── Update Lesson ──────────────────────────────────────────────────────────────
def cmd_update_lesson(args):
    """Update MDF content for an existing lesson (with optimistic locking)."""
    base_url, token = resolve_auth(args)
    shifu_bid = args.shifu_bid
    outline_bid = args.outline_bid

    # Step 1: Get current revision for optimistic locking
    current = api(base_url, token, "get",
                  f"/shifus/{shifu_bid}/outlines/{outline_bid}/mdflow")
    base_revision = None
    if isinstance(current, dict):
        base_revision = current.get("revision")

    # Step 2: Read new content
    with open(args.mdf_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Step 3: POST with base_revision
    payload = {"data": content}
    if base_revision:
        payload["base_revision"] = base_revision

    api(base_url, token, "post",
        f"/shifus/{shifu_bid}/outlines/{outline_bid}/mdflow",
        json=payload)
    print(f"Updated lesson {outline_bid} ({len(content)} chars)")
    if base_revision:
        print(f"  Base revision: {base_revision}")


# ── Rename Lesson ──────────────────────────────────────────────────────────────
def cmd_rename_lesson(args):
    """Rename an existing lesson."""
    base_url, token = resolve_auth(args)
    api(base_url, token, "post",
        f"/shifus/{args.shifu_bid}/outlines/{args.outline_bid}",
        json={"name": args.name})
    print(f"Renamed lesson {args.outline_bid} to: {args.name}")


# ── Delete Lesson ──────────────────────────────────────────────────────────────
def cmd_delete_lesson(args):
    """Delete a lesson from a course."""
    base_url, token = resolve_auth(args)
    api(base_url, token, "delete",
        f"/shifus/{args.shifu_bid}/outlines/{args.outline_bid}")
    print(f"Deleted lesson {args.outline_bid}")


# ── Reorder ────────────────────────────────────────────────────────────────────
def cmd_reorder(args):
    """Reorder lessons in a course."""
    base_url, token = resolve_auth(args)
    bids = [b.strip() for b in args.order.split(",") if b.strip()]
    api(base_url, token, "patch",
        f"/shifus/{args.shifu_bid}/outlines/reorder",
        json={"order": bids})
    print(f"Reordered {len(bids)} lessons")


# ── Import ─────────────────────────────────────────────────────────────────────
def _import_flat(base_url, token, json_file, shifu_bid):
    """Import from flat JSON file (original shifu-api-import.py logic)."""
    with open(json_file, "r", encoding="utf-8") as f:
        import_data = json.load(f)

    shifu_info = import_data["shifu"]
    outline_items = import_data["outline_items"]

    # Create or reuse shifu
    if shifu_bid:
        print(f"Using existing shifu: {shifu_bid}")
    else:
        print(f"Creating new shifu: {shifu_info['title']}")
        result = api(base_url, token, "put", "/shifus",
                     json={"name": shifu_info["title"],
                           "description": shifu_info.get("description", "")})
        shifu_bid = result.get("bid") or result.get("shifu_bid")
        print(f"  Created shifu: {shifu_bid}")

    # Update shifu detail
    keywords = shifu_info.get("keywords", "")
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    detail_payload = {
        "name": shifu_info["title"],
        "description": shifu_info.get("description", ""),
        "avatar": shifu_info.get("avatar_res_bid", ""),
        "keywords": keywords,
        "model": shifu_info.get("llm", ""),
        "temperature": shifu_info.get("llm_temperature", 0.3),
        "system_prompt": shifu_info.get("llm_system_prompt", ""),
    }
    price = shifu_info.get("price")
    if price and price > 0:
        detail_payload["price"] = price
    detail_payload.update({
        "tts_enabled": False,
        "tts_provider": "minimax",
        "tts_model": "",
        "tts_voice_id": "",
        "tts_speed": 1.0,
        "tts_pitch": 0,
        "tts_emotion": "",
        "use_learner_language": False,
    })
    for attempt in range(1, 4):
        result = api_safe(base_url, token, "post", f"/shifus/{shifu_bid}/detail",
                          json=detail_payload)
        if result is not None:
            print("  Updated shifu detail")
            break
        if attempt < 3:
            print(f"  Warning: failed to update shifu detail (attempt {attempt}/3), retrying...")
            time.sleep(1)
        else:
            print("Error: failed to update shifu detail after 3 attempts")
            sys.exit(1)

    # Clean existing outlines (delete children first, then parents)
    tree = api_safe(base_url, token, "get", f"/shifus/{shifu_bid}/outlines")
    if tree and isinstance(tree, list):
        for item in tree:
            for child in item.get("children", []):
                if child.get("bid"):
                    result = api_safe(base_url, token, "delete",
                                      f"/shifus/{shifu_bid}/outlines/{child['bid']}")
                    if result is None:
                        print(f"Error: failed to delete child outline: {child['bid']}")
                        sys.exit(1)
            if item.get("bid"):
                result = api_safe(base_url, token, "delete",
                                  f"/shifus/{shifu_bid}/outlines/{item['bid']}")
                if result is None:
                    print(f"Error: failed to delete outline: {item.get('name', item['bid'])}")
                    sys.exit(1)
                print(f"  Deleted old outline: {item.get('name', item['bid'])}")

    # Separate parents (chapters) and children (lessons) for two-pass creation
    parents = []
    children = []
    for item in outline_items:
        if item.get("parent_bid"):
            children.append(item)
        else:
            parents.append(item)

    bid_map = {}  # old outline_item_bid -> new API bid
    created = []
    total = len(outline_items)
    count = 0

    # Phase 1: Create parent items (chapters)
    for item in parents:
        count += 1
        title = item["title"]
        content = item.get("content", "")
        old_bid = item.get("outline_item_bid", "")

        result = api(base_url, token, "put", f"/shifus/{shifu_bid}/outlines",
                     json={"name": title})
        new_bid = result.get("bid") or result.get("outline_item_bid")
        bid_map[old_bid] = new_bid
        print(f"  [{count}/{total}] Created: {title} ({new_bid})")

        if content:
            api(base_url, token, "post",
                f"/shifus/{shifu_bid}/outlines/{new_bid}/mdflow",
                json={"data": content})
            print(f"    MDF saved ({len(content)} chars)")

        created.append({"bid": new_bid, "title": title})
        time.sleep(0.3)

    # Phase 2: Create child items (lessons) with mapped parent_bid
    for item in children:
        count += 1
        title = item["title"]
        content = item.get("content", "")
        old_parent = item["parent_bid"]
        new_parent = bid_map.get(old_parent, old_parent)

        result = api(base_url, token, "put", f"/shifus/{shifu_bid}/outlines",
                     json={"name": title, "parent_bid": new_parent})
        new_bid = result.get("bid") or result.get("outline_item_bid")
        print(f"  [{count}/{total}] Created: {title} ({new_bid})")

        if content:
            api(base_url, token, "post",
                f"/shifus/{shifu_bid}/outlines/{new_bid}/mdflow",
                json={"data": content})
            print(f"    MDF saved ({len(content)} chars)")

        created.append({"bid": new_bid, "title": title})
        time.sleep(0.3)

    print(f"\nDone! Shifu: {shifu_bid}")
    print(f"  Course: {shifu_info['title']}")
    print(f"  Chapters: {len(parents)}, Lessons: {len(children)}")
    print(f"  URL: {base_url}/shifu/{shifu_bid}")
    return shifu_bid


def cmd_import(args):
    """Import a course from JSON file or course directory."""
    if args.new and args.shifu_bid:
        print("Error: omit <shifu_bid> when using --new")
        sys.exit(1)
    if not args.new and not args.shifu_bid:
        print("Error: provide <shifu_bid> or use --new")
        sys.exit(1)

    base_url, token = resolve_auth(args)
    shifu_bid = None if args.new else args.shifu_bid

    if args.course_dir:
        # Build JSON first, then import
        json_file = _build_import_json(
            course_dir=args.course_dir,
            title=getattr(args, "title", None),
            description=getattr(args, "description", None),
            keywords=getattr(args, "keywords", None),
            chapter_name=getattr(args, "chapter_name", None),
        )
        _import_flat(base_url, token, json_file, shifu_bid)
    elif args.json_file:
        _import_flat(base_url, token, args.json_file, shifu_bid)
    else:
        print("Error: provide --json-file or --course-dir")
        sys.exit(1)


# ── Build ──────────────────────────────────────────────────────────────────────
def _extract_lesson_title(content, filename):
    """Extract lesson_title from HTML comment block, fallback to filename."""
    match = re.search(r'lesson_title:\s*(.+)', content)
    if match:
        return match.group(1).strip()
    name = Path(filename).stem
    return name.replace("-", " ").title()


def _build_import_json(course_dir, title=None, description=None,
                       keywords=None, chapter_name=None, output_path=None):
    """Build import JSON from a local course directory. Returns the output file path."""
    lessons_dir = os.path.join(course_dir, "lessons")
    if not os.path.isdir(lessons_dir):
        print(f"Error: lessons directory not found: {lessons_dir}")
        sys.exit(1)

    # Read system prompt if exists
    llm_system_prompt = ""
    sys_prompt_path = os.path.join(course_dir, "system-prompt.md")
    if os.path.exists(sys_prompt_path):
        with open(sys_prompt_path, "r", encoding="utf-8") as f:
            llm_system_prompt = f.read().strip()
        print(f"Loaded system prompt ({len(llm_system_prompt)} chars)")

    # Scan lesson files
    lesson_files = sorted([
        f for f in os.listdir(lessons_dir)
        if f.startswith("lesson-") and f.endswith(".md")
    ])
    if not lesson_files:
        print(f"Error: no lesson-*.md files found in {lessons_dir}")
        sys.exit(1)

    shifu_bid = str(uuid.uuid4()).replace("-", "")

    # Determine title: explicit arg > README > directory name
    if not title:
        readme_path = os.path.join(course_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line.startswith("#"):
                title = first_line.lstrip("#").strip()
        if not title:
            title = Path(course_dir).name

    # Load chapter structure from structure.json if exists,
    # otherwise auto-create a single chapter wrapping all lessons
    structure_file = os.path.join(course_dir, "structure.json")
    if os.path.exists(structure_file):
        with open(structure_file, "r", encoding="utf-8") as f:
            chapter_defs = json.load(f).get("chapters", [])
    else:
        chapter_defs = None

    outline_items = []
    structure_chapters = []

    if chapter_defs:
        # Multi-chapter mode: use structure.json definitions
        for ch_idx, ch_def in enumerate(chapter_defs):
            ch_bid = str(uuid.uuid4()).replace("-", "")
            ch_title = ch_def["title"]

            # Chapter item (container, no MDF content)
            outline_items.append({
                "outline_item_bid": ch_bid,
                "title": ch_title,
                "type": 401,
                "hidden": 0,
                "parent_bid": "",
                "position": str(ch_idx),
                "prerequisite_item_bids": "",
                "llm": "",
                "llm_temperature": 0,
                "llm_system_prompt": "",
                "ask_enabled_status": 5101,
                "ask_llm": "",
                "ask_llm_temperature": 0.0,
                "ask_llm_system_prompt": "",
                "content": "",
            })

            lesson_children = []
            for ls_idx, ls_def in enumerate(ch_def.get("lessons", [])):
                ls_file = ls_def["file"]
                filepath = safe_join_path(lessons_dir, ls_file)
                if filepath is None:
                    continue
                if not os.path.exists(filepath):
                    print(f"Warning: file not found: {filepath}, skipping")
                    continue
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                item_bid = str(uuid.uuid4()).replace("-", "")
                ls_title = ls_def.get("title") or _extract_lesson_title(content, ls_file)

                outline_items.append({
                    "outline_item_bid": item_bid,
                    "title": ls_title,
                    "type": 401,
                    "hidden": 0,
                    "parent_bid": ch_bid,
                    "position": str(ls_idx),
                    "prerequisite_item_bids": "",
                    "llm": "",
                    "llm_temperature": 0,
                    "llm_system_prompt": llm_system_prompt,
                    "ask_enabled_status": 5101,
                    "ask_llm": "",
                    "ask_llm_temperature": 0.0,
                    "ask_llm_system_prompt": "",
                    "content": content,
                })

                lesson_children.append({
                    "bid": item_bid, "id": 0, "type": "outline",
                    "children": [], "child_count": 0,
                })

            structure_chapters.append({
                "bid": ch_bid, "id": 0, "type": "outline",
                "children": lesson_children,
                "child_count": len(lesson_children),
            })
    else:
        # Single-chapter mode: wrap all lessons under one chapter
        chapter_bid = str(uuid.uuid4()).replace("-", "")
        chapter_title = chapter_name or title

        # Chapter item (container, no MDF content)
        outline_items.append({
            "outline_item_bid": chapter_bid,
            "title": chapter_title,
            "type": 401,
            "hidden": 0,
            "parent_bid": "",
            "position": "0",
            "prerequisite_item_bids": "",
            "llm": "",
            "llm_temperature": 0,
            "llm_system_prompt": "",
            "ask_enabled_status": 5101,
            "ask_llm": "",
            "ask_llm_temperature": 0.0,
            "ask_llm_system_prompt": "",
            "content": "",
        })

        lesson_children = []
        for idx, filename in enumerate(lesson_files):
            filepath = safe_join_path(lessons_dir, filename)
            if filepath is None:
                continue
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            item_bid = str(uuid.uuid4()).replace("-", "")
            lesson_title = _extract_lesson_title(content, filename)

            outline_items.append({
                "outline_item_bid": item_bid,
                "title": lesson_title,
                "type": 401,
                "hidden": 0,
                "parent_bid": chapter_bid,
                "position": str(idx),
                "prerequisite_item_bids": "",
                "llm": "",
                "llm_temperature": 0,
                "llm_system_prompt": llm_system_prompt,
                "ask_enabled_status": 5101,
                "ask_llm": "",
                "ask_llm_temperature": 0.0,
                "ask_llm_system_prompt": "",
                "content": content,
            })

            lesson_children.append({
                "bid": item_bid, "id": 0, "type": "outline",
                "children": [], "child_count": 0,
            })

        structure_chapters.append({
            "bid": chapter_bid, "id": 0, "type": "outline",
            "children": lesson_children,
            "child_count": len(lesson_children),
        })

    import_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "shifu": {
            "shifu_bid": shifu_bid,
            "title": title,
            "keywords": keywords or "",
            "description": description or "",
            "avatar_res_bid": "",
            "llm": "",
            "llm_temperature": 0,
            "llm_system_prompt": llm_system_prompt,
            "ask_enabled_status": 5101,
            "ask_llm": "",
            "ask_llm_temperature": 0.0,
            "ask_llm_system_prompt": "",
        },
        "outline_items": outline_items,
        "structure": {
            "bid": shifu_bid,
            "id": 0,
            "type": "shifu",
            "children": structure_chapters,
            "child_count": len(structure_chapters),
        },
    }

    # Output
    if not output_path:
        output_path = os.path.join(course_dir, "shifu-import.json")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(import_data, f, ensure_ascii=False, indent=2)

    chapters = [i for i in outline_items if not i.get("parent_bid")]
    lessons = [i for i in outline_items if i.get("parent_bid")]
    print(f"Generated {output_path}")
    print(f"  Course: {title}")
    print(f"  Chapters: {len(chapters)}, Lessons: {len(lessons)}")
    print(f"  Shifu BID: {shifu_bid}")
    return output_path


def cmd_build(args):
    """Build import JSON from local course directory (no network needed)."""
    _build_import_json(
        course_dir=args.course_dir,
        title=args.title,
        description=args.description,
        keywords=args.keywords,
        chapter_name=args.chapter_name,
        output_path=args.output,
    )


# ── Publish / Archive / Unarchive ──────────────────────────────────────────────
def cmd_publish(args):
    """Publish a course."""
    base_url, token = resolve_auth(args)
    api(base_url, token, "post", f"/shifus/{args.shifu_bid}/publish", json={})
    print(f"Published: {args.shifu_bid}")


def cmd_archive(args):
    """Archive a course."""
    base_url, token = resolve_auth(args)
    api(base_url, token, "post", f"/shifus/{args.shifu_bid}/archive", json={})
    print(f"Archived: {args.shifu_bid}")


def cmd_unarchive(args):
    """Unarchive a course."""
    base_url, token = resolve_auth(args)
    api(base_url, token, "post", f"/shifus/{args.shifu_bid}/unarchive", json={})
    print(f"Unarchived: {args.shifu_bid}")


# ── CLI Entry Point ────────────────────────────────────────────────────────────
def build_parser():
    """Build and return the argument parser with all subcommands."""
    # Shared parent parser for --base-url and --token on every subcommand
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--base-url", default=None,
                               help="AI-Shifu base URL (or SHIFU_BASE_URL in .env)")
    parent_parser.add_argument("--token", default=None,
                               help="JWT token (or SHIFU_TOKEN in .env)")

    parser = argparse.ArgumentParser(
        prog="shifu-cli",
        description="AI-Shifu Course CLI - Unified tool for course CRUD operations",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── login ──
    p = sub.add_parser("login", parents=[parent_parser],
                       help="SMS login and save token")
    p.add_argument("--phone", required=True, help="Phone number for SMS login")
    p.add_argument("--sms-code", default=None,
                   help="SMS verification code (skip interactive input)")
    p.add_argument("--region", choices=["cn", "global"], default=None,
                   help="Region: cn (中国大陆) or global (非中国大陆)")

    # ── list ──
    sub.add_parser("list", parents=[parent_parser], help="List all courses")

    # ── show ──
    p = sub.add_parser("show", parents=[parent_parser],
                       help="Show course detail or lesson MDF content")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("outline_bid", nargs="?", default=None,
                   help="Outline BID (omit to show tree)")

    # ── history ──
    p = sub.add_parser("history", parents=[parent_parser],
                       help="Show MDF revision history")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("outline_bid", help="Outline BID")

    # ── export ──
    p = sub.add_parser("export", parents=[parent_parser],
                       help="Export course to JSON")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("-o", "--output", default=None, help="Output file (stdout if omitted)")

    # ── create ──
    p = sub.add_parser("create", parents=[parent_parser],
                       help="Create a new empty course")
    p.add_argument("--name", required=True, help="Course name")
    p.add_argument("--description", default=None, help="Course description")

    # ── update-meta ──
    p = sub.add_parser("update-meta", parents=[parent_parser],
                       help="Update course metadata")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("--name", default=None, help="New course name")
    p.add_argument("--description", default=None, help="New description")
    p.add_argument("--system-prompt-file", default=None,
                   help="File containing system prompt")

    # ── add-chapter ──
    p = sub.add_parser("add-chapter", parents=[parent_parser],
                       help="Add a new top-level chapter")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("--name", required=True, help="Chapter name")

    # ── add-lesson ──
    p = sub.add_parser("add-lesson", parents=[parent_parser],
                       help="Add a new lesson under a chapter")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("--name", required=True, help="Lesson name")
    p.add_argument("--mdf-file", default=None, help="MDF content file")
    p.add_argument("--parent-bid", required=True,
                   help="Parent chapter BID (use add-chapter to create one first)")

    # ── update-lesson ──
    p = sub.add_parser("update-lesson", parents=[parent_parser],
                       help="Update lesson MDF content")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("outline_bid", help="Outline BID")
    p.add_argument("--mdf-file", required=True, help="MDF content file")

    # ── rename-lesson ──
    p = sub.add_parser("rename-lesson", parents=[parent_parser],
                       help="Rename a lesson")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("outline_bid", help="Outline BID")
    p.add_argument("--name", required=True, help="New lesson name")

    # ── delete-lesson ──
    p = sub.add_parser("delete-lesson", parents=[parent_parser],
                       help="Delete a lesson")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("outline_bid", help="Outline BID")

    # ── reorder ──
    p = sub.add_parser("reorder", parents=[parent_parser],
                       help="Reorder lessons")
    p.add_argument("shifu_bid", help="Course BID")
    p.add_argument("--order", required=True,
                   help="Comma-separated list of outline BIDs in desired order")

    # ── import ──
    p = sub.add_parser("import", parents=[parent_parser],
                       help="Import a course from JSON file or course directory")
    p.add_argument("shifu_bid", nargs="?", default=None,
                   help="Existing course BID (omit with --new to create)")
    p.add_argument("--new", action="store_true",
                   help="Create a new course instead of updating")
    p.add_argument("--json-file", default=None, help="Flat import JSON file")
    p.add_argument("--course-dir", default=None,
                   help="Course directory (builds JSON then imports)")
    p.add_argument("--title", default=None,
                   help="Course title (only with --course-dir)")
    p.add_argument("--description", default=None,
                   help="Course description (only with --course-dir)")
    p.add_argument("--keywords", default=None,
                   help="Keywords, comma-separated (only with --course-dir)")
    p.add_argument("--chapter-name", default=None,
                   help="Chapter name (only with --course-dir)")

    # ── build ──
    p = sub.add_parser("build", help="Build import JSON from local course directory")
    p.add_argument("--course-dir", required=True, help="Course directory path")
    p.add_argument("-o", "--output", default=None,
                   help="Output file (default: <course-dir>/shifu-import.json)")
    p.add_argument("--title", default=None, help="Course title")
    p.add_argument("--chapter-name", default=None,
                   help="Chapter name (default: same as course title)")
    p.add_argument("--description", default=None, help="Course description")
    p.add_argument("--keywords", default=None, help="Keywords (comma-separated)")

    # ── publish ──
    p = sub.add_parser("publish", parents=[parent_parser],
                       help="Publish a course")
    p.add_argument("shifu_bid", help="Course BID")

    # ── archive ──
    p = sub.add_parser("archive", parents=[parent_parser],
                       help="Archive a course")
    p.add_argument("shifu_bid", help="Course BID")

    # ── unarchive ──
    p = sub.add_parser("unarchive", parents=[parent_parser],
                       help="Unarchive a course")
    p.add_argument("shifu_bid", help="Course BID")

    return parser


def main():
    load_env()

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "login": cmd_login,
        "list": cmd_list,
        "show": cmd_show,
        "history": cmd_history,
        "export": cmd_export,
        "create": cmd_create,
        "update-meta": cmd_update_meta,
        "add-chapter": cmd_add_chapter,
        "add-lesson": cmd_add_lesson,
        "update-lesson": cmd_update_lesson,
        "rename-lesson": cmd_rename_lesson,
        "delete-lesson": cmd_delete_lesson,
        "reorder": cmd_reorder,
        "import": cmd_import,
        "build": cmd_build,
        "publish": cmd_publish,
        "archive": cmd_archive,
        "unarchive": cmd_unarchive,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
