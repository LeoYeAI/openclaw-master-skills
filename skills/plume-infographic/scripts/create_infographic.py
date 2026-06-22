#!/usr/bin/env python3
"""
Infographic creation script
Subcommands:
  create   -- Create infographic task and synchronously wait for result (returns local image path, agent can continue with subsequent operations)
  transfer -- Transfer local file to R2

All commands output JSON format for Agent parsing.
"""

import argparse
import json
import os
import ssl
import struct
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Import plume_api module (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plume_api
import action_log

# Result image download directory (under OpenClaw allowed media directory)
MEDIA_DIR = Path.home() / ".openclaw" / "media" / "plume"

# --- Circuit breaker (based on action_log, no separate file, agent cannot bypass) ---
CIRCUIT_BREAKER_WINDOW = 600   # 10-minute window
CIRCUIT_BREAKER_THRESHOLD = 2  # >= 2 failures within window triggers circuit breaker
FAIL_STATUSES = {"failed", "timeout", "cancelled"}


def _check_circuit_breaker(channel: str | None) -> str | None:
    """Count recent failures from action_log, trigger circuit breaker if threshold reached"""
    entries = action_log.read_log(channel or "")
    cutoff = time.time() - CIRCUIT_BREAKER_WINDOW
    recent_fails = [
        e for e in entries
        if e.get("status") in FAIL_STATUSES
        and e.get("completed_at", e.get("created_at", 0)) > cutoff
    ]
    if len(recent_fails) >= CIRCUIT_BREAKER_THRESHOLD:
        task_ids = [e.get("task_id", "?") for e in recent_fails]
        return (
            f"Circuit breaker: {len(recent_fails)} task failures in the last "
            f"{CIRCUIT_BREAKER_WINDOW // 60} minutes "
            f"(task_ids: {', '.join(task_ids)}). "
            f"Please wait {CIRCUIT_BREAKER_WINDOW // 60} minutes before retrying, "
            f"or contact admin to investigate backend issues."
        )
    return None


def log(msg: str):
    """Output debug log to stderr (does not affect stdout JSON output)"""
    print(f"[plume-infographic] {msg}", file=sys.stderr, flush=True)


def output(data: dict):
    """Output JSON result to stdout"""
    print(json.dumps(data, ensure_ascii=False))


# --- transfer subcommand ---

def _get_image_dimensions(file_path: str) -> tuple[int, int] | None:
    """Read local image width/height (supports JPEG/PNG/GIF/BMP/WebP), pure stdlib implementation"""
    try:
        with open(file_path, "rb") as f:
            header = f.read(32)
            if len(header) < 8:
                return None

            # PNG: 8-byte signature, then IHDR chunk with width/height at offset 16
            if header[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", header[16:24])
                return (w, h)

            # GIF: "GIF87a" or "GIF89a", width/height at offset 6 (little-endian)
            if header[:6] in (b"GIF87a", b"GIF89a"):
                w, h = struct.unpack("<HH", header[6:10])
                return (w, h)

            # BMP: "BM", width/height at offset 18 (little-endian)
            if header[:2] == b"BM":
                w, h = struct.unpack("<ii", header[18:26])
                return (abs(w), abs(h))

            # WebP: "RIFF....WEBPVP8"
            if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
                f.seek(0)
                data = f.read(64)
                if b"VP8 " in data:
                    idx = data.index(b"VP8 ") + 10
                    w = struct.unpack("<H", data[idx:idx + 2])[0] & 0x3FFF
                    h = struct.unpack("<H", data[idx + 2:idx + 4])[0] & 0x3FFF
                    return (w, h)
                if b"VP8L" in data:
                    idx = data.index(b"VP8L") + 9
                    bits = struct.unpack("<I", data[idx:idx + 4])[0]
                    w = (bits & 0x3FFF) + 1
                    h = ((bits >> 14) & 0x3FFF) + 1
                    return (w, h)

            # JPEG: SOI marker 0xFFD8
            if header[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2:
                        return None
                    if marker[0] != 0xFF:
                        return None
                    m = marker[1]
                    # SOF markers: C0-C3, C5-C7, C9-CB, CD-CF
                    if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                             0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        f.read(3)  # length(2) + precision(1)
                        h, w = struct.unpack(">HH", f.read(4))
                        return (w, h)
                    # skip this segment
                    length_data = f.read(2)
                    if len(length_data) < 2:
                        return None
                    length = struct.unpack(">H", length_data)[0]
                    f.seek(length - 2, 1)

    except Exception:
        return None
    return None


def cmd_transfer(args):
    """Upload local file to R2 (for reference image upload)"""
    local_file = args.file

    if not local_file:
        output({"success": False, "error": "Must specify --file parameter"})
        return

    if local_file.startswith("file://"):
        local_file = local_file[7:]

    if not os.path.exists(local_file):
        output({"success": False, "error": f"File not found: {local_file}"})
        return

    # Read local image dimensions
    dimensions = _get_image_dimensions(local_file)
    local_width = dimensions[0] if dimensions else None
    local_height = dimensions[1] if dimensions else None
    if dimensions:
        log(f"transfer: local dimensions {local_width}x{local_height}")

    log(f"transfer: uploading local file to R2, file={local_file}")
    upload_result = plume_api.upload_image(local_file)

    if not upload_result.get("success"):
        output({"success": False, "step": "upload_to_r2",
                "error": upload_result.get("message", "R2 upload failed")})
        return

    data = upload_result.get("data", {})
    output({
        "success": True,
        "image_url": data.get("file_url"),
        "file_key": data.get("file_key"),
        "file_size": data.get("file_size"),
        "width": data.get("width") or local_width,
        "height": data.get("height") or local_height,
    })


# --- create subcommand ---

def _is_local_path(url: str) -> bool:
    if not url:
        return False
    return url.startswith("file://") or url.startswith("/")


SUPPORTED_RATIOS = [
    ("16:9", 16 / 9),
    ("4:3", 4 / 3),
    ("1:1", 1 / 1),
    ("3:4", 3 / 4),
    ("9:16", 9 / 16),
]


def _infer_aspect_ratio(width: int, height: int) -> str:
    """Infer closest supported ratio from reference image dimensions"""
    if width <= 0 or height <= 0:
        return "3:4"
    actual = width / height
    best_ratio = "3:4"
    best_diff = float("inf")
    for label, value in SUPPORTED_RATIOS:
        diff = abs(actual - value)
        if diff < best_diff:
            best_diff = diff
            best_ratio = label
    log(f"Reference image {width}x{height} (ratio={actual:.3f}) -> inferred ratio {best_ratio}")
    return best_ratio


def _build_params_snapshot(args, mode: str) -> dict:
    """Extract creation parameter snapshot for retry restoration"""
    params = {}
    for key in ("article", "style_hint", "aspect_ratio", "locale"):
        val = getattr(args, key, None)
        if val is not None:
            params[key] = val
    if mode == "reference":
        for key in ("reference_type", "reference_image_urls",
                     "reference_topic", "reference_article"):
            val = getattr(args, key, None)
            if val is not None:
                params[key] = val
    if (args.count or 1) >= 2:
        params["count"] = args.count
        if args.child_reference_type:
            params["child_reference_type"] = args.child_reference_type
    return params


def _validate_params(args) -> str | None:
    """Parameter validation, returns error message or None"""
    # action mode: basic retry only needs action + last_task_id; reference retry also needs reference context
    if args.action:
        if not args.last_task_id:
            return "Retry action requires --last-task-id"
        if args.mode == "reference":
            if not args.reference_type:
                return "Reference image retry requires --reference-type"
            if not args.reference_image_urls:
                return "Reference image retry requires --reference-image-urls"
            if args.action == "switch_content":
                if args.reference_type == "style_transfer" and not args.reference_topic and not args.reference_article:
                    return "Style transfer content switch retry requires --reference-topic or --reference-article"
                if args.reference_type == "product_embed" and not args.reference_article:
                    return "Product embed content switch retry requires --reference-article"
                if args.reference_type == "content_rewrite" and not args.reference_article and not args.reference_topic:
                    return "Content rewrite content switch retry requires --reference-article or --reference-topic"
        return None

    if not args.mode:
        return "Must specify --mode (topic/article/reference)"

    if args.mode == "topic" and not args.topic:
        return "Topic mode requires --topic"
    if args.mode == "article" and not args.article:
        return "Article mode requires --article"
    if args.mode == "reference":
        if not args.reference_type:
            return "Reference mode requires --reference-type (sketch/style_transfer/product_embed/content_rewrite)"
        if not args.reference_image_urls:
            return "Reference mode requires --reference-image-urls"
        if args.reference_type == "style_transfer" and not args.reference_topic and not args.reference_article:
            return "Style transfer mode requires --reference-topic or --reference-article"
        if args.reference_type == "product_embed" and not args.reference_article:
            return "Product embed mode requires --reference-article"
        if args.reference_type == "content_rewrite" and not args.reference_article and not args.reference_topic:
            return "Content rewrite mode requires --reference-article or --reference-topic"

    count = args.count or 1
    if count >= 2 and args.mode == "reference":
        return "Batch infographics do not support reference mode yet, please use topic or article mode"

    return None


def _do_create(args) -> dict:
    """Core logic for creating infographic task, returns result dict (does not output directly)"""
    # reference mode parameter mapping: if article has value but reference_article is empty, auto-map
    if args.mode == "reference" and args.article and not args.reference_article:
        log("reference mode parameter mapping: article -> reference_article")
        args.reference_article = args.article

    # Parameter validation
    err = _validate_params(args)
    if err:
        return {"success": False, "error": err}

    # Process reference image URLs: reject local paths (must use transfer subcommand first)
    ref_urls = None
    if args.reference_image_urls:
        ref_urls = [u.strip() for u in args.reference_image_urls.split(",") if u.strip()]
        for url in ref_urls:
            if _is_local_path(url):
                return {"success": False, "error": f"Local file paths are not accepted in --reference-image-urls. Please upload via 'transfer --file {url}' first and use the returned remote URL."}

    # mode normalization: article content > 50 chars but mode=topic -> force article
    mode = args.mode
    if args.article and len(args.article.strip()) > 50 and mode == "topic":
        log("mode normalization: topic -> article (long-form content detected)")
        mode = "article"

    count = min(max(round(args.count or 1), 1), 10)
    is_batch = count >= 2

    # Aspect ratio inference: in reference mode, when user hasn't specified ratio, infer from reference image dimensions
    # In product_embed mode, reference image is the product itself, don't use its dimensions for output ratio, use default 3:4
    if args.aspect_ratio:
        aspect_ratio = args.aspect_ratio
    elif (mode == "reference"
          and getattr(args, "reference_type", None) != "product_embed"
          and args.reference_image_width and args.reference_image_height):
        aspect_ratio = _infer_aspect_ratio(args.reference_image_width, args.reference_image_height)
    else:
        aspect_ratio = "3:4"

    # Build generationConfig
    generation_config = {
        "responseModalities": ["IMAGE"],
        "imageConfig": {
            "aspectRatio": aspect_ratio,
            "image_size": "2K",
        },
    }

    # Build content
    if args.action:
        category = "infographic-batch" if is_batch else "infographic"
        content = {
            "mode": mode,
            "article": args.article,
            "reference_type": args.reference_type,
            "reference_image_urls": ref_urls,
            "reference_topic": args.reference_topic,
            "reference_article": args.reference_article,
            "action": args.action,
            "last_task_id": args.last_task_id,
            "locale": args.locale or "zh-CN",
            "generationConfig": generation_config,
        }
    elif is_batch:
        category = "infographic-batch"
        content = {
            "base_mode": mode,
            "count": count,
            "topic": args.topic,
            "article": args.article,
            "article_summary": args.article_summary,
            "style_hint": args.style_hint,
            "child_reference_type": args.child_reference_type or "style_transfer",
            "locale": args.locale or "zh-CN",
            "template_id": args.template_id,
            "generationConfig": generation_config,
        }
    else:
        category = "infographic"
        content = {
            "mode": mode,
            "topic": args.topic,
            "article": args.article,
            "article_summary": args.article_summary,
            "style_hint": args.style_hint,
            "locale": args.locale or "zh-CN",
            "template_id": args.template_id,
            "generationConfig": generation_config,
        }
        # Reference mode fields
        if mode == "reference":
            content["reference_type"] = args.reference_type
            content["reference_image_urls"] = ref_urls
            content["reference_topic"] = args.reference_topic
            content["reference_article"] = args.reference_article

    # Clean up None values
    content = {k: v for k, v in content.items() if v is not None}

    log(f"create: category={category}, mode={mode}, count={count}")

    # Generate title
    title = args.title
    if not title:
        def _label():
            if args.topic:
                return args.topic
            if args.article:
                text = args.article.strip().split("\n")[0][:15]
                return text + ("..." if len(args.article.strip()) > 15 else "")
            return None

        if args.action:
            title = f"Infographic-Retry"
        elif is_batch:
            title = f"Infographic-Batch-{_label() or 'conversion'}-{count}pcs"
        elif mode == "topic":
            title = f"Infographic-{args.topic}"
        elif mode == "article":
            title = f"Infographic-{_label() or 'text-conversion'}"
        elif mode == "reference":
            ref_names = {
                "sketch": "Sketch-to-Infographic",
                "style_transfer": "Style-Transfer",
                "product_embed": "Product-Embed",
                "content_rewrite": "Content-Rewrite",
            }
            title = f"Infographic-{ref_names.get(args.reference_type, 'reference-mode')}"

    result = plume_api.create_task(
        category=category,
        content=content,
        title=title,
    )

    log(f"create result: {json.dumps(result, ensure_ascii=False)[:500]}")

    if result.get("success"):
        task_data = result.get("data", {})
        task_id = task_data.get("id")

        # Write action log (regardless of whether channel is passed, must record for circuit breaker)
        if task_id:
            log_entry = {
                "task_id": task_id,
                "action": args.action,
                "last_task_id": args.last_task_id,
                "mode": mode,
                "params": _build_params_snapshot(args, mode),
            }
            action_log.append_entry(args.channel or "", log_entry)

        return {
            "success": True,
            "task_id": task_id,
            "category": category,
            "count": count,
            "status": task_data.get("status"),
            "credits_cost": task_data.get("credits_cost"),
        }
    else:
        return {
            "success": False,
            "code": result.get("code"),
            "error": result.get("message", "Task creation failed"),
        }


# --- Synchronous polling and download ---

SSL_CONTEXT = ssl.create_default_context()


def _poll_until_done(task_id: str, interval: int, timeout: int) -> dict:
    """Synchronously poll until task reaches terminal state or timeout"""
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            return {"timeout": True, "elapsed": elapsed}

        result = plume_api.get_task(task_id)
        if not result.get("success"):
            code = result.get("code", "")
            if code in ("NOT_FOUND", "UNAUTHORIZED", "FORBIDDEN"):
                return {"error": True, "code": code,
                        "message": result.get("message", "")}
            log(f"Query failed [{code}], retrying in {interval}s")
            time.sleep(interval)
            continue

        task = result.get("data", {})
        status = task.get("status", 0)

        if status >= 3:
            return {"done": True, "task": task, "status": status}

        log(f"Task {task_id} processing (status={status}, "
            f"elapsed={elapsed:.0f}s/{timeout}s)")
        time.sleep(interval)


def _download_file(url: str, output_path: str, timeout: int = 120) -> bool:
    """Download file to local"""
    req = urllib.request.Request(url, headers={"User-Agent": "Plume-Infographic/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
        if os.path.getsize(output_path) == 0:
            os.remove(output_path)
            return False
        return True
    except Exception as e:
        log(f"Download failed: {e}")
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass
        return False


def _extract_result_urls(task_result: dict) -> list[tuple[str, str]]:
    """Extract all result URLs from task result, returns [(url, media_type), ...]"""
    results = []
    if not isinstance(task_result, dict):
        return results

    parts = task_result.get("parts")
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict):
                url = part.get("imageUrl") or part.get("url")
                if url:
                    results.append((url, "image"))

    if not results:
        url = task_result.get("imageUrl") or task_result.get("url")
        if url:
            results.append((url, "image"))

    return results


def _download_results(task_id: str, task: dict) -> dict:
    """Download task result images to local, returns dict with path list"""
    task_result = task.get("result")
    if isinstance(task_result, str):
        try:
            task_result = json.loads(task_result)
        except json.JSONDecodeError:
            pass

    urls = _extract_result_urls(task_result)
    if not urls:
        return {"success": True, "images": [], "result_urls": []}

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    local_files = []
    result_urls = []
    for i, (url, _media_type) in enumerate(urls):
        suffix = ".jpg" if ".jpg" in url.lower() or ".jpeg" in url.lower() else ".png"
        idx_label = f"_{i + 1}" if len(urls) > 1 else ""
        local_file = str(MEDIA_DIR / f"result_{task_id}{idx_label}{suffix}")
        if _download_file(url, local_file):
            local_files.append(local_file)
            result_urls.append(url)
            log(f"Download complete ({i + 1}/{len(urls)}): {local_file}")
        else:
            log(f"Download failed ({i + 1}/{len(urls)}): {url}")

    return {"success": True, "images": local_files, "result_urls": result_urls}


# --- create subcommand ---

def cmd_create(args):
    """Create infographic task and synchronously wait for result"""
    # 0. Circuit breaker check: count recent failures from action_log, reject if threshold reached
    breaker_msg = _check_circuit_breaker(args.channel)
    if breaker_msg:
        log(f"Circuit breaker triggered: {breaker_msg}")
        output({
            "success": False,
            "code": "CIRCUIT_BREAKER",
            "error": breaker_msg,
        })
        return

    # 1. Create task
    create_result = _do_create(args)
    if not create_result.get("success"):
        output(create_result)
        return

    task_id = create_result["task_id"]
    log(f"Task created task_id={task_id}, starting synchronous wait...")

    # 2. Poll and wait
    poll_result = _poll_until_done(task_id, args.poll_interval, args.timeout)

    if poll_result.get("timeout"):
        output({
            "success": False,
            "task_id": task_id,
            "status": "timeout",
            "error": f"Wait timeout ({args.timeout}s), task is still processing",
            "credits_cost": create_result.get("credits_cost"),
        })
        return

    if poll_result.get("error"):
        output({
            "success": False,
            "task_id": task_id,
            "code": poll_result["code"],
            "error": poll_result.get("message", "Task query failed"),
        })
        return

    # 3. Handle terminal state
    task = poll_result["task"]
    status = poll_result["status"]

    if status != 3:
        status_map = {4: "Failed", 5: "Timeout", 6: "Cancelled"}
        status_text = status_map.get(status, f"Unknown({status})")
        error_info = task.get("result", "")

        status_key_map = {4: "failed", 5: "timeout", 6: "cancelled"}
        action_log.update_entry(args.channel or "", task_id, {
            "status": status_key_map.get(status, f"unknown_{status}"),
            "error": str(error_info) if error_info else None,
        })

        output({
            "success": False,
            "task_id": task_id,
            "status": status,
            "status_text": status_text,
            "error": str(error_info) if error_info else status_text,
        })
        return

    # 4. Success: download results
    dl = _download_results(task_id, task)

    action_log.update_entry(args.channel or "", task_id, {
        "status": "success",
        "result_url": dl["result_urls"][0] if dl["result_urls"] else None,
        "result_urls": dl["result_urls"],
        "local_file": dl["images"][0] if dl["images"] else None,
        "local_files": dl["images"],
    })

    output({
        "success": True,
        "task_id": task_id,
        "status": status,
        "images": dl["images"],
        "result_urls": dl["result_urls"],
        "count": len(dl["images"]),
        "credits_cost": create_result.get("credits_cost"),
    })


# --- CLI entry point ---

def main():
    parser = argparse.ArgumentParser(description="Plume Infographic Creation Script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # transfer
    p_transfer = subparsers.add_parser("transfer", help="Transfer local file to R2")
    p_transfer.add_argument("--file", required=True, help="Local file path")

    # create (sync: create + poll wait + download result)
    p_create = subparsers.add_parser("create", help="Create infographic task and synchronously wait for result")
    p_create.add_argument("--mode", choices=["topic", "article", "reference"], help="Infographic mode")
    p_create.add_argument("--topic", help="Topic (required for mode=topic)")
    p_create.add_argument("--article", help="Long-form content (required for mode=article)")
    p_create.add_argument("--article-summary", help="Article summary (optional)")
    p_create.add_argument("--style-hint", help="Style hint (max 10 chars, optional)")
    p_create.add_argument("--aspect-ratio", default=None,
                          help="Ratio: 3:4(default) / 4:3 / 1:1 / 16:9 / 9:16")
    p_create.add_argument("--locale", default=None, help="Language: zh-CN(default) / en-US / ja-JP etc.")
    p_create.add_argument("--count", type=int, default=1, help="Generation count, >=2 triggers batch mode")
    p_create.add_argument("--child-reference-type", choices=["style_transfer", "content_rewrite"],
                          help="Batch mode sub-task strategy (default style_transfer)")
    p_create.add_argument("--action",
                          choices=["repeat_last_task", "switch_style", "switch_content", "switch_all"],
                          help="Retry action")
    p_create.add_argument("--last-task-id", help="Previous task ID for retry")
    p_create.add_argument("--template-id", help="Specify template ID (optional)")
    p_create.add_argument("--reference-type",
                          choices=["sketch", "style_transfer", "product_embed", "content_rewrite"],
                          help="Reference image type (required for mode=reference)")
    p_create.add_argument("--reference-image-urls", help="Reference image URLs, comma-separated")
    p_create.add_argument("--reference-topic", help="New topic for reference mode")
    p_create.add_argument("--reference-article", help="New content for reference mode")
    p_create.add_argument("--reference-image-width", type=int, default=None, help="Reference image width (px), for auto aspect ratio inference")
    p_create.add_argument("--reference-image-height", type=int, default=None, help="Reference image height (px), for auto aspect ratio inference")
    p_create.add_argument("--channel", help="Channel identifier, for writing action log")
    p_create.add_argument("--title", help="Task title (optional)")
    p_create.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds (default 10)")
    p_create.add_argument("--timeout", type=int, default=1800, help="Max wait time in seconds (default 1800, i.e. 30 minutes)")

    args = parser.parse_args()

    commands = {
        "transfer": cmd_transfer,
        "create": cmd_create,
    }

    try:
        log(f"=== create_infographic.py {args.command} called, argv={sys.argv[1:]} ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
