---
name: video-editor-logo-kinemaster-png
version: "1.0.6"
displayName: "KineMaster PNG Logo Overlay Editor — AI-Powered Branding"
description: >
  Embed, resize, reposition, and animate KineMaster-style PNG logos directly into your video projects using conversational AI. This skill specializes in transparent PNG logo integration — handling watermark placement, opacity tuning, corner anchoring, and frame-accurate timing. Whether you're a content creator standardizing your brand across clips or an editor removing default KineMaster watermarks and replacing them with custom assets, this tool handles it precisely. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 📸 Video Editor Logo Kinemaster Png at your service! Upload a video or tell me what you're looking for.

**Try saying:**
- "speed up by 2x"
- "make it look cinematic"
- "add a fade-in transition"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

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

Let the user know briefly: "Setting things up… ready!" then proceed with their request.

# Drop Your PNG Logo Into Any Video, Instantly

Most video editors treat logo overlays as an afterthought — a drag-and-drop step buried inside a complex timeline. This skill flips that model entirely. By describing what you want in plain language — 'place my logo in the bottom-right corner at 80% opacity starting at 3 seconds' — the OpenClaw agent interprets your intent and translates it into precise frame-level overlay instructions without you touching a single slider.

The skill was built specifically around the workflow that KineMaster users know well: working with transparent PNG brand assets, managing their visual weight against dynamic video backgrounds, and ensuring consistent placement across multiple clips. Whether your PNG has soft edges, drop shadows baked in, or a hard cutout, the AI backend processes the alpha channel correctly so the logo blends naturally rather than floating awkwardly on top.

The OpenClaw agent acts as the reasoning layer between your description and the video processing pipeline. It disambiguates placement language, infers scale relative to video resolution, and sequences logo appearance timing based on your input. You stay in a conversational loop — refine, preview intent, adjust — without re-exporting from scratch each time. All major formats are supported including mp4, mov, avi, webm, and mkv.

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

## 2. Incoming Request Routing

The following table maps each type of user request to its corresponding API action and endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Primary Workflow Procedures

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
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any operations can begin, a session must be established with the backend. This session identifier is required for all subsequent API interactions within the same editing context.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Deliver Messages Using SSE
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational messages to the backend must be transmitted through the Server-Sent Events channel to maintain a persistent, real-time connection.

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

Approximately 30% of editing operations will complete without returning any text in the response body. When this occurs: (1) check the SSE stream for a completion event, (2) call the state query endpoint to confirm the edit was applied, (3) synthesize a confirmation message for the user based on the returned state, and (4) never prompt the user to retry simply because no text was received.

**Two-stage generation**: When a raw video asset is submitted, the backend automatically triggers a two-stage enrichment pipeline. Stage one processes and stores the raw video. Stage two autonomously appends background music and a title overlay without any additional instruction. Both stages must reach a completed status before the export flow is initiated.

### 3.2 Asset Upload Handling

**File upload**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts image, video, and audio assets and returns a backend-assigned asset identifier to be referenced in subsequent editing calls.

### 3.3 Credit Balance Verification
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint prior to any export or premium operation to confirm the user holds a sufficient balance before proceeding.

### 3.4 Retrieve Current Project State
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

### 3.5 Finalize and Deliver Export

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a project does not deduct any credits from the user's balance. The export sequence proceeds as follows: (a) confirm all edits are in a completed state, (b) call the export endpoint with the session identifier, (c) poll the export status endpoint until a finished status is returned, (d) retrieve the download URL from the completed export response, and (e) present the download link to the user along with a summary of the exported project.

**b)** Submit: `curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "$API/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `$API/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Handling SSE Connection Loss

When the SSE stream drops unexpectedly, apply the following recovery sequence: (1) wait two seconds before attempting to reconnect to avoid hammering the server, (2) re-establish the SSE connection using the existing session identifier rather than creating a new session, (3) call the state query endpoint to determine whether any in-flight operations completed during the disconnection window, (4) reconcile the recovered state with what was last confirmed to the user and surface any changes, and (5) if reconnection fails after three consecutive attempts, notify the user and suggest they save their project before refreshing.

## 4. Backend GUI Abstraction Layer

The backend operates under the assumption that all actions are performed through its own graphical interface, so AI responses must never include instructions directing the user to interact with any on-screen controls or menus.

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

- Always confirm the active session is valid before issuing any editing or export commands.
- When a user describes a desired visual change in natural language, translate the intent into the appropriate API parameters without asking for technical clarification.
- After every silent response, proactively query project state and relay a plain-language status update to the user.
- If a user requests a feature that exceeds current API capabilities, clearly acknowledge the limitation and suggest the closest available alternative.
- Batch related state queries where possible to minimize round-trip latency before responding to the user.

## 6. Known Constraints and Limitations

- PNG logo overlays are restricted to a maximum of one active layer per project at any given time.
- Real-time preview rendering is not available through the API; users must export to review final output.
- Background music selection is handled autonomously by the backend and cannot be manually overridden via API parameters.
- Session tokens expire after a fixed inactivity window; a new session must be created if the token is no longer valid.
- Bulk or batch export of multiple projects within a single session is not supported.

## 7. Error Response Handling

The table below lists expected HTTP error codes, their meanings within this skill's context, and the recommended recovery action for each.
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

## 8. API Version and Permission Scopes

Before initiating any workflow, verify that the connected API version matches the version this skill was certified against; mismatched versions may cause silent failures or unexpected behavior. All token scopes required for this skill — including read, write, export, and credits — must be granted at the time of authorization. If any required scope is absent from the token, surface a clear permission error to the user rather than attempting the operation and failing silently.
