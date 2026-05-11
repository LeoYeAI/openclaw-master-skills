# AI Image Module

Generate images from text prompts or edit existing images with AI-powered models.

## Supported Task Types

| Type | Description | Required Params |
|------|-------------|-----------------|
| `text2image` | **Text-to-Image** — generate images from a text prompt | `--model`, `--prompt`, `--aspect-ratio` |
| `image_edit` | **Image Edit** — edit images with prompt + reference images | `--model`, `--prompt`, `--aspect-ratio`, `--input-images` |

## Subcommands

| Subcommand | When to use | Polls? |
|------------|-------------|--------|
| `run` | **Default.** New request, start to finish | Yes — waits until done |
| `submit` | Batch: fire multiple tasks without waiting | No — exits immediately |
| `query` | Recovery: resume polling a known `taskId` | Yes — waits until done |
| `list-models` | Check models, constraints, and supported ratios | No |
| `estimate-cost` | Estimate credit cost before running | No |

## Usage

```bash
python {baseDir}/scripts/ai_image.py <subcommand> --type <text2image|image_edit> [options]
```

## Examples

### List Models

```bash
python {baseDir}/scripts/ai_image.py list-models --type text2image
python {baseDir}/scripts/ai_image.py list-models --type image_edit --json
```

### Text-to-Image

```bash
python {baseDir}/scripts/ai_image.py run \
  --type text2image \
  --model "Nano Banana 2" \
  --prompt "A futuristic city skyline at dusk, neon lights reflected on wet streets" \
  --aspect-ratio "16:9" \
  --resolution "2K" \
  --count 2
```

Fixed-price model (no resolution):

```bash
python {baseDir}/scripts/ai_image.py run \
  --type text2image \
  --model "GPT Image 1.5" \
  --prompt "A watercolor painting of a cat" \
  --aspect-ratio "1:1"
```

### Image Edit

```bash
python {baseDir}/scripts/ai_image.py run \
  --type image_edit \
  --model "Nano Banana 2" \
  --prompt "Change the background to a snowy mountain landscape" \
  --aspect-ratio "auto" \
  --resolution "2K" \
  --input-images photo.jpg
```

Multi-image reference:

```bash
python {baseDir}/scripts/ai_image.py run \
  --type image_edit \
  --model "Nano Banana 2" \
  --prompt "Blend the style of both images" \
  --aspect-ratio "1:1" \
  --resolution "2K" \
  --input-images style.jpg content.jpg \
  --count 2
```

### Cost Estimation

```bash
python {baseDir}/scripts/ai_image.py estimate-cost \
  --type text2image --model "Nano Banana 2" --resolution "2K" --count 2
```

### Download Results

```bash
python {baseDir}/scripts/ai_image.py run \
  --type text2image --model "Nano Banana 2" \
  --prompt "Northern lights" --aspect-ratio "16:9" --resolution "2K" \
  --output-dir ./results
```

## Options

| Option | Description |
|--------|-------------|
| `--type` | `text2image` or `image_edit` (required) |
| `--model` | Model **display name** (required) |
| `--prompt` | Text prompt (required) |
| `--aspect-ratio` | Aspect ratio (required), e.g. `"16:9"`, `"1:1"`, `"auto"` |
| `--resolution` | `"512p"`, `"1K"`, `"2K"`, `"4K"` — model-dependent |
| `--count` | Number of images (1-4, default: 1) |
| `--board-id` | Board ID |
| `--input-images` | Reference image fileIds/local paths (image_edit only) |
| `--timeout` | Max polling time (default: 300) |
| `--interval` | Polling interval (default: 3) |
| `--output-dir` | Download results to directory |
| `--json` | Full JSON response |
| `-q, --quiet` | Suppress status messages |

## Model Recommendation

> **Nano Banana 2 is the top recommendation for all image tasks.**
> Best overall quality, 14 aspect ratios, up to 4K, 14 reference images for editing.

| Use Case | Recommended Models | Why |
|----------|--------------------|-----|
| **Best overall (default)** | **Nano Banana 2** | Strongest all-round model |
| **Budget** | Seedream 4.0 (0.15/img), Grok Image (0.15/img) | Lowest cost |
| **No-resolution simplicity** | GPT Image 1.5, Kontext-Pro | No resolution param needed |
| **Auto aspect ratio** | Seedream 5.0, Seedream 4.5 | `auto` ratio |

**Defaults:**
- text2image → `Nano Banana 2`
- image_edit → `Nano Banana 2`

## Key Notes

- `aspectRatio` is always required; image_edit models additionally support `"auto"`
- `resolution` is required for some models, forbidden for others — check via `list-models`
- **Imagen 4** is only available for text2image, not image_edit
