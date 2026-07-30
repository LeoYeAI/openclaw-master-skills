# Seedance Video Generation Skill (BytePlus International)

Generate AI videos using **ByteDance Seedance** models via the **BytePlus Ark API** (International version).

> This skill is designed for [Claude Code](https://claude.com/claude-code) and allows you to generate professional AI videos directly from your terminal using natural language prompts.

## Features

- **Text-to-Video**: Generate videos from text descriptions
- **Image-to-Video**: Animate images using first frame, first+last frame, or reference images
- **Audio Generation**: Seedance 1.5 Pro can generate synchronized voice, sound effects, and music
- **Draft Mode**: Preview videos at lower cost before generating the final version
- **Multiple Models**: Support for Seedance 1.5 Pro, 1.0 Pro, 1.0 Pro Fast, and 1.0 Lite
- **Flexible Output**: Control resolution (480p/720p/1080p), aspect ratio, duration, and more

## Quick Start

### 1. Get Your API Key

Sign up at [BytePlus ModelArk Console](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey) and create an API Key.

### 2. Set Environment Variable

```bash
export ARK_API_KEY="your-byteplus-api-key-here"
```

### 3. Install the Skill

Copy the skill folder to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/seedance-video-byteplus
# Copy SKILL.md and seedance_byteplus.py to the directory
```

### 4. Use with Claude Code

Simply ask Claude to generate a video:

```
/seedance-video-byteplus A kitten yawning at the camera in slow motion
```

Or use the Python CLI directly:

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A kitten yawning at the camera" --wait --download ~/Desktop
```

## Supported Models

| Model | Model ID | Key Features |
|-------|----------|-------------|
| **Seedance 1.5 Pro** | `seedance-1-5-pro-251215` | Latest model with audio, draft mode, adaptive ratio |
| **Seedance 1.0 Pro** | `seedance-1-0-pro-250428` | High quality, first frame + last frame support |
| **Seedance 1.0 Pro Fast** | `seedance-1-0-pro-fast-250528` | Faster generation, first frame only |
| **Seedance 1.0 Lite T2V** | `seedance-1-0-lite-t2v-250219` | Text-to-video only, cost effective |
| **Seedance 1.0 Lite I2V** | `seedance-1-0-lite-i2v-250219` | Reference images (1-4), first/last frame |

## Code Examples

### Example 1: Text-to-Video

Generate a video from a text prompt with default settings (720p, 16:9, 5 seconds, with audio).

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A golden retriever running through a field of sunflowers at sunset, cinematic lighting" \
  --wait --download ~/Desktop
```

**curl equivalent:**
```bash
curl -s -X POST "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "seedance-1-5-pro-251215",
    "content": [{"type": "text", "text": "A golden retriever running through a field of sunflowers at sunset, cinematic lighting"}],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p",
    "generate_audio": true
  }'
```

### Example 2: Image-to-Video (First Frame)

Animate a static image into a video.

```bash
# From a local file
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "The person slowly turns and smiles at the camera" \
  --image /path/to/portrait.jpg \
  --wait --download ~/Desktop

# From a URL
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "Gentle waves flowing across the landscape" \
  --image "https://example.com/landscape.jpg" \
  --ratio adaptive \
  --wait --download ~/Desktop
```

### Example 3: First + Last Frame Animation

Create a video that transitions from one image to another.

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A flower blooming from bud to full bloom" \
  --image bud.jpg \
  --last-frame bloom.jpg \
  --duration 8 \
  --wait --download ~/Desktop
```

### Example 4: Reference Images (Lite I2V)

Use 1-4 reference images to guide video generation. Use `[Image 1]`, `[Image 2]` in the prompt to reference specific images.

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A boy from [Image 1] and a corgi dog from [Image 2], playing on the lawn, 3D cartoon style" \
  --ref-images boy.jpg corgi.jpg \
  --model seedance-1-0-lite-i2v-250219 \
  --wait --download ~/Desktop
```

### Example 5: Draft Mode (Cost-Effective Preview)

Generate a low-cost preview first, then produce the final video if satisfied.

```bash
# Step 1: Create a draft video (480p, lower cost)
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "An astronaut walking on Mars, red dust swirling" \
  --draft true \
  --wait --download ~/Desktop

# Step 2: If the draft looks good, generate the final video
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --draft-task-id <DRAFT_TASK_ID_FROM_STEP_1> \
  --resolution 720p \
  --wait --download ~/Desktop
```

### Example 6: Video with Audio

Seedance 1.5 Pro can generate synchronized audio. Enclose dialogue in double quotes for speech.

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt 'A man stops a woman and says, "Remember, never point your finger at the moon." Wind rustling through trees in the background' \
  --generate-audio true \
  --wait --download ~/Desktop
```

### Example 7: Custom Video Specifications

```bash
# Vertical video for social media (9:16, 1080p, 10 seconds)
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A dancer performing a contemporary routine in a studio" \
  --ratio 9:16 --resolution 1080p --duration 10 \
  --wait --download ~/Desktop

# Ultra-wide cinematic (21:9)
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "Sweeping aerial shot of a mountain range at dawn" \
  --ratio 21:9 --duration 8 --resolution 720p \
  --camera-fixed true \
  --wait --download ~/Desktop
```

### Example 8: Consecutive Videos (Video Chain)

Generate multiple connected videos by using the last frame of one as the first frame of the next.

```bash
# Generate first video with last frame return
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A spaceship launches from a desert planet" \
  --return-last-frame true \
  --wait --download ~/Desktop
# Note the last_frame_url from the output

# Use last frame as first frame for the next video
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "The spaceship enters hyperspace with a flash of light" \
  --image "<LAST_FRAME_URL_FROM_PREVIOUS>" \
  --return-last-frame true \
  --wait --download ~/Desktop
```

### Example 9: Task Management

```bash
# List all recent tasks
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py list

# List only succeeded tasks
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py list --status succeeded

# Check a specific task status
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py status <TASK_ID>

# Cancel a queued task or delete a completed task
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py delete <TASK_ID>
```

### Example 10: Offline Mode (50% Cost Savings)

Use `flex` service tier for batch processing at half the price.

```bash
python3 ~/.claude/skills/seedance-video-byteplus/seedance_byteplus.py create \
  --prompt "A timelapse of clouds moving over a city skyline" \
  --service-tier flex \
  --wait --download ~/Desktop
```

## Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `seedance-1-5-pro-251215` | Model ID |
| `ratio` | string | `16:9` / `adaptive` | `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `adaptive` |
| `duration` | int | `5` | 4-12s (1.5 Pro) / 2-12s (others). `-1` = auto (1.5 Pro) |
| `resolution` | string | `720p` | `480p`, `720p`, `1080p` |
| `seed` | int | `-1` | Reproducibility seed. `-1` = random |
| `camera_fixed` | bool | `false` | Lock camera position |
| `watermark` | bool | `false` | Add watermark |
| `generate_audio` | bool | `true` | Audio generation (1.5 Pro only) |
| `draft` | bool | `false` | Draft preview mode (1.5 Pro, forces 480p) |
| `return_last_frame` | bool | `false` | Return last frame URL for chaining |
| `service_tier` | string | `default` | `default` (online) / `flex` (offline, 50% off) |
| `execution_expires_after` | int | `172800` | Timeout in seconds (3600-259200) |

## Image Requirements

- **Formats**: JPEG, PNG, WebP, BMP, TIFF, GIF (1.5 Pro also supports HEIC, HEIF)
- **Aspect ratio**: Width/Height between 0.4 and 2.5
- **Dimensions**: Shorter side > 300px, longer side < 6000px
- **Max file size**: 30 MB

## Demo Videos

Below are example prompts and the types of videos you can generate:

### Text-to-Video Demo
**Prompt**: `"A kitten yawning at the camera, soft morning light, shallow depth of field"`
- Model: Seedance 1.5 Pro
- Settings: 720p, 16:9, 5s, audio enabled
- Expected: A cute kitten yawning with ambient sound

### Image-to-Video Demo
**Prompt**: `"The person slowly turns their head and smiles warmly"`
- Model: Seedance 1.5 Pro
- Input: Portrait photo as first frame
- Settings: 720p, adaptive ratio, 5s
- Expected: Smooth animation of the portrait coming to life

### Draft-to-Final Demo
1. **Draft** (480p preview): Quick preview to check composition
2. **Final** (720p/1080p): Full quality render from approved draft

## API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create Task | POST | `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks` |
| Get Task | GET | `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{id}` |
| List Tasks | GET | `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks` |
| Delete Task | DELETE | `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{id}` |

## Useful Links

- [BytePlus ModelArk Console](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision)
- [API Key Management](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey)
- [Model List & Pricing](https://docs.byteplus.com/en/docs/ModelArk/1330310)
- [Model Billing](https://docs.byteplus.com/en/docs/ModelArk/1099320#video-generation)
- [API Call Guide](https://docs.byteplus.com/en/docs/ModelArk/1366799)
- [API Reference](https://docs.byteplus.com/en/docs/ModelArk/Video_Generation_API)
- [Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/1587797)
- [FAQs](https://docs.byteplus.com/en/docs/ModelArk/1359411)
- [Model Activation](https://console.byteplus.com/ark/region:ark+ap-southeast-1/openManagement?LLM=%7B%7D&tab=ComputerVision)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ARK_API_KEY not set` | Run `export ARK_API_KEY="your-key"` |
| `HTTP 401 Unauthorized` | Check your API key is valid and not expired |
| `HTTP 403 Forbidden` | Ensure the model is activated in your BytePlus console |
| `HTTP 429 Too Many Requests` | You've hit the rate limit. Wait and retry or use `flex` tier |
| Task stuck in `queued` | High demand. Wait or use `flex` tier for larger quota |
| Video URL expired | Video URLs are valid for 24 hours. Re-download or re-generate |

## License

This skill is provided as-is for use with Claude Code. The Seedance models and BytePlus API are products of ByteDance/BytePlus and subject to their terms of service.
