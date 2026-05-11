#!/usr/bin/env python3
"""
Add background music to a video file.

Supports using an existing audio file or generating AI music via the MiniMax
Music API. Can mix BGM with original audio or replace it entirely.

Usage (from project root):
    python scripts/video/add_bgm.py --video input.mp4 --audio bgm.mp3 --output output.mp4
    python scripts/video/add_bgm.py --video input.mp4 --generate-bgm --music-prompt "upbeat pop" --output output.mp4
    python scripts/video/add_bgm.py --video input.mp4 --generate-bgm --instrumental --output output.mp4
    python scripts/video/add_bgm.py --video input.mp4 --audio bgm.mp3 --replace-audio --output output.mp4
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from env_loader import load_dotenv
load_dotenv()

MUSIC_API_URL = "https://api.minimaxi.com/v1/music_generation"


def generate_music(prompt, api_key, output_path, instrumental=False):
    """Generate music via the MiniMax Music API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "music-2.5+",
        "prompt": prompt or "background music, cinematic, ambient",
        "output_format": "url",
    }

    if instrumental:
        payload["is_instrumental"] = True
    else:
        payload["lyrics"] = "[Intro]\nla da da\nla la la"

    print(f"Generating {'instrumental ' if instrumental else ''}music...")
    print(f"  Prompt: {prompt}")

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

    download_with_retry(audio_url, output_path)
    return str(output_path)


def download_with_retry(url, output_path, max_retries=3):
    """Download a file from a URL with retry logic."""
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            path.write_bytes(resp.content)
            print(f"  Downloaded: {output_path} ({len(resp.content)} bytes)")
            return str(path)
        except Exception as e:
            if attempt == max_retries:
                raise RuntimeError(f"Download failed after {max_retries} attempts: {e}")
            wait = 2 ** attempt
            print(f"  Download attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)


def video_has_audio(video_path):
    """Check if a video file contains an audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return False
    info = json.loads(result.stdout)
    streams = info.get("streams", [])
    return len(streams) > 0


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
                      fade_in=0, fade_out=0, keep_original_audio=True):
    """Merge video with background audio using ffmpeg."""
    output = pathlib.Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    duration = get_video_duration(video_path)
    has_audio = video_has_audio(video_path)

    bgm_filter = f"[1:a]volume={bgm_volume}"
    if fade_in > 0:
        bgm_filter += f",afade=t=in:d={fade_in}"
    if fade_out > 0:
        bgm_filter += f",afade=t=out:st={max(0, duration - fade_out)}:d={fade_out}"

    if keep_original_audio and has_audio:
        bgm_filter += "[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-filter_complex", bgm_filter,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ]
    else:
        bgm_filter += "[bgm]"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-filter_complex", bgm_filter,
            "-map", "0:v",
            "-map", "[bgm]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ]

    print(f"Merging video + audio (bgm_volume={bgm_volume}, "
          f"fade_in={fade_in}s, fade_out={fade_out}s, "
          f"keep_original={keep_original_audio})...")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg merge failed: {result.stderr}")

    print(f"Output saved: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Add background music to a video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--video", required=True, help="Input video file path")

    audio_source = parser.add_argument_group("audio source (choose one)")
    audio_source.add_argument("--audio", help="Path to an existing audio/music file")
    audio_source.add_argument("--generate-bgm", dest="generate_bgm", action="store_true",
                              help="Generate BGM using MiniMax Music API")
    audio_source.add_argument("--instrumental", action="store_true",
                              help="Generate instrumental music (no vocals)")
    audio_source.add_argument("--music-prompt", dest="music_prompt",
                              help="Prompt for AI music generation")

    mix = parser.add_argument_group("mixing options")
    mix.add_argument("--bgm-volume", dest="bgm_volume", type=float, default=0.3,
                     help="BGM volume level 0.0-1.0 (default: 0.3)")
    mix.add_argument("--fade-in", dest="fade_in", type=float, default=0,
                     help="BGM fade-in duration in seconds")
    mix.add_argument("--fade-out", dest="fade_out", type=float, default=0,
                     help="BGM fade-out duration in seconds")
    mix.add_argument("--replace-audio", dest="replace_audio", action="store_true",
                     help="Replace original audio instead of mixing")

    parser.add_argument("--output", "-o", required=True, help="Output video file path")

    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        return 1

    if not args.audio and not args.generate_bgm:
        print("Error: Provide --audio or --generate-bgm")
        return 1

    audio_path = args.audio

    if args.generate_bgm:
        api_key = os.getenv("MINIMAX_API_KEY")
        if not api_key:
            print("Error: MINIMAX_API_KEY environment variable is not set.")
            return 1
        audio_path = os.path.splitext(args.output)[0] + "_bgm.mp3"
        try:
            generate_music(
                prompt=args.music_prompt,
                api_key=api_key,
                output_path=audio_path,
                instrumental=args.instrumental,
            )
        except Exception as e:
            print(f"Error generating music: {e}")
            return 1

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return 1

    try:
        duration = get_video_duration(args.video)
        print(f"Video duration: {duration:.1f}s")

        merge_video_audio(
            video_path=args.video,
            audio_path=audio_path,
            output_path=args.output,
            bgm_volume=args.bgm_volume,
            fade_in=args.fade_in,
            fade_out=args.fade_out,
            keep_original_audio=not args.replace_audio,
        )
        print("Done!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
