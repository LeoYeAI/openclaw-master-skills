---
name: video-editor-ai
version: "1.0.10"
displayName: "Video Editor AI — Smart Editing Powered by Conversational AI"
description: "A powerful AI video editor that transforms how you edit videos — just describe what you want in plain language. Trim clips, merge sequences, adjust pacing, apply filters, and extract segments through natural conversation. Built for content creators, marketers, and educators. Supports mp4, mov, avi, webm, and mkv."
  video-editor-ai is a ClawHub skill that lets you edit video files through natural conversation instead of complex timelines or manual controls. Trim clips, merge sequences, adjust pacing, apply filters, and extract segments — all by describing what you want in plain language. Designed for content creators, marketers, educators, and developers who need fast, repeatable video workflows without steep learning curves. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎙️ Hey! I'm ready to help you video editor ai. Send me a video file or just tell me what you need!

**Try saying:**
- "add a fade-in transition"
- "make it look cinematic"
- "speed up by 2x"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.

# Edit Video by Talking, Not Clicking

Most video editing tools put the burden of execution on you — drag this clip, find this timestamp, apply this effect. video-editor-ai flips that model entirely. You describe the outcome you want, and the skill figures out how to produce it. Whether you need the first 30 seconds trimmed, two clips joined with a crossfade, or a specific scene extracted from a longer recording, you express the intent and the system handles the mechanics.

Under the hood, the OpenClaw agent interprets your editing instructions and translates them into precise, ordered operations applied directly to your video file. The agent maintains context across a conversation, meaning you can refine, undo, or chain multiple edits in a single session without starting over. It understands relative language — 'cut the slow part near the middle' or 'keep only the section where the presenter is speaking' — and resolves those instructions against the actual file structure.

This skill is purpose-built for people who work with video frequently but don't want to invest time in traditional editing software for routine tasks. Batch processing, scripted workflows, and repeatable edit patterns are all within reach. Input files can be provided in mp4, mov, avi, webm, or mkv formats, giving you flexibility regardless of your recording setup or source platform.

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
  mkdir -p ~/.config/nemovideo & echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Routing Incoming Requests

Use the table below to determine which endpoint should handle each type of user request.

| User says... | Action | Skip SSE |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Primary Workflow Sequences

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

### 3.0 Initialize a Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any editing work can begin, a session must be established. This session ID ties all subsequent requests together for the duration of the editing task.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Transmit Messages via SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational editing instructions are delivered to the backend through a Server-Sent Events connection.

#### SSE Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

Typical durations: text 5-15s, video generation 100-300s, editing 10-30s.

**Timeout**: 10 min heartbeats-only → assume timeout. **Never re-send** during generation (duplicates + double-charge).

Ignore trailing "I encountered a temporary issue" if prior responses were normal.

#### Silent Response Fallback (CRITICAL)

Approximately 30% of editing operations complete without returning any text in the SSE stream. When no text response is detected, do not treat this as a failure. Instead: (1) wait for the stream to close cleanly, (2) immediately call the state query endpoint to retrieve the current project status, (3) surface the updated state to the user as confirmation that the operation succeeded, and (4) continue the conversation normally.

**Two-stage generation**: When the backend delivers a raw video result, it automatically triggers a second processing stage that appends background music and generates a title overlay — no additional instruction from the AI is needed. Present the first-stage output to the user, then monitor the stream for the second-stage completion event before surfacing the final enriched result.

### 3.2 Asset Upload

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Both video and image file uploads are supported through the designated upload endpoint.

### 3.3 Credit Balance
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint to retrieve the user's current available balance before initiating any credit-consuming operation.

### 3.4 Retrieve Project State
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
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

### 3.5 Export and Deliver Final Output

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished project does not deduct any credits from the user's balance. To complete an export: (a) confirm the project is in a finalized state, (b) call the export endpoint with the session ID, (c) await the export job completion event on the SSE stream, (d) retrieve the download URL from the response payload, and (e) present the URL to the user for download or sharing.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `https://mega-api-prod.nemovideo.ai/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Handling SSE Disconnections

If the SSE connection drops unexpectedly, follow these recovery steps: (1) detect the disconnection through a stream error or timeout event, (2) wait a minimum of two seconds before attempting to reconnect to avoid hammering the server, (3) re-establish the SSE connection using the original session ID, (4) call the state query endpoint to reconcile any events that may have been missed during the outage, and (5) resume normal message handling once the current project state has been confirmed.

## 4. Mapping Backend Responses to the User Interface

The backend operates under the assumption that a graphical interface is present, so the AI must never relay raw GUI-specific instructions or interface directives directly to the user.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Recommended Conversational Approaches

- Acknowledge each user request before dispatching it to the backend, so the user knows their instruction was understood.
- After a silent response, proactively query project state and report back rather than waiting for the user to ask what happened.
- Break multi-step editing tasks into clearly communicated stages so the user can follow progress.
- When a credit-consuming action is requested, confirm the available balance first and flag any potential shortfall before proceeding.
- Summarize completed changes in plain language after each successful operation instead of echoing raw API response data.

## 6. Known Constraints and Limitations

- The AI cannot directly manipulate the video timeline; all edits must be submitted as natural-language instructions through the SSE message flow.
- Real-time preview streaming is not available; users must wait for a processing stage to complete before reviewing output.
- A single session supports one active editing job at a time — concurrent operations within the same session are not permitted.
- File uploads are subject to size and format restrictions enforced by the upload endpoint; the AI cannot override these limits.
- Credit balances are read-only from the AI's perspective; adjustments or refunds must be handled through the platform's billing interface.

## 7. Error Recognition and Response

The table below maps common HTTP status codes and error identifiers to their causes and the appropriate recovery actions.
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

Before initiating any session, verify that the API version returned by the version check endpoint matches the version this skill was built against. Token scopes must include read and write permissions for projects, plus read access for credits. If a required scope is missing, surface a clear authorization error to the user rather than proceeding with a request that will be rejected.
