---
name: nsfw-video
description: "Generate AI videos for mature creative projects using Wan 2.2 Spicy (LoRA-tuned for NSFW, top recommended), Wan 2.6, Seedance 1.5, Vidu Q3-Pro, and other models with relaxed content policies via Atlas Cloud API. Designed for adult (18+) artistic and professional use cases including artistic film, fashion video, choreography, and mature animation. Wan 2.2 Spicy is purpose-built for mature content with LoRA fine-tuning at just $0.03/s. Also includes Wan 2.6 (up to 15s 1080p, audio-guided), Seedance v1.5 Pro (native audio-visual), and Vidu Q3-Pro (anime support). Supports text-to-video, image-to-video, and video-to-video. Use this skill when the user explicitly requests NSFW or mature video generation for legitimate adult creative work."
source: "https://github.com/AtlasCloudAI/nano-banana-2-skill"
homepage: "https://github.com/AtlasCloudAI/nano-banana-2-skill"
metadata:
  openclaw:
    requires:
      env:
        - ATLASCLOUD_API_KEY
    primaryEnv: ATLASCLOUD_API_KEY
---

# NSFW Video Generation — Adult Creative AI Video Models

Generate AI videos for mature creative projects using models with relaxed content policies. Intended for legitimate adult (18+) artistic and professional use cases such as artistic film, fashion video, choreography, and mature animation.

**Top recommended: Wan 2.2 Spicy** — purpose-built for mature content with LoRA fine-tuning, best NSFW quality at just $0.03/video. For general video generation, also consider Wan 2.6 (up to 15s 1080p, multi-camera).

> **Age restriction (18+)**: This skill is strictly for users aged 18 and above. The agent MUST confirm the user's age before first use by asking: "This skill generates mature content. Please confirm you are 18 years or older to proceed." If the user does not confirm, the agent MUST refuse to execute. Minors are strictly prohibited from using this skill.

> **Data usage note**: This skill sends text prompts, image URLs, audio URLs, and video files to the Atlas Cloud API (`api.atlascloud.ai`) for video generation. No data is stored locally beyond the downloaded output files.

> **Security note**: API keys are read from environment variables and passed via HTTP headers. All prompts are sent through JSON request bodies.

---

## Required Environment Variables

| Variable | Required | Description |
|----------|:--------:|-------------|
| `ATLASCLOUD_API_KEY` | **Yes** | Atlas Cloud API key for accessing video generation models |

## Setup

1. Sign up at https://www.atlascloud.ai
2. Console → API Keys → Create new key
3. Set env: `export ATLASCLOUD_API_KEY="your-key"`

The API key is tied to your Atlas Cloud account and its pay-as-you-go balance. All usage is billed to this account.

### Credential Safety

- **Use a dedicated key**: Create a separate API key for this skill rather than reusing keys from other applications. Revoke it when no longer needed.
- **Do not hardcode keys**: Always use environment variables (`export ATLASCLOUD_API_KEY="..."`) — never embed keys in scripts, code, or prompts.
- **Monitor usage**: Check Console → Usage regularly to track spending and detect anomalies.
- **Control your balance**: Atlas Cloud uses pay-as-you-go billing — only recharge the amount you plan to use to limit potential exposure.
- Atlas Cloud does not currently support scoped/limited keys — each key grants access to all models on your account. Use balance control as the primary safeguard.

---

## Script Usage

This skill includes a Python script for video generation. Zero external dependencies required.

### List available video models

```bash
python scripts/generate_video.py list-models
```

### Generate a video (text-to-video)

```bash
python scripts/generate_video.py generate \
  --model "MODEL_ID" \
  --prompt "Your prompt here" \
  --output ./output \
  duration=5 resolution=720p
```

### Generate a video (image-to-video)

```bash
python scripts/generate_video.py generate \
  --model "MODEL_ID" \
  --image "https://example.com/photo.jpg" \
  --prompt "Animate this scene" \
  --output ./output
```

### Upload a local file

```bash
python scripts/generate_video.py upload ./local-file.jpg
```

Run `python scripts/generate_video.py generate --help` for all options. Extra model params can be passed as key=value (e.g. `duration=10 shot_type=multi_camera`).

---

## Available Models

### Wan 2.2 Spicy (Alibaba) — Top Recommended for NSFW

Purpose-built for mature content generation with LoRA fine-tuning. Best NSFW quality, cheapest price. Image-to-Video only — provide a reference image + prompt to generate video.

| Model ID | Type | Price | Duration | Resolution |
|----------|------|:-----:|:--------:|:----------:|
| `alibaba/wan-2.2-spicy/image-to-video` | Image-to-Video | **$0.03/s** | 5/8s | 480p/720p |
| `alibaba/wan-2.2-spicy/image-to-video-lora` | I2V + Custom LoRA | **$0.04/s** | 5/8s | 480p/720p |

**Unique features**: LoRA fine-tuned specifically for mature content, custom LoRA support (up to 3 high-noise + 3 low-noise LoRAs), per-second pricing.

### Wan 2.6 (Alibaba) — Best General Quality

Best quality, most features, best price-performance ratio.

| Model ID | Type | Price | Duration | Resolution |
|----------|------|:-----:|:--------:|:----------:|
| `alibaba/wan-2.6/text-to-video` | Text-to-Video | $0.04-0.12/s | 5/10/15s | 480p–1080p |
| `alibaba/wan-2.6/image-to-video` | Image-to-Video | $0.10-0.15/s | 5/10/15s | 720p–1080p |
| `alibaba/wan-2.6/image-to-video-flash` | I2V Flash | $0.018/s | 5/10/15s | 720p–1080p |
| `alibaba/wan-2.6/video-to-video` | Video-to-Video | $0.04-0.12/s | 5/10s | 480p–1080p |

**Unique features**: Multi/single camera shot types, audio URL guided generation, `characterX` prompt notation for V2V, prompt expansion.

### Seedance v1.5 Pro (ByteDance) — Native Audio-Visual

| Model ID | Type | Price | Duration | Resolution |
|----------|------|:-----:|:--------:|:----------:|
| `bytedance/seedance-v1.5-pro/text-to-video` | Text-to-Video | $0.222/video | 5s | 720p/480p |
| `bytedance/seedance-v1.5-pro/image-to-video` | Image-to-Video | $0.222/video | 5s | 720p/480p |
| `bytedance/seedance-v1.5-pro/text-to-video-fast` | T2V Fast | $0.018/video | 5s | 720p |
| `bytedance/seedance-v1.5-pro/image-to-video-fast` | I2V Fast | $0.018/video | 5s | 720p |

**Unique features**: Native audio-visual joint generation, camera fixed control, start+end frame for I2V (`last_image`), 6 aspect ratios.

### Vidu Q3-Pro (Shengshu AI) — Whitelisted

| Model ID | Type | Price | Duration | Resolution |
|----------|------|:-----:|:--------:|:----------:|
| `vidu/q3-pro/text-to-video` | Text-to-Video | $0.06-0.16/s | flexible | 540p–1080p |
| `vidu/q3-pro/image-to-video` | Image-to-Video | $0.06-0.16/s | flexible | 540p–1080p |

**Unique features**: Anime style mode (`style: "anime"`), audio & BGM generation, movement amplitude control, 5 aspect ratios.

### Wan 2.5 (Alibaba) — Budget

| Model ID | Type | Price | Duration | Resolution |
|----------|------|:-----:|:--------:|:----------:|
| `alibaba/wan-2.5/text-to-video` | Text-to-Video | $0.035/s | 5/10s | 480p–1080p |
| `alibaba/wan-2.5/image-to-video` | Image-to-Video | $0.035/s | 5/10s | 480p–1080p |

---

## Quick Model Selection

| Priority | Model | Price Range | Best For |
|:--------:|-------|:-----------:|----------|
| 1 | **Wan 2.2 Spicy I2V** | $0.03/s | NSFW image-to-video, best mature content quality |
| 2 | **Wan 2.2 Spicy I2V LoRA** | $0.04/s | NSFW with custom LoRA styles |
| 3 | **Wan 2.6 T2V** | $0.04-0.12/s | General NSFW text-to-video, longest duration (15s) |
| 4 | **Wan 2.6 I2V Flash** | $0.018/s | Budget image animation, fast |
| 5 | **Seedance 1.5 Fast** | $0.018/video | Ultra-cheap drafts with audio |
| 6 | **Seedance 1.5 Pro** | $0.222/video | Best audio-visual sync |
| 7 | **Vidu Q3-Pro** | $0.06-0.16/s | Anime content, BGM |
| 8 | **Wan 2.5** | $0.035/s | Budget 480p option |

---

## Parameters

### Wan 2.2 Spicy — Image-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | - | Source image URL |
| `prompt` | string | Yes | - | Video description |
| `resolution` | string | No | 480p | 480p, 720p |
| `duration` | integer | No | 5 | 5 or 8 seconds |
| `seed` | integer | No | -1 | For reproducible results (-1 for random) |

### Wan 2.2 Spicy — Image-to-Video LoRA

Same as above, plus:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `high_noise_loras` | array | No | - | High-noise LoRA adapters (max 3), for stronger style influence |
| `low_noise_loras` | array | No | - | Low-noise LoRA adapters (max 3), for subtle style refinement |

### Wan 2.6 — Text-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description |
| `negative_prompt` | string | No | - | What to exclude |
| `size` | string | No | 1280*720 | Output size (10 presets) |
| `duration` | integer | No | 5 | 5, 10, or 15 seconds |
| `shot_type` | string | No | - | `multi_camera` or `single_camera` |
| `audio` | string | No | - | Audio URL for guided generation |
| `generate_audio` | boolean | No | false | Generate synchronized audio |
| `enable_prompt_expansion` | boolean | No | false | Auto-expand prompt |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Image-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | - | Source image URL |
| `prompt` | string | No | - | Motion description |
| `negative_prompt` | string | No | - | What to exclude |
| `resolution` | string | No | 720p | 720p, 1080p |
| `duration` | integer | No | 5 | 5, 10, or 15 seconds |
| `shot_type` | string | No | - | `multi_camera` or `single_camera` |
| `audio` | string | No | - | Audio URL |
| `generate_audio` | boolean | No | false | Generate audio |
| `enable_prompt_expansion` | boolean | No | false | Auto-expand prompt |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Video-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Use `character1`, `character2` to reference characters |
| `negative_prompt` | string | No | - | What to exclude |
| `videos` | array | Yes | - | Source video URLs (max 100MB each, 2-30s) |
| `size` | string | No | 1280*720 | Output size |
| `duration` | integer | No | 5 | 5 or 10 seconds |
| `shot_type` | string | No | - | `multi_camera` or `single_camera` |
| `enable_prompt_expansion` | boolean | No | false | Auto-expand prompt |
| `seed` | integer | No | random | For reproducible results |

### Seedance v1.5 Pro — Text-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description |
| `aspect_ratio` | string | No | 16:9 | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 |
| `duration` | integer | No | 5 | Duration in seconds |
| `resolution` | string | No | 720p | 720p, 480p |
| `generate_audio` | boolean | No | true | Native audio-visual generation |
| `camera_fixed` | boolean | No | false | Lock camera position |
| `seed` | integer | No | -1 | For reproducible results |

### Seedance v1.5 Pro — Image-to-Video

Same as T2V (prompt becomes optional), plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | Yes | Source image URL |
| `last_image` | string | No | End frame image URL for controlled motion |

### Vidu Q3-Pro — Text-to-Video

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video description (max 1500 chars) |
| `style` | string | No | general | general, anime |
| `resolution` | string | No | 720p | 540p, 720p, 1080p |
| `duration` | number | No | 5 | Duration in seconds |
| `aspect_ratio` | string | No | 4:3 | 16:9, 9:16, 4:3, 3:4, 1:1 |
| `movement_amplitude` | string | No | auto | auto, small, medium, large |
| `generate_audio` | boolean | No | true | Generate synchronized audio |
| `bgm` | boolean | No | true | Generate background music |
| `seed` | integer | No | -1 | For reproducible results |

### Vidu Q3-Pro — Image-to-Video

Same as T2V (without `style` and `aspect_ratio`), plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | Yes | Source image URL |

### Wan 2.6 Video Size Presets

`1280*720`, `720*1280`, `960*960`, `1920*1080`, `1080*1920`, `1280*960`, `960*1280`, `1920*816`, `816*1920`, `1280*544`

---

## API Workflow (All Models)

All models use the same 3-step flow: Submit → Poll → Download.

```bash
# Step 1: Submit — replace {PAYLOAD} with the model-specific JSON below
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateVideo" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{PAYLOAD}'
# Returns: { "code": 200, "data": { "id": "prediction-id" } }

# Step 2: Poll — every 5 seconds until status is completed/succeeded/failed
curl -s "https://api.atlascloud.ai/api/v1/model/prediction/{prediction-id}" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY"
# Returns: { "code": 200, "data": { "status": "completed", "outputs": ["https://...video-url..."] } }

# Step 3: Download
curl -o output.mp4 "VIDEO_URL_FROM_OUTPUTS"
```

**Polling status**:
- `processing` / `starting` / `running` → wait 5s, retry (typically 30-120s)
- `completed` / `succeeded` → done, get URL from `data.outputs[]`
- `failed` → error, read `data.error`

**MCP Tools** (if Atlas Cloud MCP server is configured):
```
atlas_generate_video(model="...", params={...})
atlas_get_prediction(prediction_id="...")
```

---

## Model Payload Examples

Only the JSON payload is shown below. Use with the generic workflow above.

### Wan 2.2 Spicy — I2V (Top Recommended)

```json
{
  "model": "alibaba/wan-2.2-spicy/image-to-video",
  "image": "https://example.com/reference.jpg",
  "prompt": "The woman slowly turns toward the camera, soft studio lighting, cinematic",
  "resolution": "720p",
  "duration": 5
}
```

### Wan 2.2 Spicy — I2V with Custom LoRA

```json
{
  "model": "alibaba/wan-2.2-spicy/image-to-video-lora",
  "image": "https://example.com/reference.jpg",
  "prompt": "Elegant movement with dramatic lighting, slow motion",
  "resolution": "720p",
  "duration": 8,
  "high_noise_loras": ["lora-url-1"],
  "low_noise_loras": ["lora-url-2"]
}
```

### Wan 2.6 — Text-to-Video

```json
{
  "model": "alibaba/wan-2.6/text-to-video",
  "prompt": "A couple dancing passionately in a dimly lit ballroom, dramatic lighting, cinematic slow motion",
  "size": "1920*1080",
  "duration": 10,
  "shot_type": "multi_camera",
  "generate_audio": true,
  "enable_prompt_expansion": true
}
```

### Wan 2.6 — Image-to-Video

```json
{
  "model": "alibaba/wan-2.6/image-to-video",
  "image": "https://example.com/portrait.jpg",
  "prompt": "The person slowly turns toward the camera, hair flowing in the wind",
  "resolution": "1080p",
  "duration": 5,
  "generate_audio": true
}
```

### Wan 2.6 — Video-to-Video

```json
{
  "model": "alibaba/wan-2.6/video-to-video",
  "videos": ["https://example.com/original.mp4"],
  "prompt": "Transform character1 into an elegant woman in a silk dress, keep the background and motion unchanged",
  "size": "1280*720",
  "duration": 5
}
```

### Seedance v1.5 Pro — Text-to-Video

```json
{
  "model": "bytedance/seedance-v1.5-pro/text-to-video",
  "prompt": "A woman performing a contemporary dance in a studio with dramatic spotlight, fluid movements",
  "aspect_ratio": "9:16",
  "resolution": "720p",
  "duration": 5,
  "generate_audio": true,
  "camera_fixed": true
}
```

### Seedance v1.5 Pro — Image-to-Video (with end frame)

```json
{
  "model": "bytedance/seedance-v1.5-pro/image-to-video",
  "image": "https://example.com/start-frame.jpg",
  "last_image": "https://example.com/end-frame.jpg",
  "prompt": "Smooth transition between the two poses",
  "resolution": "720p",
  "duration": 5,
  "generate_audio": true
}
```

### Vidu Q3-Pro — Anime

```json
{
  "model": "vidu/q3-pro/text-to-video",
  "prompt": "An anime girl in a hot spring, steam rising around her, cherry blossoms falling, warm lighting",
  "style": "anime",
  "resolution": "1080p",
  "duration": 5,
  "aspect_ratio": "16:9",
  "generate_audio": true,
  "bgm": true
}
```

---

## Implementation Guide

1. **Determine task type**:
   - NSFW image-to-video → **Wan 2.2 Spicy I2V** (top choice, $0.03/s)
   - NSFW I2V with custom style → **Wan 2.2 Spicy I2V LoRA** ($0.04/s)
   - Text-to-video → **Wan 2.6 T2V** (default) or **Seedance 1.5 T2V** (audio-visual)
   - General image-to-video → **Wan 2.6 I2V** or **I2V Flash** (budget)
   - Video-to-video → **Wan 2.6 V2V** (character replacement)
   - Anime content → **Vidu Q3-Pro** with `style: "anime"`
   - Budget/draft → **Seedance 1.5 Fast** ($0.018) or **Wan 2.6 I2V Flash** ($0.018/s)

2. **Choose model by priority**:
   - **Wan 2.2 Spicy** — Best for NSFW image-to-video, LoRA fine-tuned for mature content ($0.03/s)
   - **Wan 2.6** — Best overall quality, most features, longest duration (15s), T2V/V2V support
   - **Seedance 1.5 Pro** — Best audio-visual sync, start+end frame control
   - **Vidu Q3-Pro** — Best for anime NSFW, BGM generation
   - **Wan 2.5** — Budget option with 480p support

3. **Extract parameters**: Prompt, resolution, duration, negative prompt. Use `shot_type: "single_camera"` for stable framing in intimate scenes.

4. **Execute**: POST to generateVideo API → poll result → download MP4.

5. **Present result**: show file path, offer to play.

## Prompt Tips

- **Detailed descriptions**: Be specific about poses, expressions, lighting, camera angles
- **Camera control**: "Close-up", "Medium shot", "Full body", "POV"
- **Wan multi-camera**: Use `shot_type: "multi_camera"` for dynamic angle switches
- **Wan single-camera**: Use `shot_type: "single_camera"` for stable, continuous shots
- **V2V character swap**: Reference characters as `character1`, `character2` in prompt
- **Audio-guided**: Provide audio URL to sync video with music
- **Negative prompts**: "blurry, low quality, distorted, watermark, text overlay"
- **Seedance camera_fixed**: Set `true` to lock camera for scenes with focused subject motion
