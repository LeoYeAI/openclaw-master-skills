#!/usr/bin/env python3
"""
MiniMax Voice Maker - Command Line Interface

A unified CLI tool for all MiniMax Voice Maker operations.
Supports TTS, segment-based TTS, voice cloning, voice design, and audio processing.

Usage:
    # Basic TTS
    python mmvoice.py tts "Hello world" -o hello.mp3
    
    # Segment-based TTS workflow (multi-voice, multi-emotion)
    python mmvoice.py validate segments.json              # Validate segments file
    python mmvoice.py generate segments.json              # Generate audio from segments
    
    # Voice clone
    python mmvoice.py clone my_voice.mp3 --voice-id my-custom-voice
    
    # Voice design
    python mmvoice.py design "A gentle female voice" --voice-id designed-voice-1
    
    # List voices
    python mmvoice.py list-voices
    
    # Environment check
    python mmvoice.py check-env
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, List


# Add scripts to path
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def cmd_tts(args):
    """Basic TTS command"""
    from scripts import quick_tts
    
    print(f"Synthesizing: {args.text[:50]}...")
    
    try:
        audio = quick_tts(
            text=args.text,
            voice_id=args.voice_id,
            output_path=args.output,
        )
        
        if args.output:
            print(f"✓ Audio saved to: {args.output}")
        else:
            print(f"✓ Generated {len(audio)} bytes")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


def cmd_validate(args):
    """Validate segments.json file"""
    from scripts import validate_segments_file, VALID_EMOTIONS
    
    if not os.path.exists(args.segments_file):
        print(f"✗ Error: File not found: {args.segments_file}")
        return 1
    
    print(f"Validating: {args.segments_file}")
    print(f"Model: {args.model}")
    print(f"Valid emotions: {', '.join(VALID_EMOTIONS)}")
    if args.validate_voices:
        print("Voice validation: enabled (checking against available voices)")
    else:
        print("Voice validation: disabled (use --validate-voices to enable)")
    print()
    
    try:
        result = validate_segments_file(
            args.segments_file, 
            strict=args.strict, 
            model=args.model,
            validate_voice=args.validate_voices
        )
        
        if result.errors:
            print("=== Errors ===")
            for err in result.errors:
                print(f"  ✗ {err}")
            print()
        
        if result.warnings:
            print("=== Warnings ===")
            for warn in result.warnings:
                print(f"  ⚠ {warn}")
            print()
        
        if result.valid:
            print(f"✓ Validation passed: {len(result.segments)} segments")
            
            # Show segment summary if verbose
            if args.verbose:
                print("\n=== Segment Summary ===")
                for i, seg in enumerate(result.segments):
                    text = seg["text"][:40] + "..." if len(seg["text"]) > 40 else seg["text"]
                    emotion = seg.get("emotion", "")
                    # Show "AUTO" for empty emotion (speech-2.8), otherwise show emotion
                    emotion_label = "AUTO" if not emotion else emotion.upper()
                    voice = seg.get("voice_id", "?")
                    print(f"  {i}: [{emotion_label:10}] voice={voice[:20]:20} \"{text}\"")
            return 0
        else:
            print(f"✗ Validation failed")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def cmd_generate(args):
    """Generate audio from segments.json"""
    from scripts import process_segments_to_audio, validate_segments_file
    
    if not os.path.exists(args.segments_file):
        print(f"✗ Error: Segments file not found: {args.segments_file}")
        return 1
    
    # Validate first
    print("Validating segments file...")
    result = validate_segments_file(args.segments_file, strict=False, model=args.model)
    if not result.valid:
        print("✗ Validation failed:")
        for err in result.errors:
            print(f"  - {err}")
        return 1
    print(f"✓ Found {len(result.segments)} valid segments\n")
    
    # Determine output path and temp directory
    # Default: ./audio/output.mp3 with temp files in ./audio/tmp/
    audio_dir = os.path.join(os.getcwd(), "audio")
    temp_dir = args.temp_dir
    output_path = args.output
    
    if not output_path:
        # Default output to ./audio/output.mp3
        os.makedirs(audio_dir, exist_ok=True)
        output_path = os.path.join(audio_dir, "output.mp3")
        print(f"Output path: {output_path}")
    
    if not temp_dir:
        # Default temp to ./audio/tmp/
        temp_dir = os.path.join(audio_dir, "tmp")
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
            keep_temp_files=True,  # Always keep temp initially
            stop_on_error=not args.continue_on_error,
            skip_existing=args.skip_existing,
        )
        
        if result["success"]:
            print(f"\n✓ Audio saved to: {result['output_path']}")
            gen_result = result["segments_result"]
            print(f"  Generated: {gen_result['succeeded']}/{gen_result['total']} segments")
            
            # Show temp files location
            if os.path.exists(temp_dir) and os.listdir(temp_dir):
                print(f"\n  Intermediate files in: {temp_dir}")
                print(f"  After confirming audio quality, delete with: rm -rf {temp_dir}")
            
            return 0
        else:
            print(f"\n✗ Error: {result['error']}")
            return 1
            
    except ValueError as e:
        print(f"✗ Validation error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def cmd_clone(args):
    """Voice cloning command"""
    from scripts import quick_clone_voice, quick_tts
    
    if not os.path.exists(args.audio_file):
        print(f"✗ Error: Audio file not found: {args.audio_file}")
        return 1
    
    print(f"Cloning voice from: {args.audio_file}")
    print(f"Voice ID: {args.voice_id}")
    
    try:
        quick_clone_voice(
            audio_path=args.audio_file,
            voice_id=args.voice_id,
        )
        
        print(f"✓ Voice cloned successfully: {args.voice_id}")
        
        # Generate preview if requested
        if args.preview_text:
            print(f"\nGenerating preview...")
            preview_path = args.preview_output or f"{args.voice_id}_preview.mp3"
            quick_tts(
                text=args.preview_text,
                voice_id=args.voice_id,
                output_path=preview_path,
            )
            print(f"✓ Preview saved to: {preview_path}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


def cmd_design(args):
    """Voice design command"""
    from scripts import design_voice, quick_tts, save_audio_from_hex
    
    print(f"Designing voice from description:")
    print(f"  \"{args.description}\"")
    print(f"Voice ID: {args.voice_id}")
    
    try:
        result = design_voice(
            prompt=args.description,
            preview_text=args.preview_text or "This is a preview of the designed voice.",
            voice_id=args.voice_id,
        )
        
        # Use custom voice_id if different from returned one
        actual_voice_id = args.voice_id or result.get('voice_id')
        print(f"✓ Voice designed: {actual_voice_id}")
        
        # Save preview
        if result.get('trial_audio'):
            preview_path = args.preview_output or f"{actual_voice_id}_preview.mp3"
            save_audio_from_hex(result['trial_audio'], preview_path)
            print(f"✓ Preview saved to: {preview_path}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


def cmd_list_voices(args):
    """List available voices"""
    from scripts import get_system_voices, get_all_custom_voices
    
    print("=== System Voices ===")
    system_voices = get_system_voices()
    if system_voices:
        for voice in system_voices[:10]:  # Show first 10
            voice_id = voice.get('voice_id', 'N/A')
            name = voice.get('name', 'N/A')
            print(f"  {voice_id}: {name}")
        if len(system_voices) > 10:
            print(f"  ... and {len(system_voices) - 10} more")
    else:
        print("  (None found)")
    
    print("\n=== Custom Voices ===")
    custom = get_all_custom_voices()
    
    cloned = custom.get('cloned', [])
    designed = custom.get('designed', [])
    
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
    """Merge audio files"""
    from scripts import merge_audio_files
    
    print(f"Merging {len(args.input_files)} files...")
    
    for f in args.input_files:
        if not os.path.exists(f):
            print(f"✗ Error: File not found: {f}")
            return 1
    
    try:
        merge_audio_files(
            input_files=args.input_files,
            output_path=args.output,
            format=args.format,
            crossfade_ms=args.crossfade,
            normalize=args.normalize,
        )
        
        print(f"✓ Merged audio saved to: {args.output}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


def cmd_convert(args):
    """Convert audio format"""
    from scripts import convert_audio
    
    if not os.path.exists(args.input_file):
        print(f"✗ Error: File not found: {args.input_file}")
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
        
        print(f"✓ Converted audio saved to: {args.output}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


def cmd_check_env(args):
    """Run environment check"""
    import subprocess
    
    check_script = Path(__file__).parent / "check_environment.py"
    
    if not check_script.exists():
        print("✗ check_environment.py not found")
        return 1
    
    # Run check script
    result = subprocess.run([sys.executable, str(check_script)] + sys.argv[2:])
    return result.returncode


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="MiniMax Voice Maker CLI - Unified command-line interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic TTS
  %(prog)s tts "Hello world" -o hello.mp3
  %(prog)s tts "你好世界" -v female-shaonv -o hello_cn.mp3
  
  # Segment-based TTS workflow (multi-voice, multi-emotion)
  %(prog)s validate segments.json                    # Validate segments file
  %(prog)s validate segments.json --verbose          # Show segment details
  %(prog)s generate segments.json -o output.mp3     # Generate and merge audio
  %(prog)s generate segments.json --crossfade 200   # With crossfade
  
  # Voice cloning
  %(prog)s clone my_voice.mp3 --voice-id my-custom-voice
  
  # Voice design
  %(prog)s design "A warm female voice for storytelling" --voice-id narrator-1
  
  # List voices
  %(prog)s list-voices
  
  # Audio processing
  %(prog)s merge part1.mp3 part2.mp3 part3.mp3 -o complete.mp3
  %(prog)s convert input.wav -o output.mp3 --format mp3 --bitrate 192k
  
  # Environment check
  %(prog)s check-env
  %(prog)s check-env --test-api
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # TTS command
    tts_parser = subparsers.add_parser('tts', help='Basic text-to-speech')
    tts_parser.add_argument('text', help='Text to synthesize')
    tts_parser.add_argument('-v', '--voice-id', default='male-qn-qingse', help='Voice ID (default: male-qn-qingse)')
    tts_parser.add_argument('-o', '--output', help='Output file path (e.g., output.mp3)')
    tts_parser.set_defaults(func=cmd_tts)
    
    # Validate segments file command
    validate_parser = subparsers.add_parser('validate', help='Validate segments.json file')
    validate_parser.add_argument('segments_file', help='Path to segments.json file')
    validate_parser.add_argument('--model', default='speech-2.8-hd', help='TTS model for context-specific validation (default: speech-2.8-hd)')
    validate_parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    validate_parser.add_argument('-v', '--verbose', action='store_true', help='Show segment details')
    validate_parser.add_argument('--validate-voices', action='store_true', help='Validate voice_id against available voices (may be slow)')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Generate from segments command
    generate_parser = subparsers.add_parser('generate', help='Generate audio from segments.json')
    generate_parser.add_argument('segments_file', help='Path to segments.json file')
    generate_parser.add_argument('-o', '--output', help='Output audio file path (default: ./audio/output.mp3)')
    generate_parser.add_argument('--model', default='speech-2.8-hd', help='TTS model (default: speech-2.8-hd, supports automatic emotion matching)')
    generate_parser.add_argument('--crossfade', type=int, default=0, help='Crossfade between segments in ms (default: 0)')
    generate_parser.add_argument('--no-normalize', action='store_true', help='Disable audio normalization')
    generate_parser.add_argument('--temp-dir', help='Directory for intermediate files (default: ./audio/tmp/)')
    generate_parser.add_argument('--keep-temp', action='store_true', help='Keep intermediate files (always kept by default; delete manually after confirming audio)')
    generate_parser.add_argument('--continue-on-error', action='store_true', help='Continue if a segment fails')
    generate_parser.add_argument('--skip-existing', action='store_true', help='Skip segments that already have corresponding audio files in temp directory')
    generate_parser.set_defaults(func=cmd_generate)
    
    # Clone command
    clone_parser = subparsers.add_parser('clone', help='Clone voice from audio sample')
    clone_parser.add_argument('audio_file', help='Audio file to clone from (10s-5min, mp3/wav/m4a)')
    clone_parser.add_argument('--voice-id', required=True, help='Custom voice ID for cloned voice')
    clone_parser.add_argument('--preview', dest='preview_text', help='Generate preview with this text')
    clone_parser.add_argument('--preview-output', help='Preview output path')
    clone_parser.set_defaults(func=cmd_clone)
    
    # Design command
    design_parser = subparsers.add_parser('design', help='Design voice from description')
    design_parser.add_argument('description', help='Voice description prompt')
    design_parser.add_argument('--voice-id', help='Custom voice ID (optional)')
    design_parser.add_argument('--preview', dest='preview_text', help='Preview text')
    design_parser.add_argument('--preview-output', help='Preview output path')
    design_parser.set_defaults(func=cmd_design)
    
    # List voices command
    list_parser = subparsers.add_parser('list-voices', help='List available voices')
    list_parser.set_defaults(func=cmd_list_voices)
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple audio files')
    merge_parser.add_argument('input_files', nargs='+', help='Input audio files')
    merge_parser.add_argument('-o', '--output', required=True, help='Output file path')
    merge_parser.add_argument('--format', default='mp3', help='Output format (default: mp3)')
    merge_parser.add_argument('--crossfade', type=int, default=300, help='Crossfade duration in ms (default: 300)')
    merge_parser.add_argument('--no-normalize', dest='normalize', action='store_false', help='Disable normalization')
    merge_parser.set_defaults(func=cmd_merge)
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert audio format')
    convert_parser.add_argument('input_file', help='Input audio file')
    convert_parser.add_argument('-o', '--output', required=True, help='Output file path')
    convert_parser.add_argument('--format', default='mp3', help='Target format (default: mp3)')
    convert_parser.add_argument('--sample-rate', type=int, help='Sample rate (e.g., 32000)')
    convert_parser.add_argument('--bitrate', help='Bitrate (e.g., 192k)')
    convert_parser.add_argument('--channels', type=int, help='Number of channels (1=mono, 2=stereo)')
    convert_parser.set_defaults(func=cmd_convert)
    
    # Check environment command
    check_parser = subparsers.add_parser('check-env', help='Check environment setup')
    check_parser.add_argument('--test-api', action='store_true', help='Test API connectivity')
    check_parser.set_defaults(func=cmd_check_env)
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    
    # Show help if no command provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
