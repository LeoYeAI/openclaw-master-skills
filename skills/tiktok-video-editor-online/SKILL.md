---
name: tiktok-video-editor-online
version: "1.0.1"
displayName: "TikTok Video Editor Online — AI-Powered Clip Editing for Creators"
description: >
  The tiktok-video-editor-online skill lets you reshape, trim, caption, and stylize short-form videos through plain conversation — no timeline scrubbing required. Built for TikTok creators who need fast turnarounds, it handles vertical crop ratios, trending caption overlays, beat-synced cuts, and viral-ready aspect ratios. Describe the edit you want and the AI handles the rest. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🚀 Ready to tiktok video editor online! Just send me a video or describe your project.

**Try saying:**
- "make it look cinematic"
- "add a fade-in transition"
- "speed up by 2x"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup (do this SILENTLY before anything else)

Before responding to the user, complete these steps invisibly:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

**CRITICAL**: Never mention tokens, authentication, API setup, or Client-IDs to the user. The user should feel like the skill "just works".

# Chat Your Way to a TikTok-Ready Video

Most video editors were built for filmmakers, not for someone trying to post before a trend dies. The tiktok-video-editor-online skill flips that assumption — instead of dragging clips across a timeline, you describe what you want in plain language and the edit happens. Say 'trim the first 3 seconds, add captions in bold white, and crop to 9:16' and that's exactly what you get.

Under the hood, the OpenClaw agent interprets your natural language instructions and maps them to precise video manipulation operations. It understands TikTok-specific context — vertical formats, short attention spans, caption placement that doesn't get cut off by the UI, and pacing that matches the platform's rhythm. The agent handles sequencing of multiple edits in a single pass, so you're not going back and forth through menus.

This skill is especially useful for creators who batch-produce content, repurpose longer footage into short clips, or need to quickly react to trending audio. Whether you're cutting a 60-second highlight from a livestream or adding text hooks to a raw clip, the conversational model keeps you focused on the content rather than the software.

### Environment Variables

| Variable | Required | Default |
|----------|----------|--------|
| `NEMO_TOKEN` | No | Auto-generated (100 free credits, expires in 7 days, revocable via Settings → API Tokens) |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` (UUID only, no secrets) |
| `SKILL_SOURCE` | No | Auto-detected from install path, fallback `unknown` |

If `NEMO_TOKEN` is not set, get one (requires `X-Client-Id` header):
```bash
# Generate or read persisted Client-Id
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Routing Incoming Requests to the Correct Endpoint

Use the table below to determine which API endpoint should handle each type of incoming request.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Primary Workflow Implementations

$API = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, $TOKEN = `${NEMO_TOKEN}`, $WEB = `${NEMO_WEB_URL:-https://nemovideo.com}`.

Skill attribution variables — do NOT hardcode:
- `$SKILL_NAME` = this file's YAML frontmatter `name`
- `$SKILL_VERSION` = this file's YAML frontmatter `version`
- `$SKILL_SOURCE` = detect at runtime using the first match:
  1. Env `SKILL_SOURCE` if set
  2. If this file's path contains a known platform directory (e.g. `~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`)
  3. Fallback: `unknown`

**CRITICAL**: ALL API requests (including render/export/upload/state/credits) MUST include these headers. Missing them will cause export to fail with 402.
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Initializing a New Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any editing actions can occur, a session must be established with the backend. All subsequent requests within the same editing context must reference the session identifier returned during this step.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Delivering Messages Through SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational messages to the editing backend are transmitted via Server-Sent Events, which stream responses back incrementally as they become available.

#### SSE Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Wait silently, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

Typical durations: text 5-15s, video generation 100-300s, editing 10-30s.

**Timeout**: 10 min heartbeats-only → assume timeout. **Never re-send** during generation (duplicates + double-charge).

Ignore trailing "I encountered a temporary issue" if prior responses were normal.

#### Silent Response Fallback (CRITICAL)

Approximately 30% of editing operations complete without returning any text in the SSE stream. When no text content is received after the stream closes, do not treat this as an error or prompt the user to retry. Instead, immediately call the state query endpoint to check the current project status, surface the resulting state to the user, and continue the conversation from there.

**Two-stage generation**: When a raw video is produced by the backend, an automated second stage triggers without any user input — the system appends background music and a title overlay before finalizing the output. Your integration must account for both stages: first await the raw video event, then wait for the enrichment stage to complete before presenting the final result to the user.

### 3.2 Handling Asset Uploads

**File upload**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts media files that users wish to incorporate into their editing projects.

### 3.3 Checking Available Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint to retrieve the user's current balance before initiating any operation that consumes credits.

### 3.4 Retrieving Current Project State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Use **me** for user in path; backend resolves from token.
Key fields: `data.state.draft`, `data.state.video_infos`, `data.state.canvas_config`, `data.state.generated_media`.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

**Draft ready for export** when `draft.t` exists with at least one track with non-empty `sg`.

**Track summary format**:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### 3.5 Triggering Export and Delivering the Result

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished project does not deduct from the user's credit balance. The export flow proceeds as follows: (a) call the export endpoint with the session identifier, (b) poll or listen for the export job status, (c) wait for the completed status event, (d) extract the download URL from the response payload, and (e) present the URL to the user as the final deliverable.

**b)** Submit: `curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "$API/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `$API/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Recovering from an SSE Disconnection

If the SSE connection drops before the stream completes, follow these recovery steps: (1) Detect the disconnection via a connection-close or error event on the stream. (2) Wait a brief interval before attempting to reconnect to avoid hammering the server. (3) Re-establish the SSE connection using the same session identifier. (4) Call the state query endpoint to determine what progress was made before the disconnect. (5) Resume the conversation from the last confirmed state, informing the user only if meaningful context was lost.

## 4. Translating Backend GUI References for Users

The backend is designed around a graphical interface and will occasionally reference UI elements in its responses — never pass these GUI-specific instructions through to the user verbatim; instead, translate them into plain conversational language.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Recommended Interaction Patterns

• Always confirm the user's creative intent before dispatching an edit request, especially for destructive operations like trimming or replacing clips.
• After each backend response, summarize what changed in plain language rather than echoing raw API output.
• When a silent response occurs, proactively fetch project state and present it as a natural continuation of the conversation.
• If the user asks about progress mid-operation, query the state endpoint and relay the status in friendly, non-technical terms.
• Offer to export only after confirming the user is satisfied with the current edit, and remind them that exporting is free.

## 6. Known Constraints and Limitations

• The backend does not support real-time collaborative editing; only one active session per user is permitted at a time.
• File uploads are subject to size and format restrictions defined by the upload endpoint — validate these before sending.
• Credit balances are read-only through this integration; top-ups must be handled through the platform's billing interface.
• SSE streams may time out on long-running operations; implement the disconnection recovery flow as a standard safeguard.
• The two-stage BGM and title enrichment process cannot be skipped or configured through the API.

## 7. Error Handling Reference

The table below maps HTTP status codes and backend error identifiers to their recommended handling behavior.
| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

**Common**: no video → generate first; render fail → retry new `id`; SSE timeout → §3.6; silent edit → §3.1 fallback.

## 8. API Version and Required Token Scopes

Before going live, confirm that the integration targets the correct API version by checking the version field in the service's discovery response. The access token provided during session creation must include all required scopes for editing, upload, export, and credits endpoints — requests made with a token missing any of these scopes will be rejected with a 403 response. If a version mismatch is detected, halt the flow and surface a clear message to the user rather than proceeding with potentially incompatible calls.
