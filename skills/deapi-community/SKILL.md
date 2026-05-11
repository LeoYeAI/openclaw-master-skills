---
name: deAPI AI Media Suite (Community)
description: "The cheapest AI media API on the market. Generate images (Flux), music (AceStep), speech with voice cloning, transcribe video/audio, OCR, video generation, background removal, upscale, style transfer, and prompt enhancement — all through one unified API. Free $5 credit on signup."
homepage: https://deapi.ai
source: https://github.com/zrewolwerowanykaloryfer/deapi-clawdbot-skill
author: zrewolwerowanykaloryfer
license: MIT
requiredEnv:
  - DEAPI_API_KEY
metadata: {"clawdbot":{"requires":{"env":["DEAPI_API_KEY"]}}}
tags:
  - media
  - transcription
  - image-generation
  - tts
  - voice-cloning
  - music-generation
  - ocr
  - video
  - audio
  - embeddings
  - prompt-enhancement
---

# deAPI Media Generation

AI-powered media tools via decentralized GPU network. Get your API key at [deapi.ai](https://deapi.ai) (free $5 credit on signup).

## Setup

```bash
export DEAPI_API_KEY=your_api_key_here
```

## Available Functions

| Function | Use when user wants to... |
|----------|---------------------------|
| Transcribe (URL) | Transcribe YouTube, Twitch, Kick, X videos, or audio URLs |
| Transcribe (File) | Transcribe uploaded local audio/video file |
| Generate Image | Generate images from text descriptions (Flux models) |
| Generate Audio | Convert text to speech (TTS, 54+ voices, 8 languages) |
| Clone Voice | Clone a voice from short audio sample (3-10s) |
| Design Voice | Create new voice from text description |
| Generate Music | Generate music tracks, jingles, songs with vocals (AceStep) |
| Generate Video | Create video from text or animate images |
| Boost Prompt | Improve prompt quality before generation |
| OCR | Extract text from images |
| Remove Background | Remove background from images |
| Upscale | Upscale image resolution (2x/4x) |
| Transform Image | Apply style transfer to images (multi-image support) |
| Embeddings | Generate text embeddings for semantic search |
| Check Balance | Check account balance |
| Discover Models | List available models dynamically |

---

## Agent Safety: Input Sanitization

All curl examples use placeholders. Before substituting user input into shell commands:

1. **JSON payloads** — build JSON safely with `jq`, never inline raw strings:
   ```bash
   # ❌ UNSAFE — shell injection risk
   curl -d '{"prompt": "{USER_INPUT}"}'

   # ✅ SAFE — jq handles all escaping
   JSON=$(jq -n --arg p "$USER_INPUT" '{"prompt": $p}')
   curl -d "$JSON"
   ```

2. **URLs** — validate format before use:
   ```bash
   if [[ ! "$URL" =~ ^https?:// ]]; then
     echo "Invalid URL"; exit 1
   fi
   ```

3. **File paths** — verify file exists, use `@` prefix only with validated local paths:
   ```bash
   [[ -f "$FILE_PATH" ]] && curl -F "image=@$FILE_PATH"
   ```

4. **Never** pass raw user input directly into shell strings without escaping.

---

## Async Pattern (Important!)

**All deAPI requests are asynchronous.** Follow this pattern for every operation:

### 1. Submit Request
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/{endpoint}" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

Response contains `request_id`.

### 2. Poll Status (loop every 10 seconds)
```bash
curl -s "https://api.deapi.ai/api/v1/client/request-status/{request_id}" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

### 3. Handle Status
- `processing` → wait 10s, poll again
- `done` → fetch result from `result_url`
- `failed` → report error to user

### Common Error Handling
| Error | Action |
|-------|--------|
| 401 Unauthorized | Check DEAPI_API_KEY |
| 429 Rate Limited | Wait 60s and retry |
| 500 Server Error | Wait 30s and retry once |

---

## Model Selection Guide

**Image generation (txt2img):**
- Quick drafts / iterations → Klein (fastest)
- Photorealistic / detailed scenes → Flux1schnell (steps=8)
- Speed critical → ZImageTurbo

**Image transformation (img2img):**
- Logo/brand placement on objects → Qwen (preserves source better)
- Style transfer / artistic → Klein (faster, creative freedom)
- Combining multiple images → Klein (supports up to 3 images)

**Video generation:**
- Best quality → LTX-2 19B (no steps/guidance needed)
- Image animation → LTXv 13B (supports first_frame_image)

**TTS:**
- Quick narration → custom_voice + Kokoro
- Clone specific voice → voice_clone + reference audio
- Create new voice from description → voice_design

**Music:**
- Fast iteration → ACE-Step-v1.5-turbo (8 steps)
- Production quality → ACE-Step-v1.5 (32+ steps)

**Tip:** Model slugs change. When in doubt, call `GET /api/v1/client/models` to get the current list.

---

## Discover Available Models

Models change over time. Query the live list:

```bash
curl -s "https://api.deapi.ai/api/v1/client/models" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Accept: application/json"
```

Filter by task type:
```bash
# Only txt2img models
curl -s "https://api.deapi.ai/api/v1/client/models?filter[inference_types]=txt2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

Each model returns: `slug` (use in requests), `inference_types`, `info.limits`, `info.defaults`, `languages` (TTS), `loras` (image).

---

## Transcription (URL — YouTube, Audio, Video)

**Use when:** user wants to transcribe video from YouTube, X, Twitch, Kick or audio URLs.

**Endpoints:**
- Video (YouTube, mp4, webm): `vid2txt`
- Audio (mp3, wav, m4a, flac, ogg): `aud2txt`

**Request (video):**
```bash
JSON=$(jq -n --arg url "$VIDEO_URL" '{
  video_url: $url,
  include_ts: true,
  model: "WhisperLargeV3"
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/vid2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Request (audio):**
```bash
JSON=$(jq -n --arg url "$AUDIO_URL" '{
  audio_url: $url,
  include_ts: true,
  model: "WhisperLargeV3"
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/aud2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**After polling:** Present transcription with timestamps in readable format.

---

## Transcription (File Upload)

**Use when:** user has a local audio/video file to transcribe (not a URL).

**Endpoints:**
- Video file: `videofile2txt` (multipart/form-data)
- Audio file: `audiofile2txt` (multipart/form-data)

**Request (audio file):**
```bash
[[ -f "$AUDIO_PATH" ]] || { echo "File not found"; exit 1; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/audiofile2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "audio=@$AUDIO_PATH" \
  -F "include_ts=true" \
  -F "model=WhisperLargeV3"
```

**Request (video file):**
```bash
[[ -f "$VIDEO_PATH" ]] || { echo "File not found"; exit 1; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/videofile2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "video=@$VIDEO_PATH" \
  -F "include_ts=true" \
  -F "model=WhisperLargeV3"
```

---

## Image Generation (Flux)

**Use when:** user wants to generate images from text descriptions.

**Endpoint:** `txt2img`

**Models:**
| Model | API Name | Steps | Max Size | Notes |
|-------|----------|-------|----------|-------|
| Klein (default) | `Flux_2_Klein_4B_BF16` | 4 (fixed) | 1536px | Fastest, recommended |
| Flux | `Flux1schnell` | 4-10 | 2048px | Higher resolution |
| Turbo | `ZImageTurbo_INT8` | 4-10 | 1024px | Fastest inference |

**Request:**
```bash
JSON=$(jq -n --arg prompt "$PROMPT" --argjson seed "$RANDOM" '{
  prompt: $prompt,
  model: "Flux_2_Klein_4B_BF16",
  width: 1024,
  height: 1024,
  steps: 4,
  seed: ($seed % 1000000)
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Note:** Klein model does NOT support `guidance` parameter — omit it.

---

## Text-to-Speech (54+ Voices)

**Use when:** user wants to convert text to speech.

**Endpoint:** `txt2audio`

**Popular Voices:**
| Voice ID | Language | Description |
|----------|----------|-------------|
| `af_bella` | American EN | Warm, friendly (best quality) |
| `af_heart` | American EN | Expressive, emotional |
| `am_adam` | American EN | Deep, authoritative |
| `bf_emma` | British EN | Elegant (best British) |
| `jf_alpha` | Japanese | Natural Japanese female |
| `zf_xiaobei` | Chinese | Mandarin female |
| `ef_dora` | Spanish | Spanish female |
| `ff_siwis` | French | French female (best quality) |

Voice format: `{lang}{gender}_{name}` (e.g., `af_bella` = American Female Bella)

### TTS Mode 1: Custom Voice (default)

Use a predefined voice from the list above.

```bash
JSON=$(jq -n --arg text "$TEXT" '{
  text: $text,
  voice: "af_bella",
  model: "Kokoro",
  lang: "en-us",
  speed: 1.0,
  format: "mp3",
  sample_rate: 24000
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2audio" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Parameters:**
- `lang`: `en-us`, `en-gb`, `ja`, `zh`, `es`, `fr`, `hi`, `it`, `pt-br`
- `speed`: 0.5-2.0
- `format`: mp3/wav/flac/ogg
- `sample_rate`: 22050/24000/44100/48000

### TTS Mode 2: Voice Clone

Clone a voice from a short audio sample (3-10 seconds, max 10MB).

```bash
[[ -f "$REF_AUDIO" ]] || { echo "Reference audio not found"; exit 1; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2audio" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "text=$TEXT" \
  -F "model=Kokoro" \
  -F "mode=voice_clone" \
  -F "ref_audio=@$REF_AUDIO" \
  -F "ref_text=$REF_TRANSCRIPT" \
  -F "lang=en-us" \
  -F "speed=1.0" \
  -F "format=mp3" \
  -F "sample_rate=24000"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | Yes | `voice_clone` |
| `ref_audio` | Yes | Audio file (mp3/wav/flac/ogg/m4a), 3-10s, max 10MB |
| `ref_text` | No | Transcript of reference audio (improves accuracy) |

### TTS Mode 3: Voice Design

Generate a voice from a text description.

```bash
JSON=$(jq -n --arg text "$TEXT" --arg instruct "$VOICE_DESCRIPTION" '{
  text: $text,
  model: "Kokoro",
  mode: "voice_design",
  instruct: $instruct,
  lang: "en-us",
  speed: 1.0,
  format: "mp3",
  sample_rate: 24000
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2audio" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | Yes | `voice_design` |
| `instruct` | Yes | Natural language voice description (e.g. "A warm female voice with a slight British accent") |

---

## Music Generation (AceStep 1.5)

**Use when:** user wants to generate music tracks, jingles, or songs with vocals.

**Endpoint:** `txt2music`

**Models:**
| Model | Slug | Steps | Duration | Notes |
|-------|------|-------|----------|-------|
| AceStep 1.5 Turbo | `ACE-Step-v1.5-turbo` | 8 | 10-600s | Fast, recommended |
| AceStep 1.5 | `ACE-Step-v1.5` | 32+ | 10-600s | Higher quality, slower |

**Request:**
```bash
JSON=$(jq -n --arg caption "$CAPTION" --arg lyrics "$LYRICS" '{
  caption: $caption,
  model: "ACE-Step-v1.5-turbo",
  lyrics: $lyrics,
  duration: 30,
  bpm: 120,
  keyscale: "C major",
  timesignature: 4,
  inference_steps: 8,
  guidance_scale: 7,
  seed: -1,
  format: "mp3"
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2music" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Parameters:**
| Parameter | Required | Range | Description |
|-----------|----------|-------|-------------|
| `caption` | Yes | — | Text description of music style |
| `model` | Yes | — | Model slug |
| `lyrics` | No | — | Lyrics text. Use `"[Instrumental]"` for no vocals |
| `duration` | Yes | 10–600 sec | Track duration |
| `bpm` | No | 30–300 | Beats per minute |
| `keyscale` | No | — | Musical key (e.g. "C major", "F# minor") |
| `timesignature` | No | 2/3/4/6 | Time signature |
| `vocal_language` | No | — | Language code for vocals (en, es, fr, etc.) |
| `inference_steps` | Yes | 1–100 | Use 8 for turbo, 32+ for base |
| `guidance_scale` | Yes | 0–20 | Classifier-free guidance |
| `seed` | Yes | -1 or 0+ | -1 = random |
| `format` | Yes | mp3/wav/flac/ogg | Output format |

**Tips:**
- Turbo model with 8 steps is enough for most use cases
- For higher quality: base model with 32+ steps
- `[Instrumental]` in lyrics → track without vocals
- Duration > 120s may be more expensive — start shorter

---

## Prompt Enhancement (Boosters)

**Use when:** user wants to improve prompt quality before generating images/video/speech.

**Endpoints:**
| Booster | Endpoint | Use Case |
|---------|----------|----------|
| Image Prompt | `POST /prompt/image` | Improve txt2img prompts |
| Video Prompt | `POST /prompt/video` | Improve txt2video/img2video prompts |
| Speech Prompt | `POST /prompt/speech` | Improve TTS text |
| Img2Img Prompt | `POST /prompt/image2image` | Improve img2img prompts |
| Sample Prompts | `GET /prompts/samples` | Generate creative prompt ideas |

**Request (Image Booster):**
```bash
JSON=$(jq -n --arg p "$PROMPT" '{"prompt": $p}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/prompt/image" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Response:**
```json
{
  "prompt": "A majestic cat floating in outer space, surrounded by stars and galaxies, cosmic nebula colors, cinematic lighting, ultra-detailed, 8K",
  "negative_prompt": "blurry, low quality, distorted, deformed"
}
```

**Sample Prompts Generator:**
```bash
curl -s "https://api.deapi.ai/api/v1/client/prompts/samples?type=text2image&topic=cyberpunk" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

**Tip:** Use boosters before sending prompts to generation — output quality improves significantly.

---

## Video Generation

**Use when:** user wants to generate video from text or animate an image.

**Endpoints:**
- Text-to-Video: `txt2video` (multipart/form-data)
- Image-to-Video: `img2video` (multipart/form-data)

**Models:**
| Model | Slug | Max Size | FPS | Frames | Notes |
|-------|------|----------|-----|--------|-------|
| LTX-2 19B (preferred) | `Ltx2_19B_Dist_FP8` | 1024x1024 | 24 (fixed) | 49-241 | Best quality, no steps/guidance params |
| LTX-Video 13B | `Ltxv_13B_0_9_8_Distilled_FP8` | 768x768 | 30 (fixed) | 30-120 | steps=1, guidance=0 required |

**Request (text-to-video, LTX-2 — preferred):**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2video" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "prompt=$PROMPT" \
  -F "model=Ltx2_19B_Dist_FP8" \
  -F "width=768" \
  -F "height=768" \
  -F "frames=120" \
  -F "fps=24" \
  -F "seed=$((RANDOM % 1000000))"
```

**Parameters (LTX-2):**
| Parameter | Required | Constraints | Description |
|-----------|----------|-------------|-------------|
| `prompt` | Yes | — | Video description |
| `model` | Yes | — | `Ltx2_19B_Dist_FP8` |
| `width` | Yes | 512-1024 | Video width |
| `height` | Yes | 512-1024 | Video height |
| `frames` | Yes | 49-241 | Number of frames |
| `fps` | Yes | 24 (fixed) | Frames per second |
| `seed` | Yes | 0-999999 | Random seed |
| `steps` | No | Do NOT send | Not supported |
| `guidance` | No | Do NOT send | Not supported |

**Request (image-to-video):**
```bash
[[ -f "$IMAGE_PATH" ]] || { curl -s -o "$IMAGE_PATH" "$IMAGE_URL"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2video" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "first_frame_image=@$IMAGE_PATH" \
  -F "prompt=gentle movement, cinematic" \
  -F "model=Ltxv_13B_0_9_8_Distilled_FP8" \
  -F "width=512" \
  -F "height=512" \
  -F "guidance=0" \
  -F "steps=1" \
  -F "frames=120" \
  -F "fps=30" \
  -F "seed=$((RANDOM % 1000000))"
```

**Note:** Video generation can take 1-3 minutes.

---

## OCR (Image to Text)

**Use when:** user wants to extract text from an image.

**Endpoint:** `img2txt` (multipart/form-data)

**Request:**
```bash
[[ -f "$IMAGE_PATH" ]] || { curl -s -o "$IMAGE_PATH" "$IMAGE_URL"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@$IMAGE_PATH" \
  -F "model=Nanonets_Ocr_S_F16"
```

---

## Background Removal

**Use when:** user wants to remove background from an image.

**Endpoint:** `img-rmbg` (multipart/form-data)

**Request:**
```bash
[[ -f "$IMAGE_PATH" ]] || { curl -s -o "$IMAGE_PATH" "$IMAGE_URL"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img-rmbg" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@$IMAGE_PATH" \
  -F "model=Ben2"
```

**Result:** PNG with transparent background.

---

## Image Upscale (2x/4x)

**Use when:** user wants to upscale/enhance image resolution.

**Endpoint:** `img-upscale` (multipart/form-data)

**Models:**
| Scale | Model |
|-------|-------|
| 2x | `RealESRGAN_x2` |
| 4x | `RealESRGAN_x4` |

**Request:**
```bash
[[ -f "$IMAGE_PATH" ]] || { curl -s -o "$IMAGE_PATH" "$IMAGE_URL"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img-upscale" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@$IMAGE_PATH" \
  -F "model=RealESRGAN_x4"
```

---

## Image Transformation (Style Transfer)

**Use when:** user wants to transform image style, combine images, or apply AI modifications.

**Endpoint:** `img2img` (multipart/form-data)

**Models:**
| Model | API Name | Max Images | Guidance | Steps | Notes |
|-------|----------|------------|----------|-------|-------|
| Klein (default) | `Flux_2_Klein_4B_BF16` | 3 | N/A (ignore) | 4 (fixed) | Faster, multi-image |
| Qwen | `QwenImageEdit_Plus_NF4` | 1 | 7.5 | 10-50 (default 20) | More control |

**Request (Klein, supports up to 3 images):**
```bash
[[ -f "$IMAGE1" ]] || { curl -s -o "$IMAGE1" "$IMAGE_URL_1"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@$IMAGE1" \
  -F "prompt=$STYLE_PROMPT" \
  -F "model=Flux_2_Klein_4B_BF16" \
  -F "steps=4" \
  -F "seed=$((RANDOM % 1000000))"
```

**Request (Qwen, higher quality single image):**
```bash
[[ -f "$IMAGE1" ]] || { curl -s -o "$IMAGE1" "$IMAGE_URL"; }
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@$IMAGE1" \
  -F "prompt=$STYLE_PROMPT" \
  -F "model=QwenImageEdit_Plus_NF4" \
  -F "guidance=7.5" \
  -F "steps=20" \
  -F "seed=$((RANDOM % 1000000))"
```

**Example prompts:** "convert to watercolor painting", "anime style", "cyberpunk neon aesthetic"

---

## Text Embeddings

**Use when:** user needs embeddings for semantic search, clustering, or RAG.

**Endpoint:** `txt2embedding`

**Request:**
```bash
JSON=$(jq -n --arg text "$TEXT" '{
  input: $text,
  model: "Bge_M3_FP16"
}')
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2embedding" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON"
```

**Result:** 1024-dimensional vector (BGE-M3, multilingual)

---

## Check Balance

**Use when:** user wants to check remaining credits.

**Request:**
```bash
curl -s "https://api.deapi.ai/api/v1/client/balance" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

**Response:** `{ "data": { "balance": 4.25 } }`

---

## Pricing (Approximate)

| Operation | Cost |
|-----------|------|
| Transcription | ~$0.02/hour |
| Image Generation | ~$0.002/image |
| TTS | ~$0.001/1000 chars |
| Music Generation | ~$0.01/track |
| Video Generation | ~$0.05/video |
| OCR | ~$0.001/image |
| Remove BG | ~$0.001/image |
| Upscale | ~$0.002/image |
| Embeddings | ~$0.0001/1000 tokens |

Free $5 credit on signup at [deapi.ai](https://deapi.ai).

---

*Converted from [deapi-ai/claude-code-skills](https://github.com/deapi-ai/claude-code-skills) for Clawdbot/OpenClaw.*

---

## Security & Privacy Note

This skill provides documentation for the **deAPI.ai** REST API, a legitimate decentralized AI media service.

**Security:**
- All `curl` commands are **examples** showing how to call the API
- Requests go to `api.deapi.ai` (official deAPI endpoint)
- Local file paths are placeholders — use any suitable temporary location
- The skill itself does not execute code or download binaries
- API key is required and must be set by user via `DEAPI_API_KEY` environment variable

**Input sanitization:**
- All curl examples in this skill use `jq` for safe JSON construction
- Agents MUST NOT substitute raw user input directly into shell strings
- URL inputs should be validated (must start with `https://`)
- File paths should be verified before use (`[[ -f "$path" ]]`)

**Privacy considerations:**
- Media URLs you submit (YouTube links, images) are sent to deapi.ai for processing
- Generated results are returned via `result_url` which may be temporarily accessible via direct link
- Results are stored on deAPI's infrastructure — review their privacy policy for retention details
- Do not process sensitive/confidential media without understanding data handling

**Provenance:**
- Service provider: [deapi.ai](https://deapi.ai)
- Original skill source: [github.com/deapi-ai/claude-code-skills](https://github.com/deapi-ai/claude-code-skills)
- API documentation: [docs.deapi.ai](https://docs.deapi.ai)
