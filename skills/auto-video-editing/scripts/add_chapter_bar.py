#!/usr/bin/env python3
"""
Burn a visual chapter timeline bar into a video.

Two styles:
  --style color   (default) Colored segments per chapter
  --style mono    Monochrome white/gray bar

Chapters can be provided as:
  - A JSON file (dedicated chapters JSON)
  - Auto-generated from transcript segments

Usage:
  python3 add_chapter_bar.py <video_path> --transcript <transcript.json>
  python3 add_chapter_bar.py <video_path> --chapters <chapters.json> --style mono

Output: <video_name>_chapters.mp4
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    detect_gpu, get_ffmpeg_encode_args, escape_ffmpeg_path,
    find_chinese_font, check_ffmpeg,
)

# Material Design palette
CHAPTER_COLORS = [
    "0x4CAF50",  # green
    "0x2196F3",  # blue
    "0xFF9800",  # orange
    "0xE91E63",  # pink
    "0x9C27B0",  # purple
    "0x00BCD4",  # cyan
    "0xFF5722",  # deep orange
    "0x3F51B5",  # indigo
    "0x8BC34A",  # light green
    "0xFFC107",  # amber
]


def get_video_info(video_path):
    """Get video duration, width, height."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path,
    ]
    result = subprocess.check_output(cmd, text=True)
    info = json.loads(result)
    duration = float(info.get("format", {}).get("duration", 0))
    streams = info.get("streams", [{}])
    s = streams[0] if streams else {}
    w = s.get("width", 1920)
    h = s.get("height", 1080)
    return duration, w, h


def is_portrait(width, height):
    return height > width


def load_chapters(chapters_path):
    """Load chapters from JSON.

    Format: {"chapters": [{"title": "...", "start": 0.0, "end": 15.0}, ...]}
    """
    with open(chapters_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("chapters", [])


def chapters_from_transcript(transcript_path, max_chapters=8):
    """Auto-generate chapters by grouping transcript segments."""
    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    if not segments:
        return []

    total_start = segments[0]["start"]
    total_end = segments[-1]["end"]
    total_duration = total_end - total_start

    if total_duration <= 0:
        return []

    n_chapters = max(2, min(max_chapters, int(total_duration / 20)))
    target_dur = total_duration / n_chapters

    chapters = []
    chap_start = segments[0]["start"]
    chap_texts = []
    chap_idx = 0

    for seg in segments:
        chap_texts.append(seg["text"].strip())
        elapsed = seg["end"] - chap_start

        if elapsed >= target_dur and chap_idx < n_chapters - 1:
            title = _pick_chapter_title(chap_texts)
            chapters.append({
                "title": title,
                "start": round(chap_start, 2),
                "end": round(seg["end"], 2),
            })
            chap_start = seg["end"]
            chap_texts = []
            chap_idx += 1

    if chap_texts or chap_start < total_end:
        title = _pick_chapter_title(chap_texts) if chap_texts else f"Part {chap_idx + 1}"
        chapters.append({
            "title": title,
            "start": round(chap_start, 2),
            "end": round(total_end, 2),
        })

    return chapters


def _pick_chapter_title(texts, max_len=12):
    if not texts:
        return ""
    best = max(texts, key=len)
    if len(best) > max_len:
        for i in range(max_len, max(max_len - 4, 0), -1):
            if best[i] in " ,，。、；：":
                return best[:i]
        return best[:max_len]
    return best


def _escape_drawtext(text):
    """Escape text for ffmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\u2019")
    text = text.replace(":", "\\:")
    text = text.replace(";", "\\;")
    text = text.replace("%", "%%%%")
    return text


def _has_drawtext():
    """Check if ffmpeg has drawtext filter."""
    try:
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-filters"],
            capture_output=True, text=True, timeout=5
        )
        return "drawtext" in r.stdout
    except Exception:
        return False


def build_chapter_bar_filter(chapters, total_duration, width, height,
                              font_path=None, style="color", has_drawtext=True):
    """Build ffmpeg -vf filter string for chapter timeline bar.

    style: "color" (colored segments) or "mono" (monochrome)
    """
    portrait = is_portrait(width, height)
    short_side = min(width, height)

    # Bar dimensions — ~1.5% of short side (visible but not intrusive)
    bar_h = max(6, int(short_side * 0.015))

    # Position
    if portrait:
        bar_y = int(height * 0.03)  # near top
    else:
        bar_y = height - bar_h  # at bottom

    # Label position
    label_fs = max(14, int(short_side * 0.02))
    if portrait:
        label_y = bar_y + bar_h + 6
    else:
        label_y = bar_y - label_fs - 8

    dur = f"{total_duration:.4f}"
    filters = []

    # --- Background ---
    filters.append(
        f"drawbox=x=0:y={bar_y}:w=iw:h={bar_h}:color=black@0.5:t=fill"
    )

    if style == "color":
        # Colored chapter segments
        for i, chap in enumerate(chapters):
            color = CHAPTER_COLORS[i % len(CHAPTER_COLORS)]
            x_frac = chap["start"] / total_duration
            w_frac = (chap["end"] - chap["start"]) / total_duration
            filters.append(
                f"drawbox=x=iw*{x_frac:.6f}:y={bar_y}"
                f":w=iw*{w_frac:.6f}:h={bar_h}"
                f":color={color}@0.85:t=fill"
            )
    else:
        # Mono: alternating light/dark gray
        for i, chap in enumerate(chapters):
            gray = "0xBBBBBB" if i % 2 == 0 else "0x888888"
            x_frac = chap["start"] / total_duration
            w_frac = (chap["end"] - chap["start"]) / total_duration
            filters.append(
                f"drawbox=x=iw*{x_frac:.6f}:y={bar_y}"
                f":w=iw*{w_frac:.6f}:h={bar_h}"
                f":color={gray}@0.8:t=fill"
            )

    # Separator lines
    for i in range(1, len(chapters)):
        x_frac = chapters[i]["start"] / total_duration
        filters.append(
            f"drawbox=x=iw*{x_frac:.6f}-1:y={bar_y}:w=2:h={bar_h}"
            f":color=white@0.9:t=fill"
        )

    # Animated progress sweep
    filters.append(
        f"drawbox=x=0:y={bar_y}:w='iw*t/{dur}':h={bar_h}"
        f":color=white@0.35:t=fill"
    )

    # Playhead cursor
    cw = max(2, bar_h // 3)
    filters.append(
        f"drawbox=x='iw*t/{dur}-{cw//2}':y={bar_y - 1}"
        f":w={cw}:h={bar_h + 2}"
        f":color=white@0.95:t=fill"
    )

    # Chapter labels (only if drawtext is available)
    if has_drawtext:
        font_arg = ""
        if font_path:
            escaped_font = escape_ffmpeg_path(font_path)
            font_arg = f":fontfile='{escaped_font}'"

        for i, chap in enumerate(chapters):
            title = chap.get("title", "").strip()
            if not title:
                continue

            escaped = _escape_drawtext(title)
            cs = chap["start"]
            ce = min(cs + 3.0, chap["end"])

            # x position: pixel offset for the center of this chapter's segment
            mid_px = int(width * (chap["start"] + chap["end"]) / 2.0 / total_duration)

            # Alpha fade: 0.4s in, hold, 0.6s out
            fade_in = 0.4
            fade_out = 0.6
            alpha_expr = (
                f"if(lt(t\\,{cs + fade_in:.2f})\\,"
                f"(t-{cs:.2f})/{fade_in:.1f}\\,"
                f"if(lt(t\\,{ce - fade_out:.2f})\\,"
                f"1\\,"
                f"({ce:.2f}-t)/{fade_out:.1f}))"
            )

            filters.append(
                f"drawtext=text='{escaped}'"
                f":fontsize={label_fs}"
                f":fontcolor=white"
                f":alpha='{alpha_expr}'"
                f":borderw=2:bordercolor=black@0.6"
                f":x={mid_px}-text_w/2:y={label_y}"
                f":enable='between(t\\,{cs:.2f}\\,{ce:.2f})'"
                f"{font_arg}"
            )

    return ",".join(filters)


def main():
    parser = argparse.ArgumentParser(
        description="Add a visual chapter timeline bar to a video")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--chapters", default=None,
                        help="Path to chapters JSON file")
    parser.add_argument("--transcript", default=None,
                        help="Path to transcript JSON (auto-generate chapters)")
    parser.add_argument("--max-chapters", type=int, default=8,
                        help="Max auto-generated chapters (default: 8)")
    parser.add_argument("--style", default="color", choices=["color", "mono"],
                        help="Bar style: color (default) or mono")
    parser.add_argument("--font-path", default=None,
                        help="Custom font file path")
    parser.add_argument("--output", default=None,
                        help="Output video path (default: <name>_chapters.mp4)")
    args = parser.parse_args()

    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"Error: Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    # Load or generate chapters
    if args.chapters:
        chapters = load_chapters(args.chapters)
    elif args.transcript:
        chapters = chapters_from_transcript(args.transcript, args.max_chapters)
    else:
        print("Error: --chapters or --transcript required.", file=sys.stderr)
        sys.exit(1)

    if not chapters:
        print("Error: No chapters found.", file=sys.stderr)
        sys.exit(1)

    duration, width, height = get_video_info(video_path)
    orient = "portrait" if is_portrait(width, height) else "landscape"
    print(f"Video: {width}x{height}, {duration:.1f}s, {orient}")
    print(f"Style: {args.style}")
    print(f"Chapters: {len(chapters)}")
    for i, ch in enumerate(chapters):
        print(f"  [{i+1}] {ch['start']:.1f}s - {ch['end']:.1f}s  {ch.get('title', '')}")

    # Check drawtext availability
    has_dt = _has_drawtext()
    if not has_dt:
        print("[warn] drawtext filter not available, chapter labels will be skipped")

    # Font
    font_path = None
    if has_dt:
        font_path, font_name = find_chinese_font(args.font_path)

    # Build filter
    vf = build_chapter_bar_filter(
        chapters, duration, width, height,
        font_path=font_path, style=args.style, has_drawtext=has_dt
    )

    # Output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(video_path)
        output_path = base + "_chapters" + ext

    encode_args = get_ffmpeg_encode_args()

    print(f"Rendering...")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
    ] + encode_args + [
        "-c:a", "copy",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Done: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)

    # YouTube timestamps
    print("\nYouTube chapter timestamps:")
    for ch in chapters:
        m = int(ch["start"] // 60)
        s = int(ch["start"] % 60)
        print(f"  {m}:{s:02d} {ch.get('title', '')}")


if __name__ == "__main__":
    main()
