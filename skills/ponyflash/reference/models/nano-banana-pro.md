# nano-banana-pro — Image Generation (Google)

Google DeepMind's highest-quality image generation model built on Gemini 3 Pro. Accurate text rendering in multiple languages, multi-image blending (up to 14 references), professional creative controls.

## Parameters

```python
gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="A minimalist logo for a coffee shop with the text 'BREW'",
    resolution="2K",
    aspect_ratio="1:1",
    output_format="png",
)
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | str | Yes | — | Text description of the image |
| `resolution` | str | No | `"2K"` | `"1K"`, `"2K"`, `"4K"` |
| `aspect_ratio` | str | No | `"match_input_image"` | See values below |
| `output_format` | str | No | `"jpg"` | `"jpg"`, `"png"` |
| `reference_images` | List[FileInput] | No | — | Up to 14 reference images |

### aspect_ratio values

`match_input_image`, `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

### Extra parameters (via **extra_body)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `safety_filter_level` | str | `"block_only_high"` | `"block_low_and_above"`, `"block_medium_and_above"`, `"block_only_high"` |

## Pricing

| Resolution | Credits |
|---|---|
| 1K | 7 |
| 2K | 10 |
| 4K | 15 |

## Examples

```python
# Text-to-image, 4K panoramic
gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="Panoramic view of Tokyo skyline at dusk, cinematic",
    resolution="4K",
    aspect_ratio="21:9",
)

# Image editing with reference
gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="Same scene but in winter with snow",
    reference_images=[open("summer_photo.jpg", "rb")],
    resolution="2K",
)
```
