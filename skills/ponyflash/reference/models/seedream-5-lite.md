# seedream-5-lite — Image Generation (ByteDance)

ByteDance's image model with built-in reasoning, example-based editing, and batch generation. Lowest cost per image. Supports up to 3K resolution.

## Parameters

```python
gen = pony_flash.images.generate(
    model="seedream-5-lite",
    prompt="A color film portrait with shallow depth of field",
    resolution="2K",
    aspect_ratio="3:2",
)
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | str | Yes | — | Text description of the image |
| `resolution` | str | No | `"2K"` | `"2K"`, `"3K"` |
| `aspect_ratio` | str | No | `"match_input_image"` | See values below |
| `output_format` | str | No | `"png"` | `"png"`, `"jpg"` |
| `reference_images` | List[FileInput] | No | — | Up to 14 reference images |
| `n` | int | No | `1` | Number of images to generate (1-15) |

### aspect_ratio values

`match_input_image`, `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`, `21:9`

### Extra parameters (via **extra_body)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sequential_image_generation` | str | `"disabled"` | `"disabled"` or `"auto"` — auto lets model generate multiple related images (storyboards, character sheets) |

## Pricing

4 credits/image (all resolutions)

## Examples

```python
# Example-based editing: show before/after pair, apply to new image
gen = pony_flash.images.generate(
    model="seedream-5-lite",
    prompt="Apply the same color grading transformation",
    reference_images=[
        open("before.jpg", "rb"),
        open("after.jpg", "rb"),
        open("new_photo.jpg", "rb"),
    ],
    resolution="2K",
)

# Batch generation: storyboard
gen = pony_flash.images.generate(
    model="seedream-5-lite",
    prompt="A series of 4 illustrations of a courtyard across four seasons",
    n=4,
    resolution="2K",
    aspect_ratio="16:9",
    sequential_image_generation="auto",
)
```
