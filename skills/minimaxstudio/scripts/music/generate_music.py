#!/usr/bin/env python3
"""
MiniMax Music Generation CLI.

Usage (from project root):
    python scripts/music/generate_music.py --lyrics "[verse]\\nHello world" --output output/song.mp3
    python scripts/music/generate_music.py --lyrics "[verse]\\nSunrise" --prompt "upbeat pop" --output output/pop.mp3
    python scripts/music/generate_music.py --lyrics "[verse]\\nStars" --genre pop --mood happy --output output/happy.mp3
    python scripts/music/generate_music.py --lyrics "[verse]\\nOcean" --output output/ocean.mp3 --output-format url --download
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from utils_audio import hex_to_bytes, save_bytes, download_url

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from env_loader import load_dotenv
load_dotenv()

API_HOST = os.getenv("MINIMAX_API_HOST", "https://api.minimaxi.com")
API_URL = f"{API_HOST}/v1/music_generation"
USE_CURL_FALLBACK = os.getenv("MUSIC_USE_CURL", "true").lower() == "true"


def build_prompt_from_fields(args):
    """Build a descriptive prompt string from structured CLI fields."""
    parts = []
    if args.genre:
        parts.append(f"Genre: {args.genre}")
    if args.mood:
        parts.append(f"Mood: {args.mood}")
    if args.tempo:
        parts.append(f"Tempo: {args.tempo}")
    if args.bpm:
        parts.append(f"BPM: {args.bpm}")
    if args.key:
        parts.append(f"Key: {args.key}")
    if args.instruments:
        parts.append(f"Instruments: {args.instruments}")
    if args.vocals:
        parts.append(f"Vocals: {args.vocals}")
    if args.use_case:
        parts.append(f"Use case: {args.use_case}")
    if args.structure:
        parts.append(f"Structure: {args.structure}")
    if args.avoid:
        parts.append(f"Avoid: {args.avoid}")
    if args.references:
        parts.append(f"References: {args.references}")
    return ". ".join(parts) if parts else ""


def build_payload(args):
    """Build the API request payload."""
    prompt = args.prompt or ""
    field_prompt = build_prompt_from_fields(args)
    if field_prompt:
        prompt = f"{prompt}. {field_prompt}" if prompt else field_prompt

    payload = {
        "model": args.model,
        "prompt": prompt,
        "output_format": args.output_format,
        "stream": args.stream,
        "audio_setting": {},
    }

    if args.instrumental:
        payload["is_instrumental"] = True
    else:
        payload["lyrics"] = args.lyrics or ""

    if args.sample_rate:
        payload["audio_setting"]["sample_rate"] = args.sample_rate
    if args.bitrate:
        payload["audio_setting"]["bitrate"] = args.bitrate
    if args.format:
        payload["audio_setting"]["format"] = args.format

    if not payload["audio_setting"]:
        del payload["audio_setting"]

    if args.aigc_watermark is not None:
        payload["aigc_watermark"] = args.aigc_watermark

    return payload


def send_request_curl(payload, api_key):
    """Send request using curl as a fallback."""
    headers_args = [
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
    ]
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST", API_URL,
        *headers_args,
        "-d", json.dumps(payload),
    ]
    print(f"Using curl fallback...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr}")

    output = result.stdout.strip()
    lines = output.rsplit("\n", 1)
    if len(lines) == 2:
        body, status_code = lines
    else:
        body = output
        status_code = "200"

    if not status_code.startswith("2"):
        raise RuntimeError(f"API returned HTTP {status_code}: {body}")

    return json.loads(body)


def send_request_python(payload, api_key):
    """Send request using the requests library."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Music Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--lyrics", default="", help="Song lyrics with structure tags like [verse], [chorus]")
    parser.add_argument("--prompt", help="Text prompt describing the desired music style")
    parser.add_argument("--model", default="music-2.5+", help="Model name (default: music-2.5+)")
    parser.add_argument("--instrumental", action="store_true", default=False,
                        help="Generate instrumental music (no vocals/lyrics, uses is_instrumental API flag)")

    style = parser.add_argument_group("style fields (auto-appended to prompt)")
    style.add_argument("--genre", help="Music genre (e.g., pop, rock, jazz)")
    style.add_argument("--mood", help="Mood/emotion (e.g., happy, melancholic)")
    style.add_argument("--tempo", help="Tempo description (e.g., fast, slow, moderate)")
    style.add_argument("--bpm", help="Beats per minute")
    style.add_argument("--key", help="Musical key (e.g., C major, A minor)")
    style.add_argument("--instruments", help="Instruments to feature")
    style.add_argument("--vocals", help="Vocal style description")
    style.add_argument("--use-case", dest="use_case", help="Intended use (e.g., background, intro)")
    style.add_argument("--structure", help="Song structure hints")
    style.add_argument("--avoid", help="Elements to avoid")
    style.add_argument("--references", help="Reference tracks or artists")

    output_group = parser.add_argument_group("output")
    output_group.add_argument("--output", "-o", required=True, help="Output file path")
    output_group.add_argument("--output-format", choices=["hex", "url"], default="url",
                              help="API output format (default: url)")
    output_group.add_argument("--stream", action="store_true", default=False, help="Enable streaming")
    output_group.add_argument("--download", action="store_true", default=False,
                              help="Download audio when output-format is url")

    audio = parser.add_argument_group("audio settings")
    audio.add_argument("--sample-rate", type=int, dest="sample_rate", help="Sample rate (e.g., 44100)")
    audio.add_argument("--bitrate", type=int, help="Bitrate (e.g., 128000)")
    audio.add_argument("--format", help="Audio format (e.g., mp3, wav)")

    parser.add_argument("--aigc-watermark", dest="aigc_watermark", type=int, choices=[0, 1],
                        help="AIGC watermark (0=off, 1=on)")

    args = parser.parse_args()

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("Error: MINIMAX_API_KEY environment variable is not set.")
        return 1

    payload = build_payload(args)
    print(f"Generating music with model: {args.model}")
    print(f"Output format: {args.output_format}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        if USE_CURL_FALLBACK:
            data = send_request_curl(payload, api_key)
        else:
            data = send_request_python(payload, api_key)
    except Exception as e:
        if USE_CURL_FALLBACK:
            print(f"Curl request failed: {e}")
            return 1
        print(f"Python request failed: {e}, trying curl fallback...")
        try:
            data = send_request_curl(payload, api_key)
        except Exception as e2:
            print(f"Curl fallback also failed: {e2}")
            return 1

    if "base_resp" in data and data["base_resp"].get("status_code", 0) != 0:
        print(f"API error: {data['base_resp']}")
        return 1

    audio_data = data.get("data", data)

    if args.output_format == "hex":
        audio_hex = audio_data.get("audio", "")
        if not audio_hex:
            print("Error: No audio hex data in response.")
            print(f"Response keys: {list(data.keys())}")
            return 1
        audio_bytes = hex_to_bytes(audio_hex)
        saved = save_bytes(audio_bytes, args.output)
        print(f"Audio saved to: {saved}")

    elif args.output_format == "url":
        audio_url = audio_data.get("audio_url", audio_data.get("audio", ""))
        if not audio_url:
            audio_file = audio_data.get("audio_file", {})
            audio_url = audio_file.get("download_url", "")
        if not audio_url:
            print("Error: No audio URL in response.")
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return 1
        print(f"Audio URL: {audio_url}")
        if args.download:
            saved = download_url(audio_url, args.output)
            print(f"Audio downloaded to: {saved}")
        else:
            print(f"Use --download to save the file, or download manually from the URL above.")
            import pathlib
            pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(args.output).write_text(audio_url)
            print(f"URL written to: {args.output}")

    extra = {}
    if "extra_info" in data:
        extra = data["extra_info"]
    elif "extra_info" in audio_data:
        extra = audio_data["extra_info"]
    if extra:
        print(f"Extra info: {json.dumps(extra, indent=2, ensure_ascii=False)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
