#!/usr/bin/env python3
"""
Extract audio from a video file using FFmpeg.
Cross-platform replacement for extract_audio.sh.

Usage: python3 extract_audio.py <video_path>
Output: <video_dir>/<video_name>_audio.wav
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Extract audio from video")
    parser.add_argument("video_path", help="Path to the video file")
    args = parser.parse_args()

    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"Error: File not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    video_dir = os.path.dirname(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(video_dir, f"{video_name}_audio.wav")

    print(f"Extracting audio from: {video_path}")
    print(f"Output: {output_path}")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Audio extraction complete: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
