#!/usr/bin/env python3
"""Manage voices: list available voices, clone custom voices, delete clones.

## AGENT INSTRUCTIONS — READ FIRST
- Use `list` to browse/search voices before running text2voice tasks.
- Use `clone` (full flow: submit + poll) to create a custom voice from audio.
  Only use `clone-submit` / `clone-query` for batch or recovery.
- Never hand a pending taskId back to the user — always poll to completion.

Subcommands:
    list          Search/browse available voices (system + custom)
    clone         Clone a voice from audio: submit + poll until done (DEFAULT)
    clone-submit  Submit clone task only, print taskId
    clone-query   Poll an existing clone taskId until done
    delete        Delete a custom (cloned) voice

Usage:
    python voice.py list [--language en] [--gender female] [--age Young] [--style UGC]
    python voice.py clone --audio <fileId_or_path> [--text "sample text"] [options]
    python voice.py clone-submit --audio <fileId_or_path> [options]
    python voice.py clone-query --task-id <taskId> [options]
    python voice.py delete --voice-id <voiceId>
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

VOICE_QUERY_PATH = "/v1/voice/query"
CLONE_SUBMIT_PATH = "/v1/voice/clone/task/submit"
CLONE_QUERY_PATH = "/v1/voice/clone/task/query"
CLONE_DELETE_PATH = "/v1/voice/clone/delete"

DEFAULT_TIMEOUT = 300
DEFAULT_INTERVAL = 5

SUPPORTED_LANGUAGES = [
    "en", "ar", "bg", "hr", "cs", "da", "nl", "fil", "fi", "fr", "de", "el",
    "hi", "hu", "id", "it", "ja", "ko", "ms", "nb", "pl", "pt", "ro", "ru",
    "zh-CN", "sk", "es", "sv", "zh-Hant", "tr", "uk", "vi", "th",
]

SUPPORTED_GENDERS = ["male", "female"]
SUPPORTED_AGES = ["Young", "Middle Age", "Old"]
SUPPORTED_STYLES = ["UGC", "Advertisement", "Cartoon_And_Animals", "Influencer"]


# ---------------------------------------------------------------------------
# list — query available voices
# ---------------------------------------------------------------------------

def cmd_list(args, parser):
    """Search available voices with optional filters."""
    client = TopviewClient()
    params = {}

    if args.page:
        params["pageNo"] = str(args.page)
    if args.size:
        params["pageSize"] = str(args.size)
    if args.language:
        params["language"] = args.language
    if args.gender:
        params["gender"] = args.gender
    if args.age:
        params["age"] = args.age
    if args.style:
        params["style"] = args.style
    if args.accent:
        params["accent"] = args.accent
    if args.custom:
        params["isCustom"] = "true"

    result = client.get(VOICE_QUERY_PATH, params=params)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    total = result.get("total", 0)
    page = result.get("pageNo", 1)
    data = result.get("data", [])

    if not args.quiet:
        print(f"Voices: {len(data)} of {total} (page {page})", file=sys.stderr)

    for v in data:
        vid = v.get("voiceId", "")
        name = v.get("voiceName", "")
        lang = v.get("language", "")
        gender = v.get("gender", "")
        age = v.get("age", "")
        style = v.get("style", "")
        accent = v.get("accent", "")
        demo = v.get("demoAudioUrl", "")
        print(f"{vid}\t{name}\t{lang}\t{gender}\t{age}\t{style}\t{accent}\t{demo}")


# ---------------------------------------------------------------------------
# clone — voice cloning (submit + poll)
# ---------------------------------------------------------------------------

def build_clone_body(args, client: TopviewClient) -> dict:
    """Build request body for voice clone submission."""
    file_id = resolve_local_file(args.audio, quiet=args.quiet, client=client)
    body = {
        "originVoiceFileId": file_id,
    }
    if args.name:
        body["name"] = args.name
    if args.text:
        body["voiceText"] = args.text
    if args.speed is not None:
        body["voiceSpeed"] = args.speed
    if args.notice_url:
        body["noticeUrl"] = args.notice_url
    return body


def do_clone_submit(client: TopviewClient, body: dict, quiet: bool) -> str:
    """POST clone task, return taskId."""
    if not quiet:
        print("Submitting voice clone task...", file=sys.stderr)
    result = client.post(CLONE_SUBMIT_PATH, json=body)
    task_id = result["taskId"]
    if not quiet:
        print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
    return task_id


def do_clone_poll(client: TopviewClient, task_id: str, timeout: float,
                  interval: float, quiet: bool) -> dict:
    """Poll clone task until success/fail or timeout."""
    if not quiet:
        print(
            f"Polling clone task {task_id} (timeout={timeout}s, interval={interval}s)...",
            file=sys.stderr,
        )
    return client.poll_task(
        CLONE_QUERY_PATH,
        task_id,
        interval=interval,
        timeout=timeout,
        verbose=not quiet,
    )


def print_clone_result(result: dict, args) -> None:
    """Print voice clone result."""
    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    status = result.get("status", "unknown")
    voice = result.get("voice", {})
    voice_id = voice.get("voiceId", "N/A")
    voice_name = voice.get("voiceName", "N/A")
    demo_url = voice.get("demoAudioUrl", "")

    print(f"status: {status}")
    print(f"  voiceId:   {voice_id}")
    print(f"  voiceName: {voice_name}")
    if demo_url:
        print(f"  demoAudio: {demo_url}")


def cmd_clone(args, parser):
    """Clone a voice: submit + poll until done."""
    client = TopviewClient()
    body = build_clone_body(args, client)
    task_id = do_clone_submit(client, body, args.quiet)
    result = do_clone_poll(client, task_id, args.timeout, args.interval, args.quiet)
    print_clone_result(result, args)


def cmd_clone_submit(args, parser):
    """Submit clone task only — print taskId and exit."""
    client = TopviewClient()
    body = build_clone_body(args, client)
    task_id = do_clone_submit(client, body, args.quiet)
    print(task_id)


def cmd_clone_query(args, parser):
    """Poll an existing clone task by taskId."""
    client = TopviewClient()
    try:
        result = do_clone_poll(
            client, args.task_id, args.timeout, args.interval, args.quiet,
        )
        print_clone_result(result, args)
    except TimeoutError as e:
        if not args.quiet:
            print(f"Timeout reached: {e}", file=sys.stderr)
            print("Fetching last known status...", file=sys.stderr)
        last = client.get(CLONE_QUERY_PATH, params={"taskId": args.task_id})
        status = last.get("status", "unknown")
        task_id = last.get("taskId", args.task_id)
        if args.json:
            print(json_mod.dumps(last, indent=2, ensure_ascii=False))
        else:
            print(f"status: {status}  taskId: {task_id}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# delete — delete a custom voice
# ---------------------------------------------------------------------------

def cmd_delete(args, parser):
    """Delete a custom (cloned) voice by voiceId."""
    client = TopviewClient()
    if not args.quiet:
        print(f"Deleting voice {args.voice_id}...", file=sys.stderr)
    result = client.delete(CLONE_DELETE_PATH, params={"voiceId": args.voice_id})
    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        if not args.quiet:
            print(f"Voice {args.voice_id} deleted.", file=sys.stderr)
        print("ok")


# ---------------------------------------------------------------------------
# Argument helpers
# ---------------------------------------------------------------------------

def add_clone_submit_args(p):
    """Arguments for clone submit."""
    p.add_argument("--audio", required=True,
                   help="Voice audio file (fileId or local path). Format: mp3/wav, 10s-5min, <10MB")
    p.add_argument("--name", default=None,
                   help="Name for the cloned voice (defaults to taskId)")
    p.add_argument("--text", default=None,
                   help="Reference text matching the audio content")
    p.add_argument("--speed", type=float, default=None,
                   help="Voice speed 0.8-1.2 (default: 1.0)")
    p.add_argument("--notice-url", default=None,
                   help="Webhook URL for completion notification")


def add_poll_args(p):
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    p.add_argument("--json", action="store_true",
                   help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress status messages on stderr")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Voice Management — list voices, clone custom voices, delete clones.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List English female voices
  python voice.py list --language en --gender female

  # List custom (cloned) voices
  python voice.py list --custom

  # Clone a voice from audio
  python voice.py clone --audio recording.mp3 --name "My Voice"

  # Clone with reference text
  python voice.py clone --audio sample.wav --name "Brand Voice" \\
      --text "Welcome to topview.ai, the ultimate AI video platform."

  # Delete a custom voice
  python voice.py delete --voice-id <voiceId>
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- list --
    p_list = sub.add_parser("list", help="Search/browse available voices")
    p_list.add_argument("--language", default=None,
                        help="Filter by language code (e.g. en, zh-CN, ja, ko)")
    p_list.add_argument("--gender", default=None, choices=SUPPORTED_GENDERS,
                        help="Filter by gender: male / female")
    p_list.add_argument("--age", default=None, choices=SUPPORTED_AGES,
                        help="Filter by age: Young / Middle Age / Old")
    p_list.add_argument("--style", default=None, choices=SUPPORTED_STYLES,
                        help="Filter by style: UGC / Advertisement / Cartoon_And_Animals / Influencer")
    p_list.add_argument("--accent", default=None,
                        help="Filter by accent (e.g. American, British, Chinese)")
    p_list.add_argument("--custom", action="store_true",
                        help="Show only custom (cloned) voices")
    p_list.add_argument("--page", type=int, default=None,
                        help="Page number (default: 1)")
    p_list.add_argument("--size", type=int, default=None,
                        help="Items per page (default: 20)")
    add_output_args(p_list)

    # -- clone (full flow) --
    p_clone = sub.add_parser("clone", help="[DEFAULT] Clone voice: submit + poll until done")
    add_clone_submit_args(p_clone)
    add_poll_args(p_clone)
    add_output_args(p_clone)

    # -- clone-submit --
    p_csub = sub.add_parser("clone-submit", help="Submit clone task only, print taskId")
    add_clone_submit_args(p_csub)
    add_output_args(p_csub)

    # -- clone-query --
    p_cquery = sub.add_parser("clone-query", help="Poll existing clone taskId until done")
    p_cquery.add_argument("--task-id", required=True,
                          help="taskId returned by clone-submit")
    add_poll_args(p_cquery)
    add_output_args(p_cquery)

    # -- delete --
    p_del = sub.add_parser("delete", help="Delete a custom (cloned) voice")
    p_del.add_argument("--voice-id", required=True,
                       help="voiceId of the voice to delete")
    add_output_args(p_del)

    args = parser.parse_args()

    handlers = {
        "list": (cmd_list, p_list),
        "clone": (cmd_clone, p_clone),
        "clone-submit": (cmd_clone_submit, p_csub),
        "clone-query": (cmd_clone_query, p_cquery),
        "delete": (cmd_delete, p_del),
    }

    fn, p = handlers[args.subcommand]
    fn(args, p)


if __name__ == "__main__":
    main()
