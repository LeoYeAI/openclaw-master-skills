---
name: minimax-studio
description: >-
  Create voice, music, and video with MiniMax AI models. Unified skill for TTS voice synthesis (text-to-speech, voice cloning, voice design, multi-segment generation), music generation (songs, instrumentals), video creation (text-to-video, image-to-video, start-end frame, subject reference, templates, long-form multi-scene), and media processing (audio/video format conversion, concatenation, trimming, extraction). Use when user wants to generate speech audio, create songs or instrumental tracks, produce AI videos, clone or design voices, convert media formats, merge/split audio or video files, or work with MiniMax APIs.
---

# MiniMax Studio

Generate voice, music, and video content via MiniMax APIs. Includes voice cloning & voice design for custom voices, and FFmpeg-based media tools for audio/video format conversion, concatenation, trimming, and extraction.

## Output Directory

**All generated files MUST be saved to `minimax-output/` under the AGENT'S current working directory (NOT the skill directory).** Every script call MUST include an explicit `--output` / `-o` argument pointing to this location. Never omit the output argument or rely on script defaults.

**Rules:**
1. Before running any script, ensure `minimax-output/` exists in the agent's working directory (create if needed: `mkdir -p minimax-output`)
2. Always use absolute or relative paths from the agent's working directory: `--output minimax-output/video.mp4`
3. **Never** `cd` into the skill directory to run scripts — run from the agent's working directory using the full script path
4. Intermediate/temp files (segment audio, video segments, extracted frames) are automatically placed in `minimax-output/tmp/`. They can be cleaned up when no longer needed: `rm -rf minimax-output/tmp`

## Prerequisites

```bash
pip install -r requirements.txt   # requests, websockets, ffmpeg-python
brew install ffmpeg                # macOS
python scripts/check_environment.py
```

### API Key Configuration

The `MINIMAX_API_KEY` can be provided in two ways (either works):

1. **`.env` file** (recommended — persists across sessions):
   Create a `.env` file in the MiniMaxStudio project root (alongside SKILL.md):
   ```
   MINIMAX_API_KEY=sk-api-xxxxxxxxxxxxxxxxxxxxxxxx
   ```
   All scripts automatically load `.env` on startup. Environment variables take precedence over `.env` values.

2. **Environment variable**:
   ```bash
   export MINIMAX_API_KEY="sk-api-xxxxxxxxxxxxxxxxxxxxxxxx"
   ```

**IMPORTANT — When API Key is missing:**
Before running any script, check if `MINIMAX_API_KEY` is available (via env var or `.env` file). If it is NOT configured:
1. Ask the user to provide their MiniMax API key
2. Write the key to the `.env` file in the **MiniMaxStudio skill directory** (i.e., the directory containing this SKILL.md): `echo 'MINIMAX_API_KEY=sk-api-xxxxx' > <skill_directory>/.env`
3. Do NOT store the key in the agent's working directory — always write to the skill directory so it persists for all future sessions
4. The key starts with `sk-api-`, obtainable from https://platform.minimaxi.com

## Key Capabilities

| Capability | Description | Entry point |
|------------|-------------|-------------|
| TTS | Text-to-speech synthesis with multiple voices and emotions | `scripts/tts/generate_voice.py` |
| Voice Cloning | Clone a voice from an audio sample (10s–5min) | `scripts/tts/generate_voice.py clone` |
| Voice Design | Create a custom voice from a text description | `scripts/tts/generate_voice.py design` |
| Music Generation | Generate songs with lyrics or instrumental tracks | `scripts/music/generate_music.py` |
| Video Generation | Text-to-video, image-to-video, subject reference, templates | `scripts/video/generate_video.py` |
| Long Video | Multi-scene chained video with crossfade transitions | `scripts/video/generate_long_video.py` |
| Media Tools | Audio/video format conversion, concatenation, trimming, extraction | `scripts/media_tools.py` |

## TTS (Text-to-Speech)

Entry point: `scripts/tts/generate_voice.py`

### IMPORTANT: Single voice vs Multi-segment — Choose the right approach

| User intent | Approach |
|-------------|----------|
| Single voice / no multi-character need | `tts` command — generate the entire text in one call |
| Multiple characters / narrator + dialogue | `generate` command with segments.json |

**Default behavior:** When the user simply asks to generate speech/voice and does NOT mention multiple voices or characters, use the `tts` command directly with a single appropriate voice. Do NOT split into segments or use the multi-segment pipeline — just pass the full text to `tts` in one call.

Only use multi-segment `generate` when:
- The user explicitly needs multiple voices/characters
- The text requires narrator + character dialogue separation
- The text exceeds **10,000 characters** (API limit per request) — in this case, split into segments with the same voice

### Single-voice generation (DEFAULT)

```bash
python scripts/tts/generate_voice.py tts "Hello world" -o minimax-output/hello.mp3
python scripts/tts/generate_voice.py tts "你好世界" -v female-shaonv -o minimax-output/hello_cn.mp3
```

### Multi-segment generation (multi-voice / audiobook / podcast)

**Complete workflow — follow ALL steps in order:**

1. **Write segments.json** — split text into segments with voice assignments (see format and rules below)
2. **Run `generate` command** — this reads segments.json, generates audio for EACH segment via TTS API, then merges them into a single output file with crossfade

```bash
# Step 1: Write segments.json to minimax-output/
# (use the Write tool to create minimax-output/segments.json)

# Step 2: Generate audio from segments.json — this is the CRITICAL step
# It generates each segment individually and merges them into one file
python scripts/tts/generate_voice.py generate minimax-output/segments.json \
  -o minimax-output/output.mp3 --crossfade 200
```

**Do NOT skip Step 2.** Writing segments.json alone does nothing — you MUST run the `generate` command to actually produce audio.

### Voice management

```bash
# List all available voices
python scripts/tts/generate_voice.py list-voices

# Voice cloning (from audio sample, 10s–5min)
python scripts/tts/generate_voice.py clone sample.mp3 --voice-id my-voice

# Voice design (from text description)
python scripts/tts/generate_voice.py design "A warm female narrator voice" --voice-id narrator
```

### Audio processing

```bash
python scripts/tts/generate_voice.py merge part1.mp3 part2.mp3 -o minimax-output/combined.mp3
python scripts/tts/generate_voice.py convert input.wav -o minimax-output/output.mp3
```

### TTS Models

| Model | Notes |
|-------|-------|
| speech-2.8-hd | Recommended, auto emotion matching |
| speech-2.8-turbo | Faster variant |
| speech-2.6-hd | Previous gen, manual emotion |
| speech-2.6-turbo | Previous gen, faster |

### segments.json Format

Default crossfade between segments: **200ms** (`--crossfade 200`).

```json
[
  { "text": "Hello!", "voice_id": "female-shaonv", "emotion": "" },
  { "text": "Welcome.", "voice_id": "male-qn-qingse", "emotion": "happy" }
]
```

Leave `emotion` empty for speech-2.8 models (auto-matched from text).

### IMPORTANT: Multi-Segment Script Generation Rules (Audiobooks, Podcasts, etc.)

When generating segments.json for audiobooks, podcasts, or any multi-character narration, you MUST split narration text from character dialogue into separate segments with distinct voices.

**Rule: Narration and dialogue are ALWAYS separate segments.**

A sentence like `"Tom said: The weather is great today!"` must be split into two segments:
- Segment 1 (narrator voice): `"Tom said:"`
- Segment 2 (character voice): `"The weather is great today!"`

**Example — Audiobook with narrator + 2 characters:**

```json
[
  { "text": "Morning sunlight streamed into the classroom as students filed in one by one.", "voice_id": "narrator-voice", "emotion": "" },
  { "text": "Tom smiled and turned to Lisa:", "voice_id": "narrator-voice", "emotion": "" },
  { "text": "The weather is amazing today! Let's go to the park after school!", "voice_id": "tom-voice", "emotion": "happy" },
  { "text": "Lisa thought for a moment, then replied:", "voice_id": "narrator-voice", "emotion": "" },
  { "text": "Sure, but I need to drop off my backpack at home first.", "voice_id": "lisa-voice", "emotion": "" },
  { "text": "They exchanged a smile and went back to listening to the lecture.", "voice_id": "narrator-voice", "emotion": "" }
]
```

**Key principles:**
1. **Narrator** uses a consistent neutral narrator voice throughout
2. **Each character** has a dedicated voice_id, maintained consistently across all their dialogue
3. **Split at dialogue boundaries** — `"He said:"` is narrator, the quoted content is the character
4. **Do NOT merge** narrator text and character speech into a single segment
5. For characters without pre-existing voice_ids, use voice cloning or voice design to create them first, then reference the created voice_id in segments

## Music Generation

Entry point: `scripts/music/generate_music.py`

### IMPORTANT: Instrumental vs Lyrics — When to use which

| Scenario | Mode | Action |
|----------|------|--------|
| BGM for video / voice / podcast | Instrumental (default) | Use `--instrumental` directly, do NOT ask user |
| User explicitly asks to "create music" / "make a song" | Ask user first | Ask whether they want instrumental or with lyrics |

**When adding background music to video or voice content**, always default to instrumental mode (`--instrumental`). Do not ask the user — BGM should never have vocals competing with the main content.

**When the user explicitly asks to create/generate music as the primary task**, ask them whether they want:
- Instrumental (pure music, no vocals)
- With lyrics (song with vocals — user provides or you help write lyrics)

```bash
# Instrumental (for BGM or when user chooses instrumental)
python scripts/music/generate_music.py \
  --instrumental \
  --prompt "ambient electronic, atmospheric" \
  --output minimax-output/ambient.mp3 --download

# Song with lyrics (when user chooses vocal music)
python scripts/music/generate_music.py \
  --lyrics "[verse]\nHello world\n[chorus]\nLa la la" \
  --prompt "indie folk, melancholic" \
  --output minimax-output/song.mp3 --download

# With style fields
python scripts/music/generate_music.py \
  --lyrics "[verse]\nLyrics here" \
  --genre "pop" --mood "upbeat" --tempo "fast" \
  --output minimax-output/pop_track.mp3 --download
```

### Music Models

| Model | Notes |
|-------|-------|
| music-2.5+ | Recommended, supports `--instrumental` |
| music-2.5 | Previous version |

## Video Generation

### IMPORTANT: Single vs Multi-Segment — Choose the right script

| User intent | Script to use |
|-------------|---------------|
| Default / no special request | `scripts/video/generate_video.py` (single segment, **10s, 768P**) |
| User explicitly asks for "long video", "multi-scene", "story", or duration > 10s | `scripts/video/generate_long_video.py` (multi-segment) |

**Default behavior:** Always use single-segment `generate_video.py` with **duration 10s and resolution 768P** unless the user explicitly asks for a long video, multi-scene video, or specifies a total duration exceeding 10 seconds. Do NOT automatically split into multiple segments — a single 10s video is the standard output. Only use `generate_long_video.py` when the user clearly needs multi-scene or longer content.

Entry point (single video): `scripts/video/generate_video.py`
Entry point (long/multi-scene): `scripts/video/generate_long_video.py`

### Video Model Constraints (MUST follow)

**Duration limits by model and resolution:**

| Model | 720P | 768P | 1080P |
|-------|------|------|-------|
| MiniMax-Hailuo-2.3 | - | 6s or **10s** | 6s only |
| MiniMax-Hailuo-2.3-Fast | - | 6s or **10s** | 6s only |
| MiniMax-Hailuo-02 | - | 6s or **10s** | 6s only |
| T2V-01 / T2V-01-Director | 6s only | - | - |
| I2V-01 / I2V-01-Director / I2V-01-live | 6s only | - | - |
| S2V-01 (ref) | 6s only | - | - |

**Resolution options by model and duration:**

| Model | 6s | 10s |
|-------|-----|-----|
| MiniMax-Hailuo-2.3 | 768P (default), 1080P | 768P only |
| MiniMax-Hailuo-2.3-Fast | 768P (default), 1080P | 768P only |
| MiniMax-Hailuo-02 | 512P, 768P (default), 1080P | 512P, 768P (default) |
| Other models | 720P (default) | Not supported |

**Key rules:**
- **Default: 10s + 768P** (best balance of length and quality for MiniMax-Hailuo-2.3)
- 1080P only supports 6s duration — if user requests 1080P, set `--duration 6`
- 10s duration only works with 768P (or 512P on Hailuo-02) — never combine 10s + 1080P
- Older models (T2V-01, I2V-01, S2V-01) only support 6s at 720P

### IMPORTANT: Prompt Optimization (MUST follow before generating any video)

Before calling any video generation script, you MUST optimize the user's prompt by reading and applying `references/video-prompt-guide.md`. Never pass the user's raw description directly as `--prompt`.

**Optimization steps:**

1. **Apply the Professional Formula**: `Main subject + Scene + Movement + Camera motion + Aesthetic atmosphere`
   - BAD: `"A puppy in a park"`
   - GOOD: `"A golden retriever puppy runs toward the camera on a sun-dappled grass path in a park, [跟随] smooth tracking shot, warm golden hour lighting, shallow depth of field, joyful atmosphere"`

2. **Add camera instructions** using `[指令]` syntax: `[推进]`, `[拉远]`, `[跟随]`, `[固定]`, `[左摇]`, etc.

3. **Include aesthetic details**: lighting (golden hour, dramatic side lighting), color grading (warm tones, cinematic), texture (dust particles, rain droplets), atmosphere (intimate, epic, peaceful)

4. **Keep to 1-2 key actions** for 6-10 second videos — do not overcrowd with events

5. **For i2v mode** (image-to-video): Focus prompt on **movement and change only**, since the image already establishes the visual. Do NOT re-describe what's in the image.
   - BAD: `"A lake with mountains"` (just repeating the image)
   - GOOD: `"Gentle ripples spread across the water surface, a breeze rustles the distant trees, [固定] fixed camera, soft morning light, peaceful and serene"`

6. **For multi-segment long videos**: Each segment's prompt must be self-contained and optimized individually. The i2v segments (segment 2+) should describe motion/change relative to the previous segment's ending frame.

```bash
# Text-to-video (default: 10s, 768P)
python scripts/video/generate_video.py \
  --mode t2v \
  --prompt "A golden retriever puppy bounds toward the camera on a sunlit grass path, [跟随] tracking shot, warm golden hour, shallow depth of field, joyful" \
  --output minimax-output/puppy.mp4

# Text-to-video with 1080P (must use --duration 6)
python scripts/video/generate_video.py \
  --mode t2v \
  --prompt "A golden retriever puppy bounds toward the camera" \
  --duration 6 --resolution 1080P \
  --output minimax-output/puppy_hd.mp4

# Image-to-video (prompt focuses on MOTION, not image content)
python scripts/video/generate_video.py \
  --mode i2v \
  --prompt "The petals begin to sway gently in the breeze, soft light shifts across the surface, [固定] fixed framing, dreamy pastel tones" \
  --first-frame photo.jpg \
  --output minimax-output/animated.mp4

# Start-end frame interpolation (sef mode uses MiniMax-Hailuo-02)
python scripts/video/generate_video.py \
  --mode sef \
  --first-frame start.jpg --last-frame end.jpg \
  --output minimax-output/transition.mp4

# Subject reference (face consistency, ref mode uses S2V-01, 6s only)
python scripts/video/generate_video.py \
  --mode ref \
  --prompt "A young woman in a white dress walks slowly through a sunlit garden, [跟随] smooth tracking, warm natural lighting, cinematic depth of field" \
  --subject-image face.jpg \
  --duration 6 \
  --output minimax-output/person.mp4
```

### Long-form Video (Multi-scene)

Multi-scene long videos chain segments together: the first segment generates via text-to-video (t2v), then each subsequent segment uses the last frame of the previous segment as its first frame (i2v). Segments are joined with crossfade transitions for smooth continuity. Default is 10 seconds per segment.

**Workflow:**
1. Segment 1: t2v — generated purely from the optimized text prompt
2. Segment 2+: i2v — the previous segment's last frame becomes `first_frame_image`, prompt describes **motion and change from that ending state**
3. All segments are concatenated with 0.5s crossfade transitions to eliminate jump cuts
4. Optional: AI-generated background music is overlaid

**Prompt rules for each segment:**
- Each segment prompt MUST be independently optimized using the Professional Formula
- Segment 1 (t2v): Full scene description with subject, scene, camera, atmosphere
- Segment 2+ (i2v): Focus on **what changes and moves** from the previous ending frame. Do NOT repeat the visual description — the first frame already provides it
- Maintain visual consistency: keep lighting, color grading, and style keywords consistent across segments
- Each segment covers only 10 seconds of action — keep it focused

```bash
# Example: 3-segment story with optimized per-segment prompts (default: 10s/segment, 768P)
python scripts/video/generate_long_video.py \
  --scenes \
    "A lone astronaut stands on a red desert planet surface, wind blowing dust particles, [推进] slow push in toward the visor, dramatic rim lighting, cinematic sci-fi atmosphere" \
    "The astronaut turns and begins walking toward a distant glowing structure on the horizon, dust swirling around boots, [跟随] tracking from behind, vast desolate landscape, golden light from the structure" \
    "The astronaut reaches the structure entrance, a massive doorway pulses with blue energy, [推进] slow push in toward the doorway, light reflects off the visor, awe-inspiring epic scale" \
  --music-prompt "cinematic orchestral ambient, slow build, sci-fi atmosphere" \
  --output minimax-output/long_video.mp4

# With custom settings
python scripts/video/generate_long_video.py \
  --scenes "Scene 1 prompt" "Scene 2 prompt" \
  --segment-duration 10 \
  --resolution 768P \
  --crossfade 0.5 \
  --music-prompt "calm ambient background music" \
  --output minimax-output/long_video.mp4
```

### Add Background Music

```bash
python scripts/video/add_bgm.py \
  --video input.mp4 \
  --generate-bgm --instrumental \
  --music-prompt "soft piano background" \
  --bgm-volume 0.3 \
  --output minimax-output/output_with_bgm.mp4
```

### Template Video

```bash
python scripts/video/generate_template_video.py \
  --template-id 392753057216684038 \
  --media photo.jpg \
  --output minimax-output/template_output.mp4
```

### Video Models

| Mode | Default Model | Default Duration | Default Resolution | Notes |
|------|--------------|-----------------|-------------------|-------|
| t2v | MiniMax-Hailuo-2.3 | 10s | 768P | Latest text-to-video |
| i2v | MiniMax-Hailuo-2.3 | 10s | 768P | Latest image-to-video |
| sef | MiniMax-Hailuo-02 | 6s | 768P | Start-end frame |
| ref | S2V-01 | 6s | 720P | Subject reference, 6s only |

## Media Tools (Audio/Video Processing)

Entry point: `scripts/media_tools.py`

Standalone FFmpeg-based utilities for format conversion, concatenation, extraction, trimming, and audio overlay. Use these when the user needs to process existing media files without generating new content via MiniMax API.

### Video Format Conversion

```bash
# Convert between formats (mp4, mov, webm, mkv, avi, ts, flv)
python scripts/media_tools.py convert-video input.webm -o output.mp4
python scripts/media_tools.py convert-video input.mp4 -o output.mov

# With quality / resolution / fps options
python scripts/media_tools.py convert-video input.mp4 -o output.mp4 \
  --crf 18 --preset medium --resolution 1920x1080 --fps 30
```

### Audio Format Conversion

```bash
# Convert between formats (mp3, wav, flac, ogg, aac, m4a, opus, wma)
python scripts/media_tools.py convert-audio input.wav -o output.mp3
python scripts/media_tools.py convert-audio input.mp3 -o output.flac \
  --bitrate 320k --sample-rate 48000 --channels 2
```

### Video Concatenation

```bash
# Concatenate with crossfade transition (default 0.5s)
python scripts/media_tools.py concat-video seg1.mp4 seg2.mp4 seg3.mp4 -o merged.mp4

# Hard cut (no crossfade)
python scripts/media_tools.py concat-video seg1.mp4 seg2.mp4 -o merged.mp4 --crossfade 0
```

### Audio Concatenation

```bash
# Simple concatenation
python scripts/media_tools.py concat-audio part1.mp3 part2.mp3 -o combined.mp3

# With crossfade
python scripts/media_tools.py concat-audio part1.mp3 part2.mp3 -o combined.mp3 --crossfade 1
```

### Extract Audio from Video

```bash
# Extract as mp3
python scripts/media_tools.py extract-audio video.mp4 -o audio.mp3

# Extract as wav with higher bitrate
python scripts/media_tools.py extract-audio video.mp4 -o audio.wav --bitrate 320k
```

### Video Trimming

```bash
# Trim by start/end time (seconds)
python scripts/media_tools.py trim-video input.mp4 -o clip.mp4 --start 5 --end 15

# Trim by start + duration
python scripts/media_tools.py trim-video input.mp4 -o clip.mp4 --start 10 --duration 8
```

### Add Audio to Video (Overlay / Replace)

```bash
# Mix audio with existing video audio
python scripts/media_tools.py add-audio --video video.mp4 --audio bgm.mp3 -o output.mp4 \
  --volume 0.3 --fade-in 2 --fade-out 3

# Replace original audio entirely
python scripts/media_tools.py add-audio --video video.mp4 --audio narration.mp3 -o output.mp4 \
  --replace
```

### Media File Info

```bash
python scripts/media_tools.py probe input.mp4
```

## Script Architecture

```
scripts/
├── check_environment.py          # Env verification
├── env_loader.py                # .env file loader (auto-loaded by all scripts)
├── media_tools.py               # Audio/video conversion, concat, trim, extract
├── tts/
│   ├── generate_voice.py         # CLI entry point
│   ├── sync_tts.py               # Synchronous TTS API
│   ├── async_tts.py              # Async (task-based) TTS API
│   ├── segment_tts.py            # Multi-segment pipeline
│   ├── audio_processing.py       # FFmpeg audio processing
│   ├── voice_clone.py            # Voice cloning API
│   ├── voice_design.py           # Voice design API
│   ├── voice_management.py       # Voice CRUD operations
│   └── utils.py                  # Shared: API config, VoiceSetting, AudioSetting
├── music/
│   ├── generate_music.py         # Music generation CLI
│   └── utils_audio.py            # Audio format utilities
└── video/
    ├── generate_video.py         # Video generation CLI (4 modes)
    ├── generate_long_video.py    # Multi-scene long video
    ├── generate_template_video.py # Template-based video
    └── add_bgm.py               # Background music overlay
```

## References

Read these for detailed API parameters, voice catalogs, and prompt engineering:

- [tts-guide.md](references/tts-guide.md) — TTS setup, voice management, audio processing, segment format, troubleshooting
- [tts-voice-catalog.md](references/tts-voice-catalog.md) — Full voice catalog with IDs, descriptions, and parameter reference
- [music-api.md](references/music-api.md) — Music generation API: endpoints, parameters, response format
- [video-api.md](references/video-api.md) — Video API: endpoints, models, parameters, camera instructions, templates
- [video-prompt-guide.md](references/video-prompt-guide.md) — Video prompt engineering: formulas, styles, image-to-video tips
