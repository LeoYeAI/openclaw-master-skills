#!/usr/bin/env python3
"""Generate a multi-exposure composite contact sheet from an HDR EXR file.

Creates a grid of the same image at different exposure levels, with EV labels
burned in, and saves as a single image for easy review/sharing.

Requires: oiiotool (pip install openimageio), Pillow
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def run_oiiotool(args):
    """Run oiiotool with the given arguments. Returns True on success."""
    cmd = ["oiiotool"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"oiiotool error: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def get_font(size=28):
    """Try to load a monospace font, fall back to default."""
    font_paths = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    parser = argparse.ArgumentParser(
        description="Generate multi-exposure composite from an HDR EXR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s input.exr
  %(prog)s input.exr --stops -8,-6,-4,-2,0,2,4,6,8
  %(prog)s input.exr --display "sRGB - Display" --view "ACES 1.0 - SDR Video"
  %(prog)s input.exr --cols 4 --output sweep.jpg
  %(prog)s input.exr --no-composite --output-dir ./exposures/
""",
    )
    parser.add_argument("input", help="Input EXR file")
    parser.add_argument(
        "--stops", default="-8,-7,-6,-5,-4,-2,0,2,4,5,6,7,8",
        help="Comma-separated exposure stops (default: -8,-7,-6,-5,-4,-2,0,2,4,5,6,7,8)",
    )
    parser.add_argument("--display", default="sRGB - Display", help="OCIO display (default: sRGB - Display)")
    parser.add_argument("--view", default="ACES 1.0 - SDR Video", help="OCIO view (default: ACES 1.0 - SDR Video)")
    parser.add_argument("--no-aces", action="store_true", help="Use simple linear->sRGB instead of ACES display transform")
    parser.add_argument("--cols", type=int, default=3, help="Number of columns in composite grid (default: 3)")
    parser.add_argument("--output", default=None, help="Output file path (default: <input>_exposures_composite.jpg)")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality (default: 90)")
    parser.add_argument("--no-composite", action="store_true", help="Save individual PNGs instead of composite")
    parser.add_argument("--output-dir", default=None, help="Output directory for individual PNGs (with --no-composite)")
    parser.add_argument("--read-channels", default=None, help="Channels to read from EXR (e.g., R,G,B). Saves memory on multichannel EXRs.")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    stops = [float(s.strip()) for s in args.stops.split(",")]

    with tempfile.TemporaryDirectory() as tmpdir:
        png_paths = []

        for ev in stops:
            mul = 2.0 ** ev
            sign = "+" if ev > 0 else ""
            label = f"exp{sign}{ev:g}"

            if args.no_composite:
                out_dir = args.output_dir or str(input_path.parent)
                os.makedirs(out_dir, exist_ok=True)
                png_path = os.path.join(out_dir, f"{input_path.stem}_{label}.png")
            else:
                png_path = os.path.join(tmpdir, f"{label}.png")

            # Build oiiotool command
            oiio_args = []
            if args.read_channels:
                oiio_args += [f"-i:ch={args.read_channels}", str(input_path)]
            else:
                oiio_args += [str(input_path)]

            oiio_args += ["--mulc", str(mul)]

            if args.no_aces:
                oiio_args += ["--colorconvert", "linear", "srgb"]
            else:
                oiio_args += ["--ociodisplay", args.display, args.view]

            oiio_args += ["-d", "uint8", "-o", png_path]

            print(f"  EV {sign}{ev:g} (x{mul:g}) ...", end=" ", flush=True)
            if not run_oiiotool(oiio_args):
                return 1
            print("done")

            png_paths.append((ev, png_path))

        if args.no_composite:
            print(f"\nSaved {len(png_paths)} individual exposure PNGs")
            return 0

        # Build composite
        print("Building composite ...", end=" ", flush=True)
        images = [(ev, Image.open(p)) for ev, p in png_paths]
        w, h = images[0][1].size
        label_h = 40
        row_h = h + label_h
        cols = args.cols
        rows = (len(images) + cols - 1) // cols

        composite = Image.new("RGB", (w * cols, row_h * rows), (26, 26, 26))
        draw = ImageDraw.Draw(composite)
        font = get_font(28)

        for i, (ev, img) in enumerate(images):
            col = i % cols
            row = i // cols
            x = col * w
            y = row * row_h

            # Label bar
            draw.rectangle([x, y, x + w, y + label_h], fill=(30, 30, 30))
            sign = "+" if ev > 0 else ""
            label = f"EV {sign}{ev:g}"
            color = (102, 255, 102) if ev > 0 else (255, 102, 102) if ev < 0 else (255, 255, 0)
            draw.text((x + 10, y + 6), label, fill=color, font=font)

            # Image
            composite.paste(img, (x, y + label_h))

        # Output path
        if args.output:
            out_path = args.output
        else:
            out_path = str(input_path.parent / f"{input_path.stem}_exposures_composite.jpg")

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        if out_path.lower().endswith(".png"):
            composite.save(out_path)
        else:
            composite.save(out_path, quality=args.quality)

        size_mb = os.path.getsize(out_path) / 1024 / 1024
        print(f"done\nSaved: {out_path} ({composite.size[0]}x{composite.size[1]}, {size_mb:.1f} MB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
