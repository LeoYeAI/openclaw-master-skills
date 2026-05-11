# MiniMax Voice API Complete Reference

## Table of Contents

1. [Configuration](#configuration)
2. [Synchronous TTS](#synchronous-tts)
3. [Asynchronous TTS](#asynchronous-tts)
4. [Emotion Parameter](#emotion-parameter)
5. [Segment-based TTS](#segment-based-tts)
6. [Voice Cloning](#voice-cloning)
7. [Voice Design](#voice-design)
8. [Voice Management](#voice-management)
9. [Audio Processing](#audio-processing)
10. [Common Parameters](#common-parameters)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)

---

## Configuration

### Environment Setup

```bash
# Set API key
export MINIMAX_VOICE_API_KEY="your-api-key-here"

# Optional: Custom API base URL
export MINIMAX_API_BASE="https://api.minimaxi.com/v1"
```

### Supported Models

```python
from scripts import AVAILABLE_MODELS

AVAILABLE_MODELS = [
    "speech-2.8-hd", # Latest HD model, accurately reproduces authentic tone details, significantly improves voice similarity (recommended)
    "speech-2.8-turbo", # Latest Turbo model, fast model, accurately reproduces authentic tone details, significantly improves voice similarity
    "speech-2.6-hd",      # HD model, excellent prosody, ultimate sound quality and prosody performance, faster and more natural generation
    "speech-2.6-turbo",   # Turbo model, excellent sound quality, ultra-low latency, more responsive
    "speech-02-hd",       # HD model
    "speech-02-turbo",    # Fast model
    "speech-01-hd",       # Legacy HD model
    "speech-01-turbo",    # Legacy fast model
]

# IMPORTANT: Model names use hyphens (-), not underscores (_)
# Wrong: "speech_02", "speech_2.8_hd"
# Correct: "speech-02-hd", "speech-2.8-hd"
```

**Model Selection Guide:**
- `speech-2.8-hd`: Latest HD model, best voice similarity and tone detail (recommended for highest quality)
- `speech-2.8-turbo`: Latest Turbo model, fast with excellent quality
- `speech-2.6-hd`: HD model, excellent prosody and natural generation
- `speech-2.6-turbo`: Turbo model, fast processing with good quality
- `speech-02-hd`: HD model
- `speech-02-turbo`: Fast model
- `speech-01-hd`: Legacy HD model
- `speech-01-turbo`: Legacy fast model

### Audio Formats

```python
from scripts import AUDIO_FORMATS

AUDIO_FORMATS = ["mp3", "wav", "flac", "pcm"]
```

### Supported Languages

```python
from scripts import SUPPORTED_LANGUAGES

SUPPORTED_LANGUAGES = [
    "Chinese", "Chinese,Yue", "English", "Arabic", "Russian", "Spanish",
    "French", "Portuguese", "German", "Turkish", "Dutch", "Ukrainian",
    "Vietnamese", "Indonesian", "Japanese", "Italian", "Korean", "Thai",
    "Polish", "Romanian", "Greek", "Czech", "Finnish", "Hindi", "Bulgarian",
    "Danish", "Hebrew", "Malay", "Persian", "Slovak", "Swedish", "Croatian",
    "Filipino", "Hungarian", "Norwegian", "Slovenian", "Catalan", "Nynorsk",
    "Tamil", "Afrikaans", "auto"
]
```

---

## Synchronous TTS

### HTTP Synthesis

```python
from scripts import synthesize_speech_http, VoiceSetting, AudioSetting

result = synthesize_speech_http(
    text: str,                              # Text to synthesize (max 10,000 chars)
    model: str = "speech-2.8-hd",           # Model version
    voice_setting: Optional[VoiceSetting],  # Voice parameters
    audio_setting: Optional[AudioSetting],  # Audio output parameters
    stream: bool = False,                   # Enable streaming output
    pronunciation_dict: Optional[Dict],     # Custom pronunciation dictionary
    timber_weights: Optional[List],         # Voice mixing weights
    language_boost: Optional[str],          # Language enhancement
    voice_modify: Optional[Dict],           # Voice effect parameters
    subtitle_enable: bool = False,          # Generate subtitles
    output_format: str = "hex",             # Output format: "hex" or "url"
    aigc_watermark: bool = False,           # Add AI watermark
    timeout: int = 120,                     # Request timeout in seconds
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "data": {
        "audio": "hex-encoded-audio-data",  # or "url": "download-url"
        "status": 0
    },
    "extra_info": {
        "duration": 12.5,                   # Audio duration in seconds
        "sample_rate": 32000,               # Sample rate
        "size": 102400,                     # File size in bytes
    },
    "trace_id": "session-id-string"
}
```

### Streaming Synthesis

```python
from scripts import synthesize_speech_http_stream

# Generator that yields audio chunks
chunks = synthesize_speech_http_stream(
    text: str,
    model: str = "speech-2.8-hd",
    voice_setting: Optional[VoiceSetting],
    audio_setting: Optional[AudioSetting],
    **kwargs  # Other parameters from synthesize_speech_http
) -> Generator[bytes, None, None]
```

**Usage:**
```python
audio_chunks = []
for chunk in synthesize_speech_http_stream("Long text..."):
    audio_chunks.append(chunk)

audio_data = b"".join(audio_chunks)
```

### WebSocket Streaming

```python
from scripts import synthesize_speech_websocket

audio_bytes = await synthesize_speech_websocket(
    text_segments: List[str],              # List of text segments
    model: str = "speech-2.8-hd",          # Model version
    voice_setting: Optional[VoiceSetting], # Voice parameters
    audio_setting: Optional[AudioSetting], # Audio output parameters
    pronunciation_dict: Optional[Dict],    # Custom pronunciation
    language_boost: Optional[str],         # Language enhancement
) -> bytes
```

### Quick Synthesis

```python
from scripts import quick_tts

audio_bytes = quick_tts(
    text: str,                    # Text to synthesize
    voice_id: str = "male-qn-qingse",  # Voice ID
    output_path: Optional[str] = None,  # Save to file path (optional)
    **kwargs                    # Other parameters
) -> bytes  # Always returns audio bytes
```

**Return value**: `bytes` - Audio data as bytes

**Side effect**: If `output_path` is specified, also saves audio to that file

**Example**:
```python
# Get bytes only
audio = quick_tts("Hello world", voice_id="male-qn-qingse")

# Get bytes AND save to file
audio = quick_tts("Hello world", output_path="hello.mp3")
```

### Pause Markers

Insert pauses in text using `<#x#>` format:

```python
text = "Hello<#1.5#>1.5 second pause<#0.5#>continue"
# Result: "Hello [1.5s pause] 1.5 second pause [0.5s pause] continue"
```

**Parameters:**
- x: Pause duration in seconds
- Range: 0.01 to 99.99 seconds

---

## Asynchronous TTS

### Create Task

```python
from scripts import create_async_tts_task

result = create_async_tts_task(
    model: str = "speech-2.8-hd",
    text: Optional[str],                  # Text to synthesize (max 1M chars)
    text_file_id: Optional[str],          # Uploaded file ID (alternative to text)
    voice_setting: Optional[VoiceSetting],
    audio_setting: Optional[AudioSetting],
    pronunciation_dict: Optional[Dict],
    timber_weights: Optional[List],
    language_boost: Optional[str],
    voice_modify: Optional[Dict],
    subtitle_enable: bool = False,
    aigc_watermark: bool = False,
    timeout: int = 60,
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "task_id": "task-id-string",
    "file_id": "file-id-string",          # Available after completion
    "base_resp": {"status_code": 0},
    "trace_id": "trace-id-string"
}
```

### Query Task Status

```python
from scripts import query_async_tts_task

result = query_async_tts_task(
    task_id: str,
    timeout: int = 30,
) -> Dict[str, Any]
```

**Status Values:**
- `"processing"`: Task is being processed
- `"success"`: Task completed successfully
- `"failed"`: Task failed
- `"expired"`: Task expired

**Success Response:**
```python
{
    "status": "success",
    "file": {
        "file_id": "file-id",
        "download_url": "https://...",
        "expires_at": "2024-01-01T00:00:00Z",  # ~9 hours validity
    },
    "extra_info": {
        "duration": 125.5,
        "sample_rate": 32000,
        "size": 1024000,
    }
}
```

### Wait for Completion

```python
from scripts import wait_for_task

result = wait_for_task(
    task_id: str,
    polling_interval: float = 5.0,         # Seconds between status checks
    max_wait_time: float = 3600,           # Maximum wait time (1 hour default)
    on_status_change: Optional[callable],  # Callback(status, result)
) -> Dict[str, Any]
```

### Complete Flow

```python
from scripts import async_tts_full_flow

result = async_tts_full_flow(
    text: str,
    model: str = "speech-2.8-hd",
    voice_setting: Optional[VoiceSetting],
    audio_setting: Optional[AudioSetting],
    output_path: Optional[str],            # Auto-download to file
    polling_interval: float = 5.0,
    max_wait_time: float = 3600,
    **kwargs,
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "task_id": "task-id",
    "status": "success",
    "audio_url": "https://download-url",
    "output_path": "/path/to/file.mp3",     # If output_path specified
    "extra_info": {...},
}
```

---

## Emotion Parameter

The `emotion` parameter controls the emotional tone of synthesized speech.

**Available emotions:**
```python
EMOTION_TYPES = [
    "happy",     # 高兴 - Joyful, excited, cheerful
    "sad",       # 悲伤 - Sorrowful, disappointed
    "angry",     # 愤怒 - Furious, annoyed
    "fearful",   # 害怕 - Scared, worried, anxious
    "disgusted", # 厌恶 - Revolted, repulsed
    "surprised", # 惊讶 - Astonished, amazed
    "calm",      # 中性 - Calm, neutral tone
    "fluent",    # 生动 - Fluent, vivid (speech-2.6 models only)
    "whisper",   # 低语 - Whisper (speech-2.6 models only)
]
```

**Model compatibility:**
- **speech-2.8-hd/turbo**: Automatically matches emotions from text (recommended: no need for manually specifying emotion)
- **speech-2.6-hd/turbo**: Supports all 9 emotions
- **speech-02-*/speech-01-***: Supports happy, sad, angry, fearful, disgusted, surprised, calm (7 emotions)

**Usage example:**
```python
voice = VoiceSetting(
    voice_id="female-shaonv",
    emotion="happy",  # Joyful tone
)
```

---

## Segment-based TTS

For multi-voice and multi-emotion workflows. Agent creates a segments.json file, then uses CLI or API to generate and merge audio.

### Default File Placement

When using the CLI without specifying paths, files are organized as:

```
./                          # Current working directory
└── audio/                  # Created automatically
    ├── tmp/                # Intermediate segment files
    │   ├── segment_0000.mp3
    │   ├── segment_0001.mp3
    │   └── ...
    └── <custom_audio_name>.mp3          # Final merged audio
```

- Output: `./audio/output.mp3` (if `-o` not specified)
- Intermediate files: `./audio/tmp/` (if `--temp-dir` not specified)
- Finally, ask user to confirm whether to delete intermediate files: `rm -rf ./audio/tmp/`

### Validate Segments File

```python
from scripts import validate_segments_file, ValidationResult

result: ValidationResult = validate_segments_file(
    file_path: str,        # Path to segments.json file
    strict: bool = True,   # Treat warnings as errors
)

# ValidationResult attributes:
# - valid: bool - Overall validation status
# - errors: List[str] - List of error messages
# - warnings: List[str] - List of warning messages
# - segments: List[Dict] - Parsed segments (empty if errors)
```

### Load Segments

```python
from scripts import load_segments

segments: List[Dict] = load_segments(
    file_path: str,         # Path to segments.json file
    validate: bool = True,  # Validate before loading
    strict: bool = False,   # Treat warnings as errors
)
# Raises ValueError if validation fails
```

### Generate from Segments

```python
from scripts import generate_from_segments

result: Dict = generate_from_segments(
    segments_file: str,             # Path to segments.json
    output_dir: Optional[str],      # Directory for audio files (default: ./audio/tmp/)
    model: str = "speech-2.8-hd",   # TTS model (speech-2.8 recommended)
    audio_format: str = "mp3",      # Output format
    sample_rate: int = 32000,       # Sample rate
    stop_on_error: bool = False,    # Stop on first error
    validate: bool = True,          # Validate file first
)

# Returns:
# {
#     "success": bool,
#     "segments": List[SegmentInfo],
#     "audio_files": List[str],     # Paths to generated files
#     "output_dir": str,
#     "errors": List[str],
#     "total": int,
#     "succeeded": int,
#     "failed": int,
# }
```

### Merge Segment Audio

```python
from scripts import merge_segment_audio

result: Dict = merge_segment_audio(
    audio_files: List[str],    # Audio file paths (in order)
    output_path: str,          # Output file path
    crossfade_ms: int = 0,     # Crossfade duration
    normalize: bool = True,    # Normalize audio levels
    fade_in_ms: int = 0,       # Fade in at start
    fade_out_ms: int = 0,      # Fade out at end
)

# Returns:
# {
#     "success": bool,
#     "output_path": str,
#     "error": Optional[str],
# }
```

### Complete Pipeline

```python
from scripts import process_segments_to_audio

result: Dict = process_segments_to_audio(
    segments_file: str,             # Path to segments.json
    output_path: str,               # Final output file path (CLI default: ./audio/output.mp3)
    output_dir: Optional[str],      # Temp directory (CLI default: ./audio/tmp/)
    model: str = "speech-2.8-hd",   # TTS model (speech-2.8 recommended)
    crossfade_ms: int = 0,          # Crossfade between segments
    normalize: bool = True,         # Normalize audio levels
    keep_temp_files: bool = False,  # Keep intermediate files (CLI keeps by default)
    stop_on_error: bool = True,     # Stop on first error
)

# Returns:
# {
#     "success": bool,
#     "output_path": str,
#     "segments_result": Dict,   # From generate_from_segments
#     "merge_result": Dict,      # From merge_segment_audio
#     "error": Optional[str],
# }
```

### segments.json Format

```json
[
  {
    "text": "Welcome to our podcast!",
    "voice_id": "male-qn-qingse",
    "emotion": "happy"
  },
  {
    "text": "Today we discuss AI.",
    "voice_id": "female-shaonv",
    "emotion": "calm"
  }
]
```

**Required fields:**
- `text`: String, non-empty
- `voice_id`: String, valid voice ID

**Optional fields:**
- `emotion`: One of `happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `calm`, `fluent`, `whisper`

### Valid Emotions

```python
from scripts import VALID_EMOTIONS

VALID_EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"]
```

### CLI Commands

```bash
# Validate segments file
python mmvoice.py validate segments.json
python mmvoice.py validate segments.json --verbose
python mmvoice.py validate segments.json --strict

# Generate audio from segments
python mmvoice.py generate segments.json -o output.mp3
python mmvoice.py generate segments.json -o output.mp3 --crossfade 200
python mmvoice.py generate segments.json -o output.mp3 --continue-on-error
```

---

## Voice Cloning

### Upload Source Audio

```python
from scripts import upload_clone_audio

file_id = upload_clone_audio(
    file_path: str,         # Audio file path (mp3, wav, m4a)
    timeout: int = 120,     # Upload timeout
) -> str
```

**File Requirements:**
- Format: mp3, wav, m4a
- Duration: 10 seconds to 5 minutes
- Size: Max 20MB
- Quality: Clear, single speaker, no background noise

### Upload Prompt Audio

```python
from scripts import upload_prompt_audio

file_id = upload_prompt_audio(
    file_path: str,        # Audio file path (< 8 seconds)
    timeout: int = 60,
) -> str
```

**Purpose:** Improve cloning similarity with short reference audio.

### Clone Voice

```python
from scripts import clone_voice

result = clone_voice(
    file_id: str,                          # From upload_clone_audio
    voice_id: str,                         # Custom ID (8-256 chars)
    clone_prompt: Optional[ClonePrompt],   # Optional prompt config
    preview_text: Optional[str],           # Generate preview audio (max 1000 chars)
    preview_model: str = "speech-2.8-hd",  # Model for preview
    need_noise_reduction: bool = False,    # Process source audio
    need_volume_normalization: bool = False,
    language_boost: Optional[str],
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]
```

**voice_id Requirements:**
- Length: 8-256 characters
- Must start with letter
- Can contain: letters, numbers, `-`, `_`
- Cannot end with `-` or `_`

**ClonePrompt Dataclass:**
```python
from scripts import ClonePrompt

clone_prompt = ClonePrompt(
    prompt_audio_file_id: str,   # From upload_prompt_audio
    prompt_text: str,            # Transcript of prompt audio
)
```

### Quick Clone

```python
from scripts import quick_clone_voice

result = quick_clone_voice(
    audio_path: str,
    voice_id: str,
    preview_text: Optional[str],
    output_preview_path: Optional[str],
    noise_reduction: bool = True,
    volume_normalize: bool = True,
) -> Dict[str, Any]
```

### High-Quality Clone

```python
from scripts import clone_voice_with_prompt

result = clone_voice_with_prompt(
    source_audio_path: str,       # 10s-5min
    prompt_audio_path: str,       # <8s
    prompt_text: str,             # Transcript
    voice_id: str,
    preview_text: Optional[str],
    output_preview_path: Optional[str],
    **kwargs,
) -> Dict[str, Any]
```

---

## Voice Design

### Design Voice

```python
from scripts import design_voice

result = design_voice(
    prompt: str,                  # Voice description
    preview_text: str,            # Preview text (max 1000 chars)
    voice_id: Optional[str],      # Custom ID (auto-generated if None)
    model: str = "speech-02-hd",
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]
```

**Prompt Examples:**
```python
# Detailed description
prompt = "A deep, resonant middle-aged male voice with clear articulation, " \
         "moderate pace, professional and trustworthy tone, suitable for " \
         "news broadcasting and documentary narration"

# Simple description
prompt = "Gentle young female voice, soft and sweet"
```

### Design from Template

```python
from scripts import design_voice_from_template

result = design_voice_from_template(
    template_key: str,           # See VOICE_PROMPT_TEMPLATES
    preview_text: str,
    voice_id: Optional[str],
    output_path: Optional[str],
    custom_modifier: str = "",   # Additional description
) -> Dict[str, Any]
```

**Available Templates:**
```python
VOICE_PROMPT_TEMPLATES = {
    "male_news_anchor": "Deep, authoritative middle-aged male voice...",
    "male_audiobook": "Warm, refined middle-aged male voice...",
    "male_youth": "Bright, cheerful young male voice...",
    "male_business": "Mature, composed business male voice...",
    "female_gentle": "Gentle, sweet young female voice...",
    "female_narrator": "Elegant, sophisticated mature female voice...",
    "female_lively": "Vivacious, playful young female voice...",
    "female_professional": "Capable, professional working woman's voice...",
    "storyteller": "Kind, warm storytelling voice...",
    "emotional": "Emotionally expressive performance voice...",
    "asmr_style": "Soft, soothing ASMR-style voice...",
}
```

---

## Voice Management

### Get Voices

```python
from scripts import get_voices, VoiceType

result = get_voices(
    voice_type: VoiceType = VoiceType.ALL,
    timeout: int = 30,
) -> Dict[str, Any]

# Filter by type
system_voices = get_voices(VoiceType.SYSTEM)
cloned_voices = get_voices(VoiceType.VOICE_CLONING)
designed_voices = get_voices(VoiceType.VOICE_GENERATION)
```

### Get Specific Voice Lists

```python
from scripts import (
    get_system_voices,
    get_cloned_voices,
    get_designed_voices,
    get_all_custom_voices,
)

voices = get_system_voices()      # List[Dict]
voices = get_cloned_voices()      # List[Dict]
voices = get_designed_voices()    # List[Dict]

custom = get_all_custom_voices()  # Dict with "cloned" and "designed"
```

### Check Voice Existence

```python
from scripts import voice_exists, get_voice_info

exists = voice_exists("male-qn-qingse")  # bool

info = get_voice_info("my-voice-id")     # Optional[Dict]
# Returns: {voice_id, type, name, description, created_time, ...}
```

### Delete Voice

```python
from scripts import delete_voice, delete_cloned_voice, delete_designed_voice, VoiceType

# Delete by type
result = delete_voice("voice-id", VoiceType.VOICE_CLONING)
result = delete_voice("voice-id", VoiceType.VOICE_GENERATION)

# Convenience functions
result = delete_cloned_voice("voice-id")
result = delete_designed_voice("voice-id")
```

**Note:** Cannot delete system voices.

### List All Voices

```python
from scripts import list_all_voices

list_all_voices(show_details=True)
# Prints formatted list of all voices
```

### Cleanup Unused Voices

```python
from scripts import cleanup_unused_voices

# Preview deletion
ids = cleanup_unused_voices(dry_run=True)

# Actually delete
ids = cleanup_unused_voices(dry_run=False)
```

---

## Audio Processing

### FFmpeg Installation

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Check Installation

```python
from scripts import check_ffmpeg_installed

if not check_ffmpeg_installed():
    print("Please install FFmpeg first")
```

### Probe Audio File

```python
from scripts import probe_audio_file

info = probe_audio_file("audio.mp3")

# AudioInfo attributes:
# - path: str
# - format: str
# - duration: float
# - sample_rate: int
# - channels: int
# - bitrate: Optional[int]
# - file_size: int
```

### Convert Format

```python
from scripts import convert_audio

# Simple conversion
convert_audio("input.wav", "output.mp3")

# With options
convert_audio(
    input_path="input.wav",
    output_path="output.mp3",
    target_format="mp3",
    sample_rate=44100,
    bitrate="192k",
    channels=2,
)

# Simple conversion (auto-named)
from scripts import convert_audio_simple
convert_audio_simple("input.wav", "mp3")
```

### Merge Audio Files

Uses filter_complex (resample, format conversion, concat, optional loudnorm/fades). If that fails and `crossfade_ms==0`, falls back to concat demuxer (`-f concat -c copy`); fallback requires all inputs to have identical format.

```python
from scripts import merge_audio_files

merge_audio_files(
    input_files=["part1.mp3", "part2.mp3", "part3.mp3"],
    output_path="complete.mp3",
    format="mp3",
    sample_rate=22050,
    crossfade_ms=1000,           # Crossfade between files
    fade_in_ms=500,               # Fade in at start
    fade_out_ms=500,              # Fade out at end
    normalize=True,               # Normalize levels
    use_concat_fallback=True,    # On filter failure, try concat demuxer (default)
)

# Simple concatenation (faster, requires same format; no fallback logic)
from scripts import concatenate_audio_files
concatenate_audio_files(
    input_files=["part1.mp3", "part2.mp3"],
    output_path="complete.mp3",
    crossfade_ms=0,              # No crossfade
)
```

### Normalize Audio

```python
from scripts import normalize_audio

normalize_audio(
    input_path="quiet.mp3",
    output_path="normalized.mp3",
    target_loudness=-16.0,       # LUFS (standard: -16 or -14)
    true_peak=-1.5,              # dBTP
    loudness_range=11.0,         # LU
)
```

### Adjust Volume

```python
from scripts import adjust_volume

# By decibels
adjust_volume(
    input_path="quiet.mp3",
    output_path="louder.mp3",
    volume_db=6.0,               # +6 dB (louder)
)

# By factor
adjust_volume(
    input_path="loud.mp3",
    output_path="quieter.mp3",
    volume_factor=0.5,           # Half volume
)
```

### Trim Audio

```python
from scripts import trim_audio

trim_audio(
    input_path="long.mp3",
    output_path="clip.mp3",
    start_time=30.0,             # Start at 30 seconds
    end_time=90.0,               # End at 90 seconds
    fade_in_ms=200,              # 200ms fade in
    fade_out_ms=200,             # 200ms fade out
)
```

### Remove Silence

```python
from scripts import remove_silence

remove_silence(
    input_path="with_silence.mp3",
    output_path="clean.mp3",
    threshold_db=-50,            # Silence threshold (dB)
    min_duration=0.5,            # Min silence duration to remove (seconds)
    keep_silence=0.2,            # Silence to keep at boundaries (seconds)
)
```

### Apply Effects

```python
from scripts import apply_effects

apply_effects(
    input_path="dry.mp3",
    output_path="reverbed.mp3",
    effects={
        "reverb": {
            "wet": 0.3,          # Wet/dry mix (0-1)
            "room_size": 0.5,    # Room size (0-1)
            "damping": 0.5,      # Damping (0-1)
        },
        "treble": 3.0,           # Treble boost (dB)
        "bass": 2.0,             # Bass boost (dB)
    },
)
```

### Optimize for Speech

```python
from scripts import optimize_for_speech

optimize_for_speech(
    input_path="recording.wav",
    output_path="optimized.wav",
    sample_rate=22050,           # Standard for speech
    channels=1,                  # Mono
    normalize=True,              # Normalize loudness
    remove_silence_threshold=-50,  # Remove silence
)
```

### Create Audio from Segments

```python
from scripts import create_audio_from_segments

# Assuming you have a TTS function
def tts_func(text, voice_id, output_path):
    # Call your TTS synthesis here
    pass

create_audio_from_segments(
    segments=[
        {
            "text": "Part one text",
            "voice_id": "male-qn-qingse",
            "tts_function": tts_func,
        },
        {
            "text": "Part two text",
            "voice_id": "female-shaonv",
            "tts_function": tts_func,
        },
    ],
    output_path="complete.mp3",
    crossfade_ms=500,
    normalize=True,
)
```

---

## Common Parameters

### VoiceSetting

```python
@dataclass
class VoiceSetting:
    voice_id: str                 # Voice ID (e.g., "male-qn-qingse", "female-shaonv")
    speed: float = 1.0            # 0.5-2.0
    volume: float = 1.0           # 0.1-10.0
    pitch: int = 0                # -12 to 12
    emotion: Optional[str] = None # happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
```

**Example:**

```python
voice = VoiceSetting(voice_id="female-shaonv", speed=1.0, volume=1.5)
```

### AudioSetting

```python
@dataclass
class AudioSetting:
    sample_rate: int = 32000     # 16000, 24000, 32000
    bitrate: int = 128000        # 64000, 128000, 192000
    format: str = "mp3"          # mp3, wav, flac, pcm
    channel: int = 1             # 1 (mono), 2 (stereo)
```

### VoiceType Enum

```python
class VoiceType(Enum):
    SYSTEM = "system"                    # System preset voices
    VOICE_CLONING = "voice_cloning"      # Cloned voices
    VOICE_GENERATION = "voice_generation"  # Designed voices
    ALL = "all"                          # All types
```

---

## Error Handling

### Common Exceptions

```python
from scripts import make_request, parse_response

try:
    result = synthesize_speech_http(text="Hello")
except ValueError as e:
    # API returned error
    print(f"API Error: {e}")
except requests.exceptions.RequestException as e:
    # Network error
    print(f"Network Error: {e}")
except TimeoutError:
    # Request timed out
    print("Request timed out")
```

### Error Response Format

```python
{
    "base_resp": {
        "status_code": 1001,    # Non-zero indicates error
        "status_msg": "Error description"
    }
}
```

### Async Task Errors

```python
from scripts import wait_for_task, AsyncTaskStatus

try:
    result = wait_for_task(task_id)
except TimeoutError:
    # Task took too long
    print("Task timed out")
except RuntimeError as e:
    # Task failed
    print(f"Task failed: {e}")
```

---

## Best Practices

### 1. Choose Right Model
- `speech-2.8-hd`: Best quality for important content
- `speech-2.8-turbo`: Good balance for most use cases
- Use async TTS for texts > 10,000 characters

### 2. Voice Selection
- Match voice to content type and audience
- Consider pacing and formality
- Test multiple voices before finalizing

### 3. Audio Quality
- Use 32000 sample rate for best quality
- Normalize audio post-processing
- Remove silence for cleaner output

### 4. Error Handling
- Always validate API responses
- Implement retry logic for network errors
- Handle async task timeouts gracefully

### 5. Cost Management
- Use preview features before committing
- Batch processing reduces per-request overhead
- Clean up unused cloned/designed voices

### 6. Performance
- Use streaming for real-time applications
- Cache voice information to reduce API calls
- Use WebSocket for long streaming sessions

### 7. Audio Processing Order
1. Merge/trim segments first
2. Apply effects
3. Normalize loudness
4. Convert to final format
