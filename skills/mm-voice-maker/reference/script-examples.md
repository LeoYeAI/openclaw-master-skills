# Runnable Script Examples

Copy-paste runnable code examples for testing each module. Run from project root with `MINIMAX_VOICE_API_KEY` set.

## Contents

- [Sync TTS](#sync-tts)
- [Async TTS](#async-tts)
- [Segment-based TTS](#segment-based-tts)
- [Audio processing](#audio-processing)
- [Voice cloning](#voice-cloning)
- [Voice design](#voice-design)
- [Voice management](#voice-management)

---

## Sync TTS

### HTTP synthesis

```python
from scripts import (
    synthesize_speech_http,
    VoiceSetting,
    AudioSetting,
    save_audio_from_hex,
)

voice = VoiceSetting(
    voice_id="male-qn-qingse",
    speed=1.0,
    volume=1.0,
    pitch=0,
    emotion="happy"
)

audio = AudioSetting(
    sample_rate=32000,
    bitrate=128000,
    format="mp3",
    channel=1
)

result = synthesize_speech_http(
    text="Today is a great day!",
    model="speech-2.6-hd",
    voice_setting=voice,
    audio_setting=audio,
)

if result.get("data", {}).get("audio"):
    save_audio_from_hex(result["data"]["audio"], "sync_output.mp3")
    print("Saved to sync_output.mp3")
```

### WebSocket streaming

```python
from scripts import synthesize_speech_websocket, VoiceSetting
import asyncio

async def stream_example():
    audio = await synthesize_speech_websocket(
        text_segments=["Hello", "This is WebSocket synthesis"],
        model="speech-2.6-hd",
        voice_setting=VoiceSetting(voice_id="female-shaonv"),
    )
    with open("ws_output.mp3", "wb") as f:
        f.write(audio)
    print("Saved to ws_output.mp3")

asyncio.run(stream_example())
```

---

## Async TTS

For long text (10k+ characters):

```python
from scripts import (
    create_async_tts_task,
    wait_for_task,
    download_audio_from_url,
    VoiceSetting,
    AudioSetting,
)

long_text = "Your very long text here..." * 100  # Up to 1M chars

voice = VoiceSetting(voice_id="audiobook_male_1", speed=0.9)
audio = AudioSetting(sample_rate=32000, bitrate=128000, format="mp3")

# Create task
create_result = create_async_tts_task(
    model="speech-2.6-hd",
    text=long_text,
    voice_setting=voice,
    audio_setting=audio,
)

task_id = create_result.get("task_id")
print(f"Task created: {task_id}")

# Wait for completion
final_result = wait_for_task(
    task_id,
    polling_interval=5,
    max_wait_time=600,
    on_status_change=lambda s, r: print(f"Status: {s}")
)

# Download
audio_url = final_result.get("file", {}).get("download_url")
if audio_url:
    download_audio_from_url(audio_url, "async_output.mp3")
    print("Saved to async_output.mp3")
```

---

## Segment-based TTS

### Validate segments file

```python
from scripts import validate_segments_file

result = validate_segments_file("segments.json", model="speech-2.8-hd")
if result.valid:
    print(f"Valid: {len(result.segments)} segments")
else:
    for err in result.errors:
        print(f"Error: {err}")
```

### Generate from segments

```python
from scripts import process_segments_to_audio

result = process_segments_to_audio(
    segments_file="segments.json",
    output_path="./audio/output.mp3",
    model="speech-2.8-hd",
    crossfade_ms=200,
)

if result["success"]:
    print(f"Audio saved to: {result['output_path']}")
```

### Using the CLI (recommended)

```bash
# Validate segments
python mmvoice.py validate segments.json

# Generate audio
python mmvoice.py generate segments.json
```

---

## Audio processing

### Format conversion

```python
from scripts import convert_audio

convert_audio("input.wav", "output.mp3", bitrate="192k")
```

### Merge files

```python
from scripts import merge_audio_files

merge_audio_files(
    ["part1.mp3", "part2.mp3"],
    "combined.mp3",
    crossfade_ms=300,
    normalize=True,
)
```

### Normalize

```python
from scripts import normalize_audio

normalize_audio("quiet.mp3", "normalized.mp3")
```

### Trim

```python
from scripts import trim_audio

trim_audio("long.mp3", "clip.mp3", start_time=30, end_time=90)
```

### Remove silence

```python
from scripts import remove_silence

remove_silence("recording.mp3", "clean.mp3")
```

### Optimize for speech

```python
from scripts import optimize_for_speech

optimize_for_speech(
    "raw.wav",
    "optimized.mp3",
    sample_rate=22050,
    channels=1,
)
```

---

## Voice cloning

### Quick clone

```python
from scripts import quick_clone_voice

quick_clone_voice("my_voice.mp3", "my-voice-001")
```

### With prompt audio

```python
from scripts import clone_voice_with_prompt

clone_voice_with_prompt(
    source_audio_path="full_sample.mp3",
    prompt_audio_path="short_clip.mp3",
    prompt_text="Short clip transcript",
    voice_id="hq-clone-001",
    preview_text="Preview text",
    output_preview_path="preview.mp3",
)
```

### Step-by-step

```python
from scripts import (
    upload_clone_audio,
    clone_voice,
    save_audio_from_hex,
)

file_id = upload_clone_audio("speaker.mp3")
result = clone_voice(
    file_id=file_id,
    voice_id="custom-001",
    preview_text="Preview",
)
if result.get("demo_audio"):
    save_audio_from_hex(result["demo_audio"], "clone_preview.mp3")
```

---

## Voice design

### Basic design

```python
from scripts import design_voice, save_audio_from_hex

result = design_voice(
    prompt="A gentle female voice, soft and warm",
    preview_text="Once upon a time...",
)

save_audio_from_hex(result["trial_audio"], "designed.mp3")
voice_id = result["voice_id"]
```

### Using templates

```python
from scripts import design_voice_from_template, VOICE_PROMPT_TEMPLATES

result = design_voice_from_template(
    template_key="male_news_anchor",
    preview_text="Welcome to the news",
    output_path="news.mp3",
)

# List templates
print(list(VOICE_PROMPT_TEMPLATES.keys()))
```

---

## Voice management

### List voices

```python
from scripts import (
    list_all_voices,
    get_system_voices,
    get_cloned_voices,
    get_designed_voices,
)

list_all_voices()
system = get_system_voices()
cloned = get_cloned_voices()
designed = get_designed_voices()
```

### Check and delete

```python
from scripts import (
    voice_exists,
    get_voice_info,
    delete_cloned_voice,
    delete_designed_voice,
)

if voice_exists("my-voice"):
    info = get_voice_info("my-voice")
    print(info)

delete_cloned_voice("old-voice")
delete_designed_voice("unused-voice")
```

### Batch cleanup

```python
from scripts import cleanup_unused_voices

# Preview
cleanup_unused_voices(dry_run=True)

# Delete all custom voices
cleanup_unused_voices(dry_run=False)
```

---

## Notes

All examples assume `MINIMAX_VOICE_API_KEY` is set:

```bash
export MINIMAX_VOICE_API_KEY="your-key"
```

For more detailed workflows, see:
- [tts-guide.md](tts-guide.md)
- [emotion-guide.md](emotion-guide.md)
- [voice-guide.md](voice-guide.md)
- [audio-guide.md](audio-guide.md)
