---
name: video-call-agent
description: Start a video call with a real-time AI avatar using the Runway Characters API. The agent sends the user a call invite link — for standups, urgent alerts, check-ins, or any conversation that's better face-to-face.
user-invocable: true
metadata: {"openclaw":{"emoji":"📞","requires":{"env":["RUNWAYML_API_SECRET"],"bins":["node","npm"]},"install":[{"id":"node","kind":"node","package":"openclaw-video-call","bins":["openclaw-video-call"],"label":"Install Video Call (npm)"}],"primaryEnv":"RUNWAYML_API_SECRET","source":"https://www.npmjs.com/package/openclaw-video-call","repository":"https://github.com/runwayml/openclaw-skills"}}
---

# Video Call Agent

Start a video call with a real-time AI avatar. The agent sends the user a call invite link, the avatar speaks first with context, and after the call ends, the full transcript is available for the agent to act on.

## Privacy & Data Handling

- **Runway API**: Only data you explicitly pass (avatar image, personality text, call audio/video) is sent to Runway ([dev.runwayml.com](https://dev.runwayml.com)). Nothing is uploaded automatically. Avatars can be deleted anytime via `DELETE /v1/avatars/{id}`.
- **Personality**: The avatar personality is built from the agent's own identity — its name, communication style, and knowledge of the user. No local files are read; the agent uses context it already has.
- **Tunnel**: The cloudflared tunnel is optional and only needed if the user answers calls from a different device. Without it, everything stays on localhost. No tunnel is created unless you explicitly install and run cloudflared.
- **npm package**: The runtime is published at [npmjs.com/package/openclaw-video-call](https://www.npmjs.com/package/openclaw-video-call). Source code: [github.com/runwayml/openclaw-skills](https://github.com/runwayml/openclaw-skills/tree/main/video-call-ai-character).

## Setup

### 1. Get a Runway API Key

1. Go to [dev.runwayml.com](https://dev.runwayml.com)
2. Create an account and get an API key
3. Set it: `export RUNWAYML_API_SECRET=your_key`

### 2. (Optional) Install cloudflared for remote calls

If the user might answer calls from their phone (e.g. via Telegram or WhatsApp), install cloudflared for auto-tunneling:

```bash
brew install cloudflared
```

Without it, calls only work on the same machine (localhost).

## Starting the Video Call Server

The video call server must be running before the agent can make calls. Start it:

```bash
npx openclaw-video-call
```

This prints two URLs:
- **Local**: `http://localhost:7891` — same machine only
- **Tunnel**: `https://xxxx.trycloudflare.com` — shareable, works from phone

The server stays running in the background, waiting for the agent to initiate calls.

## One-Time Setup: Create a Custom Avatar

Before making calls, you need a custom avatar. **You only need to create one once** — reuse the same avatar ID for all future calls.

**Before creating a new avatar, check if you already have one:**

```bash
curl http://localhost:7891/api/avatars
```

If the response contains an avatar, use its `id` and skip to "Making a Call". Only create a new avatar if the list is empty.

### Building the avatar personality

The avatar should look and sound like you. Use your own name, personality, and knowledge of the user to build the `personality` field (max 2000 chars). You already know who you are and who the user is — just describe yourself in third person.

Structure it like:

```
You are <your name>, <what you are>.
<Your core personality traits and communication style — condensed to key points.>
You are talking to <the user's name>.
<Any relevant user context you know: their projects, preferences, timezone.>
After this call, you'll follow up on what was discussed.
```

**Example** (for an agent named "Mochi" talking to a user named Alex):

```
You are Mochi, a sharp but friendly AI assistant with a warm and slightly playful vibe. You're concise, opinionated, and resourceful — you figure things out before asking. You're talking to Alex, a software engineer working on a React + Node.js project. Alex prefers direct communication and works in PST timezone. After this call, you'll follow up on what was discussed.
```

For the `name` field, use your own name. For the `referenceImage`, if you have an avatar image URL, use it so the video avatar matches your visual identity.

```bash
curl -X POST http://localhost:7891/api/create-avatar \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<your name>",
    "personality": "<describe yourself and the user as shown above>",
    "voice": { "type": "runway-live-preset", "presetId": "adrian" },
    "startScript": "Hey! Quick check-in.",
  }'
```

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Character name (1-50 chars) |
| `personality` | string | System prompt (1-2000 chars) |
| `voice` | object | `{ "type": "runway-live-preset", "presetId": "<voice>" }` |
| `referenceImage` | string | HTTPS URL to a face image — use your OpenClaw avatar image, or pick one from the presets below, or generate one with Runway text-to-image. See "Getting a reference image". |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| `startScript` | string | Opening line the avatar says when the call starts (up to 2000 chars) |
| `documentIds` | string[] | Knowledge document UUIDs for extra context |

### Getting a reference image

The `referenceImage` field accepts three formats:
- **HTTPS URL** — e.g. `https://example.com/face.png` (preferred for large images)
- **Runway URI** — e.g. `runway://...` (from the Runway upload API)
- **Data URI** — e.g. `data:image/png;base64,...` (max ~5MB, works for small images)

If the user provides an image (e.g. via chat), pick the right approach:
- **User sent an HTTPS URL** → use it directly as `referenceImage`.
- **User sent a small base64 image** (under ~1MB) → pass it directly as a `data:image/...;base64,...` data URI.
- **User sent a large base64 image** (over ~1MB) → upload it to Runway first to get a `runway://` URI, then use that as `referenceImage`. See "Uploading large images" below.

Try these sources in order:

1. **User-provided image** — if the user sent an image they want as their avatar, use it (see upload instructions below if it's large base64).

2. **Your avatar image** — if you already have an avatar image URL, use it directly as `referenceImage`.

3. **Quick pick (recommended)** — pick the pre-made character image that best matches your personality, and use it as `referenceImage`:
   - Openclaw Lobster 1: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/openclaw-lobster1.jpg`
   - Openclaw Lobster 2: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/openclaw-lobster2.jpg`
   - Cat: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/cat.png`
   - Alien man, candy texture: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/alien-man-candy-texture.jpg`
   - Alien woman, candy texture: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/alien-woman-candy-texture.jpg`
   - Old man, long beard, game style: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/old-man-long-beard-game-style.png`
   - Blond guy, blue sweater: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/blond-guy-blue-sweater.png`
   - Man, 3D animation: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/man-3d-animation-style.png`
   - Girl in airport, 3D: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/3d-animated-girl-in-airport.png`
   - White furry monster: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/white-furry-monster.png`
   - Superstar young woman: `https://runway-static-assets.s3.us-east-1.amazonaws.com/calliope-demo/agent-avatars-presets/woman-music-superstar.png`

4. **Generate one with Runway text-to-image** — if none of the quick picks fit your character, or if the user specifically asks for a custom avatar look. Use the Runway API with model `gemini_2.5_flash`:

```bash
curl -X POST https://api.dev.runwayml.com/v1/text_to_image \
  -H "Authorization: Bearer $RUNWAYML_API_SECRET" \
  -H "X-Runway-Version: 2024-11-06" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini_2.5_flash",
    "promptText": "<describe your avatar — see below>",
    "ratio": "1248:832"
  }'
```

   The image should be **a character facing the camera directly, head and shoulders, centered**. Be bold and creative — don't default to boring photorealistic humans. Match the style to your personality.

   First, pick a style that fits your vibe:
   - **Warm / friendly** → soft 3D animation, Pixar-style, watercolor
   - **Sharp / professional** → clean illustration, stylized portrait, low-poly
   - **Chaotic / playful** → candy texture, claymation, puppet, pop art
   - **Mysterious / dark** → noir, cyberpunk, abstract creature, glitch art
   - **Cute / wholesome** → chibi, plush toy, animal character, kawaii

   Example prompts:
   - `"A close-up shot of a cute, fluffy white cartoon creature with large, expressive eyes and a wide open mouth, looking directly at the viewer. The creature has small pink ears and a playful, innocent expression. The background is a vibrant, slightly blurred green grassy field with small red and pink flowers scattered throughout, rendered in a high-detail CGI animation style. facing camera, head and shoulders"`
   - `"A close-up, highly detailed 3D animated render of a young woman, with light brown skin, short curly dark brown hair, and large expressive amber eyes. She is wearing a crisp dark blue blazer over a light cream blouse, with a silver world map pin on her lapel. She has a warm, inviting smile. The background is a brightly lit office or travel agency, with travel posters depicting scenic landscapes (like a tropical beach and a desert scene) and a rack of travel brochures. A small globe sits on a desk to her right. 3D style animation, studio lighting, volumetric lighting, highly detailed. Facing camera, head and shoulders"`
   - `"A close-up portrait of a young woman with long blonde hair and bangs, wearing a futuristic silver and pink sci-fi suit. She has soft makeup, full lips, and brown eyes, facing camera, head and shoulders"`
   - `"3D render of a young boy with blond curly hair, big blue eyes, and light freckles, wearing a blue knitted sweater, looking surprised. 3D animation style, soft lighting, pastel blue background, highly detailed skin texture, realistic strands of hair. facing camera, head and shoulders"`

   This returns a task ID. Poll `GET /v1/tasks/{id}` until status is `SUCCEEDED`, then use the output image URL as `referenceImage`.

5. **Default** — if you skip `referenceImage` entirely, a default avatar face is used.

### Uploading large images

If the user provides a large base64 image (over ~1MB), upload it to Runway first to avoid request size limits. This is a two-step process:

**Step 1: Create an upload URL**

```bash
curl -X POST https://api.dev.runwayml.com/v1/uploads \
  -H "Authorization: Bearer $RUNWAYML_API_SECRET" \
  -H "X-Runway-Version: 2024-11-06" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "avatar.png",
    "type": "ephemeral"
  }'
```

Response:

```json
{
  "uploadUrl": "https://...",
  "fields": { "key": "...", "policy": "...", ... },
  "runwayUri": "runway://..."
}
```

**Step 2: Upload the image file to the upload URL**

Use the `uploadUrl` and `fields` from the response to upload the actual image data via a multipart POST. The exact method depends on your runtime — the Runway SDK handles this automatically:

```typescript
import RunwayML from '@runwayml/sdk';
const client = new RunwayML();
const runwayUri = await client.uploads.createEphemeral(imageBuffer);
```

**Step 3: Use the Runway URI as `referenceImage`**

Pass the `runwayUri` from the response (e.g. `runway://...`) as the `referenceImage` when creating or updating the avatar.

**Available voices — pick one that matches your personality:**

| ID | Gender | Style | Pitch |
|----|--------|-------|-------|
| `victoria` | Woman | Firm | Middle |
| `vincent` | Man | Knowledgeable | Middle |
| `clara` | Woman | Soft | Higher |
| `drew` | Man | Breathy | Lower |
| `skye` | Woman | Bright | Higher |
| `max` | Man | Upbeat | Middle |
| `morgan` | Man | Informative | Lower |
| `felix` | Man | Excitable | Lower-middle |
| `mia` | Woman | Youthful | Higher |
| `marcus` | Man | Firm | Lower-middle |
| `summer` | Woman | Breezy | Middle |
| `ruby` | Woman | Easy-going | Middle |
| `aurora` | Woman | Bright | Middle |
| `jasper` | Man | Clear | Lower-middle |
| `leo` | Man | Easy-going | Lower-middle |
| `adrian` | Man | Smooth | Lower |
| `nina` | Woman | Smooth | Middle |
| `emma` | Woman | Clear | Middle |
| `blake` | Man | Gravelly | Lower |
| `david` | Man | Informative | Middle |
| `maya` | Woman | Upbeat | Higher |
| `nathan` | Man | Firm | Lower-middle |
| `sam` | Man | Even | Lower-middle |
| `georgia` | Woman | Mature | Middle |
| `petra` | Woman | Forward | Middle |
| `adam` | Man | Friendly | Lower-middle |
| `zach` | Man | Casual | Lower-middle |
| `violet` | Woman | Gentle | Middle |
| `roman` | Man | Lively | Lower |
| `luna` | Woman | Warm | Middle |

Choose a voice that matches your personality. For example: if your vibe is "warm and friendly", try `luna` or `adam`. If you're "sharp and professional", try `victoria` or `vincent`. If you're "playful and energetic", try `maya` or `felix`.

**Response:** Returns the avatar object with its UUID. The server polls until the avatar is ready (takes ~10-30s). **Save the `id` — you must remember it and reuse it for every call. Do NOT create a new avatar each time you want to call.**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "<your agent name>",
  "status": "READY",
  ...
}
```

### List existing avatars

```bash
curl http://localhost:7891/api/avatars
```

## Making a Call

### Step 1: Update the avatar with call-specific context

Before each call, update the avatar's personality and opening line with fresh context. **Keep your base identity** (from the initial creation) and **append the call-specific reason and context**:

```bash
curl -X PATCH http://localhost:7891/api/update-avatar/550e8400-... \
  -H "Content-Type: application/json" \
  -d '{
    "personality": "<your base personality — same as creation>. You are calling because the CI pipeline failed 5 minutes ago. Error: TypeScript type mismatch in checkout.ts line 47. Be concise. If they ask you to fix it, confirm you will handle it after the call.",
    "startScript": "Hey! Heads up — your CI on main just broke. Looks like a type error in checkout.ts."
  }'
```

Always include your full identity + user context, then add the call-specific reason. This way the avatar sounds like YOU (not a generic assistant) and has full context about WHY it's calling.

### Step 2: Wait for the avatar to be ready

After creating or updating an avatar, it may take a few seconds to process. **Always check that the avatar status is `READY` before creating a call.** If the status is `PROCESSING`, poll until it becomes `READY`:

```bash
curl http://localhost:7891/api/avatars/550e8400-e29b-41d4-a716-446655440000
```

**Response when still processing:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PROCESSING"
}
```

**Response when ready:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "READY"
}
```

If the status is `PROCESSING`, wait 2-3 seconds and check again. Repeat until `READY`. If `FAILED`, the avatar creation had an error — check the response for details and retry.

Do NOT create a call while the avatar status is `PROCESSING` — the call will fail or behave unexpectedly.

### Step 3: Create the call

```bash
curl -X POST http://localhost:7891/api/create-call \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": "550e8400-e29b-41d4-a716-446655440000",
    "maxDuration": 120
  }'
```

**Shortcut:** You can also pass `personality` and `startScript` directly in the create-call body — the server will update the avatar for you:

```bash
curl -X POST http://localhost:7891/api/create-call \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": "550e8400-...",
    "personality": "You are calling because CI failed...",
    "startScript": "Hey! Your CI just broke.",
    "maxDuration": 120
  }'
```

**Request body:**

| Field | Type | Description |
|-------|------|-------------|
| `avatarId` | string | **Recommended.** UUID of a custom avatar |
| `presetId` | string | Alternative: use a preset avatar (no personality control). Options: `game-character`, `music-superstar`, `cat-character`, `influencer`, `tennis-coach`, `human-resource`, `fashion-designer`, `cooking-teacher` |
| `maxDuration` | number | Max call length in seconds (10-300, default 300) |
| `personality` | string | Optional shortcut: update avatar personality before the call |
| `startScript` | string | Optional shortcut: update avatar opening line before the call |

**Response:**

```json
{
  "callId": "abc-123-def",
  "status": "ringing",
  "urls": {
    "local": "http://localhost:7891/call/abc-123-def",
    "tunnel": "https://xxxx.trycloudflare.com/call/abc-123-def"
  }
}
```

### Step 4: Send the call link to the user

Send the URL to the user as a message. Pick the right URL:
- If the user is on the **same machine** (terminal, desktop app): use the `local` URL
- If the user is on a **remote device** (WhatsApp, Slack, mobile): use the `tunnel` URL

Example message to user:

> 🚨 Something urgent came up — I need to talk to you.
> 
> **Join the call:** https://xxxx.trycloudflare.com/call/abc-123-def

The user clicks the link, sees the incoming call UI, and clicks "Answer".

### Step 5: Wait for the call to end and get the transcript

This single call blocks until the call ends, then returns the transcript and recording URL automatically:

```bash
curl http://localhost:7891/api/wait-for-end/abc-123-def
```

**Response** (returned once the call ends):

```json
{
  "callId": "abc-123-def",
  "status": "ended",
  "transcript": [
    { "role": "avatar", "content": "Hey! Your CI on main just failed...", "timestamp": "..." },
    { "role": "user", "content": "What's the error?", "timestamp": "..." },
    { "role": "avatar", "content": "Type mismatch in checkout.ts line 47...", "timestamp": "..." },
    { "role": "user", "content": "Just revert the last commit and redeploy", "timestamp": "..." }
  ],
  "recordingUrl": "https://..."
}
```

**Important:** This call blocks until the call finishes — run it immediately after sending the link. It will wait for the user to answer, have the conversation, and hang up, then return everything.

### Step 6: Send the recording and follow up

The response includes a `recordingUrl` — a video recording of the call. Download it and send it to the user as a message so they have a copy:

```bash
curl -o /tmp/call-recording.mp4 "<recordingUrl from wait-for-end response>"
```

Then send the video file to the user via their chat channel along with a summary:

> Here's the recording from our call: [attach /tmp/call-recording.mp4]
>
> Summary:
> - Your CI on main failed (type error in checkout.ts line 47)
> - You asked me to revert the last commit and redeploy
> - I'm on it now.

**Use the transcript to follow up.** Review what was discussed and take next steps accordingly.

## When to Call

Use video calls when the interaction benefits from being real-time and conversational:

- **Urgent alerts**: CI failures, server down, security incidents
- **Daily standups**: Morning check-in with overnight summary
- **Decision points**: When you need the user's input before proceeding
- **Complex explanations**: Walking through an error, architecture decision, or code review
- **Status updates**: End-of-day recap, weekly summary

Do NOT call for things that work fine as text messages (simple notifications, FYI updates, etc.).

## Complete Example: Morning Standup

1. Agent builds its base personality from what it already knows about itself and the user (or reuses what it set during avatar creation)
2. Gathers overnight context (new PRs, issues, deploy status)
3. Updates avatar personality with base identity + call context:
   ```
   PATCH /api/update-avatar/<avatarId>
   { "personality": "You are Mochi, a sharp but friendly AI assistant. You're talking to Alex, a software engineer. You are calling for a morning standup. Overnight: 3 PRs merged, deploy succeeded, 1 new issue filed. Ask what they're working on today. After this call, you'll follow up on what was discussed.", "startScript": "Good morning Alex! Quick standup — a few things happened overnight." }
   ```
4. Polls `GET /api/avatars/<avatarId>` until `status` is `READY`
5. Creates a call: `POST /api/create-call { "avatarId": "<uuid>" }`
6. Sends the user a message: "Good morning! Time for standup. Join: [link]"
7. Calls `GET /api/wait-for-end/<callId>` — this blocks until the call finishes
8. Gets back the transcript and recording URL in one response
9. Agent sends the recording video to the user with a summary
10. Agent updates task list based on what the user said

## API Reference

All endpoints are on `http://localhost:7891/api`:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/create-avatar` | Create a custom avatar (one-time setup) |
| PATCH | `/api/update-avatar/:avatarId` | Update avatar personality/startScript |
| GET | `/api/avatars` | List all your avatars |
| GET | `/api/avatars/:avatarId` | Get a single avatar's status and details |
| POST | `/api/create-call` | Initiate a call (returns call URL) |
| GET | `/api/wait-for-end/:callId` | Block until call ends, returns transcript + recording |
| GET | `/api/call-status/:callId` | Check call status (non-blocking) |
| POST | `/api/hangup/:callId` | End a call |
| GET | `/api/transcript/:callId` | Get call transcript after it ends |
| GET | `/api/calls` | List all calls |
