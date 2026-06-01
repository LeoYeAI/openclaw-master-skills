# Speech API Reference

## Method

### `pony_flash.speech.generate(**kwargs) -> Generation`

Generate speech audio and wait for completion.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | `str` | Yes | — | Model ID (e.g. `"speech-2.8-hd"`) |
| `input` | `str` | Yes | — | Text to synthesize |
| `voice` | `str` | Yes | — | Voice ID (e.g. `"English_Graceful_Lady"`, `"English_Insightful_Speaker"`) |
| `language` | `str` | No | — | Language code |
| `speed` | `float` | No | — | Playback speed multiplier |
| `pitch` | `int` | No | — | Pitch adjustment |
| `emotion` | `str` | No | — | Emotion (e.g. `"happy"`, `"sad"`, `"calm"`, `"angry"`, `"surprised"`) |
| `instructions` | `str` | No | — | Style instructions |
| `voice_settings` | `VoiceSettings` | No | — | Fine-grained voice control |
| `sample_rate` | `int` | No | — | Audio sample rate in Hz |
| `format` | `str` | No | — | Output format (e.g. `"mp3"`, `"wav"`) |

### VoiceSettings (TypedDict)

| Field | Type | Description |
|---|---|---|
| `stability` | `float` | Voice stability (0.0-1.0) |
| `similarity_boost` | `float` | Voice similarity (0.0-1.0) |
| `style` | `float` | Style exaggeration (0.0-1.0) |
| `use_speaker_boost` | `bool` | Enable speaker boost |

## Example

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Hello, welcome to PonyFlash!",
    voice="English_Graceful_Lady",
    speed=1.0,
    format="mp3",
)
print(gen.url)
```

## Available models

- [speech-2.8-hd](models/speech-2.8-hd.md) — 40+ languages, 300+ voices, interjection tags, emotion control

For the full model list, see [models/INDEX.md](models/INDEX.md).
