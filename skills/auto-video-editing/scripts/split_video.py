#!/usr/bin/env python3
"""
Split a video into individual sentence-level clips based on transcript timestamps.
Usage: python3 split_video.py <video_path> <transcript_json_path>
Output: <video_dir>/<video_name>_clips/clip_001.mp4, clip_002.mp4, ...
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import detect_gpu, get_ffmpeg_encode_args


def main():
    parser = argparse.ArgumentParser(description="Split video into sentence clips")
    parser.add_argument("video_path", help="Path to the source video file")
    parser.add_argument("transcript_path", help="Path to the transcript JSON file")
    parser.add_argument("--padding", type=float, default=0.0,
                        help="Padding in seconds added before/after each clip (default: 0.0)")
    args = parser.parse_args()

    video_path = args.video_path
    transcript_path = args.transcript_path

    if not os.path.isfile(video_path):
        print(f"Error: Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(transcript_path):
        print(f"Error: Transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    segments = transcript.get("segments", [])
    if not segments:
        print("Error: No segments found in transcript", file=sys.stderr)
        sys.exit(1)

    video_dir = os.path.dirname(os.path.abspath(video_path))
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    clips_dir = os.path.join(video_dir, f"{video_name}_clips")
    os.makedirs(clips_dir, exist_ok=True)

    print(f"Splitting video into {len(segments)} clips...")
    print(f"Output directory: {clips_dir}")

    # Get video duration for boundary clamping
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        duration_str = subprocess.check_output(probe_cmd, text=True).strip()
        video_duration = float(duration_str)
    except (subprocess.CalledProcessError, ValueError):
        video_duration = None

    # Detect GPU and choose encoder
    gpu_info = detect_gpu()
    encode_args = get_ffmpeg_encode_args(gpu_info)
    print(f"Video encoder: {encode_args[1]}")

    for seg in segments:
        seg_id = seg["id"]
        start = max(0, seg["start"] - args.padding)
        end = seg["end"] + args.padding
        if video_duration is not None:
            end = min(end, video_duration)

        clip_duration = end - start
        clip_filename = f"clip_{seg_id:03d}.mp4"
        clip_path = os.path.join(clips_dir, clip_filename)

        # Always re-encode for precise audio/video cuts (stream copy causes keyframe-aligned cuts
        # which can include audio from adjacent segments)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ss", str(start),
            "-t", str(clip_duration),
        ] + encode_args + [
            "-c:a", "aac", "-b:a", "192k",
            "-avoid_negative_ts", "make_zero",
            clip_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  clip_{seg_id:03d}.mp4  [{start:.2f}s - {end:.2f}s]  {seg['text']}")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR on clip_{seg_id:03d}: {e.stderr[:200]}", file=sys.stderr)

    print(f"\nSplitting complete. {len(segments)} clips saved to: {clips_dir}")


if __name__ == "__main__":
    main()
