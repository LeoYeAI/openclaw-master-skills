#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Generate image or video outputs with reference-image transport helpers.")
    p.add_argument("--mode", choices=["image", "video"], default="image", help="Target modality")
    p.add_argument("--prompt", required=True, help="Request prompt")
    p.add_argument("--reference-image", action="append", default=[], help="Repeatable reference image path")
    p.add_argument("--reference-key", default="reference_images", help="JSON field name used when passing encoded reference images to the provider")
    p.add_argument("--transport", choices=["auto", "none", "provider-json"], default="auto", help="How to pass reference images")
    p.add_argument("--video-reference-mode", choices=["reference", "animate"], default="reference", help="Video request mode when using a reference image")
    p.add_argument("--size", help="Forwarded size")
    p.add_argument("--quality", help="Forwarded image quality")
    p.add_argument("--style", help="Forwarded image style")
    p.add_argument("--background", help="Forwarded image background")
    p.add_argument("--n", type=int, help="Forwarded image count")
    p.add_argument("--seed", type=int, help="Forwarded seed")
    p.add_argument("--duration", help="Forwarded video duration")
    p.add_argument("--seconds", type=int, help="Forwarded video seconds")
    p.add_argument("--fps", type=int, help="Forwarded video fps")
    p.add_argument("--provider", help="Forwarded provider name")
    p.add_argument("--config", help="Forwarded config path")
    p.add_argument("--model", help="Forwarded model name")
    p.add_argument("--endpoint", help="Forwarded endpoint path")
    p.add_argument("--status-endpoint-template", help="Forwarded video polling template")
    p.add_argument("--out-dir", help="Forwarded output directory")
    p.add_argument("--prefix", help="Forwarded output prefix")
    p.add_argument("--print-json", action="store_true", help="Print structured JSON summary")
    return p.parse_args()


def data_url_for(path: Path):
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def build_command(args, prompt, extra_json=None, extra_json_file=None):
    script_name = "generate_image.py" if args.mode == "image" else "generate_video.py"
    script_path = Path(__file__).resolve().parent / script_name
    cmd = [sys.executable, str(script_path), "--prompt", prompt]

    forwarded = {
        "--size": args.size,
        "--quality": args.quality if args.mode == "image" else None,
        "--style": args.style if args.mode == "image" else None,
        "--background": args.background if args.mode == "image" else None,
        "--n": args.n if args.mode == "image" else None,
        "--seed": args.seed,
        "--duration": args.duration if args.mode == "video" else None,
        "--seconds": args.seconds if args.mode == "video" else None,
        "--fps": args.fps if args.mode == "video" else None,
        "--provider": args.provider,
        "--config": args.config,
        "--model": args.model,
        "--endpoint": args.endpoint,
        "--status-endpoint-template": args.status_endpoint_template if args.mode == "video" else None,
        "--out-dir": args.out_dir,
        "--prefix": args.prefix,
    }
    for flag, value in forwarded.items():
        if value is not None:
            cmd.extend([flag, str(value)])
    if extra_json is not None:
        cmd.extend(["--extra-json", json.dumps(extra_json, ensure_ascii=False)])
    if extra_json_file is not None:
        cmd.extend(["--extra-json-file", str(extra_json_file)])
    if args.print_json:
        cmd.append("--print-json")
    return cmd


def try_run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def main():
    args = parse_args()
    reference_paths = [Path(p) for p in args.reference_image]
    for path in reference_paths:
        if not path.exists():
            raise SystemExit(f"reference image not found: {path}")

    prompt = args.prompt.strip()
    summary = {
        "mode": args.mode,
        "videoReferenceMode": args.video_reference_mode if args.mode == "video" else None,
        "referenceCount": len(reference_paths),
        "transport": args.transport,
        "fallbackUsed": False,
        "prompt": prompt,
        "result": None,
        "hints": [
            "If provider-json transport fails, check whether the provider accepts encoded reference images and whether the reference key matches its schema.",
        ],
    }

    extra_json = None
    extra_json_file = None
    temp_path = None
    try:
        if reference_paths and args.transport in {"auto", "provider-json"}:
            extra_json = {args.reference_key: [data_url_for(path) for path in reference_paths]}
            if len(json.dumps(extra_json, ensure_ascii=False)) > 50000:
                tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
                json.dump(extra_json, tmp, ensure_ascii=False)
                tmp.flush()
                tmp.close()
                temp_path = Path(tmp.name)
                extra_json_file = temp_path
                extra_json = None

        first_cmd = build_command(args, prompt, extra_json=extra_json, extra_json_file=extra_json_file)
        if args.mode == "video" and reference_paths:
            first_cmd.extend(["--mode", args.video_reference_mode, "--image", str(reference_paths[0]), "--image-transport", "data-url"])
            if args.video_reference_mode == "reference" and args.reference_key in {"image", "input_image", "first_frame_image", "reference_images"}:
                first_cmd.extend(["--image-field", args.reference_key])
        first = try_run(first_cmd)
        if first.returncode == 0:
            summary["result"] = first.stdout.strip()
            if args.print_json:
                print(json.dumps(summary, ensure_ascii=False, indent=2))
            else:
                print(first.stdout, end="")
            return

        if reference_paths and args.transport == "auto":
            if first.stderr:
                print("INFO: provider-json reference transport failed; retrying without provider-json references", file=sys.stderr)
            fallback_cmd = build_command(args, prompt, extra_json=None)
            if args.mode == "video" and reference_paths:
                fallback_cmd.extend(["--mode", args.video_reference_mode, "--image", str(reference_paths[0]), "--image-transport", "data-url"])
            fallback = try_run(fallback_cmd)
            if fallback.returncode == 0:
                summary["fallbackUsed"] = True
                summary["result"] = fallback.stdout.strip()
                if args.print_json:
                    print(json.dumps(summary, ensure_ascii=False, indent=2))
                else:
                    print(fallback.stdout, end="")
                return
            if fallback.stderr:
                print(fallback.stderr, file=sys.stderr, end="")
            if fallback.stdout:
                print(fallback.stdout, end="")
            raise SystemExit(fallback.returncode)

        if first.stderr:
            print(first.stderr, file=sys.stderr, end="")
        if first.stdout:
            print(first.stdout, end="")
        raise SystemExit(first.returncode)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    main()
