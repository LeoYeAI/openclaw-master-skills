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
import json
import mimetypes
import os
import pathlib
import sys
import time
from urllib.parse import quote

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from env_loader import load_dotenv
load_dotenv()

API_BASE = "https://api.minimaxi.com/v1"
VIDEO_GENERATION_URL = f"{API_BASE}/video_generation"
QUERY_URL = f"{API_BASE}/query/video_generation"
FILE_RETRIEVE_URL = f"{API_BASE}/files/retrieve"

H3_MODEL = "MiniMax-H3"
REGIONAL_BASES = {
    "global_en": "https://api.minimax.io",
    "cn_zh": "https://api.minimaxi.com",
}
H3_RATIOS = ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]

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


for models in VALID_MODELS.values():
    models.append(H3_MODEL)


def api_url(path, region="cn_zh", api_version="v1"):
    """Select the region without changing the legacy defaults for callers."""
    return f"{REGIONAL_BASES[region]}/{api_version}/{path}"


def build_h3_payload(args):
    """Build the v2 content request for the existing generation modes."""
    if not args.prompt or not args.prompt.strip() or len(args.prompt) > 7000:
        raise ValueError("MiniMax-H3 requires a non-empty --prompt of at most 7000 characters")
    if type(args.duration) is not int or not 4 <= args.duration <= 15:
        raise ValueError("MiniMax-H3 --duration must be an integer from 4 to 15")
    resolution = args.resolution or "2K"
    if resolution != "2K":
        raise ValueError("MiniMax-H3 --resolution must be 2K")
    if args.prompt_optimizer is not None or args.fast_pretreatment is not None:
        raise ValueError("--prompt-optimizer and --fast-pretreatment require a legacy model")
    if args.aigc_watermark is not None and getattr(args, "region", "cn_zh") != "cn_zh":
        raise ValueError("--aigc-watermark is only available in the cn_zh region")

    reference_video = getattr(args, "reference_video", None)
    reference_audio = getattr(args, "reference_audio", None)
    has_frames = bool(args.first_frame or args.last_frame)
    has_references = bool(args.subject_image or reference_video or reference_audio)
    if has_frames and has_references:
        raise ValueError("Frame inputs and reference inputs cannot be mixed")
    if args.mode == "t2v" and (has_frames or has_references):
        raise ValueError("t2v mode only accepts a text prompt")
    if args.mode in ("i2v", "sef"):
        if not args.first_frame or has_references:
            raise ValueError("Frame modes require --first-frame and cannot use reference inputs")
        if args.mode == "i2v" and args.last_frame:
            raise ValueError("Use sef mode for --last-frame")
    if args.mode == "ref" and (has_frames or not (args.subject_image or reference_video)):
        raise ValueError("ref mode requires --subject-image or --reference-video without frame inputs")

    content = [{"type": "text", "text": args.prompt}]
    for value, kind, role in (
        (args.first_frame, "image_url", "first_frame"),
        (args.last_frame, "image_url", "last_frame"),
        (args.subject_image, "image_url", "reference_image"),
        (reference_video, "video_url", "reference_video"),
        (reference_audio, "audio_url", "reference_audio"),
    ):
        if value:
            if kind == "image_url":
                value = resolve_image(value)
            elif not value.startswith(("https://", "http://")):
                raise ValueError("Reference video and audio inputs must be public URLs")
            content.append({"type": kind, kind: {"url": value}, "role": role})

    ratio = getattr(args, "ratio", None) or ("16:9" if args.mode == "t2v" else "adaptive")
    if ratio not in H3_RATIOS or (args.mode == "t2v" and ratio == "adaptive"):
        raise ValueError("Use a supported --ratio; t2v requires a concrete aspect ratio")
    payload = {
        "model": H3_MODEL, "content": content, "duration": args.duration,
        "resolution": resolution, "ratio": ratio,
    }
    if args.callback_url:
        payload["callback_url"] = args.callback_url
    if args.aigc_watermark is not None:
        payload["aigc_watermark"] = bool(args.aigc_watermark)
    if len(json.dumps(payload).encode("utf-8")) > 64 * 1024 * 1024:
        raise ValueError("The request body exceeds 64 MB; use public media URLs")
    return payload


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

    if model == H3_MODEL:
        return build_h3_payload(args)
    if any(getattr(args, name, None) for name in ("ratio", "reference_video", "reference_audio")):
        raise ValueError("--ratio and reference video/audio inputs require MiniMax-H3")

    payload = {
        "model": model,
    }

    if args.prompt:
        payload["prompt"] = args.prompt

    if args.duration:
        payload["duration"] = args.duration

    payload["resolution"] = args.resolution or "768P"

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


def create_task(payload, headers, region="cn_zh"):
    """Submit a video generation task and return the task_id."""
    print(f"Creating video generation task...")
    api_version = "v2" if payload["model"] == H3_MODEL else "v1"
    resp = requests.post(api_url("video_generation", region, api_version),
                         headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if "base_resp" in data and data["base_resp"].get("status_code", 0) != 0:
        raise RuntimeError(f"API error: {data['base_resp']}")

    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {data}")

    print(f"Task created: {task_id}")
    return task_id


def poll_task(task_id, headers, region="cn_zh", api_version="v1"):
    """Return (status, download URL for v2 or file ID for v1)."""
    print(f"Polling task {task_id}...")
    query_url = api_url("query/video_generation", region, api_version)
    params = {"task_id": task_id}
    if api_version == "v2":
        query_url += "/" + quote(str(task_id), safe="")
        params = None
    start_time = time.time()
    consecutive_failures = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(f"Task {task_id} timed out after {MAX_WAIT_TIME}s")

        try:
            resp = requests.get(
                query_url,
                headers=headers,
                params=params,
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

        if data.get("base_resp", {}).get("status_code", 0) != 0:
            raise RuntimeError(f"API error: {data['base_resp']}")
        task = data.get("task", {}) if api_version == "v2" else data
        status = task.get("status", "Unknown")
        print(f"  [{int(elapsed)}s] Status: {status}")

        if api_version == "v2":
            if status == "succeeded":
                download_url = task.get("content", {}).get("url")
                if not download_url:
                    raise RuntimeError("Task succeeded but no task.content.url was returned")
                return status, download_url
            if status in ("failed", "cancelled"):
                raise RuntimeError(f"Task {status}: {task.get('error') or 'No error detail'}")

        if api_version == "v1" and status == "Success":
            file_id = data.get("file_id")
            if not file_id:
                raise RuntimeError(f"Task succeeded but no file_id: {data}")
            return status, file_id

        if status in ("Fail", "Failed", "Error"):
            error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
            raise RuntimeError(f"Task failed: {error_msg} (full response: {data})")

        time.sleep(POLL_INTERVAL)


def download_video(file_id, output_path, headers, region="cn_zh", api_version="v1"):
    """Download a v2 result URL directly or retrieve a legacy file ID first."""
    if api_version == "v2":
        download_url = file_id
    else:
        print(f"Retrieving file {file_id}...")
        resp = requests.get(
            api_url("files/retrieve", region),
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
    parser.add_argument("--model", default=H3_MODEL, help="Model name (default: MiniMax-H3)")
    parser.add_argument("--region", choices=REGIONAL_BASES, default="cn_zh",
                        help="API region (default: cn_zh)")
    parser.add_argument("--duration", type=int, default=10, help="Video duration in seconds (default: 10)")
    parser.add_argument("--resolution", help="Video resolution (default: 2K for H3, 768P for legacy)")
    parser.add_argument("--ratio", choices=H3_RATIOS, help="H3 aspect ratio (t2v default: 16:9)")

    frames = parser.add_argument_group("frame inputs")
    frames.add_argument("--first-frame", dest="first_frame", help="First frame image (path or URL)")
    frames.add_argument("--last-frame", dest="last_frame", help="Last frame image (path or URL, sef mode)")
    frames.add_argument("--subject-image", dest="subject_image", help="Subject reference image (ref mode)")

    frames.add_argument("--reference-video", help="Public reference video URL (H3 ref mode)")
    frames.add_argument("--reference-audio", help="Public reference audio URL (H3 ref mode)")

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

        api_version = "v2" if payload["model"] == H3_MODEL else "v1"
        task_id = create_task(payload, headers, args.region)
        status, result = poll_task(task_id, headers, args.region, api_version)
        download_video(result, args.output, headers, args.region, api_version)
        print("Done!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
