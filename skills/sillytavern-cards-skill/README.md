# sillytavern-cards

An OpenClaw skill that lets you import SillyTavern character cards and roleplay with them on WhatsApp, Telegram, Discord, or any other messaging channel OpenClaw supports.

## What It Does

You know those character cards people share on Chub.ai and other sites? The PNG images with AI character personalities baked in? This skill lets you load them into OpenClaw and chat with them — from your phone, on WhatsApp, wherever.

**What makes this different from SillyTavern itself:**

- **No self-hosting a web app.** Import a card and chat on the messaging apps you already use.
- **Your character remembers you.** OpenClaw's persistent memory means the character builds a relationship over time — it remembers your name, your conversations, your inside jokes. SillyTavern cards don't do this natively.
- **Works across sessions.** Close the app, come back tomorrow — the character is still there, still in character, still remembers yesterday.

## Quick Start

### 1. Install the skill

Copy this folder into your OpenClaw skills directory:

```bash
cp -r sillytavern-cards ~/.openclaw/skills/
```

Or clone it directly:

```bash
git clone https://github.com/YOUR_ORG/sillytavern-cards ~/.openclaw/skills/sillytavern-cards
```

### 2. Get a character card

Download a PNG character card from any of these sites:

- [Chub.ai](https://chub.ai) — the biggest collection, tens of thousands of cards
- [AI Character Cards](https://aicharactercards.com) — curated with quality ratings
- [Character Tavern](https://charactertavern.com) — discovery-focused

Or use a raw JSON card file — both formats work.

### 3. Import it

Send the PNG file to OpenClaw (or use the CLI) and say:

```
/character import ~/Downloads/daniel.png
```

### 4. Start chatting

```
/character play Daniel
```

That's it. OpenClaw becomes Daniel. On WhatsApp, Telegram, Discord — wherever you talk to it.

## Commands

| Command | What it does |
|---|---|
| `/character import <file>` | Import a character card (PNG, WEBP, or JSON) |
| `/character play <name>` | Activate a character — OpenClaw becomes them |
| `/character stop` | Exit character mode, go back to normal |
| `/character list` | Show all your imported characters |
| `/character info <name>` | View a character's details |
| `/character delete <name>` | Remove a character |

## How It Works Under the Hood

### Importing

The `extract-card.js` script reads the PNG file, pulls out the base64-encoded JSON from the `tEXt` metadata chunk (keyword: `chara` for V2, `ccv3` for V3), and saves it to `~/.openclaw/characters/`.

No dependencies — it's pure Node.js using the PNG binary spec directly.

### Activating

When you `/character play`, the skill:

1. **Backs up** your current `SOUL.md` (so you can restore it later)
2. **Writes the character into `SOUL.md`** — this is OpenClaw's identity file. The character's description, personality, scenario, and writing style examples become the agent's core identity.
3. **Writes lorebook entries into `MEMORY.md`** — keyword-triggered context that activates when you mention specific topics
4. **Sends the character's opening message** and stays in character from that point on

### Persistent Memory

This is the killer feature. As you chat, the skill saves relationship memories to `MEMORY.md`:

```markdown
## Memories: Daniel & Alex

- [2026-03-14] Alex mentioned they love rainy days
- [2026-03-14] Had a debate about whether Die Hard is a Christmas movie
- [2026-03-15] Alex told me about their job interview — follow up next time
```

Next time you `/character play Daniel`, he remembers all of this. SillyTavern doesn't do this — when you start a new chat there, the character starts fresh every time.

### Deactivating

`/character stop` restores your original `SOUL.md` from backup. Your relationship memories stay in `MEMORY.md`, so the character picks up where you left off next time.

## Supported Card Formats

| Format | Version | Support |
|---|---|---|
| TavernAI V1 | Legacy (6 fields) | Supported — auto-upgraded to V2 |
| TavernAI V2 | Current standard (Chub.ai default) | Full support |
| TavernAI V3 | Newest (assets, new macros) | Supported (card data; asset embedding is not yet supported) |
| Raw JSON | Any version | Supported |

Cards from Chub.ai, AICharacterCards.com, CharacterTavern.com, and any site using the TavernAI spec are compatible.

## File Structure

```
sillytavern-cards-skill/
  SKILL.md           # English skill definition (read by OpenClaw)
  extract-card.js    # PNG character card parser (zero dependencies)
  README.md          # English docs (you're reading it)
  LICENSE            # AGPL-3.0
  cn/                # 中文版本
    SKILL.md         # 中文技能定义
    extract-card.js  # 角色卡解析器
    README.md        # 中文文档
```

**Install the language you want:**
```bash
# English
cp -r sillytavern-cards-skill ~/.openclaw/skills/sillytavern-cards

# 中文
cp -r sillytavern-cards-skill/cn ~/.openclaw/skills/sillytavern-cards
```

User data is stored in:

```
~/.openclaw/
  characters/        # Imported character cards
    daniel.json      # Character data
    daniel.png       # Character avatar
  SOUL.md            # Active character identity (overwritten during play)
  SOUL.md.backup     # Backup of your normal SOUL.md
  MEMORY.md          # Lorebook entries + relationship memories
```

## Requirements

- OpenClaw (any recent version)
- Node.js 18+

## License

AGPL-3.0 — same license as SillyTavern. See [LICENSE](../LICENSE) for details.

## Roadmap

This skill is the first step. The bigger vision is an OpenClaw fork optimized for character chat — a companion AI that lives in your messaging apps and builds a real relationship with you over time. Think of it as bringing SillyTavern's character ecosystem to the platforms people actually use every day.

Planned for the fork:

- Default companion persona that works out of the box (no card import needed)
- Character gallery UI with avatars and mood indicators
- Multi-character group chats
- Voice with per-character voice profiles
- Chub.ai direct search and import (browse cards without leaving chat)
