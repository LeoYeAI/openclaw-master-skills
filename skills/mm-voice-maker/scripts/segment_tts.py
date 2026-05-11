"""
MiniMax Voice API - Segment-based TTS Module

Generates audio from segmentation file (segments.json) with per-segment
voice and emotion settings. Designed for multi-voice and multi-emotion workflows.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, asdict


# Valid emotion types for MiniMax API
# Available emotions: happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
# Chinese: 高兴, 悲伤, 愤怒, 害怕, 厌恶, 惊讶, 中性, 生动, 低语
VALID_EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"]

# Cache for available voices (to avoid repeated API calls)
_cached_voices: Optional[set] = None


def _get_available_voices() -> set:
    """
    Get set of available voice IDs from the API.
    
    Returns:
        Set of available voice IDs (cached after first call)
    """
    global _cached_voices
    if _cached_voices is None:
        try:
            from .voice_management import get_all_custom_voices, get_system_voices
            # Get all voice IDs
            system_voices = get_system_voices()
            custom_voices = get_all_custom_voices()
            
            # Extract voice_ids
            _cached_voices = set()
            for voice in system_voices:
                if voice_id := voice.get("voice_id"):
                    _cached_voices.add(voice_id)
            for voice in custom_voices:
                if voice_id := voice.get("voice_id"):
                    _cached_voices.add(voice_id)
                    
            print(f"✓ Loaded {len(_cached_voices)} available voices")
        except Exception as e:
            print(f"⚠ Warning: Could not fetch available voices: {e}")
            _cached_voices = set()
    
    return _cached_voices if _cached_voices else set()


def clear_voice_cache():
    """Clear the voice cache to force refetching from API"""
    global _cached_voices
    _cached_voices = None


@dataclass
class SegmentInfo:
    """Information about a processed segment"""
    index: int
    text: str
    voice_id: str
    emotion: str
    audio_path: str
    success: bool
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of segment file validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    segments: List[Dict]
    
    def to_dict(self) -> Dict:
        return asdict(self)


def validate_segment(
    segment: Dict, 
    index: int,
    model: str = "speech-2.8-hd",
    validate_voice: bool = False,
    available_voices: Optional[set] = None
) -> tuple[List[str], List[str]]:
    """
    Validate a single segment entry.
    
    Args:
        segment: Segment dictionary
        index: Segment index for error reporting
        model: TTS model for context-specific validation
        validate_voice: Whether to validate voice_id against available voices (default: False)
        available_voices: Set of available voice IDs (used when validate_voice=True)
        
    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    
    # Check required 'text' field
    if "text" not in segment:
        errors.append(f"Segment {index}: missing required 'text' field")
    elif not isinstance(segment["text"], str):
        errors.append(f"Segment {index}: 'text' must be a string")
    elif not segment["text"].strip():
        errors.append(f"Segment {index}: 'text' cannot be empty")
    
    # Check required 'voice_id' field
    if "voice_id" not in segment:
        errors.append(f"Segment {index}: missing required 'voice_id' field")
    elif not isinstance(segment["voice_id"], str):
        errors.append(f"Segment {index}: 'voice_id' must be a string")
    elif not segment["voice_id"].strip():
        errors.append(f"Segment {index}: 'voice_id' cannot be empty")
    else:
        # Validate voice_id against available voices if requested
        if validate_voice and available_voices is not None:
            voice_id = segment["voice_id"]
            if available_voices and voice_id not in available_voices:
                # Voice not found - this is an error (not a warning)
                errors.append(
                    f"Segment {index}: voice_id '{voice_id}' not found in available voices. "
                    f"Use 'python mmvoice.py list-voices' to check available voices."
                )
    
    # Check 'emotion' field with model-specific validation
    emotion = segment.get("emotion", "")
    
    # Models that support automatic emotion matching (no manual emotion needed)
    auto_emotion_models = ["speech-2.8-hd", "speech-2.8-turbo"]
    
    if model in auto_emotion_models:
        # For speech-2.8 models: emotion can be empty or a valid emotion
        # Empty is recommended (auto-matching)
        if emotion and emotion.strip():
            if emotion.lower() not in VALID_EMOTIONS:
                errors.append(
                    f"Segment {index}: invalid emotion '{emotion}'. "
                    f"For {model}, use empty string for auto-matching or one of: {', '.join(VALID_EMOTIONS)}"
                )
            else:
                warnings.append(
                    f"Segment {index}: {model} automatically matches emotions. "
                    f"Consider using empty emotion string."
                )
        # Empty emotion is fine for auto-matching models
    else:
        # For older models: emotion is required
        if not emotion or not emotion.strip():
            errors.append(
                f"Segment {index}: 'emotion' is required for {model}. "
                f"Valid options: {', '.join(VALID_EMOTIONS)}"
            )
        elif emotion.lower() not in VALID_EMOTIONS:
            errors.append(
                f"Segment {index}: invalid emotion '{emotion}'. "
                f"Valid options: {', '.join(VALID_EMOTIONS)}"
            )
    
    return errors, warnings


def validate_segments_file(
    file_path: str,
    strict: bool = True,
    model: str = "speech-2.8-hd",
    validate_voice: bool = False
) -> ValidationResult:
    """
    Validate a segments.json file format and content.
    
    Args:
        file_path: Path to segments.json file
        strict: If True, treat warnings as errors
        model: TTS model for context-specific validation (default: speech-2.8-hd)
        validate_voice: Whether to validate voice_id against available voices (default: False)
        
    Returns:
        ValidationResult with validation status and details
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    errors = []
    warnings = []
    segments = []
    available_voices = None
    
    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Segments file not found: {file_path}")
    
    # Fetch available voices once (only if validate_voice is True)
    if validate_voice:
        print("Fetching available voices...")
        available_voices = _get_available_voices()
        if available_voices:
            print(f"✓ Loaded {len(available_voices)} available voices")
        else:
            print("⚠ Warning: Could not fetch available voices. Voice validation skipped.")
    
    # Read and parse JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings, segments=[])
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {e}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings, segments=[])
    
    # Must be a list
    if not isinstance(data, list):
        errors.append("Root element must be a JSON array")
        return ValidationResult(valid=False, errors=errors, warnings=warnings, segments=[])
    
    # Check for empty list
    if len(data) == 0:
        errors.append("Segments array is empty")
        return ValidationResult(valid=False, errors=errors, warnings=warnings, segments=[])
    
    # Validate each segment with model-specific rules
    for i, segment in enumerate(data):
        if not isinstance(segment, dict):
            errors.append(f"Segment {i}: must be a JSON object")
            continue
        
        seg_errors, seg_warnings = validate_segment(
            segment, 
            i, 
            model=model, 
            validate_voice=validate_voice,
            available_voices=available_voices
        )
        errors.extend(seg_errors)
        warnings.extend(seg_warnings)
    
    # Determine validity
    is_valid = len(errors) == 0
    if strict and len(warnings) > 0:
        is_valid = False
    
    return ValidationResult(
        valid=is_valid,
        errors=errors,
        warnings=warnings,
        segments=data if len(errors) == 0 else []
    )


def load_segments(
    file_path: str,
    validate: bool = True,
    strict: bool = False,
    model: str = "speech-2.8-hd"
) -> List[Dict]:
    """
    Load and optionally validate segments from file.
    
    Args:
        file_path: Path to segments.json file
        validate: Whether to validate the file content
        strict: Whether to treat warnings as errors
        model: TTS model for context-specific validation (default: speech-2.8-hd)
        
    Returns:
        List of segment dictionaries
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If validation fails
    """
    if validate:
        result = validate_segments_file(file_path, strict=strict, model=model)
        if not result.valid:
            error_msg = "Segment file validation failed:\n"
            for err in result.errors:
                error_msg += f"  - {err}\n"
            if strict:
                for warn in result.warnings:
                    error_msg += f"  - [Warning] {warn}\n"
            raise ValueError(error_msg)
        return result.segments
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


def generate_segment_audio(
    segment: Dict,
    index: int,
    output_dir: str,
    model: str = "speech-01-hd",
    audio_format: str = "mp3",
    sample_rate: int = 32000,
) -> SegmentInfo:
    """
    Generate audio for a single segment.
    
    Args:
        segment: Segment dictionary with text, voice_id, emotion
        index: Segment index
        output_dir: Directory to save audio file
        model: TTS model to use
        audio_format: Output audio format
        sample_rate: Audio sample rate
        
    Returns:
        SegmentInfo with generation result
    """
    # Import here to avoid circular imports and allow standalone validation
    from .utils import VoiceSetting, AudioSetting, save_audio_from_hex
    from .sync_tts import synthesize_speech_http
    
    text = segment["text"]
    voice_id = segment["voice_id"]
    emotion = segment.get("emotion", "").strip()
    
    # Determine if we should set emotion parameter
    # speech-2.8 models: auto-match emotions, don't set emotion parameter if empty
    # Older models: emotion must be set
    auto_emotion_models = ["speech-2.8-hd", "speech-2.8-turbo"]
    
    # Create output path
    output_path = os.path.join(output_dir, f"segment_{index:04d}.{audio_format}")
    
    try:
        # Configure voice with emotion
        voice_kwargs = {"voice_id": voice_id}
        
        # Only set emotion if:
        # 1. Model is NOT speech-2.8 series, OR
        # 2. Emotion is explicitly provided and valid
        if model not in auto_emotion_models:
            # Older models require emotion
            if not emotion:
                emotion = "calm"  # Default for older models
            voice_kwargs["emotion"] = emotion.lower()
        elif emotion:
            # speech-2.8 with explicit emotion (not recommended but supported)
            if emotion.lower() in VALID_EMOTIONS:
                voice_kwargs["emotion"] = emotion.lower()
            else:
                # Invalid emotion for speech-2.8, ignore it (auto-match)
                pass
        
        voice_setting = VoiceSetting(**voice_kwargs)
        
        audio_setting = AudioSetting(
            format=audio_format,
            sample_rate=sample_rate,
        )
        
        # Generate audio
        result = synthesize_speech_http(
            text=text,
            model=model,
            voice_setting=voice_setting,
            audio_setting=audio_setting,
        )
        
        # Save audio
        if result.get("data", {}).get("audio"):
            save_audio_from_hex(result["data"]["audio"], output_path)
            
            return SegmentInfo(
                index=index,
                text=text,
                voice_id=voice_id,
                emotion=emotion,
                audio_path=output_path,
                success=True,
            )
        else:
            return SegmentInfo(
                index=index,
                text=text,
                voice_id=voice_id,
                emotion=emotion,
                audio_path="",
                success=False,
                error="No audio data in response",
            )
            
    except Exception as e:
        return SegmentInfo(
            index=index,
            text=text,
            voice_id=voice_id,
            emotion=emotion,
            audio_path="",
            success=False,
            error=str(e),
        )


def generate_from_segments(
    segments_file: str,
    output_dir: Optional[str] = None,
    model: str = "speech-2.8-hd",
    audio_format: str = "mp3",
    sample_rate: int = 32000,
    stop_on_error: bool = False,
    validate: bool = True,
    skip_existing: bool = False,
) -> Dict[str, Any]:
    """
    Generate audio files from a segments.json file.

    Args:
        segments_file: Path to segments.json file
        output_dir: Directory to save audio files (defaults to temp directory)
        model: TTS model to use (default: speech-2.8-hd)
        audio_format: Output audio format (default: mp3)
        sample_rate: Audio sample rate (default: 32000)
        stop_on_error: If True, stop processing on first error
        validate: If True, validate segments file before processing
        skip_existing: If True, skip segments that already have audio files in output_dir
        
    Returns:
        Dictionary with:
            - success: bool - Overall success status
            - segments: List[SegmentInfo] - Results for each segment
            - audio_files: List[str] - Paths to successfully generated audio files
            - output_dir: str - Directory containing audio files
            - errors: List[str] - List of error messages
            
    Raises:
        FileNotFoundError: If segments file not found
        ValueError: If validation fails (when validate=True)
    """
    # Load and validate segments with model-specific rules
    segments = load_segments(segments_file, validate=validate, model=model)
    
    # Create output directory
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="mmvoice_segments_")
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # Process each segment
    results: List[SegmentInfo] = []
    audio_files: List[str] = []
    errors: List[str] = []
    
    for i, segment in enumerate(segments):
        # Check if audio file already exists (for skip_existing mode)
        if skip_existing:
            expected_file = os.path.join(output_dir, f"segment_{i:04d}.{audio_format}")
            if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                print(f"Processing segment {i + 1}/{len(segments)}: {segment['text'][:40]}...")
                print(f"  ⊘ [SKIP] File already exists: {os.path.basename(expected_file)}")
                results.append(SegmentInfo(
                    index=i,
                    text=segment["text"],
                    voice_id=segment.get("voice_id", ""),
                    emotion=segment.get("emotion", ""),
                    audio_path=expected_file,
                    success=True,
                ))
                audio_files.append(expected_file)
                continue

        print(f"Processing segment {i + 1}/{len(segments)}: {segment['text'][:40]}...")

        info = generate_segment_audio(
            segment=segment,
            index=i,
            output_dir=output_dir,
            model=model,
            audio_format=audio_format,
            sample_rate=sample_rate,
        )
        
        results.append(info)
        
        if info.success:
            audio_files.append(info.audio_path)
            # Show emotion label, or "AUTO" for auto-matched emotions
            emotion_label = info.emotion.upper() if info.emotion else "AUTO"
            print(f"  ✓ [{emotion_label}] -> {os.path.basename(info.audio_path)}")
        else:
            errors.append(f"Segment {i}: {info.error}")
            print(f"  ✗ Error: {info.error}")
            
            if stop_on_error:
                print("Stopping due to error (stop_on_error=True)")
                break
    
    # Determine overall success
    success = len(audio_files) == len(segments)
    
    return {
        "success": success,
        "segments": results,
        "audio_files": audio_files,
        "output_dir": output_dir,
        "errors": errors,
        "total": len(segments),
        "succeeded": len(audio_files),
        "failed": len(errors),
    }


def merge_segment_audio(
    audio_files: List[str],
    output_path: str,
    crossfade_ms: int = 0,
    normalize: bool = True,
    fade_in_ms: int = 0,
    fade_out_ms: int = 0,
) -> Dict[str, Any]:
    """
    Merge multiple audio files into a single output file.
    
    Args:
        audio_files: List of audio file paths (in order)
        output_path: Path for merged output file
        crossfade_ms: Crossfade duration between segments (default: 0)
        normalize: Whether to normalize audio levels (default: True)
        fade_in_ms: Fade in duration at start (default: 0)
        fade_out_ms: Fade out duration at end (default: 0)
        
    Returns:
        Dictionary with:
            - success: bool
            - output_path: str
            - error: Optional[str]
    """
    from .audio_processing import merge_audio_files
    
    if not audio_files:
        return {
            "success": False,
            "output_path": "",
            "error": "No audio files to merge",
        }
    
    # Verify all files exist
    missing = [f for f in audio_files if not os.path.exists(f)]
    if missing:
        return {
            "success": False,
            "output_path": "",
            "error": f"Missing audio files: {missing}",
        }
    
    try:
        merge_audio_files(
            input_files=audio_files,
            output_path=output_path,
            crossfade_ms=crossfade_ms,
            normalize=normalize,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            use_concat_fallback=True,  # Enable fallback for robustness
        )
        
        return {
            "success": True,
            "output_path": output_path,
            "error": None,
        }
        
    except Exception as e:
        return {
            "success": False,
            "output_path": "",
            "error": str(e),
        }


def process_segments_to_audio(
    segments_file: str,
    output_path: str,
    output_dir: Optional[str] = None,
    model: str = "speech-2.8-hd",
    crossfade_ms: int = 0,
    normalize: bool = True,
    keep_temp_files: bool = False,
    stop_on_error: bool = True,
    skip_existing: bool = False,
) -> Dict[str, Any]:
    """
    Complete pipeline: generate audio from segments and merge into final output.

    This is the main entry point for the segment-based TTS workflow.

    Args:
        segments_file: Path to segments.json file
        output_path: Path for final merged audio file
        output_dir: Directory for intermediate files (temp dir if not specified)
        model: TTS model to use (default: speech-2.8-hd, auto emotion matching)
        crossfade_ms: Crossfade between segments (default: 0)
        normalize: Normalize audio levels (default: True)
        keep_temp_files: Keep intermediate segment files (default: False)
        stop_on_error: Stop on first generation error (default: True)
        skip_existing: Skip segments that already have audio files (default: False)
        
    Returns:
        Dictionary with:
            - success: bool
            - output_path: str - Final output path (if success)
            - segments_result: Dict - Result from generate_from_segments
            - merge_result: Dict - Result from merge_segment_audio (if generation succeeded)
            - error: Optional[str] - Error message if failed
            
    Example:
        result = process_segments_to_audio(
            segments_file="segments.json",
            output_path="final_output.mp3",
            crossfade_ms=200,
            normalize=True,
        )
        if result["success"]:
            print(f"Audio saved to: {result['output_path']}")
        else:
            print(f"Error: {result['error']}")
    """
    # Step 1: Generate audio for each segment
    print(f"=== Step 1: Generating audio from {segments_file} ===")
    gen_result = generate_from_segments(
        segments_file=segments_file,
        output_dir=output_dir,
        model=model,
        stop_on_error=stop_on_error,
        skip_existing=skip_existing,
    )
    
    if not gen_result["success"] and stop_on_error:
        return {
            "success": False,
            "output_path": "",
            "segments_result": gen_result,
            "merge_result": None,
            "error": f"Audio generation failed for {gen_result['failed']}/{gen_result['total']} segments",
        }
    
    if not gen_result["audio_files"]:
        return {
            "success": False,
            "output_path": "",
            "segments_result": gen_result,
            "merge_result": None,
            "error": "No audio files generated",
        }
    
    # Step 2: Merge audio files
    print(f"\n=== Step 2: Merging {len(gen_result['audio_files'])} audio files ===")
    merge_result = merge_segment_audio(
        audio_files=gen_result["audio_files"],
        output_path=output_path,
        crossfade_ms=crossfade_ms,
        normalize=normalize,
    )
    
    # Cleanup temp files if requested
    if not keep_temp_files and merge_result["success"]:
        import shutil
        temp_dir = gen_result["output_dir"]
        if temp_dir and temp_dir.startswith(tempfile.gettempdir()):
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                print(f"Warning: Failed to cleanup temp dir: {e}")
    
    if not merge_result["success"]:
        return {
            "success": False,
            "output_path": "",
            "segments_result": gen_result,
            "merge_result": merge_result,
            "error": f"Audio merge failed: {merge_result['error']}",
        }
    
    print(f"\n✓ Final audio saved to: {output_path}")
    
    return {
        "success": True,
        "output_path": output_path,
        "segments_result": gen_result,
        "merge_result": merge_result,
        "error": None,
    }
