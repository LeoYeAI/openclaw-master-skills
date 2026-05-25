# Memorist Agent — Openclaw Skill

> Capture your parents' life stories before it's too late.

Memorist Agent is an Openclaw skill that conducts adaptive, empathetic interviews with your parents or grandparents across **9 life domains** — in **English or Chinese (普通话)**. It builds a growing map of every person, place, and year they mention, and uses that to ask richer follow-up questions each session.

All story data lives **locally on your machine**. Nothing is sent to any server without your explicit action.

---

## Quick Start

```bash
# Install into Openclaw
openclaw skill install memorist_agent

# Set up your first narrator
/memorist_agent setup

# Start the first interview
/memorist_agent interview

# After a few sessions, compile into a memoir
/memorist_agent compile

# Export as a Markdown document
/memorist_agent export --format md
```

---

## Features

### Adaptive AI Interviews
The AI adapts every follow-up question based on what the narrator just said. If Dad mentions "Uncle Chen" in passing, the AI will return to that name in a future session. If Grandma mentions she lived in Chengdu, the AI will explore that chapter of her life more deeply.

### 9 Life Domains
Systematic coverage of a whole life:
1. Origins & Childhood (出身与童年)
2. Growing Up (成长岁月)
3. Family History (家族历史)
4. Love & Partnership (爱情与伴侣)
5. Work & Career (工作与事业)
6. Places & Journeys (地方与旅途)
7. Historical Moments (历史时刻)
8. Family Milestones (家庭里程碑)
9. Values & Wisdom (价值观与智慧)

### Three Interview Modes

| Mode | How it works | Best for |
|------|-------------|----------|
| **Direct** | You relay questions and answers manually | WeChat users, elderly relatives |
| **WhatsApp** | Skill messages narrator directly | Parents comfortable with WhatsApp |
| **In-conversation** | Parent is present with you now | In-person sessions |

### WeChat Support (Relay Mode)
WeChat doesn't have a public bot API, so Memorist Agent generates copy-paste ready questions in Chinese that you send manually. Your parent replies in WeChat, you paste the answer back. Simple and private.

### Bilingual
Interview in English, Chinese, or both. Questions and compiled chapters are generated in the narrator's language. Summaries can be generated in both languages for bilingual families.

### Local-First Privacy
```
~/.openclaw/memorist_agent/
├── narrators.json
└── narrators/{id}/
    ├── profile.json
    ├── entities.json        ← People, places, years map
    ├── sessions.json
    ├── fragments/           ← Raw story fragments
    ├── chapters/            ← Compiled memoir chapters
    └── exports/             ← Final export files
```

No cloud. No account. No subscription.

### Family Co-editing
The Openclaw user sees every fragment and chapter as it's created. During `/memorist_agent compile`, they can review, edit, and annotate each chapter before it's finalized. Changes are tracked with timestamps.

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/memorist_agent setup` | Add a narrator |
| `/memorist_agent interview [--narrator NAME] [--domain DOMAIN]` | Conduct an interview session |
| `/memorist_agent remind [--narrator NAME]` | Send narrator a warm reminder |
| `/memorist_agent stories [--narrator NAME]` | Browse story fragments |
| `/memorist_agent entities [--narrator NAME]` | View the entity map |
| `/memorist_agent compile [--narrator NAME]` | Compile into memoir chapters |
| `/memorist_agent export [--narrator NAME] [--format md\|json\|txt]` | Export memoir |
| `/memorist_agent share [--narrator NAME]` | Share with family |
| `/memorist_agent status` | Overview of all narrators |

---

## Why This Exists

The average person carries 70+ years of unrepeatable experience. Most of it is never recorded. Existing memoir services are either English-only, cloud-based, or require the narrator to download an app.

This skill is designed for:
- Adult children of first-generation immigrants
- Families with elderly relatives in China, where WeChat is the only IM
- Anyone who wants to capture stories privately, without a subscription
- Bilingual families where English and Chinese are both spoken

---

## License

MIT — free to use, modify, and share.
