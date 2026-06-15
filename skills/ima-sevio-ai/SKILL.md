---
name: IMA Sevio AI Generation
version: 1.1.0
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, video generation, text-to-video, image-to-video, IMA, Ima Sevio, Sevio, IMA Video Pro, IMA Video Pro Fast
argument-hint: "[text prompt or media URL]"
description: >
  IMA model generation with exactly two Sevio models: Ima Sevio 1.0 and Ima Sevio 1.0-Fast.
  Supports text-to-video, image-to-video, first-last-frame, and reference-image workflows.
  Keeps the same API flow, reflection retry mechanism, and interface contract as ima-video-ai.
  Requires IMA API key.
requires:
  env:
    - IMA_API_KEY
  primaryCredential: IMA_API_KEY
  credentialNote: >
    IMA_API_KEY is sent to api.imastudio.com for product/task APIs and to
    imapi.liveme.com only when local media must be uploaded before task creation.
persistence:
  readWrite:
    - ~/.openclaw/memory/ima_prefs.json
    - ~/.openclaw/logs/ima_skills/
  retention: Logs are auto-cleaned after 7 days; preferences remain until user deletes them.
instructionScope:
  crossSkillReadOptional:
    - ~/.openclaw/skills/ima-knowledge-ai/references/*
---

# IMA Sevio AI Creation

## 🎯 Skill Capabilities

本技能是 **Ima Sevio 视频生成专用入口**。对外不是“模型 ID 映射器”，而是两档清晰的视频生成能力：

- **Ima Sevio 1.0（质量优先）**
  - 定位：正式出片、质感优先、镜头语言要求高的任务。
  - 适合：广告镜头、角色叙事、风格化短片、需要更高一致性的镜头段落。
- **Ima Sevio 1.0-Fast（速度优先）**
  - 定位：快速打样、批量试风格、创意迭代。
  - 适合：提案阶段 A/B 版本、镜头预演、低延迟验证。

### Ability Positioning (Top-Tier Video Model Class)

在公开视频能力维度上，Sevio 系列可按以下能力理解（用于用户预期管理）：

- **时序与主体一致性**：在连续动作和主体保持上具备高稳定性表现。
- **镜头语言控制**：支持对推拉摇移、节奏和运动感的描述驱动。
- **多模态条件理解**：可结合文本与参考素材（image/reference/first-last frame）进行生成。
- **高质量输出取向**：面向高分辨率、高观感视频产出（以当次产品规则为准）。

### Workflow Coverage

- `text_to_video`：文本直接生成视频。
- `image_to_video`：以首帧图驱动动态生成。
- `first_last_frame_to_video`：以首尾帧约束过渡与收束。
- `reference_image_to_video`：以参考图约束风格/主体特征。

### Input & Reliability

- `prompt` 负责主体、动作、镜头、风格与节奏描述。
- `--input-images` 支持单个/多个输入，统一以字符串数组语义处理。
- 本地文件先上传再生成，远程 HTTP(S) 链接直接使用。
- 运行时动态匹配产品规则（credit_rules/form_config）并内置自动重试与降级策略。
- 轮询上限 40 分钟；若无明确报错但超时，会提示前往创作记录页查看。

### Output

- 返回可直接分发的视频结果 URL（含封面信息），可直接用于消息卡片或播放器。

---

## ✨ Expected Outcomes & Boundaries (Outcomes, Timing, Scope Limits)

### Expected Outcomes

- **质量预期（Sevio 1.0）**：在画面稳定、主体一致、镜头控制上，目标体验达到行业同级高水平能力带。
- **速度预期（Sevio 1.0-Fast）**：在保持可用画质与控制力的前提下，提供更快周转，适合多轮迭代。
- **模式预期**：图生/参考/首尾帧模式，相比纯文生视频更有利于主体连续性与风格一致性。

### Timing Expectations

| 模型（用户展示） | 典型耗时 |
|---|---:|
| Ima Sevio 1.0（IMA Video Pro） | 120~300s |
| Ima Sevio 1.0-Fast（IMA Video Pro Fast） | 60~120s |

轮询超时上限：`40 分钟（2400s）`。

### Capability Boundaries (Avoid Misunderstanding)

- 本技能只做 **视频生成链路**，不负责后期剪辑、自动分镜编排、成片包装。
- 结果质量受提示词、参考素材质量、当次产品规则与积分策略影响，不保证每次一致。
- 仅支持本技能白名单模型；其他模型名会被拦截或映射后执行。

---

## ⚠️ 内部调用：模型 ID 参考（不对用户展示）

**User-facing rule:** In user messages, always use **Ima Sevio 1.0 / Ima Sevio 1.0-Fast** names.  
Do not expose raw `model_id` unless the user explicitly asks for technical details.

**CRITICAL:** When calling the script, you MUST use exact `model_id` values. For `ima-sevio-ai`, only these two are allowed:

| Friendly Name | model_id | Notes |
|---|---|---|
| IMA Pro | `ima-pro` | Default quality model |
| IMA Pro Fast | `ima-pro-fast` | Faster / lower-latency model |
| Ima Sevio 1.0 | `ima-pro` | Display-name alias |
| Ima Sevio 1.0-Fast | `ima-pro-fast` | Display-name alias |

### 模型中文介绍（可公开口径）

**IMA Video Pro（Ima Sevio 1.0）**

面向高质量视频创作的主力模型。  
在时序一致性、镜头语言控制、多模态条件理解等核心维度上，能力定位达到行业同级高水平视频模型能力。  
适合对质感、稳定性和镜头可控性要求更高的生产任务。

**核心优势（公开可查）**
- 高帧率时序一致性
- 精准镜头语言控制
- 图像 / 音频 / 文本多模态输入
- 2K 级输出画质

**IMA Video Pro Fast（Ima Sevio 1.0-Fast）**

面向高频迭代场景的加速模型版本。  
在保持主体可辨识与镜头可控的基础上，优先缩短生成时延，适合提案打样、快速试风格和实时创作流程。

**Rules:**
- Do NOT infer model IDs from other IMA skills.
- Do NOT use any model outside this allowlist.
- If user asks for other models, map to one of the two allowed models with explanation.
- Alias input `Ima Sevio 1.0` is auto-mapped to `ima-pro`.
- Alias input `Ima Sevio 1.0-Fast` is auto-mapped to `ima-pro-fast`.

---

## 📚 Optional Knowledge Enhancement (ima-knowledge-ai)

This skill is fully runnable as a standalone package.  
If `ima-knowledge-ai` is installed, the agent may read its references for better mode selection and consistency guidance.

Recommended optional reads:

1. **Understand video modes** — Read `ima-knowledge-ai/references/video-modes.md`:
- `image_to_video` = input image becomes frame 1
- `reference_image_to_video` = input image is visual reference, not frame 1

2. **Check visual consistency needs** — Read `ima-knowledge-ai/references/visual-consistency.md` if user mentions:
- "系列"、"分镜"、"同一个"、"角色"、"续"、"多个镜头"
- multi-shot continuity, character consistency, repeated subject

3. **Check workflow/model/parameters** — Read related references when unsure about mode or parameters.

**Why this matters:**
- AI generation is independent by default.
- Text-only generation cannot preserve visual continuity reliably.
- Wrong mode choice causes wrong results.

---

## 📥 User Input Parsing (Model & Parameter Recognition)

### 1) User phrasing → `task_type`

| User intent | task_type |
|---|---|
| Only text | `text_to_video` |
| One image as first frame | `image_to_video` |
| One image as reference | `reference_image_to_video` |
| Two images as first+last frame | `first_last_frame_to_video` |

### 2) User phrasing → `model_id`

Normalize case-insensitively and ignore spaces:

| User says | model_id |
|---|---|
| `ima-pro`, `pro`, `专业版`, `高质量` | `ima-pro` |
| `ima-pro-fast`, `fast`, `极速`, `快速` | `ima-pro-fast` |
| `Ima Sevio 1.0` | `ima-pro` |
| `Ima Sevio 1.0-Fast` | `ima-pro-fast` |
| "默认" / "推荐" / "自动" | `ima-pro` |

If user explicitly asks "faster", prefer `ima-pro-fast`.
If user explicitly asks "best quality", prefer `ima-pro`.

### 3) User phrasing → duration / resolution / aspect_ratio

| User says | Parameter | Normalized value |
|---|---|---|
| 5秒 / 5s | duration | 5 |
| 10秒 / 10s | duration | 10 |
| 15秒 / 15s | duration | 15 |
| 横屏 / 16:9 | aspect_ratio | 16:9 |
| 竖屏 / 9:16 | aspect_ratio | 9:16 |
| 方形 / 1:1 | aspect_ratio | 1:1 |
| 720P / 720p | resolution | 720P |
| 1080P / 1080p | resolution | 1080P |
| 4K / 4k | resolution | 4K (only if model/rule supports) |

If unspecified, use product `form_config` defaults.

---

## ⚙️ How This Skill Works

This skill uses bundled script `scripts/ima_video_create.py` and keeps original API workflow:
- product list query
- parameter resolution
- create task
- poll task detail
- return video URL

### 🌐 Network Endpoints Used

| Domain | Purpose | What's Sent |
|---|---|---|
| `api.imastudio.com` | task create + status polling | prompt, model params, task IDs, API key |
| `imapi.liveme.com` | image upload (when image input exists) | image bytes, API key |

**Privacy notes:**
- API key is sent to both domains for auth.
- `--user-id` is local-only and not sent to IMA servers.
- Local files: preferences and logs in `~/.openclaw`.

---

## Agent Execution (Internal)

```bash
# Text to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_video \
  --model-id ima-pro \
  --prompt "a puppy runs across a sunny meadow, cinematic" \
  --user-id {user_id} \
  --output-json

# Image to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type image_to_video \
  --model-id ima-pro-fast \
  --prompt "camera slowly zooms in" \
  --input-images https://example.com/photo.jpg \
  --user-id {user_id} \
  --output-json

# First-last frame to video
python3 {baseDir}/scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type first_last_frame_to_video \
  --model-id ima-pro \
  --prompt "smooth transition" \
  --input-images https://example.com/first.jpg https://example.com/last.jpg \
  --user-id {user_id} \
  --output-json

```

`--input-images` accepts remote HTTP(S) links and local file paths.
Local image files are uploaded to OSS first; non-local HTTP(S) links are assigned directly.
CLI form is space-separated arguments; equivalent JSON form is:
`["https://example.com/ref1.jpg","https://example.com/ref2.jpg"]`.

---

## 🚨 CRITICAL: How to send video to user

Always send remote URL directly:

```python
video_url = json_output["url"]
message(action="send", media=video_url, caption="✅ 视频生成成功")
```

Do NOT download to local file before sending.

---

## 🧠 User Preference Memory

Storage: `~/.openclaw/memory/ima_prefs.json`

```json
{
  "user_{user_id}": {
    "text_to_video": {"model_id": "ima-pro", "model_name": "Ima Sevio 1.0", "credit": 0, "last_used": "..."},
    "image_to_video": {"model_id": "ima-pro-fast", "model_name": "Ima Sevio 1.0-Fast", "credit": 0, "last_used": "..."},
    "first_last_frame_to_video": {"model_id": "ima-pro", "model_name": "Ima Sevio 1.0", "credit": 0, "last_used": "..."},
    "reference_image_to_video": {"model_id": "ima-pro", "model_name": "Ima Sevio 1.0", "credit": 0, "last_used": "..."}
  }
}
```

Model selection priority:
1. user preference
2. knowledge-ai recommendation
3. fallback default (`ima-pro`)

### Defaults

| Task | Default | Alt (fast) |
|---|---|---|
| text_to_video | `ima-pro` | `ima-pro-fast` |
| image_to_video | `ima-pro` | `ima-pro-fast` |
| first_last_frame_to_video | `ima-pro` | `ima-pro-fast` |
| reference_image_to_video | `ima-pro` | `ima-pro-fast` |

---

## 💬 User Experience Protocol (IM / Feishu / Discord)

### Estimated Generation Time

| Model | Estimated Time | Poll Every | Send Progress Every |
|---|---:|---:|---:|
| ima-pro | 120~300s | 8s | 45s |
| ima-pro-fast | 60~120s | 8s | 30s |

Polling timeout upper bound: **40 minutes** (`2400s`).

Use:
- Step 1: pre-generation notice (model/time/credits)
- Step 2: progress updates
- Step 3: success push (video first, then shareable link)
- Step 4: failure message with actionable retry options

Progress formula:

```text
P = min(95, floor(elapsed_seconds / estimated_max_seconds * 100))
```

---

## Step 4 — Failure Notification

Translate technical errors to user language. For 401/4008 include links:
- API key: https://www.imaclaw.ai/imaclaw/apikey
- credits: https://www.imaclaw.ai/imaclaw/subscription

### Enhanced Error Handling (Reflection)

The script keeps the same reflection mechanism (up to 3 retries):
- `500` → parameter degradation
- `6009` → auto-complete missing params from matched rules
- `6010` → reselect matching credit rule
- timeout → actionable guidance

### Fallback suggestion table

| Failed model | First alt | Second alt |
|---|---|---|
| `ima-pro` | `ima-pro-fast` | `ima-pro` (retry with downgraded params) |
| `ima-pro-fast` | `ima-pro` | `ima-pro-fast` (retry with defaults) |
| unknown | `ima-pro` | `ima-pro-fast` |

---

## Supported Models

Only two models are exposed by this skill:
- `ima-pro`
- `ima-pro-fast`

Supported categories:
- `text_to_video`
- `image_to_video`
- `first_last_frame_to_video`
- `reference_image_to_video`

> Attribute rules, points, and exact parameter combinations must be queried at runtime from product list.

---

## Environment

Base URL: `https://api.imastudio.com`

Required headers:
- `Authorization: Bearer ima_your_api_key_here`
- `x-app-source: ima_skills`
- `x_app_language: en` (or `zh`)

---

## ⚠️ MANDATORY: Always Query Product List First

You MUST call `/open/v1/product/list` before creating tasks.
`attribute_id` and `credit` must match current rule set.

Common failures if skipped:
- invalid product attribute
- insufficient points
- `6006`, `6010`

---

## Core Flow

```text
1) GET /open/v1/product/list
2) (if image input) upload image(s) -> HTTPS CDN URL(s)
3) POST /open/v1/tasks/create
4) POST /open/v1/tasks/detail (poll every 8s)
```

---

## Image Upload

For image tasks, source images must resolve to public HTTPS URLs.
Bundled script supports local file path and uploads automatically.

---

## API 1: Product List

`GET /open/v1/product/list?app=ima&platform=web&category=<task_type>`

Use type=3 leaf nodes to read:
- `model_id`
- `id` (`model_version`)
- `credit_rules[]`
- `form_config[]`

---

## API 2: Create Task

`POST /open/v1/tasks/create`

### text_to_video (example)

```json
{
  "task_type": "text_to_video",
  "enable_multi_model": false,
  "src_img_url": [],
  "parameters": [
    {
      "attribute_id": 1234,
      "model_id": "ima-pro",
      "model_name": "Ima Sevio 1.0",
      "model_version": "ima-pro",
      "app": "ima",
      "platform": "web",
      "category": "text_to_video",
      "credit": 25,
      "parameters": {
        "prompt": "a puppy dancing happily",
        "duration": 5,
        "resolution": "1080P",
        "aspect_ratio": "16:9",
        "n": 1,
        "input_images": [],
        "cast": {"points": 25, "attribute_id": 1234}
      }
    }
  ]
}
```

For image tasks, keep top-level `src_img_url` and nested `input_images` consistent.

---

## API 3: Task Detail

`POST /open/v1/tasks/detail` with `{ "task_id": "..." }`

Status interpretation:
- `resource_status`: `0/null` processing, `1` ready, `2` failed, `3` deleted
- Stop only when all medias have `resource_status == 1` and none failed

---

## Common Mistakes

- Polling too fast (use 8s)
- Missing required nested fields (`prompt`, `cast`, `n`)
- Credit/attribute mismatch (`6006` / `6010`)
- Inconsistent `src_img_url` and `input_images`
- Wrong mode choice (`image_to_video` vs `reference_image_to_video`)

---

## Python Example

```python
import time
import requests

BASE_URL = "https://api.imastudio.com"
API_KEY = "ima_your_key_here"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "x-app-source": "ima_skills",
    "x_app_language": "en",
}

ALLOWED = {"ima-pro", "ima-pro-fast"}


def get_products(category: str) -> list:
    r = requests.get(
        f"{BASE_URL}/open/v1/product/list",
        headers=HEADERS,
        params={"app": "ima", "platform": "web", "category": category},
    )
    r.raise_for_status()
    nodes = r.json().get("data", [])
    leaves = []

    def walk(items):
        for n in items:
            if n.get("type") == "3" and n.get("model_id") in ALLOWED:
                leaves.append(n)
            walk(n.get("children") or [])

    walk(nodes)
    return leaves


def create_video_task(task_type: str, prompt: str, product: dict, src_img_url=None, **extra) -> str:
    src_img_url = src_img_url or []
    rule = product["credit_rules"][0]
    defaults = {f["field"]: f["value"] for f in product.get("form_config", []) if f.get("value") is not None}

    params = {
        "prompt": prompt,
        "n": 1,
        "input_images": src_img_url,
        "cast": {"points": rule["points"], "attribute_id": rule["attribute_id"]},
        **defaults,
    }
    params.update(extra)

    payload = {
        "task_type": task_type,
        "enable_multi_model": False,
        "src_img_url": src_img_url,
        "parameters": [{
            "attribute_id": rule["attribute_id"],
            "model_id": product["model_id"],
            "model_name": product["name"],
            "model_version": product["id"],
            "app": "ima",
            "platform": "web",
            "category": task_type,
            "credit": rule["points"],
            "parameters": params,
        }],
    }

    r = requests.post(f"{BASE_URL}/open/v1/tasks/create", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["data"]["id"]


def poll(task_id: str, interval: int = 8, timeout: int = 600) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.post(f"{BASE_URL}/open/v1/tasks/detail", headers=HEADERS, json={"task_id": task_id})
        r.raise_for_status()
        task = r.json().get("data", {})
        medias = task.get("medias", [])
        if medias:
            rs = lambda m: m.get("resource_status") if m.get("resource_status") is not None else 0
            if any(rs(m) in (2, 3) or (m.get("status") == "failed") for m in medias):
                raise RuntimeError(f"Task failed: {task_id}")
            if all(rs(m) == 1 for m in medias):
                return task
        time.sleep(interval)
    raise TimeoutError(f"Task timed out: {task_id}")
```
