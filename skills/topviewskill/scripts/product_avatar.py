#!/usr/bin/env python3
"""Product Avatar image replacement using Topview PA V3/V4 API.

## AGENT INSTRUCTIONS — READ FIRST
- Default workflow: ALWAYS use `run` (submit + auto-poll).
  Do NOT ask the user to run query manually.
- Only use `query` when `run` has already timed out and a taskId exists,
  or when the user explicitly provides a taskId to resume.
- When using `query`, keep polling (default timeout=600s) until
  status is 'success' or 'fail'. Do NOT stop after a single check.
- Never hand a pending taskId back to the user and say "check it later".
  Always poll to completion within the timeout window.

Subcommands:
    run              Submit task AND poll until done — DEFAULT, use this first
    submit           Submit only, print taskId, exit — use for parallel batch jobs
    query            Poll an existing taskId until done (or timeout) — use for recovery
    list-categories  List product avatar categories
    list-avatars     Browse public product avatar templates

Usage:
    python product_avatar.py run --product-image <fileId|path> --template-image <fileId|path> [options]
    python product_avatar.py submit --product-image <fileId|path> [options]
    python product_avatar.py query --task-id <taskId> [options]
    python product_avatar.py list-categories [--json]
    python product_avatar.py list-avatars [--gender female] [--category-ids id1,id2] [options]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

SUBMIT_PATH = "/v3/product_avatar/task/image_replace/submit"
QUERY_PATH = "/v3/product_avatar/task/image_replace/query"
PA_CATEGORY_PATH = "/v1/product_avatar/category/list"
PA_PUBLIC_AVATAR_PATH = "/v1/product_avatar/public_avatar/query"

VALID_MODES = ("auto", "manual")
VALID_KEEP_TARGETS = ("model", "product")
VALID_VERSIONS = ("v3", "v4")

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5

FIXED_COST = 0.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_file(client: TopviewClient, file_ref: str, quiet: bool) -> str:
    """If file_ref looks like a local path, upload it and return fileId."""
    return resolve_local_file(file_ref, quiet=quiet, client=client)


def build_body(args, client: TopviewClient) -> dict:
    """Build the submit-task request body from parsed args."""
    body = {}

    if args.product_image:
        body["productImageFileId"] = resolve_file(client, args.product_image, args.quiet)
    if args.product_image_no_bg:
        body["productImageWithoutBackgroundFileId"] = resolve_file(
            client, args.product_image_no_bg, args.quiet
        )
    if args.template_image:
        body["templateImageFileId"] = resolve_file(client, args.template_image, args.quiet)
    if args.avatar_id:
        body["avatarId"] = args.avatar_id
    if args.face_image:
        body["userFaceImageFileId"] = resolve_file(client, args.face_image, args.quiet)
    if args.prompt:
        body["imageEditPrompt"] = args.prompt
    if args.mode:
        body["generateImageMode"] = args.mode
    if args.keep_target:
        body["keepTarget"] = args.keep_target
    if args.version:
        body["version"] = args.version
    if args.location:
        body["location"] = json_mod.loads(args.location)
    if args.product_size is not None:
        body["productSize"] = args.product_size
    if args.project_id:
        body["projectId"] = args.project_id
    if args.board_id:
        body["boardId"] = args.board_id
    if args.notice_url:
        body["noticeUrl"] = args.notice_url

    return body


def do_submit(client: TopviewClient, body: dict, quiet: bool) -> str:
    """POST submit task, return taskId."""
    if not quiet:
        print("Submitting product avatar image-replace task...", file=sys.stderr)
    result = client.post(SUBMIT_PATH, json=body)
    task_id = result["taskId"]
    if not quiet:
        print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
    return task_id


def do_poll(client: TopviewClient, task_id: str, timeout: float, interval: float,
            quiet: bool) -> dict:
    """Poll until status is 'success' or 'fail', or timeout is exceeded."""
    if not quiet:
        print(
            f"Polling task {task_id} (timeout={timeout}s, interval={interval}s)...",
            file=sys.stderr,
        )
    return client.poll_task(
        QUERY_PATH,
        task_id,
        interval=interval,
        timeout=timeout,
        verbose=not quiet,
    )


def download_file(url: str, output: str, quiet: bool) -> None:
    """Download a file from URL to a local path."""
    import requests as req

    if not quiet:
        print(f"Downloading result to {output}...", file=sys.stderr)

    resp = req.get(url, stream=True)
    resp.raise_for_status()

    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    if not quiet:
        size_kb = os.path.getsize(output) / 1024
        print(f"Downloaded: {output} ({size_kb:.1f} KB)", file=sys.stderr)


def print_result(result: dict, args) -> None:
    """Print final result."""
    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = result.get("status", "unknown")
        cost = result.get("costCredit", FIXED_COST)
        print(f"status: {status}  cost: {cost} credits")

        result_url = result.get("finishedVideoUrl") or result.get("resultImageUrl") or ""
        if result_url:
            print(f"  result: {result_url}")
            if args.output and result_url:
                download_file(result_url, args.output, args.quiet)
    board_task_id = result.get("boardTaskId", "")
    board_id = result.get("boardId", "") or getattr(args, "board_id", "") or ""
    if board_task_id and board_id:
        print(f"  edit: https://www.topview.ai/board/{board_id}?boardResultId={board_task_id}")


# ---------------------------------------------------------------------------
# Argument definitions
# ---------------------------------------------------------------------------

def add_submit_args(p):
    """Add arguments used by 'submit' and 'run' subcommands."""
    p.add_argument("--product-image", default=None,
                   help="Product image fileId or local path")
    p.add_argument("--product-image-no-bg", default=None,
                   help="Product image (background removed) fileId or local path")
    p.add_argument("--template-image", default=None,
                   help="Template/model image fileId or local path")
    p.add_argument("--avatar-id", default=None,
                   help="Avatar ID (digital human)")
    p.add_argument("--face-image", default=None,
                   help="User face image fileId or local path")
    p.add_argument("--prompt", default=None,
                   help="Image edit prompt")
    p.add_argument("--mode", default=None, choices=VALID_MODES,
                   help="Generate image mode: auto or manual (default: auto)")
    p.add_argument("--keep-target", default=None, choices=VALID_KEEP_TARGETS,
                   help="Keep target: model (default) or product (only for auto mode)")
    p.add_argument("--version", default=None, choices=VALID_VERSIONS,
                   help="API version: v3 (default) or v4 (banana_pro, supports manual mode)")
    p.add_argument("--location", default=None,
                   help='Product coordinates as JSON 2D array, e.g. \'[[10.5, 20.0], [30.5, 40.0]]\'')
    p.add_argument("--product-size", type=int, default=None,
                   help="Product size (enum value)")
    p.add_argument("--project-id", default=None,
                   help="Project ID")
    p.add_argument("--board-id", default=None,
                   help="Board ID for task organization")
    p.add_argument("--notice-url", default=None,
                   help="Webhook URL for task completion notification")


def add_poll_args(p):
    """Add polling control arguments."""
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    """Add output/download arguments."""
    p.add_argument("--output", default=None,
                   help="Download result to this local path")
    p.add_argument("--json", action="store_true",
                   help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress status messages on stderr")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_run(args, parser):
    """Submit task then poll until done — full flow (default)."""
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, body, args.quiet)
    result = do_poll(client, task_id, args.timeout, args.interval, args.quiet)
    print_result(result, args)


def cmd_submit(args, parser):
    """Submit task only — print taskId and exit immediately."""
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, body, args.quiet)
    print(task_id)


def cmd_query(args, parser):
    """Poll an existing task by taskId until done or timeout."""
    client = TopviewClient()
    try:
        result = do_poll(
            client, args.task_id, args.timeout, args.interval, args.quiet,
        )
        print_result(result, args)
    except TimeoutError as e:
        if not args.quiet:
            print(f"Timeout reached: {e}", file=sys.stderr)
            print("Fetching last known status...", file=sys.stderr)
        last = client.get(QUERY_PATH, params={"taskId": args.task_id})
        status = last.get("status", "unknown")
        task_id = last.get("taskId", args.task_id)
        if args.json:
            print(json_mod.dumps(last, indent=2, ensure_ascii=False))
        else:
            print(f"status: {status}  taskId: {task_id}", file=sys.stderr)
        sys.exit(2)


def cmd_list_categories(args, parser):
    """List product avatar categories."""
    client = TopviewClient()
    result = client.get(PA_CATEGORY_PATH)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    categories = result if isinstance(result, list) else [result] if result else []
    if not args.quiet:
        print(f"Categories: {len(categories)}", file=sys.stderr)

    for c in categories:
        cid = c.get("categoryId", "")
        name = c.get("categoryName", "")
        print(f"{cid}\t{name}")


def cmd_list_avatars(args, parser):
    """Browse public product avatar templates with optional filters."""
    client = TopviewClient()
    params = {}

    if args.gender:
        params["gender"] = args.gender
    if args.category_ids:
        params["categoryIds"] = args.category_ids
    if args.ethnicity_ids:
        params["ethnicityIds"] = args.ethnicity_ids
    if args.sort:
        params["sortingType"] = args.sort
    if args.page:
        params["pageNo"] = str(args.page)
    if args.size:
        params["pageSize"] = str(args.size)

    result = client.get(PA_PUBLIC_AVATAR_PATH, params=params)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    avatars = result if isinstance(result, list) else result.get("records", result.get("data", []))
    if not isinstance(avatars, list):
        avatars = [avatars] if avatars else []

    if not args.quiet:
        print(f"Avatars: {len(avatars)}", file=sys.stderr)

    for a in avatars:
        aid = a.get("avatarId", "")
        gender = a.get("gender", "")
        img = a.get("avatarImagePath", "")
        subs = a.get("minSubsType", "")
        cats = a.get("avatarCategoryList", {})
        cat_name = cats.get("categoryName", "") if isinstance(cats, dict) else ""
        print(f"{aid}\t{gender}\t{cat_name}\t{subs}\t{img}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Product Avatar — replace product images in digital human scenes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AGENT WORKFLOW RULES:
  1. ALWAYS start with `run` — it submits and polls automatically.
  2. Only use `query` if `run` timed out and you have a taskId to resume.
  3. `query` polls continuously (not once) until done or --timeout.
  4. NEVER hand a pending taskId back to the user — always poll to completion.

Examples:
  # Browse available avatar templates
  python product_avatar.py list-categories
  python product_avatar.py list-avatars --gender female

  # Auto mode (model-priority)
  python product_avatar.py run \\
      --product-image product.png --template-image template.png \\
      --mode auto --keep-target model

  # With a public avatar (use avatarId from list-avatars)
  python product_avatar.py run \\
      --product-image product.png --avatar-id <avatarId>

  # Manual mode with V4 (banana_pro)
  python product_avatar.py run \\
      --product-image product.png --template-image template.png \\
      --mode manual --version v4 \\
      --location '[[10.5, 20.0], [30.5, 40.0]]'

  # With background-removed product image (from remove_bg.py)
  python product_avatar.py run \\
      --product-image-no-bg <bgRemovedImageFileId> \\
      --avatar-id <avatarId>

  # Batch: submit without waiting
  python product_avatar.py submit \\
      --product-image product.png --template-image template.png -q

  # Recovery: poll existing task
  python product_avatar.py query --task-id <taskId> --timeout 1200
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- run (default full flow) --
    p_run = sub.add_parser("run", help="[DEFAULT] Submit task and poll until done")
    add_submit_args(p_run)
    add_poll_args(p_run)
    add_output_args(p_run)

    # -- submit only --
    p_submit = sub.add_parser("submit", help="Submit task only, print taskId and exit")
    add_submit_args(p_submit)
    add_output_args(p_submit)

    # -- query / poll existing task --
    p_query = sub.add_parser("query", help="Poll existing taskId until done or timeout")
    p_query.add_argument("--task-id", required=True,
                         help="taskId returned by 'submit' or a previous 'run'")
    add_poll_args(p_query)
    add_output_args(p_query)

    # -- list-categories --
    p_cats = sub.add_parser("list-categories",
                            help="List product avatar categories")
    p_cats.add_argument("--json", action="store_true",
                        help="Output full JSON response")
    p_cats.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress status messages on stderr")

    # -- list-avatars --
    p_avatars = sub.add_parser("list-avatars",
                               help="Browse public product avatar templates")
    p_avatars.add_argument("--gender", default=None, choices=["male", "female"],
                           help="Filter by gender")
    p_avatars.add_argument("--category-ids", default=None,
                           help="Filter by category IDs (comma-separated)")
    p_avatars.add_argument("--ethnicity-ids", default=None,
                           help="Filter by ethnicity IDs (comma-separated)")
    p_avatars.add_argument("--sort", default=None,
                           choices=["Popularity", "Newest"],
                           help="Sort order (default: Popularity)")
    p_avatars.add_argument("--page", type=int, default=None,
                           help="Page number (default: 1)")
    p_avatars.add_argument("--size", type=int, default=None,
                           help="Items per page (default: 20)")
    p_avatars.add_argument("--json", action="store_true",
                           help="Output full JSON response")
    p_avatars.add_argument("-q", "--quiet", action="store_true",
                           help="Suppress status messages on stderr")

    args = parser.parse_args()

    handlers = {
        "run": (cmd_run, p_run),
        "submit": (cmd_submit, p_submit),
        "query": (cmd_query, p_query),
        "list-categories": (cmd_list_categories, p_cats),
        "list-avatars": (cmd_list_avatars, p_avatars),
    }

    fn, p = handlers[args.subcommand]
    fn(args, p)


if __name__ == "__main__":
    main()
