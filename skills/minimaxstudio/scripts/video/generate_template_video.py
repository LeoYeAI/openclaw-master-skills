#!/usr/bin/env python3
"""
MiniMax Template Video Generation CLI.

Generate videos from pre-defined templates by providing media and text inputs.

Usage (from project root):
    python scripts/video/generate_template_video.py \\
        --template-id T00001 \\
        --media image1.jpg image2.jpg \\
        --text "Title" "Subtitle" \\
        --output output/template_video.mp4

    python scripts/video/generate_template_video.py \\
        --template-id T00002 \\
        --media https://example.com/photo.jpg \\
        --text "Welcome" \\
        --output output/welcome.mp4
"""

import argparse
import os
import pathlib
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from env_loader import load_dotenv
load_dotenv()

API_BASE = "https://api.minimaxi.com/v1"
TEMPLATE_URL = f"{API_BASE}/video_generation/template"
TEMPLATE_QUERY_URL = f"{API_BASE}/query/video_generation"
FILE_RETRIEVE_URL = f"{API_BASE}/files/retrieve"

POLL_INTERVAL = 10
MAX_WAIT_TIME = 600
REQUEST_TIMEOUT = 60
MAX_CONSECUTIVE_FAILURES = 5


def create_template_task(template_id, media_inputs, text_inputs, headers):
    """Create a template-based video generation task."""
    payload = {
        "template_id": template_id,
    }

    if media_inputs:
        payload["media_inputs"] = media_inputs

    if text_inputs:
        payload["text_inputs"] = text_inputs

    print(f"Creating template video task (template: {template_id})...")
    resp = requests.post(TEMPLATE_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if "base_resp" in data and data["base_resp"].get("status_code", 0) != 0:
        raise RuntimeError(f"API error: {data['base_resp']}")

    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {data}")

    print(f"Task created: {task_id}")
    return task_id


def poll_template_task(task_id, headers):
    """Poll template task status until completion or timeout. Returns (status, file_id)."""
    print(f"Polling task {task_id}...")
    start_time = time.time()
    consecutive_failures = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(f"Task {task_id} timed out after {MAX_WAIT_TIME}s")

        try:
            resp = requests.get(
                TEMPLATE_QUERY_URL,
                headers=headers,
                params={"task_id": task_id},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            consecutive_failures = 0
        except Exception as e:
            consecutive_failures += 1
            print(f"  Poll error ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}): {e}")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise RuntimeError(f"Too many consecutive poll failures for task {task_id}")
            time.sleep(POLL_INTERVAL)
            continue

        status = data.get("status", "Unknown")
        print(f"  [{int(elapsed)}s] Status: {status}")

        if status == "Success":
            file_id = data.get("file_id")
            if not file_id:
                raise RuntimeError(f"Task succeeded but no file_id: {data}")
            return status, file_id

        if status in ("Fail", "Failed", "Error"):
            error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
            raise RuntimeError(f"Task failed: {error_msg} (full response: {data})")

        time.sleep(POLL_INTERVAL)


def download_template_video(file_id, output_path, headers):
    """Download the generated template video file."""
    print(f"Retrieving file {file_id}...")
    resp = requests.get(
        FILE_RETRIEVE_URL,
        headers=headers,
        params={"file_id": file_id},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    download_url = data.get("file", {}).get("download_url")
    if not download_url:
        raise RuntimeError(f"No download_url in file response: {data}")

    print(f"Downloading video...")
    video_resp = requests.get(download_url, timeout=REQUEST_TIMEOUT * 3)
    video_resp.raise_for_status()

    output = pathlib.Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(video_resp.content)
    print(f"Video saved to: {output_path} ({len(video_resp.content)} bytes)")
    return str(output)


def resolve_media_input(value):
    """Resolve a media input to a URL or read a local file."""
    if value.startswith(("http://", "https://", "data:")):
        return value

    import base64
    import mimetypes

    path = pathlib.Path(value)
    if not path.exists():
        raise FileNotFoundError(f"Media file not found: {value}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Template Video Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--template-id", dest="template_id", required=True,
                        help="Template ID to use")
    parser.add_argument("--media", nargs="+",
                        help="Media inputs (image paths or URLs)")
    parser.add_argument("--text", nargs="+",
                        help="Text inputs for template placeholders")
    parser.add_argument("--output", "-o", required=True, help="Output video file path")

    args = parser.parse_args()

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("Error: MINIMAX_API_KEY environment variable is not set.")
        return 1

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    media_inputs = None
    if args.media:
        media_inputs = []
        for i, m in enumerate(args.media):
            try:
                resolved = resolve_media_input(m)
                media_inputs.append({"index": i, "url": resolved})
                print(f"  Media [{i}]: {m}")
            except Exception as e:
                print(f"Error resolving media input '{m}': {e}")
                return 1

    text_inputs = None
    if args.text:
        text_inputs = []
        for i, t in enumerate(args.text):
            text_inputs.append({"index": i, "text": t})
            print(f"  Text [{i}]: {t}")

    try:
        task_id = create_template_task(args.template_id, media_inputs, text_inputs, headers)
        status, file_id = poll_template_task(task_id, headers)
        download_template_video(file_id, args.output, headers)
        print("Done!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
