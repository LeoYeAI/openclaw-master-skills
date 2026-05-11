#!/usr/bin/env python3
"""Generate a 3D model via Meshy.ai text-to-3D API and download the GLB file.

Usage:
    MESHY_API_KEY=your_key python3 meshy_generate.py "a steampunk robot" output.glb

Requires: MESHY_API_KEY environment variable and the 'requests' package.
"""
import argparse
import os
import sys
import time

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests",
          file=sys.stderr)
    sys.exit(1)


MESHY_BASE = "https://api.meshy.ai/openapi/v2/text-to-3d"


def main():
    parser = argparse.ArgumentParser(description="Generate 3D model via Meshy.ai")
    parser.add_argument("prompt", help="Text description of the 3D model")
    parser.add_argument("output", help="Output path for .glb file")
    parser.add_argument("--art-style", default="realistic",
                        choices=["realistic", "cartoon", "low-poly", "sculpture"],
                        help="Art style (default: realistic)")
    parser.add_argument("--poll-interval", type=int, default=15,
                        help="Seconds between status checks (default: 15)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Max wait time in seconds (default: 600)")
    args = parser.parse_args()

    api_key = os.environ.get("MESHY_API_KEY")
    if not api_key:
        print("Error: MESHY_API_KEY environment variable not set.", file=sys.stderr)
        print("Get a key at https://www.meshy.ai/", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}

    # Create text-to-3D task
    print(f"Creating 3D model: {args.prompt}")
    resp = requests.post(MESHY_BASE, headers=headers, json={
        "mode": "refine",
        "prompt": args.prompt,
        "art_style": args.art_style,
        "should_remesh": True
    })
    resp.raise_for_status()
    task_id = resp.json()["result"]
    print(f"Task ID: {task_id}")

    # Poll until complete
    start = time.time()
    while time.time() - start < args.timeout:
        status = requests.get(f"{MESHY_BASE}/{task_id}", headers=headers).json()
        state = status.get("status", "UNKNOWN")
        progress = status.get("progress", 0)
        print(f"  Status: {state} ({progress}%)")

        if state == "SUCCEEDED":
            glb_url = status["model_urls"]["glb"]
            print(f"Downloading GLB from {glb_url}...")
            glb_data = requests.get(glb_url).content
            with open(args.output, "wb") as f:
                f.write(glb_data)
            size_mb = len(glb_data) / (1024 * 1024)
            print(f"Saved: {args.output} ({size_mb:.1f} MB)")
            return

        if state == "FAILED":
            print(f"Error: Meshy task failed: {status.get('message', 'unknown')}",
                  file=sys.stderr)
            sys.exit(1)

        time.sleep(args.poll_interval)

    print(f"Error: Timed out after {args.timeout}s", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
