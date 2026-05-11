#!/usr/bin/env python3
"""
MiniMax Long Video Generation CLI.

Generates multi-segment videos by chaining scenes together using the last frame
of each segment as the first frame of the next. Optionally adds AI-generated
background music.

Usage (from project root):
    python scripts/video/generate_long_video.py \\
        --scenes "A sunrise over mountains" "Birds flying across the sky" "A calm lake at dawn" \\
        --output output/long_video.mp4

    python scripts/video/generate_long_video.py \\
        --scenes "A robot waking up" "The robot walks outside" \\
        --music-prompt "cinematic orchestral ambient" \\
        --bgm-volume 0.2 --fade-in 2 --fade-out 3 \\
        --output output/robot_story.mp4
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_video import (
    create_task,
    poll_task,
    download_video,
    resolve_image,
    build_payload,
    API_BASE,
    QUERY_URL,
    FILE_RETRIEVE_URL,
    REQUEST_TIMEOUT,
    POLL_INTERVAL,
    MAX_WAIT_TIME,
)

MUSIC_API_URL = f"{API_BASE}/music_generation"


def get_frame_count(video_path):
    """Get total number of frames in a video using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-count_frames",
        "-show_entries", "stream=nb_read_frames",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except (ValueError, AttributeError):
        return None


def extract_last_frame(video_path, output_image_path):
    """Extract the exact last frame from a video using ffmpeg.

    Uses frame count to select the precise last frame, with a fallback
    to reverse-seeking if frame counting fails.
    """
    frame_count = get_frame_count(video_path)

    if frame_count and frame_count > 0:
        last_frame_idx = frame_count - 1
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"select=eq(n\\,{last_frame_idx})",
            "-frames:v", "1",
            "-q:v", "2",
            str(output_image_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-sseof", "-0.04",
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(output_image_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg extract last frame failed: {result.stderr}")
    if not pathlib.Path(output_image_path).exists():
        raise RuntimeError(f"Failed to extract last frame to {output_image_path}")
    print(f"  Extracted last frame: {output_image_path}")
    return str(output_image_path)


def get_video_fps(video_path):
    """Get the frame rate of a video using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return 25
    try:
        num, den = result.stdout.strip().split("/")
        return round(int(num) / int(den))
    except (ValueError, ZeroDivisionError):
        return 25


def _video_has_audio(video_path):
    """Check if a video file contains an audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and "audio" in result.stdout


def concatenate_videos(video_paths, output_path, crossfade=0.5):
    """Concatenate multiple video files with crossfade transitions.

    Uses ffmpeg xfade filter for smooth transitions between segments,
    with unified re-encoding to ensure consistent output quality.
    Handles videos with or without audio tracks.

    Args:
        video_paths: List of video file paths to concatenate.
        output_path: Output file path.
        crossfade: Crossfade duration in seconds (0 to disable).
    """
    if not video_paths:
        raise ValueError("No video paths provided for concatenation")

    if len(video_paths) == 1:
        import shutil
        shutil.copy2(video_paths[0], output_path)
        return str(output_path)

    fps = get_video_fps(video_paths[0])
    has_audio = all(_video_has_audio(vp) for vp in video_paths)

    if crossfade > 0:
        durations = [get_video_duration(vp) for vp in video_paths]

        inputs = []
        for vp in video_paths:
            inputs.extend(["-i", str(os.path.abspath(vp))])

        n = len(video_paths)
        video_filter_parts = []
        audio_filter_parts = []

        offsets = []
        cumulative = 0.0
        for i in range(n - 1):
            offset = cumulative + durations[i] - crossfade
            offsets.append(offset)
            cumulative = offset

        if n == 2:
            video_filter_parts.append(
                f"[0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={offsets[0]}[vout]"
            )
            if has_audio:
                audio_filter_parts.append(
                    f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[aout]"
                )
        else:
            video_filter_parts.append(
                f"[0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={offsets[0]}[xv1]"
            )
            if has_audio:
                audio_filter_parts.append(
                    f"[0:a][1:a]acrossfade=d={crossfade}:c1=tri:c2=tri[xa1]"
                )
            for i in range(2, n):
                prev_v = f"[xv{i-1}]"
                if i == n - 1:
                    out_v = "[vout]"
                    out_a = "[aout]"
                else:
                    out_v = f"[xv{i}]"
                    out_a = f"[xa{i}]"
                video_filter_parts.append(
                    f"{prev_v}[{i}:v]xfade=transition=fade:duration={crossfade}:offset={offsets[i-1]}{out_v}"
                )
                if has_audio:
                    prev_a = f"[xa{i-1}]"
                    audio_filter_parts.append(
                        f"{prev_a}[{i}:a]acrossfade=d={crossfade}:c1=tri:c2=tri{out_a}"
                    )

        filter_complex = ";".join(video_filter_parts + audio_filter_parts)

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
        ]
        if has_audio:
            cmd.extend(["-map", "[aout]"])
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
        ])
        if has_audio:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            print(f"  Crossfade concat failed, falling back to re-encode concat: {result.stderr[:200]}")
            _concatenate_reencode(video_paths, output_path, fps)
    else:
        _concatenate_reencode(video_paths, output_path, fps)

    print(f"Concatenated {len(video_paths)} segments -> {output_path}")
    return str(output_path)


def _concatenate_reencode(video_paths, output_path, fps=25):
    """Fallback: concatenate with unified re-encoding (no crossfade)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for vp in video_paths:
            f.write(f"file '{os.path.abspath(vp)}'\n")
        concat_list = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {result.stderr}")
    finally:
        os.unlink(concat_list)


def generate_music_instrumental(prompt, api_key, output_path):
    """Generate instrumental background music via the MiniMax Music API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "music-2.5+",
        "is_instrumental": True,
        "prompt": prompt or "cinematic background music, orchestral, ambient",
        "output_format": "url",
    }

    print(f"Generating instrumental music: {prompt}")
    resp = requests.post(MUSIC_API_URL, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    if "base_resp" in data and data["base_resp"].get("status_code", 0) != 0:
        raise RuntimeError(f"Music API error: {data['base_resp']}")

    audio_data = data.get("data", data)
    audio_url = audio_data.get("audio_url", audio_data.get("audio", ""))
    if not audio_url:
        audio_file = audio_data.get("audio_file", {})
        audio_url = audio_file.get("download_url", "")
    if not audio_url:
        raise RuntimeError(f"No audio URL in music response: {data}")

    download_music(audio_url, output_path)
    return str(output_path)


def download_music(url, output_path):
    """Download music from a URL."""
    print(f"Downloading music to {output_path}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    print(f"  Music saved: {output_path} ({len(resp.content)} bytes)")


def get_video_duration(video_path):
    """Get the duration of a video file in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def merge_video_audio(video_path, audio_path, output_path, bgm_volume=0.3,
                      fade_in=0, fade_out=0):
    """Merge video with background audio using ffmpeg."""
    duration = get_video_duration(video_path)

    audio_filter = f"[1:a]volume={bgm_volume}"
    if fade_in > 0:
        audio_filter += f",afade=t=in:d={fade_in}"
    if fade_out > 0:
        audio_filter += f",afade=t=out:st={max(0, duration - fade_out)}:d={fade_out}"
    audio_filter += "[bgm]"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex", audio_filter,
        "-map", "0:v",
        "-map", "[bgm]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg merge failed: {result.stderr}")
    print(f"Merged video+audio -> {output_path}")
    return str(output_path)


def generate_video_segment(args, prompt, first_frame_path, subject_reference_path,
                           output_path, headers):
    """Generate a single video segment."""

    class SegmentArgs:
        pass

    seg_args = SegmentArgs()
    seg_args.mode = "i2v" if first_frame_path else "t2v"
    seg_args.prompt = prompt
    seg_args.model = args.model
    seg_args.duration = args.segment_duration
    seg_args.resolution = args.resolution
    seg_args.first_frame = first_frame_path
    seg_args.last_frame = None
    seg_args.subject_image = subject_reference_path
    seg_args.prompt_optimizer = False if first_frame_path else None
    seg_args.fast_pretreatment = None
    seg_args.callback_url = None
    seg_args.aigc_watermark = None

    if subject_reference_path and not first_frame_path:
        seg_args.mode = "ref"

    payload = build_payload(seg_args)
    task_id = create_task(payload, headers)
    status, file_id = poll_task(task_id, headers)
    download_video(file_id, output_path, headers)
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Long Video Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--scenes", nargs="+", required=True,
                        help="List of scene prompts (each becomes a video segment)")
    parser.add_argument("--model", help="Video model (auto-selected if omitted)")
    parser.add_argument("--segment-duration", dest="segment_duration", type=int, default=10,
                        help="Duration per segment in seconds (default: 10)")
    parser.add_argument("--resolution", default="768P", help="Video resolution (default: 768P)")
    parser.add_argument("--first-frame", dest="first_frame",
                        help="First frame image for the initial segment (path or URL)")
    parser.add_argument("--subject-reference", dest="subject_reference",
                        help="Subject reference image for consistency (path or URL)")
    parser.add_argument("--crossfade", type=float, default=0.5,
                        help="Crossfade duration between segments in seconds (default: 0.5, 0 to disable)")

    music = parser.add_argument_group("background music")
    music.add_argument("--music-prompt", dest="music_prompt",
                       help="Prompt for AI-generated instrumental BGM")
    music.add_argument("--bgm-volume", dest="bgm_volume", type=float, default=0.3,
                       help="BGM volume level (default: 0.3)")
    music.add_argument("--fade-in", dest="fade_in", type=float, default=0,
                       help="BGM fade-in duration in seconds")
    music.add_argument("--fade-out", dest="fade_out", type=float, default=0,
                       help="BGM fade-out duration in seconds")

    parser.add_argument("--output", "-o", required=True, help="Output video file path")

    args = parser.parse_args()

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("Error: MINIMAX_API_KEY environment variable is not set.")
        return 1

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    output_dir = pathlib.Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Place temp files in a tmp/ sibling directory alongside output
    tmpdir = output_dir / "tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    print(f"Temp directory: {tmpdir}")

    try:
        segment_paths = []

        print(f"=== Generating {len(args.scenes)} video segments ===\n")

        current_first_frame = args.first_frame

        for i, scene_prompt in enumerate(args.scenes):
            print(f"\n--- Segment {i + 1}/{len(args.scenes)} ---")
            print(f"  Prompt: {scene_prompt}")

            segment_output = str(tmpdir / f"segment_{i:03d}.mp4")

            try:
                generate_video_segment(
                    args=args,
                    prompt=scene_prompt,
                    first_frame_path=current_first_frame,
                    subject_reference_path=args.subject_reference,
                    output_path=segment_output,
                    headers=headers,
                )
                segment_paths.append(segment_output)

                last_frame_path = str(tmpdir / f"last_frame_{i:03d}.jpg")
                try:
                    extract_last_frame(segment_output, last_frame_path)
                    current_first_frame = last_frame_path
                except Exception as e:
                    print(f"  Warning: Could not extract last frame: {e}")
                    current_first_frame = None

            except Exception as e:
                print(f"  Error generating segment {i + 1}: {e}")
                if not segment_paths:
                    return 1
                print("  Continuing with segments generated so far...")
                break

        if not segment_paths:
            print("Error: No segments were generated.")
            return 1

        if len(segment_paths) == 1:
            import shutil
            final_video = args.output
            shutil.copy2(segment_paths[0], final_video)
        else:
            final_video = str(tmpdir / "concatenated.mp4") if args.music_prompt else args.output
            concatenate_videos(segment_paths, final_video, crossfade=args.crossfade)

        if args.music_prompt:
            print(f"\n--- Generating background music ---")
            music_path = str(tmpdir / "bgm.mp3")
            try:
                generate_music_instrumental(args.music_prompt, api_key, music_path)
                merge_video_audio(
                    video_path=final_video,
                    audio_path=music_path,
                    output_path=args.output,
                    bgm_volume=args.bgm_volume,
                    fade_in=args.fade_in,
                    fade_out=args.fade_out,
                )
            except Exception as e:
                print(f"Warning: Failed to add BGM: {e}")
                if final_video != args.output:
                    import shutil
                    shutil.copy2(final_video, args.output)

        print(f"\n=== Done! Output: {args.output} ===")
        print(f"  Intermediate files in: {tmpdir}")
        print(f"  Delete with: rm -rf {tmpdir}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
