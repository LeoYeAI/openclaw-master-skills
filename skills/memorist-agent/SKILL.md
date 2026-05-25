---
name: memorist_agent
description: "Memorist Agent — helps you capture your parents' and family members' life stories through adaptive interviews via WhatsApp, WeChat, or direct conversation. Organizes stories into memoir chapters. Local-first, privacy-protected. Bilingual: English + Chinese (普通话). Commands: /memorist_agent setup, interview, stories, compile, export, share."
version: 0.1.0
license: MIT
metadata:
  openclaw:
    emoji: "📖"
    os: ["darwin", "linux", "windows"]
    optional:
      anyBins:
        - mlx-whisper-transcribe
        - whisper
    install:
      - id: mlx-whisper
        kind: exec
        command: pip3
        args: ["install", "mlx-whisper"]
        label: "Install mlx-whisper (Apple Silicon, recommended)"
        platforms: ["darwin"]
      - id: openai-whisper
        kind: brew
        formula: openai-whisper
        bins: ["whisper"]
        label: "Install OpenAI Whisper via Homebrew (Intel Mac / Linux fallback)"
        platforms: ["darwin", "linux"]
allowed-tools:
  - file_read
  - file_write
  - whatsapp_send_message
  - fetch
  - web_search
---

# Memorist Agent

Help your parents and grandparents tell their stories before it's too late.

Memorist Agent conducts adaptive, empathetic interviews across 9 life domains — in English or Chinese. It remembers every name, place, and year the narrator mentions and follows up with targeted questions to draw out richer memories.

### Why Memorist Agent?

- **Local-first** — Every story fragment, entity, and chapter lives on your machine at `~/.openclaw/memorist_agent/`. Nothing is uploaded to any server. You own your family's data completely.
- **Private by design** — No accounts, no cloud sync, no third-party databases. The only network calls are the ones you explicitly trigger (sending a WhatsApp question or sharing an export). Delete the folder and it's gone.
- **Easy to use** — Run `/memorist_agent setup`, answer 4 questions, and you're interviewing. Relay mode works immediately with zero configuration. WhatsApp auto-reply takes one extra command. The AI handles question flow, entity tracking, and story writing — you just talk to your family.
- **Bilingual** — Native support for English and Chinese (普通话). The agent mirrors the narrator's language naturally, including dialect phrases and colloquial expressions.
- **Works with any channel** — WhatsApp, Telegram, WeCom, iMessage, or just relay questions in person over tea. The skill adapts to however your family communicates.

---

## Quick Start — Your First Interview

**Step 1** — Set up a narrator:
```
/memorist_agent setup
```

**Step 2** — Pick "Relay" mode (easiest — no extra config needed). You'll get questions to ask your narrator in person, over the phone, or via any messaging app. Type or paste their answers back.

**Step 3** — Run the interview:
```
/memorist_agent interview --narrator "Dad"
```

That's it. After 3–5 questions, the skill saves a story fragment automatically.

**Want hands-free WhatsApp?** Pick "WhatsApp auto-reply" during setup instead. The narrator chats directly with their own dedicated agent — no copy-pasting needed. Requires WhatsApp gateway setup (see Prerequisites below).

---

## What You Need

- **OpenClaw gateway running**: `openclaw status` should show gateway `running`.
- Everything else is set up automatically on first run.

**Nice to have (based on your setup):**

| Feature | What to configure |
|---------|-------------------|
| WhatsApp auto-reply | WhatsApp linked (`openclaw status`), narrator's number in `channels.whatsapp.allowFrom` or `dmPolicy: "open"`, `mkdir -p ~/.openclaw/media` |
| Telegram auto-reply | Telegram bot configured, narrator's numeric user ID in `channels.telegram.allowFrom` |
| WeCom auto-reply | `@sunnoy/wecom` plugin loaded, `channels.wecom.enabled: true` |
| iMessage auto-reply | macOS only. `channels.imessage.enabled: true`, narrator's phone/email in `channels.imessage.allowFrom`, Full Disk Access granted to terminal. Requires `imsg` CLI (`brew install pj4533/homebrew-imsg/imsg`) |
| Voice replies (TTS) | `messages.tts` configured in openclaw config — see `references/media-and-voice.md` |
| Voice note transcription | `pip3 install mlx-whisper` (Apple Silicon) or `brew install openai-whisper`, or run `/memorist_agent setup-stt` |

File paths use `~/.openclaw/` (`$HOME/.openclaw/` on all platforms — macOS, Linux, Windows WSL).

---

## Commands

| Command | Description |
|---------|-------------|
| `/memorist_agent setup` | Add a narrator and configure their interview channel |
| `/memorist_agent interview [--narrator NAME] [--domain DOMAIN]` | Start or continue an interview session |
| `/memorist_agent spawn [--narrator NAME]` | Enable auto-reply — creates a dedicated agent for this narrator |
| `/memorist_agent despawn [--narrator NAME]` | Disable auto-reply — remove the dedicated agent |
| `/memorist_agent remind [--narrator NAME]` | Send a gentle reminder to continue their story |
| `/memorist_agent stories [--narrator NAME] [--domain DOMAIN]` | Browse collected story fragments |
| `/memorist_agent entities [--narrator NAME]` | Show the entity map: people, places, years |
| `/memorist_agent compile [--narrator NAME]` | Compile fragments into polished memoir chapters |
| `/memorist_agent export [--narrator NAME] [--format md\|json\|txt]` | Export the memoir to a file |
| `/memorist_agent share [--narrator NAME]` | Invite a family co-editor to review |
| `/memorist_agent status` | Show all narrators, progress, and agent status |
| `/memorist_agent setup-stt` | Auto-install voice transcription |

---

## Life Story Domains

| ID | Domain (EN) | Domain (ZH) | Sample Opening Question |
|----|-------------|-------------|------------------------|
| `origins` | Origins & Childhood | 出身与童年 | "Where were you born, and what's your earliest memory of home?" |
| `growing-up` | Growing Up | 成长岁月 | "What was school like for you? Who were your closest friends?" |
| `family-history` | Family History | 家族历史 | "Tell me about your parents — what kind of people were they?" |
| `love` | Love & Partnership | 爱情与伴侣 | "How did you and Mum/Dad first meet?" |
| `work` | Work & Career | 工作与事业 | "What was your first real job? What did you dream of becoming?" |
| `places` | Places & Journeys | 地方与旅途 | "What places have you lived in across your life?" |
| `history` | Historical Moments | 历史时刻 | "You lived through [decade] — what do you remember most?" |
| `milestones` | Family Milestones | 家庭里程碑 | "What family celebrations stand out most in your memory?" |
| `wisdom` | Values & Wisdom | 价值观与智慧 | "What's the most important lesson life has taught you?" |

---

## Storage Layout

All data is stored locally at `~/.openclaw/memorist_agent/`:

```
~/.openclaw/memorist_agent/
├── owner.json                           # Skill owner's name
├── narrators.json                       # Index of all narrators
├── narrators/
│   └── {narrator-id}/
│       ├── profile.json                 # Narrator metadata & domain progress
│       ├── entities.json                # Extracted people, places, years
│       ├── sessions.json                # Interview session log
│       ├── fragments/                   # Story fragments by domain
│       ├── chapters/                    # Compiled memoir chapters
│       ├── exports/                     # Exported memoir files
│       └── workspace/                   # Agent workspace (if auto-reply enabled)
```

---

## /memorist_agent setup

**Purpose:** Register a narrator and choose how interviews will be conducted.

**Steps:**

1. **First-run bootstrap**: Create the data directory if it doesn't exist:
   - `mkdir -p ~/.openclaw/memorist_agent/narrators`
   - If `narrators.json` doesn't exist, create it as `[]`.
   - If this is the first run, ask: **"What's your name? (This is how narrators will know who set this up.)"** Save to `~/.openclaw/memorist_agent/owner.json` as `{ "name": "{name}" }`. Skip if `owner.json` already exists.

2. Ask the user:
   ```
   Let's set up your narrator. I'll ask a few questions.

   1. What is their name? (e.g. "Dad", "Grandma Li", "Uncle Chen")
   2. What's their relationship to you? (parent / grandparent / relative / friend)
   3. What language should I interview them in?
      [1] English
      [2] Chinese (普通话)
      [3] Both (start in Chinese, key summaries in English)
   4. How should I conduct interviews?
      [1] Relay — I give you questions, you ask them and bring back answers
          (Works with any channel: in person, phone call, WeChat, etc.)
      [2] WhatsApp auto-reply — they chat directly with a dedicated agent
          (Requires WhatsApp gateway. I'll help you set it up.)
      [3] iMessage auto-reply — they chat via iMessage with a dedicated agent
          (macOS only. Requires iMessage channel configured.)
      [4] Telegram auto-reply — they chat via Telegram with a dedicated agent
          (Requires Telegram bot configured.)
      [5] Live — the narrator is here right now, let's start talking
   ```

3. **If "WhatsApp auto-reply" is selected:**
   a. Ask for their WhatsApp number (with country code, e.g. `+1234567890`).
   b. **Validate allowlist**: Read the openclaw config and check if the number is in `channels.whatsapp.allowFrom` or if `dmPolicy` is `"open"`. If NOT:
      ```
      ⚠️  {number} is not in your WhatsApp allowlist yet.
      Their replies will be silently dropped without this.

      I can add it for you — shall I update channels.whatsapp.allowFrom?
      [Yes, add it] / [No, I'll do it manually]
      ```
      If user says yes, add the number to `channels.whatsapp.allowFrom` in the openclaw config file.
   c. **Verify gateway**: Check `openclaw status` output. If WhatsApp is not `linked`:
      ```
      ⚠️  WhatsApp gateway is not connected.
      Run: openclaw status
      If WhatsApp shows "not linked", you'll need to pair it first.

      For now, I'll set up the narrator in Relay mode. You can switch to
      WhatsApp auto-reply later with /memorist_agent spawn.
      ```
      Fall back to relay mode if gateway is not ready.
   d. **Create media directory**: `mkdir -p ~/.openclaw/media` (gateway rejects media from other paths).

4. **If "iMessage auto-reply" is selected:**
   a. Ask for their phone number or Apple ID email.
   b. **Check platform**: If not macOS, warn: "iMessage is only available on macOS. Switching to Relay mode."
   c. **Validate allowlist**: Check if the number/email is in `channels.imessage.allowFrom` or if `dmPolicy` is `"open"`. Offer to add if missing (same flow as WhatsApp step 3b).
   d. **Verify iMessage**: Check `openclaw status` — iMessage should show `OK` or `configured`. If not:
      ```
      ⚠️  iMessage channel is not configured.
      Make sure:
        1. channels.imessage.enabled: true in your openclaw config
        2. imsg CLI is installed: brew install pj4533/homebrew-imsg/imsg
        3. Full Disk Access is granted to your terminal app
           (System Settings → Privacy & Security → Full Disk Access)

      For now, I'll set up in Relay mode. Switch later with /memorist_agent spawn.
      ```
   e. **Create media directory**: `mkdir -p ~/.openclaw/media`.

5. **If "Telegram auto-reply" is selected:**
   a. Ask for their Telegram user ID (numeric). Explain: "Ask them to message @userinfobot on Telegram to get their numeric ID."
   b. **Validate allowlist**: Check if the ID is in `channels.telegram.allowFrom`. Offer to add if missing.
   c. **Verify Telegram**: Check `openclaw status` — Telegram should show `OK`. Warn and fall back to relay if not configured.

6. **If "Live" is selected:** Note that the narrator is present — skip channel setup, start interview immediately after setup completes.

5. Generate a narrator ID: `narrator-{slug(name)}-{timestamp}`.

6. Create `~/.openclaw/memorist_agent/narrators/{id}/` directory structure (including `fragments/`, `chapters/`, `exports/` subdirs):

   **profile.json:**
   ```json
   {
     "id": "{narrator-id}",
     "name": "{name}",
     "relationship": "{relationship}",
     "lang": "{en|zh|both}",
     "channel": "{relay|whatsapp|imessage|telegram|live}",
     "whatsapp": "{number or null}",
     "imessage": "{phone or email or null}",
     "telegram": "{numeric user ID or null}",
     "replyFormat": "text",
     "createdAt": "{ISO timestamp}",
     "domains": {
       "origins": { "status": "not-started", "fragmentCount": 0 },
       "growing-up": { "status": "not-started", "fragmentCount": 0 },
       "family-history": { "status": "not-started", "fragmentCount": 0 },
       "love": { "status": "not-started", "fragmentCount": 0 },
       "work": { "status": "not-started", "fragmentCount": 0 },
       "places": { "status": "not-started", "fragmentCount": 0 },
       "history": { "status": "not-started", "fragmentCount": 0 },
       "milestones": { "status": "not-started", "fragmentCount": 0 },
       "wisdom": { "status": "not-started", "fragmentCount": 0 }
     }
   }
   ```

   **entities.json:** `{ "people": [], "places": [], "years": [], "events": [] }`

   **sessions.json:** `[]`

7. Append narrator to `narrators.json`.

8. **If channel is "whatsapp", "imessage", or "telegram", immediately recommend auto-reply:**
   ```
   Narrator added: {name}
   Language  : {lang}
   Channel   : WhatsApp ({number})

   For the best experience, I recommend enabling auto-reply so {name}
   can chat directly without you copy-pasting messages.

   Enable now? /memorist_agent spawn --narrator "{name}"
   [Skip — I'll use relay mode for now]
   ```

   **Otherwise (relay or live):**
   ```
   Narrator added: {name}
   Language  : {lang}
   Channel   : {channel}
   Domains   : 9 life story domains ready

   Start the first interview with:
   /memorist_agent interview --narrator "{name}"
   ```

---

## /memorist_agent interview

**Purpose:** Conduct one interview session covering one memory domain. Generates 1–3 story fragments and updates the entity map.

**Usage:**
- `/memorist_agent interview` — auto-selects narrator and next domain
- `/memorist_agent interview --narrator "Dad"` — specific narrator
- `/memorist_agent interview --narrator "Dad" --domain origins` — specific domain
- `/memorist_agent interview --narrator "Dad" --resume` — continue last session

**High-level flow:**
1. Load narrator context (profile, entities, prior fragments)
2. Pick next domain (or resume in-progress one)
3. Generate opening question adapted to language and prior context
4. Send question via configured channel (relay, WhatsApp, or live)
5. Run adaptive follow-up loop (3–5 exchanges per session)
6. Distill exchanges into a first-person story fragment
7. Update entity map and save all data

**Error handling:**
- If no narrators exist: "No narrators set up yet. Run `/memorist_agent setup` first."
- If all 9 domains are complete: "All domains are complete! Run `/memorist_agent compile` to create the memoir."
- If WhatsApp gateway is down: Fall back to relay mode and warn the user.

**For detailed step-by-step instructions, read:** `references/interview-workflow.md`

**Interview principles (read before first session):** `references/interview-principles.md`

---

## /memorist_agent remind

**Purpose:** Send a gentle, warm reminder to continue sharing stories.

**Steps:**
1. Load narrator profile. Find in-progress or next not-started domain.
2. Generate personalized reminder referencing something they already shared.
3. Send via WhatsApp if configured, otherwise display for relay.

---

## /memorist_agent stories

**Purpose:** Browse collected story fragments.

**Usage:**
- `/memorist_agent stories` — all fragments for default narrator
- `/memorist_agent stories --narrator "Dad" --domain origins` — filtered

**Steps:**
1. Load all fragment files for the narrator.
2. Display grouped by domain: title, preview, people/places mentioned, pending follow-ups.
3. Show total fragment count and domain coverage.

---

## /memorist_agent entities

**Purpose:** Show the entity map — all people, places, years, events extracted from stories.

**Steps:**
1. Load `entities.json` for the narrator.
2. Display grouped by type, with follow-up status (resolved vs pending).
3. Show count of unresolved entities that will be followed up automatically.

---

## /memorist_agent compile, export, share

**Purpose:** Compile fragments into memoir chapters, export to file, share with family.

**For detailed instructions, read:** `references/compile-export-share.md`

---

## /memorist_agent spawn, despawn

**Purpose:** Enable or disable auto-reply for a narrator. "Spawn" creates a dedicated, isolated agent that chats directly with the narrator — no copy-pasting needed. "Despawn" removes it.

After spawning, all messages from the narrator's WhatsApp/Telegram route directly to their personal agent. The main session is never touched.

**Error handling:**
- If gateway is not running: "Gateway is not running. Start it with `openclaw gateway start`, then try again."
- If WhatsApp is not linked: "WhatsApp is not connected. Run `openclaw status` to check."
- If narrator's number is not in allowlist: Offer to add it (same as setup step 3b).
- If spawn fails for any reason: Fall back gracefully — "Auto-reply couldn't be enabled. You can still use relay mode with `/memorist_agent interview`."

**For detailed instructions, read:** `references/spawn-despawn.md`

---

## /memorist_agent status

**Purpose:** Overview of all narrators and their progress.

**Steps:**
1. Load `narrators.json` and each narrator's `profile.json`.
2. Display per narrator: name, relationship, language, channel, agent status, domain progress bar, fragment count, last session date.
3. Show available commands.

```
Memorist Agent — Overview

Narrators: {N}
───────────────────────────────
{name} ({relationship})
  Language  : {lang}
  Channel   : {Relay / WhatsApp auto-reply / Live}
  Agent     : {active/none}
  Progress  : {bar} {N}/9 domains
  Fragments : {count} stories collected
───────────────────────────────
```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Narrator's WhatsApp replies don't arrive | Number not in allowlist | Add to `channels.whatsapp.allowFrom` in openclaw config, or set `dmPolicy: "open"` |
| `/memorist_agent spawn` fails | Gateway not running | `openclaw gateway start` or `openclaw gateway restart` |
| Media sends hang (text works) | Gateway WhatsApp connection crashed | `openclaw gateway restart` |
| Voice notes not transcribed | No STT tool installed | Run `/memorist_agent setup-stt` |
| Voice replies don't play properly | Wrong audio format | WhatsApp needs OGG/Opus, not MP3. See `references/media-and-voice.md` |
| TTS produces garbled speech | Wrong voice language | Set `messages.tts.edge.voice` to match narrator's language in openclaw config |
| Interview says "no narrators" | Haven't run setup yet | Run `/memorist_agent setup` first |
| All domains complete | Interviews finished | Run `/memorist_agent compile` to create the memoir |

---

## Privacy Architecture

| Data | Where it lives | Who can access |
|------|---------------|----------------|
| Story fragments | `~/.openclaw/memorist_agent/` | Local machine only |
| Entity map | `~/.openclaw/memorist_agent/` | Local machine only |
| Interview sessions | `~/.openclaw/memorist_agent/` | Local machine only |
| Compiled chapters | `~/.openclaw/memorist_agent/` | Local machine only |
| WhatsApp messages sent | Narrator's WhatsApp | Narrator only |
| Exported files | Path you choose | You control sharing |

**Claude AI** processes text during active sessions. If privacy-sensitive, use relay mode — type questions manually and record answers yourself.

---

## Tool Usage Notes

- **file_read / file_write**: all narrator data at `~/.openclaw/memorist_agent/`.
- **whatsapp_send_message**: used only when narrator channel is `whatsapp`.
- **fetch**: only called if user runs `/memorist_agent share` with API option.
- **web_search**: not used. This skill is intentionally offline-first.

**For media format requirements, TTS config, STT setup, and troubleshooting, read:** `references/media-and-voice.md`
