#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageStat  # type: ignore
except Exception:
    Image = None
    ImageChops = None
    ImageStat = None

ROOT = Path(__file__).resolve().parent


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def load_image(path):
    if Image is None:
        raise RuntimeError("PIL_unavailable")
    return Image.open(path).convert("RGB")


def crop_if_needed(img, region):
    if not region:
        return img
    x = int(region["x"])
    y = int(region["y"])
    w = int(region["width"])
    h = int(region["height"])
    return img.crop((x, y, x + w, y + h))


def resolve_region(args):
    if args.region_label:
        if not args.app:
            raise RuntimeError("app_required_for_region_label")
        desktop_ops = ROOT / "desktop_ops.py"
        window_regions = ROOT / "window_regions.py"
        bounds = run_json([args.python, str(desktop_ops), "front-window-bounds", "--app", args.app])
        region_out = run_json([
            args.python, str(window_regions),
            "--window-x", str(bounds["x"]),
            "--window-y", str(bounds["y"]),
            "--window-width", str(bounds["width"]),
            "--window-height", str(bounds["height"]),
            "--label", args.region_label,
        ])
        return region_out["region"]["absolute"]
    if args.region_x is not None:
        return {
            "x": args.region_x,
            "y": args.region_y,
            "width": args.region_width,
            "height": args.region_height,
        }
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--threshold", type=float, default=0.02)
    ap.add_argument("--app")
    ap.add_argument("--region-label")
    ap.add_argument("--region-x", type=int)
    ap.add_argument("--region-y", type=int)
    ap.add_argument("--region-width", type=int)
    ap.add_argument("--region-height", type=int)
    ap.add_argument("--python", default="python3")
    args = ap.parse_args()

    if Image is None:
        jprint({"ok": False, "error": "PIL_unavailable"})
        return

    try:
        region = resolve_region(args)
    except Exception as exc:
        jprint({"ok": False, "error": str(exc)})
        return

    before = load_image(args.before)
    after = load_image(args.after)
    if before.size != after.size:
        jprint({"ok": False, "error": "image_size_mismatch", "before": before.size, "after": after.size})
        return

    before_crop = crop_if_needed(before, region)
    after_crop = crop_if_needed(after, region)
    diff = ImageChops.difference(before_crop, after_crop)
    stat = ImageStat.Stat(diff)
    mean = sum(stat.mean) / (len(stat.mean) * 255.0)
    changed = mean >= args.threshold

    jprint({
        "ok": True,
        "diff_mean": mean,
        "changed": changed,
        "threshold": args.threshold,
        "region": region,
    })


if __name__ == "__main__":
    main()
