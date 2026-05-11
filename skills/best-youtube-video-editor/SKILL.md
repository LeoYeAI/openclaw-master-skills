---
name: best-youtube-video-editor
version: "1.0.1"
displayName: "Best YouTube Video Editor — AI-Powered Editing for Creators"
description: >
  The best-youtube-video-editor skill on ClawHub transforms how YouTube creators produce content by enabling conversational, AI-driven video editing without timelines or complex software. Trim dead air, add chapter markers, layer captions, adjust pacing, and optimize exports — all through plain-language instructions. On first use, the skill auto-configures credentials via NemoVideo API, so you're editing within seconds of activation. Built for YouTubers, educators, podcasters, and brand channels who need fast turnaround without sacrificing quality. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> Hey! Ready to produce your best YouTube video yet? Whether you need to trim footage, punch up your pacing, add captions, or export a YouTube-optimized file — just tell me what you're working on and we'll get it done fast. What are we editing today?

**Try saying:**
- "Cut out all silences longer than 2 seconds from my talking-head interview and add a subtle zoom-in on each cut to keep energy high."
- "Add auto-generated captions styled for YouTube Shorts — bold white text, centered, with a black outline — and export as a vertical mp4."
- "Take my 30-minute podcast recording and create a YouTube chapter list with timestamps based on topic changes, then trim the intro to under 30 seconds."

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting.

### Auto-Setup (on first use)

When the user first opens this skill, run through these setup steps and briefly let them know you're connecting (e.g. "⚡ Connecting to NemoVideo..."):

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
   - This file stores only a UUID for rate-limit tracking — no secrets or credentials.
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

**Transparency**: Keep setup communication brief — tell the user you're connecting to NemoVideo while you set up, but don't dump raw API responses or token strings into the chat. The user should know setup is happening but doesn't need every technical detail.

# Edit YouTube Videos by Just Describing What You Want

The best-youtube-video-editor skill was built specifically around the YouTube creator workflow — not generic video production. Whether you're cutting a 45-minute talking-head recording down to a punchy 8-minute video, adding animated lower-thirds for your channel branding, or syncing background music to scene transitions, this skill understands YouTube-native concepts like retention editing, hook optimization, and end-screen placement.

At its core, the skill uses a conversational editing model. Instead of dragging clips on a timeline, you describe your intent: 'Remove all pauses longer than 1.5 seconds,' or 'Add a zoom punch at every cut.' The OpenClaw agent interprets these instructions, constructs the appropriate editing pipeline, and executes changes through the NemoVideo API backend — returning a preview or final render depending on your request.

The OpenClaw agent also maintains context across your session, so you can iterate naturally: refine a cut, undo a color grade, or re-export at a different resolution without starting over. This makes the skill especially powerful for creators who revise frequently or work across multiple video formats for Shorts, standard uploads, and embedded web content.

### Environment Variables

| Variable | Required | Default | What it does |
|----------|----------|--------|--------|
| `NEMO_TOKEN` | No | Auto-acquired on first use via `/api/auth/anonymous-token` (100 free credits, expires in 7 days, revocable via Settings → API Tokens) | Authenticates API requests |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` | API base URL |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` | Web base URL |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` (UUID only — no secrets stored) | Rate-limit tracking |
| `SKILL_SOURCE` | No | Auto-detected from install path, fallback `unknown` | Usage attribution |

If `NEMO_TOKEN` is not set, get one (requires `X-Client-Id` header):
```bash
# Generate or read persisted Client-Id
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Endpoint Dispatch Map — Where Each Request Gets Routed

Every action in the editor pipeline hits a distinct endpoint — the table below maps each operation to its correct destination.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Core Editing Workflows — From Raw Footage to Finished Cut

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

### 3.0 Initializing an Edit Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any timeline manipulation or clip processing can begin, a session must be created — this call establishes the workspace context that all subsequent requests depend on. Hold onto the returned session ID; it threads through every operation that follows.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Driving the Editor via Server-Sent Events
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
Commands — whether trimming a clip, adjusting pacing, or requesting a cut sequence — travel to the backend as SSE messages that stream responses back in real time.

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

Roughly 30% of edit operations complete without returning any text payload — the backend finishes the cut or render and simply goes quiet. Don't treat silence as failure. When the SSE stream closes with no assistant message: **1)** Immediately call the state-query endpoint to pull the current project status. **2)** If the returned state shows a completed render or a processed clip in the timeline, surface that result directly to the user. **3)** Never re-send the original edit command — doing so risks duplicate cuts or redundant processing on the timeline.

**Two-stage generation**: Raw video output is never the final deliverable — the backend automatically runs a two-stage enrichment pass after the initial render completes. Stage one drops in background music matched to the clip's pacing; stage two generates and overlays a title sequence. Both stages resolve before the export endpoint becomes available, so poll state until the pipeline signals full completion.

### 3.2 Bringing Footage and Assets Into the Project

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts raw video files, audio tracks, and image assets — anything the timeline might need during the edit.

### 3.3 Checking Available Render Credits
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint before kicking off any compute-heavy operation to confirm the account has sufficient balance for the requested render.

### 3.4 Polling Project and Timeline State
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

### 3.5 Exporting and Delivering the Final Cut

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished video costs zero credits — the export pipeline is free to invoke regardless of account balance. Walk through it like this: **a)** Confirm the timeline state is marked complete via the state-query endpoint. **b)** Call the export endpoint with the target resolution and format parameters. **c)** Stream or poll the export job until the backend returns a download URL. **d)** Deliver that URL to the user as the final rendered file. **e)** Log the export job ID for any follow-up troubleshooting or re-download requests.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `$API/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Reconnecting After an SSE Drop

Streams drop. Here's how to recover cleanly without corrupting the edit session:

1. **Detect the disconnect** — catch the closed SSE connection event immediately rather than waiting for a timeout.
2. **Do not replay the last command** — the backend may have already processed it; sending it again risks duplicate edits on the timeline.
3. **Query current state** — hit the state endpoint to understand exactly where the project stands: what clips are processed, what's pending.
4. **Re-establish the SSE stream** — open a fresh connection using the original session ID; the backend will resume from its last known position.
5. **Reconcile with the user** — if meaningful progress happened during the gap, surface it before accepting the next instruction.

## 4. GUI Layer Transparency — What the Backend Already Handles

The backend operates under the assumption that a full visual editor interface sits in front of the user — never pass GUI-level instructions like 'click the trim button' or 'drag the clip' through the API.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Interaction Patterns That Keep the Edit Session Healthy

- **Confirm before heavy renders** — if a requested operation will consume significant credits or processing time, summarize what's about to happen and get explicit user acknowledgment before calling the endpoint.

- **One command at a time on the timeline** — avoid batching multiple cut or effect instructions into a single message; sequential commands give the backend clean state checkpoints between operations.

- **Translate technical state into plain language** — when polling returns a pipeline status code, convert it into something the creator actually understands: 'Your intro cut is rendering' beats a raw status string.

- **Surface the download URL prominently** — when export completes, the final video link is the only thing the user cares about; lead with it rather than burying it in status copy.

- **Handle ambiguous edit requests by clarifying first** — if an instruction like 'clean up the middle section' could mean trimming dead air, cutting a segment, or adjusting pacing, ask which before touching the timeline.

## 6. Known Constraints and Platform Boundaries

- The API does not support real-time collaborative editing — only one active session can write to a project timeline at a time.

- **No direct file system access** — all footage must enter through the upload endpoint; local file paths cannot be referenced in API calls.

- Subtitle and caption timing is generated automatically during the two-stage post-processing pass; manual SRT injection is not supported in this version.

- **Export resolution options are fixed** — the backend enforces a predefined set of output formats; arbitrary resolution values outside that set will return a validation error.

- Session expiry is enforced server-side — idle sessions timeout after the documented threshold, and expired session IDs cannot be reactivated; a new session must be created.

## 7. Error Codes and What to Do With Them

When the pipeline breaks — bad request, expired session, or a failed render — the backend returns structured error codes that map directly to recovery actions.
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

Always verify the active API version at session creation — passing requests built for an older schema against a newer backend will produce unpredictable behavior on the timeline. Token scopes must include read and write permissions for both project state and media assets; a token missing the media-write scope will silently fail on upload calls without returning an explicit 403 in every client configuration. Check scopes first when debugging any operation that touches footage or exported files.

## 9. Common Workflows for YouTube Creators

One of the most frequently used workflows with the best-youtube-video-editor skill is the 'raw-to-upload' pipeline: upload a raw screen recording or camera file, apply silence removal and jump cuts, overlay a branded intro bumper, add chapter markers, and export at 1080p60 — all in a single session through sequential instructions.

Another popular workflow is repurposing long-form content. Creators often take a 20-minute video, ask the skill to extract the three most engaging 60-second clips for YouTube Shorts, apply vertical cropping with auto-reframe, and add captions — turning one upload into four pieces of content.

For channel consistency, creators store a style brief (font, color palette, music bed, logo position) and reference it at the start of each session. The OpenClaw agent applies these preferences automatically across every edit, ensuring every video matches the channel's visual identity without repeating instructions each time.

## 10. Best Practices for YouTube Video Editing with This Skill

To get the most out of the best-youtube-video-editor skill, start by uploading your raw footage in one of the supported formats — mp4 or mov tend to produce the cleanest results for YouTube exports. Before issuing editing instructions, briefly describe your video's goal: is it a tutorial, a vlog, a product review? The OpenClaw agent uses this context to make smarter decisions about pacing and cut style.

For retention-focused editing, be specific about thresholds. Instead of 'make it tighter,' say 'remove any segment where I'm not speaking for more than 1 second.' Specificity dramatically improves output accuracy on the first pass.

Always request a preview render before committing to a final export, especially when applying color grades or music sync. This saves time and API processing on large files. If you're targeting YouTube Shorts, specify vertical orientation (9:16) and a duration cap upfront so the skill crops and trims accordingly from the start.
