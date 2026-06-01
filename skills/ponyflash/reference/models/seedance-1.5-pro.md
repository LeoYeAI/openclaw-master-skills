# seedance-1.5-pro — Video Generation (ByteDance)

Cinema-quality video with synchronized audio, lip-sync, multilingual support. Dual-branch architecture generates audio+video simultaneously.

## Parameters

| Parameter | Type | Required | Default | Values |
|---|---|---|---|---|
| `prompt` | str | Yes* | — | Text description (*or first_frame required) |
| `duration` | int | No | 8 | 2-12 (any integer) |
| `resolution` | str | No | "720p" | `"480p"`, `"720p"`, `"1080p"` |
| `aspect_ratio` | str | No | "16:9" | `"16:9"`, `"4:3"`, `"1:1"`, `"3:4"`, `"9:16"`, `"21:9"`, `"9:21"` |
| `generate_audio` | bool | No | false | Synchronized audio generation |
| `first_frame` | FileInput | No | — | Starting image for image-to-video |
| `last_frame` | FileInput | No | — | Ending image |

Extra via `**extra_body`: `camera_fixed` (bool, lock camera to reduce motion blur)

## Pricing

| resolution | with_audio | without_audio |
|---|---|---|
| 480p | 3 credits/s | 1 credit/s |
| 720p | 5 credits/s | 3 credits/s |
| 1080p | 12 credits/s | 6 credits/s |

Example: 8s 720p with audio = 5 * 8 = 40 credits

## Examples

```python
# Text-to-video
gen = pony_flash.video.generate(
    model="seedance-1.5-pro",
    prompt="A cinematic sunrise over mountains, slow camera pan",
    duration=5,
    resolution="720p",
    aspect_ratio="16:9",
)

# Image-to-video with audio
gen = pony_flash.video.generate(
    model="seedance-1.5-pro",
    prompt="Person starts talking to the camera",
    first_frame=open("portrait.jpg", "rb"),
    duration=8,
    resolution="1080p",
    generate_audio=True,
)

# Budget mode: 480p, short, no audio
gen = pony_flash.video.generate(
    model="seedance-1.5-pro",
    prompt="Quick product demo",
    duration=3,
    resolution="480p",
    generate_audio=False,
)
```
