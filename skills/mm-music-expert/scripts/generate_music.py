import argparse
import os
import sys
import time
import requests

from utils_audio import hex_to_bytes, save_bytes, download_url

API_URL = "https://api.minimaxi.com/v1/music_generation"
POLL_INTERVAL = 5  # seconds between status checks
MAX_WAIT_TIME = 900  # max 15 minutes for complex music
REQUEST_TIMEOUT = 180  # per-request HTTP timeout
MAX_CONSECUTIVE_FAILURES = 5  # tolerate transient errors across long polls


def build_prompt_from_fields(args):
    fields = []
    def add(label, value):
        if value:
            fields.append(f"{label}: {value}")

    add("Genre", args.genre)
    add("Mood", args.mood)
    add("Tempo", args.tempo or (f"{args.bpm} BPM" if args.bpm else None))
    add("Key", args.key)
    add("Instruments", args.instruments)
    add("Vocals", args.vocals)
    add("Use case", args.use_case)
    add("Structure", args.structure)
    add("Avoid", args.avoid)
    add("References", args.references)

    if not fields:
        return None
    return "\n".join(fields)


def build_payload(args):
    payload = {
        "model": args.model,
    }

    if args.lyrics:
        payload["lyrics"] = args.lyrics

    if args.is_instrumental is not None:
        payload["is_instrumental"] = args.is_instrumental

    if args.lyrics_optimizer is not None:
        payload["lyrics_optimizer"] = args.lyrics_optimizer

    prompt = args.prompt
    if prompt is None:
        prompt = build_prompt_from_fields(args)
    if prompt is not None:
        payload["prompt"] = prompt

    if args.output_format:
        payload["output_format"] = args.output_format

    if args.stream:
        payload["stream"] = True

    if args.aigc_watermark is not None:
        payload["aigc_watermark"] = args.aigc_watermark

    audio_setting = {}
    if args.sample_rate:
        audio_setting["sample_rate"] = args.sample_rate
    if args.bitrate:
        audio_setting["bitrate"] = args.bitrate
    if args.format:
        audio_setting["format"] = args.format

    if audio_setting:
        payload["audio_setting"] = audio_setting

    return payload


def submit_and_poll(api_url, payload, headers):
    """
    Submit music generation request and poll until status == 2 (completed).
    Uses consecutive-failure tracking with exponential backoff so transient
    network errors don't kill a long-running generation.
    """
    start_time = time.time()
    consecutive_failures = 0

    print("[info] Submitting music generation request...", file=sys.stderr)

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(
                f"Music generation timed out after {int(elapsed)}s "
                f"(limit: {MAX_WAIT_TIME}s)"
            )

        try:
            resp = requests.post(
                api_url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()

            consecutive_failures = 0

            base_resp = data.get("base_resp", {})
            if base_resp.get("status_code") != 0:
                status_code = base_resp.get("status_code")
                if status_code in [1002, 1008]:
                    wait_time = 10
                    print(
                        f"[warning] API error ({status_code}): "
                        f"{base_resp.get('status_msg')}, retrying in {wait_time}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"API error: {base_resp}")

            status = data.get("data", {}).get("status")

            if status == 2:
                return data
            elif status == 1:
                print(
                    f"[info] Generating... {int(elapsed)}s elapsed",
                    file=sys.stderr,
                )
                time.sleep(POLL_INTERVAL)
            else:
                raise RuntimeError(f"Unexpected generation status: {status}")

        except requests.exceptions.Timeout:
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise TimeoutError(
                    f"Request timed out {MAX_CONSECUTIVE_FAILURES} consecutive times. "
                    f"Total elapsed: {int(elapsed)}s"
                )
            backoff = min(POLL_INTERVAL * (2 ** (consecutive_failures - 1)), 30)
            print(
                f"[warning] Request timed out, retry "
                f"{consecutive_failures}/{MAX_CONSECUTIVE_FAILURES} "
                f"(backoff {backoff}s)...",
                file=sys.stderr,
            )
            time.sleep(backoff)

        except requests.exceptions.ConnectionError:
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise
            backoff = min(POLL_INTERVAL * (2 ** (consecutive_failures - 1)), 30)
            print(
                f"[warning] Connection error, retry "
                f"{consecutive_failures}/{MAX_CONSECUTIVE_FAILURES} "
                f"(backoff {backoff}s)...",
                file=sys.stderr,
            )
            time.sleep(backoff)

        except requests.exceptions.RequestException as e:
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise
            backoff = min(POLL_INTERVAL * (2 ** (consecutive_failures - 1)), 30)
            print(
                f"[warning] Request failed: {e}, retry "
                f"{consecutive_failures}/{MAX_CONSECUTIVE_FAILURES} "
                f"(backoff {backoff}s)...",
                file=sys.stderr,
            )
            time.sleep(backoff)


def main():
    parser = argparse.ArgumentParser(description="Generate music with MiniMax Music API")
    parser.add_argument("--lyrics", default=None, help="Lyrics text (use \\n for line breaks). Not required for pure music with is_instrumental=true or lyrics_optimizer=true")
    parser.add_argument("--prompt", default=None, help="Style/scene prompt (required for is_instrumental=true)")
    parser.add_argument("--model", default="music-2.5+", help="Model name (default: music-2.5+)")
    parser.add_argument("--is-instrumental", type=lambda v: v.lower() == "true", default=None, help="Generate pure music without vocals (music-2.5+ only)")
    parser.add_argument("--lyrics-optimizer", type=lambda v: v.lower() == "true", default=None, help="Auto-generate lyrics from prompt")
    parser.add_argument("--genre", default=None, help="Genre/subgenre (e.g., 1980s synthwave)")
    parser.add_argument("--mood", default=None, help="Mood/emotion (e.g., nostalgic, uplifting)")
    parser.add_argument("--tempo", default=None, help="Tempo description (e.g., upbeat, slow groove)")
    parser.add_argument("--bpm", type=int, default=None, help="Tempo in BPM (e.g., 120)")
    parser.add_argument("--key", default=None, help="Musical key (e.g., A minor)")
    parser.add_argument("--instruments", default=None, help="Key instruments or textures")
    parser.add_argument("--vocals", default=None, help="Vocal style or 'Instrumental only'")
    parser.add_argument("--use-case", dest="use_case", default=None, help="Usage context (e.g., game, ad, meditation)")
    parser.add_argument("--structure", default=None, help="Song structure (e.g., Intro/Verse/Chorus/Bridge)")
    parser.add_argument("--avoid", default=None, help="Negative prompt (e.g., no vocals, avoid reverb)")
    parser.add_argument("--references", default=None, help="Style references (artists/songs)")
    parser.add_argument("--output", required=True, help="Output file path (e.g., ./music.mp3)")
    parser.add_argument("--output-format", choices=["hex", "url"], default="url", help="Response format (default: url - faster and more reliable)")
    parser.add_argument("--stream", action="store_true", help="Enable streaming (hex only)")
    parser.add_argument("--sample-rate", type=int, default=None)
    parser.add_argument("--bitrate", type=int, default=None)
    parser.add_argument("--format", dest="format", default=None, help="Audio format, e.g., mp3")
    parser.add_argument("--aigc-watermark", type=lambda v: v.lower() == "true", default=None)
    parser.add_argument("--download", action="store_true", help="Download if output_format=url")
    args = parser.parse_args()

    api_key = os.getenv("MINIMAX_MUSIC_API_KEY")
    if not api_key:
        print("MINIMAX_MUSIC_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    if args.stream and args.output_format != "hex":
        print("When --stream is true, output_format must be hex", file=sys.stderr)
        sys.exit(1)

    # Validation for is_instrumental
    if args.is_instrumental and args.model != "music-2.5+":
        print("Warning: is_instrumental is only supported on music-2.5+. Will use music-2.5+...", file=sys.stderr)
        args.model = "music-2.5+"

    # Validation: lyrics required unless is_instrumental=true or lyrics_optimizer=true
    if not args.lyrics and not args.is_instrumental and not args.lyrics_optimizer:
        print("Error: --lyrics is required (unless --is-instrumental=true or --lyrics-optimizer=true)", file=sys.stderr)
        sys.exit(1)

    # Validation: prompt is required for is_instrumental=true (per official API docs)
    if args.is_instrumental and not args.prompt and not build_prompt_from_fields(args):
        print("Error: --prompt is required for pure music generation (is_instrumental=true)", file=sys.stderr)
        sys.exit(1)

    if args.prompt is None:
        auto_prompt = build_prompt_from_fields(args)
        if auto_prompt:
            print("[info] Built prompt from fields:\n" + auto_prompt)
    payload = build_payload(args)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if args.stream:
        print("[info] Using streaming mode (direct response)...", file=sys.stderr)
        try:
            resp = requests.post(
                API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            print("Error: Streaming request timed out.", file=sys.stderr)
            sys.exit(1)
    else:
        fmt = args.output_format or "hex"
        print(f"[info] Starting generation (format={fmt}) with polling...", file=sys.stderr)
        data = submit_and_poll(API_URL, payload, headers)

    base_resp = data.get("base_resp", {})
    if base_resp.get("status_code") != 0:
        raise RuntimeError(f"API error: {base_resp}")

    audio_data = data.get("data", {}).get("audio")
    if not audio_data:
        raise RuntimeError("No audio data returned")

    extra_info = data.get("extra_info", {})
    if extra_info:
        duration_ms = extra_info.get("music_duration", 0)
        duration_sec = duration_ms / 1000
        print(f"[info] Generation complete! Duration: {duration_sec:.1f}s", file=sys.stderr)

    if args.output_format == "hex":
        audio_bytes = hex_to_bytes(audio_data)
        saved = save_bytes(audio_bytes, args.output)
        print(saved)
        return

    # output_format == url
    # Default to auto-download for url format
    if args.download or args.output_format == "url":
        saved = download_url(audio_data, args.output)
        print(saved)
    else:
        # print URL for manual download
        print(audio_data)


if __name__ == "__main__":
    main()
