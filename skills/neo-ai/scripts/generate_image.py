#!/usr/bin/env python3
"""
Neodomain AI - Image Generation Script
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

BASE_URL = "https://story.neodomain.cn/agent/ai-image-generation"
POLL_INTERVAL = 3  # seconds


def submit_generation(token: str, **params):
    """Submit image generation request."""
    url = f"{BASE_URL}/generate"
    
    payload = {
        "prompt": params.get("prompt"),
        "negativePrompt": params.get("negative_prompt", ""),
        "modelName": params.get("model", "doubao-seedream-4-0"),
        "imageUrls": params.get("image_urls", []),
        "aspectRatio": params.get("aspect_ratio", "1:1"),
        "numImages": params.get("num_images", "1"),
        "outputFormat": params.get("output_format", "jpeg"),
        "syncMode": params.get("sync_mode", False),
        "safetyTolerance": params.get("safety_tolerance", "5"),
        "guidanceScale": params.get("guidance_scale", 7.5),
        "size": params.get("size", "2K"),
        "showPrompt": params.get("show_prompt", True),
    }
    
    if params.get("seed"):
        payload["seed"] = params["seed"]
    
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


def check_result(token: str, task_code: str):
    """Check generation result."""
    url = f"{BASE_URL}/result/{task_code}"
    headers = {"accessToken": token}
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def download_image(url: str, output_path: str):
    """Download image from URL."""
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate images with Neodomain AI")
    parser.add_argument("--prompt", required=True, help="Image prompt/description")
    parser.add_argument("--negative-prompt", help="Negative prompt")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview", help="Model name")
    parser.add_argument("--reference-image", "--ref", dest="reference_images", action="append",
                        help="Reference image URL(s) for I2I (can specify multiple, up to 10)")
    parser.add_argument("--aspect-ratio", default="1:1", 
                        choices=["1:1", "16:9", "9:16", "4:3", "3:4"], help="Aspect ratio")
    parser.add_argument("--num-images", default="1", choices=["1", "4"], help="Number of images")
    parser.add_argument("--size", default="2K", choices=["1K", "2K", "4K"], help="Image size")
    parser.add_argument("--guidance-scale", type=float, default=7.5, help="Guidance scale (1-20)")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--output-format", default="jpeg", choices=["jpeg", "png", "webp"])
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
    
    print(f"🎨 Generating image...")
    print(f"   Prompt: {args.prompt}")
    print(f"   Model: {args.model}")
    print(f"   Aspect: {args.aspect_ratio}, Size: {args.size}")
    
    # Prepare reference images (support up to 10)
    image_urls = []
    if args.reference_images:
        image_urls = args.reference_images[:10]  # Limit to 10
        if len(args.reference_images) > 10:
            print(f"⚠️ Warning: More than 10 reference images provided, using first 10", file=sys.stderr)
        print(f"   References: {len(image_urls)} image(s)")
    
    # Submit generation
    result = submit_generation(
        args.token,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        model=args.model,
        image_urls=image_urls,
        aspect_ratio=args.aspect_ratio,
        num_images=args.num_images,
        size=args.size,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        output_format=args.output_format,
    )
    
    if not result.get("success"):
        print(f"❌ Failed: {result.get('errMessage')}", file=sys.stderr)
        sys.exit(1)
    
    task_data = result.get("data", {})
    task_code = task_data.get("task_code")
    print(f"   Task: {task_code}")
    
    # Poll for result
    print("⏳ Waiting for generation...", end="", flush=True)
    
    while True:
        time.sleep(POLL_INTERVAL)
        print(".", end="", flush=True)
        
        status_result = check_result(args.token, task_code)
        status_data = status_result.get("data", {})
        status = status_data.get("status")
        
        if status == "SUCCESS":
            print("\n✅ Done!")
            break
        elif status == "FAILED":
            print(f"\n❌ Failed: {status_data.get('failure_reason')}", file=sys.stderr)
            sys.exit(1)
    
    # Download images
    image_urls = status_data.get("image_urls", [])
    print(f"\n📥 Downloading {len(image_urls)} image(s)...")
    
    metadata = {
        "task_code": task_code,
        "prompt": args.prompt,
        "model": args.model,
        "reference_images": image_urls,
        "aspect_ratio": args.aspect_ratio,
        "size": args.size,
        "images": []
    }
    
    for i, url in enumerate(image_urls):
        ext = args.output_format
        filename = f"image_{i+1}.{ext}"
        filepath = output_dir / filename
        
        if download_image(url, str(filepath)):
            print(f"   ✅ Saved: {filepath}")
            metadata["images"].append({
                "filename": filename,
                "url": url
            })
        else:
            print(f"   ❌ Failed: {url}")
    
    # Save metadata
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✨ Complete! Output in: {output_dir}")


if __name__ == "__main__":
    main()
