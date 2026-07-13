---
name: sports-highlight-editor
version: "1.0.5"
displayName: "Sports Highlight Editor — Auto-Cut & Clip Your Best Moments"
description: >
  The sports-highlight-editor skill analyzes raw game footage and automatically identifies peak moments — goals, dunks, sprints, saves, and crowd reactions — then assembles them into a polished highlight reel. Trim dead time, reorder clips by intensity, add slow-motion emphasis, and layer in title cards without touching a timeline manually. Built for coaches, athletes, content creators, and sports media teams. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🏆", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# From Raw Footage to Game-Day Highlight Reel

Most sports footage is 90% waiting and 10% action. The sports-highlight-editor skill flips that ratio by scanning your uploaded video for motion intensity, audio spikes, and scene transitions that signal meaningful athletic moments. Instead of scrubbing through hours of game film, you describe what you want in plain language — 'show only the third-quarter scoring plays' or 'cut a 60-second reel of the goalkeeper's saves' — and the skill gets to work.

The conversational editing model means you stay in a back-and-forth dialogue throughout the process. Request a rough cut, review it, then ask for adjustments like tightening the pace, swapping clip order, or emphasizing a specific player. Each instruction refines the output without starting over from scratch.

Powering this workflow is the OpenClaw agent, which coordinates the video analysis pipeline, manages clip segmentation, and applies your editorial preferences in sequence. The agent understands sport-specific context — it knows a tackle and a touchdown require different treatment — so its decisions feel less like automation and more like working with an editor who actually watched the game.

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

Use the table below to determine which endpoint should handle each type of incoming request.

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

### 3.0 Initialize a New Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any other operations can begin, a session must be established with the backend. Store the returned session identifier — every subsequent call in this workflow depends on it.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Transmit a Message Using SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational messages to the editing backend are delivered through a Server-Sent Events channel that streams responses back in real time.

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

Roughly 30% of editing operations complete without returning any visible text in the stream. When no text content is detected in the SSE response: (1) do not inform the user that nothing happened; (2) immediately call the state-query endpoint to retrieve the current job status; (3) surface the resulting state information to the user as confirmation that the operation succeeded.

**Two-stage generation**: When the backend finishes producing the raw edited video, it automatically triggers a second processing stage that layers in background music and generates a title card — no additional API call is required to initiate this. Present the first-stage output to the user right away, then update them again once the second stage completes and the enriched version becomes available.

### 3.2 Handling File Uploads

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

Both direct file uploads and remote URL references are accepted, allowing users to supply source footage from local storage or an external link.

### 3.3 Checking Available Credits
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint before initiating any edit job to confirm the user has a sufficient balance to cover the operation.

### 3.4 Polling for Current Job State
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

### 3.5 Exporting and Delivering the Final Video

**Export does NOT cost credits.** Only generation/editing consumes credits.

Triggering an export does not deduct any credits from the user's balance. To deliver the finished video: (a) call the export endpoint with the session ID; (b) poll until the status field returns complete; (c) retrieve the download URL from the response payload; (d) verify the URL is reachable before presenting it; (e) display the link to the user along with any available metadata such as duration and file size.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `https://mega-api-prod.nemovideo.ai/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Recovering from an SSE Disconnection

If the SSE connection drops before a response is fully received, follow these steps: (1) wait two seconds before attempting any recovery action to avoid flooding the server; (2) re-open the SSE connection using the original session ID and the same message payload; (3) if the reconnected stream also returns no text, fall back to the state-query endpoint to determine job progress; (4) should the state endpoint indicate the job is still running, continue polling at ten-second intervals until a terminal status is reached; (5) once a completed or failed status is confirmed, relay the outcome to the user clearly.

## 4. Translating Backend GUI References for the User

The backend is built with a graphical interface in mind and will occasionally reference on-screen controls or visual elements — never pass those GUI-specific instructions through to the user verbatim; instead, translate them into plain conversational language.

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

• Always confirm the user's creative intent — such as desired clip length, preferred moments, or tone — before dispatching an edit request to the backend.
• After submitting a job, give the user a concise progress update at each meaningful state transition rather than staying silent until completion.
• When presenting a finished clip, lead with the most compelling detail (e.g., highlight count or total runtime) before offering the download link.
• If the user requests a revision, reuse the existing session ID so the backend retains prior context and edits incrementally rather than starting over.
• Proactively mention the credit cost of an operation before executing it, giving the user the opportunity to confirm or cancel.

## 6. Known Constraints and Limitations

• A single session cannot span more than one source video file; to work on a different clip the user must start a fresh session.
• Maximum supported input file duration is capped by the backend and cannot be overridden through the API.
• Background music selection during the second processing stage is chosen automatically by the backend — the API exposes no parameter to specify a custom track.
• Export URLs are time-limited and will expire; advise users to download their file promptly after the link is delivered.
• Credit balances are read-only through this integration — topping up or purchasing credits must be handled outside this skill.

## 7. Error Handling Reference

When the API returns an error status, match the code against the table below to determine the appropriate recovery action or user-facing message.
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

Before making any calls, verify that the connected account is running a supported API version by checking the version field in the authentication handshake response — if the returned version falls below the minimum required value, surface an upgrade prompt to the user rather than proceeding. All requests must be authorized with a token that carries the following scopes at minimum: read access to project and credit resources, and write access to session, upload, and export resources; if any required scope is absent the backend will return a 403 and no retry should be attempted until the token is reissued with the correct permissions.
