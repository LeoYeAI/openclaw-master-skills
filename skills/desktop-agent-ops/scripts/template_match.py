#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def ensure_cv():
    try:
        import cv2  # type: ignore
        return None
    except Exception:
        return "cv2_unavailable"


def capture_region(app, region_label, python_exec):
    desktop_ops = ROOT / "desktop_ops.py"
    window_regions = ROOT / "window_regions.py"

    bounds = run_json([python_exec, str(desktop_ops), "front-window-bounds", "--app", app])
    if region_label:
        region_out = run_json([
            python_exec, str(window_regions),
            "--window-x", str(bounds["x"]),
            "--window-y", str(bounds["y"]),
            "--window-width", str(bounds["width"]),
            "--window-height", str(bounds["height"]),
            "--label", region_label,
        ])
        region = region_out["region"]["absolute"]
    else:
        region = {
            "x": bounds["x"],
            "y": bounds["y"],
            "width": bounds["width"],
            "height": bounds["height"],
        }

    output = tempfile.mktemp(prefix="tmpl-region-", suffix=".png")
    cap = run_json([
        python_exec, str(desktop_ops), "capture-region",
        "--x", str(region["x"]),
        "--y", str(region["y"]),
        "--width", str(region["width"]),
        "--height", str(region["height"]),
        "--output", output,
    ])
    return {
        "bounds": bounds,
        "region": region,
        "capture": cap,
        "image": output,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--template", required=True)
    ap.add_argument("--app")
    ap.add_argument("--region-label")
    ap.add_argument("--python", default="python3")
    ap.add_argument("--threshold", type=float, default=0.8)
    ap.add_argument("--max-matches", type=int, default=3)
    args = ap.parse_args()

    err = ensure_cv()
    if err:
        jprint({"ok": False, "error": err})
        return

    import cv2  # type: ignore
    import numpy as np  # type: ignore

    source = {"type": "image", "image": args.image}
    capture = None
    region = None
    bounds = None
    image_path = args.image
    if not image_path:
        if not args.app:
            jprint({"ok": False, "error": "image_or_app_required"})
            return
        capture = capture_region(args.app, args.region_label, args.python)
        image_path = capture["image"]
        region = capture["region"]
        bounds = capture["bounds"]
        source = {"type": "capture", "app": args.app, "region_label": args.region_label, "image": image_path}

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    tmpl = cv2.imread(args.template, cv2.IMREAD_COLOR)
    if img is None:
        jprint({"ok": False, "error": "image_load_failed"})
        return
    if tmpl is None:
        jprint({"ok": False, "error": "template_load_failed"})
        return

    h, w = tmpl.shape[:2]
    res = cv2.matchTemplate(img, tmpl, cv2.TM_CCOEFF_NORMED)

    matches = []
    for _ in range(args.max_matches):
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < args.threshold:
            break
        x, y = max_loc
        matches.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "score": float(max_val),
        })
        x0 = max(x - w // 2, 0)
        y0 = max(y - h // 2, 0)
        x1 = min(x + w // 2, res.shape[1] - 1)
        y1 = min(y + h // 2, res.shape[0] - 1)
        res[y0:y1, x0:x1] = 0

    if region:
        offset_x = region["x"]
        offset_y = region["y"]
        abs_matches = []
        for m in matches:
            abs_matches.append({
                "x": m["x"] + offset_x,
                "y": m["y"] + offset_y,
                "width": m["width"],
                "height": m["height"],
                "score": m["score"],
            })
        matches = abs_matches

    jprint({
        "ok": True,
        "source": source,
        "bounds": bounds,
        "region": region,
        "matches": matches,
    })


if __name__ == "__main__":
    main()
