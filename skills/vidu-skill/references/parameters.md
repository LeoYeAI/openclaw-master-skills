# Vidu Task Parameters Reference

## 任务支持列表 (Supported task list)

模型版本: **Q3** → `model_version: "3.2"`；**Q2** → `model_version: "3.1"`。

| 任务类型     | type              | 输入                                           | 模型 | 时长(秒) | 宽高比                    | transition                     | 清晰度              |
| ------------ | ----------------- | ---------------------------------------------- | ---- | -------- | ------------------------- | ------------------------------ | ------------------- |
| 文生图       | text2image        | 一段文字                                       | Q2   | 0        | 4:3, 3:4, 1:1, 9:16, 16:9 | 不传                           | 1080p, 2K(默认), 4K |
| 文生视频     | text2video        | 一段文字                                       | Q3   | 1–16     | 16:9, 9:16, 1:1, 4:3, 3:4 | pro(电影大片), speed(闪电出片) | 1080p               |
| 文生视频     | text2video        | 一段文字                                       | Q2   | 2–8      | 16:9, 9:16, 1:1, 4:3, 3:4 | 不传                           | 1080p               |
| 图生视频     | img2video         | **一张图 + 一段文字**                          | Q3   | 1–16     | 依据输入图，**不传**      | pro, speed                     | 1080p               |
| 图生视频     | img2video         | 一张图 + 一段文字                              | Q2   | 2–8      | 依据输入图，不传          | pro, speed                     | 1080p               |
| 首尾帧生视频 | headtailimg2video | **两张图 + 一段文字**                          | Q3   | 1–16     | —                         | pro, speed                     | 1080p               |
| 首尾帧生视频 | headtailimg2video | 两张图 + 一段文字                              | Q2   | 2–8      | —                         | pro, speed                     | 1080p               |
| 参考生图     | reference2image   | **图+主体+文字（文字必填；图+主体合计最多7）** | Q2   | 0        | 4:3, 3:4, 1:1, 9:16, 16:9 | **不传**                       | 1080p, 2K, 4K       |
| 参考生视频   | character2video   | **图+主体+文字（文字必填；图+主体合计最多7）** | Q3   | 1–16     | 16:9, 9:16, 1:1, 4:3, 3:4 | **不传**                       | 1080p               |
| 参考生视频   | character2video   | **图+主体+文字（文字必填；图+主体合计最多7）** | Q2   | 2–8      | 16:9, 9:16, 1:1, 4:3, 3:4 | **不传**                       | 1080p               |

- **文生图**: 只传文字。需要设置 duration 为 0，支持分辨率 1080p/2K/4K (默认 2K)。
- **文生视频**: 只传文字。Q2 时不要传 transition。
- **图生视频**: 仅 1 张图片 + 1 段文字；宽高比由输入图决定，**不要传 aspect_ratio**。
- **首尾帧生视频**: 固定 2 张图（首帧、尾帧）+ 1 段文字。
- **参考生图**: 图+主体+文字（**文字必填**；图+主体数量合计至少1，最多7）；仅 Q2，需要设置 `duration` 为 0，要求传入 `resolution` 与 `aspect_ratio`，**不要传 transition**。
- **参考生视频**: 图+主体+文字（**文字必填**；图+主体合计最多 7，至少一种）；Q3 模型时长 1-16，Q2 模型时长 2-8，**不要传 transition**。

---

## Task type (API)

| Value             | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| text2image        | 文生图：prompts 仅文字                                        |
| text2video        | 文生视频：prompts 仅文字                                      |
| img2video         | 图生视频：1 张图 + 1 段文字                                   |
| headtailimg2video | 首尾帧生视频：2 张图 + 1 段文字                               |
| character2video   | 参考生视频：图+主体+文字（文字必填；图+主体合计最多7）       |
| reference2image   | 参考生图：图+主体+文字（文字必填；图+主体合计最多7，仅 Q2）   |

---

## Input

### prompts (array)

- **Text prompt**: `{"type": "text", "content": "<string>"}`. Max length 4096.
- **Image prompt**: `{"type": "image", "content": "ssupload:?id=<upload_id>", "src_imgs": [...], "selected_region": {...}}`. Optional: `src_imgs`, `selected_region`.

Order: for headtailimg2video use [text, image1, image2] (首帧、尾帧). For character2video and reference2image: **text prompt required**; image + material combined at most 7 (图+主体合计最多7).

### input.editor_mode

| Value  | Description |
| ------ | ----------- |
| normal | Default     |

### input.enhance

- `true` (default): recaption text prompts.
- `false`: use prompts as-is.

---

## Settings (by task type)

| Field         | text2image                | reference2image           | text2video                | img2video         | headtailimg2video | character2video           |
| ------------- | ------------------------- | ------------------------- | ------------------------- | ----------------- | ----------------- | ------------------------- |
| duration      | 0                         | 0                         | Q3: 1–16; Q2: 2–8         | Q3: 1–16; Q2: 2–8 | Q3: 1–16; Q2: 2–8 | Q3: 1–16; Q2: 2–8         |
| aspect_ratio  | 4:3, 3:4, 1:1, 9:16, 16:9 | 4:3, 3:4, 1:1, 9:16, 16:9 | 16:9, 9:16, 1:1, 4:3, 3:4 | **不传**          | —                 | 16:9, 9:16, 1:1, 4:3, 3:4 |
| transition    | **不传**                  | **不传**                  | Q3: pro, speed; Q2: 不传  | pro, speed        | pro, speed        | **不传**                  |
| resolution    | 1080p, 2K, 4K             | 1080p, 2K, 4K             | 1080p                     | 1080p             | 1080p             | 1080p                     |
| model_version | 3.1                       | 3.1 (Q2 only)             | 3.2 (Q3) or 3.1 (Q2)      | 3.2 or 3.1        | 3.2 or 3.1        | 3.2 (Q3) or 3.1 (Q2)      |

- **transition "pro"**: 电影大片.
- **transition "speed"**: 闪电出片.

---

## File upload metadata

For **CreateUpload** (images):

- `metadata.image-height`: integer string (pixels).
- `metadata.image-width`: integer string (pixels).
- `scene`: `"vidu"`.

Same dimensions must be sent as `x-amz-meta-image-height` and `x-amz-meta-image-width` on the PUT to put_url.
