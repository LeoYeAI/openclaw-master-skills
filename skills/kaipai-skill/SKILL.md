---
name: openclaw-kaipai-ai
version: 1.2.2
description: "Video file → videoscreenclear or hdvideoallinone + spawn-run-task and sessions_spawn (main session). Image → eraser_watermark or image_restoration + blocking run-task only (never spawn-run-task for image tasks). Process images or video with Kaipai AI — four tasks — image watermark removal (eraser_watermark), video watermark removal (videoscreenclear), image quality restoration (image_restoration), video quality restoration (hdvideoallinone). Use when the user asks for watermark removal or quality restoration on images or video. Paid API (consumes tenant quota); never claim the service is free or invent pricing. For videoscreenclear and hdvideoallinone, always use spawn-run-task plus OpenClaw sessions_spawn in the main session (never blocking run-task there); only bypass spawn if the host explicitly forbids sessions_spawn."
metadata: {"openclaw":{"emoji":"🖼️","requires":{"bins":["python3"],"env":{"MT_AK":{"required":true},"MT_SK":{"required":true}}},"tags":["image-processing","watermark-removal","image-restoration","kaipai","paid-api"]}}
---

# Kaipai Skill

## When to Use This Skill

Activate when the user wants any of the following:

- **Watermark removal** on images or video (remove watermark, eraser watermark, etc.)
- **Image quality restoration** (restore, upscale, enhance, super-resolution)
- **Video quality restoration** (video restore, upscale, hdvideo-style enhancement)

## Billing and user-facing claims (MANDATORY)

- **Fact:** Each successful **`run-task`** (including inside a **`sessions_spawn`** worker) goes through server-side **quota / credit consumption** for the **MT_AK** tenant. This is a **paid, metered commercial API**, not free compute bundled with the skill or the host.
- **Forbidden:** Do **not** state or imply that the service is **free**, costs nothing, uses **no quota**, has **unlimited trial**, or similar. Do **not** invent **prices**, **plan names**, **promotions**, or **trial rules**.
- **Allowed:** Neutral wording — e.g. processing **uses the Kaipai account quota** tied to the configured keys; **billing and plans** are **per your console or administrator**. If the user asks about cost, point them to **admin / official billing docs / console**; do not guess. When the API returns quota or membership errors, follow **Step 3 — MANDATORY (quota / consume failures)** using server **`detail`** and **`pricing_url`** when present.
- **On success too:** Success summaries must stay factual (task completed, delivery). Do **not** add “free” or zero-cost implications.

## Supported Algorithms

| task_name | Capability | Input |
|---|---|---|
| `eraser_watermark` | Image watermark removal | Image path or URL |
| `videoscreenclear` | Video watermark removal | Video path or URL |
| `image_restoration` | Image quality restoration | Image path or URL |
| `hdvideoallinone` | Video quality restoration | Video path or URL |

### Video tasks — default execution

For **`videoscreenclear`** and **`hdvideoallinone`**: **`spawn-run-task`** → pass **`sessions_spawn_args`** to **`sessions_spawn`** (main session does not block on **`run-task`**). Command shape, **`runTimeoutSeconds`** (default **3600**), worker **`install-deps`** / **`run-task`** / Step 4, polling and recovery: **[§3b](#3b--async-worker-sessions_spawn-all-video-tasks)** and **[docs/errors-and-polling.md](docs/errors-and-polling.md)**.

---

## Multi-stage pipelines (chaining tasks) / 多阶段管线

When the user asks for **more than one** Kaipai step on the **same** media (e.g. remove watermark **then** restore quality), treat each step as a **separate job**:

| Typical chain | Stages |
|---|---|
| Image | `eraser_watermark` → `image_restoration` |
| Video | `videoscreenclear` → `hdvideoallinone` |

**Rules:**

1. After stage A completes with `skill_status: "completed"`, use **`primary_result_url`** or **`output_urls[0]`** as **`--input`** for stage B with a **new** `--task`. That is a **new** job, not a retry of stage A. For **video**, stage B means a **new** **`spawn-run-task`** + **`sessions_spawn`** (each spawn embeds a **single** `run-task`), not a second `run-task` inside the same embed.
2. **“Do not re-run `run-task`”** in this skill means: **do not submit `run-task` again for the same `task_id` / the same submitted job** (use `query-task` to resume polling instead). It does **not** forbid the **next pipeline stage** with a different `task_name` and the previous result URL as input.
3. **Step 4 (delivery):** Prefer **final-stage** native delivery when the user wanted the full pipeline; intermediate stages may still run embedded Step 4 per worker (one spawn per video stage) — tune the user-facing copy if they only care about the last asset.
4. **Video chains (medeo-style):** **One `sessions_spawn` = one embedded `run-task`.** Do **not** put two `run-task` calls in one spawn. Chain = **multiple spawns**: after stage A, read **`primary_result_url`** from stdout or **`last-task`** / **`history`**, then **`spawn-run-task`** for stage B with that URL as **`--input`**. No video **`run-task`** in the main session. Optional one-line user update before the second spawn.

See also Step 3 success bullets and **`agent_instruction`** in the JSON.

---

## API submission path (MANDATORY)

- **New jobs:** Submit **only** via **`python3 {baseDir}/scripts/kaipai_ai.py run-task …`** (§3a / §3b), or the **same** `run-task` command embedded in **`spawn-run-task`** → `sessions_spawn`. **Do not** hand-craft HTTP to **wapi.kaipai.ai** or **AIGC / invoke** endpoints to replace that flow — that skips **`POST /skill/consume.json`** (quota and permission) and breaks the supported pipeline.
- **Exception:** **`query-task --task-id`** is **only** for resuming status polling on an **existing** full `task_id` (no upload, no second consume). **Do not** use it instead of **`run-task`** for a **new** submission.
- **No curl replay:** This skill does not emit debug curl for API calls. **Do not** hand-craft HTTP to **wapi / AIGC** to mimic requests — always use the **CLI** above so **`/skill/consume.json`** runs before algorithm submit.

---

## 0. Pre-Flight Check (MANDATORY — run before anything else)

Verify AK/SK are configured (**only run this command**; do not read other Python sources first):

```bash
python3 {baseDir}/scripts/kaipai_ai.py preflight
```

- Output `ok` → continue to Step 1
- Output `missing` → **stop** and send the user the configuration message below

**Feishu** — send an interactive card via the Feishu API (do not use the `message` tool for this):

```python
import json, urllib.request
cfg = json.loads(open("~/.openclaw/openclaw.json").read())
feishu = cfg["channels"]["feishu"]["accounts"]["default"]
token = json.loads(urllib.request.urlopen(urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": feishu["appId"], "app_secret": feishu["appSecret"]}).encode(),
    headers={"Content-Type": "application/json"}
)).read())["tenant_access_token"]
card = {
    "config": {"wide_screen_mode": True},
    "header": {"title": {"tag": "plain_text", "content": "🖼️ Kaipai — credentials required"}, "template": "blue"},
    "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": "Set **MT_AK** and **MT_SK** in `scripts/.env`, then run:\n```\nsource scripts/.env\n```\nIf you do not have keys, contact your administrator."}}],
}
urllib.request.urlopen(urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    data=json.dumps({"receive_id": "<USER_OPEN_ID>", "msg_type": "interactive", "content": json.dumps(card)}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
))
```

**Telegram / Discord / other channels** — use the `message` tool with plain text:

```
🖼️ Kaipai — credentials required

Set MT_AK and MT_SK in scripts/.env, then run:
  source scripts/.env

If you do not have keys, contact your administrator.
```

---

## Step 1 — Pick task and input

Choose `task_name` from the table above and confirm the input file location.

**Media type → `task_name` (MANDATORY checklist):**

1. **Video** — Path or URL ends with common video extensions (e.g. `.mp4`, `.mov`, `.webm`, `.mkv`, `.m4v`) **or** the user / attachment clearly indicates **video / clip / footage** → choose only **`videoscreenclear`** (watermark) or **`hdvideoallinone`** (quality). Then use **§3b** (`spawn-run-task` + `sessions_spawn`), not blocking `run-task` in the main session.
2. **Image** — Extensions like `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp` **or** the user says **photo / picture / screenshot / 图** (static image) → choose only **`eraser_watermark`** or **`image_restoration`**. Use **§3a** (`run-task` in the main session). **Do not** use **`spawn-run-task`** for these tasks (the CLI rejects it).
3. **Watermark vs quality** — “Remove watermark / 去水印” → `eraser_watermark` (image) or `videoscreenclear` (video). “Restore / upscale / enhance / 画质修复 / 清晰化” → `image_restoration` (image) or `hdvideoallinone` (video).
4. **Uncertain** — If media type is ambiguous (e.g. user only says “去水印” with no file), **ask one short clarifying question** (image or video?) or infer from IM attachment type per [docs/im-attachments.md](docs/im-attachments.md); do not guess the wrong modality.
5. **Same message: video + extra still image** — IM payloads often include **both** a **video** and a **separate still** (Feishu preview / `image_key`, Telegram or other **cover / thumbnail**, or an extra photo next to the clip). If the user’s wording targets **the video** (watermark or quality on the clip), use **only** that video as `--input` for **`videoscreenclear`** or **`hdvideoallinone`** (§3b). **Do not** submit **`eraser_watermark`** or **`image_restoration`** for the sibling image unless the user **explicitly** asks to process that picture too. Optional cover for **sending** the result is a delivery helper concern ([docs/feishu-send-video.md](docs/feishu-send-video.md), Telegram `--cover-url`), not a second Kaipai job.

**Getting media from IM messages** (full detail: [docs/im-attachments.md](docs/im-attachments.md)):

| Platform | How to obtain |
|---|---|
| Feishu | Message resource URL / `image_key` + `message_id` → optional **`resolve-input`** |
| Telegram | `file_id` → **`resolve-input --telegram-file-id`** (needs `TELEGRAM_BOT_TOKEN`) |
| Discord | `attachments[0].url` — often usable directly as `--input` |
| Generic | URL or path |

```bash
python3 {baseDir}/scripts/kaipai_ai.py resolve-input --file /tmp/saved.jpg --output-dir /tmp
# or: --url, --telegram-file-id, --feishu-image-key + --feishu-message-id
```

Use the JSON **`path`** field as **`--input`**.

**`--input` as `http(s)://` URL:** In shells, **quote the whole URL** so `&` in query strings (e.g. signed OSS links) is not split. Large or slow downloads: defaults are **120s read timeout** and **100MB** max (same as `resolve-input --url`); override with **`MT_AI_URL_READ_TIMEOUT`**, **`MT_AI_URL_CONNECT_TIMEOUT`**, **`MT_AI_URL_MAX_BYTES`**. For very large video or flaky links, prefer **`resolve-input --url`** then **`--input`** with the local **`path`**.

If the user already gave a path or URL when triggering the skill, go to Step 2 without asking again.

**Reply immediately** to acknowledge the task, for example:

> "🖼️ Processing — please wait a moment…"

---

## Step 2 — Install dependencies

```bash
python3 {baseDir}/scripts/kaipai_ai.py install-deps
```

If dependencies are already installed this step is quick; then continue to Step 3.

---

## Step 3 — Run the task

If **`task`** is **`videoscreenclear`** or **`hdvideoallinone`**, use **only** **[§3b](#3b--async-worker-sessions_spawn-all-video-tasks)** (`spawn-run-task` + `sessions_spawn`). Use **§3a** **only** for image tasks (`eraser_watermark`, `image_restoration`).

### 3a — Inline (blocking, image tasks only)

Use when the host can wait on the shell until the command returns (`eraser_watermark`, `image_restoration`).

```bash
python3 {baseDir}/scripts/kaipai_ai.py run-task \
  --task "<task_name>" \
  --input "<image_url_or_path>"
```

Replace `<task_name>` and `<image_url_or_path>` with the real values.

Default params include `rsp_media_type: url`. For custom JSON params:

```bash
python3 {baseDir}/scripts/kaipai_ai.py run-task \
  --task "<task_name>" \
  --input "<url_or_path>" \
  --params '{"parameter":{"rsp_media_type":"url"}}'
```

**When `run-task` exits 0**, stdout is JSON that includes:

- **`skill_status`: `"completed"`** — the algorithm and polling are finished; the result is in this response. If the user asked for **only this** stage, **proceed to Step 4**. If they asked for a **multi-stage pipeline**, use **`primary_result_url`** as `--input` for the **next** `--task` (see **Multi-stage pipelines** above); **Step 4 after the last stage**. **Do not** re-submit `run-task` for the **same `task_id`** (same job); use `query-task` to resume polling if needed.
- **`output_urls`** — ordered `http(s)` links (same extraction as before: `data.result.urls`, `images`, `media_info_list`, etc.).
- **`primary_result_url`** — same as `output_urls[0]` when present; convenient for delivery scripts.
- **`task_id`** — full task id as a top-level string when known (from `data.result.id` or the polling session). Keep it for manual status recovery or support handoff; do not truncate. Some synchronous completions may omit it if the API does not return an id.
- **`agent_instruction`** — short reminder for the model.
- **`meta` / `data`** — full API payload for debugging.

**MANDATORY (user-visible outcome):** When stdout JSON has **`skill_status`: `"completed"`** (from **`run-task`** or **`query-task`**), you **must** (1) send the user a **short natural-language summary** (success + what was done), and (2) **complete Step 4** on their channel (delivery scripts below) using **`primary_result_url`** or **`output_urls[0]`**, unless the user explicitly asked **only** for the URL with no IM delivery. **Do not** end the turn with only raw JSON in the tool transcript — the user should see a normal reply and the media or link in the chat.

**When `run-task` exits non-zero**, stdout is JSON with **`skill_status`: `"failed"`** (or an `error` field) — explain it to the user; do not treat as success or Step 4 delivery.

**MANDATORY (quota / consume failures):** When stdout JSON has **`failure_stage`: `"consume_quota"`** and **`error`** is **`credit_required`** (typically **`api_code` 60002**): you **must** send the user a **clear, user-visible** message grounded in the server **`detail`** (API `msg`). If the JSON includes **`pricing_url`** (extracted from that message when it contains an `https` link), **must** include it as a **clickable link**; if **`pricing_url`** is absent, **must** quote or paste the full **`detail`** so any links or instructions from the API still reach the user. **Do not** only dump raw JSON; **do not** retry **`run-task`** expecting success from tweaking **`--task`** / **`--params`** alone. When **`error`** is **`membership_required`** (**60001**): same rule (**`pricing_url`** when present, else full **`detail`**). When **`error`** is **`consume_param_error`**: treat as **parameter / invocation** mistakes — fix **`--task`**, **`--input`**, **`--params`** per SKILL and remote config; **do not** tell the user to recharge.

**Video tasks** use **§3b** in the main session. Polling, stderr, **`MT_AI_*`**, timeouts, SIGKILL / host caps, **`query-task`** / **`last-task`** recovery: **[docs/errors-and-polling.md](docs/errors-and-polling.md)** and **§3c–§3d**. Optional: raise host tool/session wait limits — does not replace **§3b** for video.

### 3b — Async worker (`sessions_spawn`, video tasks only)

**Forbidden:** Do **not** call **`spawn-run-task`** for **`eraser_watermark`** or **`image_restoration`**. Image tasks use **§3a** only. The CLI exits with an error if `--task` is not a video algorithm.

Same pattern as **medeo-video** `spawn-task`: the main agent does not block on polling; a sub-session runs `run-task` and is told exactly how to detect success and deliver.

1. Build the payload (`<task_name>` must be **`videoscreenclear`** or **`hdvideoallinone`**):

```bash
python3 {baseDir}/scripts/kaipai_ai.py spawn-run-task \
  --task "<task_name>" \
  --input "<video_url_or_path>" \
  --deliver-to "<oc_xxx_or_ou_xxx_or_chat_id>" \
  --deliver-channel "feishu"
```

Optional: `--params '<json>'` (same as `run-task`), `--deliver-channel telegram|discord|...`, `--run-timeout-seconds` (default **3600**, aligned with extended poll budget). **Do not reduce** `runTimeoutSeconds` below the payload default unless you accept timeout risk — wall time varies (often minutes to tens of minutes).

2. Call OpenClaw **`sessions_spawn`** with the printed **`sessions_spawn_args`** (`task`, `label`, `runTimeoutSeconds`) **without reducing** `runTimeoutSeconds` unless you intentionally accept timeout risk.

3. **Reply immediately** to the user that processing has started (same as Step 1 acknowledgment). The sub-agent completes **`install-deps`** (if needed), **`run-task`**, then Step 4 using **`skill_status` / `output_urls`** per the embedded task text. For **video** tasks on Feishu/Telegram, the payload instructs **`feishu_send_video.py`** / **`telegram_send_video.py`** after `curl` download.

**Multi-stage + spawn:** One embed = one **`run-task`** (medeo-style). Video chains: **Multi-stage pipelines** (rule 4). Image chains: **§3a** only — run **`run-task`** once per stage in the main session (or host-equivalent blocking shell); **do not** use **`spawn-run-task`** for image stages.

### 3c — Resume polling (`query-task`)

When you already have a **full `task_id`** (from a previous stdout JSON, e.g. success, `poll_timeout`, or `poll_aborted`, or from stderr `task_id=...` lines) and the job may still be running on the server — **do not run `run-task` again** for that id; resume polling only:

```bash
python3 {baseDir}/scripts/kaipai_ai.py query-task \
  --task-id "<full_task_id>"
```

Optional **`--task`** sets the `task_name` field in the success JSON for your logs (default labels as `query_task`). Uses the same **`MT_AK` / `MT_SK`** and remote config as the original submit. **Stdout JSON and exit codes** match **`run-task`**: exit **0** with `skill_status: "completed"` when the task finishes successfully; exit **non-zero** with `skill_status: "failed"` / `error` on timeout, query errors, or API-reported failure.

### 3d — Last task and history (user-visible)

Local state under **`~/.openclaw/workspace/openclaw-kaipai-ai/`** (`last_task.json`, `history/task_*.json`, last **50** records). For async **`run-task`**, **`last_task.json`** may briefly show **`skill_status`: `"polling"`** with **`task_id`** while the client is still polling (checkpoint so **`query-task`** can resume if the process is killed mid-poll):

```bash
python3 {baseDir}/scripts/kaipai_ai.py last-task
python3 {baseDir}/scripts/kaipai_ai.py history
```

Use when the user asks whether a recent job finished, or for a short history summary. Do not expose raw secrets.

---

## Step 4 — Deliver result to the channel

**Required after success:** When **`skill_status`** is **`completed`**, deliver here — the CLI does not post to IM by itself. Send the processed image or video back on the user’s platform (and keep the Step 3 **MANDATORY** summary in the same turn).

### Resolve deliver-to target

| Platform | Source | Format |
|---|---|---|
| Feishu group | `conversation_label` or `chat_id` without `chat:` prefix | `oc_xxx` |
| Feishu DM | `sender_id` without `user:` prefix | `ou_xxx` |
| Telegram | Inbound message `chat_id` | e.g. `-1001234567890` |
| Discord | `channel_id` | e.g. `123456789` |

### Feishu — image tasks

```bash
python3 {baseDir}/scripts/feishu_send_image.py \
  --image "<result_url>" \
  --to "<oc_xxx or ou_xxx>"
```

### Feishu — video tasks (`videoscreenclear`, `hdvideoallinone`)

```bash
curl -sL -o /tmp/kaipai_result.mp4 "<primary_result_url_or_output_urls[0]>"
python3 {baseDir}/scripts/feishu_send_video.py \
  --video /tmp/kaipai_result.mp4 \
  --to "<oc_xxx or ou_xxx>" \
  --video-url "<primary_result_url_or_output_urls[0]>" \
  [--cover-url "<optional_thumb_url>"] \
  [--duration <milliseconds_if_known>]
```

`--video-url` adds a second message with the download link. Optional cover/duration; details: [docs/feishu-send-video.md](docs/feishu-send-video.md).

### Telegram — image tasks

```bash
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 {baseDir}/scripts/telegram_send_image.py \
  --image "<result_url>" \
  --to "<chat_id>" \
  --caption "✅ Done"
```

### Telegram — video tasks

```bash
curl -sL -o /tmp/kaipai_result.mp4 "<primary_result_url_or_output_urls[0]>"
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 {baseDir}/scripts/telegram_send_video.py \
  --video /tmp/kaipai_result.mp4 \
  --to "<chat_id>" \
  --video-url "<primary_result_url_or_output_urls[0]>" \
  [--cover-url "<optional_thumb_url>"] \
  [--duration <seconds>] \
  --caption "✅ Done"
```

`--video-url` sends a follow-up text message with the download link. Max ~**50 MB** for Bot API video; larger files rely on the link line.

### Discord

Download the result, then send with the `message` tool (use **`.mp4`** for video, **`.jpg`** / **`.png`** for image):

```bash
curl -L "<result_url>" -o /tmp/result_image.jpg
```

Then:

```
message(action="send", channel="discord", target="<channel_id>", filePath="/tmp/result_image.jpg")
```

For files over ~25MB, send the result URL as a link instead.

### WhatsApp / Signal / others

Use the `message` tool with `media`, or send the result URL directly.

---

## Quick commands reference (agent)

| Command | Description | User-facing? |
|---------|-------------|--------------|
| `preflight` | AK/SK ok / missing | No |
| `install-deps` | pip install requirements | No |
| `run-task` | Submit + poll until done | Indirectly |
| `query-task` | Resume poll by `task_id` | When recovering |
| `spawn-run-task` | Print `sessions_spawn` payload — **`videoscreenclear` / `hdvideoallinone` only** | No |
| `resolve-input` | IM/URL → local path for `--input` | No |
| `last-task` | Last job JSON | Yes — “last job?” |
| `history` | Up to 50 recent records | Yes — “history?” |

---

## Notes

- **Single business entrypoint**: algorithm runs and config fetch go through `kaipai_ai.py`; agents do not need to open `client.py` / `ai/api.py`. **Must not** bypass this with direct HTTP to AIGC/wapi for new jobs — see **[API submission path (MANDATORY)](#api-submission-path-mandatory)** above. **`query-task`** is the supported way to resume polling when a **`task_id`** is already known.
- **Video tasks**: **`spawn-run-task` + `sessions_spawn`** in the main session (mandatory path); the worker runs **`run-task`** and delivery. **`run-task`** in the **main** session is for **image** tasks (§3a) and for **recovery** (`query-task`). Polling and env tuning: [docs/errors-and-polling.md](docs/errors-and-polling.md).
- **AK/SK loading**: environment variables `MT_AK` / `MT_SK` first; if unset, `scripts/.env` is read automatically (same as `SkillClient`).
- **Client init** pulls the latest algorithm config from the server; no manual `INVOKE` setup.
- **Bot token safety**: pass `TELEGRAM_BOT_TOKEN` and similar only via environment variables — never as CLI arguments.
- **On failure**: stdout JSON has `skill_status: "failed"` / `error`, **exit code ≠ 0** — explain to the user; check AK/SK, network, quotas; timeouts / SIGKILL / no final JSON: **[docs/errors-and-polling.md](docs/errors-and-polling.md)**. URL input errors may mention **HTTP 403** (expired signed URL) or **timeout** — see **`MT_AI_URL_*`** env vars above.
- **More docs**: [README.md](README.md), [docs/multi-platform.md](docs/multi-platform.md), [docs/im-attachments.md](docs/im-attachments.md), [docs/feishu-send-video.md](docs/feishu-send-video.md).
