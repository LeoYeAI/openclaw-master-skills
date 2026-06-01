# Video API Reference

## Method

### `pony_flash.video.generate(**kwargs) -> Generation`

Generate video and wait for completion.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | `str` | Yes | — | Model ID (e.g. `"seedance-1.5-pro"`, `"veo-3.1"`, `"omnihuman-1.5"`, `"motion-transfer-1"`) |
| `prompt` | `str` | No | — | Text description |
| `size` | `str` | No | — | Output size (e.g. `"1920x1080"`) |
| `duration` | `int` | No | — | Duration in seconds |
| `quality` | `str` | No | — | Quality level |
| `first_frame` | `FileInput` | No | — | Starting frame image |
| `last_frame` | `FileInput` | No | — | Ending frame image |
| `video` | `FileInput` | No | — | Input video |
| `audio` | `FileInput` | No | — | Audio track (for OmniHuman) |
| `reference_images` | `List[FileInput]` | No | — | Reference images |
| `motion_video` | `FileInput` | No | — | Motion source video (for Motion Transfer) |

## Generation modes

| Mode | Required params | Model example |
|---|---|---|
| Text-to-video | `model`, `prompt` | `seedance-1.5-pro`, `veo-3.1` |
| First-frame to video | `model`, `first_frame`, `prompt` | `seedance-1.5-pro`, `veo-3.1` |
| OmniHuman | `model`, `first_frame`, `audio` | `omnihuman-1.5` |
| Motion Transfer | `model`, `first_frame`, `motion_video` | `motion-transfer-1` |

## Example

```python
gen = pony_flash.video.generate(
    model="seedance-1.5-pro",
    prompt="Ocean waves crashing on a beach",
    duration=5,
)
print(gen.url)
print(f"Credits: {gen.credits}")
```

## Available models

- [seedance-1.5-pro](models/seedance-1.5-pro.md) — 720p, 2-12s, auto-generated audio, multi-language
- [veo-3.1](models/veo-3.1.md) — 720p/1080p, 4/6/8s, reference images, English only

For the full model list, see [models/INDEX.md](models/INDEX.md).
