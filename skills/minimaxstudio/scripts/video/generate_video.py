#!/usr/bin/env python3
"""
MiniMax Video Generation CLI.

Usage (from project root):
    python scripts/video/generate_video.py --mode t2v --prompt "A cat playing piano" --output output/cat.mp4
    python scripts/video/generate_video.py --mode i2v --prompt "Gentle breeze" --first-frame image.jpg --output output/anim.mp4
    python scripts/video/generate_video.py --mode sef --prompt "Pan right slowly" --first-frame start.jpg --last-frame end.jpg --output output/sef.mp4
    python scripts/video/generate_video.py --mode ref --prompt "Person dancing" --subject-image person.jpg --output output/ref.mp4
"""

import argparse
import base64
import mimetypes
import os
import pathlib
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from env_loader import load_dotenv
load_dotenv()

API_BASE = "https://api.minimaxi.com/v1"
VIDEO_GENERATION_URL = f"{API_BASE}/video_generation"
QUERY_URL = f"{API_BASE}/query/video_generation"
FILE_RETRIEVE_URL = f"{API_BASE}/files/retrieve"

POLL_INTERVAL = 10
MAX_WAIT_TIME = 600
REQUEST_TIMEOUT = 60
MAX_CONSECUTIVE_FAILURES = 5

MODE_MODELS = {
    "t2v": "MiniMax-Hailuo-2.3",
    "i2v": "MiniMax-Hailuo-2.3",
    "sef": "MiniMax-Hailuo-02",
    "ref": "S2V-01",
}

VALID_MODELS = {
    "t2v": ["MiniMax-Hailuo-2.3", "MiniMax-Hailuo-02", "MiniMax-Hailuo-01", "T2V-01", "T2V-01-Director"],
    "i2v": ["MiniMax-Hailuo-2.3", "MiniMax-Hailuo-02", "MiniMax-Hailuo-01", "I2V-01", "I2V-01-Director", "I2V-01-live"],
    "sef": ["MiniMax-Hailuo-02"],
    "ref": ["S2V-01"],
}


def image_to_data_url(image_path):
    """Convert a local image file to a base64 data URL."""
    path = pathlib.Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = "image/jpeg"

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def resolve_image(image_input):
    """Return a URL as-is, or convert a local path to a data URL."""
    if not image_input:
        return None
    if image_input.startswith(("http://", "https://", "data:")):
        return image_input
    return image_to_data_url(image_input)


def build_payload(args):
    """Build the API request payload based on mode."""
    model = args.model or MODE_MODELS.get(args.mode, "MiniMax-Hailuo-2.3")

    if model not in VALID_MODELS.get(args.mode, []):
        print(f"Warning: Model '{model}' may not be valid for mode '{args.mode}'. "
              f"Valid models: {VALID_MODELS.get(args.mode, [])}")

    payload = {
        "model": model,
    }

    if args.prompt:
        payload["prompt"] = args.prompt

    if args.duration:
        payload["duration"] = args.duration

    if args.resolution:
        payload["resolution"] = args.resolution

    if args.prompt_optimizer is not None:
        payload["prompt_optimizer"] = args.prompt_optimizer

    if args.callback_url:
        payload["callback_url"] = args.callback_url

    if args.aigc_watermark is not None:
        payload["aigc_watermark"] = args.aigc_watermark

    if args.mode == "t2v":
        pass

    elif args.mode == "i2v":
        first_frame = resolve_image(args.first_frame)
        if not first_frame:
            raise ValueError("--first-frame is required for i2v mode")
        payload["first_frame_image"] = first_frame
        if args.fast_pretreatment is not None:
            payload["fast_pretreatment"] = args.fast_pretreatment

    elif args.mode == "sef":
        first_frame = resolve_image(args.first_frame)
        if not first_frame:
            raise ValueError("--first-frame is required for sef mode")
        payload["first_frame_image"] = first_frame
        if args.last_frame:
            payload["last_frame_image"] = resolve_image(args.last_frame)

    elif args.mode == "ref":
        subject_image = resolve_image(args.subject_image)
        if not subject_image:
            raise ValueError("--subject-image is required for ref mode")
        payload["subject_reference"] = [{"type": "character", "image": subject_image}]
        if args.first_frame:
            payload["first_frame_image"] = resolve_image(args.first_frame)

    return payload


def create_task(payload, headers):
    """Submit a video generation task and return the task_id."""
    print(f"Creating video generation task...")
    resp = requests.post(VIDEO_GENERATION_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if "base_resp" in data and data["base_resp"].get("status_code", 0) != 0:
        raise RuntimeError(f"API error: {data['base_resp']}")

    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {data}")

    print(f"Task created: {task_id}")
    return task_id


def poll_task(task_id, headers):
    """Poll task status until completion or timeout. Returns (status, file_id)."""
    print(f"Polling task {task_id}...")
    start_time = time.time()
    consecutive_failures = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(f"Task {task_id} timed out after {MAX_WAIT_TIME}s")

        try:
            resp = requests.get(
                QUERY_URL,
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


def download_video(file_id, output_path, headers):
    """Download the generated video file."""
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


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Video Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", required=True, choices=["t2v", "i2v", "sef", "ref"],
                        help="Generation mode: t2v (text-to-video), i2v (image-to-video), "
                             "sef (start-end frames), ref (subject reference)")
    parser.add_argument("--prompt", help="Text prompt describing the video")
    parser.add_argument("--model", help="Model name (auto-selected per mode if omitted)")
    parser.add_argument("--duration", type=int, default=10, help="Video duration in seconds (default: 10)")
    parser.add_argument("--resolution", default="768P", help="Video resolution (default: 768P)")

    frames = parser.add_argument_group("frame inputs")
    frames.add_argument("--first-frame", dest="first_frame", help="First frame image (path or URL)")
    frames.add_argument("--last-frame", dest="last_frame", help="Last frame image (path or URL, sef mode)")
    frames.add_argument("--subject-image", dest="subject_image", help="Subject reference image (ref mode)")

    advanced = parser.add_argument_group("advanced")
    advanced.add_argument("--prompt-optimizer", dest="prompt_optimizer", type=lambda x: x.lower() == "true",
                          help="Enable prompt optimization (true/false)")
    advanced.add_argument("--fast-pretreatment", dest="fast_pretreatment", type=lambda x: x.lower() == "true",
                          help="Enable fast pretreatment for i2v (true/false)")
    advanced.add_argument("--callback-url", dest="callback_url", help="Webhook callback URL")
    advanced.add_argument("--aigc-watermark", dest="aigc_watermark", type=int, choices=[0, 1],
                          help="AIGC watermark (0=off, 1=on)")

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

    try:
        payload = build_payload(args)
        print(f"Mode: {args.mode}")
        print(f"Model: {payload.get('model')}")

        task_id = create_task(payload, headers)
        status, file_id = poll_task(task_id, headers)
        download_video(file_id, args.output, headers)
        print("Done!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
