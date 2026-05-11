"""
Content Claw - Discord Notification Helper

Sends messages and media to the Discord #nemoclaw channel via openclaw CLI.

Usage:
    uv run notify.py "message text" [--media /path/to/image.png]

Or import:
    from notify import send_discord
    send_discord("message", media_path="/tmp/image.png")
"""

import json
import subprocess
import sys


DISCORD_CHANNEL = "channel:nemoclaw"


def send_discord(message: str, media_path: str | None = None, dry_run: bool = False) -> dict:
    """Send a message to Discord #nemoclaw via openclaw CLI."""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "discord",
        "--target", DISCORD_CHANNEL,
        "-m", message,
    ]
    if media_path:
        cmd.extend(["--media", media_path])
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "status": "sent" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except FileNotFoundError:
        return {"status": "error", "error": "openclaw CLI not found. Is OpenClaw installed?"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timed out sending Discord message"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: notify.py 'message' [--media path]"}))
        sys.exit(1)

    message = sys.argv[1]
    media = None
    dry_run = False

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--media" and i + 1 < len(args):
            media = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    result = send_discord(message, media_path=media, dry_run=dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
