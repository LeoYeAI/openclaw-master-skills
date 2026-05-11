# Voice Creation Guide

Create custom voices through cloning or design.

## Contents

- [Voice cloning](#voice-cloning)
- [Voice design](#voice-design)
- [Voice management](#voice-management)

---

## Voice cloning

Create custom voices from audio samples (10s–5min).

### Quick clone

Simplest way to clone a voice:

```python
from scripts import quick_clone_voice

quick_clone_voice(
    audio_path="my_voice.mp3",
    voice_id="my-custom-voice-001"
)

# Use immediately
from scripts import quick_tts
quick_tts(
    text="Test with cloned voice",
    voice_id="my-custom-voice-001",
    output_path="cloned_test.mp3"
)
```

### High-quality cloning with prompt audio

For better quality, provide a short prompt audio with transcript:

```python
from scripts import clone_voice_with_prompt

result = clone_voice_with_prompt(
    source_audio_path="full_recording.mp3",    # 10s-5min
    prompt_audio_path="short_sample.mp3",      # <8s, same speaker
    prompt_text="This is a short sample clip", # Exact transcript
    voice_id="hq-clone-001",
    preview_text="This is a preview of the cloned voice",
    output_preview_path="preview.mp3",
)

print(f"Voice ID: {result['voice_id']}")
# Preview audio saved to preview.mp3
```

### Step-by-step cloning

For custom workflows:

```python
from scripts import (
    upload_clone_audio,
    upload_prompt_audio,
    clone_voice,
    ClonePrompt,
    save_audio_from_hex,
)

# Step 1: Upload source audio
file_id = upload_clone_audio("speaker.mp3")

# Step 2: Upload prompt audio (optional)
prompt_file_id = upload_prompt_audio("short_clip.mp3")
clone_prompt = ClonePrompt(
    prompt_file_id=prompt_file_id,
    prompt_text="Exact transcript of short clip"
)

# Step 3: Clone
result = clone_voice(
    file_id=file_id,
    voice_id="custom-voice-001",
    clone_prompt=clone_prompt,
    preview_text="Preview generation text",
    need_noise_reduction=True,
    need_volume_normalization=True,
)

# Step 4: Save preview
if result.get("demo_audio"):
    save_audio_from_hex(result["demo_audio"], "clone_preview.mp3")

print(f"Voice cloned: {result['voice_id']}")
```

### Requirements

| Aspect | Requirement |
|--------|-------------|
| **Source audio** | 10s–5min duration, ≤20MB, mp3/wav/m4a |
| **Prompt audio** | <8s duration, same speaker as source |
| **voice_id** | 8-256 chars, starts with letter, alphanumeric/-/_ |

### Important notes

- Cloned voices are **temporary** by default
- Must be used with TTS API within **7 days** to be permanently saved
- Otherwise automatically deleted
- Preview audio generation is **free**

---

## Voice design

Generate unique voices from text descriptions.

### Basic design

```python
from scripts import design_voice, save_audio_from_hex

result = design_voice(
    prompt="A gentle young female voice with soft, sweet tones, suitable for bedtime stories",
    preview_text="Once upon a time, in a faraway kingdom...",
)

voice_id = result["voice_id"]
save_audio_from_hex(result["trial_audio"], "designed_voice.mp3")

# Use immediately
from scripts import quick_tts
quick_tts(
    text="Story content",
    voice_id=voice_id,
    output_path="story.mp3"
)
```

### Using templates

Predefined templates for common voice types:

```python
from scripts import (
    design_voice_from_template,
    VOICE_PROMPT_TEMPLATES,
    list_voice_templates,
)

# List available templates
templates = list_voice_templates()
print(templates.keys())
# ['male_news_anchor', 'female_gentle', 'storyteller', ...]

# Use template
result = design_voice_from_template(
    template_key="male_news_anchor",
    preview_text="Welcome to tonight's news program",
    output_path="news_voice.mp3",
)
```

### Available templates

```python
VOICE_PROMPT_TEMPLATES = {
    "male_news_anchor": "Professional male news anchor voice...",
    "female_gentle": "Soft, warm female voice for gentle content...",
    "storyteller": "Expressive narrative voice for storytelling...",
    "business_male": "Confident professional male voice...",
    "assistant_female": "Friendly, helpful female assistant voice...",
    # ... more templates
}
```

### Voice description tips

Include in your prompt:
- **Gender**: male, female, neutral
- **Age**: young, middle-aged, mature
- **Characteristics**: gentle, energetic, authoritative, warm
- **Tone**: professional, casual, friendly, serious
- **Use case**: news, storytelling, tutorials, podcasts

**Good example**:
```
"A confident middle-aged male voice with clear articulation 
and authoritative tone, suitable for business presentations 
and corporate training"
```

**Bad example**:
```
"A nice voice"
```

### Important notes

- Designed voices are **temporary** by default
- Must be used with TTS API within **7 days** to be saved
- Trial audio generation incurs **charges**
- More detailed prompts = better results

---

## Voice management

List, check, and delete custom voices.

### List voices

```python
from scripts import (
    get_system_voices,
    get_cloned_voices,
    get_designed_voices,
    get_all_custom_voices,
    list_all_voices,
)

# List by type
system = get_system_voices()        # Preset voices
cloned = get_cloned_voices()        # Your cloned voices
designed = get_designed_voices()    # Your designed voices

# All custom
all_custom = get_all_custom_voices()
print(f"Cloned: {len(all_custom['cloned'])}")
print(f"Designed: {len(all_custom['designed'])}")

# Pretty print all
list_all_voices()
```

### Check voice existence

```python
from scripts import voice_exists, get_voice_info

# Check if voice exists
if voice_exists("male-qn-qingse"):
    print("Voice available")

# Get detailed info
info = get_voice_info("my-custom-voice")
if info:
    print(f"Type: {info['type']}")
    print(f"ID: {info['voice_id']}")
```

### Delete voices

```python
from scripts import delete_cloned_voice, delete_designed_voice

# Delete cloned voice
delete_cloned_voice("my-cloned-voice")

# Delete designed voice
delete_designed_voice("my-designed-voice")
```

### Batch cleanup

Remove all custom voices:

```python
from scripts import cleanup_unused_voices

# Preview what will be deleted (dry run)
deleted_ids = cleanup_unused_voices(dry_run=True)
print(f"Would delete {len(deleted_ids)} voices")

# Actually delete
deleted_ids = cleanup_unused_voices(dry_run=False)
print(f"Deleted {len(deleted_ids)} voices")
```

## Best practices

### Cloning

- **Audio quality**: Use clear recordings without background noise
- **Duration**: 30s-2min is usually sufficient
- **Prompt audio**: Include if available, improves quality significantly
- **Noise reduction**: Enable for recordings with background noise
- **Test immediately**: Generate preview to verify quality

### Designing

- **Be specific**: Detailed descriptions yield better results
- **Use templates**: Start with templates and modify if needed
- **Test prompts**: Try variations to find best match
- **Save successful prompts**: Reuse descriptions that work well

### Management

- **Use within 7 days**: Voices expire if not used with TTS
- **Track voice IDs**: Keep a list of your custom voices
- **Clean up regularly**: Remove unused voices to avoid clutter
- **Name systematically**: Use descriptive, consistent naming (e.g., `project-narrator-v1`)

## Error handling

```python
from scripts import quick_clone_voice

try:
    quick_clone_voice("my_voice.mp3", "my-voice-001")
except ValueError as e:
    if "duration" in str(e):
        print("Audio too short/long (need 10s-5min)")
    elif "file size" in str(e):
        print("Audio too large (max 20MB)")
    elif "voice_id" in str(e):
        print("Invalid voice_id format")
    else:
        print(f"Error: {e}")
```

## See also

- **API reference**: [api_documentation.md](api_documentation.md#voice-cloning)
- **Voice catalog**: [voice_catalog.md](voice_catalog.md)
- **Using voices**: [tts-guide.md](tts-guide.md)
