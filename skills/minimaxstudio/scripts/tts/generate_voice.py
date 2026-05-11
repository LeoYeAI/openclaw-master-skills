#!/usr/bin/env python3
"""
MiniMax Voice CLI - Unified command-line interface for TTS operations.

Usage (from MiniMaxStudio directory):
    python scripts/tts/generate_voice.py tts "Hello world" -o hello.mp3
    python scripts/tts/generate_voice.py clone my_voice.mp3 --voice-id my-custom-voice
    python scripts/tts/generate_voice.py design "A gentle female voice" --voice-id designed-voice-1
    python scripts/tts/generate_voice.py list-voices
    python scripts/tts/generate_voice.py validate segments.json
    python scripts/tts/generate_voice.py generate segments.json -o output.mp3
    python scripts/tts/generate_voice.py merge file1.mp3 file2.mp3 -o combined.mp3
    python scripts/tts/generate_voice.py convert input.wav -o output.mp3
    python scripts/tts/generate_voice.py check-env
"""

import sys
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
TTS_DIR = Path(__file__).resolve().parent
if str(TTS_DIR) not in sys.path:
    sys.path.insert(0, str(TTS_DIR))


def cmd_tts(args):
    from scripts.tts.sync_tts import quick_tts

    print(f"Synthesizing: {args.text[:50]}...")
    try:
        audio = quick_tts(
            text=args.text,
            voice_id=args.voice_id,
            output_path=args.output,
        )
        if args.output:
            print(f"Done: {args.output}")
        else:
            print(f"Generated {len(audio)} bytes")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_validate(args):
    from scripts.tts.segment_tts import validate_segments_file, VALID_EMOTIONS

    if not os.path.exists(args.segments_file):
        print(f"Error: File not found: {args.segments_file}")
        return 1

    print(f"Validating: {args.segments_file}")
    print(f"Model: {args.model}")
    print(f"Valid emotions: {', '.join(VALID_EMOTIONS)}")
    if args.validate_voices:
        print("Voice validation: enabled")
    print()

    try:
        result = validate_segments_file(
            args.segments_file,
            strict=args.strict,
            model=args.model,
            validate_voice=args.validate_voices,
        )
        if result.errors:
            print("=== Errors ===")
            for err in result.errors:
                print(f"  - {err}")
            print()
        if result.warnings:
            print("=== Warnings ===")
            for warn in result.warnings:
                print(f"  ! {warn}")
            print()
        if result.valid:
            print(f"Validation passed: {len(result.segments)} segments")
            if args.verbose:
                print("\n=== Segment Summary ===")
                for i, seg in enumerate(result.segments):
                    text = seg["text"][:40] + "..." if len(seg["text"]) > 40 else seg["text"]
                    emotion = seg.get("emotion", "")
                    emotion_label = "AUTO" if not emotion else emotion.upper()
                    voice = seg.get("voice_id", "?")
                    print(f"  {i}: [{emotion_label:10}] voice={voice[:20]:20} \"{text}\"")
            return 0
        else:
            print("Validation failed")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_generate(args):
    from scripts.tts.segment_tts import process_segments_to_audio, validate_segments_file

    if not os.path.exists(args.segments_file):
        print(f"Error: Segments file not found: {args.segments_file}")
        return 1

    print("Validating segments file...")
    result = validate_segments_file(args.segments_file, strict=False, model=args.model)
    if not result.valid:
        print("Validation failed:")
        for err in result.errors:
            print(f"  - {err}")
        return 1
    print(f"Found {len(result.segments)} valid segments\n")

    output_path = args.output
    temp_dir = args.temp_dir

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if not temp_dir:
        # Place temp files alongside output in a tmp/ sibling directory
        output_parent = os.path.dirname(os.path.abspath(output_path))
        temp_dir = os.path.join(output_parent, "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Temp directory: {temp_dir}")

    try:
        result = process_segments_to_audio(
            segments_file=args.segments_file,
            output_path=output_path,
            output_dir=temp_dir,
            model=args.model,
            crossfade_ms=args.crossfade,
            normalize=not args.no_normalize,
            keep_temp_files=True,
            stop_on_error=not args.continue_on_error,
        )
        if result["success"]:
            print(f"\nAudio saved to: {result['output_path']}")
            gen = result["segments_result"]
            print(f"  Generated: {gen['succeeded']}/{gen['total']} segments")
            if os.path.exists(temp_dir) and os.listdir(temp_dir):
                print(f"\n  Intermediate files in: {temp_dir}")
                print(f"  Delete with: rm -rf {temp_dir}")
            return 0
        else:
            print(f"\nError: {result['error']}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_clone(args):
    from scripts.tts.voice_clone import quick_clone_voice
    from scripts.tts.sync_tts import quick_tts

    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        return 1

    print(f"Cloning voice from: {args.audio_file}")
    print(f"Voice ID: {args.voice_id}")
    try:
        quick_clone_voice(audio_path=args.audio_file, voice_id=args.voice_id)
        print(f"Voice cloned successfully: {args.voice_id}")
        if args.preview_text:
            print("Generating preview...")
            preview_path = args.preview_output or f"{args.voice_id}_preview.mp3"
            quick_tts(text=args.preview_text, voice_id=args.voice_id, output_path=preview_path)
            print(f"Preview saved to: {preview_path}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_design(args):
    from scripts.tts.voice_design import design_voice
    from scripts.tts.utils import save_audio_from_hex

    print(f"Designing voice from: \"{args.description}\"")
    print(f"Voice ID: {args.voice_id}")
    try:
        result = design_voice(
            prompt=args.description,
            preview_text=args.preview_text or "This is a preview of the designed voice.",
            voice_id=args.voice_id,
        )
        actual_voice_id = args.voice_id or result.get("voice_id")
        print(f"Voice designed: {actual_voice_id}")
        if result.get("trial_audio"):
            preview_path = args.preview_output or f"{actual_voice_id}_preview.mp3"
            save_audio_from_hex(result["trial_audio"], preview_path)
            print(f"Preview saved to: {preview_path}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_list_voices(args):
    from scripts.tts.voice_management import get_system_voices, get_all_custom_voices

    print("=== System Voices ===")
    system_voices = get_system_voices()
    if system_voices:
        for voice in system_voices[:10]:
            vid = voice.get("voice_id", "N/A")
            name = voice.get("name", "N/A")
            print(f"  {vid}: {name}")
        if len(system_voices) > 10:
            print(f"  ... and {len(system_voices) - 10} more")
    else:
        print("  (None found)")

    print("\n=== Custom Voices ===")
    custom = get_all_custom_voices()
    cloned = custom.get("cloned", [])
    designed = custom.get("designed", [])
    if cloned:
        print(f"Cloned ({len(cloned)}):")
        for voice in cloned:
            print(f"  {voice.get('voice_id', 'N/A')}")
    if designed:
        print(f"Designed ({len(designed)}):")
        for voice in designed:
            print(f"  {voice.get('voice_id', 'N/A')}")
    if not cloned and not designed:
        print("  (None found)")
    return 0


def cmd_merge(args):
    from scripts.tts.audio_processing import merge_audio_files

    print(f"Merging {len(args.input_files)} files...")
    for f in args.input_files:
        if not os.path.exists(f):
            print(f"Error: File not found: {f}")
            return 1
    try:
        merge_audio_files(
            input_files=args.input_files,
            output_path=args.output,
            format=args.format,
            crossfade_ms=args.crossfade,
            normalize=args.normalize,
        )
        print(f"Merged audio saved to: {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_convert(args):
    from scripts.tts.audio_processing import convert_audio

    if not os.path.exists(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        return 1
    print(f"Converting {args.input_file} to {args.format}...")
    try:
        convert_audio(
            input_path=args.input_file,
            output_path=args.output,
            target_format=args.format,
            sample_rate=args.sample_rate,
            bitrate=args.bitrate,
            channels=args.channels,
        )
        print(f"Converted audio saved to: {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_check_env(args):
    import subprocess as sp
    check_script = PROJECT_ROOT / "scripts" / "check_environment.py"
    if not check_script.exists():
        print("check_environment.py not found")
        return 1
    result = sp.run([sys.executable, str(check_script)] + sys.argv[2:])
    return result.returncode


def create_parser():
    parser = argparse.ArgumentParser(
        description="MiniMax Voice CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s tts "Hello world" -o hello.mp3
  %(prog)s tts "你好世界" -v female-shaonv -o hello_cn.mp3
  %(prog)s validate segments.json --verbose
  %(prog)s generate segments.json -o output.mp3
  %(prog)s clone my_voice.mp3 --voice-id my-custom-voice
  %(prog)s design "A warm female voice" --voice-id narrator-1
  %(prog)s list-voices
  %(prog)s merge part1.mp3 part2.mp3 -o complete.mp3
  %(prog)s convert input.wav -o output.mp3
  %(prog)s check-env --test-api
        """,
    )
    sub = parser.add_subparsers(dest="command", help="Command to execute")

    # tts
    p = sub.add_parser("tts", help="Basic text-to-speech")
    p.add_argument("text", help="Text to synthesize")
    p.add_argument("-v", "--voice-id", default="male-qn-qingse", help="Voice ID")
    p.add_argument("-o", "--output", help="Output file path")
    p.set_defaults(func=cmd_tts)

    # validate
    p = sub.add_parser("validate", help="Validate segments.json file")
    p.add_argument("segments_file", help="Path to segments.json")
    p.add_argument("--model", default="speech-2.8-hd", help="TTS model")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    p.add_argument("-v", "--verbose", action="store_true", help="Show segment details")
    p.add_argument("--validate-voices", action="store_true", help="Validate voice_id against API")
    p.set_defaults(func=cmd_validate)

    # generate
    p = sub.add_parser("generate", help="Generate audio from segments.json")
    p.add_argument("segments_file", help="Path to segments.json")
    p.add_argument("-o", "--output", required=True, help="Output audio file path")
    p.add_argument("--model", default="speech-2.8-hd", help="TTS model")
    p.add_argument("--crossfade", type=int, default=200, help="Crossfade between segments in ms (default: 200)")
    p.add_argument("--no-normalize", action="store_true", help="Disable normalization")
    p.add_argument("--temp-dir", help="Directory for intermediate files")
    p.add_argument("--continue-on-error", action="store_true", help="Continue if a segment fails")
    p.set_defaults(func=cmd_generate)

    # clone
    p = sub.add_parser("clone", help="Clone voice from audio sample")
    p.add_argument("audio_file", help="Audio file (10s-5min, mp3/wav/m4a)")
    p.add_argument("--voice-id", required=True, help="Custom voice ID")
    p.add_argument("--preview", dest="preview_text", help="Generate preview with this text")
    p.add_argument("--preview-output", help="Preview output path")
    p.set_defaults(func=cmd_clone)

    # design
    p = sub.add_parser("design", help="Design voice from description")
    p.add_argument("description", help="Voice description prompt")
    p.add_argument("--voice-id", help="Custom voice ID")
    p.add_argument("--preview", dest="preview_text", help="Preview text")
    p.add_argument("--preview-output", help="Preview output path")
    p.set_defaults(func=cmd_design)

    # list-voices
    p = sub.add_parser("list-voices", help="List available voices")
    p.set_defaults(func=cmd_list_voices)

    # merge
    p = sub.add_parser("merge", help="Merge multiple audio files")
    p.add_argument("input_files", nargs="+", help="Input audio files")
    p.add_argument("-o", "--output", required=True, help="Output file path")
    p.add_argument("--format", default="mp3", help="Output format")
    p.add_argument("--crossfade", type=int, default=300, help="Crossfade ms")
    p.add_argument("--no-normalize", dest="normalize", action="store_false", help="Disable normalization")
    p.set_defaults(func=cmd_merge)

    # convert
    p = sub.add_parser("convert", help="Convert audio format")
    p.add_argument("input_file", help="Input audio file")
    p.add_argument("-o", "--output", required=True, help="Output file path")
    p.add_argument("--format", default="mp3", help="Target format")
    p.add_argument("--sample-rate", type=int, help="Sample rate")
    p.add_argument("--bitrate", help="Bitrate (e.g., 192k)")
    p.add_argument("--channels", type=int, help="Channels (1=mono, 2=stereo)")
    p.set_defaults(func=cmd_convert)

    # check-env
    p = sub.add_parser("check-env", help="Check environment setup")
    p.add_argument("--test-api", action="store_true", help="Test API connectivity")
    p.set_defaults(func=cmd_check_env)

    return parser


def main():
    parser = create_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    args = parser.parse_args()
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
