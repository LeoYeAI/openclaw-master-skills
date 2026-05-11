#!/usr/bin/env python3
import argparse
import subprocess
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from media_request_common import default_mask_dir, default_output_dir


DEFAULT_MASK_DIR = str(default_mask_dir())
DEFAULT_OUT_DIR = str(default_output_dir("images"))


def parse_args():
    p = argparse.ArgumentParser(description="Create or reuse a mask image and call the image-edit helper.")
    p.add_argument("--image", required=True, help="Path to the source image")
    p.add_argument("--prompt", required=True, help="Edit request text")
    p.add_argument("--mask", help="Optional existing mask image path")
    p.add_argument("--mask-dir", default=DEFAULT_MASK_DIR, help="Directory for generated masks")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory for final edited outputs")
    p.add_argument("--prefix", default="inpaint", help="Filename prefix")
    p.add_argument("--config", help="Forwarded config path for edit_image.py")
    p.add_argument("--provider", help="Forwarded provider for edit_image.py")
    p.add_argument("--model", help="Forwarded image edit model for edit_image.py")
    p.add_argument("--endpoint", help="Forwarded endpoint for edit_image.py")
    p.add_argument("--x", type=int, help="Rectangle left")
    p.add_argument("--y", type=int, help="Rectangle top")
    p.add_argument("--width", type=int, help="Rectangle width")
    p.add_argument("--height", type=int, help="Rectangle height")
    p.add_argument("--x2", type=int, help="Rectangle right")
    p.add_argument("--y2", type=int, help="Rectangle bottom")
    p.add_argument("--ellipse", action="store_true", help="Use an ellipse for the legacy single-region coordinates instead of a rectangle")
    p.add_argument("--region", action="append", default=[], help="Repeatable region spec. Formats: rect:x:y:w:h, box:x1:y1:x2:y2, ellipse:x:y:w:h, rect-pct:x:y:w:h, box-pct:x1:y1:x2:y2, ellipse-pct:x:y:w:h")
    p.add_argument("--feather", type=int, default=8, help="Mask feather radius in pixels")
    p.add_argument("--expand", type=int, default=0, help="Grow the mask by this many pixels before feathering")
    p.add_argument("--shrink", type=int, default=0, help="Shrink the mask by this many pixels before feathering")
    p.add_argument("--invert", action="store_true", help="Invert the generated or supplied mask before use")
    p.add_argument("--mask-only", action="store_true", help="Only generate and save the mask, then exit")
    p.add_argument("--print-json", action="store_true", help="Forward --print-json to edit_image.py")
    p.add_argument("--no-download", action="store_true", help="Forward --no-download to edit_image.py")
    return p.parse_args()


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


def odd_kernel(px):
    value = max(1, int(px) * 2 + 1)
    return value if value % 2 == 1 else value + 1


def apply_expand_shrink(mask, expand, shrink):
    if expand > 0:
        mask = mask.filter(ImageFilter.MaxFilter(size=odd_kernel(expand)))
    if shrink > 0:
        mask = mask.filter(ImageFilter.MinFilter(size=odd_kernel(shrink)))
    return mask


def parse_float_list(text, expected):
    parts = [p.strip() for p in text.split(":")]
    if len(parts) != expected:
        raise SystemExit(f"invalid region spec: {text}")
    try:
        return [float(p) for p in parts]
    except ValueError:
        raise SystemExit(f"invalid numeric region spec: {text}")


def normalize_region(kind, numbers, w, h):
    pct = kind.endswith("-pct")
    base_kind = kind[:-4] if pct else kind
    if pct:
        if base_kind in {"rect", "ellipse"}:
            x, y, rw, rh = numbers
            x1 = round(w * x / 100.0)
            y1 = round(h * y / 100.0)
            x2 = round(w * (x + rw) / 100.0)
            y2 = round(h * (y + rh) / 100.0)
        elif base_kind == "box":
            x1, y1, x2, y2 = [round(v * axis / 100.0) for v, axis in zip(numbers, (w, h, w, h))]
        else:
            raise SystemExit(f"unsupported region kind: {kind}")
    else:
        if base_kind in {"rect", "ellipse"}:
            x, y, rw, rh = numbers
            x1 = round(x)
            y1 = round(y)
            x2 = round(x + rw)
            y2 = round(y + rh)
        elif base_kind == "box":
            x1, y1, x2, y2 = [round(v) for v in numbers]
        else:
            raise SystemExit(f"unsupported region kind: {kind}")
    x1 = clamp(x1, 0, w)
    y1 = clamp(y1, 0, h)
    x2 = clamp(x2, 0, w)
    y2 = clamp(y2, 0, h)
    if x2 <= x1 or y2 <= y1:
        raise SystemExit(f"invalid region after clamping: {kind}:{numbers}")
    return base_kind, (x1, y1, x2, y2)


def collect_regions(args, w, h):
    regions = []
    if None not in (args.x, args.y, args.width, args.height):
        kind = "ellipse" if args.ellipse else "rect"
        regions.append((kind, normalize_region(kind, [args.x, args.y, args.width, args.height], w, h)[1]))
    elif None not in (args.x, args.y, args.x2, args.y2):
        if args.ellipse:
            regions.append(("ellipse", normalize_region("ellipse", [args.x, args.y, args.x2 - args.x, args.y2 - args.y], w, h)[1]))
        else:
            regions.append(("box", normalize_region("box", [args.x, args.y, args.x2, args.y2], w, h)[1]))
    for spec in args.region:
        try:
            kind, coords = spec.split(":", 1)
        except ValueError:
            raise SystemExit(f"invalid --region format: {spec}")
        normalized = normalize_region(kind, parse_float_list(coords, 4), w, h)
        regions.append((normalized[0], normalized[1]))
    if not regions and not args.mask:
        raise SystemExit("provide either --mask, a legacy single region, or one or more --region specs")
    return regions


def draw_regions(mask, regions):
    draw = ImageDraw.Draw(mask)
    for kind, box in regions:
        if kind in {"rect", "box"}:
            draw.rectangle(box, fill=255)
        elif kind == "ellipse":
            draw.ellipse(box, fill=255)
        else:
            raise SystemExit(f"unsupported region draw kind: {kind}")
    return mask


def load_existing_mask(image_path: Path, mask_path: Path, invert: bool):
    if not mask_path.exists():
        raise SystemExit(f"mask not found: {mask_path}")
    with Image.open(image_path) as src:
        size = src.size
    with Image.open(mask_path) as m:
        mask = m.convert("L")
        if mask.size != size:
            mask = mask.resize(size)
        if invert:
            mask = Image.eval(mask, lambda px: 255 - px)
    return mask


def save_mask(mask, mask_dir: Path, prefix: str):
    out = mask_dir / f"{prefix}_mask_{uuid.uuid4().hex[:8]}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    mask.save(out)
    return out


def prepare_mask(image_path: Path, args):
    mask_dir = Path(args.mask_dir)
    if args.mask:
        mask = load_existing_mask(image_path, Path(args.mask), args.invert)
        mask = apply_expand_shrink(mask, args.expand, args.shrink)
        if args.feather > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(radius=args.feather))
        return save_mask(mask, mask_dir, args.prefix)
    with Image.open(image_path) as src:
        w, h = src.size
    regions = collect_regions(args, w, h)
    mask = Image.new("L", (w, h), 0)
    draw_regions(mask, regions)
    mask = apply_expand_shrink(mask, args.expand, args.shrink)
    if args.feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=args.feather))
    if args.invert:
        mask = Image.eval(mask, lambda px: 255 - px)
    return save_mask(mask, mask_dir, args.prefix)


def main():
    args = parse_args()
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"image not found: {image_path}")
    mask_path = prepare_mask(image_path, args)
    if args.mask_only:
        print(mask_path)
        return
    edit_script = Path(__file__).resolve().parent / "edit_image.py"
    cmd = [sys.executable, str(edit_script), "--image", str(image_path), "--mask", str(mask_path), "--prompt", args.prompt, "--out-dir", args.out_dir, "--prefix", args.prefix]
    if args.config:
        cmd.extend(["--config", args.config])
    if args.provider:
        cmd.extend(["--provider", args.provider])
    if args.model:
        cmd.extend(["--model", args.model])
    if args.endpoint:
        cmd.extend(["--endpoint", args.endpoint])
    if args.no_download:
        cmd.append("--no-download")
    if args.print_json:
        cmd.append("--print-json")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        raise SystemExit(result.returncode)
    if not args.print_json:
        print(f"MASK_USED: {mask_path}")


if __name__ == "__main__":
    main()
