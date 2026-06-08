#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def candidate_points(region):
    absr = region["absolute"]
    x = absr["x"]
    y = absr["y"]
    w = absr["width"]
    h = absr["height"]
    inset = 12
    left = x + inset
    right = x + w - inset
    top = y + inset
    bottom = y + h - inset
    cx = x + w // 2
    cy = y + h // 2
    return [
        {"label": "center", "x": cx, "y": cy},
        {"label": "upper_middle", "x": cx, "y": top + max(0, (cy - top) // 2)},
        {"label": "lower_middle", "x": cx, "y": cy + max(0, (bottom - cy) // 2)},
        {"label": "left_middle", "x": left, "y": cy},
        {"label": "right_middle", "x": right, "y": cy},
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--python", default="python3")
    args = ap.parse_args()

    desktop_ops = ROOT / "desktop_ops.py"
    window_regions = ROOT / "window_regions.py"
    bounds = run_json([args.python, str(desktop_ops), "front-window-bounds", "--app", args.app])
    region_out = run_json([
        args.python, str(window_regions),
        "--window-x", str(bounds["x"]),
        "--window-y", str(bounds["y"]),
        "--window-width", str(bounds["width"]),
        "--window-height", str(bounds["height"]),
        "--label", args.label,
    ])
    mouse = run_json([args.python, str(desktop_ops), "mouse-position"])
    report = {
        "ok": True,
        "app": {"name": args.app},
        "window": {"x": bounds["x"], "y": bounds["y"], "width": bounds["width"], "height": bounds["height"], "window": bounds.get("window", "")},
        "region": region_out["region"],
        "mouse": {"x": mouse["x"], "y": mouse["y"]},
        "candidates": candidate_points(region_out["region"]),
    }
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
