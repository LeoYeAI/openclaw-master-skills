---
name: cinematic-story-video-gen
version: 1.1.0
description: "Generate and create cinematic story videos—film-language lighting, shallow depth of field, widescreen 16:9, orange–teal grade, narrative camera moves, and score-like audio via WeryAI. Use when you need to produce emotional scenes, brand mood films, character beats, or image-to-video from a still; expand short briefs into full prompts before submit. Default: KLING_V3_0_PRO; draft: SEEDANCE_2_0."

tags: [cinematic, narrative, film-look, drama, brand, widescreen, text-to-video, image-to-video, video-gen]

metadata: { "openclaw": { "emoji": "🎬", "primaryEnv": "WERYAI_API_KEY", "paid": true, "network_required": true, "requires": { "env": ["WERYAI_API_KEY"], "bins": ["node"], "node": ">=18" } } }
user-invocable: true
---

# Cinematic story & film-language video

**Cinematic story video** in one line: dramatic light, **shallow depth of field**, **widescreen** framing, believable skin, optional **orange–teal** contrast, subtle **film grain**, and camera grammar (dolly, track, orbit, foreground occlusion)—plus **piano / strings / ambient**-style audio when models allow.

## Use when

- Someone asks for a **cinematic**, **film look**, **movie-like**, or **mood / atmosphere** clip with **story** or **emotion** (not only a generic filter).
- **Brand film**, **hero moment**, **dialogue-free beat**, or **B-roll** that should read like narrative cinema.
- **Text-to-video** or **image-to-video** (single reference still) with **16:9** (default), **9:16**, or **1:1**.
- Users mention **orange and teal**, **film grain**, **bokeh**, **rack focus**, **slow push-in**, or **cinematic lighting**.

**Narrative cinema in motion:** strong light–shadow hierarchy, shallow depth of field, widescreen framing, believable skin tones, warm key vs cool fill (orange–teal when it fits the scene), subtle film grain, and camera grammar that reads like a scene—not a filter dump.

**Model choice (this package):** **⭐ Best** → **`KLING_V3_0_PRO`** (default for final emotion, skin, and lighting). **👍 Good** → **`KLING_V3_0_STA`** (balanced cost). **⚡ Fast / draft** → **`SEEDANCE_2_0`** with **`resolution`** **`720p`** (explicit resolution control; omit **`negative_prompt`** for this model). Kling rows **must omit `resolution`** from JSON.

**Dependencies:** `WERYAI_API_KEY` + Node.js 18+. This folder includes **[`references/WERYAI_VIDEO_API.md`](references/WERYAI_VIDEO_API.md)** (CLI/API reference); **`scripts/video_gen.js`** is supplied by your **sync / publish** step (same as other WeryAI video skills). Full commands and JSON fields: **[`references/WERYAI_VIDEO_API.md`](references/WERYAI_VIDEO_API.md)**. **No other Cursor skills required.**

## Prerequisites

- `WERYAI_API_KEY` **must be set** before running `video_gen.js`.
- Node.js **18+**; prefer public **`https`** image URLs. If the bundled runtime supports local file paths, review `scripts/video_gen.js`, verify read-and-upload behavior, and obtain **explicit consent** before using a local path.
- **Model:** `video_gen.js` **requires** a non-empty `model` in every `submit-*` / `wait` JSON—no script default. List the chosen **`model_key`** in the confirmation table.
- Each successful **`submit-*`** / **`wait`** may consume credits; re-submit creates new paid tasks.

## Security, secrets, and API hosts

- **`WERYAI_API_KEY`**: Treat as a secret; never commit its value. OpenClaw metadata lists **`requires.env`** / **`primaryEnv`** so installers know it is mandatory at runtime.
- **API hosts (fixed in `video_gen.js`)**: Video tasks use **`https://api.weryai.com`**; the models list uses **`https://api-growth-agent.weryai.com`**. Do not document or rely on host overrides—only **`WERYAI_API_KEY`** is read from the environment.
- **Local image handling:** Prefer **`https`** URLs. If the bundled runtime can read local files, it may upload them to WeryAI to obtain a public URL before image-to-video; require review, verification, and **explicit consent** before that path.
- **Higher assurance:** Run in an isolated environment; review `scripts/video_gen.js` before production use.

## Pre-submit gate (mandatory)

⚠️ **No paid submit without explicit user confirmation.** Do **not** call `submit-text`, `submit-image`, or `wait` until the user has **explicitly approved** the parameter table below, including the **full expanded `prompt`** (entire text, not a summary). **Never** infer consent from silence. **Explicit** means **confirm** / **go** / **approved** / **yes, generate** (or equivalent).

**Parameter confirmation table (show before submit):** `model`, `duration`, `aspect_ratio`, `resolution` (**only** if the chosen model supports it—**never** for Kling V3), `generate_audio`, `negative_prompt` (**only** for models that support it), **full expanded `prompt`**.

## Workflow

1. Confirm the request matches this skill (text-to-video and/or single image-to-video).
2. Collect the user's **brief**, optional **`image`** URL, and **tier**:
   - **Default / best / "final"** → **`KLING_V3_0_PRO`**
   - **Balanced / good** → **`KLING_V3_0_STA`**
   - **Draft / cheap / fast** → **`SEEDANCE_2_0`** (use **`resolution`** **`720p`** or **`480p`**; **do not** send **`negative_prompt`**)
   - User may **name a `model_key`** explicitly if it appears in the frozen table for the active channel—then ignore tier defaults for `model`.
3. Collect **aspect**: default **`16:9`** for widescreen story; use **`9:16`** or **`1:1`** when the user targets mobile or square feeds.
4. **Expand prompt (mandatory):** Unless the user supplied a finished long prompt (within **`prompt_length_limit`**) and asked **not** to rewrite, expand per **`## Prompt expansion (mandatory)`**. **Do not** submit only the user's minimal words.
5. Validate JSON fields against the frozen tables: **Kling** → **omit `resolution`**; **Seedance** → include **`resolution`** when using that model; **`negative_prompt`** only for Kling (optional but recommended with a short cinematic-safe line).
6. **Pre-submit gate:** Show the confirmation table with the **full expanded `prompt`**; **stop** until explicit approval or edits.
7. **Submit (async, default):** After approval, run **`submit-text`** or **`submit-image`**. **Do not** start a long blocking **`wait`** in the same turn unless the user **already** asked to block until the video is ready.
8. **Immediate notify:** On success with **`taskId`** / **`batchId`** (or documented id fields), **immediately** tell the user: accepted, id(s), short queue note, and **ask** whether to continue with **`status`** polling or **`wait`**. **Do not** run long invisible **`wait`** loops without this choice.
9. **Continue (user-driven):** Only after the user agrees, poll `status --task-id …` **or** run `wait --json '…'` with the **same** payload—per user preference.
10. When presenting playable URLs, use **Markdown inline links only** (e.g. `[Video](https://…)`). **Do not** wrap those links in code fences.

## CLI reference

**Single source of truth:** All concrete **`video_gen.js`** usage—`submit-text` / `submit-image` / `submit-multi-image`, **`status`**, **`wait`**, JSON field rules, image URL requirements, stdout keys, and copy-paste examples—is documented in **[`references/WERYAI_VIDEO_API.md`](references/WERYAI_VIDEO_API.md)** (next to `SKILL.md` under **`references/`**).

**Portable invocation (OpenClaw `{baseDir}`):** run from the skill package root; in OpenClaw listings, `{baseDir}` resolves to that root.

```sh
node {baseDir}/scripts/video_gen.js submit-text --json '{"model":"KLING_V3_0_PRO","prompt":"<expanded English prompt>","duration":10,"aspect_ratio":"16:9","generate_audio":true}'
node {baseDir}/scripts/video_gen.js status --task-id "<TASK_ID>"
```

**Blocking until done** (only if the user asked to wait): `node {baseDir}/scripts/video_gen.js wait --json '…'` with the **same** JSON shape—see **[`references/WERYAI_VIDEO_API.md`](references/WERYAI_VIDEO_API.md)**.

**This skill adds only model-specific filtering on top of that doc:** build JSON that satisfies **`## Model and API constraints`** here (e.g. **omit `resolution`** for **Kling V3**; **include `resolution`** for **Seedance 2.0**; **do not** send **`negative_prompt`** to **Seedance**). **Default rhythm:** after explicit confirmation, prefer **async `submit-*`** then **`status`**; use **`wait`** only when the user asked to block until completion—see the **Agent UX** section in the API file for polling guidance.

## Prompt expansion (mandatory)

`video_gen.js` does **not** auto-expand. Before **`submit-*`** or **`wait`**, turn short input into a **full English production `prompt`** aligned with **cinematic story** grammar—not generic “cinematic” adjectives only.

**When:** Brief, vague, missing shot/light/audio detail, or **no usable prompt** (topic only)—still build a full `prompt`.

**What to add (checklist):**

- **Look:** cinematic, dramatic lighting, shallow depth of field, widescreen composition, subtle **film grain**, **orange–teal** or warm key vs cool fill, natural **skin tone** priority for people.
- **Lens & depth:** subtle anamorphic-style cues if appropriate; **rack focus** or **bokeh** where it serves emotion; foreground objects for **parallax** and **occlusion** transitions.
- **Camera grammar (pick 1–2 per clip):** **slow push-in (dolly in)**; **lateral track**; **gentle orbit**; **foreground silhouette passing**—describe speed and motivation (hesitation, revelation, intimacy).
- **Narrative:** a **clear emotional beat** or story moment within `duration`.
- **Negative space & composition:** rule-of-thirds, lead room, eye-line continuity if two subjects.
- **Audio (mandatory when `generate_audio` is true):** labeled **`Audio:`** block—**cinematic underscore** (generic: **piano**, **strings**, subtle **pulse** or **ambient electronic** pads), room tone, soft foley; **no** copyrighted tracks or recognizable branded cues. If the user wants **silent** video: set **`generate_audio`: `false`** and omit audio from the prompt; state that in the confirmation table.

**Style anchors (weave naturally):** *cinematic, dramatic lighting, shallow depth of field, widescreen, film grain, orange teal contrast.*

**Length:** Stay within **`prompt_length_limit` 2000** for the selected model in the frozen table; drop lower-priority adjectives before losing the core beat.

**Confirmation:** The pre-submit table **must** include the **full** expanded `prompt`.

**`### Example prompts`** below are **richness targets only**—always derive from the user's actual brief.

## Definition of done

Done when the user gets at least one playable Markdown inline link whose label is **Video** and whose target is **`https://…`**, or a clear failure with next steps. **Pre-submit:** parameters and **full expanded `prompt`** were **explicitly** confirmed. **After submit:** user was notified with task id(s) and **chose** `status` vs blocking **`wait`**. Submitted JSON **must** match the frozen row for the chosen **`model_key`** (especially: **never** send **`resolution`** to Kling V3; **never** send **`negative_prompt`** to Seedance 2.0). **`generate_audio`** defaults to **`true`** when the model supports audio unless the user requested silent output.

## Boundaries (out of scope)

- Do **not** send **`resolution`** on **`KLING_V3_0_PRO`** or **`KLING_V3_0_STA`**—it is unsupported and may cause parameter errors.
- Do **not** send **`negative_prompt`** for **`SEEDANCE_2_0`** (not supported).
- Do **not** rely on paths or unofficial docs outside this package for CLI/API details; use only **`references/WERYAI_VIDEO_API.md`**.
- Do **not** embed the secret value of `WERYAI_API_KEY` in files.
- Do **not** wrap user-facing playable URLs in Markdown code fences.

### Example prompts

- `Make a 16:9 cinematic brand mood film—slow push-in, orange-teal grade, shallow DOF, soft strings`
- `Woman learns bad news by a rainy window—slow dolly in, teal shadows, warm lamp, piano and strings`
- `Two colleagues reconcile in a lobby—orbit, shallow DOF, foreground plant wipes frame, subtle score`
- `Turn this photo into a moody film scene—gentle push-in, film grain, orange key on skin, cool background, ambient bed (image URL in JSON)`

---

## Model and API constraints (frozen for this skill)

> Derived from repository alignment with WeryAI model metadata (2026-03-21 snapshot). **Re-run** `node scripts/video_gen.js models` after platform upgrades and refresh this table if values change.

### Text-to-video

| model_key | durations | aspect_ratios | resolutions | Audio | negative_prompt | prompt limit |
|-----------|-----------|---------------|-------------|-------|-----------------|--------------|
| `KLING_V3_0_PRO` | 5, 10, 15 | 9:16, 1:1, 16:9 | *(omit—do not send)* | Yes | Yes | 2000 |
| `KLING_V3_0_STA` | 5, 10, 15 | 9:16, 1:1, 16:9 | *(omit—do not send)* | Yes | Yes | 2000 |
| `SEEDANCE_2_0` | 5, 10, 15 | 9:16, 1:1, 16:9 | 480p, 720p | Yes | No (do not send) | 2000 |

### Image-to-video (single `image`)

| model_key | durations | aspect_ratios | resolutions | Audio | negative_prompt | Notes |
|-----------|-----------|---------------|-------------|-------|-----------------|--------|
| `KLING_V3_0_PRO` | 5, 10, 15 | 9:16, 16:9, 1:1 | *(omit)* | Yes | Yes | single `image` |
| `KLING_V3_0_STA` | 5, 10, 15 | 9:16, 16:9, 1:1 | *(omit)* | Yes | Yes | single `image` |
| `SEEDANCE_2_0` | 5, 10, 15 | 9:16, 1:1, 16:9 | 480p, 720p | Yes | No (do not send) | `upload_image_limit` **3** (this skill documents single-image flow by default) |

---

## Recommended models

| Tier | model_key | Default duration | Notes |
|------|-----------|------------------|--------|
| ⭐ Best (default) | `KLING_V3_0_PRO` | 10 (use **15** for slower emotional arcs) | **Omit `resolution`.** Optional **`negative_prompt`** for clean cinematic output |
| 👍 Good | `KLING_V3_0_STA` | 10 | **Omit `resolution`.** Lower cost than Pro |
| ⚡ Fast / draft | `SEEDANCE_2_0` | 10 | Set **`resolution`** **`720p`** (or **`480p`**). **No `negative_prompt`** |

**Tier keywords:** unspecified / quality-first → **Best**; "balanced" / "good" → **Good**; "draft" / "cheap" / "fast" → **Fast** (`SEEDANCE_2_0`).

---

## Default parameters

| Field | Value |
|-------|--------|
| `model` | `KLING_V3_0_PRO` unless tier or user overrides |
| `aspect_ratio` | **`16:9`** (widescreen story); **`9:16`** / **`1:1`** when the user names mobile or square |
| `duration` | `10` (use **`5`** for a single beat; **`15`** on Kling/Seedance for slower arcs) |
| `resolution` | **Only for `SEEDANCE_2_0`:** **`720p`** (or **`480p`**)—**omit for Kling** |
| `generate_audio` | **`true`** unless the user requests silent |
| `negative_prompt` | **Kling only** (optional); e.g. `watermark, illegible text, oversharpened CGI, plastic skin`—omit for Seedance |

---

## Scenario: Text-to-video cinematic story

1. Capture subject, emotion, and setting (or accept a minimal brief).
2. **Expand** per **`## Prompt expansion (mandatory)`**; pick **`model_key`** from tier rules.
3. **Pre-submit gate** → explicit user confirmation (full **`prompt`**, correct optional fields per model).
4. **`submit-text`** → notify → user chooses **`status`** vs **`wait`**.

---

## Scenario: Image-to-video cinematic story

**Before use:** Prefer public **`https://`** URLs. Local paths only with verified runtime support and **explicit consent**.

1. Plan motion (focus pull, parallax, occlusion) and respect likeness if requested.
2. Expand prompt; include `image` and **`model_key`** in the confirmation table.
3. After explicit confirm: **`submit-image`** (or **`wait`** if the user pre-requested blocking).

---

## Loop seam (optional)

If the user asks for a **seamless loop**, append at the **end** of the expanded prompt: `seamless loop`, `perfect loop`, `ends where it begins`—no separate API flag.

> Skill: `cinematic-story-video-gen`.
