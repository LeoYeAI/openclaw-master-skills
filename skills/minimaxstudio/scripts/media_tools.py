#!/usr/bin/env python3
"""
MiniMax Studio Media Tools CLI.

FFmpeg-based utilities for audio/video format conversion, concatenation,
extraction, and trimming.

Usage:
    python scripts/media_tools.py convert-video input.webm -o output.mp4
    python scripts/media_tools.py concat-video seg1.mp4 seg2.mp4 -o merged.mp4
    python scripts/media_tools.py extract-audio input.mp4 -o audio.mp3
    python scripts/media_tools.py trim-video input.mp4 --start 5 --end 15 -o clip.mp4
    python scripts/media_tools.py probe input.mp4
"""

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


# ---------------------------------------------------------------------------
# Probe / info
# ---------------------------------------------------------------------------

def probe_media(file_path):
    """Probe a media file and return format + stream info."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_format", "-show_streams",
        "-of", "json",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    return json.loads(result.stdout)


def get_duration(file_path):
    """Get duration in seconds."""
    info = probe_media(file_path)
    return float(info["format"].get("duration", 0))


def get_video_fps(file_path):
    """Get video frame rate."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "csv=p=0",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return 25
    try:
        num, den = result.stdout.strip().split("/")
        return round(int(num) / int(den))
    except (ValueError, ZeroDivisionError):
        return 25


def has_audio_stream(file_path):
    """Check if file contains an audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and "audio" in result.stdout


def has_video_stream(file_path):
    """Check if file contains a video stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and "video" in result.stdout


# ---------------------------------------------------------------------------
# Video format conversion
# ---------------------------------------------------------------------------

VIDEO_CODEC_MAP = {
    "mp4": "libx264",
    "mov": "libx264",
    "webm": "libvpx-vp9",
    "mkv": "libx264",
    "avi": "libx264",
    "ts": "libx264",
    "flv": "libx264",
}

AUDIO_CODEC_FOR_CONTAINER = {
    "mp4": "aac",
    "mov": "aac",
    "webm": "libopus",
    "mkv": "aac",
    "avi": "mp3",
    "ts": "aac",
    "flv": "aac",
}


def convert_video(input_path, output_path, crf=18, preset="medium",
                   resolution=None, fps=None):
    """Convert video to a different format with optional re-encoding.

    Args:
        input_path: Source video file.
        output_path: Destination file (format inferred from extension).
        crf: Quality (0-51, lower=better, default 18).
        preset: Encoding speed/quality tradeoff (default "medium").
        resolution: Optional target resolution, e.g. "1920x1080" or "1280x720".
        fps: Optional target frame rate.
    """
    ext = pathlib.Path(output_path).suffix.lstrip(".").lower()
    v_codec = VIDEO_CODEC_MAP.get(ext, "libx264")
    a_codec = AUDIO_CODEC_FOR_CONTAINER.get(ext, "aac")

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-i", str(input_path)]

    # Video filters
    vf_parts = []
    if resolution:
        w, h = resolution.split("x")
        vf_parts.append(f"scale={w}:{h}")
    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])

    # Video codec
    cmd.extend(["-c:v", v_codec])
    if v_codec in ("libx264", "libx265"):
        cmd.extend(["-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p"])
    elif v_codec == "libvpx-vp9":
        cmd.extend(["-crf", str(crf), "-b:v", "0"])

    if fps:
        cmd.extend(["-r", str(fps)])

    # Audio codec
    if has_audio_stream(input_path):
        cmd.extend(["-c:a", a_codec, "-b:a", "192k"])
    else:
        cmd.append("-an")

    cmd.append(str(output_path))

    print(f"Converting: {input_path} -> {output_path} ({v_codec}/{a_codec})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"Video conversion failed: {result.stderr}")
    print(f"  Done: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# Video concatenation (standalone)
# ---------------------------------------------------------------------------

def concat_videos(video_paths, output_path, crossfade=0.5):
    """Concatenate multiple videos with optional crossfade transitions.

    Args:
        video_paths: List of video file paths.
        output_path: Output file path.
        crossfade: Crossfade duration in seconds (0 to disable).
    """
    if not video_paths:
        raise ValueError("No video paths provided")

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if len(video_paths) == 1:
        shutil.copy2(video_paths[0], output_path)
        return str(output_path)

    fps = get_video_fps(video_paths[0])
    audio = all(has_audio_stream(vp) for vp in video_paths)

    if crossfade > 0:
        durations = [get_duration(vp) for vp in video_paths]

        inputs = []
        for vp in video_paths:
            inputs.extend(["-i", str(os.path.abspath(vp))])

        n = len(video_paths)
        vf_parts = []
        af_parts = []

        # Calculate offsets
        offsets = []
        cumulative = 0.0
        for i in range(n - 1):
            offset = cumulative + durations[i] - crossfade
            offsets.append(offset)
            cumulative = offset

        # Build xfade filter chain
        if n == 2:
            vf_parts.append(
                f"[0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={offsets[0]}[vout]"
            )
            if audio:
                af_parts.append(
                    f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[aout]"
                )
        else:
            vf_parts.append(
                f"[0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={offsets[0]}[xv1]"
            )
            if audio:
                af_parts.append(
                    f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[xa1]"
                )
            for i in range(2, n):
                prev_v = f"[xv{i-1}]"
                out_v = "[vout]" if i == n - 1 else f"[xv{i}]"
                vf_parts.append(
                    f"{prev_v}[{i}:v]xfade=transition=fade:duration={crossfade}:offset={offsets[i-1]}{out_v}"
                )
                if audio:
                    prev_a = f"[xa{i-1}]"
                    out_a = "[aout]" if i == n - 1 else f"[xa{i}]"
                    af_parts.append(
                        f"{prev_a}[{i}:a]acrossfade=d={crossfade}:c1=tri:c2=tri{out_a}"
                    )

        filter_complex = ";".join(vf_parts + af_parts)

        cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex,
               "-map", "[vout]"]
        if audio:
            cmd.extend(["-map", "[aout]"])
        cmd.extend([
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(fps),
        ])
        if audio:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        cmd.append(str(output_path))

        print(f"Concatenating {n} videos with {crossfade}s crossfade...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            print(f"  Crossfade failed, falling back to re-encode: {result.stderr[:200]}")
            _concat_reencode(video_paths, output_path, fps)
    else:
        _concat_reencode(video_paths, output_path, fps)

    print(f"  Done: {output_path}")
    return str(output_path)


def _concat_reencode(video_paths, output_path, fps=25):
    """Fallback: concat with unified re-encoding, no crossfade."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for vp in video_paths:
            f.write(f"file '{os.path.abspath(vp)}'\n")
        concat_list = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"Concat failed: {result.stderr}")
    finally:
        os.unlink(concat_list)


# ---------------------------------------------------------------------------
# Audio extraction from video
# ---------------------------------------------------------------------------

AUDIO_EXTRACT_CODEC = {
    "mp3": "libmp3lame",
    "wav": "pcm_s16le",
    "flac": "flac",
    "aac": "aac",
    "m4a": "aac",
    "ogg": "libvorbis",
    "opus": "libopus",
}


def extract_audio(input_path, output_path, bitrate="192k"):
    """Extract audio track from a video file.

    Args:
        input_path: Source video file.
        output_path: Destination audio file (format from extension).
        bitrate: Audio bitrate (default "192k").
    """
    if not has_audio_stream(input_path):
        raise RuntimeError(f"No audio stream found in {input_path}")

    ext = pathlib.Path(output_path).suffix.lstrip(".").lower()
    codec = AUDIO_EXTRACT_CODEC.get(ext, "libmp3lame")

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-c:a", codec,
        "-b:a", bitrate,
        str(output_path),
    ]

    print(f"Extracting audio: {input_path} -> {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Audio extraction failed: {result.stderr}")
    print(f"  Done: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# Video trimming
# ---------------------------------------------------------------------------

def trim_video(input_path, output_path, start=None, end=None, duration=None):
    """Trim a video by time range.

    Args:
        input_path: Source video file.
        output_path: Destination file.
        start: Start time in seconds (default: 0).
        end: End time in seconds (default: to end).
        duration: Duration in seconds (alternative to end).
    """
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y"]

    if start is not None:
        cmd.extend(["-ss", str(start)])

    cmd.extend(["-i", str(input_path)])

    if duration is not None:
        cmd.extend(["-t", str(duration)])
    elif end is not None:
        actual_start = start or 0
        cmd.extend(["-t", str(end - actual_start)])

    cmd.extend([
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p",
    ])
    if has_audio_stream(input_path):
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    cmd.append(str(output_path))

    start_str = f"{start}s" if start else "0s"
    end_str = f"{end}s" if end else ("+" + f"{duration}s" if duration else "end")
    print(f"Trimming: {input_path} [{start_str} - {end_str}] -> {output_path}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Video trim failed: {result.stderr}")
    print(f"  Done: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# Audio format conversion (complements tts/audio_processing.py)
# ---------------------------------------------------------------------------

AUDIO_CODEC_MAP = {
    "mp3": "libmp3lame",
    "wav": "pcm_s16le",
    "flac": "flac",
    "ogg": "libvorbis",
    "aac": "aac",
    "m4a": "aac",
    "opus": "libopus",
    "wma": "wmav2",
}


def convert_audio(input_path, output_path, bitrate="192k",
                  sample_rate=None, channels=None):
    """Convert audio to a different format.

    Args:
        input_path: Source audio file.
        output_path: Destination file (format from extension).
        bitrate: Audio bitrate (default "192k").
        sample_rate: Optional target sample rate (e.g. 44100).
        channels: Optional channel count (1=mono, 2=stereo).
    """
    ext = pathlib.Path(output_path).suffix.lstrip(".").lower()
    codec = AUDIO_CODEC_MAP.get(ext, "libmp3lame")

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:a", codec,
        "-b:a", bitrate,
    ]
    if sample_rate:
        cmd.extend(["-ar", str(sample_rate)])
    if channels:
        cmd.extend(["-ac", str(channels)])
    cmd.append(str(output_path))

    print(f"Converting audio: {input_path} -> {output_path} ({codec})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Audio conversion failed: {result.stderr}")
    print(f"  Done: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# Audio concatenation
# ---------------------------------------------------------------------------

def concat_audio(audio_paths, output_path, crossfade=0):
    """Concatenate multiple audio files with optional crossfade.

    Args:
        audio_paths: List of audio file paths.
        output_path: Output file path.
        crossfade: Crossfade duration in seconds (0 for hard cut).
    """
    if not audio_paths:
        raise ValueError("No audio paths provided")

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if len(audio_paths) == 1:
        shutil.copy2(audio_paths[0], output_path)
        return str(output_path)

    ext = pathlib.Path(output_path).suffix.lstrip(".").lower()
    codec = AUDIO_CODEC_MAP.get(ext, "libmp3lame")

    if crossfade > 0:
        inputs = []
        for ap in audio_paths:
            inputs.extend(["-i", str(os.path.abspath(ap))])

        n = len(audio_paths)
        af_parts = []

        if n == 2:
            af_parts.append(
                f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[aout]"
            )
        else:
            af_parts.append(
                f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[xa1]"
            )
            for i in range(2, n):
                prev = f"[xa{i-1}]"
                out = "[aout]" if i == n - 1 else f"[xa{i}]"
                af_parts.append(
                    f"{prev}[{i}:a]acrossfade=d={crossfade}:c1=tri:c2=tri{out}"
                )

        filter_complex = ";".join(af_parts)
        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-c:a", codec, "-b:a", "192k",
            str(output_path),
        ]
        print(f"Concatenating {n} audio files with {crossfade}s crossfade...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"  Crossfade failed, falling back: {result.stderr[:200]}")
            _concat_audio_simple(audio_paths, output_path, codec)
    else:
        _concat_audio_simple(audio_paths, output_path, codec)

    print(f"  Done: {output_path}")
    return str(output_path)


def _concat_audio_simple(audio_paths, output_path, codec="libmp3lame"):
    """Fallback: concat audio with re-encoding, no crossfade."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for ap in audio_paths:
            f.write(f"file '{os.path.abspath(ap)}'\n")
        concat_list = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list,
            "-c:a", codec, "-b:a", "192k",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Audio concat failed: {result.stderr}")
    finally:
        os.unlink(concat_list)


# ---------------------------------------------------------------------------
# Add audio to video (overlay / replace)
# ---------------------------------------------------------------------------

def add_audio_to_video(video_path, audio_path, output_path, volume=1.0,
                       fade_in=0, fade_out=0, replace=False):
    """Add or overlay audio onto a video.

    Args:
        video_path: Source video file.
        audio_path: Audio file to add.
        output_path: Output video file.
        volume: Audio volume (0.0-1.0, default 1.0).
        fade_in: Fade-in duration in seconds.
        fade_out: Fade-out duration in seconds.
        replace: If True, replace original audio; if False, mix with original.
    """
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    duration = get_duration(video_path)
    video_audio = has_audio_stream(video_path)

    # Build audio filter for the new audio
    af = f"[1:a]volume={volume}"
    if fade_in > 0:
        af += f",afade=t=in:d={fade_in}"
    if fade_out > 0:
        fade_out_start = max(0, duration - fade_out)
        af += f",afade=t=out:st={fade_out_start}:d={fade_out}"

    if video_audio and not replace:
        # Mix original + new audio
        af += "[newaudio];[0:a][newaudio]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        map_audio = ["-map", "[aout]"]
    else:
        # Replace or no original audio
        af += "[aout]"
        map_audio = ["-map", "[aout]"]

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex", af,
        "-map", "0:v",
        *map_audio,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]

    mode = "replacing" if replace or not video_audio else "mixing with"
    print(f"Adding audio ({mode} original): {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Add audio failed: {result.stderr}")
    print(f"  Done: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_convert_video(args):
    convert_video(args.input, args.output, crf=args.crf, preset=args.preset,
                  resolution=args.resolution, fps=args.fps)

def cmd_convert_audio(args):
    convert_audio(args.input, args.output, bitrate=args.bitrate,
                  sample_rate=args.sample_rate, channels=args.channels)

def cmd_concat_video(args):
    concat_videos(args.inputs, args.output, crossfade=args.crossfade)

def cmd_concat_audio(args):
    concat_audio(args.inputs, args.output, crossfade=args.crossfade)

def cmd_extract_audio(args):
    extract_audio(args.input, args.output, bitrate=args.bitrate)

def cmd_trim_video(args):
    trim_video(args.input, args.output, start=args.start, end=args.end,
               duration=args.duration)

def cmd_add_audio(args):
    add_audio_to_video(args.video, args.audio, args.output, volume=args.volume,
                       fade_in=args.fade_in, fade_out=args.fade_out,
                       replace=args.replace)

def cmd_probe(args):
    info = probe_media(args.input)
    fmt = info.get("format", {})
    print(f"File:     {args.input}")
    print(f"Format:   {fmt.get('format_long_name', 'unknown')}")
    print(f"Duration: {float(fmt.get('duration', 0)):.2f}s")
    print(f"Size:     {int(fmt.get('size', 0)) / 1024 / 1024:.2f} MB")
    print(f"Bitrate:  {int(fmt.get('bit_rate', 0)) / 1000:.0f} kbps")
    for s in info.get("streams", []):
        stype = s.get("codec_type", "unknown")
        codec = s.get("codec_name", "unknown")
        if stype == "video":
            w, h = s.get("width", "?"), s.get("height", "?")
            r = s.get("r_frame_rate", "?")
            print(f"Video:    {codec} {w}x{h} @ {r} fps")
        elif stype == "audio":
            sr = s.get("sample_rate", "?")
            ch = s.get("channels", "?")
            print(f"Audio:    {codec} {sr}Hz {ch}ch")


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Studio Media Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- convert-video --
    p = sub.add_parser("convert-video", help="Convert video format")
    p.add_argument("input", help="Input video file")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--crf", type=int, default=18, help="Quality (0-51, default 18)")
    p.add_argument("--preset", default="medium", help="Encoding preset")
    p.add_argument("--resolution", help="Target resolution, e.g. 1920x1080")
    p.add_argument("--fps", type=int, help="Target frame rate")
    p.set_defaults(func=cmd_convert_video)

    # -- convert-audio --
    p = sub.add_parser("convert-audio", help="Convert audio format")
    p.add_argument("input", help="Input audio file")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--bitrate", default="192k", help="Bitrate (default 192k)")
    p.add_argument("--sample-rate", dest="sample_rate", type=int, help="Sample rate")
    p.add_argument("--channels", type=int, help="Channels (1=mono, 2=stereo)")
    p.set_defaults(func=cmd_convert_audio)

    # -- concat-video --
    p = sub.add_parser("concat-video", help="Concatenate videos")
    p.add_argument("inputs", nargs="+", help="Input video files")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--crossfade", type=float, default=0.5,
                   help="Crossfade seconds (default 0.5, 0 to disable)")
    p.set_defaults(func=cmd_concat_video)

    # -- concat-audio --
    p = sub.add_parser("concat-audio", help="Concatenate audio files")
    p.add_argument("inputs", nargs="+", help="Input audio files")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--crossfade", type=float, default=0,
                   help="Crossfade seconds (default 0)")
    p.set_defaults(func=cmd_concat_audio)

    # -- extract-audio --
    p = sub.add_parser("extract-audio", help="Extract audio from video")
    p.add_argument("input", help="Input video file")
    p.add_argument("-o", "--output", required=True, help="Output audio file")
    p.add_argument("--bitrate", default="192k", help="Bitrate (default 192k)")
    p.set_defaults(func=cmd_extract_audio)

    # -- trim-video --
    p = sub.add_parser("trim-video", help="Trim video by time range")
    p.add_argument("input", help="Input video file")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--start", type=float, help="Start time in seconds")
    p.add_argument("--end", type=float, help="End time in seconds")
    p.add_argument("--duration", type=float, help="Duration in seconds (alt to --end)")
    p.set_defaults(func=cmd_trim_video)

    # -- add-audio --
    p = sub.add_parser("add-audio", help="Add/overlay audio on video")
    p.add_argument("--video", required=True, help="Input video file")
    p.add_argument("--audio", required=True, help="Audio file to add")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.add_argument("--volume", type=float, default=1.0, help="Audio volume (default 1.0)")
    p.add_argument("--fade-in", dest="fade_in", type=float, default=0)
    p.add_argument("--fade-out", dest="fade_out", type=float, default=0)
    p.add_argument("--replace", action="store_true",
                   help="Replace original audio instead of mixing")
    p.set_defaults(func=cmd_add_audio)

    # -- probe --
    p = sub.add_parser("probe", help="Show media file info")
    p.add_argument("input", help="Media file to probe")
    p.set_defaults(func=cmd_probe)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
