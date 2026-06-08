#!/usr/bin/env python3
import argparse
import json


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def build_region(label, wx, wy, rx, ry, width, height):
    return {
        "label": label,
        "relative": {"x": rx, "y": ry, "width": width, "height": height},
        "absolute": {"x": wx + rx, "y": wy + ry, "width": width, "height": height},
    }


def presets(wx, wy, ww, wh):
    return {
        "top_search": build_region("top_search", wx, wy, int(ww * 0.02), int(wh * 0.03), int(ww * 0.24), int(wh * 0.08)),
        "left_sidebar": build_region("left_sidebar", wx, wy, 0, int(wh * 0.08), int(ww * 0.28), int(wh * 0.72)),
        "left_sidebar_top": build_region("left_sidebar_top", wx, wy, 0, int(wh * 0.08), int(ww * 0.28), int(wh * 0.25)),
        "title_header": build_region("title_header", wx, wy, int(ww * 0.28), 0, int(ww * 0.68), int(wh * 0.10)),
        "content_area": build_region("content_area", wx, wy, int(ww * 0.28), int(wh * 0.10), int(ww * 0.68), int(wh * 0.62)),
        "toolbar_row": build_region("toolbar_row", wx, wy, int(ww * 0.28), int(wh * 0.72), int(ww * 0.68), int(wh * 0.08)),
        "bottom_input": build_region("bottom_input", wx, wy, int(ww * 0.28), int(wh * 0.80), int(ww * 0.66), int(wh * 0.16)),
        "primary_action": build_region("primary_action", wx, wy, int(ww * 0.78), int(wh * 0.88), int(ww * 0.16), int(wh * 0.08)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-x", type=int, required=True)
    ap.add_argument("--window-y", type=int, required=True)
    ap.add_argument("--window-width", type=int, required=True)
    ap.add_argument("--window-height", type=int, required=True)
    ap.add_argument("--label")
    args = ap.parse_args()

    all_regions = presets(args.window_x, args.window_y, args.window_width, args.window_height)
    if args.label:
        region = all_regions.get(args.label)
        if not region:
            raise SystemExit(f"unknown label: {args.label}")
        jprint({"ok": True, "window": {"x": args.window_x, "y": args.window_y, "width": args.window_width, "height": args.window_height}, "region": region})
        return
    jprint({"ok": True, "window": {"x": args.window_x, "y": args.window_y, "width": args.window_width, "height": args.window_height}, "regions": all_regions})


if __name__ == "__main__":
    main()
