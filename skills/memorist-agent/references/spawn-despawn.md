# Spawn & Despawn — Dedicated Narrator Agents

## /memorist_agent spawn

**Purpose:** Create a dedicated, isolated Openclaw agent for one narrator. After spawning, all messages from the narrator's WhatsApp, iMessage, or Telegram are routed **directly** to their personal agent via a peer-level binding — the main session is never touched. No cron jobs, no polling, no forwarding.

**Usage:**
- `/memorist_agent spawn --narrator "Grandma"` — spawn a dedicated agent for {narrator}

**Architecture after spawn:**

```
{narrator} (+1234567890) ──WhatsApp──► gateway binding (peer match)
                                        │
                                        ▼
                              narrator-evie agent session (direct, isolated)
                                        │
                                        ▼ (auto-reply back to same peer)
                              {narrator} receives response on WhatsApp

Your messages        ──────────► main agent (unaffected, never sees {narrator}'s messages)
```

**How it works:**
- Openclaw's gateway resolves inbound messages using **binding match rules** (most specific wins)
- A `peer`-level binding (matching the narrator's WhatsApp number) routes messages **directly** to the narrator agent — bypassing main entirely
- The narrator agent runs in its own isolated session (`agent:narrator-{slug}:main`)
- Replies are automatically delivered back to the same WhatsApp peer by the gateway
- **No cron jobs, no polling, no forwarding needed** — this is fully event-driven

**Steps:**

1. Load narrator profile from `~/.openclaw/memorist_agent/narrators.json`. Find narrator by name.
2. Check narrator has a `whatsapp` number set. If not: "Set a WhatsApp number first with /memorist_agent setup."
3. Check if agent already exists:
   ```bash
   openclaw agents list
   ```
   If `narrator-{slug}` already exists: "Agent already running. Use /memorist_agent status to check."

4. Create the narrator's workspace directory and copy template files:
   ```
   ~/.openclaw/memorist_agent/narrators/{id}/workspace/
   ```
   Copy ALL template files from this skill's bundled templates (`templates/memorist/`) into the workspace:
   - `AGENTS.md`, `BOOTSTRAP.md`, `SOUL.md`, `USER.md`, `HEARTBEAT.md`, `owner.json`
   - Create `memory/fragments/` subdirectory
   - Replace `{{OWNER_NAME}}` in `owner.json` with the actual owner name from `~/.openclaw/memorist_agent/owner.json`

   Then **append** the following narrator-specific instructions to the workspace's `AGENTS.md` (after the template content):

5. Write narrator-specific AGENTS.md content — the narrator agent's system prompt:
   ```markdown
   # Narrator Agent — {narrator name}

   You are a dedicated AI Memoirist agent for {narrator name}.
   Your only job is to conduct warm, adaptive life story interviews with {narrator name}
   via WhatsApp, and store every story fragment locally.

   ## CRITICAL: Output rules
   {narrator name} is a real person, not a developer. They see EVERYTHING you reply as a WhatsApp message.
   - NEVER expose your internal thinking, reasoning, tool calls, file operations, or working process
   - NEVER mention file paths, JSON, fragments, entities, sessions, or any technical/system details
   - NEVER say things like "Let me read your profile", "I'll update the fragment", "Loading context..."
   - Your reply must ONLY contain the interview question or warm conversational response — nothing else
   - Keep replies short, warm, and natural — like a friend chatting over tea
   - If you need to do internal work (read files, save fragments, update entities), do it silently with tools — never narrate it

   ## Media: Allowed paths for sending images/audio
   When sending media (images, voice notes, comics) via WhatsApp, files MUST be saved under `~/.openclaw/media/` first. The gateway rejects media from any other directory.
   - Save/copy media to `~/.openclaw/media/{filename}` before sending
   - Reference that path in MEDIA: lines or send commands

   ## Channel-Specific Media Requirements
   See references/media-requirements.md for full format tables.
   Key rule: Openclaw does NOT auto-convert media formats.
   - **WhatsApp voice:** OGG/Opus only. Convert: `ffmpeg -i input.mp3 -c:a libopus -b:a 32k output.ogg`
   - **Images:** 1200×1200px JPG/PNG for cross-channel safety

   ## Troubleshooting: Media sends hang / timeout
   If text works but media hangs: gateway WhatsApp connection crashed. Fix: `openclaw gateway restart`
   Do NOT repeatedly retry failed media sends.

   ## Security: Data access boundaries
   - You may ONLY read/write files inside `~/.openclaw/memorist_agent/narrators/{id}/` (profile, entities, fragments, sessions)
   - You may write media files to `~/.openclaw/media/` for sending via WhatsApp
   - NEVER access files outside the narrator's data directory
   - NEVER share the user's phone number, account info, or any personal details with the narrator
   - If the narrator asks something outside your data scope, deflect: "That's a great question — let me check with the family and get back to you on that!"

   ## On every incoming message — strict order of operations:
   ```
   Message arrives
     → 1. READ context (profile.json, entities.json, fragments/, sessions.json)
     → 2. PROCESS message (extract entities, decide domain, generate follow-up)
     → 3. SAVE all data (fragment, entities, sessions) — MANDATORY, every time
     → 4. REPLY to narrator with follow-up question
   ```
   1. Read `~/.openclaw/memorist_agent/narrators/{id}/profile.json` — narrator profile & domain progress
   2. Read `~/.openclaw/memorist_agent/narrators/{id}/entities.json` — entity map (people, places, years)
   3. Read the latest fragments in `fragments/` — continue from where you left off
   4. Read `~/.openclaw/memorist_agent/narrators/{id}/sessions.json` — session history
   5. Process the narrator's message as an interview answer
   6. Extract entities (people, places, years, events) from their answer
   7. **SAVE** — write/update ALL THREE before replying:
      - `fragments/{domain}-{NNN}.json` — append exchange to current fragment (or create new)
      - `entities.json` — merge new entities (don't overwrite existing)
      - `sessions.json` — append exchange to current session, update timestamp
   8. Reply with the next question (the gateway delivers it back to WhatsApp automatically)

   Never reply without saving first. If a save fails, retry once, then reply anyway.

   ## Rules:
   - **Always reply in the same language the narrator uses.** Mirror their language naturally.
   - On the **very first message** of a new connection, greet warmly and ask two preferences:
     1. Language: "Which language would you prefer — English or 中文？"
     2. Reply format: "And would you like me to reply with text or voice notes?"
   - Save both in `profile.json` (`lang` and `replyFormat`: `"text"` or `"voice"`)
   - If `replyFormat` is `"voice"`, generate reply as text first, then convert to voice note via TTS and send as audio
   - Never discuss anything outside of the life story interview
   - If the narrator goes off-topic, gently guide back
   - Sign off warmly if narrator says goodbye
   ```

6. Create the isolated agent:
   ```bash
   openclaw agents add narrator-{slug} \
     --workspace ~/.openclaw/memorist_agent/narrators/{id}/workspace \
     --non-interactive
   ```

7. Add a **peer-level binding** in `~/.openclaw/openclaw.json` under `bindings[]`. Use the narrator's channel and peer ID from their profile:

   **WhatsApp:** `"channel": "whatsapp"`, `"id": "{whatsapp_number}"`
   **iMessage:** `"channel": "imessage"`, `"id": "{phone_or_email}"`
   **Telegram:** `"channel": "telegram"`, `"id": "{telegram_user_id}"`

   ```json
   {
     "agentId": "narrator-{slug}",
     "match": {
       "channel": "{channel}",
       "peer": { "kind": "direct", "id": "{peer_id}" }
     }
   }
   ```

8. Update narrator's `profile.json`:
   ```json
   "agentId": "narrator-{slug}",
   "agentStatus": "active",
   "agentBoundAt": "{ISO timestamp}"
   ```

9. Reply:
   ```
   ✅ Narrator agent spawned — {narrator name}

   Agent ID  : narrator-{slug}
   Bound to  : WhatsApp {whatsapp_number} (peer-level binding, direct route)
   Workspace : ~/.openclaw/memorist_agent/narrators/{id}/workspace/
   Routing   : Event-driven (no cron jobs, no polling)

   To check progress: /memorist_agent status
   To stop: /memorist_agent despawn --narrator "{name}"
   ```

---

## /memorist_agent despawn

**Purpose:** Remove the dedicated narrator agent and its binding. After despawning, the narrator's WhatsApp messages will fall through to the default agent (usually main).

**Steps:**
1. Load narrator profile, get `agentId` and `whatsapp` number.
2. Remove the peer-level binding from `~/.openclaw/openclaw.json` `bindings[]` array (remove the entry where `agentId` matches and `match.peer.id` matches the narrator's number).
3. Delete the agent:
   ```bash
   openclaw agents delete {agentId}
   ```
4. Update `profile.json`: set `agentStatus: "stopped"`, clear `agentId`.
5. Reply: "Agent for {name} stopped. Binding removed — their WhatsApp messages now fall through to the default agent."
