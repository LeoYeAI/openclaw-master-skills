---
name: plume-infographic
description: |
  Plume AI Infographic Generation Service. Triggered when users want to convert topics, long-form text, or reference images into infographics.
  Supports: topic infographics, long-form text to infographic, reference image infographics (sketch/style transfer/product embed/content rewrite), batch infographics, retry.
  Activate when user mentions: infographic, knowledge poster, visualize article,
  diagram, summary chart, timeline, turn this article into a graphic, create a visual about XX,
  use this infographic's style as reference, use this product image for infographic, replace the content of this infographic,
  create a series of infographics, split long text into multi-page infographics,
  信息图, 知识图谱海报, 把文章可视化, 图解, 总结图, 时间线图, 把这篇文章转成图,
  围绕XX主题做一张图解, 参照这张信息图的风格, 用这张产品图做信息图,
  把这张信息图的内容换成, 做一组系列信息图, 把长文拆成多页信息图.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/*), Bash(cat ~/.openclaw/media/plume/*), Bash(zip *)
metadata: {"openclaw": {"requires": {"env": ["PLUME_API_KEY"]}, "primaryEnv": "PLUME_API_KEY"}}
---

# Plume AI Infographic Service

Help users generate infographics through natural language. Infographics emphasize "layout design" and "information delivery", distinct from regular illustrations/posters.

Boundary with plume-image: User says "infographic/diagram/visualize/timeline/turn article into graphic" → this skill; says "generate image/poster/remove background/video" → plume-image.

## Mandatory Pre-check

Must execute before each use:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/check_config.py
```

- `CONFIGURED` — Configured, proceed with workflow
- `NOT_CONFIGURED` — Stop, prompt user to visit Plume[https://design.useplume.app/openclaw-skill](https://design.useplume.app/openclaw-skill) to get API Key and configure it in `~/.openclaw/openclaw.json` under `skills.entries.plume-infographic.env.PLUME_API_KEY`

## Template Gallery

During content planning, always include the template gallery link for users to browse styles. Append `?lang=` parameter based on the user's language:

| User Language | Link |
|--------------|------|
| 中文 | `https://design.useplume.app/openclaw-skill/templates?lang=zh-CN` |
| English | `https://design.useplume.app/openclaw-skill/templates?lang=en` |
| 日本語 | `https://design.useplume.app/openclaw-skill/templates?lang=ja` |

Agent auto-selects the matching link based on the language the user is currently using in conversation. Example: [Browse Template Gallery](https://design.useplume.app/openclaw-skill/templates?lang=en)

When user clicks a template and pastes it back, Agent extracts the template name to search for matching ID, then passes it via `--template-id` when creating the task.

If user doesn't select a template and confirms directly, Agent auto-matches style based on content (can pass via `--style-hint`).

## Core Workflow

**`transfer` (when reference image exists) → `create` (sync wait for result) → get local image path → subsequent operations (deliver/package etc.)**

**Before calling create, you must first send a waiting message to the user via `message send`**, e.g. "Sure, generating your infographic now. This usually takes 1-2 minutes, please wait." This message must be a separate tool call, **cannot be in the same turn as create**. After `message send` returns success, call create in the next turn. Because create is synchronous and blocking — if the prompt text and create are in the same turn, the text may not reach the user before blocking starts.

```bash
# Upload reference image (reference mode, subcommand is transfer not upload)
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py transfer --file /path/to/image.png
# Returns {"success": true, "image_url": "https://...", "width": W, "height": H}

# Create task and wait for result (default timeout 30 minutes)
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> --mode <article|reference> [params...]
# Returns {"success": true, "task_id": "xxx", "images": ["/abs/path/result_xxx.png", ...], "result_urls": [...]}

# After getting images, continue with operations:
# Deliver to user
openclaw message send --channel <channel> --target <target> --media /abs/path/result_xxx.png --message "Infographic generation complete"
# Or package
zip -j /tmp/infographic.zip /abs/path/result_xxx.png
openclaw message send --channel <channel> --target <target> --media /tmp/infographic.zip --message "Infographic packaged"
```

**Prohibited:** Fabricating task_id/URL, asking for API Key in chat, auto-creating tasks when user only sends image without text, creating tasks directly when user only gives a topic word or one sentence in any language (e.g. "做一张XX的信息图", "帮我做个XX图解", "Make an infographic about XX" — must guide and confirm content and style first, see "Content Planning" section), uploading local files without explicit user confirmation, deleting or modifying any JSON files under `~/.openclaw/media/plume/` (action_log, circuit_breaker, etc.).

**Timeout handling:** If create returns `"status": "timeout"`, inform user the task is still processing and they can retry later.

## Scenario Detection

When receiving user message, check in the following order, stop on first match:

```
1. Does this turn have a new image?
   ├─ Has image + has action instruction → go to [Reference Image] flow
   │   ├─ Product/physical item/character + selling points text → reference_type=product_embed
   │   ├─ Existing infographic + "use this style as reference" → reference_type=style_transfer
   │   ├─ Existing infographic + "replace content with XX" → reference_type=content_rewrite
   │   └─ Hand-drawn/sketch → reference_type=sketch
   │   Note: Even with detailed text, as long as this turn has an image, must go through reference image flow, cannot use article
   ├─ Has image + no text → Reply "Got the image, how would you like me to process it?"
   └─ No new image → continue ↓

2. Does conversation history have [media attached: /path/...] with no corresponding task record in action_log?
   ├─ Yes → **Ask user for confirmation before uploading** (e.g. "I found an image from earlier: <filename>. Shall I upload it as the reference image?")
   │       After user confirms, transfer --file <path>, determine reference_type based on user's text description, go to [Reference Image] flow
   └─ No → continue ↓

3. Is user referencing/modifying existing results? ("switch style", "try again", "regenerate", "change the look", "换个风格", "再试一次", "重新生成", "换个样式")
   ├─ Yes → Read action_log, go to [Retry] flow
   └─ No → go to [New Creation] flow (article mode)
```

**Typical two-turn scenario:** Turn 1: sends image without text → generic agent replies (skill not triggered); Turn 2: says "use this rice cooker for an infographic, selling points: ..." → skill triggers, step 2 asks user to confirm the image before uploading, then goes to product_embed.

**Retry detection:** When action_log records exist, step 2 is skipped, step 3 matches retry keywords → goes to retry flow.

### User Intent → Mode Mapping

| User Says | mode | Key Parameters |
|-----------|------|---------------|
| "Make an infographic about XX" / "做一张XX的信息图" / "帮我做个XX图解" | `article` | `--article` (Agent first expands into complete content) |
| "Turn this article into an infographic" / "把这篇文章转成信息图" | `article` | `--article` |
| Upload image + "turn this into an infographic" / "把这个做成信息图" | `reference` | `--reference-type sketch` + urls + width + height |
| Upload image + "use this style to make one about XX" / "参照这个风格做一张关于XX" | `reference` | `--reference-type style_transfer` + urls + width + height + topic/article |
| Upload image + "replace the content with XX" / "把内容换成XX" | `reference` | `--reference-type content_rewrite` + urls + width + height + article |
| Upload product image + "use this product for infographic, selling points are..." / "用这个产品做信息图，卖点是..." | `reference` | `--reference-type product_embed` + urls + width + height + `--reference-article <selling points>` |
| "Switch style" / "换个风格" (for existing result) | Retry | `--action switch_style` + `--last-task-id` + `--article <original content>` |
| "Regenerate" / "重新生成" / "再试一次" (for existing result) | Retry | `--action repeat_last_task` + `--last-task-id` |
| "Replace content with XX" / "把内容换成XX" (for existing result) | Retry | `--action switch_content` + `--article <new content>` + `--last-task-id` |
| "Change to 16:9" / "landscape" / "portrait" / "换成16:9" / "横版" / "竖版" (change ratio) | Retry | `--action switch_content` + `--last-task-id` + `--article <original content>` + `--aspect-ratio <new ratio>` |
| "Generate N infographics in a series" / "生成N张系列信息图" | Batch | `--count N` + `--child-reference-type` (see Batch rules below) |

**Important: When user requests a ratio change, must pass `--aspect-ratio` (e.g. 16:9 / 4:3 / 1:1 / 3:4 / 9:16), otherwise default 3:4 will be used.**

For complete parameter documentation see [references/modes.md](references/modes.md), scenario examples see [references/workflows.md](references/workflows.md).

### Reference Image Source

1. Current turn has image + text → `transfer --file` to upload, pass returned `width`/`height` via `--reference-image-width`/`--reference-image-height`
2. Current turn has only image, no text → Reply "Got the image, how would you like me to process it?"
3. Previous turn had image, current turn has text → Extract `[media attached: /path/...]` path from history, **ask user to confirm before uploading** (e.g. "I'll use the image you sent earlier as the reference. OK?")
4. User references "the last generated one" → Read `action_log_{channel}.json` for most recent `status=success` entry's `result_url`; if empty, fallback to `last_result_{channel}.json`
5. None available → Prompt to send an image

`result_url` is a remote URL, do NOT use `local_file`.

### Retry

1. Read `action_log_{channel}.json`; if empty, fallback to `last_result_{channel}.json`; if both empty, prompt to generate one first

2. Select base record:
   - "Try again" / "Regenerate" → Take the **last entry** (regardless of success/failure) and replay
   - "Switch style" / "Switch content" → Take the **most recent entry with status=success**, use its task_id as `--last-task-id`

3. Build command:
   - **Batch retry must restore count**: If `params.count >= 2`, must include `--count {params.count}`
   - "Try again": `action=null` → `repeat_last_task`; `action!=null` → replay with same action, `--last-task-id` from original record's `last_task_id`
   - `switch_style` must include `--article` (get original content from action_log), otherwise subsequent retries lose context

> When retrying, no need to re-upload reference images (backend reads from original task via `last_task_id`).

## Usage Guide

When the user first triggers this skill but their intent is vague (e.g. just says "infographic", "make me a graphic", without providing a specific topic or image), Agent must reply with a brief usage guide containing two example directions:

```
Here's how you can get started:

1️⃣ Tell me a topic directly, e.g.: "Create an infographic about the history of gold"
2️⃣ Upload an existing infographic, then say: "Replace the content with xxx topic"

How would you like to start?
```

**Trigger condition:** User message contains infographic-related keywords but has neither a specific topic/content nor an uploaded image. If the user has already given a clear intent (e.g. "make an infographic about the history of AI"), skip the guide and go directly to the content planning flow.

**Multilingual note:** Users may write in any language. The same rules apply regardless of language. For example, "帮我生成一张手机发展史的信息图" is equivalent to "Make an infographic about the history of smartphones" — both are topic-only requests with no specific content, and must go through content planning.

## Content Planning (Mandatory, Cannot Skip)

**Before calling create, must determine if user input is "information-complete":**

**CRITICAL — Language-agnostic rule:** A single topic/sentence request is NEVER information-complete, regardless of language. "帮我生成一张手机发展史的信息图" (Chinese), "Make an infographic about smartphone history" (English), "スマホの歴史のインフォグラフィックを作って" (Japanese) — all are incomplete. The agent MUST propose a content plan and wait for user confirmation before calling create.

```
Information-complete = all of the following are met:
  1. Has clear content body (at least 3+ specific knowledge points/paragraphs/data, not a one-line summary)
  2. User has confirmed content and style (or explicitly said "you decide" / "whatever" / "just do it" / "你来定" / "随便" / "直接做")

Typical incomplete examples (must NOT create directly):
  ❌ "Make an infographic about the history of AI"  → Only a topic, no specific content
  ❌ "Create a blockchain diagram"                  → Only a topic word
  ❌ "Generate an infographic about healthy eating"  → One-line request
  ❌ "Make a Python learning roadmap"               → Topic + direction, but no specific content
  Chinese equivalents (same rule applies):
  ❌ "做一张人工智能发展史的信息图"  → 只有主题，没有具体内容
  ❌ "帮我做个区块链图解"            → 只有主题词
  ❌ "生成一张关于健康饮食的信息图"    → 一句话需求
  ❌ "做张Python学习路线图"           → 主题+方向，但无具体内容

Complete examples (can create directly):
  ✅ User pasted a complete article + "turn this into an infographic"
  ✅ User provided detailed content outline (3+ sections with key points for each)
  ✅ Previous turn Agent proposed content plan, user replied "looks good" / "go ahead"
  Chinese equivalents:
  ✅ 用户贴了一篇完整文章 + "把这篇转成信息图"
  ✅ 用户给了详细的内容大纲（3个以上板块+每个板块的要点）
  ✅ 上一轮 Agent 提出了内容规划，用户回复"可以"/"就这样做"

When information-complete: First send user a message via message send saying "Generating now, please wait",
            after send returns, call create in the next turn.
```

**When information is incomplete, must first reply with a planning message:**
- Include 2-3 content section suggestions (specific to key points for each section)
- **Must include template gallery link** (select the matching `?lang=` parameter based on user's language, see "Template Gallery" section), guiding user to browse styles
- Wait for user confirmation before calling create
- Complete in one message, don't ask across multiple turns

**Batch (count >= 2, information incomplete):** First plan quantity, style consistency, sub-topic division, then pass complete content via `--article` after user confirms.

**Batch `--child-reference-type` selection rule:**
- `content_rewrite` (default for batch): User wants a coherent series with unified/consistent style (e.g. "统一风格", "连贯的", "series", "consistent look", "like a PPT deck"). The first infographic becomes the layout template, subsequent ones rewrite content while preserving visual consistency. **When in doubt, use `content_rewrite`.**
- `style_transfer`: User provides a specific external reference image and says "use this style for all N infographics". Only applies when there is an uploaded reference image to transfer style from — NOT for maintaining consistency within a batch.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel <channel> --mode article \
  --article "<complete content with detailed text for each chapter>" \
  --count 5 --style-hint "classical hand-drawn" --child-reference-type content_rewrite
```

Usually 1-2 turns to complete planning, don't over-ask.

## Error Handling

In the JSON returned by create, `success` and `status` fields mean:

| Return Value | Meaning | Agent Must Do |
|-------------|---------|--------------|
| `"success": false, "status": 4` | **Task failed** (backend processing error) | Stop immediately, inform user "task failed", must NOT retry |
| `"success": false, "status": 5` | **Task timeout** (backend processing timeout) | Stop immediately, inform user "task timed out" |
| `"success": false, "status": 6` | **Task cancelled** | Stop immediately, inform user |
| `"success": false, "status": "timeout"` | **Local wait timeout** (script poll timeout) | Inform user task is still processing, can retry later |
| `"success": false` (other) | API call failed | Inform user of error reason |

**status=4 is a definitive failure, not a timeout, not a content issue, do not misjudge.**

Error codes see [references/error-codes.md](references/error-codes.md).

### Automatic Retry Strictly Prohibited

After create returns `"success": false`:
1. **Do NOT** automatically switch content, style, parameters, or simplify content and re-call create
2. **Do NOT** misjudge status=4 (failure) as timeout or content issue
3. Must stop immediately and inform user of the failure as-is
4. Only retry when user explicitly says "try again", and max 2 task creations per conversation
5. Each create deducts credits (200 credits), blind retries directly waste user's money
