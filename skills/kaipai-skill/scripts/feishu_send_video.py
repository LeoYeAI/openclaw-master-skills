#!/usr/bin/env python3
"""
Send video messages via Feishu (Lark).

Usage:
    python3 feishu_send_video.py \\
        --video /path/to/video.mp4 \\
        --to ou_xxx \\
        [--cover /path/to/cover.jpg | --cover-url https://...] \\
        [--duration 20875] \\
        [--video-url https://...]
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

JSON_UTF8 = "application/json; charset=utf-8"


def get_feishu_credentials():
    """Read Feishu credentials from openclaw config."""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path) as f:
        config = json.load(f)
    feishu = config.get("channels", {}).get("feishu", {})
    accounts = feishu.get("accounts", {})
    if accounts:
        main_acct = accounts.get(
            "main",
            accounts.get("default", list(accounts.values())[0] if accounts else {}),
        )
        app_id = main_acct.get("appId", "")
        app_secret = main_acct.get("appSecret", "")
    else:
        app_id = feishu.get("appId", "")
        app_secret = feishu.get("appSecret", "")
    if not app_id or not app_secret:
        print(
            json.dumps(
                {
                    "error": "Feishu credentials not found in ~/.openclaw/openclaw.json",
                    "hint": "Configure channels.feishu.accounts.main.appId and appSecret",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    return app_id, app_secret


def get_tenant_token():
    """Get tenant access token from Feishu."""
    app_id, app_secret = get_feishu_credentials()
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
    )
    resp.raise_for_status()
    return resp.json()["tenant_access_token"]


def normalize_recipient(to: str) -> tuple[str, str]:
    """Return (receive_id, receive_id_type) with chat:/user: stripped."""
    if to.startswith("chat:"):
        to = to[5:]
    elif to.startswith("user:"):
        to = to[5:]
    if to.startswith("oc_"):
        return to, "chat_id"
    return to, "open_id"


def upload_video(token, video_path, duration_ms=None):
    """Upload video file, return file_key."""
    data = {"file_type": "mp4", "file_name": os.path.basename(video_path)}
    if duration_ms:
        data["duration"] = str(int(duration_ms))

    with open(video_path, "rb") as f:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/files",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files={"file": (os.path.basename(video_path), f, "video/mp4")},
            timeout=(15, 120),
        )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Upload failed: {result}")
    return result["data"]["file_key"]


def upload_cover(token, cover_source):
    """Upload cover image, return image_key. cover_source can be a local path or URL."""
    if cover_source.startswith("http"):
        img_resp = requests.get(cover_source, timeout=30)
        img_resp.raise_for_status()
        img_data = img_resp.content
        filename = "cover.jpg"
    else:
        with open(cover_source, "rb") as f:
            img_data = f.read()
        filename = os.path.basename(cover_source)

    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        data={"image_type": "message"},
        files={"image": (filename, img_data, "image/jpeg")},
        timeout=(15, 60),
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Cover upload failed: {result}")
    return result["data"]["image_key"]


def send_media_message(token, receive_id, receive_id_type, file_key, image_key=None):
    """Send media message via Feishu."""
    content = {"file_key": file_key}
    if image_key:
        content["image_key"] = image_key

    resp = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": JSON_UTF8,
        },
        json={
            "receive_id": receive_id,
            "msg_type": "media",
            "content": json.dumps(content),
        },
        timeout=(15, 30),
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Send failed: {result}")
    return result["data"]["message_id"]


def send_text_message(token, receive_id, receive_id_type, text: str):
    """Send plain text message (supports Feishu [label](url) links in text)."""
    resp = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": JSON_UTF8,
        },
        json={
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}),
        },
        timeout=(15, 30),
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Text send failed: {result}")
    return result["data"]["message_id"]


def main():
    parser = argparse.ArgumentParser(description="Send video messages via Feishu")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient open_id (ou_xxx) or group chat_id (oc_xxx)",
    )
    parser.add_argument("--cover", help="Cover image path or URL")
    parser.add_argument("--cover-url", help="Cover image URL (alias for --cover)")
    parser.add_argument("--duration", type=int, help="Video duration in milliseconds")
    parser.add_argument(
        "--video-url",
        default="",
        help="Result URL: always sends an extra text message with this download link after the video step",
    )
    args = parser.parse_args()

    cover = args.cover or args.cover_url
    video_url = (args.video_url or "").strip()
    receive_id, receive_id_type = normalize_recipient(args.to)

    token = get_tenant_token()
    print(f"[feishu] Uploading video: {args.video}", file=sys.stderr)
    file_key = upload_video(token, args.video, args.duration)
    print(f"[feishu] Video file_key: {file_key}", file=sys.stderr)

    image_key = None
    if cover:
        print(f"[feishu] Uploading cover: {cover}", file=sys.stderr)
        image_key = upload_cover(token, cover)
        print(f"[feishu] Cover image_key: {image_key}", file=sys.stderr)

    media_message_id = None
    media_error = None
    try:
        media_message_id = send_media_message(
            token, receive_id, receive_id_type, file_key, image_key
        )
        print(f"[feishu] Media message_id: {media_message_id}", file=sys.stderr)
    except Exception as exc:
        media_error = str(exc)
        print(f"[feishu] Media send error: {media_error}", file=sys.stderr)

    text_message_id = None
    text_error = None
    if video_url:
        link_text = f"视频下载：[链接]({video_url})"
        try:
            text_message_id = send_text_message(
                token, receive_id, receive_id_type, link_text
            )
            print(f"[feishu] Text message_id: {text_message_id}", file=sys.stderr)
        except Exception as exc:
            text_error = str(exc)
            print(f"[feishu] Text send error: {text_error}", file=sys.stderr)

    if video_url:
        ok = bool(media_message_id or text_message_id)
    else:
        ok = bool(media_message_id)

    out = {
        "status": "ok" if ok else "failed",
        "message_id": media_message_id,
        "media_message_id": media_message_id,
        "text_message_id": text_message_id,
        "file_key": file_key,
        "image_key": image_key,
    }
    if media_error:
        out["media_error"] = media_error
    if text_error:
        out["text_error"] = text_error

    print(json.dumps(out))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
