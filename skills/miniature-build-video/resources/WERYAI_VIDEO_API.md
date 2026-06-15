# WeryAI video CLI & JSON (`video_gen.js`)

Shipped at **`resources/WERYAI_VIDEO_API.md`** (next to `SKILL.md`). From the skill package root, run **`node scripts/video_gen.js`** (see examples below). **Node.js 18+** required.

This file describes **CLI usage, JSON shape, and image handling**. Per-skill rules (prompt expansion, confirmation tables, allowed models) live in each skill’s **`SKILL.md`**.

---

## What you need by generation mode

The script picks the API route from your JSON:

| Mode | When | Required in JSON | API path (conceptually) |
|------|------|-------------------|-------------------------|
| **Text → video** | No `image` and no non-empty `images[]` | `model`, `prompt`, `duration` (and any optional fields the **model** supports) | `text-to-video` |
| **Image → video** | Non-empty string `image` | Same as above **plus** `image` — **must be a public `https` image URL** (see below) | `image-to-video` |
| **Multi-image → video** | Non-empty `images` array | Same as above **plus** `images` — **every element must be a public `https` image URL** | `multi-image-to-video` |

- **`model`**: required for real runs and for `--dry-run` when `prompt` is present. Empty/missing → `MISSING_PARAM` (there is **no default model**). The script does **not** enforce skill-specific model allowlists—callers must match the skill’s `SKILL.md`.
- **`prompt`**: required for `wait` and all `submit-*` flows that generate video.
- **`duration`**: sent to the API; must be one of the values allowed for the chosen model (check `models` output or the skill’s frozen table).
- Other fields (`aspect_ratio`, `resolution`, `generate_audio`, `negative_prompt`) are **only** valid if that model supports them—see `node scripts/video_gen.js models` and the skill’s **`## Model and API constraints`**.

---

## Image-to-video & multi-image: public URL requirement

For **image-to-video** (`image`) and **multi-image-to-video** (`images[]`), the value that ultimately reaches WeryAI must be a **public, directly fetchable image URL on the internet**:

- **Scheme must be `https://`** — plain **`http://` image URLs are rejected** by `video_gen.js` and must not be used.
- The URL must be reachable **from WeryAI’s servers** (not `localhost`, `127.0.0.1`, LAN-only hosts, or links that only work inside your browser session).
- Do **not** pass opaque file paths, `data:` URLs, or private object-storage links that are not already a stable public `https` address.

**Operational rule for skills and operators:** treat **public `https` image URLs as mandatory** for any image-to-video request. Host the image on a CDN, object storage with public read, or any HTTPS endpoint the API can GET without your local machine.

---

## Image input: public URL vs local path (how `video_gen.js` behaves)

### Normal path: public **https** URL (required for correct image-to-video usage)

- Put that URL in `image` (single) or each entry of `images[]` (multi).
- The script **does not** re-upload; it sends the URL straight to the video API.
- This matches the **public URL requirement** above.

### Advanced: local file → script uploads, then uses returned public URL

If `image` or an `images[]` entry is **not** already a public https URL, `video_gen.js` treats it as a **local path** (or `file://…`) and:

1. Reads the file from disk.
2. **POST**s it to **`https://api-growth-agent.weryai.com/growthai/v1/generation/upload-file`** with `Authorization: Bearer $WERYAI_API_KEY` and multipart fields `batch_no`, `fixed`, `file`.
3. Parses the response for a returned **public https** URL and substitutes that URL into the JSON sent to **video** generation — i.e. the video API still only ever sees a **public URL**; the script is just creating one from a local file.

**Implications (local path only)**

- Requires **`WERYAI_API_KEY`** with access to both **video** and **upload-file** endpoints.
- File must exist and be a **regular file**. Extensions with sensible MIME types in script: **`.jpg` / `.jpeg` / `.png` / `.webp` / `.gif`**.
- **`--dry-run`**: does **not** upload; stdout may still show local paths with a note that a real run would upload first.

**Skills / product docs:** prefer telling users to supply a **public `https` link**; use local paths only after **reviewing `video_gen.js`** and **explicit user consent** to read and upload files.

### Multi-image limits in this script

- `images` is passed through after upload resolution; the built request body keeps **at most the first 3** entries (`images.slice(0, 3)`). Models may allow fewer—always check `models` / skill tables (e.g. `upload_image_limit`).

---

## Environment

- **`WERYAI_API_KEY`** (required for `models`, generation, `status`, and local-image upload; **not** required for `--dry-run` only): bearer token. Never commit the value.
- **No other environment variables** are read. Hosts are fixed in `video_gen.js`. The **`wait`** command polls task status with **exponential backoff**: first delay **3s**, then **6s → 12s → 24s → …** (each step doubles), **capped at 60s** between polls, with a **total wall-clock budget of 600s (10 minutes)** before timeout.

## API hosts (fixed)

| Purpose | Base URL |
|---------|-----------|
| Video generation & task status | `https://api.weryai.com` |
| Model registry (`models` command) | `https://api-growth-agent.weryai.com` |
| Local file → public URL (upload) | `https://api-growth-agent.weryai.com/growthai/v1/generation/upload-file` |

---

## `models` — model metadata (JSON on stdout)

```sh
node scripts/video_gen.js models
node scripts/video_gen.js models --mode text_to_video
node scripts/video_gen.js models --mode image_to_video
node scripts/video_gen.js models --mode multi_image_to_video
```

Typical fields include `model_key`, `title`, `durations`, `aspect_ratios`, `resolutions`, `has_generate_audio`, `has_negative_prompt`, `prompt_length_limit`; image modes may add `support_multiple_images`, `support_first_last_frame`, `upload_image_limit`, etc. Use this to author **`## Model and API constraints`** in `SKILL.md`.

---

## `wait` — submit and block until done

```sh
node scripts/video_gen.js wait --json '{"model":"KLING_V3_0_PRO","prompt":"...","duration":5,"aspect_ratio":"9:16"}'
node scripts/video_gen.js wait --json '{"model":"...","prompt":"...","image":"https://cdn.example.com/pet.jpg","duration":5}'
node scripts/video_gen.js wait --json '{"model":"...","prompt":"...","images":["https://cdn.example.com/a.jpg","https://cdn.example.com/b.jpg"],"duration":5}'
# Advanced only: local paths trigger upload-file first; skills should default to public https URLs above.
node scripts/video_gen.js wait --json '{"model":"...","prompt":"...","image":"./girl.png","duration":5}'
node scripts/video_gen.js wait --json '...' --dry-run
```

Same JSON object is used for **`submit-*`**; only the blocking behavior differs.

---

## `submit-*` — submit only (async)

```sh
node scripts/video_gen.js submit-text  --json '{"model":"…","prompt":"…","duration":5}'
node scripts/video_gen.js submit-image --json '{"model":"…","prompt":"…","image":"https://…","duration":5}'
node scripts/video_gen.js submit-multi-image --json '{"model":"…","prompt":"…","images":["https://…","https://…"],"duration":5}'
# Advanced only: local file → upload then submit (same public-URL requirement for the API).
node scripts/video_gen.js submit-image --json '{"model":"…","prompt":"…","image":"./local.png","duration":5}'
```

**Note:** `submit-text`, `submit-image`, and `submit-multi-image` are **aliases** in this script: routing (text vs image vs multi-image) is decided **only** from JSON (`image` / `images`), exactly like `wait`. Use the verb that matches your intent; behavior is the same `submitTask` path aside from blocking.

Poll completion with **`status`** (below). Response JSON may include `batchId` / `taskIds` from the API; this CLI does **not** expose a separate `batch-status` subcommand.

---

## `status`

```sh
node scripts/video_gen.js status --task-id <id>
```

You may also pass a task id inside JSON as `task_id` or `taskId` when using `--json` (less common). If `--task-id` is omitted and JSON has no id, the script errors with `status command requires --task-id <id>`.

There is **no** `batch-status` command in `video_gen.js`; use per-task `status` with each `taskId` you care about. Invalid invocation prints a **Usage** line to stdout JSON (there is no `--help` flag).

---

## Agent UX: in-progress notice, task IDs, backoff polling, completion, skill name

Use this when an executor should **talk to the user** during async generation (not only return raw JSON).

1. **Right after a successful `submit-*`:** Tell the user that generation **has started** and paste **`taskId`** from stdout JSON. If the API returns **`batchId`** and/or **`taskIds`**, include those too so logs and support can correlate the job.

2. **Poll until terminal state:** Run `status --task-id <id>` repeatedly until the payload shows **completed** or **failed** (or your wrapper treats the script’s `phase` / `ok` as terminal). **Recommended delay between polls:** **3s, then 6s, then 12s, …** doubling each time, **cap at 60s**—the same pattern as **`wait`** uses inside `video_gen.js`. Stop early on success/failure; respect your own overall timeout if you need stricter limits than the built-in 10-minute `wait` budget.

3. **`wait` vs `submit-*`:** **`wait`** is one blocking call; it does **not** emit a separate “submitted” line for the user unless **your** layer prints one before/after. For “notify immediately, then poll in the open,” use **`submit-*`** and your own **`status`** loop with the backoff above.

4. **When generation finishes:** Summarize the **outcome** for the user: on success, **playable links** from **`videos`** (e.g. Markdown `[label](url)`); on failure, **`errorCode`** and **`errorMessage`**. **`video_gen.js` does not know which skill was used**—add **skill attribution** yourself from the active skill’s **`SKILL.md`** (e.g. frontmatter **`name`**) or the skill folder slug, in the same user-facing message.

---

## JSON field reference

| Field | Role |
|--------|------|
| `model` | **Required** (non-empty). No default. |
| `prompt` | **Required** for generation commands. |
| `duration` | Sent as number; default **5** if missing/invalid in script—still must be valid for the model. |
| `aspect_ratio` | Optional; model-dependent. |
| `resolution` | Optional; model-dependent. |
| `generate_audio` | Optional boolean; model-dependent. |
| `negative_prompt` | Optional string; model-dependent. |
| `image` | **Image-to-video:** use a **public `https` image URL** (required for normal use). Local path / `file://` is **script-only**: uploads first, then the API receives the returned public URL. |
| `images` | **Multi-image-to-video:** each entry must end up as a **public `https` URL** (directly, or via the script’s upload step). Up to **3** entries are forwarded after preparation. |

Do not send fields the chosen model does not support (reduces spurious `1002` / parameter errors).

---

## Status & stdout conventions

- HTTP OK with business `status === 0` (or `200` in some responses): request accepted for that layer.
- Generation success: look for completed phase and `videos` with `url` / `cover_url`.
- Errors: stdout JSON with `ok: false`, `errorCode`, `errorMessage` (script maps common API codes to short messages).
- Common keys: `ok`, `phase`, `taskId`, `batchId`, `taskIds`, `videos`, `tasks`, `inProgress`, `errorCode`, `errorMessage`.

---

**Reminder:** Skills may require user confirmation before any paid `wait` / `submit-*` call. For **any** image-to-video flow, assume **public `https` image URLs are mandatory** unless the skill explicitly documents a vetted local-upload path—always follow the active skill’s **`SKILL.md`**.
