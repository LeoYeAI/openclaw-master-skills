#!/usr/bin/env python3
"""Generate audio from text using Topview Text-to-Voice API.

## AGENT INSTRUCTIONS — READ FIRST
- Default workflow: ALWAYS use `run` (submit + auto-poll).
  Do NOT ask the user to run query manually.
- Only use `query` when `run` has already timed out and a taskId exists,
  or when the user explicitly provides a taskId to resume.
- When using `query`, keep polling (default timeout=300s) until
  status is 'success' or 'fail'. Do NOT stop after a single check.
- Never hand a pending taskId back to the user and say "check it later".
  Always poll to completion within the timeout window.

Subcommands:
    run     Submit task AND poll until done — DEFAULT, use this first
    submit  Submit only, print taskId, exit — use for parallel batch jobs
    query   Poll an existing taskId until done (or timeout) — use for recovery

Usage:
    python text2voice.py run --text "Hello world" --voice-id <voiceId> [options]
    python text2voice.py submit --text "Hello world" --voice-id <voiceId> [options]
    python text2voice.py query --task-id <taskId> [options]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

SUBMIT_PATH = "/v1/voice/text2voice/task/submit"
QUERY_PATH = "/v1/voice/text2voice/task/query"

DEFAULT_TIMEOUT = 300
DEFAULT_INTERVAL = 3

FIXED_COST = 0.1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_body(args, client: TopviewClient) -> dict:
    """Build the submit-task request body from parsed args."""
    body = {
        "voiceText": args.text,
        "voiceId": args.voice_id,
    }

    if args.name:
        body["name"] = args.name
    if args.speed is not None:
        body["voiceSpeed"] = args.speed
    if args.emotion:
        body["emotionName"] = args.emotion
    if args.origin_voice_file:
        body["originVoiceFileId"] = resolve_local_file(
            args.origin_voice_file, quiet=args.quiet, client=client
        )
    if args.pron_rules:
        body["pronRules"] = json_mod.loads(args.pron_rules)
    if args.board_id:
        body["boardId"] = args.board_id
    if args.notice_url:
        body["noticeUrl"] = args.notice_url

    return body


def do_submit(client: TopviewClient, body: dict, quiet: bool) -> str:
    """POST submit task, return taskId."""
    if not quiet:
        print("Submitting text-to-voice task...", file=sys.stderr)
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


def download_audio(url: str, output: str, quiet: bool) -> None:
    """Download an audio file from URL to a local path."""
    import requests as req

    if not quiet:
        print(f"Downloading audio to {output}...", file=sys.stderr)

    resp = req.get(url, stream=True)
    resp.raise_for_status()

    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    if not quiet:
        size_kb = os.path.getsize(output) / 1024
        print(f"Downloaded: {output} ({size_kb:.1f} KB)", file=sys.stderr)


def print_result(result: dict, args) -> None:
    """Print final result: audio URL by default, full JSON with --json."""
    voice = result.get("voice", {})
    audio_url = voice.get("demoAudioUrl", "")

    if args.output and audio_url:
        download_audio(audio_url, args.output, args.quiet)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        cost = result.get("costCredit", FIXED_COST)
        duration = voice.get("durations", "N/A")
        print(f"status: {result.get('status')}  cost: {cost} credits  duration: {duration}s")
        if audio_url:
            print(f"  audio: {audio_url}")
    board_task_id = result.get("boardTaskId", "")
    board_id = result.get("boardId", "") or getattr(args, "board_id", "") or ""
    if board_task_id and board_id:
        print(f"  edit: https://www.topview.ai/board/{board_id}?boardResultId={board_task_id}")


# ---------------------------------------------------------------------------
# Argument definitions
# ---------------------------------------------------------------------------

def add_submit_args(p):
    """Add arguments used by 'submit' and 'run' subcommands."""
    p.add_argument("--text", required=True,
                   help="Text to convert to speech")
    p.add_argument("--voice-id", required=True,
                   help="Voice ID (tone/speaker)")
    p.add_argument("--name", default=None,
                   help="Voice name label")
    p.add_argument("--speed", type=float, default=None,
                   help="Speech speed multiplier (e.g. 1.0 = normal)")
    p.add_argument("--emotion", default=None,
                   help="Voice emotion name (e.g. happy, sad)")
    p.add_argument("--origin-voice-file", default=None,
                   help="Original voice file fileId or local path")
    p.add_argument("--pron-rules", default=None,
                   help='Pronunciation rules as JSON array, e.g. \'[{"oldStr":"行","newStr":"xing"}]\'')
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
                   help="Download result audio to this local path")
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Text-to-Voice — generate audio from text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AGENT WORKFLOW RULES:
  1. ALWAYS start with `run` — it submits and polls automatically.
  2. Only use `query` if `run` timed out and you have a taskId to resume.
  3. `query` polls continuously (not once) until done or --timeout.
  4. NEVER hand a pending taskId back to the user — always poll to completion.

Examples:
  # Standard usage
  python text2voice.py run --text "Hello world" --voice-id voice-888

  # With speed and emotion
  python text2voice.py run --text "你好，欢迎使用。" --voice-id voice-888 \\
      --speed 1.2 --emotion happy

  # With pronunciation rules
  python text2voice.py run --text "行不行" --voice-id voice-888 \\
      --pron-rules '[{"oldStr":"行","newStr":"xing"}]'

  # Download result audio
  python text2voice.py run --text "Hello" --voice-id voice-888 \\
      --output result.mp3

  # Batch: submit without waiting
  python text2voice.py submit --text "Segment 1" --voice-id voice-888 -q

  # Recovery: poll existing task
  python text2voice.py query --task-id <taskId>
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

    args = parser.parse_args()

    if args.subcommand == "run":
        cmd_run(args, p_run)
    elif args.subcommand == "submit":
        cmd_submit(args, p_submit)
    elif args.subcommand == "query":
        cmd_query(args, p_query)


if __name__ == "__main__":
    main()
