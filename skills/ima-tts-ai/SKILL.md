---
name: IMA Studio TTS
version: 1.0.0
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, tts, text-to-speech, speech synthesis, voice, 语音合成, 文字转语音, IMA, TTS, 多模型
argument-hint: "[text to speak or 要朗读的文本]"
description: >
  Use when generating speech from text (text-to-speech) via IMA Open API. Use for: voice synthesis,
  TTS,朗读, 语音合成, 配音, 有声内容. Output: audio URL (mp3/wav). Flow: query products →
  create task → poll until done. Requires IMA API key. This skill targets seed-tts-2.0 only
  (seed-tts-1.1 is not supported). Default model is seed-tts-2.0.
requires:
  env:
    - IMA_API_KEY
  primaryCredential: IMA_API_KEY
  credentialNote: IMA_API_KEY is sent only to api.imastudio.com for TTS product/task APIs.
persistence:
  readWrite:
    - ~/.openclaw/memory/ima_prefs.json
    - ~/.openclaw/logs/ima_skills/
  retention: Logs are auto-cleaned after 7 days; preferences remain until user deletes them.
---

# IMA TTS (Text-to-Speech)

## Overview

Call IMA Open API to create **text-to-speech** audio. Same flow as other IMA creation skills: **query products → create task → poll until done**. Task type is `text_to_speech`. **This skill targets seed-tts-2.0 only** — seed-tts-1.1 is not supported; the script defaults to `seed-tts-2.0` when no model is specified.

## ⚙️ How This Skill Works

This skill uses a bundled Python script `scripts/ima_tts_create.py` to call the IMA Open API:

- Sends **text (prompt)** to `https://api.imastudio.com`
- Uses `--user-id` only locally for preference storage
- Returns an **audio URL** when synthesis is complete
- **Reflection mechanism**: on create failure, retries up to 3 times with parameter adjustments

**What gets sent to IMA:** prompt (text to speak), model selection, parameters (e.g. voice_id, speed). **Not sent:** API key in prompt body; user_id is local only.

### Agent Execution

Use the bundled script:

```bash
# List available TTS models (optional; default is seed-tts-2.0)
python3 {baseDir}/scripts/ima_tts_create.py --api-key $IMA_API_KEY --list-models

# Generate speech (default model: seed-tts-2.0; omit --model-id to use default)
python3 {baseDir}/scripts/ima_tts_create.py \
  --api-key $IMA_API_KEY \
  --model-id seed-tts-2.0 \
  --prompt "Text to be spoken here." \
  --user-id {user_id} \
  --output-json
```

Script outputs JSON; parse it for `url` and pass to the user via the UX protocol below.

---

## Environment

Base URL: `https://api.imastudio.com`

| Header | Required | Value |
|--------|----------|-------|
| `Authorization` | ✅ | `Bearer ima_your_api_key_here` |
| `x-app-source` | ✅ | `ima_skills` |
| `x_app_language` | recommended | `en` / `zh` |

---

## ⚠️ MANDATORY: Always Query Product List First

You **MUST** call `/open/v1/product/list` with `category=text_to_speech` before creating any task. `attribute_id` is required; if 0 or missing → `"Invalid product attribute"` and task fails.

```python
GET /open/v1/product/list?app=ima&platform=web&category=text_to_speech
```

Then traverse the V2 tree: `type=2` = model groups, `type=3` = versions (leaves). Only `type=3` nodes have `credit_rules` and `form_config`. Use a leaf’s `model_id`, `id` (= model_version), and `credit_rules[0].attribute_id` / `points` for create.

---

## Core Flow

```
1. GET /open/v1/product/list?app=ima&platform=web&category=text_to_speech
   → Get attribute_id, credit, model_version, form_config

2. POST /open/v1/tasks/create
   → task_type: "text_to_speech", parameters[].parameters.prompt = text to speak

3. POST /open/v1/tasks/detail  { "task_id": "..." }
   → Poll every 2–5s until medias[].resource_status == 1 and status != "failed"
   → Read medias[].url (and optional duration_str, format)
```

---

## Task Detail API — Actual Response Shape

Poll `POST /open/v1/tasks/detail` until completion. Response uses the same structure as other IMA audio tasks:

| Field | Type | Meaning |
|-------|------|--------|
| `resource_status` | int or null | 0=处理中, 1=可用, 2=失败, 3=已删除；null 视为 0 |
| `status` | string | "pending" / "processing" / "success" / "failed" |
| `url` | string | Audio URL when resource_status=1 (mp3/wav) |
| `duration_str` | string | Optional, e.g. "30s" |
| `format` | string | Optional, e.g. "mp3", "wav" |

**Completed success example:**

```json
{
  "id": "task_xxx",
  "medias": [{
    "resource_status": 1,
    "status": "success",
    "url": "https://cdn.../output.mp3",
    "duration_str": "12s",
    "format": "mp3"
  }]
}
```

**Rules:**

- Treat `resource_status: null` as 0 (processing).
- Success only when **all** medias have `resource_status == 1` and `status != "failed"`.
- On `resource_status == 2` or `status == "failed"`, stop and handle error (e.g. use `error_msg` / `remark`).

---

## API 2: Create Task

```
POST /open/v1/tasks/create
```

**text_to_speech** — no image input. `src_img_url: []`, `input_images: []`.

```json
{
  "task_type": "text_to_speech",
  "enable_multi_model": false,
  "src_img_url": [],
  "parameters": [{
    "attribute_id":  "<from credit_rules>",
    "model_id":      "<model_id>",
    "model_name":    "<model_name>",
    "model_version": "<version_id>",
    "app":           "ima",
    "platform":      "web",
    "category":      "text_to_speech",
    "credit":        "<points>",
    "parameters": {
      "prompt":       "Text to be spoken.",
      "n":            1,
      "input_images": [],
      "cast":         {"points": "<points>", "attribute_id": "<attribute_id>"}
    }
  }]
}
```

`prompt` must be inside `parameters[].parameters`, not at top level. Extra fields (e.g. voice_id, speed) come from product `form_config`; include only those present in the product’s credit_rules/form_config.

Response: `data.id` = task_id for polling.

---

## Supported Task Type & Models

| category | Capability | Input |
|----------|------------|-------|
| `text_to_speech` | Text → Speech | prompt (text to speak) |

**Models:** This skill supports **seed-tts-2.0** only (seed-tts-1.1 is not supported). The script defaults to `--model-id seed-tts-2.0` when none is provided. For current `attribute_id` and `credit`, the script reads from the product list at runtime.

### seed-tts-2.0 — Verified request parameters

The following `parameters[].parameters` shape has been verified to work for **seed-tts-2.0** (attribute_id/credit come from product list and may differ by app/platform):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ | Text to speak (合成文本). |
| `n` | int | ✅ | Usually 1. |
| `model` | string | ✅ | Sub-model: `seed-tts-2.0-expressive` (default) or `seed-tts-2.0-standard`. |
| `speaker` | string | optional | Speaker ID / 发音人，e.g. `zh_male_sophie_uranus_bigtts`（[音色列表 1257544](https://www.volcengine.com/docs/6561/1257544) 中原生 voice_type）. **注意：** 使用原生格式（如 `zh_male_*_uranus_bigtts`），不支持 `BV*_streaming` 格式。 |
| `audio_params` | object | optional | `emotion`（情感）、`speech_rate`（语速 [-50,100]）、`loudness_rate`（音量 [-50,100]）等，见 [1598757 请求 Body](https://www.volcengine.com/docs/6561/1598757?lang=zh). |
| `additions` | object | optional | e.g. `{"explicit_language": "crosslingual", "context_texts": []}`. |
| `cast` | object | ✅ | `{"points": <credit>, "attribute_id": <attribute_id>}` from product list. |

**Script example with extra params:**

```bash
python3 ima_tts_create.py --api-key $IMA_API_KEY --model-id seed-tts-2.0 \
  --prompt "阳光青年音色测试，你好世界。" \
  --extra-params '{"model":"seed-tts-2.0-expressive","speaker":"zh_male_sophie_uranus_bigtts","audio_params":{"emotion":"neutral"},"additions":{"explicit_language":"crosslingual","context_texts":[]}}' \
  --output-json
```

**Note:** The script gets `attribute_id` and `credit` from the product list (e.g. `app=ima&platform=web` → often 2 pts / attribute_id 4419 for seed-tts-2.0). If you have a different app/platform (e.g. webAgent), the product list may return different credit_rules (e.g. 5 pts / attribute_id 8987); the script uses whatever the product list returns for the chosen model.

**Speaker / 音色列表（seed-tts-2.0 兼容火山引擎音色）：** 完整音色 ID 与场景分类见项目内 `volcengine_tts_timbre_list.json`。该文件来自 [火山引擎豆包语音合成音色列表](https://www.volcengine.com/docs/6561/1257544)，使用原生 `voice_type` 格式（如 `zh_male_sophie_uranus_bigtts` 魅力苏菲、`zh_female_vv_uranus_bigtts` Vivi）。**⚠️ 注意：** IMA API 只支持原生格式（`*_uranus_bigtts` 系列），不支持 `BV*_streaming` 豆包音色 ID。

**与火山引擎 2.0 文档对照：** 上述参数与 [HTTP Chunked/SSE 单向流式 V3 请求 Body](https://www.volcengine.com/docs/6561/1598757?lang=zh) 一致：`req_params.text` → prompt，`req_params.speaker` → speaker（必填项），`req_params.model` → model（expressive/standard），`req_params.audio_params`（emotion、speech_rate、loudness_rate 等），`req_params.additions`（如 explicit_language）。2.0 能力说明见 [豆包语音合成2.0能力介绍](https://www.volcengine.com/docs/6561/1871062?lang=zh)（语音指令、引用上文、语音标签等）。

---

## 🎤 当用户说「帮我制作旁白/配音」时如何询问

当用户表达「帮我制作旁白」「做一段配音」「把这段文字读出来」等意图时，**必须先收集关键信息再调用脚本**，避免缺参或盲目默认。

### 必问

| 询问项 | 对应参数 | 说明 |
|--------|----------|------|
| **要朗读的内容 / 旁白文案** | `prompt` | 合成文本，必填。若用户只给主题，可请用户提供具体文案或由你生成后让用户确认。 |

### 建议问（让用户选择）

| 询问项 | 对应参数 | 选项来源与示例 |
|--------|----------|----------------|
| **音色 / 发音人** | `speaker` | 从项目内 `volcengine_tts_timbre_list.json`（或 [音色列表 1257544](https://www.volcengine.com/docs/6561/1257544)）按场景推荐：**通用场景**（魅力苏菲 `zh_male_sophie_uranus_bigtts`、Vivi `zh_female_vv_uranus_bigtts`、云舟 `zh_male_m191_uranus_bigtts`）、**视频配音**（大壹 `zh_male_dayi_uranus_bigtts`、猴哥 `zh_male_sunwukong_uranus_bigtts`）、**角色扮演**（知性灿灿 `zh_female_cancan_uranus_bigtts`、撒娇学妹 `zh_female_sajiaoxuemei_uranus_bigtts`）。可简短列出 3–5 个候选让用户选，或问「要男声/女声？偏解说/读书/助手？」再缩小范围。**⚠️ 使用原生格式**（`*_uranus_bigtts`）。 |

### 可选问（按需补充）

| 询问项 | 对应参数 | 说明与取值 |
|--------|----------|------------|
| **情感 / 情绪** | `audio_params.emotion` | 部分音色支持，如 neutral、sad、angry；详见 [音色列表-多情感音色](https://www.volcengine.com/docs/6561/1257544)。 |
| **语速** | `audio_params.speech_rate` | 范围 [-50, 100]，0 为正常，100 约 2 倍速。可通过 `--extra-params '{"audio_params":{"speech_rate":20}}'` 传入。 |
| **音量** | `audio_params.loudness_rate` | 范围 [-50, 100]，0 为正常（mix 音色不支持）。 |
| **模型风格** | `model` | `seed-tts-2.0-expressive`（默认，表现力强）或 `seed-tts-2.0-standard`（更稳定）。 |

**脚本对应：** `--prompt` 必填；`--speaker`、`--emotion` 直接支持；语速/音量/模型等通过 `--extra-params` 传入 JSON（见上文 Script example）。

---

## 📥 User Input Parsing (Parameter Recognition)

Map user intent to parameters using product `form_config` (e.g. voice, speed):

| User intent / phrasing | Parameter (if in form_config) | Notes |
|-------------------------|---------------------------------|--------|
| 旁白 / 配音 / 朗读 / 把这段读出来 | prompt + speaker（建议问） | **先问清内容与音色**，再调用；见上方「当用户说制作旁白/配音时如何询问」。 |
| 女声 / 女声朗读 / female voice | voice_id / voice_type / speaker | Use value from form_config or e.g. speaker ID |
| 男声 / 男声朗读 / male voice | voice_id / voice_type / speaker | Use value from form_config or e.g. speaker ID |
| 发音人 / 音色 / speaker | speaker | seed-tts-2.0: e.g. zh_male_sophie_uranus_bigtts，见 volcengine_tts_timbre_list.json（原生格式） |
| 情感 / 情绪 / emotion | audio_params.emotion | e.g. "neutral", "sad"；部分音色支持 |
| 语速快/慢 / speed up/slow | audio_params.speech_rate | 范围 [-50, 100]，0 为正常 |
| 音调 / pitch | pitch | If supported |
| 大声/小声 / volume | audio_params.loudness_rate | 范围 [-50, 100] |
| 风格 expressive/standard | model | seed-tts-2.0: seed-tts-2.0-expressive / seed-tts-2.0-standard |

If the user does not specify, use form_config defaults. Do not send parameters not present in the product’s credit_rules/attributes or form_config (reflection will strip them on retry).

---

## 🧠 User Preference Memory

Storage: `~/.openclaw/memory/ima_prefs.json`

```json
{
  "user_{user_id}": {
    "text_to_speech": {
      "model_id": "...",
      "model_name": "...",
      "credit": 2,
      "last_used": "..."
    }
  }
}
```

- **Before generation:** Load prefs; if `user_{user_id}.text_to_speech` exists, use that model and optionally mention it.
- **After success:** Save used model to `user_{user_id}.text_to_speech`.
- **On explicit change:** e.g. “换成XXX” / “以后都用XXX” → switch and save.

---

## 💬 User Experience Protocol (IM / Feishu / Discord)

TTS usually completes in a few seconds to tens of seconds. **Do not leave users without feedback.**

### Step 0 — Initial Acknowledgment (Normal Reply)

First reply with a short acknowledgment (normal reply, not message tool), e.g.:

- 好的，正在帮你把这段文字转成语音。
- OK, converting this text to speech.

### Step 1 — Pre-Generation Notification (message tool)

Push once:

```
🔊 开始语音合成，请稍候…
• 模型：[Model Name]
• 预计耗时：[X ~ Y 秒]
• 消耗积分：[N pts]
```

### Step 2 — Progress

Poll every 2–5s. Every 10–15s send a progress update, e.g.:

```
⏳ 语音合成中… [P]%
已等待 [elapsed]s，预计最长 [max]s
```

Cap progress at 95% until API returns success.

### Step 3 — Success (message tool)

When `resource_status == 1` and `status != "failed"`, send the audio and caption:

- **media** = `medias[0].url`
- **caption** example:

```
✅ 语音合成成功！
• 模型：[Model Name]
• 耗时：[actual]s
• 消耗积分：[N pts]
🔗 原始链接：[url]
```

Use the **URL** from the API (do not use local file paths).

### Step 4 — Failure (message tool)

On failure or API/network error, send a short, user-friendly message and suggestions:

```
❌ 语音合成失败
• 原因：[自然语言原因]
• 建议：换个模型重试或检查文本长度/内容

需要我帮你用其他模型重试吗？
```

**Error translation (do not expose raw API/technical errors):**

| Technical | ✅ Say (CN) | ✅ Say (EN) |
|-----------|-------------|-------------|
| 401 Unauthorized | 密钥无效或未授权，请至 imaclaw.ai 生成新密钥 | API key invalid; generate at imaclaw.ai |
| 4008 Insufficient points | 积分不足，请至 imaclaw.ai 购买积分 | Insufficient points; buy at imaclaw.ai |
| Invalid product attribute | 参数配置异常，请稍后重试 | Configuration error, try again later |
| Error 6006 / 6010 | 积分或参数不匹配，请换模型或重试 | Points/params mismatch, try another model |
| resource_status == 2 / status failed | 合成失败，建议换模型或缩短文本 | Synthesis failed, try another model or shorter text |
| timeout | 合成超时，请稍后重试 | Timed out, try again later |
| Network error | 网络不稳定，请检查后重试 | Network unstable, check and retry |

Links: API key — https://www.imaclaw.ai/imaclaw/apikey ；Credits — https://www.imaclaw.ai/imaclaw/subscription

### Step 5 — Done

After Step 0–4, no further reply needed. Do not send duplicate confirmations.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| prompt at top level | Put prompt inside `parameters[].parameters` |
| Wrong or missing attribute_id | Always call product list first; use credit_rules[0] |
| Single poll | Poll until all medias have resource_status == 1 |
| Ignoring status when resource_status=1 | Check status != "failed" |
| Sending params not in form_config/credit_rules | Use only params from product list; script reflection will strip others on retry |

---

## Security & Local Data

- **Network:** This skill uses only `https://api.imastudio.com` (no image upload domain for TTS).
- **Local files:** `~/.openclaw/memory/ima_prefs.json` (preferences), `~/.openclaw/logs/ima_skills/` (logs, e.g. 7-day retention). No prompts or API keys stored.
- **API key:** Set via environment (e.g. `IMA_API_KEY`) or agent config; never hardcode.

---

## Python Example (Minimal)

```python
import time
import requests

BASE = "https://api.imastudio.com"
HEADERS = {
    "Authorization": "Bearer ima_your_key",
    "Content-Type": "application/json",
    "x-app-source": "ima_skills",
}

# 1. Product list
r = requests.get(
    f"{BASE}/open/v1/product/list",
    headers=HEADERS,
    params={"app": "ima", "platform": "web", "category": "text_to_speech"},
)
tree = r.json()["data"]
# ... find type=3 node, get attribute_id, model_id, model_version, credit ...

# 2. Create task
body = {
    "task_type": "text_to_speech",
    "enable_multi_model": False,
    "src_img_url": [],
    "parameters": [{
        "attribute_id": attribute_id,
        "model_id": model_id,
        "model_name": model_name,
        "model_version": model_version,
        "app": "ima", "platform": "web",
        "category": "text_to_speech",
        "credit": credit,
        "parameters": {
            "prompt": "Hello, world.",
            "n": 1,
            "input_images": [],
            "cast": {"points": credit, "attribute_id": attribute_id},
        },
    }],
}
r = requests.post(f"{BASE}/open/v1/tasks/create", headers=HEADERS, json=body)
task_id = r.json()["data"]["id"]

# 3. Poll
while True:
    r = requests.post(f"{BASE}/open/v1/tasks/detail", headers=HEADERS, json={"task_id": task_id})
    task = r.json()["data"]
    medias = task.get("medias") or []
    if not medias:
        time.sleep(3)
        continue
    rs = medias[0].get("resource_status")
    if rs is None: rs = 0
    if rs == 2 or (medias[0].get("status") or "").lower() == "failed":
        raise RuntimeError(medias[0].get("error_msg") or "failed")
    if rs == 1 and (medias[0].get("url") or medias[0].get("watermark_url")):
        url = medias[0]["url"] or medias[0]["watermark_url"]
        print(url)  # e.g. https://cdn.../output.mp3
        break
    time.sleep(3)
```

---

## Quick Reference

| Item | Value |
|------|--------|
| Task type | `text_to_speech` |
| Product list | `GET /open/v1/product/list?category=text_to_speech` |
| Create | `POST /open/v1/tasks/create` (prompt inside parameters[].parameters) |
| Poll | `POST /open/v1/tasks/detail` every 2–5s |
| Done when | All medias: resource_status=1, status≠"failed", url present |
| Script | `scripts/ima_tts_create.py` (--list-models, --model-id, --prompt, --output-json) |
