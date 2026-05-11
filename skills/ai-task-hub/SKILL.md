---
name: ai-task-hub
description: AI task hub for image analysis, background removal, speech-to-text, text-to-speech, markdown conversion, and async execute/poll/presentation orchestration. Use when users need hosted AI outcomes while host runtime manages identity, credits, payment, and risk control.
version: 3.1.4
metadata:
  openclaw:
    skillKey: ai-task-hub
    emoji: "🧩"
    homepage: https://gateway.binaryworks.app
    requires:
      bins:
        - node
      env:
        - AGENT_TASK_TOKEN
    primaryEnv: AGENT_TASK_TOKEN
---

# AI Task Hub

Formerly `skill-hub-gateway`.

Public package boundary:

- Only orchestrates `portal.skill.execute`, `portal.skill.poll`, and `portal.skill.presentation`.
- Does not exchange `api_key` or `userToken` inside this package.
- Does not handle recharge or payment flows inside this package.
- Assumes host runtime injects short-lived task tokens and attachment URLs.

Chinese documentation: `SKILL.zh-CN.md`

## When to Use This Skill

Use this skill when the user asks to:

- detect people, faces, hands, keypoints, or tags from images
- remove backgrounds or generate cutout/matting results for products or portraits
- transcribe uploaded audio into text (`speech to text`, `audio transcription`)
- generate speech from text input (`text to speech`, `voice generation`)
- convert uploaded files into markdown (`document to markdown`)
- start async jobs and check status later (`poll`, `check job status`)
- fetch rendered visual outputs such as `overlay`, `mask`, and `cutout`
- run embedding or reranking tasks for retrieval workflows

## Common Requests

Example requests that should trigger this skill:

- "Detect faces in this image and return bounding boxes."
- "Tag this image and summarize the main objects."
- "Remove the background from this product photo."
- "Create a clean cutout from this portrait image."
- "Transcribe this meeting audio into text."
- "Generate speech from this paragraph."
- "Convert this PDF file into markdown."
- "Start this job now and let me poll the run status later."
- "Fetch overlay and mask files for run_456."
- "Generate embeddings for this text list and rerank the candidates."

## Search-Friendly Capability Aliases

- `vision` aliases: face detection, human detection, person detection, image tagging
- `background` aliases: remove background, background removal, cutout, matting, product-cutout
- `asr` aliases: speech to text, audio transcription, transcribe audio
- `tts` aliases: text to speech, voice generation, speech synthesis
- `markdown_convert` aliases: document to markdown, file to markdown, markdown conversion
- `poll` aliases: check job status, poll long-running task, async run status
- `presentation` aliases: rendered output, overlay, mask, cutout files
- `embeddings/reranker` aliases: vectorization, semantic vectors, relevance reranking

## Runtime Contract

Default API base URL: `https://gateway-api.binaryworks.app`

Action to endpoint mapping:

- `portal.skill.execute` -> `POST /agent/skill/execute`
- `portal.skill.poll` -> `GET /agent/skill/runs/:run_id`
- `portal.skill.presentation` -> `GET /agent/skill/runs/:run_id/presentation`

## Auth Contract (Host-Managed)

Every request must include:

- `X-Agent-Task-Token: <jwt_or_paseto>`

Recommended token claims:

- `sub` (user_id)
- `agent_uid`
- `conversation_id`
- `scope` (`execute|poll|presentation`)
- `exp`
- `jti`

CLI argument order for `scripts/skill.mjs`:

- `[agent_task_token] <action> <payload_json> [base_url]`
- If token arg is omitted, script reads `AGENT_TASK_TOKEN` from environment.
- Host runtime should refresh and inject short-lived `AGENT_TASK_TOKEN` automatically to avoid user-facing auth friction.

## Payload Contract

- `portal.skill.execute`: payload requires `capability` and `input`.
- `payload.request_id` is optional and passed through.
- `portal.skill.poll` and `portal.skill.presentation`: payload requires `run_id`.
- `portal.skill.presentation` supports `include_files` (defaults to `true`).

Attachment normalization:

- Prefer explicit `image_url` / `audio_url` / `file_url`.
- `attachment.url` is mapped to target media field by capability.
- Local `file_path` is disabled in the published package.
- Host must upload chat attachments first, then pass URL fields.
- Example host upload endpoint: `/api/blob/upload-file`.

## Error Contract

- Preserve gateway envelope: `request_id`, `data`, `error`.
- Preserve `POINTS_INSUFFICIENT` and pass through `error.details.recharge_url`.

## Bundled Files

- `scripts/skill.mjs`
- `scripts/agent-task-auth.mjs`
- `scripts/base-url.mjs`
- `scripts/attachment-normalize.mjs`
- `scripts/telemetry.mjs` (compatibility shim)
- `references/capabilities.json`
- `references/openapi.json`
- `SKILL.zh-CN.md`
