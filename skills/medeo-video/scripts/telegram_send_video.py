#!/usr/bin/env python3
"""
Send video messages via Telegram Bot API.

Usage:
    TELEGRAM_BOT_TOKEN=<token> python3 telegram_send_video.py \
        --video /path/to/video.mp4 \
        --to <chat_id> \
        [--cover-url https://...] \
        [--duration <seconds>] \
        [--caption "Video ready!"]

Security note:
    Bot token MUST be provided via TELEGRAM_BOT_TOKEN env var.
    Never pass it as a CLI argument (visible in `ps aux`).

Flow:
    1. Send video via sendVideo (supports thumbnail + caption)
    2. Output JSON with message_id on success

Telegram Bot API reference:
    - sendVideo: POST /bot<token>/sendVideo
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print(json.dumps({
        "error": "requests package not installed",
        "install_command": "pip install requests",
    }), file=sys.stderr)
    sys.exit(1)

TELEGRAM_API_BASE = "https://api.telegram.org"
CONNECT_TIMEOUT = 15   # seconds
UPLOAD_TIMEOUT = 180   # seconds — video upload can be slow


def get_bot_token() -> str:
    """Read bot token from environment only (never CLI args)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(json.dumps({
            "error": "TELEGRAM_BOT_TOKEN environment variable is not set",
            "hint": "Export TELEGRAM_BOT_TOKEN before running this script",
        }), file=sys.stderr)
        sys.exit(1)
    return token


def send_video(token: str, chat_id: str, video_path: str,
               cover_url: str = "", duration_seconds: int = 0,
               caption: str = "") -> dict:
    """
    Send a video file to a Telegram chat.

    Args:
        token: Bot token (from env, never logged)
        chat_id: Telegram chat_id (int or string, e.g. -1001234567890)
        video_path: Local path to the .mp4 file
        cover_url: Optional thumbnail URL (downloaded and sent as thumbnail)
        duration_seconds: Video duration in seconds (shown in player)
        caption: Optional caption text

    Returns:
        Telegram sendVideo result dict
    """
    print(f"[telegram] Sending video: {video_path}", file=sys.stderr)

    data: dict = {"chat_id": chat_id}
    if duration_seconds:
        data["duration"] = duration_seconds
    if caption:
        data["caption"] = caption
    data["supports_streaming"] = True

    files: dict = {}

    with open(video_path, "rb") as vf:
        files["video"] = (os.path.basename(video_path), vf, "video/mp4")

        # Download and attach thumbnail if provided
        thumb_bytes = None
        if cover_url:
            try:
                print(f"[telegram] Downloading thumbnail: {cover_url}", file=sys.stderr)
                r = requests.get(cover_url, timeout=(CONNECT_TIMEOUT, 30))
                if r.status_code == 200:
                    thumb_bytes = r.content
                    files["thumbnail"] = ("cover.jpg", thumb_bytes, "image/jpeg")
                else:
                    print(f"[telegram] Thumbnail download failed (HTTP {r.status_code}), skipping",
                          file=sys.stderr)
            except Exception as exc:
                print(f"[telegram] Thumbnail download error: {exc}, skipping", file=sys.stderr)

        resp = requests.post(
            f"{TELEGRAM_API_BASE}/bot{token}/sendVideo",
            data=data,
            files=files,
            timeout=(CONNECT_TIMEOUT, UPLOAD_TIMEOUT),
        )

    if resp.status_code != 200:
        body = {}
        try:
            body = resp.json()
        except Exception:
            pass
        print(json.dumps({
            "error": f"Telegram API error: HTTP {resp.status_code}",
            "description": body.get("description", resp.text[:200]),
        }), file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    if not result.get("ok"):
        print(json.dumps({
            "error": "Telegram sendVideo failed",
            "description": result.get("description", "unknown error"),
        }), file=sys.stderr)
        sys.exit(1)

    msg = result["result"]
    message_id = msg.get("message_id")
    print(f"[telegram] Sent successfully, message_id={message_id}", file=sys.stderr)
    return msg


def main():
    parser = argparse.ArgumentParser(
        description="Send video via Telegram Bot API. "
                    "Bot token must be set via TELEGRAM_BOT_TOKEN env var."
    )
    parser.add_argument("--video", required=True,
                        help="Local video file path (.mp4)")
    parser.add_argument("--to", required=True,
                        help="Telegram chat_id (e.g. -1001234567890 or @channel)")
    parser.add_argument("--cover-url", default="",
                        help="Thumbnail image URL (optional)")
    parser.add_argument("--duration", type=int, default=0,
                        help="Video duration in seconds (optional)")
    parser.add_argument("--caption", default="",
                        help="Caption text (optional)")
    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(json.dumps({"error": f"Video file not found: {args.video}"}),
              file=sys.stderr)
        sys.exit(1)

    token = get_bot_token()
    msg = send_video(
        token=token,
        chat_id=args.to,
        video_path=args.video,
        cover_url=args.cover_url,
        duration_seconds=args.duration,
        caption=args.caption,
    )

    print(json.dumps({
        "status": "ok",
        "message_id": msg.get("message_id"),
        "chat_id": msg.get("chat", {}).get("id"),
    }))


if __name__ == "__main__":
    main()
