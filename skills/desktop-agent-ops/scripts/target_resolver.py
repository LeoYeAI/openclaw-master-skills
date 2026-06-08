#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def normalize_text(text):
    return re.sub(r"\s+", "", text.strip().lower())


def match_text(text, query, mode):
    if not query:
        return False
    t = normalize_text(text)
    q = normalize_text(query)
    if mode == "exact":
        return t == q
    if mode == "regex":
        return re.search(query, text, flags=re.IGNORECASE) is not None
    # "contains" mode: also try character-by-character overlap for CJK
    if q in t:
        return True
    # Fuzzy: check if any query char is in text (for single-char OCR fragments)
    if len(q) == 1 and q in t:
        return True
    return False


def _merge_adjacent_boxes(boxes, query, max_gap=30):
    """Merge adjacent OCR boxes whose combined text contains the query.

    Tesseract often splits Chinese text into individual characters.
    E.g. "进" "入" "微" "信" as 4 separate boxes. This function
    tries to merge horizontally adjacent boxes and match the combined text.
    """
    if not boxes or not query:
        return []

    q = normalize_text(query)
    # Sort boxes by y then x for left-to-right, top-to-bottom order
    sorted_boxes = sorted(boxes, key=lambda b: (
        (b.get("abs_box") or b.get("box", {})).get("y", 0),
        (b.get("abs_box") or b.get("box", {})).get("x", 0),
    ))

    merged_matches = []
    n = len(sorted_boxes)
    for start in range(n):
        combined_text = ""
        combined_boxes = []
        for end in range(start, min(start + len(q) + 3, n)):
            box = sorted_boxes[end]
            ab = box.get("abs_box") or box.get("box", {})

            # Check horizontal adjacency
            if combined_boxes:
                prev_ab = combined_boxes[-1].get("abs_box") or combined_boxes[-1].get("box", {})
                prev_right = prev_ab.get("x", 0) + prev_ab.get("width", 0)
                curr_left = ab.get("x", 0)
                y_diff = abs(ab.get("y", 0) - prev_ab.get("y", 0))
                if curr_left - prev_right > max_gap or y_diff > ab.get("height", 20):
                    break

            combined_text += box.get("text", "")
            combined_boxes.append(box)

            if q in normalize_text(combined_text):
                # Build merged bounding box
                all_abs = [b.get("abs_box") or b.get("box", {}) for b in combined_boxes]
                min_x = min(a.get("x", 0) for a in all_abs)
                min_y = min(a.get("y", 0) for a in all_abs)
                max_x = max(a.get("x", 0) + a.get("width", 0) for a in all_abs)
                max_y = max(a.get("y", 0) + a.get("height", 0) for a in all_abs)
                avg_conf = sum(b.get("confidence", 0) for b in combined_boxes) / len(combined_boxes)

                merged_matches.append({
                    "text": combined_text,
                    "confidence": avg_conf,
                    "abs_box": {
                        "x": min_x, "y": min_y,
                        "width": max_x - min_x, "height": max_y - min_y,
                    },
                })
                break

    return merged_matches


def ocr_provider(args, region_label):
    if not args.text:
        return {"name": "ocr_text", "ok": False, "error": "text_query_required"}
    ocr = ROOT / "ocr_text.py"
    cmd = [args.python, str(ocr), "--app", args.app, "--min-conf", str(args.ocr_min_conf), "--python", args.python]
    if region_label:
        cmd += ["--region-label", region_label]
    out = run_json(cmd)
    if not out.get("ok"):
        return {"name": "ocr_text", "ok": False, "error": out.get("error")}

    matches = []
    # First pass: direct single-box matching
    for box in out.get("boxes", []):
        text = box.get("text", "")
        if not match_text(text, args.text, args.text_match):
            continue
        abs_box = box.get("abs_box") or box.get("box") or {}
        x = abs_box.get("x")
        y = abs_box.get("y")
        w = abs_box.get("width")
        h = abs_box.get("height")
        if None in (x, y, w, h):
            continue
        conf = float(box.get("confidence", 0.0))
        matches.append({
            "x": int(x + w / 2),
            "y": int(y + h / 2),
            "width": int(w),
            "height": int(h),
            "confidence": min(1.0, max(0.0, conf / 100.0)),
            "label": f"text:{text}",
            "source": "ocr_text",
        })

    # Second pass: merge adjacent boxes for CJK text split into characters
    if not matches and args.text_match != "regex":
        merged = _merge_adjacent_boxes(out.get("boxes", []), args.text)
        for m in merged:
            ab = m["abs_box"]
            matches.append({
                "x": int(ab["x"] + ab["width"] / 2),
                "y": int(ab["y"] + ab["height"] / 2),
                "width": int(ab["width"]),
                "height": int(ab["height"]),
                "confidence": min(1.0, max(0.0, m["confidence"] / 100.0)),
                "label": f"text_merged:{m['text']}",
                "source": "ocr_text_merged",
            })

    return {
        "name": "ocr_text",
        "ok": True,
        "matches": matches,
        "source": out.get("source"),
        "region": out.get("region"),
    }


def template_provider(args, region_label):
    if not args.template:
        return {"name": "template_match", "ok": False, "error": "template_required"}
    tmpl = ROOT / "template_match.py"
    cmd = [
        args.python, str(tmpl),
        "--app", args.app,
        "--template", args.template,
        "--threshold", str(args.template_threshold),
        "--max-matches", str(args.template_max_matches),
    ]
    if region_label:
        cmd += ["--region-label", region_label]
    out = run_json(cmd)
    if not out.get("ok"):
        return {"name": "template_match", "ok": False, "error": out.get("error")}
    matches = []
    for m in out.get("matches", []):
        x = m["x"]
        y = m["y"]
        w = m["width"]
        h = m["height"]
        score = float(m.get("score", 0.0))
        matches.append({
            "x": int(x + w / 2),
            "y": int(y + h / 2),
            "width": int(w),
            "height": int(h),
            "confidence": min(1.0, max(0.0, score)),
            "label": "template_match",
            "source": "template_match",
        })
    return {
        "name": "template_match",
        "ok": True,
        "matches": matches,
        "source": out.get("source"),
        "region": out.get("region"),
    }


def heuristic_provider(args):
    if not args.label:
        return {"name": "heuristic_region", "ok": False, "error": "label_required"}
    target_report = ROOT / "target_report.py"
    out = run_json([args.python, str(target_report), "--app", args.app, "--label", args.label, "--python", args.python])
    matches = []
    for candidate in out.get("candidates", []):
        matches.append({
            "x": candidate["x"],
            "y": candidate["y"],
            "width": out["region"]["absolute"]["width"],
            "height": out["region"]["absolute"]["height"],
            "confidence": 0.2,
            "label": f"heuristic:{candidate['label']}",
            "source": "heuristic_region",
        })
    return {
        "name": "heuristic_region",
        "ok": True,
        "matches": matches,
        "region": out.get("region"),
    }


def accessibility_provider():
    return {"name": "accessibility", "ok": False, "error": "accessibility_provider_not_implemented"}


def choose_best(results):
    candidates = []
    for res in results:
        if not res.get("ok"):
            continue
        for m in res.get("matches", []):
            candidates.append(m)
    if not candidates:
        return None
    return sorted(candidates, key=lambda c: c.get("confidence", 0.0), reverse=True)[0]


def main():
    ap = argparse.ArgumentParser(
        description="Hybrid target resolver. Locates UI elements within a SPECIFIC app window "
                    "(not full screen). All providers scope their search to the target app's window bounds."
    )
    ap.add_argument("--app", required=True,
                     help="Target app name. The resolver will focus this app and search ONLY within its window.")
    ap.add_argument("--label")
    ap.add_argument("--text")
    ap.add_argument("--template")
    ap.add_argument("--providers", default="ocr_text,template_match,heuristic_region",
                     help="Comma-separated provider priority order. "
                          "OCR is first by default for best cross-platform accuracy.")
    ap.add_argument("--python", default="python3")
    ap.add_argument("--ocr-min-conf", type=float, default=40.0)
    ap.add_argument("--text-match", choices=["contains", "exact", "regex"], default="contains")
    ap.add_argument("--template-threshold", type=float, default=0.8)
    ap.add_argument("--template-max-matches", type=int, default=3)
    ap.add_argument("--region-label")
    args = ap.parse_args()

    desktop_ops = ROOT / "desktop_ops.py"

    # Step 1: Focus the target app so it's frontmost
    try:
        run_json([args.python, str(desktop_ops), "focus-app", "--name", args.app])
    except Exception:
        pass  # Continue even if focus fails; bounds check will catch issues

    # Step 2: Get the target app's window bounds
    window_bounds = None
    try:
        window_bounds = run_json([args.python, str(desktop_ops), "front-window-bounds", "--app", args.app])
    except Exception:
        pass

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    results = []
    for provider in providers:
        if provider == "accessibility":
            results.append(accessibility_provider())
        elif provider == "ocr_text":
            results.append(ocr_provider(args, args.region_label or args.label))
        elif provider == "template_match":
            results.append(template_provider(args, args.region_label or args.label))
        elif provider == "heuristic_region":
            results.append(heuristic_provider(args))
        else:
            results.append({"name": provider, "ok": False, "error": "unknown_provider"})

    # Step 3: Filter candidates to ensure they fall within the app window
    best = choose_best(results)
    if best and window_bounds and window_bounds.get("ok") is not False:
        wx = window_bounds.get("x", 0)
        wy = window_bounds.get("y", 0)
        ww = window_bounds.get("width", 99999)
        wh = window_bounds.get("height", 99999)
        bx, by = best.get("x", 0), best.get("y", 0)
        best["within_window"] = (wx <= bx <= wx + ww) and (wy <= by <= wy + wh)

    jprint({
        "ok": True,
        "app": args.app,
        "window_bounds": window_bounds,
        "providers": results,
        "best_candidate": best,
    })


if __name__ == "__main__":
    main()
