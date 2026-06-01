# speech-2.8-hd — Text-to-Speech (MiniMax)

MiniMax's highest-quality speech synthesis model. Supports 40+ languages, interjection tags, emotion control, voice modification, and pronunciation dictionaries.

## Supported parameters via PonyFlash SDK

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Hello (laughs), welcome to PonyFlash!",
    voice="English_Graceful_Lady",
    language="English",
    speed=1.0,
    pitch=0,
    emotion="happy",
    format="mp3",
)
```

## Voice IDs (selection)

### English
- `English_Graceful_Lady`
- `English_Insightful_Speaker`
- `English_radiant_girl`
- `English_Persuasive_Man`
- `English_Lucky_Robot`

### Chinese
- `Chinese (Mandarin)_Lyrical_Voice`
- `Chinese (Mandarin)_HK_Flight_Attendant`

### Japanese
- `Japanese_Whisper_Belle`

### Other system voices
300+ system voices available. Custom cloned voices and AI-generated voices also supported.

## Emotion control

Supported values: `happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `calm`, `fluent`.

By default the model auto-selects the most natural emotion. Manual specification only when explicitly needed.

Note: `whisper` is NOT supported on speech-2.8-hd (only on speech-2.6 series).

## Interjection tags

Only supported on speech-2.8-hd and speech-2.8-turbo:

`(laughs)`, `(chuckle)`, `(coughs)`, `(clear-throat)`, `(groans)`, `(breath)`, `(pant)`, `(inhale)`, `(exhale)`, `(gasps)`, `(sniffs)`, `(sighs)`, `(snorts)`, `(burps)`, `(lip-smacking)`, `(humming)`, `(hissing)`, `(emm)`, `(sneezes)`.

Place them inline: `"Hello (laughs), that's amazing (gasps)!"`.

## Voice settings

| Parameter | Range | Default | Description |
|---|---|---|---|
| `speed` | 0.5–2.0 | 1.0 | Speech speed |
| `pitch` | -12 to 12 | 0 | Pitch adjustment |

## Audio output settings

| Parameter | Supported values |
|---|---|
| `sample_rate` | 8000, 16000, 22050, 24000, 32000, 44100 |
| `format` | mp3, pcm, flac, wav (wav only in non-streaming) |

## Pause control

Insert `<#x#>` in text for custom pauses (x = 0.01–99.99 seconds):

`"First sentence.<#2.5#>Second sentence after 2.5s pause."`

## Supported languages (40+)

Chinese, English, Arabic, Russian, Spanish, French, Portuguese, German, Turkish, Dutch, Ukrainian, Vietnamese, Indonesian, Japanese, Italian, Korean, Thai, Polish, Romanian, Greek, Czech, Finnish, Hindi, Bulgarian, Danish, Hebrew, Malay, Persian, Slovak, Swedish, Croatian, Filipino, Hungarian, Norwegian, Slovenian, Catalan, Nynorsk, Tamil, Afrikaans, `auto` (auto-detect).

## Example: expressive narration

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="(sighs) The real danger is not that computers start thinking like people (gasps), but that people start thinking like computers.",
    voice="English_Insightful_Speaker",
    language="English",
    speed=0.9,
    pitch=-2,
    emotion="calm",
    sample_rate=44100,
    format="mp3",
)
print(gen.url)
```

## Example: multilingual with auto-detect

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Hello World! Welcome to PonyFlash!",
    voice="English_Graceful_Lady",
    language="auto",
)
```

## Related model

`speech-2.8-turbo` — faster generation, slightly lower quality. Same parameter set.
