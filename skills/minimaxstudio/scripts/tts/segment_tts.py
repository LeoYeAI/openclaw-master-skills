"""
MiniMax Voice API - Segment-based TTS Module
Provides multi-segment text-to-speech synthesis with per-segment voice and emotion control.

Workflow:
  1. Define segments in a JSON file (text, voice_id, emotion per segment)
  2. Validate the segments file
  3. Generate audio for each segment
  4. Merge segment audio files into a single output

Docs: https://platform.minimaxi.com/document/T2A%20V2
"""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, asdict


VALID_EMOTIONS = [
    "happy", "sad", "angry", "fearful", "disgusted",
    "surprised", "calm", "fluent", "whisper",
]

_cached_voices: Optional[set] = None


def _get_available_voices() -> set:
    """
    Retrieve all available voice IDs (system + custom) and cache them.

    Returns:
        Set of available voice_id strings.
    """
    global _cached_voices
    if _cached_voices is not None:
        return _cached_voices

    voices = set()
    try:
        from .voice_management import get_all_custom_voices, get_system_voices
    except ImportError:
        from voice_management import get_all_custom_voices, get_system_voices

    try:
        system_voices = get_system_voices()
        if system_voices:
            for voice in system_voices:
                vid = voice.get("voice_id")
                if vid:
                    voices.add(vid)
    except Exception:
        pass

    try:
        custom_voices = get_all_custom_voices()
        for voice in custom_voices.get("cloned", []) + custom_voices.get("designed", []):
            vid = voice.get("voice_id")
            if vid:
                voices.add(vid)
    except Exception:
        pass

    _cached_voices = voices
    return _cached_voices


@dataclass
class ValidationResult:
    """Result of segment validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    segments: List[Dict[str, Any]]


@dataclass
class SegmentInfo:
    """Metadata and result for a single processed segment."""
    index: int
    text: str
    voice_id: str
    emotion: Optional[str]
    audio_path: Optional[str]
    success: bool
    error: Optional[str]


def validate_segment(
    segment: Dict[str, Any],
    index: int,
    strict: bool = False,
    model: str = "speech-2.6-hd",
    validate_voice: bool = False,
) -> tuple:
    """
    Validate a single segment dictionary.

    Args:
        segment: Segment dict with keys like text, voice_id, emotion.
        index: Segment index (for error messages).
        strict: If True, warnings are treated as errors.
        model: TTS model name (affects valid emotions).
        validate_voice: If True, check voice_id against the API.

    Returns:
        Tuple of (errors: list[str], warnings: list[str], cleaned_segment: dict).
    """
    errors: List[str] = []
    warnings: List[str] = []
    cleaned: Dict[str, Any] = {}

    # Validate text
    text = segment.get("text", "").strip()
    if not text:
        errors.append(f"Segment {index}: 'text' is required and must not be empty")
    elif len(text) > 10000:
        errors.append(f"Segment {index}: text exceeds maximum length of 10,000 characters")
    cleaned["text"] = text

    # Validate voice_id
    voice_id = segment.get("voice_id", "").strip()
    if not voice_id:
        errors.append(f"Segment {index}: 'voice_id' is required")
    cleaned["voice_id"] = voice_id

    if validate_voice and voice_id:
        available = _get_available_voices()
        if available and voice_id not in available:
            msg = (
                f"Segment {index}: voice_id '{voice_id}' not found in available voices. "
                f"Run: python scripts/tts/generate_voice.py list-voices"
            )
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

    # Validate emotion
    emotion = segment.get("emotion", None)
    if emotion is not None:
        emotion = emotion.strip().lower()
        if emotion == "":
            emotion = None
        elif emotion not in VALID_EMOTIONS:
            errors.append(
                f"Segment {index}: invalid emotion '{emotion}'. "
                f"Valid emotions: {', '.join(VALID_EMOTIONS)}"
            )

        if emotion in ("fluent", "whisper"):
            if model and not model.startswith("speech-2.6") and not model.startswith("speech-2.8"):
                warnings.append(
                    f"Segment {index}: emotion '{emotion}' only works with "
                    f"speech-2.6-hd/turbo or speech-2.8-hd/turbo models"
                )
    cleaned["emotion"] = emotion

    # Pass through optional fields
    for key in ("speed", "volume", "pitch", "language_boost"):
        if key in segment:
            cleaned[key] = segment[key]

    return errors, warnings, cleaned


def validate_segments_file(
    file_path: str,
    strict: bool = False,
    model: str = "speech-2.6-hd",
    validate_voice: bool = False,
) -> ValidationResult:
    """
    Validate a segments JSON file.

    The file should contain a JSON array of segment objects, or an object
    with a "segments" key containing the array.

    Args:
        file_path: Path to the JSON file.
        strict: If True, treat warnings as errors.
        model: TTS model name.
        validate_voice: If True, validate voice_id values against the API.

    Returns:
        ValidationResult with validation outcome and cleaned segments.
    """
    all_errors: List[str] = []
    all_warnings: List[str] = []
    cleaned_segments: List[Dict[str, Any]] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ValidationResult(
            valid=False,
            errors=[f"File not found: {file_path}"],
            warnings=[],
            segments=[],
        )
    except json.JSONDecodeError as e:
        return ValidationResult(
            valid=False,
            errors=[f"Invalid JSON: {e}"],
            warnings=[],
            segments=[],
        )

    # Accept both a raw list and {"segments": [...]}
    if isinstance(data, dict):
        segments = data.get("segments", [])
    elif isinstance(data, list):
        segments = data
    else:
        return ValidationResult(
            valid=False,
            errors=["JSON root must be an array or an object with a 'segments' key"],
            warnings=[],
            segments=[],
        )

    if not segments:
        return ValidationResult(
            valid=False,
            errors=["No segments found in file"],
            warnings=[],
            segments=[],
        )

    for i, segment in enumerate(segments):
        if not isinstance(segment, dict):
            all_errors.append(f"Segment {i}: must be a JSON object")
            continue

        seg_errors, seg_warnings, cleaned = validate_segment(
            segment, i, strict=strict, model=model, validate_voice=validate_voice
        )
        all_errors.extend(seg_errors)
        all_warnings.extend(seg_warnings)

        if not seg_errors:
            cleaned_segments.append(cleaned)

    if strict:
        all_errors.extend(all_warnings)
        all_warnings = []

    return ValidationResult(
        valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        segments=cleaned_segments,
    )


def load_segments(file_path: str) -> List[Dict[str, Any]]:
    """
    Load and return segments from a JSON file (no validation).

    Args:
        file_path: Path to segments JSON file.

    Returns:
        List of segment dictionaries.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("segments", [])
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("JSON root must be an array or an object with a 'segments' key")


def generate_segment_audio(
    segment: Dict[str, Any],
    index: int,
    output_dir: str,
    model: str = "speech-2.6-hd",
) -> SegmentInfo:
    """
    Generate audio for a single segment.

    Args:
        segment: Validated segment dict (text, voice_id, emotion, ...).
        index: Segment index for naming the output file.
        output_dir: Directory to write the segment audio file.
        model: TTS model name.

    Returns:
        SegmentInfo with the result of the generation attempt.
    """
    try:
        from .utils import VoiceSetting, AudioSetting, save_audio_from_hex
        from .sync_tts import synthesize_speech_http
    except ImportError:
        from utils import VoiceSetting, AudioSetting, save_audio_from_hex
        from sync_tts import synthesize_speech_http

    text = segment["text"]
    voice_id = segment["voice_id"]
    emotion = segment.get("emotion")
    speed = segment.get("speed", 1.0)
    volume = segment.get("volume", 1.0)
    pitch = segment.get("pitch", 0)

    audio_path = os.path.join(output_dir, f"segment_{index:04d}.mp3")

    try:
        voice_setting = VoiceSetting(
            voice_id=voice_id,
            speed=speed,
            volume=volume,
            pitch=pitch,
            emotion=emotion,
        )
        audio_setting = AudioSetting(format="mp3")

        result = synthesize_speech_http(
            text=text,
            model=model,
            voice_setting=voice_setting,
            audio_setting=audio_setting,
        )

        audio_data = result.get("data", {}).get("audio", "")
        if not audio_data:
            audio_data = result.get("extra_info", {}).get("audio", "")

        if not audio_data:
            return SegmentInfo(
                index=index, text=text, voice_id=voice_id, emotion=emotion,
                audio_path=None, success=False, error="No audio data in response",
            )

        save_audio_from_hex(audio_data, audio_path)

        return SegmentInfo(
            index=index, text=text, voice_id=voice_id, emotion=emotion,
            audio_path=audio_path, success=True, error=None,
        )

    except Exception as e:
        return SegmentInfo(
            index=index, text=text, voice_id=voice_id, emotion=emotion,
            audio_path=None, success=False, error=str(e),
        )


def generate_from_segments(
    segments: List[Dict[str, Any]],
    output_dir: str,
    model: str = "speech-2.6-hd",
    stop_on_error: bool = True,
) -> Dict[str, Any]:
    """
    Generate audio for all segments in a list.

    Args:
        segments: List of validated segment dicts.
        output_dir: Directory for segment audio files.
        model: TTS model name.
        stop_on_error: If True, stop processing on first failure.

    Returns:
        Dict with keys: total, succeeded, failed, segments (list of SegmentInfo dicts).
    """
    os.makedirs(output_dir, exist_ok=True)

    results: List[Dict[str, Any]] = []
    succeeded = 0
    failed = 0

    for i, segment in enumerate(segments):
        print(f"  Generating segment {i + 1}/{len(segments)}: "
              f"{segment['text'][:40]}...")

        info = generate_segment_audio(segment, i, output_dir, model=model)

        if info.success:
            succeeded += 1
            print(f"    ✓ Saved: {info.audio_path}")
        else:
            failed += 1
            print(f"    ✗ Error: {info.error}")
            if stop_on_error:
                results.append(asdict(info))
                break

        results.append(asdict(info))

    return {
        "total": len(segments),
        "succeeded": succeeded,
        "failed": failed,
        "segments": results,
    }


def merge_segment_audio(
    segment_results: List[Dict[str, Any]],
    output_path: str,
    crossfade_ms: int = 0,
    normalize: bool = True,
) -> str:
    """
    Merge successfully generated segment audio files into a single file.

    Args:
        segment_results: List of segment result dicts (from generate_from_segments).
        output_path: Path for the merged output audio.
        crossfade_ms: Crossfade duration between segments in milliseconds.
        normalize: Whether to apply loudness normalization.

    Returns:
        Path to the merged audio file.

    Raises:
        ValueError: If no successful segments to merge.
        RuntimeError: If merging fails.
    """
    try:
        from .audio_processing import merge_audio_files
    except ImportError:
        from audio_processing import merge_audio_files

    audio_files = [
        seg["audio_path"]
        for seg in segment_results
        if seg.get("success") and seg.get("audio_path")
    ]

    if not audio_files:
        raise ValueError("No successful segments to merge")

    if len(audio_files) == 1:
        import shutil
        shutil.copy2(audio_files[0], output_path)
        return output_path

    output_format = Path(output_path).suffix.lstrip(".") or "mp3"

    return merge_audio_files(
        input_files=audio_files,
        output_path=output_path,
        format=output_format,
        crossfade_ms=crossfade_ms,
        normalize=normalize,
    )


def process_segments_to_audio(
    segments_file: str,
    output_path: str,
    output_dir: Optional[str] = None,
    model: str = "speech-2.6-hd",
    crossfade_ms: int = 0,
    normalize: bool = True,
    keep_temp_files: bool = False,
    stop_on_error: bool = True,
) -> Dict[str, Any]:
    """
    Complete pipeline: validate → generate → merge.

    Args:
        segments_file: Path to segments JSON file.
        output_path: Path for the final merged audio file.
        output_dir: Directory for intermediate segment files.
                    If None, a temporary directory is used.
        model: TTS model name.
        crossfade_ms: Crossfade duration between segments in milliseconds.
        normalize: Whether to apply loudness normalization.
        keep_temp_files: If True, keep intermediate segment audio files.
        stop_on_error: If True, stop on first segment generation failure.

    Returns:
        Dict with keys: success, output_path, segments_result, error.
    """
    # Validate
    validation = validate_segments_file(segments_file, model=model)
    if not validation.valid:
        return {
            "success": False,
            "output_path": None,
            "segments_result": None,
            "error": f"Validation failed: {'; '.join(validation.errors)}",
        }

    # Set up output directory — use tmp/ alongside output file
    use_temp = output_dir is None
    if use_temp:
        output_parent = os.path.dirname(os.path.abspath(output_path))
        output_dir = os.path.join(output_parent, "tmp")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Generate
        gen_result = generate_from_segments(
            segments=validation.segments,
            output_dir=output_dir,
            model=model,
            stop_on_error=stop_on_error,
        )

        if gen_result["succeeded"] == 0:
            return {
                "success": False,
                "output_path": None,
                "segments_result": gen_result,
                "error": "No segments were generated successfully",
            }

        # Merge
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        merged_path = merge_segment_audio(
            segment_results=gen_result["segments"],
            output_path=output_path,
            crossfade_ms=crossfade_ms,
            normalize=normalize,
        )

        return {
            "success": True,
            "output_path": merged_path,
            "segments_result": gen_result,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "output_path": None,
            "segments_result": None,
            "error": str(e),
        }

    finally:
        if use_temp and not keep_temp_files:
            import shutil
            try:
                shutil.rmtree(output_dir)
            except Exception:
                pass
