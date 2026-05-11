#!/usr/bin/env python3
"""Board management: list, create, update, delete boards; query board tasks.

Boards organize generated results so users can view and edit them on the web.
Every user has a default "My First Board". API users should fetch the default
board ID once per session and pass it as --board-id to generation scripts.

Subcommands:
    list          List boards (paginated). Use --default to get the default board ID.
    create        Create a new board
    detail        Get board details (members, share tokens)
    update        Rename a board
    delete        Delete a board
    tasks         List tasks in a board (with filters)
    task-detail   Get a single task's full details

Usage:
    python board.py list [--default] [--page N] [--size N]
    python board.py create --name "Campaign Board"
    python board.py detail --board-id <boardId>
    python board.py update --board-id <boardId> --name "New Name"
    python board.py delete --board-id <boardId>
    python board.py tasks --board-id <boardId> [--media-type video] [--sort-field gmtCreate]
    python board.py task-detail --task-id <taskId>
"""

import argparse
import json as json_mod
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError

BOARD_LIST_PATH = "/boards/list"
BOARD_CREATE_PATH = "/boards/create"
BOARD_DETAIL_PATH = "/boards/detail"
BOARD_UPDATE_PATH = "/boards/update"
BOARD_DELETE_PATH = "/boards/delete"
BOARD_TASKS_PATH = "/boards/tasks/list"
BOARD_TASK_DETAIL_PATH = "/boards/tasks/detail"

BOARD_WEB_BASE = "https://aigc-web-base-preview.vercel.app/board"


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def cmd_list(args, parser):
    """List boards with optional pagination. --default prints only the default board ID."""
    client = TopviewClient()
    params = {}
    if args.page:
        params["pageNo"] = str(args.page)
    if args.size:
        params["pageSize"] = str(args.size)

    result = client.get(BOARD_LIST_PATH, params=params)

    if args.default:
        records = result.get("data", [])
        board_id = None
        for r in records:
            if r.get("name") == "My First Board" or r.get("isSystemDefault"):
                board_id = r.get("boardId")
                break
        if not board_id and records:
            board_id = records[0].get("boardId")
        if board_id:
            print(f"Get default 'My First Board' board id: {board_id}")
        else:
            print("No boards found.", file=sys.stderr)
            sys.exit(1)
        return

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    records = result.get("data", [])
    total = result.get("total", 0)
    page = result.get("pageNo", 1)
    if not args.quiet:
        print(f"Boards: {len(records)} of {total} (page {page})", file=sys.stderr)

    for b in records:
        bid = b.get("boardId", "")
        name = b.get("name", "")
        count = b.get("taskCount", 0)
        default = " [default]" if b.get("isSystemDefault") or name == "My First Board" else ""
        print(f"{bid}\t{name}\t{count} tasks{default}")


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

def cmd_create(args, parser):
    """Create a new board."""
    client = TopviewClient()
    result = client.post(BOARD_CREATE_PATH, json={"name": args.name})

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    board_id = result.get("boardId", "")
    name = result.get("name", "")
    if not args.quiet:
        print(f"Board created: {name}", file=sys.stderr)
        print(f"  url: {BOARD_WEB_BASE}/{board_id}", file=sys.stderr)
    print(board_id)


# ---------------------------------------------------------------------------
# detail
# ---------------------------------------------------------------------------

def cmd_detail(args, parser):
    """Get board details."""
    client = TopviewClient()
    result = client.get(BOARD_DETAIL_PATH, params={"boardId": args.board_id})

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    name = result.get("name", "")
    count = result.get("taskCount", 0)
    owner = result.get("ownerName", "")
    created = result.get("gmtCreate", "")
    members = result.get("members", [])

    print(f"Board: {name}")
    print(f"  boardId:  {args.board_id}")
    print(f"  owner:    {owner}")
    print(f"  tasks:    {count}")
    print(f"  created:  {created}")
    print(f"  url:      {BOARD_WEB_BASE}/{args.board_id}")
    if members:
        print(f"  members:  {len(members)}")
        for m in members:
            role = m.get("role", "")
            nick = m.get("nickname", "")
            print(f"    - {nick} ({role})")


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

def cmd_update(args, parser):
    """Rename a board."""
    client = TopviewClient()
    result = client.put(BOARD_UPDATE_PATH, json={
        "boardId": args.board_id,
        "name": args.name,
    })

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    new_name = result.get("name", args.name)
    if not args.quiet:
        print(f"Board {args.board_id} renamed to: {new_name}", file=sys.stderr)
    print("ok")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def cmd_delete(args, parser):
    """Delete a board."""
    client = TopviewClient()
    client.delete(BOARD_DELETE_PATH, params={"boardId": args.board_id})

    if not args.quiet:
        print(f"Board {args.board_id} deleted.", file=sys.stderr)
    print("ok")


# ---------------------------------------------------------------------------
# tasks
# ---------------------------------------------------------------------------

def cmd_tasks(args, parser):
    """List tasks in a board."""
    client = TopviewClient()
    params = {"boardId": args.board_id}
    if args.page:
        params["pageNo"] = str(args.page)
    if args.size:
        params["pageSize"] = str(args.size)
    if args.media_type:
        params["mediaType"] = args.media_type
    if args.rating is not None:
        params["rating"] = str(args.rating)
    if args.tool_category:
        params["toolCategory"] = args.tool_category
    if args.tool_type:
        params["toolType"] = args.tool_type
    if args.sort_field:
        params["sortField"] = args.sort_field
    if args.sort_order:
        params["sortOrder"] = args.sort_order

    result = client.get(BOARD_TASKS_PATH, params=params)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    tasks = result.get("list", [])
    total = result.get("total", 0)
    page = result.get("pageNo", 1)
    if not args.quiet:
        print(f"Tasks: {len(tasks)} of {total} (page {page})", file=sys.stderr)

    for t in tasks:
        tid = t.get("taskId", "")
        btid = t.get("boardTaskId", "")
        status = t.get("status", "")
        tool = t.get("toolType", "")
        media = t.get("mediaType", "")
        cost = t.get("creditsCost", 0)
        created = t.get("gmtCreate", "")
        res = t.get("result", {})
        url = res.get("videoUrl") or res.get("imageUrl") or ""
        print(f"{tid}\t{btid}\t{status}\t{tool}\t{media}\t{cost}cr\t{created}\t{url}")


# ---------------------------------------------------------------------------
# task-detail
# ---------------------------------------------------------------------------

def _print_task_detail(result: dict) -> None:
    """Format and print a single task result."""
    tid = result.get("taskId", "")
    btid = result.get("boardTaskId", "")
    bid = result.get("boardId", "")
    status = result.get("status", "")
    tool = result.get("toolType", "")
    cost = result.get("creditsCost", 0)
    created = result.get("gmtCreate", "")
    completed = result.get("completedAt", "")
    error_msg = result.get("errorMessage", "")
    res = result.get("result", {})

    print(f"Task: {tid}")
    print(f"  boardTaskId: {btid}")
    print(f"  boardId:     {bid}")
    print(f"  status:      {status}")
    print(f"  tool:        {tool}")
    print(f"  cost:        {cost} credits")
    print(f"  created:     {created}")
    if completed:
        print(f"  completed:   {completed}")
    if error_msg:
        print(f"  error:       {error_msg}")
    if res:
        for k, v in res.items():
            print(f"  {k}: {v}")
    if btid and bid:
        print(f"  edit: {BOARD_WEB_BASE}/{bid}?boardResultId={btid}")

    estimate = result.get("estimateInfo")
    if estimate:
        queue = estimate.get("queueCount", 0)
        wait = estimate.get("estimatedWaitSeconds", 0)
        print(f"  queue: {queue} ahead, ~{wait}s wait")


TERMINAL_STATUSES = {"success", "fail", "failed"}
DEFAULT_TD_TIMEOUT = 600
DEFAULT_TD_INTERVAL = 5


def cmd_task_detail(args, parser):
    """Poll a single task until it reaches a terminal status, then print details."""
    client = TopviewClient()
    timeout = args.timeout
    interval = args.interval
    start = time.time()

    while True:
        elapsed = time.time() - start
        result = client.get(BOARD_TASK_DETAIL_PATH, params={"taskId": args.task_id})
        status = result.get("status", "")

        if status in TERMINAL_STATUSES or elapsed >= timeout:
            break

        if not args.quiet:
            print(
                f"  [{elapsed:.0f}s] status: {status}",
                file=sys.stderr,
            )
        time.sleep(interval)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_task_detail(result)

    if status not in TERMINAL_STATUSES:
        if not args.quiet:
            print(
                f"Timeout after {timeout}s — task still {status}. "
                f"Re-run with --timeout to keep polling.",
                file=sys.stderr,
            )
        sys.exit(2)


# ---------------------------------------------------------------------------
# Shared arg helpers
# ---------------------------------------------------------------------------

def add_output_args(p):
    p.add_argument("--json", action="store_true", help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress status messages on stderr")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Board Management — organize generated results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get default board ID (agent startup)
  python board.py list --default -q

  # List all boards
  python board.py list

  # Create a new board
  python board.py create --name "Campaign Q3"

  # View board details
  python board.py detail --board-id <boardId>

  # Rename a board
  python board.py update --board-id <boardId> --name "Campaign Q4"

  # Delete a board
  python board.py delete --board-id <boardId>

  # List video tasks in a board
  python board.py tasks --board-id <boardId> --media-type video

  # Get task details
  python board.py task-detail --task-id <taskId>
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- list --
    p_list = sub.add_parser("list", help="List boards")
    p_list.add_argument("--default", action="store_true",
                        help="Print only the default board ID (for agent auto-discovery)")
    p_list.add_argument("--page", type=int, default=None, help="Page number")
    p_list.add_argument("--size", type=int, default=None, help="Items per page")
    add_output_args(p_list)

    # -- create --
    p_create = sub.add_parser("create", help="Create a new board")
    p_create.add_argument("--name", required=True, help="Board name (max 200 chars)")
    add_output_args(p_create)

    # -- detail --
    p_detail = sub.add_parser("detail", help="Get board details")
    p_detail.add_argument("--board-id", required=True, help="Board ID")
    add_output_args(p_detail)

    # -- update --
    p_update = sub.add_parser("update", help="Rename a board")
    p_update.add_argument("--board-id", required=True, help="Board ID")
    p_update.add_argument("--name", required=True, help="New board name (max 200 chars)")
    add_output_args(p_update)

    # -- delete --
    p_delete = sub.add_parser("delete", help="Delete a board")
    p_delete.add_argument("--board-id", required=True, help="Board ID")
    add_output_args(p_delete)

    # -- tasks --
    p_tasks = sub.add_parser("tasks", help="List tasks in a board")
    p_tasks.add_argument("--board-id", required=True, help="Board ID")
    p_tasks.add_argument("--page", type=int, default=None, help="Page number")
    p_tasks.add_argument("--size", type=int, default=None, help="Items per page")
    p_tasks.add_argument("--media-type", default=None, help="Filter: image / video")
    p_tasks.add_argument("--rating", type=int, default=None, choices=[0, 1, 2, 3], help="Filter by rating 0-3")
    p_tasks.add_argument("--tool-category", default=None, help="Filter by tool category")
    p_tasks.add_argument("--tool-type", default=None, help="Filter by tool type")
    p_tasks.add_argument("--sort-field", default=None, help="Sort field: gmtCreate / sortWeight")
    p_tasks.add_argument("--sort-order", default=None, choices=["asc", "desc"], help="Sort order")
    add_output_args(p_tasks)

    # -- task-detail --
    p_td = sub.add_parser("task-detail", help="Poll a task until done, then print details")
    p_td.add_argument("--task-id", required=True, help="Task ID")
    p_td.add_argument("--timeout", type=float, default=DEFAULT_TD_TIMEOUT,
                       help=f"Max polling time in seconds (default: {DEFAULT_TD_TIMEOUT})")
    p_td.add_argument("--interval", type=float, default=DEFAULT_TD_INTERVAL,
                       help=f"Polling interval in seconds (default: {DEFAULT_TD_INTERVAL})")
    add_output_args(p_td)

    args = parser.parse_args()

    handlers = {
        "list": (cmd_list, p_list),
        "create": (cmd_create, p_create),
        "detail": (cmd_detail, p_detail),
        "update": (cmd_update, p_update),
        "delete": (cmd_delete, p_delete),
        "tasks": (cmd_tasks, p_tasks),
        "task-detail": (cmd_task_detail, p_td),
    }

    fn, p = handlers[args.subcommand]
    fn(args, p)


if __name__ == "__main__":
    main()
    
