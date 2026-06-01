# nano-banana-2 — Image Generation (Google)

Google's fast image model built on Gemini 3.1 Flash. High-quality generation with Google Search grounding for real-time info, multi-image fusion, and 14 aspect ratios. Faster than Pro.

## Parameters

```python
gen = pony_flash.images.generate(
    model="nano-banana-2",
    prompt="Current weather forecast for Tokyo as an infographic",
    resolution="2K",
    aspect_ratio="9:16",
)
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | str | Yes | — | Text description of the image |
| `resolution` | str | No | `"1K"` | `"1K"`, `"2K"`, `"4K"` |
| `aspect_ratio` | str | No | `"match_input_image"` | See values below |
| `output_format` | str | No | `"jpg"` | `"jpg"`, `"png"` |
| `reference_images` | List[FileInput] | No | — | Up to 14 reference images |

### aspect_ratio values

`match_input_image`, `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`

### Extra parameters (via **extra_body)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `google_search` | bool | `true` | Use Google Web Search for real-time info (weather, sports, events) |
| `image_search` | bool | `true` | Use Google Image Search for visual context |

## Pricing

| Resolution | Credits |
|---|---|
| 1K | 7 |
| 2K | 10 |
| 4K | 15 |

## Examples

```python
# Real-time info grounding
gen = pony_flash.images.generate(
    model="nano-banana-2",
    prompt="Today's NBA scores as a sports infographic",
    resolution="2K",
    google_search=True,
)

# Multi-image blending
gen = pony_flash.images.generate(
    model="nano-banana-2",
    prompt="Combine these photos into a collage with consistent lighting",
    reference_images=[open("photo1.jpg", "rb"), open("photo2.jpg", "rb")],
    resolution="4K",
    aspect_ratio="16:9",
)
```
