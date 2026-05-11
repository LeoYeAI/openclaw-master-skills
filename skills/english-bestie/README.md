# 🤙 english-bestie

> **Your student's American friend who happens to teach English.**

An AI English teacher that doesn't feel like a teacher. It texts your student throughout the day, corrects them casually, shares news, asks about their life, sends voice messages, and makes language learning feel like hanging out with a native English speaker.

---

## What It Does

- 📚 **Structured lessons** — rotating grammar, conversation, vocabulary, creative, and mistake-review sessions
- 🎙️ **Voice-first** — sends TTS voice messages like a real friend would
- 🔁 **Spaced repetition** — tracks every word, every mistake, brings them back at the right time
- 🧠 **Self-improving teacher** — reflects after every session, adjusts difficulty, adapts teaching style
- ⚡ **Proactive & spontaneous** — doesn't wait to be asked; messages throughout the day unpredictably
- 🤳 **Telegram-native** — runs through a dedicated Telegram bot

---

## Requirements

- [OpenClaw](https://openclaw.dev) v2026+
- A Telegram bot (see recommended setup below)
- OpenAI API key (for TTS voice — uses `tts-1` with `onyx` voice)
- The student's Telegram user ID (numeric)

---

## Recommended Setup

### 🤖 Dedicated agent (strongly recommended)

This skill works with your existing OpenClaw agent — but we strongly recommend giving english-bestie **its own dedicated agent**. The skill sends 10–12 messages a day, runs deep self-reflection, and maintains an evolving student profile. Mixing it with your main agent causes confusion.

**What to add to `openclaw.json`:**

```json
{
  "agents": {
    "english-bestie": {
      "model": "google/gemini-2.5-flash",
      "workspace": "workspace-english-bestie"
    }
  }
}
```

Then create `workspace-english-bestie/` with the `SOUL.md`, `HEARTBEAT.md`, and `skills/english-bestie/` from this package.

> Any model works. Gemini 2.5 Flash is the best balance of quality + cost for a skill that runs 12× daily.

---

### 📱 Dedicated Telegram bot (strongly recommended)

The agent messages your student **multiple times per day** — morning check-ins, lessons, riddles, news, goodnight messages. If you use your main OpenClaw bot, all of this mixes with your other agent conversations.

A dedicated bot gives the skill its own identity (the student sees it as a separate "friend") and keeps conversations clean.

**Create a dedicated bot in 30 seconds:**
1. Open Telegram → search `@BotFather`
2. Send `/newbot`
3. Pick a name (e.g. "Alex English") and a username (e.g. `alex_english_bot`)
4. Copy the token → paste it when `install.py` asks for it

---

## Installation

### Via ClawHub (recommended)

```
clawhub install english-bestie
```

Then run the setup script to register your Telegram bot:

```
python3 skills/english-bestie/install.py
```

### Manual installation (without ClawHub)

```
python3 install.py
```

The script asks for your OpenClaw directory, Telegram bot token, channel key, and student ID — then handles the rest.

---

## First Run (Onboarding)

After installation, send any message to the bot or let the first cron fire. The agent detects `onboardingComplete: false` in `student-profile.json` and runs the full onboarding flow automatically:

1. **Step 0 — Channel setup** — reads `telegramChannel` from `student-profile.json` (pre-filled by install.py), or learns it from the student's first incoming message
2. **Step 1 — Profile interview** — 6 casual voice questions (name, native language, job, hobbies, goals)
3. **Step 2 — Level assessment** — 5-question conversation to assess English level (A1–B2)
4. **Step 3 — Auto-setup** — saves results to tracking files, sends a friendly summary, and **schedules all 12 daily cron jobs automatically**

No manual cron setup needed. Everything is configured by the agent during first run.

---

## Lesson Rotation

```
grammar → conversation → vocabulary → creative → mistake-review → (repeat)
```

- **Grammar** — one rule, casual explanation, native-language translation exercises
- **Conversation** — role-play scenario, no corrections during, full feedback report after
- **Vocabulary** — 5-7 words with pronunciation/memory tricks, spaced repetition quiz
- **Creative** — wildcard: song, mini-story, debate, real-world challenge, code review...
- **Mistake Review** — address logged mistakes, drill patterns, celebrate fixes

---

## Voice Message Protocol

The agent defaults to **voice (TTS) for all conversational replies**. After every voice message, if the student made a mistake, it sends a TEXT correction card:

```
✗ "I very like coffee" → ✓ "I really like coffee"
  💡 "really" before verbs, "very" before adjectives only
```

Text-only for: grammar lists, vocabulary cards, links, code snippets.

---

## Tracking Files

All session data lives in `tracking/`:

| File | Purpose |
|------|---------|
| `student-profile.json` | Student info, level, strengths, weak areas |
| `progress.json` | Lesson count, rotation position, streak |
| `vocabulary-bank.json` | All words taught with mastery scores (0-10) |
| `mistakes.json` | Every mistake logged with context |
| `grammar-log.json` | Grammar topics covered |
| `teacher-journal.json` | Teacher's private reflections |
| `teaching-plan.json` | Experiment ideas, weekly focus |
| `weekly-report.md` | Auto-generated weekly summary |
| `conversation-history.md` | Full session history |

---

## Customization Tips

- **Not a programmer?** Remove the "Tech-Specific Teaching Opportunities" section in `SKILL.md`
- **Different native language?** Update `SOUL.md` and `SKILL.md` — the agent adapts its analogies to whatever the student knows
- **Different TTS voice?** Change `voice: onyx` to any OpenAI TTS voice in your OpenClaw config
- **More/less messages?** Disable individual cron jobs to reduce frequency

---

*Built with [OpenClaw](https://openclaw.dev) • Inspired by how friends actually teach each other*
