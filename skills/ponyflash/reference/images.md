# Images API Reference

## Method

### `pony_flash.images.generate(**kwargs) -> Generation`

Generate images and wait for completion. Returns `Generation` with output URLs.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | `str` | Yes | — | Model ID (e.g. `"nanobanana-pro"`, `"nanobanana"`) |
| `prompt` | `str` | Yes | — | Text description of the image to generate |
| `size` | `str` | No | — | Output size (e.g. `"1K"`, `"2K"`, `"4K"`) |
| `n` | `int` | No | — | Number of images to generate |
| `quality` | `str` | No | — | Quality level |
| `output_format` | `str` | No | — | Output format |
| `images` | `List[FileInput]` | No | — | Reference/input images for editing |
| `mask` | `FileInput` | No | — | Mask image for inpainting |
| `context` | `str` | No | — | Additional context for the generation |

## Return type: Generation

| Field | Type | Description |
|---|---|---|
| `request_id` | `str` | Request ID |
| `status` | `"queued" \| "running" \| "succeeded" \| "failed"` | Current status |
| `outputs` | `List[GenerationOutput]` | Output items |
| `usage` | `GenerationUsage \| None` | Credit usage |
| `error` | `GenerationError \| None` | Error details if failed |

**Convenience properties:** `gen.url` (first URL), `gen.urls` (all URLs), `gen.credits` (credits used).

## Example

```python
gen = pony_flash.images.generate(
    model="nanobanana-pro",
    prompt="A cyberpunk cityscape at night",
    size="2K",
    n=2,
)
for url in gen.urls:
    print(url)
```

## Available models

- [nanobanana-pro / nanobanana](models/nanobanana-pro.md) — sizes (1K/2K/4K), aspect ratios, credit costs, image-to-image

For the full model list, see [models/INDEX.md](models/INDEX.md).
