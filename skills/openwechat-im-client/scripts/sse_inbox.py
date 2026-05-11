#!/usr/bin/env python3
"""
Push inbox script: connects to GET /stream and appends received messages to ../openwechat_im_client/inbox_pushed.md.
On disconnect, appends a disconnect record.
Records connection lifecycle (connect/disconnect/fail) to ../openwechat_im_client/sse_channel.log so the model knows connection status.
Usage: run from the Skill root directory, or have the model invoke it after the user agrees to enable push.
Requires: requests (or urllib); ../openwechat_im_client/config.json must contain base_url and token.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Script is in scripts/; data in sibling of skill root (../openwechat_im_client)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_ROOT, "..", "openwechat_im_client")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
INBOX_PUSHED_PATH = os.path.join(DATA_DIR, "inbox_pushed.md")
SSE_CHANNEL_LOG_PATH = os.path.join(DATA_DIR, "sse_channel.log")
SEP = "─" * 40


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def append_message(payload: str):
    ensure_data_dir()
    need_sep = os.path.exists(INBOX_PUSHED_PATH) and os.path.getsize(INBOX_PUSHED_PATH) > 0
    with open(INBOX_PUSHED_PATH, "a", encoding="utf-8") as f:
        if need_sep:
            f.write("\n" + SEP + "\n")
        f.write(payload.strip())
        f.write("\n")


def append_disconnect():
    ensure_data_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(INBOX_PUSHED_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + SEP + "\n[Disconnected] " + ts + "\n")


def log_channel(event: str, **kwargs):
    """Append a channel lifecycle event to sse_channel.log so the model knows connection status."""
    ensure_data_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts = [f"[{ts}]", event]
    for k, v in kwargs.items():
        parts.append(f"{k}={v}")
    line = " ".join(parts) + "\n"
    with open(SSE_CHANNEL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    parser = argparse.ArgumentParser(
        description="Connect to GET /stream; append messages to inbox_pushed.md."
    )
    parser.parse_args()

    ensure_data_dir()
    cfg = load_config()
    if not cfg or not cfg.get("token") or not cfg.get("base_url"):
        print(
            "../openwechat_im_client/config.json not found or missing base_url/token. "
            "See SKILL.md for config format. Create config.json in ../openwechat_im_client with base_url and token."
        )
        sys.exit(1)

    base_url = cfg["base_url"].rstrip("/")
    token = cfg["token"]
    stream_url = base_url + "/stream"

    try:
        import requests
    except ImportError:
        print("requests is required: pip install requests")
        sys.exit(1)

    headers = {"X-Token": token, "Accept": "text/event-stream"}
    log_channel("SSE_CONNECT_START")
    try:
        r = requests.get(stream_url, headers=headers, stream=True, timeout=60)
        r.raise_for_status()
        log_channel("SSE_CONNECTED")
    except requests.exceptions.HTTPError as e:
        reason = f"http_{e.response.status_code}"
        log_channel("SSE_CONNECT_FAILED", reason=reason)
        if e.response.status_code == 429:
            print("Error: SSE connection limit reached for this IP (max 1).")
        elif e.response.status_code == 401:
            print("Error: Invalid token.")
        else:
            print(f"Connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        log_channel("SSE_CONNECT_FAILED", reason=str(e))
        print(f"Connection failed: {e}")
        sys.exit(1)

    disconnect_reason = "stream_end"
    try:
        buf = []
        current_event = "message"  # 默认兼容无 event 的旧格式
        for line in r.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                buf.append(line[5:].lstrip())
            elif line == "" and buf:
                full = "\n".join(buf)
                buf = []
                if full.strip() and not full.strip().startswith(": ping"):
                    if current_event == "log":
                        # 服务端日志事件：写入 sse_channel.log，不入收件箱
                        ensure_data_dir()
                        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                        with open(SSE_CHANNEL_LOG_PATH, "a", encoding="utf-8") as f:
                            f.write(f"[{ts}] [server] {full.strip()}\n")
                    else:
                        append_message(full)
    except Exception as e:
        disconnect_reason = str(e)
        print(f"Error reading stream: {e}", file=sys.stderr)
    finally:
        log_channel("SSE_DISCONNECTED", reason=disconnect_reason)
        append_disconnect()
        print("SSE disconnected; disconnect record written to ../openwechat_im_client/inbox_pushed.md.")


if __name__ == "__main__":
    main()
