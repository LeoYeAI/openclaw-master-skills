#!/usr/bin/env python3
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parent

# Mapping of locale prefixes to tesseract language codes
_LOCALE_TO_TESS = {
    "zh-Hans": "chi_sim", "zh-Hant": "chi_tra", "zh": "chi_sim",
    "ja": "jpn", "ko": "kor", "ar": "ara", "hi": "hin",
    "th": "tha", "vi": "vie", "ru": "rus", "de": "deu",
    "fr": "fra", "es": "spa", "pt": "por", "it": "ita",
}


def jprint(data):
    print(json.dumps(data, ensure_ascii=False))


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def ensure_ocr_ready():
    if Image is None:
        return "PIL_unavailable"
    if shutil.which("tesseract") is None:
        return "tesseract_binary_missing"
    try:
        import pytesseract  # type: ignore
        return None
    except Exception:
        return "pytesseract_unavailable"


def _get_installed_tess_langs():
    """Get set of installed tesseract language codes."""
    try:
        p = subprocess.run(["tesseract", "--list-langs"],
                           capture_output=True, text=True, timeout=5)
        lines = (p.stderr + "\n" + p.stdout).strip().splitlines()
        langs = set()
        for line in lines:
            s = line.strip()
            if s and not s.startswith("List of") and "/" not in s:
                langs.add(s)
        return langs
    except Exception:
        return set()


def auto_detect_lang():
    """Build a tesseract --lang string based on system locale + installed packs.

    Always includes 'eng'. Adds the system locale language if its pack is installed.
    Returns e.g. 'eng+chi_sim' or just 'eng'.
    """
    installed = _get_installed_tess_langs()
    parts = ["eng"]

    # Detect system locale
    system = platform.system().lower()
    locale_langs = []
    _UNDERSCORE_LOCALE = {
        "zh_CN": "chi_sim", "zh_TW": "chi_tra",
        "ja_JP": "jpn", "ko_KR": "kor",
    }
    if system == "darwin":
        try:
            p = subprocess.run(["defaults", "read", "-g", "AppleLanguages"],
                               capture_output=True, text=True, timeout=5)
            if p.returncode == 0:
                locale_langs = re.findall(r'"([^"]+)"', p.stdout)
        except Exception:
            pass
    elif system == "windows":
        try:
            import locale
            def_locale = locale.getdefaultlocale()
            if def_locale and def_locale[0]:
                locale_langs.append(def_locale[0])
        except Exception:
            pass
    else:
        for env_var in ["LANG", "LANGUAGE", "LC_ALL"]:
            val = os.environ.get(env_var, "")
            if val:
                locale_langs.append(val.split(".")[0])

    for lang in locale_langs:
        for prefix, tess_code in _LOCALE_TO_TESS.items():
            if lang.startswith(prefix) and tess_code in installed and tess_code not in parts:
                parts.append(tess_code)
                break
        for prefix, tess_code in _UNDERSCORE_LOCALE.items():
            if lang.startswith(prefix) and tess_code in installed and tess_code not in parts:
                parts.append(tess_code)
                break

    return "+".join(parts)


def _detect_dpi_scale(python_exec):
    """Detect the DPI scale factor between screenshot pixels and logical coordinates.

    On Retina/HiDPI displays, screencapture produces images at 2x (or 3x) the
    logical resolution. OCR coordinates are in pixel space but mouse operations
    use logical space, so we need this ratio to convert.

    Returns the scale factor (e.g. 2.0 for Retina, 1.0 for non-Retina).
    """
    try:
        desktop_ops = ROOT / "desktop_ops.py"
        # Get logical screen size
        screen = run_json([python_exec, str(desktop_ops), "screen-size"])
        logical_w = screen.get("width", 0)
        if logical_w <= 0:
            return 1.0

        # Take a tiny screenshot and check its pixel width
        tmp = tempfile.mktemp(prefix="dpi-probe-", suffix=".png")
        run_json([python_exec, str(desktop_ops), "screenshot", "--output", tmp])
        img = Image.open(tmp)
        pixel_w = img.width
        try:
            Path(tmp).unlink(missing_ok=True)
        except Exception:
            pass

        if pixel_w > 0 and logical_w > 0:
            ratio = pixel_w / logical_w
            # Round to nearest 0.5 (common values: 1.0, 1.5, 2.0, 3.0)
            return round(ratio * 2) / 2
    except Exception:
        pass
    return 1.0


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

    output = tempfile.mktemp(prefix="ocr-region-", suffix=".png")
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


def extract_text(image_path, min_conf, lang):
    import pytesseract  # type: ignore

    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang=lang)
    boxes = []
    for i in range(len(data.get("text", []))):
        text = (data["text"][i] or "").strip()
        conf_raw = data.get("conf", ["-1"])[i]
        try:
            conf = float(conf_raw)
        except Exception:
            conf = -1.0
        if not text or conf < min_conf:
            continue
        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])
        boxes.append({
            "text": text,
            "confidence": conf,
            "box": {"x": x, "y": y, "width": w, "height": h},
        })
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--app")
    ap.add_argument("--region-label")
    ap.add_argument("--python", default="python3")
    ap.add_argument("--min-conf", type=float, default=40.0)
    ap.add_argument("--lang", default="auto",
                     help="Tesseract lang code (e.g. eng, chi_sim, eng+chi_sim). "
                          "Default 'auto' detects from system locale.")
    args = ap.parse_args()

    err = ensure_ocr_ready()
    if err:
        jprint({"ok": False, "error": err})
        return

    # Resolve language
    lang = args.lang
    if lang == "auto":
        lang = auto_detect_lang()

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

    boxes = extract_text(image_path, args.min_conf, lang)

    # Detect DPI scale to convert pixel coordinates → logical coordinates
    dpi_scale = _detect_dpi_scale(args.python)

    def scale_box(b):
        """Convert a pixel-space box to logical coordinates."""
        return {
            "x": int(b["x"] / dpi_scale),
            "y": int(b["y"] / dpi_scale),
            "width": max(1, int(b["width"] / dpi_scale)),
            "height": max(1, int(b["height"] / dpi_scale)),
        }

    if region:
        offset_x = region["x"]
        offset_y = region["y"]
        scaled_boxes = []
        for box in boxes:
            pixel_box = box["box"]
            logical_box = scale_box(pixel_box)
            scaled_boxes.append({
                "text": box["text"],
                "confidence": box["confidence"],
                "pixel_box": pixel_box,
                "box": logical_box,
                "abs_box": {
                    "x": logical_box["x"] + offset_x,
                    "y": logical_box["y"] + offset_y,
                    "width": logical_box["width"],
                    "height": logical_box["height"],
                },
            })
        boxes = scaled_boxes
    else:
        scaled_boxes = []
        for box in boxes:
            pixel_box = box["box"]
            logical_box = scale_box(pixel_box)
            scaled_boxes.append({
                "text": box["text"],
                "confidence": box["confidence"],
                "pixel_box": pixel_box,
                "box": logical_box,
            })
        boxes = scaled_boxes

    jprint({
        "ok": True,
        "source": source,
        "lang": lang,
        "dpi_scale": dpi_scale,
        "bounds": bounds,
        "region": region,
        "boxes": boxes,
    })


if __name__ == "__main__":
    main()
