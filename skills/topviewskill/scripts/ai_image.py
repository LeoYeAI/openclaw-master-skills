#!/usr/bin/env python3
"""Generate images or edit existing images using Topview Common Task APIs.

## AGENT INSTRUCTIONS — READ FIRST
- Default workflow: ALWAYS use `run` (submit + auto-poll).
  Do NOT ask the user to run query manually.
- Only use `query` when `run` has already timed out and a taskId exists,
  or when the user explicitly provides a taskId to resume.
- When using `query`, keep polling (default timeout=600s) until
  status is 'success' or 'fail'. Do NOT stop after a single check.
- Never hand a pending taskId back to the user and say "check it later".
  Always poll to completion within the timeout window.

Supported task types:
    text2image   Text-to-Image  — generate images from a text prompt
    image_edit   Image Edit     — edit images with prompt + reference images

Subcommands:
    run           Submit task AND poll until done — DEFAULT, use this first
    submit        Submit only, print taskId, exit — use for parallel batch jobs
    query         Poll an existing taskId until done (or timeout) — use for recovery
    list-models   Show supported models and parameter constraints
    estimate-cost Estimate credit cost before running

Usage:
    python ai_image.py run  --type text2image --model "Seedream 5.0" --prompt "..." [options]
    python ai_image.py run  --type image_edit --model "Kontext-Pro" --prompt "..." --input-images file1 [options]
    python ai_image.py submit --type <text2image|image_edit> [task-specific options]
    python ai_image.py query  --type <text2image|image_edit> --task-id <taskId> [options]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

TASK_TYPES = ("text2image", "image_edit")

ENDPOINTS = {
    "text2image": {
        "submit": "/v1/common_task/text2image/task/submit",
        "query": "/v1/common_task/text2image/task/query",
    },
    "image_edit": {
        "submit": "/v1/common_task/image_edit/task/submit",
        "query": "/v1/common_task/image_edit/task/query",
    },
}

DEFAULT_TIMEOUT = 300
DEFAULT_INTERVAL = 3

# ---------------------------------------------------------------------------
# Model constraints
# Each entry: { "aspectRatio": list, "resolution": list|None, "maxImages": int }
#   resolution=None means the model does NOT support resolution (do not send).
#   resolution=[...] means the parameter is required.
# ---------------------------------------------------------------------------

TEXT2IMAGE_MODELS = {
    "Nano Banana 2":   {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9", "2:3", "3:2", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"], "resolution": ["512p", "1K", "2K", "4K"]},
    "Nano Banana Pro":  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": ["1K", "2K", "4K"]},
    "Nano Banana":      {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": None},
    "Seedream 5.0":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                  "resolution": ["2K"]},
    "Seedream 4.5":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                  "resolution": ["2K", "4K"]},
    "Seedream 4.0":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                  "resolution": ["1K", "2K", "4K"]},
    "Grok Image Pro":   {"aspectRatio": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "2:1", "1:2", "20:9", "9:20", "19.5:9", "9:19.5"],  "resolution": ["1K", "2K"]},
    "Grok Image":       {"aspectRatio": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "2:1", "1:2", "20:9", "9:20", "19.5:9", "9:19.5"],  "resolution": ["1K", "2K"]},
    "GPT Image 1.5":    {"aspectRatio": ["3:2", "1:1", "2:3"],                                                                                  "resolution": None},
    "Kontext-Pro":      {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": None},
    "Imagen 4":         {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": None},
}

IMAGE_EDIT_MODELS = {
    "Nano Banana 2":   {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "2:3", "3:2", "5:4", "4:5", "21:9", "4:1", "1:4", "8:1", "1:8"], "resolution": ["512p", "1K", "2K", "4K"], "maxImages": 14},
    "Nano Banana Pro":  {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": ["1K", "2K", "4K"],       "maxImages": 6},
    "Nano Banana":      {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": None,                     "maxImages": 6},
    "Seedream 5.0":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                          "resolution": ["2K"],                   "maxImages": 14},
    "Seedream 4.5":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                          "resolution": ["2K", "4K"],             "maxImages": 14},
    "Seedream 4.0":     {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9", "21:9"],                                                          "resolution": ["1K", "2K", "4K"],       "maxImages": 5},
    "Grok Image Pro":   {"aspectRatio": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "2:1", "1:2", "20:9", "9:20", "19.5:9", "9:19.5"],          "resolution": ["1K", "2K"],             "maxImages": 1},
    "Grok Image":       {"aspectRatio": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "2:1", "1:2", "20:9", "9:20", "19.5:9", "9:19.5"],          "resolution": ["1K", "2K"],             "maxImages": 1},
    "GPT Image 1.5":    {"aspectRatio": ["3:2", "1:1", "2:3"],                                                                                          "resolution": None,                     "maxImages": 8},
    "Kontext-Pro":      {"aspectRatio": ["auto", "9:16", "3:4", "1:1", "4:3", "16:9"],                                                                  "resolution": None,                     "maxImages": 1},
}

MODEL_REGISTRY = {"text2image": TEXT2IMAGE_MODELS, "image_edit": IMAGE_EDIT_MODELS}

# ---------------------------------------------------------------------------
# Pricing — credits per image (generateCount=1).
# Key: resolution string or "default" for models without resolution.
# totalCost = unitCost × generateCount
# ---------------------------------------------------------------------------

_PRICING = {
    "text2image": {
        "Nano Banana 2":   {"512p": 0.25, "1K": 0.40, "2K": 0.60, "4K": 0.85},
        "Nano Banana Pro":  {"1K": 0.80, "2K": 0.80, "4K": 1.40},
        "Nano Banana":      {"default": 0.30},
        "Seedream 5.0":     {"2K": 0.20},
        "Seedream 4.5":     {"2K": 0.20, "4K": 0.20},
        "Seedream 4.0":     {"1K": 0.15, "2K": 0.15, "4K": 0.15},
        "Grok Image Pro":   {"1K": 0.45, "2K": 0.45},
        "Grok Image":       {"1K": 0.15, "2K": 0.15},
        "GPT Image 1.5":    {"default": 2.00},
        "Kontext-Pro":      {"default": 0.50},
        "Imagen 4":         {"default": 0.50},
    },
    "image_edit": {
        "Nano Banana 2":   {"512p": 0.25, "1K": 0.40, "2K": 0.60, "4K": 0.85},
        "Nano Banana Pro":  {"1K": 0.80, "2K": 0.80, "4K": 1.40},
        "Nano Banana":      {"default": 0.30},
        "Seedream 5.0":     {"2K": 0.20},
        "Seedream 4.5":     {"2K": 0.20, "4K": 0.20},
        "Seedream 4.0":     {"1K": 0.15, "2K": 0.15, "4K": 0.15},
        "Grok Image Pro":   {"1K": 0.45, "2K": 0.45},
        "Grok Image":       {"1K": 0.15, "2K": 0.15},
        "GPT Image 1.5":    {"default": 2.00},
        "Kontext-Pro":      {"default": 0.50},
    },
}


def estimate_cost(task_type: str, model: str, resolution: str | None,
                  count: int = 1) -> float | None:
    """Return estimated total cost in credits, or None if model/params unknown."""
    prices = _PRICING.get(task_type, {}).get(model)
    if not prices:
        return None
    if resolution and resolution in prices:
        return round(prices[resolution] * count, 2)
    if "default" in prices:
        return round(prices["default"] * count, 2)
    return None


def validate_model_params(task_type: str, model: str, aspect_ratio: str | None,
                          resolution: str | None, quiet: bool) -> None:
    """Warn on stderr if parameters are incompatible with model constraints."""
    registry = MODEL_REGISTRY.get(task_type, {})
    if model not in registry:
        if not quiet:
            known = ", ".join(sorted(registry.keys()))
            print(
                f"Warning: unknown model '{model}' for {task_type}. "
                f"Known models: {known}",
                file=sys.stderr,
            )
        return

    spec = registry[model]

    if aspect_ratio and aspect_ratio not in spec["aspectRatio"]:
        if not quiet:
            print(
                f"Warning: model '{model}' supports aspectRatio "
                f"{spec['aspectRatio']}, got '{aspect_ratio}'.",
                file=sys.stderr,
            )

    if resolution and spec["resolution"] is None:
        if not quiet:
            print(
                f"Warning: model '{model}' does not support resolution "
                f"(got '{resolution}'). Do NOT send this parameter.",
                file=sys.stderr,
            )
    elif resolution and spec["resolution"] and resolution not in spec["resolution"]:
        if not quiet:
            print(
                f"Warning: model '{model}' supports resolution "
                f"{spec['resolution']}, got '{resolution}'.",
                file=sys.stderr,
            )
    elif not resolution and spec["resolution"] is not None:
        if not quiet:
            print(
                f"Warning: model '{model}' requires resolution "
                f"(one of {spec['resolution']}). Please provide --resolution.",
                file=sys.stderr,
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_file(client: TopviewClient, file_ref: str, quiet: bool) -> str:
    """If file_ref looks like a local path, upload it and return fileId."""
    return resolve_local_file(file_ref, quiet=quiet, client=client)


def build_text2image_body(args) -> dict:
    body = {
        "model": args.model,
        "prompt": args.prompt,
        "aspectRatio": args.aspect_ratio,
        "generateCount": args.count,
    }
    if args.resolution:
        body["resolution"] = args.resolution
    if args.board_id:
        body["boardId"] = args.board_id
    return body


def build_image_edit_body(args, client: TopviewClient) -> dict:
    body = {
        "model": args.model,
        "prompt": args.prompt,
        "aspectRatio": args.aspect_ratio,
        "generateCount": args.count,
    }
    if args.input_images:
        body["inputImageFileIds"] = [
            resolve_file(client, ref, args.quiet) for ref in args.input_images
        ]
    if args.resolution:
        body["resolution"] = args.resolution
    if args.board_id:
        body["boardId"] = args.board_id
    return body


def build_body(args, client: TopviewClient) -> dict:
    """Dispatch to the type-specific body builder, with model constraint checks."""
    validate_model_params(
        args.type, args.model,
        getattr(args, "aspect_ratio", None),
        getattr(args, "resolution", None),
        args.quiet,
    )
    if args.type == "text2image":
        return build_text2image_body(args)
    elif args.type == "image_edit":
        return build_image_edit_body(args, client)
    raise ValueError(f"Unknown type: {args.type}")


def do_submit(client: TopviewClient, task_type: str, body: dict, quiet: bool) -> str:
    """POST submit task, return taskId."""
    path = ENDPOINTS[task_type]["submit"]
    label = {"text2image": "text-to-image", "image_edit": "image-edit"}
    if not quiet:
        print(f"Submitting {label[task_type]} task...", file=sys.stderr)
    result = client.post(path, json=body)
    task_id = result["taskId"]
    if not quiet:
        print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
    return task_id


def do_poll(client: TopviewClient, task_type: str, task_id: str,
            timeout: float, interval: float, quiet: bool) -> dict:
    """Poll until status is terminal or timeout is exceeded."""
    path = ENDPOINTS[task_type]["query"]
    if not quiet:
        print(
            f"Polling task {task_id} (timeout={timeout}s, interval={interval}s)...",
            file=sys.stderr,
        )
    return client.poll_task(
        path,
        task_id,
        interval=interval,
        timeout=timeout,
        verbose=not quiet,
    )


def download_image(url: str, output: str, quiet: bool) -> None:
    """Download an image from URL to a local file."""
    import requests as req

    if not quiet:
        print(f"Downloading image to {output}...", file=sys.stderr)

    resp = req.get(url, stream=True)
    resp.raise_for_status()

    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    if not quiet:
        size_kb = os.path.getsize(output) / 1024
        print(f"Downloaded: {output} ({size_kb:.1f} KB)", file=sys.stderr)


def print_result(result: dict, args) -> None:
    """Print final result: image URLs by default, full JSON with --json."""
    images = result.get("images", [])

    if args.output_dir and images:
        os.makedirs(args.output_dir, exist_ok=True)
        for i, img in enumerate(images):
            if img.get("status") == "success" and img.get("filePath"):
                url = img["filePath"]
                ext = url.rsplit(".", 1)[-1].split("?")[0] if "." in url else "jpg"
                out_path = os.path.join(args.output_dir, f"image_{i+1}.{ext}")
                download_image(url, out_path, args.quiet)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        cost = result.get("costCredit", "N/A")
        print(f"status: {result.get('status')}  cost: {cost} credits")
        for i, img in enumerate(images):
            status = img.get("status", "unknown")
            url = img.get("filePath", "")
            err = img.get("errorMsg", "")
            if status == "success":
                dims = ""
                if img.get("width") and img.get("height"):
                    dims = f" ({img['width']}x{img['height']})"
                print(f"  [{i+1}] {url}{dims}")
            else:
                print(f"  [{i+1}] {status}: {err}")
    board_task_id = result.get("boardTaskId", "")
    board_id = result.get("boardId", "") or getattr(args, "board_id", "") or ""
    if board_task_id and board_id:
        print(f"  edit: https://www.topview.ai/board/{board_id}?boardResultId={board_task_id}")


# ---------------------------------------------------------------------------
# Argument definitions
# ---------------------------------------------------------------------------

def add_common_args(p):
    """Add arguments shared by all task types."""
    p.add_argument("--type", required=True, choices=TASK_TYPES,
                   help="Task type: text2image or image_edit")
    p.add_argument("--model", required=True,
                   help='Model display name, e.g. "Seedream 5.0", "Kontext-Pro"')
    p.add_argument("--prompt", required=True,
                   help="Text prompt describing the image to generate or the edit to apply")
    p.add_argument("--aspect-ratio", required=True,
                   help='Aspect ratio, e.g. "16:9", "1:1", "auto"')
    p.add_argument("--resolution", default=None,
                   help='Resolution: "512p", "1K", "2K", "4K" (model-dependent, some require it, some forbid it)')
    p.add_argument("--count", type=int, default=1,
                   help="Number of images to generate (1-4, default: 1)")
    p.add_argument("--board-id", default=None,
                   help="Board ID for task organization")


def add_image_edit_args(p):
    """Add image-edit specific arguments."""
    p.add_argument("--input-images", nargs="+", default=None,
                   help="Reference image fileIds or local paths for image editing")


def add_poll_args(p):
    """Add polling control arguments."""
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    """Add output/download arguments."""
    p.add_argument("--output-dir", default=None,
                   help="Download result images to this directory")
    p.add_argument("--json", action="store_true",
                   help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress status messages on stderr")


def validate_args(args, parser):
    """Validate type-specific required arguments."""
    if args.type == "image_edit":
        if not args.input_images:
            parser.error("--input-images is required for image_edit")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_list_models(args, parser):
    """Print supported models and their parameter constraints."""
    task_type = args.type
    registry = MODEL_REGISTRY.get(task_type, {})
    if not registry:
        print(f"No models registered for type '{task_type}'.")
        return

    if args.json:
        print(json_mod.dumps(registry, indent=2, ensure_ascii=False))
        return

    type_label = {"text2image": "Text-to-Image", "image_edit": "Image Edit"}
    print(f"\n{type_label.get(task_type, task_type)} — Supported Models\n")

    if task_type == "image_edit":
        print(f"{'Model':<22} {'Aspect Ratio':<45} {'Resolution':<22} {'Max Images'}")
        print("-" * 100)
        for name, spec in registry.items():
            ar = ", ".join(spec["aspectRatio"])
            res = ", ".join(spec["resolution"]) if spec["resolution"] else "N/A (forbidden)"
            mi = str(spec.get("maxImages", "N/A"))
            print(f"{name:<22} {ar:<45} {res:<22} {mi}")
    else:
        print(f"{'Model':<22} {'Aspect Ratio':<45} {'Resolution'}")
        print("-" * 80)
        for name, spec in registry.items():
            ar = ", ".join(spec["aspectRatio"])
            res = ", ".join(spec["resolution"]) if spec["resolution"] else "N/A (forbidden)"
            print(f"{name:<22} {ar:<45} {res}")
    print()


def cmd_estimate_cost(args, parser):
    """Print estimated cost for a given model + parameters."""
    cost = estimate_cost(args.type, args.model, args.resolution, args.count or 1)
    if cost is None:
        print(f"Cannot estimate cost for model '{args.model}' with given parameters.", file=sys.stderr)
        print("Use list-models to see available models, or check references/api-docs.md.", file=sys.stderr)
        sys.exit(1)
    count = args.count or 1
    unit = round(cost / count, 2)
    if args.json:
        print(json_mod.dumps({"type": args.type, "model": args.model,
                               "resolution": args.resolution,
                               "count": count, "unitCost": unit, "totalCost": cost}))
    else:
        print(f"type: {args.type}  model: {args.model}  "
              f"resolution: {args.resolution or 'default'}  count: {count}")
        print(f"estimated unit cost: {unit} credits")
        print(f"estimated total cost: {cost} credits")


def cmd_run(args, parser):
    """Submit task then poll until done — full flow (default)."""
    validate_args(args, parser)
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, args.type, body, args.quiet)
    result = do_poll(client, args.type, task_id, args.timeout, args.interval, args.quiet)
    print_result(result, args)


def cmd_submit(args, parser):
    """Submit task only — print taskId and exit immediately."""
    validate_args(args, parser)
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, args.type, body, args.quiet)
    print(task_id)


def cmd_query(args, parser):
    """Poll an existing task by taskId until done or timeout."""
    client = TopviewClient()
    try:
        result = do_poll(
            client, args.type, args.task_id,
            args.timeout, args.interval, args.quiet,
        )
        print_result(result, args)
    except TimeoutError as e:
        if not args.quiet:
            print(f"Timeout reached: {e}", file=sys.stderr)
            print("Fetching last known status...", file=sys.stderr)
        path = ENDPOINTS[args.type]["query"]
        last = client.get(path, params={"taskId": args.task_id})
        status = last.get("status", "unknown")
        task_id = last.get("taskId", args.task_id)
        if args.json:
            print(json_mod.dumps(last, indent=2, ensure_ascii=False))
        else:
            print(f"status: {status}  taskId: {task_id}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview AI Image — text-to-image and image editing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AGENT WORKFLOW RULES:
  1. ALWAYS start with `run` — it submits and polls automatically.
  2. Only use `query` if `run` timed out and you have a taskId to resume.
  3. `query` polls continuously (not once) until done or --timeout.
  4. NEVER hand a pending taskId back to the user — always poll to completion.

Task types:
  text2image  Text-to-Image  (model + prompt → images)
  image_edit  Image Edit     (model + prompt + reference images → edited images)

Examples:
  # List available models for a task type
  python ai_image.py list-models --type text2image

  # Text-to-image
  python ai_image.py run --type text2image --model "Seedream 5.0" \\
      --prompt "A futuristic city" --aspect-ratio "16:9" --resolution "2K" --count 2

  # Image editing
  python ai_image.py run --type image_edit --model "Kontext-Pro" \\
      --prompt "Change background to a beach" --aspect-ratio "auto" \\
      --input-images photo.jpg

  # Estimate cost
  python ai_image.py estimate-cost --type text2image --model "Seedream 5.0" \\
      --resolution "2K" --count 2

  # Query a timed-out task
  python ai_image.py query --type text2image --task-id <taskId>
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- run (default full flow) --
    p_run = sub.add_parser("run", help="[DEFAULT] Submit task and poll until done")
    add_common_args(p_run)
    add_image_edit_args(p_run)
    add_poll_args(p_run)
    add_output_args(p_run)

    # -- submit only --
    p_submit = sub.add_parser("submit", help="Submit task only, print taskId and exit")
    add_common_args(p_submit)
    add_image_edit_args(p_submit)
    add_output_args(p_submit)

    # -- query / poll existing task --
    p_query = sub.add_parser("query", help="Poll existing taskId until done or timeout")
    p_query.add_argument("--type", required=True, choices=TASK_TYPES,
                         help="Task type (needed to select correct query endpoint)")
    p_query.add_argument("--task-id", required=True,
                         help="taskId returned by 'submit' or a previous 'run'")
    add_poll_args(p_query)
    add_output_args(p_query)

    # -- list-models --
    p_list = sub.add_parser("list-models", help="Show supported models and parameter constraints")
    p_list.add_argument("--type", required=True, choices=TASK_TYPES,
                        help="Task type to list models for")
    p_list.add_argument("--json", action="store_true",
                        help="Output as JSON")

    # -- estimate-cost --
    p_cost = sub.add_parser("estimate-cost", help="Estimate credit cost before running a task")
    p_cost.add_argument("--type", required=True, choices=TASK_TYPES,
                        help="Task type")
    p_cost.add_argument("--model", required=True, help="Model display name")
    p_cost.add_argument("--resolution", default=None, help="Resolution (e.g. 1K, 2K, 4K)")
    p_cost.add_argument("--count", type=int, default=1, help="generateCount (1-4)")
    p_cost.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.subcommand == "run":
        cmd_run(args, p_run)
    elif args.subcommand == "submit":
        cmd_submit(args, p_submit)
    elif args.subcommand == "query":
        cmd_query(args, p_query)
    elif args.subcommand == "list-models":
        cmd_list_models(args, p_list)
    elif args.subcommand == "estimate-cost":
        cmd_estimate_cost(args, p_cost)


if __name__ == "__main__":
    main()
