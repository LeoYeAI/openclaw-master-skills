# Vidu API Reference

Base URL: configurable via **VIDU_BASE_URL**. **中国大陆** 使用 `https://service.vidu.cn`（默认）；**海外/非中国地区** 使用 `https://service.vidu.com`。See scripts/README.md.

All requests must include:

| Header        | Value                                                                                  |
| ------------- | -------------------------------------------------------------------------------------- |
| Authorization | `Token {token}`                                                                        |
| Content-Type  | `application/json`                                                                     |
| User-Agent    | `viduclawbot/1.0 (+{VIDU_BASE_URL})` (default VIDU_BASE_URL=`https://service.vidu.cn`) |

---

## 1. Create upload (image, for img2video)

**POST** `/tools/v1/files/uploads`

Create upload supports not only images but any file type (image, video, audio, etc.). The skill’s `upload_image.py` only wraps the image flow; other types can use the same API with appropriate metadata and Content-Type.

**Request body:**

```json
{
  "metadata": {
    "image-height": "<height_in_pixels>",
    "image-width": "<width_in_pixels>"
  },
  "scene": "vidu"
}
```

**Response:**

- `id` (number) — Upload ID. Use in finish and in task body as `ssupload:?id={id}`.
- `put_url` (string) — URL to PUT the image bytes to.
- `expires_at` (string) — Upload must complete before this time.

---

## 2. PUT image to put_url

**PUT** `{put_url}` (from CreateUpload response)

**Request headers:**

- `Content-Type`: `image/webp` (or the actual image type, e.g. `image/jpeg`, `image/png`)
- `x-amz-meta-image-height`: same numeric height as in CreateUpload metadata
- `x-amz-meta-image-width`: same numeric width as in CreateUpload metadata

**Request body:** Raw image bytes.

**Response:** Note the **ETag** response header value (include quotes if the server returns them; some clients strip quotes). Use it in FinishUpload.

---

## 3. Finish upload

**PUT** `/tools/v1/files/uploads/{id}/finish`

**Request body:**

```json
{
  "etag": "<ETag from PUT response>",
  "id": "<upload_id>"
}
```

`id` must match the upload ID from CreateUpload (path and body).

**Response:**

- `uri` (string) — Internal URI. For task body, use `ssupload:?id={id}` with the numeric upload id.

---

## 3b. Get presigned URL(s) for upload(s)

**POST** `/tools/v1/files/uploads/presigned-urls`

Get public download URL(s) for one or more uploaded resources identified by `ssupload:?id={id}`.

**Request body:**

```json
{
  "uris": ["ssupload:?id=<upload_id>", "ssupload:?id=<upload_id2>", ...]
}
```

**Response:**

- A map from each requested URI to a public (presigned) download URL, e.g. `presigned_urls` or `urls`: `{ "ssupload:?id=123": "https://..." }`.

**Important:** Returned presigned URLs are valid for **1 hour** only. After expiry, call this endpoint again to get a new URL.

---

## 3b. Pre-process material element (主体预处理)

**POST** `/vidu/v1/material/elements/pre-process`

Pre-process before creating a material element. **This step is required** — call it before every create-element request, whether or not the user provides a description. The response `recaption` (style, description) can be used to fill the subject description when not specially specified.

**Request body:**

| Field      | Type   | Required | Description                                                                                                                                                                      |
| ---------- | ------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| components | array  | yes      | 1–3 items. One with `type: "main"`, rest with `type: "auxiliary"`. Each: `content` = `ssupload:?id={upload_id}`, `src_img` = `ssupload:?id={upload_id}`, `content_type: "image"` |
| name       | string | yes      | Subject name (e.g. element_name)                                                                                                                                                 |
| type       | string | yes      | `"user"`                                                                                                                                                                         |

**Response:** `id`, `name`, `type`, `creator_id`, `recaption` (object with `style`, `description` — vidu-generated description), `modality`. Use `recaption.description` and optionally `recaption.style` in the create-element body when the user does not provide them.

---

## 3c. Create material element (创建主体)

**POST** `/vidu/v1/material/elements`

Create a material element (subject) with 1–3 images, a name, and a description. **Pre-process (3b) is required before every create** — call it first, then use the **pre-process response `id`** in this request body, along with the same `components` and either user-provided or pre-process `recaption`. Images must be uploaded first (sections 1–3); use the returned `ssupload:?id=...` in `components`.

**Request body:**

| Field      | Type          | Required | Description                                                                                                                                                                                   |
| ---------- | ------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id         | string/number | yes      | Element id from pre-process (3b) response; must be included when creating                                                                                                                     |
| name       | string        | yes      | Subject name                                                                                                                                                                                  |
| modality   | string        | yes      | `"image"`                                                                                                                                                                                     |
| type       | string        | yes      | `"user"`                                                                                                                                                                                      |
| components | array         | yes      | 1–3 items. One with `type: "main"` (core image), rest with `type: "auxiliary"`. Each: `content` = `ssupload:?id={upload_id}`, `src_img` = `ssupload:?id={upload_id}`, `content_type: "image"` |
| version    | string        | yes      | e.g. `"0"`                                                                                                                                                                                    |
| recaption  | object        | yes      | `description` (required), `style` (optional)                                                                                                                                                  |

**Response:** Element object including `id` and `version`; use these when submitting character2video tasks.

---

## 3d. Query personal material elements (查询主体)

**GET** `/vidu/v1/material/elements/personal`

**Query parameters:** `pager.page` (page number, 0-based), `pager.pagesz` (page size, e.g. 30), `pager.page_token` (optional), `keyword` (search term, URL-encoded), `modalities` (repeat for filter, e.g. `modalities=image`).

**Response:** `elements` (array; each has `id`, `name`, `version`, `components`, `recaption`, etc.), `next_page_token`. Use each element's `id` and `version` when submitting character2video.

---

## 4. Create task (submit video generation)

**POST** `/vidu/v1/tasks`

**Request body:** JSON with the following top-level fields.

| Field    | Type   | Required | Description                                                                                                                                                                      |
| -------- | ------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| type     | string | yes      | `"text2image"`, `"text2video"`, `"img2video"`, `"headtailimg2video"`, `"character2video"`, or `"reference2image"` (subject/material only in character2video and reference2image) |
| input    | object | yes      | See Input below                                                                                                                                                                  |
| settings | object | yes      | See Settings below. For img2video do not send aspect_ratio; for reference2image and character2video do not send transition.                                                      |

**Input:**

| Field       | Type    | Required | Description                                                                                                                                                                        |
| ----------- | ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| prompts     | array   | yes      | List of prompt objects (text, image, and/or material). Max 20. For character2video and reference2image: **text required**; image + material combined at most 7 (图+主体合计最多7). |
| editor_mode | string  | no       | `"normal"` typical                                                                                                                                                                 |
| enhance     | boolean | yes      | Default true (recaption for text)                                                                                                                                                  |

**Prompt object (text):**

```json
{ "type": "text", "content": "your prompt text" }
```

**Prompt object (image):**

- `type`: `"image"`
- `content`: `"ssupload:?id={upload_id}"` (from finish step)
- `src_imgs`: optional array of `ssupload:?id=...` (source image refs)
- `selected_region`: optional `{ "top_left": {"x", "y"}, "bottom_right": {"x", "y"} }`

**Prompt object (material, for character2video and reference2image only):**

- `type`: `"material"`
- `name`: subject name (e.g. display name)
- `material`: `{ "id": "<element_id>", "version": "<element_version>" }` — from create element or query personal elements response.

**Settings:** See references/parameters.md for full list. Common: duration (0 for text2image/reference2image), resolution (1080p, 2K, 4K for text2image/reference2image), aspect_ratio, model_version, transition, codec, sample_count, schedule_mode, use_trial, movement_amplitude.

**Response:**

- `id` (string or number) — Task ID. Use for state and get-task.

---

## 5. Get task state (SSE)

**GET** `/vidu/v1/tasks/state?id={task_id}`

**Example URL:** `https://service.vidu.cn/vidu/v1/tasks/state?id=3202402178822691`

**Headers:** Same as above (Authorization, Content-Type, User-Agent). Accept SSE (e.g. `Accept: text/event-stream`).

**Response:** Server-Sent Events stream. **When using this endpoint, return the SSE output directly to the model — do not wait for a terminal state.**

Each event is a line of the form `data: <JSON>`. Example:

```
data: {"state":"processing", "estimated_time_left":0, "err_code":"", "queue_wait_time":{"min":[0], "max":[0]}}
```

**Fields:**

- `state` (string): e.g. `created`, `queueing`, `preparation`, `scheduling`, `processing`, `success`, `failed`, `canceled`
- `estimated_time_left` (number, optional)
- `err_code` (string, optional, when state is failed)
- `queue_wait_time` (object, optional): **Predicted queue wait time (排队预测时间)**. Unit: **minutes**. `min` and `max` are arrays of numbers (minutes).

---

## 6. Get task (result)

**GET** `/vidu/v1/tasks/{task_id}`

**Response:** JSON task object. Relevant fields:

- `state`: `success` | `failed` | ...
- `creations`: array of creation objects when state is success
  - Each creation: `nomark_uri` (watermark-free video/image URL), `uri`, `download_uri`, `cover_uri`, `duration`, `video.resolution`, etc.
- `err_code`, `err_msg` (when state is failed)

Use **nomark_uri** for the final video link to the user.
