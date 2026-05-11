#!/usr/bin/env python3
"""Generate a talking avatar video from a photo using Topview Avatar4.

## AGENT INSTRUCTIONS — READ FIRST
- Default workflow: ALWAYS use `run` (submit + auto-poll).
  Do NOT ask the user to run query manually.
- Only use `query` when `run` has already timed out and a taskId exists,
  or when the user explicitly provides a taskId to resume.
- When using `query`, keep polling (default timeout=600s) until
  status is 'success' or 'failed'. Do NOT stop after a single check.
- Never hand a pending taskId back to the user and say "check it later".
  Always poll to completion within the timeout window.

Subcommands:
    run            Submit task AND poll until done — DEFAULT, use this first
    submit         Submit only, print taskId, exit — use for parallel batch jobs
    query          Poll an existing taskId until done (or timeout) — use for recovery
    list-captions  List available caption styles (captionId + thumbnail)

Usage:
    python avatar4.py run    --image <fileId|path> --text "..." --voice <id> [options]
    python avatar4.py submit --image <fileId|path> --text "..." --voice <id> [options]
    python avatar4.py query  --task-id <taskId> [--timeout 600] [--interval 5] [options]
    python avatar4.py list-captions [--json]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

SUBMIT_PATH = "/v1/photo_avatar/task/submit"
QUERY_PATH = "/v1/photo_avatar/task/query"
CAPTION_LIST_PATH = "/v1/caption/list"
VALID_MODES = ("avatar4", "avatar4Fast")

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_body(args, file_id: str, audio_id: str | None) -> dict:
    """Build the submit-task request body from parsed args."""
    script_mode = "text" if args.text else "audio"
    body = {
        "templateImageFileId": file_id,
        "mode": args.mode,
        "scriptMode": script_mode,
    }
    if script_mode == "text":
        body["ttsText"] = args.text
        body["voiceId"] = args.voice
    else:
        body["audioFileId"] = audio_id
    if args.motion:
        body["customMotion"] = args.motion[:600]
    if args.caption:
        body["captionId"] = args.caption
    if args.save_avatar:
        body["saveCustomAiAvatar"] = True
    if args.board_id:
        body["boardId"] = args.board_id
    if args.notice_url:
        body["noticeUrl"] = args.notice_url
    return body


def do_submit(client: TopviewClient, body: dict, quiet: bool) -> str:
    """POST submit task, return taskId."""
    if not quiet:
        print("Submitting avatar4 task...", file=sys.stderr)
    result = client.post(SUBMIT_PATH, json=body)
    task_id = result["taskId"]
    if not quiet:
        print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
    return task_id


def do_poll(client: TopviewClient, task_id: str, timeout: float, interval: float,
            quiet: bool) -> dict:
    """Poll until status is 'success' or 'failed', or timeout is exceeded."""
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


def download_video(url: str, output: str, quiet: bool) -> None:
    """Download a video from URL to a local file."""
    import requests as req

    if not quiet:
        print(f"Downloading video to {output}...", file=sys.stderr)

    resp = req.get(url, stream=True)
    resp.raise_for_status()

    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    if not quiet:
        size_mb = os.path.getsize(output) / (1024 * 1024)
        print(f"Downloaded: {output} ({size_mb:.1f} MB)", file=sys.stderr)


def print_result(result: dict, args) -> None:
    """Print final result: video URL by default, full JSON with --json."""
    video_url = result.get("finishedVideoUrl", "")
    if args.output and video_url:
        download_video(video_url, args.output, args.quiet)
    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(video_url)
    board_task_id = result.get("boardTaskId", "")
    board_id = result.get("boardId", "") or getattr(args, "board_id", "") or ""
    if board_task_id and board_id:
        print(f"  edit: https://www.topview.ai/board/{board_id}?boardResultId={board_task_id}")


# ---------------------------------------------------------------------------
# Shared argument definitions
# ---------------------------------------------------------------------------

def add_submit_args(p):
    """Add arguments used by 'submit' and 'run' subcommands."""
    p.add_argument("--image", required=True,
                   help="Image fileId or local file path")
    p.add_argument("--text", default=None,
                   help="TTS text for the avatar to speak (use with --voice)")
    p.add_argument("--voice", default=None,
                   help="Voice ID (required when using --text)")
    p.add_argument("--audio", default=None,
                   help="Audio fileId for audio-driven mode")
    p.add_argument("--mode", default="avatar4", choices=VALID_MODES,
                   help="Generation mode (default: avatar4)")
    p.add_argument("--motion", default=None,
                   help="Custom action description (max 600 chars)")
    p.add_argument("--caption", default=None,
                   help="Caption style ID")
    p.add_argument("--save-avatar", action="store_true",
                   help="Save the image as a reusable custom avatar")
    p.add_argument("--board-id", default=None,
                   help="Board ID for task organization")
    p.add_argument("--notice-url", default=None,
                   help="Webhook URL to receive task completion notification")


def add_poll_args(p):
    """Add polling control arguments."""
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    """Add output/download arguments."""
    p.add_argument("--output", default=None,
                   help="Download result video to this local path")
    p.add_argument("--json", action="store_true",
                   help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress status messages on stderr")


def validate_submit_args(args, parser):
    if not args.text and not args.audio:
        parser.error("Either --text (with --voice) or --audio is required")
    if args.text and not args.voice:
        parser.error("--voice is required when using --text")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _resolve_inputs(args) -> tuple[str, str | None]:
    """Upload local image/audio paths and return (image_fileId, audio_fileId_or_None)."""
    client = TopviewClient()
    file_id = resolve_local_file(args.image, quiet=args.quiet, client=client)
    audio_id = None
    if args.audio:
        audio_id = resolve_local_file(args.audio, quiet=args.quiet, client=client)
    return file_id, audio_id


def cmd_run(args, parser):
    """Submit task then poll until done — full flow (default)."""
    validate_submit_args(args, parser)
    file_id, audio_id = _resolve_inputs(args)
    client = TopviewClient()
    body = build_body(args, file_id, audio_id)
    task_id = do_submit(client, body, args.quiet)
    result = do_poll(client, task_id, args.timeout, args.interval, args.quiet)
    print_result(result, args)


def cmd_submit(args, parser):
    """Submit task only — print taskId and exit immediately."""
    validate_submit_args(args, parser)
    file_id, audio_id = _resolve_inputs(args)
    client = TopviewClient()
    body = build_body(args, file_id, audio_id)
    task_id = do_submit(client, body, args.quiet)
    print(task_id)


def cmd_query(args, parser):
    """Poll an existing task by taskId until done or timeout.

    Keeps retrying until status == 'success' or 'failed', or --timeout expires.
    Does NOT stop after a single check — always polls to completion.
    """
    client = TopviewClient()
    try:
        result = do_poll(
            client, args.task_id, args.timeout, args.interval, args.quiet
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


def cmd_list_captions(args, parser):
    """List available caption styles (captionId + thumbnail URL)."""
    client = TopviewClient()
    result = client.get(CAPTION_LIST_PATH)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    captions = result if isinstance(result, list) else result.get("result", result)
    if not isinstance(captions, list):
        captions = [captions] if captions else []

    if not args.quiet:
        print(f"Captions: {len(captions)}", file=sys.stderr)

    for c in captions:
        cid = c.get("captionId", "")
        thumb = c.get("thumbnail", "")
        print(f"{cid}\t{thumb}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Avatar4 — generate a talking avatar video from a photo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
AGENT WORKFLOW RULES:
  1. ALWAYS start with `run` — it submits and polls automatically.
  2. Only use `query` if `run` timed out and you have a taskId to resume.
  3. `query` polls continuously (not once) until done or --timeout.
  4. NEVER hand a pending taskId back to the user — always poll to completion.

Subcommands:
  run            Submit + poll until done (DEFAULT — use this)
  submit         Submit only, print taskId, exit (for parallel batch)
  query          Poll existing taskId until done (for recovery after timeout)
  list-captions  List available caption styles

Examples:
  # List caption styles (use captionId with --caption)
  python avatar4.py list-captions

  # Standard usage — submit and wait (agent default)
  python avatar4.py run --image photo.png --text "Hello!" --voice <id>

  # Batch: submit multiple tasks without waiting
  python avatar4.py submit --image photo.png --text "Video 1" --voice <id>
  python avatar4.py submit --image photo2.png --text "Video 2" --voice <id>

  # Recovery: resume polling a taskId from a previous timed-out run
  python avatar4.py query --task-id <taskId>

  # Recovery with longer timeout
  python avatar4.py query --task-id <taskId> --timeout 1200
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- run (default full flow) --
    p_run = sub.add_parser(
        "run",
        help="[DEFAULT] Submit task and poll until done",
    )
    add_submit_args(p_run)
    add_poll_args(p_run)
    add_output_args(p_run)

    # -- submit only --
    p_submit = sub.add_parser(
        "submit",
        help="Submit task only, print taskId and exit immediately",
    )
    add_submit_args(p_submit)
    add_output_args(p_submit)

    # -- query / poll existing task --
    p_query = sub.add_parser(
        "query",
        help="Poll existing taskId until done or timeout (for recovery)",
    )
    p_query.add_argument("--task-id", required=True,
                         help="taskId returned by 'submit' or a previous 'run'")
    add_poll_args(p_query)
    add_output_args(p_query)

    # -- list-captions --
    p_captions = sub.add_parser(
        "list-captions",
        help="List available caption styles (captionId + thumbnail)",
    )
    p_captions.add_argument("--json", action="store_true",
                            help="Output full JSON response")
    p_captions.add_argument("-q", "--quiet", action="store_true",
                            help="Suppress status messages on stderr")

    args = parser.parse_args()

    handlers = {
        "run": (cmd_run, p_run),
        "submit": (cmd_submit, p_submit),
        "query": (cmd_query, p_query),
        "list-captions": (cmd_list_captions, p_captions),
    }

    fn, p = handlers[args.subcommand]
    fn(args, p)


if __name__ == "__main__":
    main()
