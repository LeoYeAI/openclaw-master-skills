# Text-to-Speech Guide

Complete workflows for synchronous and asynchronous TTS.

## Contents

- [Synchronous TTS (short text)](#synchronous-tts-short-text)
- [Asynchronous TTS (long text)](#asynchronous-tts-long-text)
- [Streaming TTS](#streaming-tts)
- [Multi-segment production](#multi-segment-production)

---

## Synchronous TTS (short text)

For text ≤ 10,000 characters. Returns audio immediately.

### Basic HTTP synthesis

```python
from scripts import (
    synthesize_speech_http,
    VoiceSetting,
    AudioSetting,
    save_audio_from_hex,
)

# Configure voice
voice = VoiceSetting(
    voice_id="female-shaonv",
    speed=1.0,
    volume=1.0,
    pitch=0,
    emotion="happy",
)

# Configure audio output
audio_settings = AudioSetting(
    sample_rate=32000,
    bitrate=128000,
    format="mp3",
    channel=1,
)

# Synthesize
result = synthesize_speech_http(
    text="Welcome to our guide on voice synthesis.",
    model="speech-2.6-hd",
    voice_setting=voice,
    audio_setting=audio_settings,
)

# Save audio
if result.get("data", {}).get("audio"):
    save_audio_from_hex(result["data"]["audio"], "output.mp3")

# Print metadata
print(f"Duration: {result['extra_info']['duration']}s")
print(f"Sample rate: {result['extra_info']['sample_rate']} Hz")
```

### Quick synthesis (one-liner)

```python
from scripts import quick_tts

audio = quick_tts(
    text="Quick synthesis example",
    voice_id="male-qn-qingse",
    output_path="quick.mp3"
)
```

---

## Asynchronous TTS (long text)

For text > 10,000 characters (up to 1 million). Creates a task and polls for completion.

### Complete async flow

```python
from scripts import async_tts_full_flow, VoiceSetting, AudioSetting

# Load long text
with open("novel_chapter.txt", "r") as f:
    long_text = f.read()

# Configure voice
voice = VoiceSetting(
    voice_id="audiobook_male_1",
    speed=0.9,  # Slower for audiobooks
    volume=1.0,
)

audio = AudioSetting(
    sample_rate=32000,
    bitrate=128000,
    format="mp3",
)

# Create task, wait for completion, download
result = async_tts_full_flow(
    text=long_text,
    model="speech-2.6-hd",
    voice_setting=voice,
    audio_setting=audio,
    output_path="chapter.mp3",
    polling_interval=10,  # Check every 10s
    max_wait_time=3600,   # Max 1 hour
)

print(f"Status: {result['status']}")
print(f"Duration: {result['extra_info']['duration']}s")
```

### Step-by-step async (for custom workflows)

```python
from scripts import (
    create_async_tts_task,
    query_async_tts_task,
    wait_for_task,
    download_audio_from_url,
)

# Step 1: Create task
create_result = create_async_tts_task(
    model="speech-2.6-hd",
    text=long_text,
    voice_setting=voice,
    audio_setting=audio,
)

task_id = create_result.get("task_id")
print(f"Task created: {task_id}")

# Step 2: Query status manually
status_result = query_async_tts_task(task_id)
print(f"Status: {status_result.get('status')}")

# Step 3: Wait for completion
final_result = wait_for_task(
    task_id,
    polling_interval=5,
    max_wait_time=600,
    on_status_change=lambda s, r: print(f"Status: {s}")
)

# Step 4: Download
audio_url = final_result.get("file", {}).get("download_url")
if audio_url:
    download_audio_from_url(audio_url, "output.mp3")
```

---

## Streaming TTS

For real-time audio generation via WebSocket.

```python
from scripts import (
    synthesize_speech_websocket,
    WebSocketTTSConfig,
    VoiceSetting,
)
import asyncio

async def stream_example():
    # Configure
    config = WebSocketTTSConfig(
        model="speech-2.6-hd",
        voice_setting=VoiceSetting(voice_id="female-shaonv"),
        chunk_size=1024,
    )
    
    # Stream multiple text segments
    text_segments = [
        "Welcome to our live broadcast.",
        "Today we'll discuss important topics.",
        "Stay tuned for more updates.",
    ]
    
    audio_data = await synthesize_speech_websocket(
        text_segments=text_segments,
        model=config.model,
        voice_setting=config.voice_setting,
    )
    
    # Save complete audio
    with open("stream_output.mp3", "wb") as f:
        f.write(audio_data)

# Run
asyncio.run(stream_example())
```

---

## Multi-segment production

Generate podcast-style content with multiple voices and transitions.

```python
from scripts import quick_tts, merge_audio_files

# Define segments
segments = [
    {"text": "Welcome to Tech Talk podcast.", "voice": "presenter_male"},
    {"text": "Today's topic is AI.", "voice": "presenter_female"},
    {"text": "Let's begin with history.", "voice": "presenter_male"},
]

# Generate each segment
temp_files = []
for i, seg in enumerate(segments):
    temp_file = f"/tmp/segment_{i}.mp3"
    quick_tts(
        text=seg["text"],
        voice_id=seg["voice"],
        output_path=temp_file,
    )
    temp_files.append(temp_file)

# Merge with crossfade
merge_audio_files(
    input_files=temp_files,
    output_path="podcast_intro.mp3",
    crossfade_ms=500,  # 0.5s crossfade
    normalize=True,
)

# Cleanup
import os
for f in temp_files:
    os.remove(f)

print("Podcast intro generated")
```

## Best practices

- **Short text**: Use `quick_tts()` or `synthesize_speech_http()`
- **Long text**: Use `async_tts_full_flow()` with appropriate polling interval
- **Real-time**: Use WebSocket streaming
- **Multi-voice**: Generate segments separately, then merge with `merge_audio_files()`
- **Quality**: Use `speech-2.6-hd` model and 32000 sample rate
- **Speed**: Use `speech-2.6-turbo` for faster processing

## Error handling

```python
from scripts import synthesize_speech_http
import requests

try:
    result = synthesize_speech_http(text="Test")
except ValueError as e:
    print(f"API error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
except TimeoutError:
    print("Request timed out")
```

## See also

- **API reference**: [api_documentation.md](api_documentation.md#synchronous-tts)
- **Voice selection**: [voice_catalog.md](voice_catalog.md)
- **Audio processing**: [audio-guide.md](audio-guide.md)
