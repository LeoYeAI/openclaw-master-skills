#!/usr/bin/env python3
"""
Transcribe audio using Whisper and output a JSON file with per-sentence timestamps.

Supports two engines (auto-detected):
  - faster-whisper (recommended, 4x faster, less memory)
  - openai-whisper (fallback)

Usage: python3 transcribe.py <audio_path> [--model auto] [--language zh] [--engine auto]
Output: <audio_dir>/<video_name>_transcript.json
"""

import argparse
import json
import os
import sys

# Allow importing utils from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    detect_gpu, detect_whisper_engine, recommend_whisper_model,
    get_whisper_device, setup_china_env, detect_platform,
)


def transcribe_faster_whisper(audio_path, model_name, language, device, compute_type):
    """Transcribe using faster-whisper engine."""
    from faster_whisper import WhisperModel

    print(f"[faster-whisper] Loading model: {model_name} (device={device}, compute={compute_type})")
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    kwargs = {}
    if language:
        kwargs["language"] = language

    segments_iter, info = model.transcribe(audio_path, **kwargs)
    detected_lang = info.language

    segments = []
    for i, seg in enumerate(segments_iter, start=1):
        segments.append({
            "id": i,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })

    return segments, detected_lang


def transcribe_openai_whisper(audio_path, model_name, language):
    """Transcribe using openai-whisper engine."""
    import whisper

    print(f"[openai-whisper] Loading model: {model_name}")
    model = whisper.load_model(model_name)

    kwargs = {}
    if language:
        kwargs["language"] = language

    result = model.transcribe(audio_path, **kwargs)
    detected_lang = result.get("language", "unknown")

    segments = []
    for i, seg in enumerate(result.get("segments", []), start=1):
        segments.append({
            "id": i,
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        })

    return segments, detected_lang


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with Whisper")
    parser.add_argument("audio_path", help="Path to the audio file (.wav)")
    parser.add_argument("--model", default="auto",
                        help="Whisper model size: tiny/base/small/medium/large-v3/large-v3-turbo/auto (default: auto)")
    parser.add_argument("--language", default=None,
                        help="Language code (e.g. zh, en, ja). Omit for auto-detection.")
    parser.add_argument("--engine", default="auto", choices=["auto", "faster-whisper", "openai-whisper"],
                        help="Whisper engine (default: auto-detect)")
    parser.add_argument("--mirror", action="store_true",
                        help="Use China mirrors for model download")
    args = parser.parse_args()

    audio_path = os.path.abspath(args.audio_path)
    if not os.path.isfile(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    # China mirror setup
    if args.mirror:
        os.environ["USE_CN_MIRROR"] = "1"
    setup_china_env()

    # Detect GPU & hardware
    gpu_info = detect_gpu()

    # Choose engine
    if args.engine == "auto":
        engine = detect_whisper_engine()
        if engine == "none":
            print("Error: No Whisper engine found.", file=sys.stderr)
            print("Install one of:", file=sys.stderr)
            print("  pip install faster-whisper  (recommended, 4x faster)", file=sys.stderr)
            print("  pip install openai-whisper", file=sys.stderr)
            sys.exit(1)
    else:
        engine = args.engine

    # Choose model
    if args.model == "auto":
        model_name, reason = recommend_whisper_model(gpu_info)
        print(f"[auto] Selected model: {model_name} ({reason})")
    else:
        model_name = args.model

    print(f"Engine: {engine}")
    print(f"Model: {model_name}")
    print(f"GPU: {gpu_info['type']}")
    print(f"Transcribing: {audio_path}")

    # Run transcription
    if engine == "faster-whisper":
        device, compute_type = get_whisper_device(gpu_info)
        segments, detected_lang = transcribe_faster_whisper(
            audio_path, model_name, args.language, device, compute_type
        )
    else:
        segments, detected_lang = transcribe_openai_whisper(
            audio_path, model_name, args.language
        )

    # Build output path
    audio_dir = os.path.dirname(audio_path)
    audio_name = os.path.splitext(os.path.basename(audio_path))[0]
    video_name = audio_name.replace("_audio", "")
    output_path = os.path.join(audio_dir, f"{video_name}_transcript.json")

    output_data = {
        "source_audio": audio_path,
        "engine": engine,
        "model": model_name,
        "language": detected_lang,
        "segments": segments,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nTranscription complete: {output_path}")
    print(f"Total segments: {len(segments)}")
    print("\nSegment preview:")
    for seg in segments[:5]:
        print(f"  #{seg['id']:3d} [{seg['start']:7.2f}s - {seg['end']:7.2f}s] {seg['text']}")
    if len(segments) > 5:
        print(f"  ... and {len(segments) - 5} more segments")


if __name__ == "__main__":
    main()
