#!/usr/bin/env python3
"""
Merge selected video clips into a single final video.
Usage: python3 merge_clips.py <clips_dir> --select "1-4,6,8" [--output <output_path>]
Output: Merged video file.

Selection format:
  - Range:    1-4       (clips 1, 2, 3, 4)
  - List:     1,3,5,7   (clips 1, 3, 5, 7)
  - Mixed:    1-4,6,8-10 (clips 1, 2, 3, 4, 6, 8, 9, 10)
"""

import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import detect_gpu, get_ffmpeg_encode_args, get_ffmpeg_encoder


def parse_selection(selection_str):
    """Parse selection string like '1-4,6,8-10' into a sorted list of integers."""
    result = []
    parts = selection_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            bounds = part.split("-", 1)
            try:
                start = int(bounds[0].strip())
                end = int(bounds[1].strip())
            except ValueError:
                print(f"Error: Invalid range '{part}'", file=sys.stderr)
                sys.exit(1)
            if start > end:
                print(f"Error: Invalid range '{part}' (start > end)", file=sys.stderr)
                sys.exit(1)
            result.extend(range(start, end + 1))
        else:
            try:
                result.append(int(part))
            except ValueError:
                print(f"Error: Invalid number '{part}'", file=sys.stderr)
                sys.exit(1)
    # Deduplicate and sort
    return sorted(set(result))


def main():
    parser = argparse.ArgumentParser(description="Merge selected video clips")
    parser.add_argument("clips_dir", help="Path to the clips directory")
    parser.add_argument("--select", required=True,
                        help="Clip selection (e.g. '1-4,6,8-10')")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: <clips_dir>/../<name>_final.mp4)")
    parser.add_argument("--reencode", action="store_true",
                        help="Re-encode clips for seamless concatenation (slower but more compatible)")
    args = parser.parse_args()

    clips_dir = os.path.abspath(args.clips_dir)
    if not os.path.isdir(clips_dir):
        print(f"Error: Clips directory not found: {clips_dir}", file=sys.stderr)
        sys.exit(1)

    selected_ids = parse_selection(args.select)
    print(f"Selected clips: {selected_ids}")

    # Verify all selected clips exist
    clip_files = []
    missing = []
    for clip_id in selected_ids:
        clip_filename = f"clip_{clip_id:03d}.mp4"
        clip_path = os.path.join(clips_dir, clip_filename)
        if os.path.isfile(clip_path):
            clip_files.append(clip_path)
        else:
            missing.append(clip_filename)

    if missing:
        print(f"Error: Missing clips: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if not clip_files:
        print("Error: No clips selected", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        parent_dir = os.path.dirname(clips_dir)
        dir_name = os.path.basename(clips_dir).replace("_clips", "")
        output_path = os.path.join(parent_dir, f"{dir_name}_final.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Detect GPU for re-encode fallback
    gpu_info = detect_gpu()
    encode_args = get_ffmpeg_encode_args(gpu_info)

    print(f"Merging {len(clip_files)} clips into: {output_path}")

    def _reencode_merge():
        """Re-encode merge using filter_complex concat."""
        filter_concat = ""
        input_args = []
        for i, cp in enumerate(clip_files):
            input_args.extend(["-i", cp])
            filter_concat += f"[{i}:v:0][{i}:a:0]"
        filter_concat += f"concat=n={len(clip_files)}:v=1:a=1[outv][outa]"

        cmd = ["ffmpeg", "-y"] + input_args + [
            "-filter_complex", filter_concat,
            "-map", "[outv]", "-map", "[outa]",
        ] + encode_args + [
            "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    if args.reencode:
        _reencode_merge()
    else:
        # Concat demuxer mode (fast, no re-encoding)
        concat_list_fd, concat_list_path = tempfile.mkstemp(suffix=".txt", prefix="concat_")
        try:
            with os.fdopen(concat_list_fd, "w", encoding="utf-8") as f:
                for clip_path in clip_files:
                    # Use forward slashes for cross-platform compat
                    safe_path = clip_path.replace("\\", "/").replace("'", "'\\''")
                    f.write(f"file '{safe_path}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list_path,
                "-c", "copy",
                output_path
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError:
                print("  Concat copy failed, falling back to re-encode mode...")
                _reencode_merge()
        finally:
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)

    print(f"\nMerge complete: {output_path}")


if __name__ == "__main__":
    main()
