#!/usr/bin/env python3
"""
Send image messages via Feishu (Lark)

Usage:
    python3 feishu_send_image.py \
        --image /path/to/image.jpg \
        --to ou_xxx

    # Or with a URL (auto-downloaded):
    python3 feishu_send_image.py \
        --image https://example.com/result.jpg \
        --to oc_xxx

Flow:
    1. Upload image (image_type=message) -> get image_key
    2. Send image message (msg_type=image)

Feishu API reference:
    - Upload image: POST /open-apis/im/v1/images
    - Send message: POST /open-apis/im/v1/messages
"""

import argparse
import json
import os
import sys
import tempfile

try:
    import requests
except ImportError:
    print(json.dumps({
        "error": "requests package not installed",
        "install_command": "pip install requests",
    }), file=sys.stderr)
    sys.exit(1)


def get_feishu_credentials():
    """Read Feishu credentials from openclaw config."""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path) as f:
        config = json.load(f)
    feishu = config.get("channels", {}).get("feishu", {})
    accounts = feishu.get("accounts", {})
    # Try accounts.main first, then top-level
    if accounts:
        main_acct = accounts.get("main", accounts.get("default", list(accounts.values())[0] if accounts else {}))
        app_id = main_acct.get("appId", "")
        app_secret = main_acct.get("appSecret", "")
    else:
        app_id = feishu.get("appId", "")
        app_secret = feishu.get("appSecret", "")
    if not app_id or not app_secret:
        print(json.dumps({
            "error": "Feishu credentials not found in ~/.openclaw/openclaw.json",
            "hint": "Configure channels.feishu.accounts.main.appId and appSecret"
        }), file=sys.stderr)
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


def upload_image(token, image_source):
    """Upload image, return image_key. image_source can be a local path or URL."""
    if image_source.startswith("http"):
        # Download from URL first
        print(f"[feishu] Downloading image: {image_source}", file=sys.stderr)
        img_resp = requests.get(image_source, timeout=(15, 60))
        img_resp.raise_for_status()
        img_data = img_resp.content
        filename = image_source.split("?")[0].split("/")[-1] or "image.jpg"
    else:
        with open(image_source, "rb") as f:
            img_data = f.read()
        filename = os.path.basename(image_source)

    # Guess content type from filename
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "jpg"
    content_type_map = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "webp": "image/webp", "gif": "image/gif",
    }
    content_type = content_type_map.get(ext, "image/jpeg")

    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        data={"image_type": "message"},
        files={"image": (filename, img_data, content_type)},
        timeout=(15, 60),
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise Exception(f"Image upload failed: {result}")
    return result["data"]["image_key"]


def send_image_message(token, to, image_key):
    """Send image message via Feishu."""
    # Strip common prefixes from OpenClaw inbound metadata (e.g. "chat:oc_xxx" → "oc_xxx")
    if to.startswith("chat:"):
        to = to[len("chat:"):]
    elif to.startswith("user:"):
        to = to[len("user:"):]

    # Determine receive_id_type based on prefix
    if to.startswith("oc_"):
        receive_id_type = "chat_id"
    else:
        receive_id_type = "open_id"

    resp = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "receive_id": to,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key}),
        },
        timeout=(15, 30),
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise Exception(f"Send failed: {result}")
    return result["data"]["message_id"]


def main():
    parser = argparse.ArgumentParser(description="Send image messages via Feishu")
    parser.add_argument("--image", required=True, help="Image file path or URL")
    parser.add_argument("--to", required=True, help="Recipient open_id (ou_xxx) or group chat_id (oc_xxx)")
    args = parser.parse_args()

    token = get_tenant_token()
    print(f"[feishu] Uploading image: {args.image}", file=sys.stderr)
    image_key = upload_image(token, args.image)
    print(f"[feishu] Image key: {image_key}", file=sys.stderr)

    msg_id = send_image_message(token, args.to, image_key)
    print(json.dumps({
        "status": "ok",
        "message_id": msg_id,
        "image_key": image_key,
    }))


if __name__ == "__main__":
    main()
