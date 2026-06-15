---
name: miniature-build-video
version: 1.0.2
description: "Generate vertical miniature build & reveal shorts (WeryAI): text or finished-shot image to shallow-depth push-ins, lights coming on, immersive camera. Use when you need a miniature diorama reel, tilt-shift room clip, or the user asks for a tiny house lights-on moment or a slow push into interior detail. Requires WERYAI_API_KEY at runtime (declared in frontmatter for registries). SEO: miniature build video; miniature model build video generation."

tags: [craft, miniature, immersive, creative, aesthetic, short-video]

requires: { env: ["WERYAI_API_KEY"] }

metadata:
  openclaw:
    emoji: "🏗️"
    primaryEnv: "WERYAI_API_KEY"
    paid: true
    network_required: true
    requires:
      env:
        - "WERYAI_API_KEY"
      bins:
        - "node"
      node: ">=18"
user-invocable: true
---

# Miniature build & diorama video generation

Late night: a matchbox-sized Japanese konbini glows amber; the camera eases out of darkness toward it—bokeh swallows the world while the glass door, shelves, and tiny fluorescents stay sharp. That “small but real” immersion is the emotional hook this skill targets.

Conbini, rainy noodle stand, cyberpunk workshop—or a photo of a finished build: one line or one image → clip.

**Dependencies:** `WERYAI_API_KEY` + Node.js 18+. When you run the CLI, **`scripts/video_gen.js`** must exist; **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)** must exist under **`resources/`** (supply both via publish or pre-use assembly). Full commands and JSON fields: see **`resources/WERYAI_VIDEO_API.md`**. No other Cursor skills. **Default parameters** and model tiers are in the tables below; live API limits follow **weryai** models. Before installing or running, review the bundled `video_gen.js` to confirm it meets your requirements. Pay particular attention to how it handles local files if you choose to allow their usage, ensuring this behavior aligns with the skill's intended workflow for image-to-video requests.

**Registry metadata:** The only **required** runtime secret is **`WERYAI_API_KEY`**. It appears in YAML frontmatter as top-level **`requires.env`** (flow mapping, for tools that flatten root keys only), **`metadata.openclaw.primaryEnv`**, and **`metadata.openclaw.requires.env`**. Skill directories and registries **should** surface that requirement up front so installers see it before download. Never commit the key inside the package.

## Before you install or set `WERYAI_API_KEY`

1. **Trust:** Confirm you trust **WeryAI** and accept that **prompts** and **image inputs** (URLs and, if used, uploaded bytes) are sent to WeryAI’s servers over the network.
2. **Sensitive content:** Do **not** put **secrets** in `prompt`. Do **not** supply **image URLs or local files** you consider sensitive unless you accept provider-side processing.
3. **`--dry-run` first:** Run `node scripts/video_gen.js wait --json '…' --dry-run` (and/or `submit-*` with `--dry-run`) **before** setting a key to inspect the JSON shape; **`WERYAI_API_KEY` is not required for `--dry-run` only** (see **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**).
4. **Source:** If you cannot verify the package author or need strict data control, do **not** set `WERYAI_API_KEY`, or run only in an **isolated / test** environment.

## Environment variables (bundled `video_gen.js`)

- **Required for real API calls:** **`WERYAI_API_KEY`** only (models, generation, `status`, local-image upload). **Not required** for **`--dry-run` only**.
- **Not read by this script:** Environment variables **do not** override API hostnames; **`https://api.weryai.com`** and **`https://api-growth-agent.weryai.com`** are **fixed in code** (see Security). Do not expect URL-override knobs—there are none in this build.
- **Polling:** `wait` uses **fixed** exponential backoff and timeout constants in the script (see **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**), not separate poll env vars in this package.

## Script vs skill defaults (must match JSON)

- **`model`:** The CLI **has no built-in default model**. If `model` is missing or empty in JSON, `video_gen.js` returns **`MISSING_PARAM`** (`no default model`). This skill’s **recommended** default in tables is **`KLING_V3_0_PRO`**—always pass **`"model":"<confirmed key>"`** explicitly in `wait` / `submit-*` JSON so it matches the pre-submit table.
- **`resolution`:** For **`KLING_V3_0_PRO`** (this skill’s default tier), **omit `resolution` entirely** from JSON—sending it can cause **`1002` / parameter errors** for models that do not support that field. Only add `resolution` when the **chosen** model lists it in `node scripts/video_gen.js models` and your confirmation table explicitly includes it.

## Prerequisites

- `WERYAI_API_KEY` **must be set** in the environment before running `video_gen.js`.
- Node.js **18+** is required. Prefer public **`https`** image URLs. If the assembled `scripts/video_gen.js` supports local file paths, review and verify the script first, then get **explicit consent** before it reads a local image and uploads it to WeryAI to obtain a public URL.
- Each successful `wait` run consumes WeryAI credits; re-running creates new paid tasks.

## Security, secrets, and API hosts

- **`WERYAI_API_KEY`**: Treat as a secret. Only configure it if you trust this skill's source; it is listed in OpenClaw metadata as **`requires.env`** / **`primaryEnv`** so installers know it is mandatory at runtime (never commit it inside the skill package).
- **API hosts (fixed in `video_gen.js`)**: Video tasks use **`https://api.weryai.com`**; the models list uses **`https://api-growth-agent.weryai.com`**. The bundled script **pins** these bases in code—**only** **`WERYAI_API_KEY`** is read from the environment for authentication. Do not rely on any environment variables to change API hostnames; requests only go to those official endpoints plus the documented upload URL when a local image is uploaded (see **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**).
- **Local image handling disclosure**: Prefer public **`https`** image URLs. If the assembled `scripts/video_gen.js` supports local file paths, it may read a local image and upload it to WeryAI to obtain a public URL; require review / verification and explicit consent before using that path.
- **Remote processing:** Paid runs send **`prompt`** and image inputs to WeryAI; see **`## Before you install or set WERYAI_API_KEY`**.
- **Higher assurance:** Follow **`## Before you install or set WERYAI_API_KEY`**; use a short-lived or isolated environment for paid runs; review `scripts/video_gen.js` (HTTPS submit + poll loop) before production use. Verify whether the runtime can read local image files and upload them to WeryAI, and obtain explicit consent before using that path.


## Prompt expansion (mandatory)

`video_gen.js` does **not** expand prompts. Before every `wait --json`, turn the user's short or vague brief into a **full English production `prompt`**.

**When:** The user gives only keywords, one line, or loose intent—or asks for richer video language. **Exception:** They paste a finished long prompt within the model's `prompt_length_limit` and ask you **not** to rewrite; still show the **full** text in the confirmation table.

**Always add (video language):** shot scale and angle; camera move or lock-off; light quality and motivation; subject action paced to `duration`; **one clear payoff** for this niche; state **9:16 vertical** when this skill defaults to vertical.

**Length:** Obey `prompt_length_limit` for the chosen `model_key` when this doc lists it; trim filler adjectives before removing core action, lens, or light clauses.

**Confirmation:** The pre-submit table **must** include the **full expanded `prompt`** (never a one-line summary). Wait for **confirm** or edits.

### Niche checklist

- **Miniature world:** shallow DOF, practical warm lights, **dolly/push-in** reveal; diorama or room-in-a-box.
- **Beats:** build → paint → **lights on** or vehicle pass; cozy atmosphere, tactile materials.
- **Scale cues:** matchstick, coin, or fingertip references where useful.

**`### Example prompts`** at the top of this file are **short triggers only**—always expand from the user's actual request.

## Workflow

1. Confirm the user request matches this skill's scenario (text-to-video and/or image-to-video as documented).
2. Collect the user's **brief**, optional image URL(s), tier (**best** / **good** / **fast**) or an explicit `model` key.
3. **Expand prompt (mandatory):** Unless the user supplied a finished long prompt and explicitly asked not to rewrite it, expand the brief into a full English production `prompt` using `## Prompt expansion (mandatory)` below. **Do not** call the API with only the user's minimal words.
4. Check the **expanded** `prompt` against the selected model's `prompt_length_limit` in the frozen tables in this document (when present); shorten if needed.
5. Verify `duration`, `aspect_ratio`, `generate_audio`, `negative_prompt`, and other fields against the frozen tables in this document and **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**. Include **`resolution` only** when the **selected `model`** supports it (for this skill’s default **KLING** tier, **do not** send `resolution`—see **`## Script vs skill defaults`**).
6. Show the pre-submit parameter table including the **full expanded `prompt`**; wait for **confirm** or edits.
7. After confirmation, run `node scripts/video_gen.js wait --json '...'` with the **expanded** prompt.
8. Parse stdout JSON and return video URLs; on failure, surface `errorCode` / `errorMessage` and suggest parameter fixes.

## CLI reference

```sh
node scripts/video_gen.js wait --json '{"model":"…","prompt":"…","duration":5,"aspect_ratio":"9:16"}'
node scripts/video_gen.js wait --json '…' --dry-run
node scripts/video_gen.js status --task-id <id>
```

**Full reference:** **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**.

## Definition of done

Done when the user receives at least one playable video URL from the API response, or a clear failure explanation with next steps. All parameters used **must** fall within the selected model's allowed sets in this document. The submitted `prompt` **must** be the **expanded** production prompt unless the user explicitly supplied a finished long prompt and asked not to rewrite it.

## Boundaries (out of scope)

- Does not review platform compliance, copyright, or portrait rights; does not guarantee commercial usability of outputs.
- Does not provide non-WeryAI offline rendering, traditional edit timelines, or API field combinations not documented in this SKILL or **[`WERYAI_VIDEO_API.md`](resources/WERYAI_VIDEO_API.md)**.
- Do not link to `weryai-model-capabilities.md` or shared `../references/` paths; use **`resources/WERYAI_VIDEO_API.md`** for CLI/API details.
- Does not hard-code absolute paths in the skill doc; run `node scripts/...` from the skill package root (the directory containing `SKILL.md`) so `scripts/` and `resources/` paths resolve.

### Example prompts

- `Hand-built miniature café: final beat lights on inside, warm fill, slow push vertical`
- `Use this street diorama still: tiny car passes, shop windows light up`
- `Painted model on base, rotate reveal, ultra-shallow depth of field`
- `Miniature build reveal 9:16, cozy warm lights turning on inside tiny house`

---

## Default parameters

| Field | Value |
|-------|-------|
| Model | KLING_V3_0_PRO (must appear as `"model"` in JSON—the script does not default it) |
| Aspect ratio | 9:16 (fixed vertical) |
| Duration | Short (`duration`: 5); use 10 for a longer build pass |
| Resolution | **Omit** for KLING default (do not include the key in JSON) |
| Style | Very shallow DOF, believable materials, accent light on hero props, slow push or subtle orbit (fixed) |
| Audio | On (room tone + tiny prop detail for immersion) |

> **API validity (default `KLING_V3_0_PRO`):** Text-to-video `duration` only **5 / 10 / 15**; `aspect_ratio` only **9:16, 1:1, 16:9**. Image-to-video `aspect_ratio` only **9:16, 16:9, 1:1**. **No `resolution` field—do not send it.** For **fast** tier with VEO: text-to-video **`VEO_3_1_FAST`**, image-to-video **`CHATBOT_VEO_3_1_FAST`**, with `duration` **fixed at 8**, `aspect_ratio` only **9:16** or **16:9**. When switching `model_key`, follow the allowed sets in this section’s model/API constraints and the API validity note above; do not send `resolution` to models that do not support it.

---

## Scene description → miniature world

**Purpose:** Concrete scene ideas, fast visual tests, or batching mood variants—no physical model required.

**Inputs:**

**Scene type** (konbini / kitchen / cottage / corner stall / workshop / cyber set) and **mood** (warm healing / neon cyber / daylight / rainy amber). If mood is omitted, pick the lighting that usually performs for that scene. Optionally stress **build process** vs **finished tour**.

Extract key props and light, pick an angle that triggers “I want this,” build the prompt, show full parameters, wait for confirm, then `node scripts/video_gen.js wait --json '…'`.

> Full parameters are shown before generation; wait for confirmation.

**Parameter configuration:**

| Field | Value |
|-------|-------|
| model | KLING_V3_0_PRO |
| aspect_ratio | 9:16 |
| duration | 5 |
| generate_audio | true |
| resolution | *(omit—do not send for this model)* |

Example inputs:

“Japanese konbini at night, warm healing” → the skill builds:

> Extreme close-up macro shot at eye level, a palm-sized miniature Japanese convenience store diorama on a dark surface, warm amber interior light glows through tiny sliding glass doors and frostwork windows illuminating a perfectly detailed interior — miniature shelves stocked with thumb-sized product packages, a tiny register counter, a softbox ceiling panel. The camera dollies in very slowly at 30fps toward the entrance as if walking toward it, the shallow depth of field keeps only the storefront razor-sharp while the surrounding darkness melts away. Cold blue night-time ambient fills the exterior, creating a warm-cold color split at the door threshold. ASMR soft ambient hum, distant city night sound, faint interior muzak.

“Cyberpunk workshop, neon” →

> Medium close-up at 45-degree overhead angle, a miniature cyberpunk studio diorama the size of a shoebox — crammed with tiny glowing monitors, cable-draped desk, neon-lit bookshelves in pink and cyan, a miniature action figure at the keyboard. The camera orbits slowly around the scene at 60fps in a single smooth rotation, neon light refracts off every tiny reflective surface — monitor bezels, coffee mug, glossy floor tile. Volumetric light rays from the neon tubes create a soft haze above the scene. Deep black void background isolates the diorama completely. ASMR low electronic hum, faint keyboard clicks, ambient synth drone.

“Hand-build a log cabin from scratch, full process” →

> Close-up tracking shot over a clean white work mat, precise hands assemble a miniature log cabin frame piece by piece in time-lapse — wooden strips cut, glued, pressed together, roof tiles laid row by row, a tiny front door hung on micro hinges. Final sequence returns to real time 60fps: a hand places the last roof tile, steps back, and a small warm interior light switches on inside the finished cabin, its glow spilling through two windows onto the mat. Neutral overhead workshop light throughout, shallow depth of field isolates the build in progress from surrounding tools. ASMR wood snapping, glue applicator, the soft click of the interior light turning on.

> **Note:** More specific beats (palette, hero prop, time of day) track intent better. “Konbini” vs “late-night warm konbini push toward glass door” are different pictures.

---

## Model photo → immersive motion

**Purpose:** Finished physical model or reference still → camera motion for posts or archive.

**Inputs:**

**Image URL** (public HTTPS). Optional motion direction:
- **Slow push in:** From outside toward interior or front—depth emphasis
- **Lights on:** Dark to lit, sources coming up in sequence
- **Orbit:** Slow 360-style pass around the build

Default pick: if already bright inside → push; if dark → lights-on.

Read scene, existing light, and hero props; match motion; show parameters; confirm; `node scripts/video_gen.js wait --json '…'`.

> Full parameters are shown before generation; wait for confirmation.

**Parameter configuration:**

| Field | Value |
|-------|-------|
| model | KLING_V3_0_PRO |
| aspect_ratio | 9:16 |
| duration | 5 |
| generate_audio | true |
| resolution | *(omit—do not send for this model)* |
| image | User-supplied image URL |

Example:

“This is my cyber street build, orbit it https://...” →

> Starting from the miniature diorama in the image, the camera performs a slow smooth 180-degree orbital rotation around the scene at 30fps, each angle revealing new details of the model — signage, light sources, material textures. Shallow depth of field maintains focus on the nearest model surface throughout the rotation, blurring the far side into bokeh. The existing lighting in the image is preserved and enhanced with subtle lens flare at bright neon sources. ASMR ambient city soundscape matching the scene aesthetic.

> **Note:** Prefer public **`https`** URLs; login-gated or in-app-only links may fail. If the assembled `scripts/video_gen.js` supports local file paths, review/verify the script and explicitly consent before local read-and-upload to WeryAI. Clearer, more centered photos track camera motion better.

---

**Prompt keyword cheat sheet**

- Immersion: `shallow depth of field bokeh background`, `only the miniature in sharp focus`, `diorama isolated on dark surface`
- Light: `warm amber spill light`, `neon volumetric haze`, `cold-warm color contrast at threshold`, `interior light switching on`
- Camera: `slow dolly push-in`, `smooth orbital rotation`, `static locked-off reveal`, `gradual light fade-in`
- Materials: `visible wood grain texture`, `reflective tiny surface`, `thumb-sized detail props`, `micro scale furniture`
- Emotion: `inviting glow`, `tiny world feeling`, `perfectly scaled details`, `a world you could step into`
