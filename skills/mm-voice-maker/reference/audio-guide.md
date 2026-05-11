# Audio Processing Guide

Process and optimize audio using FFmpeg-based tools.

## Contents

- [Format conversion](#format-conversion)
- [Merging audio](#merging-audio)
- [Normalization](#normalization)
- [Trimming and editing](#trimming-and-editing)
- [Optimization](#optimization)

---

## Format conversion

Convert between audio formats with custom parameters.

### Basic conversion

```python
from scripts import convert_audio

convert_audio(
    input_path="input.wav",
    output_path="output.mp3",
    target_format="mp3",
)
```

### With custom parameters

```python
convert_audio(
    input_path="input.wav",
    output_path="output.mp3",
    target_format="mp3",
    sample_rate=32000,    # Hz
    bitrate="192k",       # Higher quality
    channels=1,           # Mono
)
```

### Supported formats

```python
from scripts import SUPPORTED_FORMATS

# ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac', 'wma', 'opus', 'pcm']
```

---

## Merging audio

Concatenate multiple audio files with optional crossfades.

### How merge_audio_files works

**Primary path (filter_complex):**
1. Normalizes each input (resample to target sample rate if needed, convert to common format).
2. Concatenates all streams with the concat filter.
3. Optionally applies loudness normalization (loudnorm) and fade-in/fade-out.

**Advantages:**
- Handles inputs with different sample rates or channel layouts.
- Optional loudness normalization for consistent volume.
- Optional crossfade between segments.

**Fallback (concat demuxer):**
- If the filter chain fails (e.g. subtle format differences between segments), and `crossfade_ms==0`, the function falls back to the concat demuxer (`-f concat -c copy`).
- Fallback requires all inputs to have identical codec, sample rate, and channels (e.g. all from the same TTS pipeline).
- If you requested normalize or fades, a second FFmpeg pass is applied to the concatenated file.
- To disable fallback, call with `use_concat_fallback=False`.

### Basic merge

```python
from scripts import merge_audio_files

merge_audio_files(
    input_files=["part1.mp3", "part2.mp3", "part3.mp3"],
    output_path="complete.mp3",
    format="mp3",
)
```

### With crossfade and fades

```python
merge_audio_files(
    input_files=["intro.mp3", "main.mp3", "outro.mp3"],
    output_path="podcast.mp3",
    format="mp3",
    crossfade_ms=500,      # 0.5s crossfade between segments
    fade_in_ms=200,        # Fade in at start
    fade_out_ms=300,       # Fade out at end
    normalize=True,        # Normalize volume
)
```

### Simple concatenation (no crossfade)

```python
from scripts import concatenate_audio_files

concatenate_audio_files(
    input_files=["1.mp3", "2.mp3", "3.mp3"],
    output_path="concatenated.mp3",
    format="mp3",
)
```

---

## Normalization

Adjust audio loudness to target levels.

### Basic normalization

```python
from scripts import normalize_audio

normalize_audio(
    input_path="quiet.mp3",
    output_path="normalized.mp3",
)
```

### Custom loudness targets

```python
normalize_audio(
    input_path="audio.mp3",
    output_path="loud.mp3",
    target_loudness=-14.0,  # LUFS (louder than default -16)
    true_peak=-1.0,         # dB
    loudness_range=7.0,     # LU
)
```

### Volume adjustment

```python
from scripts import adjust_volume

# Increase by 6dB
adjust_volume("input.mp3", "louder.mp3", volume_db=6.0)

# Decrease to 50%
adjust_volume("input.mp3", "quieter.mp3", volume_factor=0.5)
```

---

## Trimming and editing

Extract portions or remove sections of audio.

### Trim to time range

```python
from scripts import trim_audio

trim_audio(
    input_path="long.mp3",
    output_path="clip.mp3",
    start_time=30,    # Start at 30s
    end_time=90,      # End at 90s (extracts 60s)
)
```

### With fades

```python
trim_audio(
    input_path="recording.mp3",
    output_path="clip.mp3",
    start_time=10,
    end_time=60,
    fade_in_ms=300,   # Smooth start
    fade_out_ms=500,  # Smooth end
)
```

### Remove silence

```python
from scripts import remove_silence

remove_silence(
    input_path="with_pauses.mp3",
    output_path="clean.mp3",
    threshold_db=-50,      # Silence threshold
    min_duration=0.5,      # Min silence duration to remove (seconds)
    keep_silence=0.2,      # Keep small pause (seconds)
)
```

---

## Optimization

Prepare audio for specific use cases.

### Optimize for speech

```python
from scripts import optimize_for_speech

optimize_for_speech(
    input_path="recording.wav",
    output_path="optimized.mp3",
    sample_rate=22050,     # Lower rate for speech
    channels=1,            # Mono
    normalize=True,
    remove_silence_threshold=-50,
)
```

### Audio info

```python
from scripts import probe_audio_file, AudioInfo

info = probe_audio_file("audio.mp3")
print(f"Duration: {info.duration}s")
print(f"Sample rate: {info.sample_rate} Hz")
print(f"Channels: {info.channels}")
print(f"Bitrate: {info.bitrate} bps")
print(f"Format: {info.format}")
print(f"Size: {info.file_size} bytes")
```

## Complete workflow: Audio production

```python
from scripts import (
    quick_tts,
    merge_audio_files,
    normalize_audio,
    trim_audio,
    optimize_for_speech,
)

# Step 1: Generate segments
segments = ["intro.mp3", "main.mp3", "outro.mp3"]
for i, text in enumerate(["Intro", "Main content", "Outro"]):
    quick_tts(text, "presenter_male", segments[i])

# Step 2: Merge with crossfades
merge_audio_files(
    input_files=segments,
    output_path="raw_podcast.mp3",
    crossfade_ms=500,
    normalize=True,
)

# Step 3: Remove silence
remove_silence("raw_podcast.mp3", "trimmed.mp3")

# Step 4: Optimize
optimize_for_speech(
    "trimmed.mp3",
    "final_podcast.mp3",
    sample_rate=22050,
    channels=1,
)

print("Production complete: final_podcast.mp3")
```

## FFmpeg requirements

```python
from scripts import check_ffmpeg_installed, get_ffmpeg_path

# Check if installed
if not check_ffmpeg_installed():
    print("Install FFmpeg:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu: sudo apt install ffmpeg")
    print("  Windows: https://ffmpeg.org/download.html")
else:
    path = get_ffmpeg_path()
    print(f"FFmpeg: {path}")
```

## Best practices

- **Always normalize**: After merging, normalize to consistent loudness
- **Use crossfades**: Smooth transitions between segments (300-500ms)
- **Remove silence**: Clean up recordings before merging
- **Sample rate**: 32000 for TTS output, 22050-44100 for final production
- **Test first**: Run on small sample before batch processing

## Error handling

```python
from scripts import merge_audio_files

try:
    merge_audio_files(["a.mp3", "b.mp3"], "merged.mp3")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except RuntimeError as e:
    print(f"FFmpeg error: {e}")
```

## See also

- **API reference**: [api_documentation.md](api_documentation.md#audio-processing)
- **TTS workflows**: [tts-guide.md](tts-guide.md#multi-segment-production)
- **Emotion workflows**: [emotion-guide.md](emotion-guide.md)
