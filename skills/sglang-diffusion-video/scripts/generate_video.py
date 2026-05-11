#!/usr/bin/env python3
"""
Generate videos using a local SGLang-Diffusion server (OpenAI-compatible API).


Usage:
   python3 generate_video.py --prompt "a curious raccoon exploring a garden"
   python3 generate_video.py --prompt "ocean waves" --size 1280x720 --steps 50 --seed 42
   python3 generate_video.py --prompt "animate this" --input-image /tmp/scene.png --server http://host:30000
"""


from __future__ import annotations


import argparse
import base64
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path




def get_api_key(provided_key: str | None) -> str | None:
   """Get API key from argument first, then environment."""
   if provided_key:
       return provided_key
   return os.environ.get("SGLANG_DIFFUSION_API_KEY")




def generate_output_path(out_arg: str | None, prompt: str) -> Path:
   """Build an output file path: explicit --out wins, otherwise timestamped tmp."""
   if out_arg:
       p = Path(out_arg).expanduser()
       p.parent.mkdir(parents=True, exist_ok=True)
       return p


   now = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
   slug = prompt[:40].lower().strip()
   slug = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in slug)
   slug = slug.strip("-") or "video"
   tmp = Path("/tmp")
   return tmp / f"sglang-video-{now}-{slug}.mp4"




def _build_headers(api_key: str) -> dict:
   headers = {"Content-Type": "application/json"}
   if api_key:
       headers["Authorization"] = f"Bearer {api_key}"
   return headers




def _api_request(
   url: str, headers: dict, data: bytes | None = None, method: str = "GET", timeout: int = 30
) -> dict:
   """Make an HTTP request and return parsed JSON."""
   req = urllib.request.Request(url, method=method, headers=headers, data=data)
   try:
       with urllib.request.urlopen(req, timeout=timeout) as resp:
           return json.loads(resp.read().decode("utf-8"))
   except urllib.error.HTTPError as e:
       payload = e.read().decode("utf-8", errors="replace")
       raise RuntimeError(
           f"SGLang-Diffusion API failed ({e.code}): {payload}"
       ) from e
   except urllib.error.URLError as e:
       raise RuntimeError(
           f"Cannot reach SGLang-Diffusion server at {url}: {e}"
       ) from e




def _download_binary(url: str, headers: dict, dest: Path, timeout: int = 300) -> None:
   """Download binary content (video file) to disk."""
   req_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
   req = urllib.request.Request(url, method="GET", headers=req_headers)
   try:
       with urllib.request.urlopen(req, timeout=timeout) as resp:
           dest.write_bytes(resp.read())
   except urllib.error.HTTPError as e:
       payload = e.read().decode("utf-8", errors="replace")
       raise RuntimeError(
           f"Failed to download video ({e.code}): {payload}"
       ) from e




def submit_video(
   server: str,
   api_key: str,
   prompt: str,
   *,
   negative_prompt: str = "",
   size: str = "1280x720",
   seconds: int | None = None,
   fps: int | None = None,
   steps: int | None = None,
   guidance_scale: float | None = None,
   seed: int | None = None,
   input_image: str | None = None,
) -> str:
   """POST to /v1/videos and return the video ID."""
   url = f"{server.rstrip('/')}/v1/videos"


   body: dict = {
       "prompt": prompt,
       "size": size,
   }
   if negative_prompt:
       body["negative_prompt"] = negative_prompt
   if seconds is not None:
       body["seconds"] = seconds
   if fps is not None:
       body["fps"] = fps
   if steps is not None:
       body["num_inference_steps"] = steps
   if guidance_scale is not None:
       body["guidance_scale"] = guidance_scale
   if seed is not None:
       body["seed"] = seed
   if input_image:
       img_path = Path(input_image).expanduser()
       if not img_path.exists():
           raise FileNotFoundError(f"Input image not found: {img_path}")
       b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
       body["input_reference"] = b64


   data = json.dumps(body).encode("utf-8")
   headers = _build_headers(api_key)


   res = _api_request(url, headers, data=data, method="POST", timeout=60)


   video_id = res.get("id")
   if not video_id:
       raise RuntimeError(f"No video ID in response: {json.dumps(res)[:400]}")
   return video_id




def poll_video(
   server: str, api_key: str, video_id: str, *, poll_interval: int, timeout: int
) -> dict:
   """Poll GET /v1/videos/{id} until status is completed or failed."""
   url = f"{server.rstrip('/')}/v1/videos/{video_id}"
   headers = _build_headers(api_key)


   start = time.monotonic()
   while True:
       elapsed = time.monotonic() - start
       if elapsed > timeout:
           raise TimeoutError(
               f"Video generation timed out after {timeout}s (status never reached 'completed')"
           )


       res = _api_request(url, headers, timeout=30)
       status = res.get("status", "unknown")


       mins = int(elapsed) // 60
       secs = int(elapsed) % 60
       print(f"  [{mins:02d}:{secs:02d}] status: {status}")


       if status == "completed":
           return res
       if status in ("failed", "error", "cancelled"):
           error_msg = res.get("error", res.get("message", "unknown error"))
           raise RuntimeError(f"Video generation {status}: {error_msg}")


       time.sleep(poll_interval)




def download_video(server: str, api_key: str, video_id: str, dest: Path) -> None:
   """GET /v1/videos/{id}/content and save to disk."""
   url = f"{server.rstrip('/')}/v1/videos/{video_id}/content"
   headers = _build_headers(api_key)
   _download_binary(url, headers, dest)




def main() -> int:
   ap = argparse.ArgumentParser(
       description="Generate videos via a local SGLang-Diffusion server."
   )
   ap.add_argument("--prompt", "-p", required=True, help="Video description/prompt.")
   ap.add_argument(
       "--negative-prompt",
       default="",
       help="What to avoid in the video.",
   )
   ap.add_argument("--size", default="1280x720", help="Video size (default: 1280x720).")
   ap.add_argument("--seconds", type=int, default=None, help="Video duration in seconds.")
   ap.add_argument("--fps", type=int, default=None, help="Frames per second (e.g. 24).")
   ap.add_argument("--steps", type=int, default=None, help="Number of denoising steps.")
   ap.add_argument(
       "--guidance-scale",
       type=float,
       default=None,
       help="Prompt adherence (higher = closer to prompt).",
   )
   ap.add_argument("--seed", type=int, default=None, help="Seed for reproducible generation.")
   ap.add_argument(
       "--input-image",
       default=None,
       help="Path to input image for image-to-video (I2V models only).",
   )
   ap.add_argument(
       "--server",
       default="http://127.0.0.1:30000",
       help="SGLang-Diffusion server URL (default: http://127.0.0.1:30000).",
   )
   ap.add_argument("--out", "-o", default=None, help="Output file path (default: timestamped /tmp/).")
   ap.add_argument("--api-key", "-k", default=None, help="API key (optional).")
   ap.add_argument(
       "--poll-interval",
       type=int,
       default=30,
       help="Seconds between status polls (default: 30).",
   )
   ap.add_argument(
       "--timeout",
       type=int,
       default=900,
       help="Max seconds to wait for generation (default: 900).",
   )
   args = ap.parse_args()


   api_key = get_api_key(args.api_key) or ""


   output_path = generate_output_path(args.out, args.prompt)


   print(f"Generating video: {args.prompt}")
   print(f"Server: {args.server}")
   print(f"Size: {args.size}")
   if args.input_image:
       print(f"Input image: {args.input_image}")


   # Step 1: Submit
   print("\nSubmitting video generation request...")
   video_id = submit_video(
       args.server,
       api_key,
       args.prompt,
       negative_prompt=args.negative_prompt,
       size=args.size,
       seconds=args.seconds,
       fps=args.fps,
       steps=args.steps,
       guidance_scale=args.guidance_scale,
       seed=args.seed,
       input_image=args.input_image,
   )
   print(f"Video ID: {video_id}")


   # Step 2: Poll
   print(f"\nWaiting for generation (polling every {args.poll_interval}s, timeout {args.timeout}s)...")
   poll_video(
       args.server,
       api_key,
       video_id,
       poll_interval=args.poll_interval,
       timeout=args.timeout,
   )
   print("Generation complete!")


   # Step 3: Download
   print("\nDownloading video...")
   download_video(args.server, api_key, video_id, output_path)


   full_path = output_path.resolve()
   print(f"\nVideo saved: {full_path}")
   print(f"MEDIA:{full_path}")
   return 0




if __name__ == "__main__":
   raise SystemExit(main())