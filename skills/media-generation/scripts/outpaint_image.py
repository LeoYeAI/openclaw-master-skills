#!/usr/bin/env python3
import argparse
import subprocess
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageFilter

from media_request_common import default_output_dir, default_outpaint_work_dir

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS


def parse_args():
    p = argparse.ArgumentParser(description="Prepare an expanded canvas and call the image-edit helper.")
    p.add_argument("--image", required=True, help="Path to the source image")
    p.add_argument("--prompt", default="", help="Request text passed to the edit model")
    p.add_argument("--out-dir", default=str(default_output_dir("images")), help="Directory for final edited outputs")
    p.add_argument("--work-dir", default=str(default_outpaint_work_dir()), help="Directory for prepared canvas inputs")
    p.add_argument("--prefix", default="outpaint", help="Filename prefix")
    p.add_argument("--config", help="Forwarded config path for edit_image.py")
    p.add_argument("--provider", help="Forwarded provider for edit_image.py")
    p.add_argument("--model", help="Forwarded image edit model for edit_image.py")
    p.add_argument("--endpoint", help="Forwarded endpoint for edit_image.py")
    p.add_argument("--expand", type=int, default=0, help="Expand all sides by this many pixels")
    p.add_argument("--left", type=int, default=0, help="Expand left side by pixels")
    p.add_argument("--right", type=int, default=0, help="Expand right side by pixels")
    p.add_argument("--top", type=int, default=0, help="Expand top side by pixels")
    p.add_argument("--bottom", type=int, default=0, help="Expand bottom side by pixels")
    p.add_argument("--mode", choices=["transparent", "blur", "solid"], default="transparent", help="How to initialize the expanded canvas")
    p.add_argument("--bg", default="#00000000", help="Background color for solid mode, e.g. '#ffffffff' or '#101010'")
    p.add_argument("--blur-radius", type=int, default=24, help="Blur radius for blur mode")
    p.add_argument("--no-download", action="store_true", help="Forward --no-download to edit_image.py")
    p.add_argument("--print-json", action="store_true", help="Forward --print-json to edit_image.py")
    return p.parse_args()


def parse_color(value: str):
    text = value.strip()
    if text.startswith("#"):
        hexv = text[1:]
        if len(hexv) == 6:
            return tuple(int(hexv[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        if len(hexv) == 8:
            return tuple(int(hexv[i:i+2], 16) for i in (0, 2, 4, 6))
    raise SystemExit(f"invalid --bg color: {value}")


def prepare_canvas(src_path: Path, out_path: Path, left: int, right: int, top: int, bottom: int, mode: str, bg: str, blur_radius: int):
    with Image.open(src_path) as im:
        src = im.convert("RGBA")
        w, h = src.size
        new_w = w + left + right
        new_h = h + top + bottom
        if new_w <= 0 or new_h <= 0:
            raise SystemExit("expanded size must be positive")
        if mode == "transparent":
            canvas = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
        elif mode == "solid":
            canvas = Image.new("RGBA", (new_w, new_h), parse_color(bg))
        else:
            scale = max(new_w / w, new_h / h)
            bw = max(new_w, int(round(w * scale)))
            bh = max(new_h, int(round(h * scale)))
            blurred = src.resize((bw, bh), RESAMPLE_LANCZOS)
            blurred = blurred.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            x = max(0, (bw - new_w) // 2)
            y = max(0, (bh - new_h) // 2)
            canvas = blurred.crop((x, y, x + new_w, y + new_h)).convert("RGBA")
        canvas.alpha_composite(src, (left, top))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path)


def main():
    args = parse_args()
    src_path = Path(args.image)
    if not src_path.exists():
        raise SystemExit(f"image not found: {src_path}")
    left = args.left + args.expand
    right = args.right + args.expand
    top = args.top + args.expand
    bottom = args.bottom + args.expand
    if left == right == top == bottom == 0:
        raise SystemExit("specify at least one of --expand/--left/--right/--top/--bottom")
    prepared = Path(args.work_dir) / f"{args.prefix}_input_{uuid.uuid4().hex[:8]}.png"
    prepare_canvas(src_path, prepared, left, right, top, bottom, args.mode, args.bg, args.blur_radius)
    edit_script = Path(__file__).resolve().parent / "edit_image.py"
    cmd = [sys.executable, str(edit_script), "--image", str(prepared), "--prompt", args.prompt, "--out-dir", args.out_dir, "--prefix", args.prefix]
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
        print(f"PREPARED_INPUT: {prepared}")
        print(f"EXPAND: left={left} right={right} top={top} bottom={bottom}")
        print(f"MODE: {args.mode}")


if __name__ == "__main__":
    main()
