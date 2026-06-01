# speech-2.8-turbo — Text-to-Speech (MiniMax)

MiniMax Speech 2.8 Turbo. Same voice quality and parameter set as HD, with faster generation and lower latency (<250ms). Best for real-time applications, drafts, and high-volume use.

## Parameters

Same as [speech-2.8-hd.md](speech-2.8-hd.md). All voices, emotions, interjection tags, languages, and audio settings are identical.

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-turbo",
    input="Quick draft narration for review",
    voice="Casual_Guy",
    emotion="calm",
)
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `input` | str | Yes | — | Text to synthesize, max 10000 chars |
| `voice` | str | Yes | — | Voice ID (see speech-2.8-hd.md for full list) |
| `emotion` | str | No | `"auto"` | `auto`, `happy`, `calm`, `sad`, `angry`, `fearful`, `disgusted`, `surprised` |
| `speed` | float | No | `1.0` | 0.5 - 2.0 |
| `pitch` | int | No | `0` | -12 to +12 semitones |
| `format` | str | No | `"mp3"` | `mp3`, `wav`, `flac`, `pcm` |
| `sample_rate` | int | No | `32000` | 8000, 16000, 22050, 24000, 32000, 44100 |
| `language` | str | No | — | Language hint or `auto` |

## Pricing

1 credit/request (provisional — actual cost is $0.06/thousand input tokens)

## When to use Turbo vs HD

| | HD | Turbo |
|---|---|---|
| Quality | Highest | Very high |
| Latency | Standard | <250ms |
| Best for | Final production, audiobooks | Real-time apps, drafts, high volume |
| Cost | $0.10/1K tokens | $0.06/1K tokens |
