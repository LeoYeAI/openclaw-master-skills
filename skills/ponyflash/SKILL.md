---
name: ponyflash
description: >-
  Generate images, videos, speech audio, and music using the PonyFlash Python SDK.
  Also handle local media editing with FFmpeg, including clip, concat, transcode,
  extract audio, frame capture, subtitle capability checks, and ASS subtitle prep.
  Use when the user asks to create, generate, produce, edit, trim, merge, concatenate,
  transcode, subtitle, or render AI-generated media content.
license: MIT
metadata:
  author: ponyflash
  version: "0.3.0"
---

# PonyFlash Skill

## Step 0: Decide Which Capability Path Applies

This skill now contains **two capability families**:

1. **Cloud generation via PonyFlash Python SDK**
   - image generation
   - video generation
   - speech synthesis
   - music generation
   - model listing
   - file management
   - account / credits
   - These tasks **require a valid PonyFlash API key**.

2. **Local media editing via FFmpeg toolchain**
   - ffmpeg / ffprobe detection
   - installation planning
   - clip / concat / transcode
   - extract audio / capture frame
   - subtitle capability checks
   - ASS subtitle generation and burn-in workflow
   - These tasks **do NOT require a PonyFlash API key**, but they **do require local `ffmpeg` / `ffprobe` support**.

Before doing anything, classify the request:

- If the user is asking to **generate** media with PonyFlash models, follow the SDK path and require API key setup.
- If the user is asking to **edit or process local media**, follow the FFmpeg path and do dependency checks first.
- If the user wants an **end-to-end production workflow**, you may use both: generate assets with PonyFlash, then assemble or export with FFmpeg.

## Step 1A: API Key Setup for PonyFlash SDK Tasks

Only do this section when the request needs PonyFlash cloud capabilities.

**The FIRST time this skill is activated for a cloud generation task**, tell the user the following in your own words:

1. PonyFlash skill is ready to use.
2. It can handle:
   - image generation
   - video generation
   - speech synthesis
   - music generation
   - local media editing with FFmpeg
3. For complex multi-step productions, there are **Creative Playbooks** in the `playbooks/` directory.
4. To use PonyFlash cloud generation, the user needs an API key:
   - Register / log in at **https://www.ponyflash.com**
   - Get API key at **https://www.ponyflash.com/api-key** (starts with `rk_`)
   - Check credits at **https://www.ponyflash.com/usage**
   - Paste the key back in the chat

**On subsequent SDK activations**, check whether `PONYFLASH_API_KEY` is set in the environment. If not, ask the user for the key again.

Once received, set it up:

```bash
export PONYFLASH_API_KEY="rk_xxx"
```

Then install the SDK:

```bash
pip install ponyflash
```

**Always verify the key works before any generation task:**

```python
from ponyflash import PonyFlash

pony_flash = PonyFlash(api_key="<key from user>")
balance = pony_flash.account.credits()
print(f"Balance: {balance.balance} {balance.currency}")
```

If verification fails:
- **Key invalid or missing** → direct user to https://api.ponyflash.com/api-key
- **Balance is zero** → direct user to https://api.ponyflash.com/usage to top up credits

## Step 1B: Local Dependency Setup for FFmpeg Tasks

Only do this section when the request needs local editing, subtitle, or export work.

1. First check local dependencies:

```bash
bash "{baseDir}/scripts/check_ffmpeg.sh"
```

2. If the task involves subtitles, do **capability checks**, not just existence checks:

```bash
bash "{baseDir}/scripts/check_ffmpeg.sh" --require-subtitles-filter
```

3. If `ffmpeg` / `ffprobe` or required filters are missing:
- Tell the user what is missing.
- Ask whether the user wants platform-appropriate FFmpeg installation guidance.
- After the user installs FFmpeg, rerun the dependency checks before continuing.

## What this Skill Can Do

| Capability | Resource | Description |
|---|---|---|
| Image generation | `pony_flash.images` | Text-to-image, image editing with mask/reference images |
| Video generation | `pony_flash.video` | Text-to-video, first-frame-to-video, OmniHuman, Motion Transfer |
| Speech synthesis | `pony_flash.speech` | Text-to-speech with voice cloning, emotion control, speed, pitch |
| Music generation | `pony_flash.music` | Text-to-music with lyrics, style, instrumental mode, continuation |
| Model listing | `pony_flash.models` | List available models, get model details and supported modes |
| File management | `pony_flash.files` | Upload, list, get, delete files |
| Account | `pony_flash.account` | Check credit balance, get recharge link |
| Local media editing | `scripts/media_ops.sh` | Clip, concat, transcode, extract audio, frame capture |
| FFmpeg environment checks | `scripts/check_ffmpeg.sh` | Detect ffmpeg / ffprobe and subtitle capabilities |
| Subtitle font prep | `scripts/ensure_subtitle_fonts.sh` | Keep a reusable local copy of the default subtitle font when explicitly requested |
| ASS subtitle prep | `scripts/build_ass_subtitles.py` | Adaptive ASS subtitle generation with pre-wrapping |

## Creative Playbooks (production workflows)

The `playbooks/` directory contains **Creative Playbooks** — step-by-step production workflow guides for specific content types. Playbooks act as a director layer: they tell you **what to create and in what order**, while this SKILL.md tells you **how to execute generation and editing**.

### When to use a playbook

1. **User explicitly requests a playbook by name** → Read the corresponding file from `playbooks/` and follow its workflow.
2. **User asks to see available playbooks** → Read [playbooks/INDEX.md](playbooks/INDEX.md) and display the full list.
3. **User's request is clearly a multi-step production task** → Suggest a matching playbook from [playbooks/INDEX.md](playbooks/INDEX.md) and ask whether to use it.
4. **User's request is a single-step generation or editing task** → Proceed directly with the relevant SDK or FFmpeg capability. No playbook needed.

### How to execute a playbook

Once a playbook is loaded:
- Follow its workflow (asset prep → content generation → voice / music → editing → output).
- Use PonyFlash SDK for generation tasks and FFmpeg scripts for local assembly / export tasks.
- Confirm key creative decisions with the user before expensive generation.
- Adapt prompts, durations, output format, and export strategy to the user's actual goal.

### Creating custom playbooks

When the user asks to create a new playbook, generate a markdown file in `playbooks/` following this template:

```markdown
---
name: Playbook Name
description: One-line summary of what this playbook produces
tags: [keyword1, keyword2, keyword3]
difficulty: beginner | intermediate | advanced
estimated_credits: credit range estimate
output_format: format description (e.g., "vertical 9:16 MP4")
---

# Playbook Name

## Use Cases
When to use this playbook.

## Workflow
### Step 1: Asset Preparation
What the user needs to provide; how to generate missing assets.

### Step 2: Visual Content Generation
Which models to use, recommended parameters, prompt guidance.

### Step 3: Voice / Music
Speech synthesis + background music guidance.

### Step 4: Editing / Assembly
How to assemble, trim, subtitle, transcode, and export with the local FFmpeg workflow.

### Step 5: Output / Optimization
Render settings, format recommendations.

## Prompt Templates
Reusable prompt examples for this content type.

## Notes
Best practices, common pitfalls.
```

After creating the file, update [playbooks/INDEX.md](playbooks/INDEX.md) to include the new playbook.

## PonyFlash SDK Core Concepts

### Client initialization

```python
from ponyflash import PonyFlash

pony_flash = PonyFlash(api_key="rk_xxx")
```

Reads `PONYFLASH_API_KEY` from environment if `api_key` is omitted.

### FileInput — zero-friction file handling

All file parameters accept any of these types:

| Input type | Example | Behavior |
|---|---|---|
| URL string | `"https://example.com/photo.jpg"` | Passed directly to API |
| file_id string | `"file_abc123"` | Passed directly to API |
| `Path` object | `Path("photo.jpg")` | Auto-uploaded via presigned URL |
| `open()` file | `open("photo.jpg", "rb")` | Auto-uploaded via presigned URL |
| `bytes` | `image_bytes` | Auto-uploaded via presigned URL |
| `(filename, bytes)` tuple | `("photo.jpg", data)` | Auto-uploaded with filename |

Temp uploads are cleaned up automatically after `generate()` completes.

Plain local string paths such as `"./photo.jpg"` are not supported. For local files, always use `Path(...)` or `open(..., "rb")`.

### Generation result

`Generation` object fields: `request_id`, `status`, `outputs`, `usage`, `error`.

Convenience properties:
- `gen.url` — first output URL (or `None`)
- `gen.urls` — list of all output URLs
- `gen.credits` — credits consumed

## Quick Examples (PonyFlash SDK)

### Image

```python
gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="A sunset over mountains",
    resolution="2K",
    aspect_ratio="16:9",
)
print(gen.url)
```

### Video

```python
gen = pony_flash.video.generate(
    model="veo-3.1-fast",
    prompt="A timelapse of a city at night",
    duration=4,
    resolution="720p",
    aspect_ratio="16:9",
    generate_audio=False,
)
print(gen.url)
```

### Speech

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Hello, welcome to PonyFlash!",
    voice="English_Graceful_Lady",
)
print(gen.url)
```

### Music

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="An upbeat electronic dance track",
    duration=30,
)
print(gen.url)
```

### List models

```python
page = pony_flash.models.list()
for model in page.items:
    print(f"{model.id} ({model.type})")
```

### Check balance

```python
balance = pony_flash.account.credits()
print(f"Balance: {balance.balance} {balance.currency}")
```

## Local Media Editing with FFmpeg

> No PonyFlash API key is needed for local editing, but local FFmpeg capability checks are mandatory.

### When to use this path

Use the local FFmpeg workflow when the user asks to:

- trim or cut a video
- merge or concatenate clips
- transcode to a target format
- extract audio
- capture a frame / thumbnail
- verify subtitle support
- prepare adaptive ASS subtitles
- export a final edited file after PonyFlash generation

### Preferred workflow

1. Check dependencies:

```bash
bash "{baseDir}/scripts/check_ffmpeg.sh"
```

2. If subtitle work is needed:

```bash
bash "{baseDir}/scripts/check_ffmpeg.sh" --require-subtitles-filter
```

3. Prefer the stable script entrypoint:

```bash
bash "{baseDir}/scripts/media_ops.sh" help
```

4. Before any multi-step editing task, create a temporary task workspace and keep **all** staged inputs and intermediate outputs inside it:

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
```

Use this directory for:

- downloaded source media;
- generated `.srt` / `.ass` files;
- intermediate clips;
- intermediate subtitled renders;
- reusable inspection outputs that were not explicitly requested as final deliverables.

5. Validate outputs after execution.

6. After the task finishes, delete the temporary task workspace unless the user explicitly asked to keep intermediate artifacts.

### Capability profiles

- `basic`: requires `ffmpeg + ffprobe + libx264 + aac`
- `full`: `basic` plus `subtitles` filter support

### Preferred commands

#### Probe media

```bash
bash "{baseDir}/scripts/media_ops.sh" probe --input "input.mp4"
```

#### Clip video

```bash
bash "{baseDir}/scripts/media_ops.sh" clip --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

Fast copy mode only when the user explicitly wants speed / near-lossless slicing:

```bash
bash "{baseDir}/scripts/media_ops.sh" clip --mode copy --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

#### Concat clips

```bash
bash "{baseDir}/scripts/media_ops.sh" concat --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

Fallback to reencode if copy concat fails:

```bash
bash "{baseDir}/scripts/media_ops.sh" concat --mode reencode --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

#### Extract audio

```bash
bash "{baseDir}/scripts/media_ops.sh" extract-audio --input "$taskDir/input.mp4" --output "$taskDir/audio.m4a"
```

#### Transcode

```bash
bash "{baseDir}/scripts/media_ops.sh" transcode --input "$taskDir/input.mov" --output "$taskDir/output.mp4"
```

#### Capture frame

```bash
bash "{baseDir}/scripts/media_ops.sh" frame --input "$taskDir/input.mp4" --output "$taskDir/cover.jpg" --time "00:00:03"
```

### Subtitle workflow

For `.srt` / `.ass` burn-in:

```bash
bash "{baseDir}/scripts/check_ffmpeg.sh" --require-subtitles-filter
```

If subtitle style is unspecified, the agent should use the default subtitle workflow, which stages its runtime font temporarily and cleans it up after export.

Preferred stable entrypoint:

```bash
bash "{baseDir}/scripts/media_ops.sh" subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

If the task needs adaptive line wrapping or controlled subtitle layout, or if you need to understand the underlying steps:

```bash
python3 "{baseDir}/scripts/build_ass_subtitles.py" --help
```

Default burn pattern:

1. Probe width and height:

```bash
ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "input.mp4"
```

2. Use the stable subtitle entrypoint when the user only wants the final rendered video:

```bash
bash "{baseDir}/scripts/media_ops.sh" subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

This path keeps only the final `final-output.mp4` by default and removes temporary ASS files and staged fonts. If the user did not explicitly request any staged files, the agent should also delete `$taskDir` after moving or confirming the final deliverable.

3. Build a default ASS subtitle file only when the user explicitly wants to keep or inspect it:

```bash
bash "{baseDir}/scripts/ensure_subtitle_fonts.sh"

python3 "{baseDir}/scripts/build_ass_subtitles.py" \
  --subtitle-file "$taskDir/subtitles.srt" \
  --output-ass "$taskDir/subtitles.ass" \
  --video-width 1920 \
  --video-height 1080 \
  --latin-font-file "$HOME/.cache/ponyflash/fonts/NotoSansCJKsc-Regular.otf" \
  --cjk-font-file "$HOME/.cache/ponyflash/fonts/NotoSansCJKsc-Regular.otf"
```

4. Burn subtitles with the prepared runtime font:

```bash
ffmpeg -i "$taskDir/input.mp4" \
  -vf "subtitles=$taskDir/subtitles.ass:fontsdir=$HOME/.cache/ponyflash/fonts" \
  -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -movflags +faststart "final-output.mp4"
```

Default subtitle references:

- Font notes: `{baseDir}/assets/fonts.md`
- Subtitle style: `{baseDir}/assets/subtitle-style.md`
- Decision rules: `{baseDir}/reference/operations.md`
- Examples: `{baseDir}/reference/examples.md`

### Decision rules

- Clip tasks: default to `reencode`; use `copy` only when the user explicitly wants speed / minimal loss.
- Concat tasks: default to `copy`; fallback to `reencode` if source parameters differ.
- Audio extraction: default to AAC in `.m4a`.
- Transcode: default to `mp4 + libx264 + aac`.
- Subtitle tasks: if subtitle style is unspecified, use the default subtitle workflow, prepared runtime font, and default subtitle styling rules.
- Subtitle tasks: prefer `subtitles`; use `drawtext` only as a plain text fallback.
- Do not overwrite outputs unless the user explicitly allows it.
- Unless the user explicitly asks to keep intermediate artifacts, remove temporary ASS files, temporary font directories, concat lists, and failed partial outputs after the task finishes.
- Unless the user explicitly asks to keep intermediate artifacts, stage all non-final files inside `taskDir` and delete `taskDir` at the end of the task.

### Failure handling

- If `ffmpeg` or `ffprobe` is missing, pause the task, help the user install FFmpeg if needed, and rerun the checks first.
- If subtitle burn-in is requested but `subtitles` is missing, do not claim the machine can burn `.srt` / `.ass`.
- If only `drawtext` exists, explain that this is text overlay fallback, not full subtitle burn-in.
- If concat copy mode fails, retry with `reencode`.
- If scripts do not cover the exact request, explain the limitation and fall back to a raw `ffmpeg` command.

## Delivering generated files to the user

> **CRITICAL**: You MUST actually send generated files to the user — never just print a file path as text.

### File save location

Always save generated files (rendered videos, downloaded media, etc.) to **your current working directory** (e.g., `./output.mp4`), NOT to `/tmp/` or other system directories. Many agent platforms restrict file-sending to the workspace directory only. Saving to `/tmp/` will cause file delivery to fail silently.

### Delivery rules

1. **API-generated content** — `gen.url` is already a downloadable URL. Send it to the user, and also use your platform's file-sending capability to send the file directly in the conversation.
2. **Locally rendered content** (e.g., `timeline.render("output.mp4")`) — save the output to your working directory, then use your platform's file-sending tool to send the actual file to the user as an attachment. Do NOT just send the file path as a text message.
3. **Multiple outputs** — send each file with a clear label describing what it is.

## Error Handling for PonyFlash SDK

```python
from ponyflash import (
    PonyFlash,
    InsufficientCreditsError,
    RateLimitError,
    GenerationFailedError,
    AuthenticationError,
)

pony_flash = PonyFlash()

try:
    gen = pony_flash.images.generate(model="nanobanana-pro", prompt="A cat")
except AuthenticationError:
    print("Invalid or missing API key.")
    print("Get your API key at: https://api.ponyflash.com/api-key")
except InsufficientCreditsError as e:
    print(f"Not enough credits. Balance: {e.balance}, required: {e.required}")
    print("Top up credits at: https://api.ponyflash.com/usage")
except RateLimitError:
    print("Rate limited — wait and retry")
except GenerationFailedError as e:
    print(f"Generation failed: {e.generation.error.code}")
```

## More Examples

For advanced PonyFlash SDK usage:
See [examples/advanced.md](examples/advanced.md)

For FFmpeg task patterns:
- [reference/operations.md](reference/operations.md)
- [reference/examples.md](reference/examples.md)

## API Reference

For complete method signatures, parameter types, and return type fields:

- **Image generation**: [reference/images.md](reference/images.md)
- **Video generation**: [reference/video.md](reference/video.md)
- **Speech synthesis**: [reference/speech.md](reference/speech.md)
- **Music generation**: [reference/music.md](reference/music.md)
- **Model listing**: [reference/models.md](reference/models.md)
- **File management**: [reference/files.md](reference/files.md)
- **Account / credits**: [reference/account.md](reference/account.md)
- **FFmpeg operation strategy**: [reference/operations.md](reference/operations.md)
- **FFmpeg examples**: [reference/examples.md](reference/examples.md)
- **Subtitle fonts**: [assets/fonts.md](assets/fonts.md)
- **Subtitle style**: [assets/subtitle-style.md](assets/subtitle-style.md)

## Model Catalog

For all available models and their specific parameters, capabilities, and examples:
See [reference/models/INDEX.md](reference/models/INDEX.md)
