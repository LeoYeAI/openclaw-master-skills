---
name: wan
description: "Generate AI videos and images using Alibaba's Wan 2.6 and Wan 2.5 — featuring text-to-video, image-to-video, video-to-video, text-to-image, and image editing with up to 1080p resolution, 15-second duration, multi/single camera shot types, audio-guided generation, and prompt expansion. Supports 18 model variants across 2 generations. Available via Atlas Cloud API at up to 30% off standard pricing. Use this skill whenever the user wants to generate AI videos, create video clips, animate images, edit videos, generate images, edit photos, or mentions Wan, Alibaba video, Tongyi video, Wanx, or Wan 2.6/2.5. Also trigger when users ask to create product demos, marketing videos, social media reels, animated scenes, cinematic clips, video-to-video transfers, character-consistent video edits, multi-camera shots, or any visual content using AI."
source: "https://github.com/AtlasCloudAI/nano-banana-2-skill"
homepage: "https://github.com/AtlasCloudAI/nano-banana-2-skill"
metadata:
  openclaw:
    requires:
      env:
        - ATLASCLOUD_API_KEY
    primaryEnv: ATLASCLOUD_API_KEY
---

# Wan 2.6 & 2.5 — AI Video & Image Generation by Alibaba

Generate AI videos and images using Alibaba's Wan 2.6 and Wan 2.5 — featuring text-to-video, image-to-video, video-to-video, text-to-image, and image editing with up to 1080p resolution, 15-second duration, multi/single camera modes, audio-guided generation, and built-in prompt expansion.

Wan 2.6 is the latest flagship model with cinematic motion quality, multi-camera shot types, audio URL input for guided generation, and video-to-video transfer with character-level prompt control. Wan 2.5 offers a cost-effective alternative with 480p support and Flash variants for rapid prototyping.

> **Data usage note**: This skill sends text prompts, image URLs, audio URLs, and video files to the Atlas Cloud API (`api.atlascloud.ai`) for generation. No data is stored locally beyond the downloaded output files. API usage incurs charges based on resolution, duration, and model selected.

---

## Key Capabilities

- **Text-to-Video** — Generate video clips from text descriptions with optional audio (2.6 / 2.5)
- **Image-to-Video** — Animate still images into dynamic video (2.6 / 2.5)
- **Video-to-Video** — Transfer style or replace characters in existing videos using `characterX` prompt notation (2.6)
- **Text-to-Image** — Generate images from text descriptions, 27 preset sizes (2.6)
- **Image Editing** — Edit images with prompt-based instructions, up to 4 reference images (2.6)
- **Audio-Guided Generation** — Provide an audio URL to guide video generation with synchronized sound (2.6)
- **Multi/Single Camera** — `multi_camera` for dynamic shots, `single_camera` for stable framing (2.6)
- **Prompt Expansion** — Built-in prompt optimization for better results
- **Up to 1080p** — Resolutions: 480p, 720p, 1080p
- **Up to 15s** — Duration: 5/10/15 seconds (2.6), 5/10 seconds (2.5)
- **Flash Variants** — Fast, budget-friendly generation for drafts (2.6 I2V Flash, 2.5 Fast)

---

## Setup

1. Sign up at https://www.atlascloud.ai
2. Console → API Keys → Create new key
3. Set env: `export ATLASCLOUD_API_KEY="your-key"`

The API key is tied to your Atlas Cloud account and its pay-as-you-go balance. All usage is billed to this account. Atlas Cloud does not currently support scoped keys — the key grants access to all models available on your account.

---

## Script Usage

This skill includes Python scripts for both video and image generation. Zero external dependencies required.

### List available models

```bash
python scripts/generate_video.py list-models
python scripts/generate_image.py list-models
```

### Generate a video

```bash
python scripts/generate_video.py generate \
  --model "alibaba/wan-2.6/text-to-video" \
  --prompt "Your prompt here" \
  --output ./output \
  duration=5
```

### Generate an image

```bash
python scripts/generate_image.py generate \
  --model "alibaba/wan-2.6/text-to-image" \
  --prompt "Your prompt here" \
  --output ./output
```

### Image-to-video

```bash
python scripts/generate_video.py generate \
  --model "alibaba/wan-2.6/image-to-video" \
  --image "https://example.com/photo.jpg" \
  --prompt "Animate this scene" \
  --output ./output \
  resolution=1080p duration=5
```

### Upload a local file

```bash
python scripts/generate_video.py upload ./local-file.jpg
```

Run `python scripts/generate_video.py generate --help` or `python scripts/generate_image.py generate --help` for all options. Extra model params can be passed as key=value.

---

## Pricing

### Wan 2.6 — Video Models (per second, by resolution)

All video prices are per second of video generated. Atlas Cloud pricing varies by resolution.

#### Text-to-Video & Video-to-Video

| Resolution | fal.ai | Atlas Cloud | Savings |
|:----------:|:------:|:-----------:|:-------:|
| **480p** | - | **$0.04/s** | - |
| **720p** | $0.10/s | **$0.08/s** | 20% off |
| **1080p** | $0.15/s | **$0.12/s** | 20% off |

#### Image-to-Video

| Resolution | fal.ai | Atlas Cloud | Savings |
|:----------:|:------:|:-----------:|:-------:|
| **720p** | $0.10/s | **$0.10/s** | - |
| **1080p** | $0.15/s | **$0.15/s** | - |

#### Image-to-Video Flash

| Resolution | Atlas Cloud |
|:----------:|:-----------:|
| **All** | **$0.018/s** |

### Wan 2.6 — Image Models (per image)

| Model | Original | Atlas Cloud | Savings |
|-------|:--------:|:-----------:|:-------:|
| Text-to-Image | ~~$0.03~~ | **$0.021** | 30% off |
| Image Edit | ~~$0.035~~ | **$0.021** | 40% off |

### Wan 2.5 — Video Models (per second, flat rate)

| Model | Atlas Cloud | Duration |
|-------|:-----------:|----------|
| Text-to-Video | **$0.035/s** | 5/10 seconds |
| Image-to-Video | **$0.035/s** | 5/10 seconds |

> fal.ai pricing sourced from [fal.ai/models/wan](https://fal.ai/models/fal-ai/wan/v2.6/text-to-video).

---

## Available Models

### Wan 2.6 Video

| Model ID | Type | Resolution | Duration |
|----------|------|:----------:|:--------:|
| `alibaba/wan-2.6/text-to-video` | Text-to-Video | 480p–1080p | 5/10/15s |
| `alibaba/wan-2.6/image-to-video` | Image-to-Video | 720p–1080p | 5/10/15s |
| `alibaba/wan-2.6/image-to-video-flash` | Image-to-Video (Fast) | 720p–1080p | 5/10/15s |
| `alibaba/wan-2.6/video-to-video` | Video-to-Video | 480p–1080p | 5/10s |

### Wan 2.6 Image

| Model ID | Type | Max Size |
|----------|------|:--------:|
| `alibaba/wan-2.6/text-to-image` | Text-to-Image | 2184×936 |
| `alibaba/wan-2.6/image-edit` | Image Editing | 24 presets |

### Wan 2.5 Video

| Model ID | Type | Resolution | Duration |
|----------|------|:----------:|:--------:|
| `alibaba/wan-2.5/text-to-video` | Text-to-Video | 480p–1080p | 5/10s |
| `alibaba/wan-2.5/image-to-video` | Image-to-Video | 480p–1080p | 5/10s |

---

## Parameters

### Wan 2.6 — Text-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description |
| `negative_prompt` | string | No | - | What to exclude from the video |
| `size` | string | No | 1280*720 | Output size (see Size Options below) |
| `duration` | integer | No | 5 | 5, 10, or 15 seconds |
| `shot_type` | string | No | - | `multi_camera` for dynamic shots, `single_camera` for stable framing |
| `audio` | string | No | - | Audio URL to guide generation with synchronized sound |
| `generate_audio` | boolean | No | false | Generate synchronized audio |
| `enable_prompt_expansion` | boolean | No | false | Expand prompt for better results |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Image-to-Video

Same as text-to-video (without `size`), plus:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | - | Source image URL |
| `resolution` | string | No | 720p | 720p, 1080p |

### Wan 2.6 — Video-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description (use `character1`, `character2` to reference characters in video) |
| `negative_prompt` | string | No | - | What to exclude |
| `videos` | array | Yes | - | Source video URLs (max 100MB each, 2-30s duration) |
| `size` | string | No | 1280*720 | Output size |
| `duration` | integer | No | 5 | 5 or 10 seconds |
| `shot_type` | string | No | - | `multi_camera` or `single_camera` |
| `enable_prompt_expansion` | boolean | No | false | Expand prompt for better results |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Text-to-Image

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Image description |
| `negative_prompt` | string | No | - | What to exclude |
| `size` | string | No | 1024*1024 | Output size (27 presets, see below) |
| `enable_prompt_expansion` | boolean | No | false | Expand prompt |
| `enable_sync_mode` | boolean | No | false | Wait for result synchronously |
| `enable_base64_output` | boolean | No | false | Return Base64 instead of URL |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Image Edit

Same as text-to-image, plus:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `images` | array | Yes | - | Images to edit (max 4, 384-5000px per side) |

### Wan 2.5 — Text-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description |
| `negative_prompt` | string | No | - | What to exclude |
| `size` | string | No | 1280*720 | Output size (13 presets, including 480p) |
| `duration` | integer | No | 5 | 5 or 10 seconds |
| `audio` | string | No | - | Audio URL for guided generation |
| `generate_audio` | boolean | No | false | Generate synchronized audio |
| `enable_prompt_expansion` | boolean | No | false | Expand prompt |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.5 — Image-to-Video

Same as Wan 2.5 text-to-video (without `size`), plus:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | - | Source image URL |
| `resolution` | string | No | 720p | 480p, 720p, 1080p |

### Video Size Options (Wan 2.6)

**T2V / V2V (10 presets):**
`1280*720`, `720*1280`, `960*960`, `1920*1080`, `1080*1920`, `1280*960`, `960*1280`, `1920*816`, `816*1920`, `1280*544`

**Image Size Options (Wan 2.6 — 27 presets):**
`1024*1024`, `1280*720`, `720*1280`, `1280*960`, `960*1280`, `1536*1024`, `1024*1536`, `1280*1280`, `1536*1536`, `2048*1024`, `1024*2048`, `1536*1280`, `1280*1536`, `1680*720`, `720*1680`, `2016*864`, `864*2016`, `1536*864`, `864*1536`, `2184*936`, `936*2184`, `1400*1050`, `1050*1400`, `1680*1050`, `1050*1680`, `1176*1176`, `1560*1560`

---

## Workflow: Submit → Poll → Download

### Text-to-Video Example (Wan 2.6)

```bash
# Step 1: Submit
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/text-to-video",
    "prompt": "A drone shot flying over ancient ruins at golden hour, camera slowly descending toward a central courtyard",
    "size": "1920*1080",
    "duration": 10,
    "shot_type": "multi_camera",
    "generate_audio": true,
    "enable_prompt_expansion": true
  }'
# Returns: { "code": 200, "data": { "id": "prediction-id" } }

# Step 2: Poll (every 5 seconds until completed)
curl -s "https://api.atlascloud.ai/api/v1/model/prediction/{prediction-id}" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY"
# Returns: { "code": 200, "data": { "status": "completed", "outputs": ["https://...video-url..."] } }

# Step 3: Download
curl -o output.mp4 "VIDEO_URL_FROM_OUTPUTS"
```

### Image-to-Video Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/image-to-video",
    "image": "https://example.com/landscape.jpg",
    "prompt": "The camera slowly zooms in as clouds drift across the sky and leaves rustle in the wind",
    "resolution": "1080p",
    "duration": 5,
    "generate_audio": true
  }'
```

### Video-to-Video Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/video-to-video",
    "videos": ["https://example.com/original-video.mp4"],
    "prompt": "Transform character1 into a cartoon anime character, keep the background unchanged",
    "size": "1280*720",
    "duration": 5,
    "shot_type": "single_camera"
  }'
```

### Audio-Guided Generation Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/text-to-video",
    "prompt": "A jazz band performing on stage, musicians playing saxophone and piano",
    "audio": "https://example.com/jazz-music.mp3",
    "size": "1920*1080",
    "duration": 10
  }'
```

### Text-to-Image Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/text-to-image",
    "prompt": "A cyberpunk cityscape at night, neon signs reflected in rain puddles, photorealistic",
    "size": "1680*720",
    "enable_prompt_expansion": true
  }'
# Returns: { "code": 200, "data": { "id": "prediction-id" } }
```

### Image Editing Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/image-edit",
    "prompt": "Change the background to a sunset beach scene, keep the person unchanged",
    "images": ["https://example.com/photo.jpg"],
    "size": "1280*720"
  }'
```

### Image-to-Video Flash Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/image-to-video-flash",
    "image": "https://example.com/portrait.jpg",
    "prompt": "The person slowly turns and smiles",
    "resolution": "720p",
    "duration": 5
  }'
```

### Polling Logic

- `processing` / `starting` / `running` → wait 5s, retry (typically takes ~30-120s for video, ~5-10s for image)
- `completed` / `succeeded` → done, get URL from `data.outputs[]`
- `failed` → error, read `data.error`

### Atlas Cloud MCP Tools (if available)

If the Atlas Cloud MCP server is configured, use built-in tools:

```
atlas_generate_video(model="alibaba/wan-2.6/text-to-video", params={...})
atlas_generate_image(model="alibaba/wan-2.6/text-to-image", params={...})
atlas_get_prediction(prediction_id="...")
```

---

## Implementation Guide

1. **Determine task type**:
   - Text-to-video: user describes a scene/action in text → **2.6 T2V** or **2.5 T2V**
   - Image-to-video: user provides an image to animate → **2.6 I2V** or **2.6 I2V Flash** (budget)
   - Video-to-video: user wants to transform an existing video → **2.6 V2V**
   - Text-to-image: user wants to generate an image → **2.6 T2I**
   - Image editing: user wants to modify existing images → **2.6 Image Edit**

2. **Choose model version**:
   - **Wan 2.6** (recommended): Latest generation, best quality, multi-camera, audio-guided, V2V
   - **Wan 2.6 Flash**: Budget I2V at $0.018/s — ideal for drafts
   - **Wan 2.5**: Cost-effective at $0.035/s flat rate, supports 480p

3. **Extract parameters**:
   - Prompt: describe scene, action, camera movement
   - Negative prompt: exclude undesired elements ("blurry, distorted, watermark")
   - Resolution: 480p for drafts, 720p default, 1080p for final output
   - Duration: 5s default, up to 15s for 2.6, up to 10s for 2.5
   - Shot type (2.6 only): `multi_camera` for dynamic shots, `single_camera` for stable framing
   - Audio: provide URL for audio-guided generation, or set `generate_audio: true`
   - Prompt expansion: set `enable_prompt_expansion: true` for auto-optimized prompts

4. **Execute**: POST to generateVideo/generateImage API → poll result → download

5. **Present result**: show file path, offer to play/open

## Prompt Tips

- **Scene + Action**: "A samurai draws his sword in a bamboo forest at dawn, mist rising from the ground"
- **Camera direction**: "Camera slowly dollies forward...", "Aerial tracking shot of...", "First-person POV walking through..."
- **Multi-camera**: Use `shot_type: "multi_camera"` with prompts like "Cut between close-up and wide shot..."
- **V2V character control**: Reference characters as `character1`, `character2` — e.g., "Transform character1 into an anime character"
- **Audio-guided**: Provide an audio URL to sync video with music, dialogue, or sound effects
- **Negative prompts**: "blurry, low quality, distorted faces, watermark, text overlay"

---

## Model Comparison

| Feature | Wan 2.6 | Wan 2.5 |
|---------|:-------:|:-------:|
| Video T2V Price (720p) | $0.08/s | $0.035/s |
| Video I2V Price (720p) | $0.10/s | $0.035/s |
| Max Resolution | 1080p | 1080p |
| Max Duration | 15s | 10s |
| Shot Type Control | Yes | No |
| Audio-Guided | Yes | Yes |
| Video-to-Video | Yes | No |
| Text-to-Image | Yes ($0.021) | No |
| Image Editing | Yes ($0.021) | No |
| Flash/Fast Variants | I2V Flash ($0.018/s) | Yes |
| Prompt Expansion | Yes | Yes |
