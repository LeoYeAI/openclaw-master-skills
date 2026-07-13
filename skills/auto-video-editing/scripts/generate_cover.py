#!/usr/bin/env python3
"""
Replace the first frame of a video with a cover frame that has title text overlay.

Usage:
  python3 generate_cover.py <video_path> --title "视频标题"
  python3 generate_cover.py <video_path> --transcript <transcript.json>

If --title is not provided but --transcript is, the transcript text will be
printed for the AI agent to summarize from the audience's perspective, then
call again with --title.

The script replaces the video's first frame with a title-overlaid version,
outputting a new video file. The original video is not modified.

Output: <video_name>_with_cover.mp4 (in the same directory as the video)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    find_chinese_font as _find_font, sanitize_title,
    detect_gpu, get_ffmpeg_encode_args, escape_ffmpeg_path,
)


def get_video_info(video_path):
    """Get video duration, width, height, and frame rate."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path,
    ]
    result = subprocess.check_output(cmd, text=True)
    info = json.loads(result)
    fmt_duration = float(info.get("format", {}).get("duration", 0))
    streams = info.get("streams", [{}])
    s = streams[0] if streams else {}
    w = s.get("width", 1080)
    h = s.get("height", 1920)
    # Parse frame rate like "30/1" or "29.97"
    r_str = s.get("r_frame_rate", "30/1")
    if "/" in r_str:
        num, den = r_str.split("/")
        fps = float(num) / float(den) if float(den) != 0 else 30.0
    else:
        fps = float(r_str)
    stream_duration = float(s.get("duration", 0))
    duration = stream_duration if stream_duration > 0 else fmt_duration
    return duration, w, h, fps


def extract_first_frame(video_path, output_path):
    """Extract the first frame of a video as a PNG image (lossless)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "1",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _wrap_title(title, font_size=60, img_width=1080):
    """Split title into lines that fit the image width."""
    usable = img_width * 0.80
    chars_per_line = max(4, int(usable / font_size))

    if len(title) <= chars_per_line:
        return [title]

    lines = []
    remaining = title
    while remaining:
        if len(remaining) <= chars_per_line:
            lines.append(remaining)
            break
        cut = chars_per_line
        best = cut
        for offset in range(min(4, cut)):
            for pos in [cut - offset, cut + offset]:
                if 0 < pos < len(remaining) and remaining[pos] in ' ,，。、；：！？·':
                    best = pos + 1 if remaining[pos] != ' ' else pos
                    break
            else:
                continue
            break
        else:
            best = cut
        lines.append(remaining[:best].strip())
        remaining = remaining[best:].strip()

    return lines


def build_drawtext_filters(title, font_path, width, height):
    """Build ffmpeg drawtext filter string for title overlay."""
    short_side = min(width, height)
    font_size = max(36, min(int(short_side * 0.06), 120))

    lines = _wrap_title(title, font_size=font_size, img_width=width)

    line_height = int(font_size * 1.5)
    block_height = len(lines) * line_height
    start_y = int(height * 0.40) - block_height // 2

    escaped_font = escape_ffmpeg_path(font_path) if font_path else ""

    filters = []
    for i, line in enumerate(lines):
        escaped_text = line.replace("\\", "\\\\").replace("'", "\u2019")
        escaped_text = escaped_text.replace(":", "\\:")
        y = start_y + i * line_height

        f = (
            f"drawtext=text='{escaped_text}'"
            f":fontsize={font_size}"
            f":fontcolor=white"
            f":borderw=4:bordercolor=black@0.8"
            f":shadowcolor=black@0.5:shadowx=3:shadowy=3"
            f":x=(w-text_w)/2:y={y}"
        )
        if escaped_font:
            f += f":fontfile='{escaped_font}'"
        filters.append(f)

    return ",".join(filters)


def replace_first_frame(video_path, cover_image_path, output_path, fps):
    """Replace the first frame of the video with the cover image.

    Strategy:
    1. Create a short video clip from the cover image (duration = 1 frame).
    2. Trim the original video starting from the 2nd frame.
    3. Concatenate: cover_clip + rest_of_video.
    """
    frame_duration = 1.0 / fps

    tmp_dir = tempfile.mkdtemp(prefix="cover_")
    cover_clip = os.path.join(tmp_dir, "cover_clip.mp4")
    rest_clip = os.path.join(tmp_dir, "rest.mp4")
    concat_list = os.path.join(tmp_dir, "concat.txt")

    # GPU-accelerated encoding
    encode_args = get_ffmpeg_encode_args()

    try:
        # Step 1: Create a 1-frame video from the cover image
        cmd_cover = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", cover_image_path,
            "-t", str(frame_duration),
            "-r", str(fps),
        ] + encode_args + [
            "-pix_fmt", "yuv420p",
            "-an",
            cover_clip,
        ]
        subprocess.run(cmd_cover, check=True, capture_output=True, text=True)

        # Step 2: Trim the original video, skip the first frame
        cmd_rest = [
            "ffmpeg", "-y",
            "-ss", str(frame_duration),
            "-i", video_path,
        ] + encode_args + [
            "-c:a", "aac", "-b:a", "192k",
            rest_clip,
        ]
        subprocess.run(cmd_rest, check=True, capture_output=True, text=True)

        # Step 3: Concatenate cover_clip + rest_clip
        cmd_final = [
            "ffmpeg", "-y",
            "-i", cover_clip,
            "-i", rest_clip,
            "-filter_complex",
            "[0:v][1:v]concat=n=2:v=1:a=0[outv]",
            "-map", "[outv]",
            "-map", "1:a?",
        ] + encode_args + [
            "-c:a", "aac", "-b:a", "192k",
            output_path,
        ]
        subprocess.run(cmd_final, check=True, capture_output=True, text=True)

    finally:
        # Clean up temp files
        for f in [cover_clip, rest_clip, concat_list]:
            if os.path.exists(f):
                os.remove(f)
        if os.path.isdir(tmp_dir):
            os.rmdir(tmp_dir)


def collect_transcript_text(transcript_path):
    """Read transcript JSON and return the combined text of all segments."""
    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    segments = data.get("segments", [])
    return " ".join(seg["text"].strip() for seg in segments if seg.get("text", "").strip())


def main():
    parser = argparse.ArgumentParser(
        description="Replace the first frame of a video with a titled cover frame")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--title", default=None,
                        help="Cover title text. If omitted, prints transcript for AI to summarize.")
    parser.add_argument("--transcript", default=None,
                        help="Path to transcript JSON (for auto title generation)")
    parser.add_argument("--font-path", default=None, help="Custom font file path")
    parser.add_argument("--output", default=None,
                        help="Output video path (default: <video_name>_with_cover.mp4)")
    args = parser.parse_args()

    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    # If no title given, output transcript text for the AI agent to summarize
    if not args.title:
        if args.transcript and os.path.isfile(args.transcript):
            full_text = collect_transcript_text(args.transcript)
            print("TRANSCRIPT_FOR_TITLE_GENERATION:")
            print(full_text)
            print("\n(Please provide a --title based on the transcript above)")
        else:
            print("Error: Either --title or --transcript must be provided.", file=sys.stderr)
        sys.exit(0)

    title = sanitize_title(args.title)
    if not title:
        print("Error: Title is empty after sanitization.", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(video_path)
        output_path = base + "_with_cover" + ext

    # Get video info
    duration, width, height, fps = get_video_info(video_path)
    print(f"Video: {width}x{height}, {fps:.2f}fps, {duration:.1f}s")

    # Extract first frame
    frame_fd, frame_path = tempfile.mkstemp(suffix=".png", prefix="cover_frame_")
    os.close(frame_fd)

    cover_fd, cover_path = tempfile.mkstemp(suffix=".png", prefix="cover_titled_")
    os.close(cover_fd)

    try:
        print(f"Extracting first frame...")
        extract_first_frame(video_path, frame_path)

        # Find font
        font_path, font_name = _find_font(args.font_path)
        if not font_path:
            print("WARNING: No Chinese font found, title may not render correctly.",
                  file=sys.stderr)

        # Overlay title on the first frame
        print(f"Overlaying title: {title}")
        drawtext = build_drawtext_filters(title, font_path, width, height)
        cmd = [
            "ffmpeg", "-y",
            "-i", frame_path,
            "-vf", drawtext,
            cover_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Replace first frame in video
        print(f"Replacing first frame with cover...")
        replace_first_frame(video_path, cover_path, output_path, fps)

        print(f"Done: {output_path}")
    finally:
        for p in [frame_path, cover_path]:
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    main()
