#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

from media_request_common import default_mask_dir, default_output_dir


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MASK_DIR = str(default_mask_dir())
DEFAULT_OUT_DIR = str(default_output_dir("images"))


def parse_args():
    p = argparse.ArgumentParser(description="Prepare an object/background mask and pass it into the localized edit workflow.")
    p.add_argument("--image", required=True, help="Source image path")
    p.add_argument("--prompt", required=True, help="Edit request text")
    p.add_argument("--selection-mode", choices=["alpha", "corner-bg"], default="corner-bg", help="How to derive the base object mask")
    p.add_argument("--edit-target", choices=["object", "background"], default="object", help="Which region to edit after mask preparation")
    p.add_argument("--threshold", type=int, default=40, help="Forwarded object-mask threshold")
    p.add_argument("--sample-size", type=int, default=8, help="Forwarded corner sample size")
    p.add_argument("--expand", type=int, default=0, help="Grow the prepared selection mask before use")
    p.add_argument("--shrink", type=int, default=0, help="Shrink the prepared selection mask before use")
    p.add_argument("--feather", type=float, default=8.0, help="Feather radius for the final edit mask")
    p.add_argument("--mask-dir", default=DEFAULT_MASK_DIR, help="Directory for generated masks")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory for final edited outputs")
    p.add_argument("--prefix", default="object-edit", help="Filename prefix")
    p.add_argument("--config", help="Forwarded config path for mask_inpaint.py / edit_image.py")
    p.add_argument("--provider", help="Forwarded provider for mask_inpaint.py / edit_image.py")
    p.add_argument("--model", help="Forwarded image edit model for mask_inpaint.py / edit_image.py")
    p.add_argument("--endpoint", help="Forwarded endpoint for mask_inpaint.py / edit_image.py")
    p.add_argument("--prepare-only", action="store_true", help="Only prepare and save the final mask, then exit")
    p.add_argument("--print-json", action="store_true", help="Print structured JSON output")
    p.add_argument("--no-download", action="store_true", help="Forward --no-download to mask_inpaint.py")
    return p.parse_args()


def run_cmd(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def main():
    args = parse_args()
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"image not found: {image_path}")
    mask_dir = Path(args.mask_dir)
    mask_dir.mkdir(parents=True, exist_ok=True)
    base_mask = mask_dir / f"{args.prefix}_base_object_mask.png"
    prep_cmd = [
        sys.executable, str(SCRIPT_DIR / "prepare_object_mask.py"),
        "--image", str(image_path),
        "--mode", args.selection_mode,
        "--threshold", str(args.threshold),
        "--sample-size", str(args.sample_size),
        "--expand", str(args.expand),
        "--shrink", str(args.shrink),
        "--feather", str(args.feather),
        "--out", str(base_mask),
    ]
    if args.edit_target == "background":
        prep_cmd.append("--invert")
    prep = run_cmd(prep_cmd)
    if prep.returncode != 0:
        if prep.stdout:
            print(prep.stdout, end="")
        if prep.stderr:
            print(prep.stderr, file=sys.stderr, end="")
        raise SystemExit(prep.returncode)
    final_mask = prep.stdout.strip().splitlines()[-1]
    summary = {"image": str(image_path), "selection_mode": args.selection_mode, "edit_target": args.edit_target, "mask": final_mask, "edited": None}
    if args.prepare_only:
        if args.print_json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(final_mask)
        return
    edit_cmd = [
        sys.executable, str(SCRIPT_DIR / "mask_inpaint.py"),
        "--image", str(image_path),
        "--mask", final_mask,
        "--prompt", args.prompt,
        "--out-dir", args.out_dir,
        "--prefix", args.prefix,
        "--feather", "0",
    ]
    if args.config:
        edit_cmd.extend(["--config", args.config])
    if args.provider:
        edit_cmd.extend(["--provider", args.provider])
    if args.model:
        edit_cmd.extend(["--model", args.model])
    if args.endpoint:
        edit_cmd.extend(["--endpoint", args.endpoint])
    if args.no_download:
        edit_cmd.append("--no-download")
    if args.print_json:
        edit_cmd.append("--print-json")
    edit = run_cmd(edit_cmd)
    if edit.returncode != 0:
        if edit.stdout:
            print(edit.stdout, end="")
        if edit.stderr:
            print(edit.stderr, file=sys.stderr, end="")
        raise SystemExit(edit.returncode)
    summary["edited"] = edit.stdout.strip()
    if args.print_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(edit.stdout, end="")


if __name__ == "__main__":
    main()
