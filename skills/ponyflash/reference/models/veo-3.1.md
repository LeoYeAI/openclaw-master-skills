# veo-3.1 — Video Generation (Google)

Google's state-of-the-art video model. Synchronized audio, reference images, first/last frame control, 720p/1080p.

## Parameters

| Parameter | Type | Required | Default | Values |
|---|---|---|---|---|
| `prompt` | str | Yes | — | Text description |
| `duration` | int | No | 8 | `4`, `6`, `8` |
| `resolution` | str | No | "1080p" | `"720p"`, `"1080p"` |
| `aspect_ratio` | str | No | "16:9" | `"16:9"`, `"9:16"` |
| `generate_audio` | bool | No | true | Synchronized audio generation |
| `first_frame` | FileInput | No | — | Starting image |
| `last_frame` | FileInput | No | — | Ending image (smooth transition) |
| `reference_images` | List[FileInput] | No | — | Up to 3 reference images |
| `negative_prompt` | str | No | — | What to exclude |

Extra via `**extra_body`: `seed` (int)

## Pricing

| | with_audio | without_audio |
|---|---|---|
| Per second | 40 credits | 20 credits |
| 4s video | 160 credits | 80 credits |
| 6s video | 240 credits | 120 credits |
| 8s video | 320 credits | 160 credits |

## Examples

```python
# Text-to-video with audio
gen = pony_flash.video.generate(
    model="veo-3.1",
    prompt="A woman sings in a recording studio, warm lighting, close-up shot",
    duration=6,
    resolution="1080p",
    aspect_ratio="16:9",
)

# Image-to-video without audio
gen = pony_flash.video.generate(
    model="veo-3.1",
    prompt="Camera slowly zooms into the scene",
    first_frame=open("photo.jpg", "rb"),
    duration=4,
    generate_audio=False,
)

# Frame-to-frame transition
gen = pony_flash.video.generate(
    model="veo-3.1",
    prompt="Smooth transition from day to night",
    first_frame=open("day.jpg", "rb"),
    last_frame=open("night.jpg", "rb"),
    duration=8,
)
```

## Related

`veo-3.1-fast` — faster, cheaper. Same parameters. See [veo-3.1-fast.md](veo-3.1-fast.md).
