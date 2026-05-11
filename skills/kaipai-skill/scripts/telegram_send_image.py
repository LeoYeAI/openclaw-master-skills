#!/usr/bin/env python3
"""
Send image messages via Telegram Bot API.

Usage:
    TELEGRAM_BOT_TOKEN=<token> python3 telegram_send_image.py \
        --image /path/to/image.jpg \
        --to <chat_id> \
        [--caption "Here is your result"]

    # Or with a URL (auto-downloaded):
    TELEGRAM_BOT_TOKEN=<token> python3 telegram_send_image.py \
        --image https://example.com/result.jpg \
        --to <chat_id>

Security note:
    Bot token MUST be provided via TELEGRAM_BOT_TOKEN env var.
    Never pass it as a CLI argument (visible in `ps aux`).

Telegram Bot API reference:
    - sendPhoto: POST /bot<token>/sendPhoto
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
UPLOAD_TIMEOUT = 60    # seconds


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


def send_photo(token: str, chat_id: str, image_source: str, caption: str = "") -> dict:
    """
    Send a photo to a Telegram chat.

    Args:
        token: Bot token (from env, never logged)
        chat_id: Telegram chat_id (int or string, e.g. -1001234567890)
        image_source: Local file path or URL
        caption: Optional caption text

    Returns:
        Telegram sendPhoto result dict
    """
    print(f"[telegram] Sending image: {image_source}", file=sys.stderr)

    data: dict = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption

    if image_source.startswith("http"):
        # Download first, then upload as file
        print(f"[telegram] Downloading image: {image_source}", file=sys.stderr)
        r = requests.get(image_source, timeout=(CONNECT_TIMEOUT, 60))
        r.raise_for_status()
        img_bytes = r.content
        filename = image_source.split("?")[0].split("/")[-1] or "image.jpg"
        files = {"photo": (filename, img_bytes, "image/jpeg")}
        resp = requests.post(
            f"{TELEGRAM_API_BASE}/bot{token}/sendPhoto",
            data=data,
            files=files,
            timeout=(CONNECT_TIMEOUT, UPLOAD_TIMEOUT),
        )
    else:
        if not os.path.isfile(image_source):
            print(json.dumps({"error": f"Image file not found: {image_source}"}), file=sys.stderr)
            sys.exit(1)
        with open(image_source, "rb") as f:
            files = {"photo": (os.path.basename(image_source), f, "image/jpeg")}
            resp = requests.post(
                f"{TELEGRAM_API_BASE}/bot{token}/sendPhoto",
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
            "error": "Telegram sendPhoto failed",
            "description": result.get("description", "unknown error"),
        }), file=sys.stderr)
        sys.exit(1)

    msg = result["result"]
    message_id = msg.get("message_id")
    print(f"[telegram] Sent successfully, message_id={message_id}", file=sys.stderr)
    return msg


def main():
    parser = argparse.ArgumentParser(
        description="Send image via Telegram Bot API. "
                    "Bot token must be set via TELEGRAM_BOT_TOKEN env var."
    )
    parser.add_argument("--image", required=True,
                        help="Local image file path or URL")
    parser.add_argument("--to", required=True,
                        help="Telegram chat_id (e.g. -1001234567890 or @channel)")
    parser.add_argument("--caption", default="",
                        help="Caption text (optional)")
    args = parser.parse_args()

    token = get_bot_token()
    msg = send_photo(
        token=token,
        chat_id=args.to,
        image_source=args.image,
        caption=args.caption,
    )

    print(json.dumps({
        "status": "ok",
        "message_id": msg.get("message_id"),
        "chat_id": msg.get("chat", {}).get("id"),
    }))


if __name__ == "__main__":
    main()
