---
name: best-tiktok-video-editor
version: "1.0.5"
displayName: "Best TikTok Video Editor — AI-Powered Clips That Go Viral"
description: >
  The best-tiktok-video-editor skill on ClawHub transforms raw footage into scroll-stopping TikTok content through a simple back-and-forth conversation. Trim dead air, add captions, apply trending transitions, adjust aspect ratios to 9:16, and punch up color grading — all by describing what you want in plain language. Built for creators, agencies, and social media managers who need fast turnaround without a steep learning curve. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ✨ Let's best tiktok video editor! Drop a video here or describe what you'd like to create.

**Try saying:**
- "make it look cinematic"
- "add a fade-in transition"
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

# Chat Your Way to a Polished TikTok Cut

Most TikTok creators lose hours wrestling with timelines, export settings, and effect libraries before a single clip goes live. This skill flips that workflow entirely — you describe the edit you want in plain language, and the AI handles the technical execution behind the scenes.

The conversational editing model means you stay in a dialogue throughout the process. Say 'cut the first three seconds, add a zoom punch on the beat drop, and caption the hook' and the OpenClaw agent interprets your intent, sequences the operations in the correct order, and returns a preview-ready result. The OpenClaw agent acts as the reasoning layer between your natural language instructions and the low-level video processing pipeline, resolving ambiguities by asking short clarifying questions rather than guessing wrong.

Under the hood, the AI backend analyzes audio waveforms to detect beats for sync cuts, scans spoken dialogue for auto-caption placement, and evaluates frame composition when applying crop or reframe operations for TikTok's 9:16 canvas. The result is an edit that feels intentional rather than automated — because every decision traces back to something you actually said.

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

## 2. Routing Incoming Requests to the Correct Endpoint

Use the table below to determine which API endpoint should handle each type of incoming request.

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

### 3.0 Initializing a New Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any editing work can begin, a session must be established with the backend. This session identifier is required for all subsequent requests within the same editing context.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Delivering Messages Over SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational messages to the editing backend are transmitted through a persistent Server-Sent Events connection.

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

Approximately 30% of editing operations complete without returning any text in the response. When no text content is detected in the SSE stream, do not treat this as an error or prompt the user to retry. Instead, immediately poll the session state endpoint to retrieve the current project status and surface the result to the user from that data.

**Two-stage generation**: When a raw video output is produced, the backend automatically triggers a second processing stage that layers in background music and generates a title overlay — no additional instruction is needed. Always wait for both stages to finish before presenting the final result to the user.

### 3.2 Handling Asset Uploads

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Both video files and image assets can be submitted to the backend using the designated upload endpoint.

### 3.3 Checking Available Credits
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint prior to initiating any edit operation to confirm the user has a sufficient balance.

### 3.4 Retrieving Current Project State
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

### 3.5 Triggering Export and Delivering the Output

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished project does not deduct from the user's credit balance. To deliver the final video: (a) call the export endpoint with the session ID, (b) poll for export completion status, (c) retrieve the download URL from the completed export object, (d) verify the URL is accessible, and (e) present the link or embed the video for the user.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `https://mega-api-prod.nemovideo.ai/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Recovering from an SSE Disconnection

If the SSE connection drops unexpectedly, follow these steps to recover: (1) detect the disconnection event and log the last received event ID; (2) wait a brief interval before attempting to reconnect to avoid hammering the server; (3) re-establish the SSE connection, supplying the last event ID in the reconnect header so the stream can resume from where it left off; (4) if the reconnect attempt fails after the maximum number of retries, fall back to polling the session state endpoint directly; (5) once continuity is restored, notify the user only if meaningful progress was missed during the gap.

## 4. Translating GUI Elements for the Backend

The backend operates under the assumption that a graphical interface is present, so GUI-specific instructions must always be converted to API calls and never forwarded as-is.

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

• Confirm the user's creative intent before dispatching any editing request, reducing unnecessary credit consumption.
• After each SSE stream closes, proactively check project state rather than waiting for the user to ask for an update.
• When presenting export results, include both the direct download link and a brief summary of what was produced.
• If a user requests a change that would overwrite existing work, briefly summarize what will be replaced before proceeding.
• For multi-step edits, break the workflow into discrete checkpoints and confirm with the user before advancing to the next stage.

## 6. Known Limitations

• The AI cannot preview video frames or analyze visual content directly; it relies entirely on metadata and user descriptions.
• Session state is not persisted across disconnected sessions — a new session must be created if the original is lost.
• Credit balance is read-only through the API; top-ups must be handled outside this skill.
• Concurrent editing sessions for the same user account may produce unpredictable state conflicts and should be avoided.
• Background music selection during the auto-stage is determined by the backend and cannot be overridden through the current API.

## 7. Error Identification and Handling

Refer to the table below to map each HTTP status or error code to its cause and the appropriate recovery action.
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

Always verify the API version header matches the supported version before making calls, as mismatched versions may result in unexpected behavior or rejected requests. The access token provided during session initialization must include all required scopes for editing, uploading, and exporting; if any scope is missing, request re-authorization from the user before proceeding.
