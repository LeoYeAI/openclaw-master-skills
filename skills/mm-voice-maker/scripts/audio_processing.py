"""
Audio Processing Module - FFmpeg-based Audio Manipulation
Provides comprehensive audio processing capabilities for voice synthesis workflows

Capabilities:
- Format conversion (mp3, wav, flac, ogg, m4a, etc.)
- Audio merging and concatenation
- Audio post-processing (normalization, trimming, silence removal)
- Audio analysis (duration, format, sample rate detection)

Requirements:
- ffmpeg: https://ffmpeg.org/download.html
- python bindings: pip install ffmpeg-python
"""

import os
import shutil
import subprocess
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# Configuration and Constants
# ============================================================================

SUPPORTED_FORMATS = {
    "mp3": "MP3 (MPEG Audio Layer 3)",
    "wav": "WAV (Waveform Audio File Format)",
    "flac": "FLAC (Free Lossless Audio Codec)",
    "ogg": "OGG (Ogg Vorbis)",
    "m4a": "M4A (MPEG-4 Audio)",
    "aac": "AAC (Advanced Audio Coding)",
    "wma": "WMA (Windows Media Audio)",
    "opus": "OPUS (Opus Audio Codec)",
}

@dataclass
class AudioInfo:
    """Audio file metadata"""
    path: str
    format: str
    duration: float
    sample_rate: int
    channels: int
    bitrate: Optional[int]
    file_size: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "format": self.format,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bitrate": self.bitrate,
            "file_size": self.file_size,
        }


# ============================================================================
# Utility Functions
# ============================================================================

def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is installed and accessible"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_ffmpeg_path() -> Optional[str]:
    """Get ffmpeg executable path"""
    try:
        result = subprocess.run(
            ["which", "ffmpeg"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def run_ffmpeg_command(args: List[str], timeout: int = 300) -> bool:
    """Execute ffmpeg command with given arguments"""
    try:
        result = subprocess.run(
            ["ffmpeg"] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"FFmpeg command timed out after {timeout} seconds")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg first.")


def probe_audio_file(file_path: str) -> AudioInfo:
    """
    Probe audio file and extract metadata using ffprobe

    Args:
        file_path: Path to audio file

    Returns:
        AudioInfo object with file metadata

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If ffprobe fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        # Use ffprobe to get format info
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {result.stderr}")

        import json
        data = json.loads(result.stdout)

        # Extract audio stream info
        audio_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break

        if not audio_stream:
            raise RuntimeError("No audio stream found in file")

        format_info = data.get("format", {})

        # Determine format from filename
        ext = Path(file_path).suffix[1:].lower() if Path(file_path).suffix else "unknown"

        return AudioInfo(
            path=file_path,
            format=ext,
            duration=float(format_info.get("duration", 0)),
            sample_rate=int(audio_stream.get("sample_rate", 44100)),
            channels=int(audio_stream.get("channels", 2)),
            bitrate=int(format_info.get("bit_rate", 0)) if format_info.get("bit_rate") else None,
            file_size=int(format_info.get("size", 0)),
        )

    except Exception as e:
        raise RuntimeError(f"Failed to probe audio file: {e}")


# ============================================================================
# Audio Format Conversion
# ============================================================================

def convert_audio(
    input_path: str,
    output_path: str,
    target_format: str = "mp3",
    sample_rate: Optional[int] = None,
    bitrate: Optional[str] = None,
    channels: Optional[int] = None,
    codec: Optional[str] = None,
    overwrite: bool = True,
) -> str:
    """
    Convert audio file to different format

    Args:
        input_path: Input audio file path
        output_path: Output file path
        target_format: Target format (mp3, wav, flac, etc.)
        sample_rate: Target sample rate (e.g., 16000, 44100, 48000)
        bitrate: Target bitrate (e.g., "128k", "192k", "320k")
        channels: Number of audio channels (1 for mono, 2 for stereo)
        codec: Audio codec (overrides format-specific default)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to converted audio file

    Example:
        >>> convert_audio("input.wav", "output.mp3", bitrate="192k", sample_rate=44100)
        'output.mp3'

        >>> # Convert to WAV with specific parameters
        >>> convert_audio("input.mp3", "output.wav", sample_rate=16000, channels=1)
        'output.wav'
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    args = []

    if overwrite:
        args.extend(["-y"])  # Overwrite output

    # Input file
    args.extend(["-i", input_path])

    # Audio codec
    if codec:
        args.extend(["-acodec", codec])
    else:
        # Use format-specific defaults
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "flac": "flac",
            "ogg": "libvorbis",
            "aac": "aac",
            "m4a": "aac",
        }
        args.extend(["-acodec", codec_map.get(target_format, "copy")])

    # Sample rate
    if sample_rate:
        args.extend(["-ar", str(sample_rate)])

    # Channels
    if channels:
        args.extend(["-ac", str(channels)])

    # Bitrate
    if bitrate:
        args.extend(["-b:a", bitrate])

    # Output file
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError(f"Audio conversion failed for: {input_path}")

    return output_path


def convert_audio_simple(
    input_path: str,
    target_format: str,
    output_dir: Optional[str] = None,
) -> str:
    """
    Simple audio format conversion with automatic output naming

    Args:
        input_path: Input audio file path
        target_format: Target format (mp3, wav, flac, etc.)
        output_dir: Output directory (defaults to input file directory)

    Returns:
        Path to converted audio file

    Example:
        >>> convert_audio_simple("input.wav", "mp3")
        '/path/to/input.mp3'
    """
    input_path = Path(input_path)

    if output_dir:
        output_path = Path(output_dir) / input_path.stem
    else:
        output_path = input_path.parent / input_path.stem

    output_path = output_path.with_suffix(f".{target_format}")

    return convert_audio(
        input_path=str(input_path),
        output_path=str(output_path),
        target_format=target_format,
    )


# ============================================================================
# Audio Merging and Concatenation
# ============================================================================

def _concat_demuxer(
    input_files: List[str],
    output_path: str,
    overwrite: bool = True,
) -> bool:
    """
    Concatenate audio files using FFmpeg concat demuxer (no re-encoding).
    Requires all inputs to have identical codec, sample rate, and channel layout.
    Returns True on success, False on failure (e.g. format mismatch).
    """
    if not input_files:
        return False
    args = []
    if overwrite:
        args.extend(["-y"])
    concat_content = ""
    for f in input_files:
        if not os.path.exists(f):
            return False
        abs_path = os.path.abspath(f)
        concat_content += f"file '{abs_path}'\n"
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(concat_content)
            concat_file = f.name
        try:
            args.extend(["-f", "concat", "-safe", "0", "-i", concat_file])
            args.extend(["-c", "copy"])
            args.append(output_path)
            return run_ffmpeg_command(args)
        finally:
            os.unlink(concat_file)
    except Exception:
        return False


def merge_audio_files(
    input_files: List[str],
    output_path: str,
    format: str = "mp3",
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None,
    fade_in_ms: int = 0,
    fade_out_ms: int = 0,
    crossfade_ms: int = 0,
    normalize: bool = True,
    overwrite: bool = True,
    use_concat_fallback: bool = True,
) -> str:
    """
    Merge multiple audio files into a single file.

    **How it works:**
    Uses FFmpeg filter_complex to:
    1. Normalize each input stream (resample to target sample_rate if needed,
       convert to mono and a common sample format).
    2. Concatenate all streams:
       - With crossfade: use acrossfade for smooth transitions between segments
       - Without crossfade: use concat filter for simple concatenation
    3. Optionally apply loudness normalization (loudnorm) and/or global
       fade-in/fade-out.

    **Crossfade implementation:**
    - When crossfade_ms > 0: uses acrossfade filter for smooth transitions
    - Crossfade duration: configurable (recommended: 100-500ms)
    - Fallback disabled when crossfade enabled (acrossfade requires re-encoding)

    **Fallback (when primary fails):**
    If the filter_complex chain fails and use_concat_fallback is True
    and crossfade_ms is 0, the function falls back to the concat demuxer:
    - Writes a concat list and uses ``-f concat -c copy`` (no re-encoding).
    - Requires all inputs to have identical codec, sample rate, and channels;
      best when all segments are from the same TTS pipeline.
    - If normalize or fades were requested, a second FFmpeg pass is applied
      to the concatenated file.

    Args:
        input_files: List of input audio file paths.
        output_path: Output file path.
        format: Output audio format (mp3, wav, flac, ogg).
        sample_rate: Target sample rate (default: first file's rate).
        channels: Target channels (default: first file's channels).
        fade_in_ms: Fade-in duration in milliseconds at start.
        fade_out_ms: Fade-out duration in milliseconds at end.
        crossfade_ms: Crossfade duration between files in milliseconds (0 = none).
        normalize: Whether to apply loudness normalization.
        overwrite: Whether to overwrite existing output file.
        use_concat_fallback: If True, on filter_complex failure and when
            crossfade_ms==0, try concat demuxer (no re-encode).

    Returns:
        Path to the merged audio file.

    Raises:
        ValueError: If input_files is empty.
        FileNotFoundError: If any input file is missing.
        RuntimeError: If both primary and fallback merging fail.
    """
    if not input_files:
        raise ValueError("No input files provided")

    for f in input_files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Input file not found: {f}")

    # Get info from first file
    first_info = probe_audio_file(input_files[0])
    sample_rate = sample_rate or first_info.sample_rate
    channels = channels or first_info.channels

    args = []

    if overwrite:
        args.extend(["-y"])

    # Build filter complex
    filter_parts = []
    
    # Add all input files
    for i, input_file in enumerate(input_files):
        args.extend(["-i", input_file])
    
    # Process each input stream
    for i in range(len(input_files)):
        # Standardize each stream: resample and convert to mono
        filter_parts.append(
            f"[{i}:a]aresample={sample_rate},aformat=sample_fmts=fltp:channel_layouts=mono[stream{i}]"
        )

    # Build concatenation or crossfade chain
    if crossfade_ms > 0 and len(input_files) >= 2:
        # Use acrossfade for smooth transitions between segments
        # Format: [stream0][stream1]acrossfade=d={crossfade_ms}[merged0];[merged0][stream2]acrossfade=d={crossfade_ms}[merged1]...
        
        crossfade_seconds = crossfade_ms / 1000.0
        merged_streams = []
        
        for i in range(len(input_files)):
            if i == 0:
                # First stream: add fade in if needed
                if fade_in_ms > 0:
                    filter_parts.append(
                        f"[stream{i}]afade=t=in:ss=0:d={fade_in_ms/1000.0}[stream{i}]"
                    )
                else:
                    filter_parts.append(f"[stream{i}][stream{i}]")
            elif i == len(input_files) - 1:
                # Last stream: add fade out if needed
                if fade_out_ms > 0:
                    filter_parts.append(
                        f"[merged{i-1}]afade=t=out:st=0:d={fade_out_ms/1000.0}[stream{i}]"
                    )
                else:
                    filter_parts.append(f"[merged{i-1}][stream{i}]")
            else:
                # Middle streams: just acrossfade
                filter_parts.append(f"[merged{i-1}][stream{i}]")
            
            # Apply acrossfade between streams
            if i > 0:
                filter_parts.append(
                    f"acrossfade=d={crossfade_seconds}[merged{i}]"
                )
        
        # Final output chain
        filter_chain = "[merged{}]".format(len(input_files) - 1)
        
    else:
        # Simple concatenation without crossfade
        concat_inputs = ''.join([f'[stream{i}]' for i in range(len(input_files))])
        filter_parts.append(f"{concat_inputs}concat=n={len(input_files)}:v=0:a=1[merged]")
        
        # Build filter chain for merged output
        filter_chain = "[merged]"
        
        # Apply fades to merged output
        if fade_in_ms > 0:
            filter_chain += f"afade=t=in:ss=0:d={fade_in_ms/1000.0}"
        if fade_out_ms > 0:
            fade_out_start = ""
            if fade_in_ms > 0:
                filter_chain += ","
            filter_chain += f"afade=t=out:st=0:d={fade_out_ms/1000.0}"

    # Add normalization if requested
    if normalize:
        fade_sep = "," if (fade_in_ms > 0 or fade_out_ms > 0 or crossfade_ms > 0) else ""
        filter_chain += f"{fade_sep}loudnorm=I=-16:TP=-1.5:LRA=11"

    filter_chain += "[final]"

    # Combine all filter parts
    full_filter = ";".join(filter_parts) + ";" + filter_chain
    args.extend(["-filter_complex", full_filter])
    args.extend(["-map", "[final]"])
    args.extend(["-ar", str(sample_rate)])
    args.extend(["-ac", str(channels)])

    codec_map = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "flac": "flac",
        "ogg": "libvorbis",
    }
    args.extend(["-acodec", codec_map.get(format, "copy")])
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success and use_concat_fallback and crossfade_ms == 0:
        # Fallback: concat demuxer (no re-encode); then optional normalize/fades
        ext = f".{format}" if format else ".mp3"
        try:
            fd = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            temp_path = fd.name
            fd.close()
        except Exception:
            raise RuntimeError(
                "Audio merging failed (filter_complex path). "
                "Fallback not attempted (could not create temp file)."
            )
        try:
            if not _concat_demuxer(input_files, temp_path, overwrite=True):
                raise RuntimeError(
                    "Audio merging failed (filter_complex path). "
                    "Fallback concat demuxer also failed (inputs may have different formats)."
                )
            if normalize or fade_in_ms > 0 or fade_out_ms > 0:
                # Second pass: normalize and/or fades
                pass_args = []
                if overwrite:
                    pass_args.extend(["-y"])
                pass_args.extend(["-i", temp_path])
                af_parts = []
                if normalize:
                    af_parts.append("loudnorm=I=-16:TP=-1.5:LRA=11")
                if fade_in_ms > 0:
                    af_parts.append(f"afade=t=in:ss=0:d={fade_in_ms/1000.0}")
                if fade_out_ms > 0:
                    # fade_out needs duration; get from probe
                    try:
                        info = probe_audio_file(temp_path)
                        st = max(0, info.duration - fade_out_ms / 1000.0)
                        af_parts.append(
                            f"afade=t=out:st={st}:d={fade_out_ms/1000.0}"
                        )
                    except Exception:
                        af_parts.append(
                            f"afade=t=out:st=0:d={fade_out_ms/1000.0}"
                        )
                pass_args.extend(["-af", ",".join(af_parts)])
                pass_args.append(output_path)
                if not run_ffmpeg_command(pass_args):
                    raise RuntimeError(
                        "Audio merging fallback (concat demuxer) succeeded, "
                        "but post-processing (normalize/fades) failed."
                    )
            else:
                shutil.move(temp_path, output_path)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
        return output_path

    if not success:
        # Provide specific error message based on why fallback was not used
        if crossfade_ms != 0:
            raise RuntimeError(
                f"Audio merging failed with crossfade (crossfade_ms={crossfade_ms}). "
                "Possible causes: incompatible audio formats, insufficient audio length for crossfade. "
                "Try reducing crossfade duration, or set crossfade_ms=0 to use simple concatenation."
            )
        elif not use_concat_fallback:
            raise RuntimeError(
                "Audio merging failed (filter_complex path). "
                "use_concat_fallback is False, so fallback was disabled. "
                "Set use_concat_fallback=True to try concat demuxer when filter_complex fails."
            )
        else:
            raise RuntimeError(
                "Audio merging failed. If segments have different formats, "
                "ensure they share codec/sample_rate/channels or use merge_audio_files "
                "with use_concat_fallback=True and crossfade_ms=0 for same-format inputs."
            )

    return output_path


def concatenate_audio_files(
    input_files: List[str],
    output_path: str,
    format: str = "mp3",
    crossfade_ms: int = 0,
    overwrite: bool = True,
) -> str:
    """
    Concatenate audio files without re-encoding (faster)

    Note: This method requires all input files to have same format and parameters

    Args:
        input_files: List of input audio file paths
        output_path: Output file path
        format: Output format
        crossfade_ms: Crossfade duration in milliseconds (requires re-encoding)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to concatenated audio file
    """
    if not input_files:
        raise ValueError("No input files provided")

    # For simple concatenation without crossfade, use concat demuxer
    if crossfade_ms == 0:
        args = []

        if overwrite:
            args.extend(["-y"])

        # Create concat file
        concat_content = ""
        for f in input_files:
            abs_path = os.path.abspath(f)
            concat_content += f"file '{abs_path}'\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(concat_content)
            concat_file = f.name

        try:
            args.extend(["-f", "concat", "-safe", "0", "-i", concat_file])
            args.extend(["-c", "copy"])
            args.append(output_path)

            success = run_ffmpeg_command(args)

            if not success:
                raise RuntimeError("Audio concatenation failed")

        finally:
            os.unlink(concat_file)

    else:
        # With crossfade requires full re-encoding
        return merge_audio_files(
            input_files=input_files,
            output_path=output_path,
            format=format,
            crossfade_ms=crossfade_ms,
            overwrite=overwrite,
        )

    return output_path


# ============================================================================
# Audio Post-Processing
# ============================================================================

def normalize_audio(
    input_path: str,
    output_path: str,
    target_loudness: float = -16.0,
    true_peak: float = -1.5,
    loudness_range: float = 11.0,
    overwrite: bool = True,
) -> str:
    """
    Normalize audio to target loudness using EBU R128 standard

    Args:
        input_path: Input audio file path
        output_path: Output file path
        target_loudness: Target integrated loudness in LUFS (default: -16)
        true_peak: Maximum true peak level in dBTP (default: -1.5)
        loudness_range: Target loudness range in LU (default: 11)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to normalized audio file

    Example:
        >>> normalize_audio("quiet.mp3", "normalized.mp3")
        'normalized.mp3'
    """
    args = []

    if overwrite:
        args.extend(["-y"])

    args.extend(["-i", input_path])
    args.extend([
        "-af", f"loudnorm=I={target_loudness}:TP={true_peak}:LRA={loudness_range}"
    ])

    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Audio normalization failed")

    return output_path


def adjust_volume(
    input_path: str,
    output_path: str,
    volume_db: float = 0.0,
    volume_factor: float = 1.0,
    overwrite: bool = True,
) -> str:
    """
    Adjust audio volume

    Args:
        input_path: Input audio file path
        output_path: Output file path
        volume_db: Volume adjustment in decibels (positive for louder, negative for quieter)
        volume_factor: Volume multiplier (e.g., 0.5 for half volume, 2.0 for double)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to adjusted audio file

    Example:
        >>> adjust_volume("quiet.mp3", "louder.mp3", volume_db=6.0)  # 6dB louder
        'louder.mp3'
    """
    args = []

    if overwrite:
        args.extend(["-y"])

    args.extend(["-i", input_path])

    # Use volume filter
    volume_filter = f"volume={volume_factor}"
    if volume_db != 0:
        import math
        factor = 10 ** (volume_db / 20)
        volume_filter = f"volume={factor}"

    args.extend(["-af", volume_filter])

    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Volume adjustment failed")

    return output_path


def trim_audio(
    input_path: str,
    output_path: str,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    fade_in_ms: int = 0,
    fade_out_ms: int = 0,
    overwrite: bool = True,
) -> str:
    """
    Trim audio file to specified time range

    Args:
        input_path: Input audio file path
        output_path: Output file path
        start_time: Start time in seconds
        end_time: End time in seconds (None for till end)
        fade_in_ms: Fade in duration in milliseconds
        fade_out_ms: Fade out duration in milliseconds
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to trimmed audio file

    Example:
        >>> trim_audio("long.mp3", "clip.mp3", start_time=30.0, end_time=90.0)
        'clip.mp3'
    """
    args = []

    if overwrite:
        args.extend(["-y"])

    args.extend(["-i", input_path])

    # Build trim filter
    if end_time is not None:
        trim_filter = f"atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS"
    else:
        trim_filter = f"atrim=start={start_time},asetpts=PTS-STARTPTS"

    # Add fades if specified
    if fade_in_ms > 0 or fade_out_ms > 0:
        duration = end_time - start_time if end_time else None
        if fade_in_ms > 0:
            trim_filter += f",afade=t=in:ss=0:d={fade_in_ms/1000}"
        if fade_out_ms > 0 and duration:
            trim_filter += f",afade=t=out:st={duration - fade_out_ms/1000}:d={fade_out_ms/1000}"

    args.extend(["-af", trim_filter])
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Audio trimming failed")

    return output_path


def remove_silence(
    input_path: str,
    output_path: str,
    threshold_db: float = -50,
    min_duration: float = 0.5,
    keep_silence: float = 0.2,
    overwrite: bool = True,
) -> str:
    """
    Remove silence from audio

    Args:
        input_path: Input audio file path
        output_path: Output file path
        threshold_db: Silence threshold in dB (default: -50)
        min_duration: Minimum silence duration to remove in seconds (default: 0.5)
        keep_silence: Amount of silence to keep at boundaries in seconds (default: 0.2)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to processed audio file

    Example:
        >>> remove_silence("with_silence.mp3", "clean.mp3", threshold_db=-40)
        'clean.mp3'
    """
    args = []

    if overwrite:
        args.extend(["-y"])

    args.extend(["-i", input_path])

    silrem_filter = (
        f"silenceremove=threshold={threshold_db}:"
        f"stop_duration={min_duration}:"
        f"leave_silence={keep_silence}"
    )

    args.extend(["-af", silrem_filter])
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Silence removal failed")

    return output_path


def apply_effects(
    input_path: str,
    output_path: str,
    effects: Dict[str, Any],
    overwrite: bool = True,
) -> str:
    """
    Apply audio effects using FFmpeg filter graph

    Args:
        input_path: Input audio file path
        output_path: Output file path
        effects: Dictionary of effects to apply
            Supported effects:
            - reverb: Reverb effect (wet, room_size, damping)
            - echo: Echo effect (decay)
            - phaser: Phaser effect (rate, depth)
            - treble: Treble adjustment (gain)
            - bass: Bass adjustment (gain)
            - highpass: High-pass filter (frequency)
            - lowpass: Low-pass filter (frequency)
        overwrite: Whether to overwrite existing output file

    Returns:
        Path to processed audio file

    Example:
        >>> apply_effects("dry.mp3", "reverbed.mp3", {
        ...     "reverb": {"wet": 0.3, "room_size": 0.5}
        ... })
        'reverbed.mp3'
    """
    args = []

    if overwrite:
        args.extend(["-y"])

    args.extend(["-i", input_path])

    # Build filter chain
    filters = []

    if "reverb" in effects:
        params = effects["reverb"]
        wet = params.get("wet", 0.3)
        room = params.get("room_size", 0.5)
        damping = params.get("damping", 0.5)
        filters.append(f"reverb=wetness={wet}:roomsize={room}:damping={damping}")

    if "echo" in effects:
        params = effects["echo"]
        decay = params.get("decay", 0.5)
        filters.append(f"aecho=decay={decay}")

    if "phaser" in effects:
        params = effects["phaser"]
        rate = params.get("rate", 0.5)
        depth = params.get("depth", 0.5)
        filters.append(f"phaser=rate={rate}:depth={depth}")

    if "treble" in effects:
        filters.append(f"treble=gain={effects['treble']}")

    if "bass" in effects:
        filters.append(f"bass=gain={effects['bass']}")

    if "highpass" in effects:
        filters.append(f"highpass=f={effects['highpass']}")

    if "lowpass" in effects:
        filters.append(f"lowpass=f={effects['lowpass']}")

    if not filters:
        raise ValueError("No valid effects specified")

    args.extend(["-af", ",".join(filters)])
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Effect application failed")

    return output_path


# ============================================================================
# High-Level Convenience Functions
# ============================================================================

def optimize_for_speech(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 22050,
    channels: int = 1,
    normalize: bool = True,
    remove_silence_threshold: float = -50,
) -> str:
    """
    Optimize audio for speech/voice content

    This is a convenience function that applies common optimizations:
    - Resampling to specified sample rate
    - Mono conversion
    - Loudness normalization
    - Optional silence removal

    Args:
        input_path: Input audio file path
        output_path: Output file path (auto-generated if None)
        sample_rate: Target sample rate (default: 22050)
        channels: Target channels, 1 for mono (default: 1)
        normalize: Whether to normalize loudness (default: True)
        remove_silence_threshold: Silence threshold in dB, None to skip

    Returns:
        Path to optimized audio file
    """
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_optimized.wav")

    args = []
    args.extend(["-y"])
    args.extend(["-i", input_path])

    filters = []

    # Resample
    filters.append(f"aresample={sample_rate}")

    # Convert to mono
    if channels == 1:
        filters.append("aformat=channel_layouts=mono")

    # Normalize
    if normalize:
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    # Remove silence
    if remove_silence_threshold is not None:
        filters.append(
            f"silenceremove=threshold={remove_silence_threshold}:"
            f"stop_duration=0.5:leave_silence=0.2"
        )

    args.extend(["-af", ",".join(filters)])
    args.append(output_path)

    success = run_ffmpeg_command(args)

    if not success:
        raise RuntimeError("Audio optimization failed")

    return output_path


def create_audio_from_segments(
    segments: List[Dict[str, Any]],
    output_path: str,
    format: str = "mp3",
    crossfade_ms: int = 500,
    normalize: bool = True,
) -> str:
    """
    Create audio from text segments using TTS, then merge

    This is a high-level function that integrates with TTS synthesis:
    1. Generate audio for each text segment
    2. Optionally apply voice settings per segment
    3. Merge with crossfades
    4. Apply post-processing

    Args:
        segments: List of segment dictionaries:
            - text: Text to synthesize
            - voice_id: Voice ID for this segment
            - output_path: Temporary output path for segment
            - tts_function: Function to call for TTS synthesis
        output_path: Final output file path
        format: Output format
        crossfade_ms: Crossfade duration in milliseconds
        normalize: Whether to normalize final audio

    Returns:
        Path to final audio file
    """
    temp_files = []

    try:
        # Generate audio for each segment
        for i, segment in enumerate(segments):
            text = segment.get("text")
            voice_id = segment.get("voice_id")
            tts_func = segment.get("tts_function")
            temp_path = segment.get("output_path", f"/tmp/segment_{i}.mp3")

            if tts_func and text:
                tts_func(text=text, voice_id=voice_id, output_path=temp_path)
                temp_files.append(temp_path)

        # Merge all segments
        if len(temp_files) == 1:
            # No merging needed, just convert
            return convert_audio(temp_files[0], output_path, format=format)
        elif len(temp_files) > 1:
            return merge_audio_files(
                input_files=temp_files,
                output_path=output_path,
                format=format,
                crossfade_ms=crossfade_ms,
                normalize=normalize,
            )
        else:
            raise ValueError("No segments to process")

    finally:
        # Cleanup temp files
        for f in temp_files:
            if os.path.exists(f):
                os.unlink(f)
