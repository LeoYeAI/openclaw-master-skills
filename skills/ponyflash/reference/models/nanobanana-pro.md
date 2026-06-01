# nanobanana-pro — Image Generation

High-quality AI image generation model. Also available as `nanobanana` (standard quality, lower cost).

## Supported parameters via PonyFlash SDK

```python
gen = pony_flash.images.generate(
    model="nanobanana-pro",   # or "nanobanana"
    prompt="A sunset over mountains",
    size="2K",                # "1K", "2K", "4K"
    n=1,
    output_format="png",
)
```

## Model variants and credits

| Model | Credits (1K) | Credits (2K) | Credits (4K) |
|---|---|---|---|
| `nanobanana` | 10 | — | — |
| `nanobanana-pro` | 20 | 20 | 20 |

Other variants: `nanobanana-fast` (5 credits), `nanobanana-vip` (30), `nanobanana-pro-vip` (40/50 at 4K), `nanobanana-2` (20/30/50).

## Resolution / size

| Value | Pixel dimensions (1:1) |
|---|---|
| `1K` | 1024x1024 |
| `2K` | 2048x2048 |
| `4K` | 4096x4096 |

Actual pixels scale proportionally with aspect ratio. For example, `16:9` at `4K` produces 4096x2304.

## Aspect ratios

Supported values: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `auto`.

Default is `1:1` if not specified.

## Modes

| Mode | Description | How to use |
|---|---|---|
| Text-to-image | Generate from text prompt | `prompt` only |
| Image-to-image | Transform with reference images | `prompt` + `images=[...]` |

Supports up to 8 reference images for image-to-image.

## Example: high-res wide image

```python
gen = pony_flash.images.generate(
    model="nanobanana-pro",
    prompt="Panoramic view of Tokyo skyline at dusk, cinematic",
    size="4K",
)
print(gen.url)
```

## Example: image-to-image with reference

```python
from pathlib import Path

gen = pony_flash.images.generate(
    model="nanobanana-pro",
    prompt="Same scene but in winter with snow",
    images=[Path("summer_photo.jpg")],
    size="2K",
)
print(gen.url)
```
