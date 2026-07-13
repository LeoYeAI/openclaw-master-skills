#!/usr/bin/env python3
"""
Burn subtitles into video clips based on transcript data.
Automatically detects language and selects appropriate Chinese/English font.

Usage: python3 burn_subtitles.py <clips_dir> <transcript_json_path> [--font-path <path>]
Output: <clips_dir>_subtitled/clip_001.mp4, clip_002.mp4, ...
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    find_chinese_font as _find_font, detect_gpu, get_ffmpeg_encode_args,
    escape_ffmpeg_path,
)


def detect_language(text):
    """Detect if text is primarily Chinese or English."""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "zh"
    return "zh" if chinese_chars / total_alpha > 0.3 else "en"


def escape_ass_text(text):
    """Escape special characters for ASS subtitle format."""
    # ASS uses { } for override tags, backslash for escapes
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    return text


def wrap_subtitle_text(text, max_chars_per_line, language):
    """Break long subtitle text into multiple lines using ASS line break \\N."""
    if language == "zh":
        # For Chinese, count all characters (including ASCII)
        if len(text) <= max_chars_per_line:
            return text
        # Try to split roughly in the middle
        mid = len(text) // 2
        # Look for natural break points near the middle (punctuation, spaces)
        best_break = mid
        for offset in range(min(5, mid)):
            for pos in [mid + offset, mid - offset]:
                if 0 < pos < len(text) and text[pos] in ' ,，。、；：！？·':
                    best_break = pos + 1
                    break
            else:
                continue
            break
        line1 = text[:best_break].rstrip()
        line2 = text[best_break:].lstrip()
        return line1 + "\\N" + line2
    else:
        # For English, split by words
        words = text.split()
        if len(text) <= max_chars_per_line:
            return text
        lines = []
        current_line = ""
        for word in words:
            if current_line and len(current_line) + 1 + len(word) > max_chars_per_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = current_line + " " + word if current_line else word
        if current_line:
            lines.append(current_line)
        return "\\N".join(lines)


def create_ass_subtitle(text, duration, font_name, font_size, language, output_path,
                        video_width=1080, video_height=1920):
    """Create an ASS subtitle file for a single clip, with proper positioning for portrait video."""
    bold = 1

    def fmt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    start_time = fmt_time(0)
    end_time = fmt_time(duration)

    # Calculate max characters per line based on video width
    margin_lr = 60
    usable_width = video_width - 2 * margin_lr
    # Chinese chars are roughly square (width ≈ font_size), ASCII chars are ~0.5x
    if language == "zh":
        max_chars = int(usable_width / font_size)
    else:
        max_chars = int(usable_width / (font_size * 0.55))

    wrapped_text = wrap_subtitle_text(text, max_chars, language)
    escaped_text = escape_ass_text(wrapped_text)

    # For portrait video (e.g., 1080x1920), position subtitle at ~72% from top
    # This is about 28% from bottom, above the Xiaohongshu interaction buttons
    margin_v = int(video_height * 0.28)

    ass_content = f"""[Script Info]
Title: Subtitle
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,{bold},0,0,0,100,100,0,0,1,3,1,2,{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{escaped_text}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_content)


def get_video_info(video_path):
    """Get video duration and resolution."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    try:
        result = subprocess.check_output(cmd, text=True)
        info = json.loads(result)
        duration = float(info.get("format", {}).get("duration", 0))
        streams = info.get("streams", [{}])
        width = streams[0].get("width", 1920) if streams else 1920
        height = streams[0].get("height", 1080) if streams else 1080
        return duration, width, height
    except (subprocess.CalledProcessError, ValueError, json.JSONDecodeError):
        return 5.0, 1920, 1080


def main():
    parser = argparse.ArgumentParser(description="Burn subtitles into video clips")
    parser.add_argument("clips_dir", help="Path to the clips directory")
    parser.add_argument("transcript_path", help="Path to the transcript JSON file")
    parser.add_argument("--font-path", default=None,
                        help="Custom font file path for Chinese subtitles")
    parser.add_argument("--font-size", type=int, default=48,
                        help="Subtitle font size (default: 48, scaled to 1080p)")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: <clips_dir>_subtitled)")
    args = parser.parse_args()

    clips_dir = os.path.abspath(args.clips_dir)
    if not os.path.isdir(clips_dir):
        print(f"Error: Clips directory not found: {clips_dir}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.transcript_path):
        print(f"Error: Transcript not found: {args.transcript_path}", file=sys.stderr)
        sys.exit(1)

    with open(args.transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    segments = transcript.get("segments", [])
    if not segments:
        print("Error: No segments found in transcript", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = clips_dir + "_subtitled"
    os.makedirs(output_dir, exist_ok=True)

    # Find Chinese font (using shared utils)
    font_path, font_name = _find_font(args.font_path)

    # Detect GPU for encoding
    gpu_info = detect_gpu()
    encode_args = get_ffmpeg_encode_args(gpu_info)

    print(f"Subtitle font: {font_name} ({font_path or 'name only'})")
    print(f"Video encoder: {encode_args[1]}")
    print(f"Output directory: {output_dir}")
    print(f"Processing {len(segments)} clips...")

    success_count = 0
    for seg in segments:
        seg_id = seg["id"]
        text = seg["text"].strip()
        if not text:
            continue

        clip_filename = f"clip_{seg_id:03d}.mp4"
        clip_path = os.path.join(clips_dir, clip_filename)
        output_path = os.path.join(output_dir, clip_filename)

        if not os.path.isfile(clip_path):
            print(f"  SKIP clip_{seg_id:03d}.mp4 (not found)")
            continue

        # Get clip duration and resolution
        duration, width, height = get_video_info(clip_path)

        # Scale font size based on the shorter dimension (width for portrait) relative to 1080p
        ref_dimension = min(width, height)
        scaled_font_size = max(16, int(args.font_size * ref_dimension / 1080))

        # Detect language for this segment
        lang = detect_language(text)

        # For English text, we can use any font; for Chinese, we need the CJK font
        if lang == "en":
            seg_font_name = "Arial"
        else:
            seg_font_name = font_name

        # Create ASS subtitle file
        ass_fd, ass_path = tempfile.mkstemp(suffix=".ass", prefix="sub_")
        os.close(ass_fd)
        try:
            create_ass_subtitle(text, duration, seg_font_name, scaled_font_size, lang, ass_path,
                                video_width=width, video_height=height)

            # Build ffmpeg command using ass filter with fontsdir
            cmd = [
                "ffmpeg", "-y",
                "-i", clip_path,
            ]

            escaped_ass = escape_ffmpeg_path(ass_path)
            if font_path:
                font_dir = os.path.dirname(font_path)
                escaped_fontdir = escape_ffmpeg_path(font_dir)
                cmd += ["-vf", f"ass={escaped_ass}:fontsdir={escaped_fontdir}"]
            else:
                cmd += ["-vf", f"ass={escaped_ass}"]

            cmd += encode_args + ["-c:a", "copy", output_path]

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  clip_{seg_id:03d}.mp4  [{lang}]  {text}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  ERROR clip_{seg_id:03d}.mp4: {e.stderr[:300] if e.stderr else 'unknown error'}", file=sys.stderr)
        finally:
            if os.path.exists(ass_path):
                os.remove(ass_path)

    print(f"\nSubtitle burning complete. {success_count}/{len(segments)} clips processed.")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
