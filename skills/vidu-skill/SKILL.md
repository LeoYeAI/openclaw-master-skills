---
name: vidu-skills
description: Generate video and images by calling the official Vidu API with curl. Use when the user wants text-to-image (文生图), text-to-video (文生视频), image-to-video (图生视频), head-tail-image-to-video (首尾帧生视频), reference-to-image (参考生图), reference-to-video (参考生视频), Create References (创建参考资料), or to submit or check Vidu tasks. Requires VIDU_TOKEN and optional VIDU_BASE_URL.
compatibility: Requires ability to run curl (or equivalent HTTP client). Set VIDU_TOKEN in the environment; VIDU_BASE_URL optional (default https://service.vidu.cn). See references/api_reference.md for full API.
version: 1.0.4
url: https://www.vidu.cn/
secrets:
  - VIDU_TOKEN
dependencies:
  - curl
---

# Vidu Video and Image Generation Skill (Vidu 音视频/图像生成技能)

Generate AI videos and images with Vidu (生数) via direct API calls — text-to-image, text-to-video, image-to-video, start-end frame, reference-based generation, and material elements, up to 1080p/2K/4K. Use curl with VIDU_TOKEN.

## Execution model: use curl (direct API)

**All execution is done by calling the official Vidu API** with curl (or any HTTP client). Base URL: **$VIDU_BASE_URL** (default `https://service.vidu.cn` for mainland China; `https://service.vidu.com` for overseas).

**Required headers for all requests:**

| Header        | Value                               |
| ------------- | ----------------------------------- |
| Authorization | `Token $VIDU_TOKEN`                 |
| Content-Type  | `application/json`                  |
| User-Agent    | `viduclawbot/1.0 (+$VIDU_BASE_URL)` |

**Main endpoints:**

- **Create upload**: POST `$VIDU_BASE_URL/tools/v1/files/uploads` → get `put_url`, `id`
- **PUT image**: PUT raw image bytes to `put_url` → get ETag
- **Finish upload**: PUT `$VIDU_BASE_URL/tools/v1/files/uploads/{id}/finish` → get `ssupload:?id={id}`
- **Submit task**: POST `$VIDU_BASE_URL/vidu/v1/tasks` → get `task_id` (response `id`)
- **Get task result**: GET `$VIDU_BASE_URL/vidu/v1/tasks/{task_id}` → get `state`, `creations[].nomark_uri`
- **Task state (SSE)**: GET `$VIDU_BASE_URL/vidu/v1/tasks/state?id={task_id}` with `Accept: text/event-stream` — return SSE stream to the user; do not wait for terminal state. Events include `state`, `estimated_time_left`, `err_code`, **queue_wait_time** (排队预测时间, unit: minutes).
- **Pre-process reference**: POST `$VIDU_BASE_URL/vidu/v1/material/elements/pre-process`
- **Create reference**: POST `$VIDU_BASE_URL/vidu/v1/material/elements`
- **List elements**: GET `$VIDU_BASE_URL/vidu/v1/material/elements/personal`

---

## Key Capabilities

- **text-to-image (文生图)** — POST `/vidu/v1/tasks` with `type: "text2image"`, `input.prompts` (text only), `settings`. Resolution 1080p, 2K, 4K.
- **text-to-video (文生视频)** — POST `/vidu/v1/tasks` with `type: "text2video"`, `input.prompts` (text only), `settings`.
- **image-to-video (图生视频)** — Upload one image (Create upload → PUT → Finish) to get `ssupload:?id=...`; then POST `/vidu/v1/tasks` with `type: "img2video"`, prompts (text + image).
- **head-tail-image-to-video (首尾帧生视频)** — Upload two images; POST `/vidu/v1/tasks` with `type: "headtailimg2video"`, prompts (text + image1 + image2).
- **reference-to-image (参考生图)** — Image(s) + reference(s) + text (text required; image + reference combined at most 7). POST `/vidu/v1/tasks` with `type: "reference2image"`; Q2 only, do not send `transition`, `duration` is 0.
- **reference-to-video (参考生视频)** — Image(s) + reference(s) + text (text required; image + reference combined at most 7). POST `/vidu/v1/tasks` with `type: "character2video"`; Q3 or Q2, do not send `transition`.
- **Create References (创建主体)** — POST pre-process → POST material/elements (images must be uploaded first). Query list: GET `/vidu/v1/material/elements/personal`.
- **Query task (查询任务)** — GET `/vidu/v1/tasks/{task_id}` for result; or GET `/vidu/v1/tasks/state?id={task_id}` for SSE stream.

---

## Setup

1. Obtain a VIDU token (e.g. from the official Vidu console).
2. Set environment variables:
   - `export VIDU_TOKEN="your-token"` (required / 必填)
   - `export VIDU_BASE_URL=https://service.vidu.cn` (mainland China / 国内, default / 默认) or `https://service.vidu.com` (overseas / 海外)
3. **Dependency**: curl or any HTTP client that can send JSON and binary PUT. No Python or scripts required for execution.

---

## Data usage and privacy note

**IMPORTANT**: This skill sends user-provided data to Vidu’s servers:

- Text prompts → Vidu API
- Image bytes (uploaded files) → Vidu API servers (service.vidu.cn or service.vidu.com)
- Task parameters (settings, model version, etc.)

Before using this skill, confirm that sending your content to Vidu is acceptable for your privacy and intellectual property requirements. Data handling follows Vidu’s official policy.

**Security recommendations**:

- Create a token with limited scope if possible
- Avoid using production/privileged tokens for initial testing
- Review Vidu’s terms of service and privacy policy

**Vidu Terms & Privacy**:

- Overseas: https://www.vidu.com/terms
- Mainland China: https://www.vidu.cn/terms

---

## Overview

Vidu media generation is **asynchronous**: submit a task → get **task_id** → use task_id to **query** status/result (GET `/vidu/v1/tasks/{task_id}` or SSE `/vidu/v1/tasks/state?id=`) when needed.

- **text-to-image (文生图)**: Text only. Duration 0, model_version 3.1. aspect_ratio optional. resolution 1080p, 2K, 4K (default 2K).
- **text-to-video (文生视频)**: Text only. Q3 duration 1–16, aspect ratios 16:9/9:16/1:1/4:3/3:4, transition pro/speed; Q2 duration 2–8, do not send transition.
- **image-to-video (图生视频)**: **One image + one text**. Aspect ratio from input image (do not send aspect_ratio). Q3 duration 1–16, Q2 duration 2–8, transition pro/speed.
- **head-tail-image-to-video (首尾帧生视频)**: **Two images (start frame, end frame) + one text**. Q3 1–16s, Q2 2–8s, transition pro/speed.
- **reference-to-image (参考生图)**: **Image + reference + text** (combinations); **text required**. **Image + reference at most 7**, at least one. Q2 only, duration 0, reference via `type: "material"`.
- **reference-to-video (参考生视频)**: **Image + reference + text** (combinations); **text required**. **Image + reference at most 7**, at least one. Q3 duration 1–16, Q2 duration 2–8. Do **not** send transition. References in prompts via `type: "material"`, `material.id`, `material.version`.
- **Create References (创建主体)**: Upload 1–3 images, name and optional description; **must** call POST `/vidu/v1/material/elements/pre-process` first, then POST `/vidu/v1/material/elements`. Use pre-process `recaption` when description is omitted. Response includes element `id` and `version` for reference-to-video.
- **Search References (查询主体)**: GET `/vidu/v1/material/elements/personal` with `pager.page`, `pager.pagesz`, `keyword`, `modalities`; returns `elements[].id`, `version`.

See **Supported task list** below and **references/parameters.md**.

---

## Supported Task List

When building the POST `/vidu/v1/tasks` body, ensure the user’s request matches one of the supported task types and constraints below. All parameters are passed in the request **body** (type, input.prompts, settings). **references/parameters.md** has the same list for quick lookup.

**Model version**

- **Q3** → `model_version: "3.2"`
- **Q2** → `model_version: "3.1"`

| Task Type                               | type (API)        | Input                               | Model | Duration | Aspect Ratio              | Transition | Resolution  |
| --------------------------------------- | ----------------- | ----------------------------------- | ----- | -------- | ------------------------- | ---------- | ----------- |
| text-to-image (文生图)                  | text2image        | text only                           | Q2    | 0        | 4:3, 3:4, 1:1, 9:16, 16:9 | —          | 1080p/2K/4K |
| text-to-video (文生视频)                | text2video        | text only                           | Q3    | 1–16s    | 16:9, 9:16, 1:1, 4:3, 3:4 | pro, speed | 1080p       |
| text-to-video (文生视频)                | text2video        | text only                           | Q2    | 2–8s     | 16:9, 9:16, 1:1, 4:3, 3:4 | —          | 1080p       |
| image-to-video (图生视频)               | img2video         | 1 image + text                      | Q3    | 1–16s    | from image                | pro, speed | 1080p       |
| image-to-video (图生视频)               | img2video         | 1 image + text                      | Q2    | 2–8s     | from image                | pro, speed | 1080p       |
| head-tail-image-to-video (首尾帧生视频) | headtailimg2video | 2 images + text                     | Q3    | 1–16s    | —                         | pro, speed | 1080p       |
| head-tail-image-to-video (首尾帧生视频) | headtailimg2video | 2 images + text                     | Q2    | 2–8s     | —                         | pro, speed | 1080p       |
| reference-to-image (参考生图)           | reference2image   | image + reference + text (required) | Q2    | 0        | 4:3, 3:4, 1:1, 9:16, 16:9 | —          | 1080p/2K/4K |
| reference-to-video (参考生视频)         | character2video   | image + reference + text (required) | Q3    | 1–16s    | 16:9, 9:16, 1:1, 4:3, 3:4 | —          | 1080p       |
| reference-to-video (参考生视频)         | character2video   | image + reference + text (required) | Q2    | 2–8s     | 16:9, 9:16, 1:1, 4:3, 3:4 | —          | 1080p       |

- **text-to-image (文生图)**: Text only; set model_version to 3.1, duration to 0, resolution defaults to 2K (1080p/2K/4K).
- **text-to-video (文生视频)**: Text only; do not send transition for Q2.
- **image-to-video (图生视频)**: Exactly **1 image + 1 text**; do not send `aspect_ratio` in settings.
- **head-tail-image-to-video (首尾帧生视频)**: Exactly **2 images (start, end) + 1 text**; order is start frame then end frame.
- **reference-to-image (参考生图)**: **Image + reference + text**; Q2 only, duration 0, resolution defaults to 2K, do not send transition.
- **reference-to-video (参考生视频)**: **Image + reference + text** (text required; image + reference combined at most 7); Q3 or Q2; **不要传 transition**.

---

## Create References

Create a material element for use in character2video or reference2image: upload 1–3 images, name and description; API returns element `id` and `version`. **Flow**: **First** call **POST** `$VIDU_BASE_URL/vidu/v1/material/elements/pre-process` (required even if user provides description; body: `components`, `name`, `type: "user"`). Response includes `recaption` (style, description). Then call **POST** `$VIDU_BASE_URL/vidu/v1/material/elements` with the pre-process response `id`, same `components`, and `recaption` (or user description).

**Pre-process**: POST `$VIDU_BASE_URL/vidu/v1/material/elements/pre-process`. See **references/api_reference.md** §3b.

**Create element**: POST `$VIDU_BASE_URL/vidu/v1/material/elements`. Body: `id` (from pre-process), `name`, `modality: "image"`, `type: "user"`, `components` (1–3 items: **content** = `ssupload:?id={id}`, **src_img** = `ssupload:?id={id}`, `content_type: "image"`), `version: "0"`, `recaption`. See **references/api_reference.md** §3c.

**Prerequisite**: Each image must be uploaded first (Create upload → PUT to put_url → Finish) to get `ssupload:?id={id}`; use these in `components`.

---

## Search References

- **URL**: GET `$VIDU_BASE_URL/vidu/v1/material/elements/personal`
- **Query**: `pager.page`, `pager.pagesz`, `pager.page_token` (optional), `keyword` (URL-encoded), `modalities` (e.g. `modalities=image`).
- **Response**: `elements[]` with `id`, `name`, `version`, etc.; use `id` and `version` in reference-to-video or reference-to-image prompts.

---

## Using References in reference-to-video and reference-to-image

References are used in **reference-to-video** and **reference-to-image**. When submitting POST `/vidu/v1/tasks`: `type: "character2video"` or `"reference2image"`; `input.prompts` must include **(1) text prompt (required)**; (2) optional image prompt (`type: "image"`); (3) optional reference prompt (`type: "material"`, `name`, `material: { "id", "version" }`). Combine image + reference + text; text required; **image + reference at most 7**, at least one.

**Example body**:

```json
{
  "input": {
    "prompts": [
      { "type": "text", "content": "[@aliya]" },
      {
        "type": "material",
        "name": "aliya",
        "material": { "id": "3073530415201165", "version": "1765430214" }
      }
    ],
    "editor_mode": "normal",
    "enhance": true
  },
  "type": "character2video",
  "settings": {
    "duration": 5,
    "resolution": "1080p",
    "movement_amplitude": "auto",
    "aspect_ratio": "16:9",
    "sample_count": 1,
    "schedule_mode": "normal",
    "codec": "h265",
    "model_version": "3.1",
    "use_trial": false
  }
}
```

---

## Bundled resources

- **references/api_reference.md** — Full API contracts (endpoints, request/response). Use for building curl requests.
- **references/parameters.md** — Task types and parameter constraints.
- **references/errors_and_retry.md** — Error handling and retry guidance.

---

## Workflow: Submit → Query → Get media URL

**Summary**: Submit (POST `/vidu/v1/tasks` → get `task_id`) → Query (GET `/vidu/v1/tasks/{task_id}` or SSE `/vidu/v1/tasks/state?id=`) → Get media from `creations[].nomark_uri`.

### 1. text-to-video (文生视频) — Submit (curl example)

```bash
curl -s -X POST "$VIDU_BASE_URL/vidu/v1/tasks" \
  -H "Authorization: Token $VIDU_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: viduclawbot/1.0 (+$VIDU_BASE_URL)" \
  -d '{
    "type": "text2video",
    "input": {
      "prompts": [{"type": "text", "content": "A cat walks in the snow at sunset"}],
      "editor_mode": "normal",
      "enhance": true
    },
    "settings": {
      "duration": 5,
      "resolution": "1080p",
      "aspect_ratio": "16:9",
      "model_version": "3.2",
      "transition": "pro",
      "sample_count": 1,
      "schedule_mode": "normal",
      "codec": "h265",
      "use_trial": false
    }
  }'
```

Response contains `id` (task_id). Use it to query.

### 2. Query Task Result (curl example)

```bash
curl -s "$VIDU_BASE_URL/vidu/v1/tasks/$TASK_ID" \
  -H "Authorization: Token $VIDU_TOKEN" \
  -H "User-Agent: viduclawbot/1.0 (+$VIDU_BASE_URL)"
```

- `state`: `success` | `failed` | `processing` | ...
- On **success**: use `creations[].nomark_uri` as the media URL(s).
- On **failed**: use `err_code`, `err_msg` to report to the user.

### 3. Task Status SSE (任务状态 SSE) (optional, stream to user)

```bash
curl -N -s "$VIDU_BASE_URL/vidu/v1/tasks/state?id=$TASK_ID" \
  -H "Authorization: Token $VIDU_TOKEN" \
  -H "Accept: text/event-stream" \
  -H "User-Agent: viduclawbot/1.0 (+$VIDU_BASE_URL)"
```

Return the SSE output directly to the user; do not wait for a terminal state. **Warning for Agents**: SSE streams continuous events which may produce large output. Ensure you either read a limited number of events or avoid autonomous streaming loops.

### 4. Image Upload (图片上传) (image-to-video / head-tail-image-to-video / Create References)

**Step 1 — Create upload:**

```bash
curl -s -X POST "$VIDU_BASE_URL/tools/v1/files/uploads" \
  -H "Authorization: Token $VIDU_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: viduclawbot/1.0 (+$VIDU_BASE_URL)" \
  -d '{"metadata":{"image-width":"1920","image-height":"1080"},"scene":"vidu"}'
```

From response take `id` and `put_url`.

**Step 2 — PUT image bytes to put_url:**

```bash
curl -s -X PUT "$PUT_URL" \
  -H "Content-Type: image/jpeg" \
  -H "x-amz-meta-image-width: 1920" \
  -H "x-amz-meta-image-height: 1080" \
  --data-binary @/path/to/image.jpg
```

Save the **ETag** from the response (use quotes if the server returns them).

**Step 3 — Finish upload:**

```bash
curl -s -X PUT "$VIDU_BASE_URL/tools/v1/files/uploads/$UPLOAD_ID/finish" \
  -H "Authorization: Token $VIDU_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: viduclawbot/1.0 (+$VIDU_BASE_URL)" \
  -d "{\"etag\":\"$ETAG\",\"id\":\"$UPLOAD_ID\"}"
```

Use `ssupload:?id=$UPLOAD_ID` in task prompts or in element `components`.

### 5. Create References (创建主体) (curl flow)

After uploading 1–3 images to get `ssupload:?id=...`:

**Pre-process** — POST `$VIDU_BASE_URL/vidu/v1/material/elements/pre-process` with body `components` (array: each item has **content** = `ssupload:?id={id}`, **src_img** = `ssupload:?id={id}`, `content_type: "image"`), `name`, `type: "user"`. See api_reference §3b.

**Create** — POST `$VIDU_BASE_URL/vidu/v1/material/elements` with body including `id` (from pre-process response), `name`, `modality: "image"`, `type: "user"`, `components`, `version: "0"`, `recaption` (from pre-process or user). See api_reference §3c.

---

## Implementation Guide

1. **Determine task type**: text-to-image, text-to-video, image-to-video, head-tail-image-to-video, reference-to-image, reference-to-video, or Create References.
2. **Choose parameters**: From Supported Task List select `model_version` (Q2/Q3), `duration`, `aspect_ratio`, `transition` (omit for image-to-video aspect_ratio, reference-to-video transition).
3. **Prepare inputs**: For image-to-video/head-tail-image-to-video/reference-to-video or Create References, upload image(s) via Create upload → PUT → Finish to get `ssupload:?id=...`. For reference-to-video with references, ensure elements exist (create via pre-process + create reference if needed).
4. **Submit**: curl POST `$VIDU_BASE_URL/vidu/v1/tasks` with JSON body (type, input.prompts, settings). Capture `id` as task_id.
5. **Query**: curl GET `$VIDU_BASE_URL/vidu/v1/tasks/{task_id}` (or use SSE) until state is success/failed; on success return `creations[].nomark_uri`; on failure return err_code/err_msg.

---

## Prompt Tips

- **text-to-image (文生图)**: Describe the subject, style, lighting, and composition explicitly.
- **text-to-video (文生视频)**: Include scene and action; you can add camera direction (e.g. “镜头缓慢左移”, “特写跟拍”).
- **image-to-video (图生视频)**: Describe what motion or change happens in the scene.
- **head-tail-image-to-video (首尾帧)**: Similar start/end frames give smooth transition; very different frames can be used for morphing effects.
- **reference-to-video / reference-to-image**: Create the reference first; in the text prompt use references like `[@reference_name]`; ensure text is always present.

---

## Output to the user

- **After submit**: Return the **task_id** (response `id`); tell the user the task is in progress and they can query status/result with that task_id (e.g. GET `/vidu/v1/tasks/{task_id}` or SSE state endpoint).
- **After query**: If state is success, return the **nomark_uri** link(s); if failed, report **err_code** and **err_msg**.
- **On failure**: Clearly state that the task failed and, when available, the reason (err_code / err_msg from the API or references).

---

## Fallback (no curl)

If the environment **cannot** run curl (or equivalent HTTP client), execution as described above is not possible. Tell the user that this skill requires curl (or an HTTP client) with VIDU_TOKEN and point them to **references/api_reference.md** for manual API usage.
