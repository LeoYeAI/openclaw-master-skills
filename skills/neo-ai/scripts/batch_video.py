#!/usr/bin/env python3
"""
Generate videos from storyboard images using Neodomain AI API
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
import mimetypes
import uuid
from datetime import datetime

BASE_URL = "https://story.neodomain.cn"

# Video model
MODEL = "doubao-seedance-1-5-pro-251215"
DURATION = "5s"
RESOLUTION = "720p"
ASPECT_RATIO = "16:9"
GENERATE_AUDIO = True

# Polling settings
POLL_INTERVAL = 5  # seconds


def get_sts_token(token: str):
    """Get OSS STS token."""
    url = f"{BASE_URL}/agent/sts/oss/token"
    headers = {"accessToken": token}
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                return result.get("data")
            else:
                print(f"❌ Failed to get STS token: {result.get('errMessage')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        sys.exit(1)


def upload_to_oss(local_file: str, token: str):
    """Upload file to OSS using STS token."""
    import oss2
    
    sts = get_sts_token(token)
    auth = oss2.StsAuth(sts['accessKeyId'], sts['accessKeySecret'], sts['securityToken'])
    bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', sts['bucketName'])
    
    filename = os.path.basename(local_file)
    ext = os.path.splitext(filename)[1]
    date_str = datetime.now().strftime("%Y%m%d")
    remote_path = f"temp/story/{date_str}/{uuid.uuid4().hex[:8]}{ext}"
    
    content_type = mimetypes.guess_type(local_file)[0] or 'application/octet-stream'
    
    with open(local_file, 'rb') as f:
        bucket.put_object(remote_path, f, headers={'Content-Type': content_type})
    
    url = f"https://wlpaas.oss-cn-shanghai.aliyuncs.com/{remote_path}"
    return url


def submit_video(token: str, first_frame_url: str, prompt: str):
    """Submit video generation."""
    url = f"{BASE_URL}/agent/user/video/generate"
    
    payload = {
        "modelName": MODEL,
        "generationType": "IMAGE_TO_VIDEO",
        "prompt": prompt,
        "firstFrameImageUrl": first_frame_url,
        "aspectRatio": ASPECT_RATIO,
        "resolution": RESOLUTION,
        "duration": DURATION,
        "fps": 24,
        "generateAudio": GENERATE_AUDIO,
    }
    
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "accessToken": token}
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def check_status(token: str, record_id: str):
    """Check video generation status."""
    url = f"{BASE_URL}/agent/user/video/status/{record_id}"
    headers = {"accessToken": token}
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
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
    parser = argparse.ArgumentParser(description="Generate videos from storyboard images")
    parser.add_argument("--storyboard-dir", required=True, help="Directory with storyboard images")
    parser.add_argument("--output-dir", required=True, help="Output directory for videos")
    parser.add_argument("--token", "--access-token", dest="token", help="Access token")
    parser.add_argument("--start", type=int, default=1, help="Start shot number")
    parser.add_argument("--end", type=int, default=17, help="End shot number")
    
    args = parser.parse_args()
    
    if not args.token:
        args.token = os.environ.get("NEODOMAIN_ACCESS_TOKEN")
    
    if not args.token:
        print("❌ Error: Access token required", file=sys.stderr)
        sys.exit(1)
    
    storyboard_dir = Path(args.storyboard_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Generating videos from {args.start} to {args.end}")
    print(f"   Model: {MODEL}")
    print(f"   Duration: {DURATION}, Resolution: {RESOLUTION}")
    print(f"   Audio: {'Yes' if GENERATE_AUDIO else 'No'}")
    print()
    
    # Video prompts for each shot
    prompts = {
        1: "Establishing shot, rainy city at night, cinematic pan",
        2: "Wide shot of hospital entrance, people with umbrellas",
        3: "Woman standing at hospital entrance, emotional scene",
        4: "Man reacting with anger, reaching for wallet",
        5: "Woman walking away alone, lonely silhouette",
        6: "Bar exterior, neon lights flickering in rain",
        7: "Man sitting alone at bar, drinking, melancholic",
        8: "Two men talking in bar, conversation scene",
        9: "Man alone at bar, deep in thought",
        10: "Man walking alone on rainy street at night",
        11: "Old apartment building with red Audi parked outside",
        12: "Man walking up dark staircase",
        13: "Door opening, surprise on man's face",
        14: "Mysterious woman sitting on sofa, elegant",
        15: "Man calling out to woman, holding umbrella",
        16: "Woman turning around, emotional moment",
        17: "Woman turning head to gaze, suspenseful ending",
    }
    
    for i in range(args.start, args.end + 1):
        shot_file = storyboard_dir / f"shot_{i:02d}_*.jpeg"
        
        # Find the actual file
        import glob
        files = list(storyboard_dir.glob(f"shot_{i:02d}_*.jpeg"))
        if not files:
            print(f"⚠️ Shot {i} not found, skipping...")
            continue
        
        storyboard_file = files[0]
        shot_name = storyboard_file.stem
        
        print(f"[{i}/17] Processing {storyboard_file.name}...")
        
        # Upload to OSS
        print(f"   📤 Uploading to OSS...")
        try:
            oss_url = upload_to_oss(str(storyboard_file), args.token)
            print(f"   ✅ Uploaded: {oss_url}")
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            continue
        
        # Generate video
        print(f"   🎬 Generating video...")
        prompt = prompts.get(i, "Cinematic scene")
        
        result = submit_video(args.token, oss_url, prompt)
        
        if not result.get("success"):
            print(f"   ❌ Failed: {result.get('errMessage')}")
            continue
        
        record_id = result.get("data", {}).get("generationRecordId")
        print(f"   📝 Task ID: {record_id}")
        
        # Poll for result
        print(f"   ⏳ Waiting...", end="", flush=True)
        
        while True:
            time.sleep(POLL_INTERVAL)
            print(".", end="", flush=True)
            
            status_result = check_status(args.token, record_id)
            status_data = status_result.get("data", {})
            status = status_data.get("status")
            
            if status == "SUCCESS":
                print(" ✅ Done!")
                break
            elif status == "FAILED":
                print(f" ❌ Failed: {status_data.get('errorMessage')}")
                break
        
        # Download video
        video_url = status_data.get("ossVideoUrl")
        if video_url:
            video_path = output_dir / f"video_{i:02d}.mp4"
            if download_file(video_url, str(video_path)):
                print(f"   ✅ Saved: {video_path}")
        
        print()


if __name__ == "__main__":
    main()
