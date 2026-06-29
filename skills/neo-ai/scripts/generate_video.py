#!/usr/bin/env python3
"""
Neodomain AI - Video Generation Script
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://story.neodomain.cn/agent/user/video"
POLL_INTERVAL = 5  # seconds


def submit_video_generation(token: str, **params):
    """Submit video generation request."""
    url = f"{BASE_URL}/generate"
    
    payload = {
        "modelName": params.get("model", "doubao-seedance-1-5-pro-251215"),
        "generationType": params.get("generation_type", "TEXT_TO_VIDEO"),
        "prompt": params.get("prompt"),
        "aspectRatio": params.get("aspect_ratio", "16:9"),
        "resolution": params.get("resolution", "720p"),
        "duration": params.get("duration", "8s"),
        "fps": params.get("fps", 24),
    }
    
    # Add optional parameters
    if params.get("negative_prompt"):
        payload["negativePrompt"] = params["negative_prompt"]
    if params.get("first_frame"):
        payload["firstFrameImageUrl"] = params["first_frame"]
    if params.get("last_frame"):
        payload["lastFrameImageUrl"] = params["last_frame"]
    if params.get("image_urls"):
        payload["imageUrls"] = params["image_urls"]
    if params.get("video_urls"):
        payload["referenceVideoUrls"] = params["video_urls"]
    if params.get("audio_urls"):
        payload["audioUrl"] = params["audio_urls"]
    if params.get("seed"):
        payload["seed"] = params["seed"]
    if params.get("generate_audio"):
        payload["generateAudio"] = params["generate_audio"]
    if params.get("enhance_prompt"):
        payload["enhancePrompt"] = params["enhance_prompt"]
    
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
    url = f"{BASE_URL}/status/{generation_record_id}"
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
    parser = argparse.ArgumentParser(description="Generate videos with Neodomain AI")
    
    # Required
    parser.add_argument("--prompt", required=True, help="Video prompt/description")
    
    # Model options
    parser.add_argument("--model", default="doubao-seedance-1-5-pro-251215", help="Model name")
    parser.add_argument("--generation-type", default="TEXT_TO_VIDEO",
                        choices=["TEXT_TO_VIDEO", "IMAGE_TO_VIDEO", "REFERENCE_TO_VIDEO", "UNIVERSAL_TO_VIDEO"],
                        help="Generation type")
    
    # Image inputs (for IMAGE_TO_VIDEO and REFERENCE_TO_VIDEO)
    parser.add_argument("--first-frame", help="First frame image URL (for IMAGE_TO_VIDEO)")
    parser.add_argument("--last-frame", help="Last frame image URL (optional)")
    parser.add_argument("--image-urls", help="Comma-separated reference image URLs (for REFERENCE_TO_VIDEO / UNIVERSAL_TO_VIDEO)")
    parser.add_argument("--video-urls", help="Comma-separated reference video URLs (for UNIVERSAL_TO_VIDEO)")
    parser.add_argument("--audio-urls", help="Comma-separated reference audio URLs (for UNIVERSAL_TO_VIDEO)")
    
    # Video options
    parser.add_argument("--aspect-ratio", default="16:9",
                        choices=["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "9:21", "auto"],
                        help="Aspect ratio (TEXT_TO_VIDEO only; IMAGE_TO_VIDEO uses 'auto' based on reference image)")
    parser.add_argument("--resolution", default="720p",
                        choices=["480p", "720p", "768p", "1080p", "2k", "4K"],
                        help="Resolution (supported values vary by model)")
    parser.add_argument("--duration", default="8s",
                        help="Duration in seconds, e.g. 5s, 8s, 10s (supported values vary by model)")
    parser.add_argument("--fps", type=int, default=24, help="Frame rate")
    parser.add_argument("--seed", type=int, help="Random seed")
    
    # Advanced options
    parser.add_argument("--negative-prompt", help="Negative prompt")
    parser.add_argument("--generate-audio", action="store_true", help="Generate audio")
    parser.add_argument("--enhance-prompt", action="store_true", help="Enhance prompt")
    
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
    
    # Parse media URLs
    image_urls = []
    if args.image_urls:
        image_urls = [url.strip() for url in args.image_urls.split(",")]
    video_urls = []
    if args.video_urls:
        video_urls = [url.strip() for url in args.video_urls.split(",")]
    audio_urls = []
    if args.audio_urls:
        audio_urls = [url.strip() for url in args.audio_urls.split(",")]
    
    # Validate generation type requirements
    if args.generation_type == "IMAGE_TO_VIDEO" and not args.first_frame:
        print("❌ Error: --first-frame is required for IMAGE_TO_VIDEO", file=sys.stderr)
        sys.exit(1)
    if args.generation_type == "REFERENCE_TO_VIDEO" and not image_urls:
        print("❌ Error: --image-urls is required for REFERENCE_TO_VIDEO", file=sys.stderr)
        sys.exit(1)
    if args.generation_type == "UNIVERSAL_TO_VIDEO" and not image_urls and not video_urls and not audio_urls and not args.first_frame:
        print("⚠️  Warning: UNIVERSAL_TO_VIDEO without any reference media (--image-urls / --video-urls / --audio-urls / --first-frame)", file=sys.stderr)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Generating video...")
    print(f"   Prompt: {args.prompt}")
    print(f"   Model: {args.model}")
    print(f"   Type: {args.generation_type}")
    print(f"   Resolution: {args.resolution}, Duration: {args.duration}")
    
    # Submit generation
    result = submit_video_generation(
        args.token,
        model=args.model,
        generation_type=args.generation_type,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        first_frame=args.first_frame,
        last_frame=args.last_frame,
        image_urls=image_urls,
        video_urls=video_urls,
        audio_urls=audio_urls,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        duration=args.duration,
        fps=args.fps,
        seed=args.seed,
        generate_audio=args.generate_audio,
        enhance_prompt=args.enhance_prompt,
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
        elif status == "PROCESSING":
            desc = status_data.get("statusDesc", "")
            print(f"\n   {desc}", end="", flush=True)
    
    # Download video and thumbnail
    video_url = status_data.get("ossVideoUrl")
    thumbnail_url = status_data.get("thumbnailUrl")
    
    metadata = {
        "generation_record_id": record_id,
        "prompt": args.prompt,
        "model": args.model,
        "generation_type": args.generation_type,
        "resolution": args.resolution,
        "duration": args.duration,
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
    }
    
    if video_url:
        video_path = output_dir / "video.mp4"
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
