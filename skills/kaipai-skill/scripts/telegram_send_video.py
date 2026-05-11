#!/usr/bin/env python3
from __future__ import annotations

"""
Send video messages via Telegram Bot API.

Security: bot token MUST be in TELEGRAM_BOT_TOKEN env var — never as a CLI arg.
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print(
        json.dumps(
            {
                "error": "requests package not installed",
                "install_command": "pip install requests",
            }
        ),
        file=sys.stderr,
    )
    sys.exit(1)

TELEGRAM_API_BASE = "https://api.telegram.org"
CONNECT_TIMEOUT = 15
UPLOAD_TIMEOUT = 180


def get_bot_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            json.dumps(
                {
                    "error": "TELEGRAM_BOT_TOKEN environment variable is not set",
                    "hint": "Export TELEGRAM_BOT_TOKEN before running this script",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def send_video(
    token: str,
    chat_id: str,
    video_path: str,
    cover_url: str = "",
    duration_seconds: int = 0,
    caption: str = "",
) -> tuple[dict | None, str | None]:
    """Send video; returns (message dict, error string)."""
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

        if cover_url:
            try:
                print(f"[telegram] Downloading thumbnail: {cover_url}", file=sys.stderr)
                r = requests.get(cover_url, timeout=(CONNECT_TIMEOUT, 30))
                if r.status_code == 200:
                    files["thumbnail"] = ("cover.jpg", r.content, "image/jpeg")
                else:
                    print(
                        f"[telegram] Thumbnail download failed (HTTP {r.status_code}), skipping",
                        file=sys.stderr,
                    )
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
        err = body.get("description", resp.text[:200])
        print(
            json.dumps(
                {
                    "error": f"Telegram API error: HTTP {resp.status_code}",
                    "description": err,
                }
            ),
            file=sys.stderr,
        )
        return None, err or f"HTTP {resp.status_code}"

    result = resp.json()
    if not result.get("ok"):
        err = result.get("description", "unknown error")
        print(
            json.dumps(
                {
                    "error": "Telegram sendVideo failed",
                    "description": err,
                }
            ),
            file=sys.stderr,
        )
        return None, err

    msg = result["result"]
    print(
        f"[telegram] Video sent, message_id={msg.get('message_id')}",
        file=sys.stderr,
    )
    return msg, None


def send_text_message(token: str, chat_id: str, text: str) -> tuple[dict | None, str | None]:
    """Send plain text (URLs are linkified by clients)."""
    print("[telegram] Sending download link text", file=sys.stderr)
    resp = requests.post(
        f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=(CONNECT_TIMEOUT, 30),
    )
    if resp.status_code != 200:
        body = {}
        try:
            body = resp.json()
        except Exception:
            pass
        err = body.get("description", resp.text[:200])
        print(
            json.dumps(
                {
                    "error": f"Telegram sendMessage error: HTTP {resp.status_code}",
                    "description": err,
                }
            ),
            file=sys.stderr,
        )
        return None, err or f"HTTP {resp.status_code}"

    result = resp.json()
    if not result.get("ok"):
        err = result.get("description", "unknown error")
        print(
            json.dumps(
                {"error": "Telegram sendMessage failed", "description": err}),
            file=sys.stderr,
        )
        return None, err

    msg = result["result"]
    print(
        f"[telegram] Text sent, message_id={msg.get('message_id')}",
        file=sys.stderr,
    )
    return msg, None


def main():
    parser = argparse.ArgumentParser(
        description="Send video via Telegram. Token via TELEGRAM_BOT_TOKEN only."
    )
    parser.add_argument("--video", required=True, help="Local video file path (.mp4)")
    parser.add_argument("--to", required=True, help="Telegram chat_id")
    parser.add_argument("--cover-url", default="", help="Thumbnail image URL (optional)")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (optional)")
    parser.add_argument("--caption", default="", help="Caption (optional)")
    parser.add_argument(
        "--video-url",
        default="",
        help="Result URL: always sends an extra text message with this link after sendVideo",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(json.dumps({"error": f"Video file not found: {args.video}"}), file=sys.stderr)
        sys.exit(1)

    token = get_bot_token()
    video_url = (args.video_url or "").strip()

    video_msg, video_err = send_video(
        token=token,
        chat_id=args.to,
        video_path=args.video,
        cover_url=args.cover_url,
        duration_seconds=args.duration,
        caption=args.caption,
    )

    text_msg = None
    text_err = None
    if video_url:
        link_text = f"Video download:\n{video_url}"
        text_msg, text_err = send_text_message(token, args.to, link_text)

    if video_url:
        ok = bool((video_msg is not None) or (text_msg is not None))
    else:
        ok = video_msg is not None

    out: dict = {
        "status": "ok" if ok else "failed",
        "message_id": video_msg.get("message_id") if video_msg else None,
        "chat_id": (video_msg or text_msg or {}).get("chat", {}).get("id"),
        "text_message_id": text_msg.get("message_id") if text_msg else None,
    }
    if video_err:
        out["video_error"] = video_err
    if text_err:
        out["text_error"] = text_err

    print(json.dumps(out))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
