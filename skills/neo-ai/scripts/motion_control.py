#!/usr/bin/env python3
"""
Neodomain AI - Motion Control Video Generation
Generate video by applying motion from a reference video to an image.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://story.neodomain.cn/agent/user/video/motion-control"
POLL_INTERVAL = 5  # seconds


def submit_motion_control(token: str, **params):
    """Submit motion control video generation request."""
    url = f"{BASE_URL}/generate"
    
    payload = {
        "imageUrl": params.get("image_url"),
        "videoUrl": params.get("video_url"),
        "characterOrientation": params.get("orientation", "image"),
        "mode": params.get("mode", "std"),
        "videoDuration": params.get("duration", 5000),
    }
    
    if params.get("prompt"):
        payload["prompt"] = params["prompt"]
    if params.get("keep_original_sound"):
        payload["keepOriginalSound"] = params["keep_original_sound"]
    
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "accessToken": token
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def check_status(token: str, generation_record_id: str):
    """Check video generation status."""
    url = f"https://story.neodomain.cn/agent/user/video/status/{generation_record_id}"
    headers = {"accessToken": token}
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def download_file(url: str, output_path: str):
    """Download file from URL."""
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate motion control video")
    
    # Required
    parser.add_argument("--image", "--image-url", "image", required=True,
                        dest="image", help="Reference image URL")
    parser.add_argument("--video", "--video-url", "video", required=True,
                        dest="video", help="Reference video URL")
    
    # Optional
    parser.add_argument("--prompt", help="Text prompt for additional control")
    parser.add_argument("--orientation", default="image",
                        choices=["image", "video"],
                        help="Character orientation source")
    parser.add_argument("--mode", default="std", choices=["std", "pro"],
                        help="Generation mode")
    parser.add_argument("--keep-original-sound", default="yes",
                        choices=["yes", "no"],
                        help="Keep original sound from reference video")
    parser.add_argument("--duration", type=int, default=5000,
                        help="Video duration in milliseconds")
    
    # Output
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--token", "--access-token", dest="token", help="Access token")
    
    args = parser.parse_args()
    
    # Get token
    if not args.token:
        args.token = os.environ.get("NEODOMAIN_ACCESS_TOKEN")
    
    if not args.token:
        print("❌ Error: Access token required", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Generating motion control video...")
    print(f"   Image: {args.image}")
    print(f"   Video: {args.video}")
    print(f"   Mode: {args.mode}, Duration: {args.duration}ms")
    
    # Submit generation
    result = submit_motion_control(
        args.token,
        image_url=args.image,
        video_url=args.video,
        prompt=args.prompt,
        orientation=args.orientation,
        mode=args.mode,
        keep_original_sound=args.keep_original_sound,
        duration=args.duration,
    )
    
    if not result.get("success"):
        print(f"❌ Failed: {result.get('errMessage')}", file=sys.stderr)
        sys.exit(1)
    
    task_data = result.get("data", {})
    record_id = task_data.get("generationRecordId")
    print(f"   Record ID: {record_id}")
    
    # Poll for result
    print("⏳ Waiting for generation...", end="", flush=True)
    
    while True:
        time.sleep(POLL_INTERVAL)
        print(".", end="", flush=True)
        
        status_result = check_status(args.token, record_id)
        status_data = status_result.get("data", {})
        status = status_data.get("status")
        
        if status == "SUCCESS":
            print("\n✅ Done!")
            break
        elif status == "FAILED":
            print(f"\n❌ Failed: {status_data.get('errorMessage')}", file=sys.stderr)
            sys.exit(1)
    
    # Download video and thumbnail
    video_url = status_data.get("ossVideoUrl")
    thumbnail_url = status_data.get("thumbnailUrl")
    
    metadata = {
        "generation_record_id": record_id,
        "image_url": args.image,
        "video_url": args.video,
        "mode": args.mode,
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
    }
    
    if video_url:
        video_path = output_dir / "motion_video.mp4"
        if download_file(video_url, str(video_path)):
            print(f"   ✅ Saved: {video_path}")
    
    if thumbnail_url:
        thumbnail_path = output_dir / "thumbnail.jpg"
        if download_file(thumbnail_url, str(thumbnail_path)):
            print(f"   ✅ Saved: {thumbnail_path}")
    
    # Save metadata
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✨ Complete! Output in: {output_dir}")


if __name__ == "__main__":
    main()
