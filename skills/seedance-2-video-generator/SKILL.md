---
name: seedance-2-video-gen
version: 1.0.1
description: "Generate Werydance 2.0 videos through WeryAI for text-to-video, image-to-video, multi-image video, and first-frame/last-frame transitions. Use when you need a Werydance 2.0 video generator, want to animate a reference image (prefer a public https URL), create a storyboard-to-video clip, migrate `image + last_image` workflows, or generate controlled start/end frame video with your WeryAI API key."

tags: [seedance, seedance-2, video-gen, text-to-video, image-to-video, multi-image-video, almighty-reference, start-frame, end-frame, video-edit]

metadata: { "openclaw": { "emoji": "🎬", "primaryEnv": "WERYAI_API_KEY", "paid": true, "network_required": true, "requires": { "env": ["WERYAI_API_KEY"], "bins": ["node"], "node": ">=18" } } }
user-invocable: true
---

# Werydance 2.0 video generator (almighty-ready)

Generate Werydance 2.0 videos on WeryAI with one skill for text-to-video, image-to-video, first-frame/last-frame transition video, multi-image storyboard video, and almighty mixed-reference video generation.
Animate and transform scenes from single images, storyboard frames, or mixed references while keeping subject and motion continuity.

**Dependencies:** `scripts/video_gen.js` at the skill package root (alongside `SKILL.md`) + `WERYAI_API_KEY` + Node.js 18+. No other Cursor skills are required.

- text-only generation
- single-image animation
- multi-image storyboard generation
- first-frame/last-frame compatibility aliases
- almighty mixed references (`images + videos + audios + prompt`)

Runtime secret: only `WERYAI_API_KEY`.

## Core upgrade

This skill now supports four input modalities for richer control:

- Image reference: composition, character, and detail lock
- Video reference: camera language, action rhythm, effect imitation
- Audio reference: mood and timing guidance
- Text prompt: intent and constraints

Smart routing policy:

- If payload includes `videos` or `audios`, route to `POST /v1/generation/almighty-reference-to-video`.
- Otherwise keep legacy routing (`text-to-video`, `image-to-video`, `multi-image-to-video`).

## Prerequisites

- `WERYAI_API_KEY` must be set.
- Node.js 18+.
- Prefer public `https` URLs for media.
- Local files are supported and auto-uploaded by this skill via `POST /v1/generation/upload-file`.

```sh
export WERYAI_API_KEY="your_api_key_here"
```

## Quick checks

```sh
node scripts/video_gen.js models --mode text_to_video
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"A glowing koi swims through ink clouds","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}' --dry-run
```

## Modes and input shapes

| Mode | Trigger | API route | Key fields |
|---|---|---|---|
| Text | no media refs | `/v1/generation/text-to-video` | `prompt`, `duration`, optional `aspect_ratio`, `resolution`, `generate_audio` |
| Single image | `image` only | `/v1/generation/image-to-video` | `image`, `prompt`, plus common fields |
| Multi image | `images` only | `/v1/generation/multi-image-to-video` | `images`, `prompt`, plus common fields |
| Almighty | has `videos` or `audios` | `/v1/generation/almighty-reference-to-video` | `images`, `videos`, `audios`, `prompt`, `video_number`, plus common fields |

Compatibility aliases still supported:

- `first_frame + last_frame` -> normalized to ordered `images`
- `image + last_image` -> normalized to ordered `images`

## Almighty constraints

Almighty validations in this skill:

- `prompt` max 500 chars
- `images` <= 9
- `videos` <= 3
- `audios` <= 3
- mixed file total (`images + videos + audios`) <= 12
- at least one of `images` or `videos`
- `duration` must be 5-15 seconds
- `video_number` must be 1-4

Notes:

- Backend enforces media-duration constraints for reference clips.
- Per current OpenAPI contract, almighty duration floor is 5s.

## Local upload behavior

Supported local files before generation submit:

- Images: `jpg/jpeg/png/webp/gif`, max 10MB
- Videos: `mp4/mov`, max 50MB
- Audios: `mp3/wav`, max 50MB

Upload endpoint used by this skill:

- Shot scale, angle, and lens feel.
- Camera movement or a clear lock-off choice.
- Lighting direction, material response, and overall mood.
- Subject motion paced to the selected `duration`.
- One clear visual payoff in the final shot.
- Output framing such as `9:16 vertical` when using the default aspect ratio.
- **Audio (default-on):** Add a labeled **`Audio:`** block (ambience, layered SFX, subtle foley—**generic**, non-copyrighted) **even if the user never mentioned sound**. JSON **`generate_audio`** defaults to **`true`** for models that support audio; use **`false`** and omit **`Audio:`** only when the user explicitly wants **silent** output.

Dry-run behavior:

- `--dry-run` never uploads local files
- output includes `uploadPreview` to show which local paths would be uploaded

## Prompt workflow (mandatory)

Before paid submit, expand brief into production prompt:

1. Decide mode.
2. Map each media to explicit role.
3. Build 2-4 timeline beats by duration.
4. Write one action arc + one final payoff.
5. Add minimal constraints for continuity.

Always show full prompt and all params before submit, then wait for explicit confirmation.

## @asset layered referencing

Use explicit role mapping in prompt drafts:

- Visual anchor: `@图片1` / `@图1`
- Camera/motion style: `参考@视频1运镜`
- Action rhythm: `参考@视频2动作节奏`
- Music/sound bed: `@音频1用于配乐`

Good:

- `@图1为首帧，参考@视频1的跑步动作，镜头从正面切到侧面，@音频1做节奏底。`

Bad:

- `用这些素材生成一个视频。`

## High-value templates

### Video extend

- `将@视频1延长 5s，新增段落为...，保持人物与场景连续。`
- Set `duration` to the added segment length.

### Video fusion

1. Decide which path fits the request: `text`, `image`, `multi-image`, or `first-frame/last-frame`.
2. Collect the user's brief, `duration`, optional `aspect_ratio`, optional `resolution`, **`generate_audio`** (default **`true`** unless the user wants silent), and reference image URLs if the mode uses assets (prefer public `https`).
3. Expand the prompt with the rules from `## Prompt expansion (mandatory)`. If the request needs tighter control, read `references/seedance-prompt-optimization.md` and explicitly decide mode, asset mapping, timeline beats, and negative constraints before writing the final prompt.
4. If you are unsure about current multi-image support or field limits, run `node scripts/video_gen.js models --mode multi_image_to_video` before a paid request.
5. Show a confirmation table with the **full expanded prompt**, model, duration, aspect ratio, resolution, audio choice, and any image URLs.
6. After explicit confirmation, run `node scripts/video_gen.js wait --json '...'`.
7. Return the JSON result. On success, surface the video URLs. On failure, report `errorCode` and `errorMessage` and suggest the likely parameter fix.

## CLI reference

```sh
# Check live model metadata
node scripts/video_gen.js models
node scripts/video_gen.js models --mode text_to_video
node scripts/video_gen.js models --mode image_to_video
node scripts/video_gen.js models --mode multi_image_to_video

# Text-to-video (non-empty model required; default audio on)
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"A paper crane unfolds into a real bird, cinematic lighting, 9:16 vertical. Audio: soft paper rustle, gentle whoosh, quiet room tone.","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'

# Single image to video
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"Animate this portrait with subtle hair and cloth movement. Audio: faint fabric rustle, subtle room ambience.","image":"https://example.com/frame.png","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'

# Multi-image to video
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"Turn these storyboard frames into one coherent reveal shot. Audio: light transition whooshes, soft underscore.","images":["https://example.com/1.png","https://example.com/2.png","https://example.com/3.png"],"duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'

# First-frame / last-frame guided video
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"Start on the first frame and transition naturally to the last frame with the same subject and environment. Audio: smooth morph tone, airy ambience.","first_frame":"https://example.com/start.png","last_frame":"https://example.com/end.png","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'

# WaveSpeed-style compatibility alias
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"Transition smoothly from the start image to the end image. Audio: soft blend whoosh, quiet room.","image":"https://example.com/start.png","last_image":"https://example.com/end.png","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'

# Preview without spending credits
node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"A glowing koi swims through ink clouds. Audio: water shimmer, subtle chime.","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}' --dry-run

# Poll an existing task
node scripts/video_gen.js status --task-id <task-id>
```

## Poll timeout classes

- `task_class=short`: default `5` minutes (`300000ms`), intended for text-to-video.
- `task_class=long`: default `20` minutes (`1200000ms`), intended for image/multi-image/almighty.
- `task_class=auto` (default): infer from effective mode.
- `WERYAI_POLL_TIMEOUT_MS` remains the highest-priority explicit override.

## Compliance notice

- Do not store `WERYAI_API_KEY` in repository files.
- Platform compliance for realistic human face references is handled by backend policy; this skill does not implement client-side blocking.

## Definition of done

Done when the user receives at least one playable video URL, or a clear failure with `errorCode` / `errorMessage` and a concrete next step. The submitted payload must stay within the selected model's supported field set. With default **`generate_audio`: `true`**, the **`prompt`** should include **`Audio:`** prose unless the user requested silent generation.

## Boundaries (out of scope)

- Do not use local file paths for references unless you have reviewed the assembled `scripts/video_gen.js` and explicitly consent to local read-and-upload to WeryAI; otherwise prefer public **`https`** URLs.
- Do not invent undocumented API fields beyond the JSON surface in this skill.
- Do not assume multi-image or first/last-frame support without checking live metadata when the behavior matters.
- Do not store the secret value of `WERYAI_API_KEY` inside the repository.
- Do not copy parameter names blindly from another provider without checking the normalized fields in this document.

## Model & API constraints (frozen for this skill)

> Frozen from the repository's current WeryAI capability snapshots. Re-run `node scripts/video_gen.js models` after platform upgrades.

### Text-to-video (`WERYDANCE_2_0`)

| model_key | durations | aspect_ratios | resolutions | Audio | negative_prompt | Prompt max |
|-----------|-----------|---------------|-------------|-------|-----------------|------------|
| `WERYDANCE_2_0` | 5, 10, 15 | 9:16, 1:1, 16:9 | 480p, 720p | Yes | No | 2000 |

### Image-to-video (`WERYDANCE_2_0`)

| model_key | durations | aspect_ratios | resolutions | Audio | negative_prompt | upload_image_limit |
|-----------|-----------|---------------|-------------|-------|-----------------|-------------------|
| `WERYDANCE_2_0` | 5, 10, 15 | 9:16, 1:1, 16:9 | 480p, 720p | Yes | No | 3 |

### Multi-image and first-frame / last-frame

- Use the `images` array for multi-image generation.
- Use either `images` with ordered URLs, `first_frame` + `last_frame`, or `image` + `last_image` for start/end-frame control.
- Before a paid submission where multi-image support matters, run `node scripts/video_gen.js models --mode multi_image_to_video` and confirm `support_multiple_images`, `support_first_last_frame`, `upload_image_limit`, and allowed output fields on the live account.
- If the live registry says the model cannot take multiple images, the runtime falls back to the first image only.

---

## Default parameters

| Field | Value |
|-------|-------|
| Model | `WERYDANCE_2_0` |
| Aspect ratio | `9:16` |
| Duration | `5` |
| Resolution | `720p` |
| Audio | **`true`** by default; expanded **`prompt`** must include **`Audio:`** unless the user wants silent |
| Prompt style | concise cinematic English prompt with one clear motion beat and one final payoff |

---

## Text brief -> Seedance video

Use this when the user has only an idea and wants Werydance 2.0 to generate the clip from scratch.

**Need from the user:**

- Subject or scene
- Motion beat
- Preferred aspect ratio or platform
- Optional duration and resolution

**Flow:**

1. Expand the brief into a full English prompt.
2. Keep `model` at `WERYDANCE_2_0` unless the user explicitly wants another model.
3. Show a confirmation table:

   > 📋 **Ready to generate - please confirm**
   >
   > | Field | This run | Notes |
   > |-------|----------|-------|
   > | `model` | `WERYDANCE_2_0` | Override only if the user explicitly requests another model |
   > | `aspect_ratio` | `9:16` | Must stay inside the Seedance row |
   > | `duration` | `5` | Allowed: 5 / 10 / 15 |
   > | `resolution` | `720p` | Allowed: 480p / 720p |
   > | `generate_audio` | `true` | Default **on**; **`Audio:`** in **`prompt`** unless user wants silent |
   > | `prompt` | **full expanded prompt** | Never show only a summary |

4. After confirmation, run:

   ```sh
   node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"...","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'
   ```

---

## Single reference image -> Seedance motion

Use this when the user already has one reference image and wants subtle or medium motion while preserving the subject.

**Need from the user:**

- One reference image URL (prefer public `https`)
- Desired motion direction
- Optional duration, aspect ratio, and audio

**Flow:**

1. Expand the prompt around preservation plus motion.
2. Add `image` to the JSON body.
3. Confirm parameters and URL, then run:

   ```sh
   node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"...","image":"https://example.com/input.png","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'
   ```

---

## Multiple reference images -> Seedance storyboard clip

Use this when the user wants several frames turned into one coherent shot or short sequence.

**Need from the user:**

- Ordered reference image URLs (prefer public `https`)
- Desired transition logic
- Optional duration and aspect ratio

**Flow:**

1. Treat the image order as meaningful story order.
2. If support is uncertain, check `models --mode multi_image_to_video` first.
3. Confirm the final prompt plus ordered `images`, then run:

   ```sh
   node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"...","images":["https://example.com/1.png","https://example.com/2.png","https://example.com/3.png"],"duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'
   ```

---

## First frame + last frame -> controlled transition

Use this when the user wants tighter motion control from a known opening frame to a known ending frame.

**Need from the user:**

- One reference start-frame URL (prefer public `https`)
- One reference end-frame URL (prefer public `https`)
- A prompt that explains the in-between action

**Flow:**

1. Expand the prompt so it explicitly bridges the first frame to the last frame.
2. Use either `first_frame` / `last_frame`, `image` / `last_image`, or pass the same two URLs through `images` in order.
3. Confirm both URLs and the full prompt, then run:

   ```sh
   node scripts/video_gen.js wait --json '{"model":"WERYDANCE_2_0","prompt":"...","first_frame":"https://example.com/start.png","last_frame":"https://example.com/end.png","duration":5,"aspect_ratio":"9:16","resolution":"720p","generate_audio":true}'
   ```

4. If the live registry rejects multi-image routing, reduce expectations: the runtime will fall back to single-image behavior with the first frame.
