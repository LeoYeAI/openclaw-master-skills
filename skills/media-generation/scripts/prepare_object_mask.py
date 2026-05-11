#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


def parse_args():
    p = argparse.ArgumentParser(description="Prepare a practical object/background mask from alpha or simple corner-background separation.")
    p.add_argument("--image", required=True, help="Source image path")
    p.add_argument("--mode", choices=["alpha", "corner-bg"], default="corner-bg", help="Mask derivation mode")
    p.add_argument("--threshold", type=int, default=40, help="Difference threshold for corner-bg mode or alpha threshold for alpha mode")
    p.add_argument("--sample-size", type=int, default=8, help="Corner sample square size for corner-bg mode")
    p.add_argument("--invert", action="store_true", help="Invert the generated mask")
    p.add_argument("--expand", type=int, default=0, help="Expand the white mask region before feathering")
    p.add_argument("--shrink", type=int, default=0, help="Shrink the white mask region before feathering")
    p.add_argument("--feather", type=float, default=4.0, help="Gaussian blur radius for soft edges")
    p.add_argument("--out", help="Output mask path")
    return p.parse_args()


def average_rgb(values):
    count = max(len(values), 1)
    return tuple(int(sum(channel[i] for channel in values) / count) for i in range(3))


def build_corner_bg_mask(img: Image.Image, threshold: int, sample_size: int):
    rgb = img.convert("RGB")
    w, h = rgb.size
    s = max(1, min(sample_size, w, h))
    corners = [
        rgb.crop((0, 0, s, s)),
        rgb.crop((w - s, 0, w, s)),
        rgb.crop((0, h - s, s, h)),
        rgb.crop((w - s, h - s, w, h)),
    ]
    samples = []
    for corner in corners:
        samples.extend(list(corner.getdata()))
    bg = average_rgb(samples)

    out = Image.new("L", rgb.size, 0)
    src = rgb.load()
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
            dst[x, y] = 255 if dist >= threshold else 0
    return out


def build_alpha_mask(img: Image.Image, threshold: int):
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    return alpha.point(lambda v: 255 if v >= threshold else 0)


def apply_grow_shrink(mask: Image.Image, expand: int, shrink: int):
    result = mask
    if expand > 0:
        result = result.filter(ImageFilter.MaxFilter(size=expand * 2 + 1))
    if shrink > 0:
        result = result.filter(ImageFilter.MinFilter(size=shrink * 2 + 1))
    return result


def main():
    args = parse_args()
    path = Path(args.image)
    if not path.exists():
        raise SystemExit(f"image not found: {path}")
    img = Image.open(path)

    if args.mode == "alpha":
        mask = build_alpha_mask(img, args.threshold)
        if img.mode != "RGBA" and "A" not in img.getbands():
            print("WARN: alpha mode was requested but the source image has no alpha channel; the result may be fully empty or fully solid.", file=sys.stderr)
    else:
        mask = build_corner_bg_mask(img, args.threshold, args.sample_size)

    mask = apply_grow_shrink(mask, args.expand, args.shrink)
    if args.feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=args.feather))
    if args.invert:
        mask = ImageChops.invert(mask)

    out_path = Path(args.out) if args.out else path.with_name(path.stem + "_object_mask.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mask.save(out_path)
    print(str(out_path))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
