# Music API Reference

## Method

### `pony_flash.music.generate(**kwargs) -> Generation`

Generate music and wait for completion.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | `str` | Yes | — | Model ID (e.g. `"music-2.5"`) |
| `prompt` | `str` | Yes | — | Description of the music to generate |
| `lyrics` | `str` | No | — | Song lyrics (supports structure tags like `[Verse]`, `[Chorus]`) |
| `title` | `str` | No | — | Song title |
| `style` | `str` | No | — | Music style (e.g. `"pop ballad"`, `"electronic"`) |
| `duration` | `int` | No | — | Duration in seconds |
| `instrumental` | `bool` | No | — | If `True`, generate without vocals |
| `reference_audio` | `FileInput` | No | — | Reference audio for style/continuation |
| `continue_at` | `float` | No | — | Timestamp (seconds) to continue from |
| `format` | `str` | No | — | Output format |
| `quality` | `str` | No | — | Quality level |

## Example

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="A chill lo-fi hip hop beat for studying",
    instrumental=True,
    duration=60,
)
print(gen.url)
```

## Available models

- [music-2.5](models/music-2.5.md) — lyrics structure tags, instrumental mode, song continuation

For the full model list, see [models/INDEX.md](models/INDEX.md).
