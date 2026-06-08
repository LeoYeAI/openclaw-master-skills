#!/usr/bin/env python3
"""Convert an EXR image sequence to MP4 video.

Two-step process:
1. Convert EXR frames to PNG via oiiotool (with optional ACES display transform + exposure)
2. Encode PNG sequence to MP4 via ffmpeg

Requires: oiiotool (pip install openimageio), ffmpeg in PATH
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def detect_sequence(directory):
    """Detect EXR sequence in a directory.

    Returns:
        (pattern, start_frame, end_frame, frame_count, name_template)
        where name_template is like 'name.{frame}.exr'
    """
    exr_files = sorted(glob.glob(os.path.join(directory, "*.exr")))
    if not exr_files:
        return None

    # Extract frame numbers — try common patterns:
    # name.1001.exr, name_00001.exr, frame_00001.exr, etc.
    frames = []
    for f in exr_files:
        basename = os.path.basename(f)
        # Try dotted frame number: name.1001.exr
        m = re.match(r"^(.+?)\.(\d+)\.exr$", basename, re.IGNORECASE)
        if m:
            frames.append((int(m.group(2)), m.group(1), "dot", len(m.group(2))))
            continue
        # Try underscored: name_00001.exr
        m = re.match(r"^(.+?)_(\d+)\.exr$", basename, re.IGNORECASE)
        if m:
            frames.append((int(m.group(2)), m.group(1), "underscore", len(m.group(2))))
            continue

    if not frames:
        return None

    frames.sort(key=lambda x: x[0])
    prefix = frames[0][1]
    sep_style = frames[0][2]
    padding = frames[0][3]
    start = frames[0][0]
    end = frames[-1][0]

    sep = "." if sep_style == "dot" else "_"

    return {
        "prefix": prefix,
        "separator": sep,
        "padding": padding,
        "start": start,
        "end": end,
        "count": len(frames),
        "directory": directory,
    }


def run_cmd(cmd, description=""):
    """Run a command, print output on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error{' (' + description + ')' if description else ''}: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert EXR image sequence to MP4 video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s /path/to/exr_sequence/
  %(prog)s /path/to/exr_sequence/ --fps 24 --crf 18
  %(prog)s /path/to/exr_sequence/ --display "sRGB - Display" --view "ACES 1.0 - SDR Video"
  %(prog)s /path/to/exr_sequence/ --exposure -4
  %(prog)s /path/to/exr_sequence/ --no-aces --output comp.mp4
""",
    )
    parser.add_argument("directory", help="Directory containing EXR sequence")
    parser.add_argument("--fps", type=float, default=None, help="Frame rate (default: auto-detect from EXR metadata, fallback 24)")
    parser.add_argument("--crf", type=int, default=18, help="H.264 CRF quality (0-51, lower=better, default: 18)")
    parser.add_argument("--preset", default="slow", help="H.264 preset (default: slow)")
    parser.add_argument("--display", default="sRGB - Display", help="OCIO display (default: sRGB - Display)")
    parser.add_argument("--view", default="ACES 1.0 - SDR Video", help="OCIO view (default: ACES 1.0 - SDR Video)")
    parser.add_argument("--no-aces", action="store_true", help="Use simple linear->sRGB instead of ACES display transform")
    parser.add_argument("--exposure", type=float, default=0, help="Exposure adjustment in stops (default: 0)")
    parser.add_argument("--output", default=None, help="Output MP4 path (default: <sequence_name>.mp4 in sequence dir)")
    parser.add_argument("--read-channels", default=None, help="Channels to read (e.g., R,G,B). Saves memory on multichannel EXRs.")
    parser.add_argument("--keep-pngs", action="store_true", help="Keep intermediate PNG files")
    parser.add_argument("--resize", default=None, help="Resize before encoding (e.g., 1920x1080, 50%%)")

    args = parser.parse_args()

    # Check dependencies
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found in PATH", file=sys.stderr)
        return 1

    # Detect sequence
    seq = detect_sequence(args.directory)
    if not seq:
        print(f"No EXR sequence found in: {args.directory}", file=sys.stderr)
        return 1

    print(f"Sequence: {seq['prefix']}{seq['separator']}***.exr")
    print(f"Frames: {seq['start']}-{seq['end']} ({seq['count']} frames)")

    # Auto-detect fps from first frame metadata if not specified
    fps = args.fps
    if fps is None:
        first_exr = os.path.join(
            seq["directory"],
            f"{seq['prefix']}{seq['separator']}{str(seq['start']).zfill(seq['padding'])}.exr",
        )
        result = subprocess.run(
            ["oiiotool", "--info", "-v", first_exr],
            capture_output=True, text=True,
        )
        fps_match = re.search(r"framesPerSecond:\s*(\d+)/(\d+)", result.stdout)
        if fps_match:
            fps = int(fps_match.group(1)) / int(fps_match.group(2))
            print(f"FPS: {fps} (from metadata)")
        else:
            fps = 24.0
            print(f"FPS: {fps} (default)")

    # Create temp dir for PNGs
    if args.keep_pngs:
        png_dir = os.path.join(seq["directory"], "_tmp_png")
        os.makedirs(png_dir, exist_ok=True)
    else:
        tmp_obj = tempfile.TemporaryDirectory()
        png_dir = tmp_obj.name

    try:
        # Convert frames
        print(f"Converting {seq['count']} frames to PNG ...")
        for i in range(seq["start"], seq["end"] + 1):
            frame_str = str(i).zfill(seq["padding"])
            exr_path = os.path.join(
                seq["directory"],
                f"{seq['prefix']}{seq['separator']}{frame_str}.exr",
            )
            png_path = os.path.join(
                png_dir,
                f"{seq['prefix']}{seq['separator']}{frame_str}.png",
            )

            if not os.path.exists(exr_path):
                continue

            oiio_args = []

            # Input with optional channel selection
            if args.read_channels:
                oiio_args += [f"-i:ch={args.read_channels}", exr_path]
            else:
                oiio_args += [exr_path]

            # Exposure
            if args.exposure != 0:
                mul = 2.0 ** args.exposure
                oiio_args += ["--mulc", str(mul)]

            # Resize
            if args.resize:
                oiio_args += ["--resize", args.resize]

            # Color transform
            if args.no_aces:
                oiio_args += ["--colorconvert", "linear", "srgb"]
            else:
                oiio_args += ["--ociodisplay", args.display, args.view]

            oiio_args += ["-d", "uint8", "-o", png_path]

            if not run_cmd(["oiiotool"] + oiio_args):
                print(f"Failed on frame {frame_str}", file=sys.stderr)
                return 1

            # Progress
            frame_idx = i - seq["start"] + 1
            if frame_idx % 10 == 0 or frame_idx == seq["count"]:
                print(f"  {frame_idx}/{seq['count']}", flush=True)

        # Encode with ffmpeg
        print("Encoding MP4 ...")

        # Determine ffmpeg input pattern
        # Use %d for unpadded, %0Nd for padded
        if seq["padding"] > 1:
            ff_pattern = f"{seq['prefix']}{seq['separator']}%0{seq['padding']}d.png"
        else:
            ff_pattern = f"{seq['prefix']}{seq['separator']}%d.png"

        # Output path
        if args.output:
            out_path = args.output
        else:
            out_path = os.path.join(seq["directory"], f"{seq['prefix']}.mp4")

        ff_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-start_number", str(seq["start"]),
            "-i", os.path.join(png_dir, ff_pattern),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", str(args.crf),
            "-preset", args.preset,
            out_path,
        ]

        if not run_cmd(ff_cmd, "ffmpeg encode"):
            return 1

        size_mb = os.path.getsize(out_path) / 1024 / 1024
        print(f"Done: {out_path} ({size_mb:.1f} MB, {fps} fps, {seq['count']} frames)")

    finally:
        if not args.keep_pngs and hasattr(tmp_obj, "cleanup"):
            tmp_obj.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
