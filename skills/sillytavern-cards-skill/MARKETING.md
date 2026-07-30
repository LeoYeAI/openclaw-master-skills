# Marketing Plan: sillytavern-cards-skill

## Core Message

**"Chat with your SillyTavern characters on WhatsApp, Telegram, Discord — and they actually remember you."**

Three hooks that differentiate us:
1. **No self-hosting a web app** — import a card, chat on the apps you already use
2. **Persistent memory** — your character remembers you across sessions (ST can't do this)
3. **Soul mode** — AI boyfriend/girlfriend that also helps with real tasks

---

## Launch Sequence (Week 1-4)

### Week 1: Foundation

| Action | Channel | Details |
|--------|---------|---------|
| Publish to ClawHub | `clawhub publish .` | Official registry. Required first step. Use tags: `roleplay`, `sillytavern`, `character-cards`, `companion` |
| Post to OpenClaw Discord | #skills or #showcase | Short demo + link. "Built a skill that imports SillyTavern character cards into OpenClaw. Supports play/soul/chat modes." |
| Post to SillyTavern Discord | Extension/community channel | Frame as: "For ST users who also use OpenClaw — you can now import your cards and chat with characters on WhatsApp/Telegram." |
| Submit to awesome-openclaw-skills | GitHub PR | https://github.com/VoltAgent/awesome-openclaw-skills — PR with description and link |
| Submit to awesome-openclaw | GitHub PR | https://github.com/vincentkoc/awesome-openclaw — PR to add under integrations |

### Week 2: Reddit

**r/SillyTavernAI** (~73K members)
```
Title: I built an OpenClaw skill that lets you chat with SillyTavern characters on WhatsApp/Telegram

Body:
I kept wishing I could talk to my ST characters on my phone without
setting up port forwarding or a reverse proxy. So I built a skill that
imports TavernAI V2 character cards into OpenClaw.

What it does:
- Import cards from Chub.ai, CharaVault, or local PNG/JSON files
- Three modes: play (pure RP), soul (character personality + assistant),
  chat (temporary tryout)
- The character REMEMBERS you across sessions via SOUL.md + MEMORY.md
- Search Chub.ai and CharaVault directly from chat

The "soul" mode is my favorite — your character has a personality and talks
like themselves, but can also do normal assistant stuff. Like an AI boyfriend
who can also check your calendar.

GitHub: [link]
License: AGPL-3.0 (same as SillyTavern)

Happy to answer questions. Feedback welcome.
```

**r/LocalLLaMA** (~650K members)
```
Title: OpenClaw skill for SillyTavern character cards — persistent memory + messaging app integration

Body:
[Similar to above but more technical. Emphasize:]
- Zero dependencies (pure Node.js PNG parser)
- Works with any LLM backend OpenClaw supports
- Three interaction modes with different SOUL.md strategies
- Clean-room reimplementation of TavernAI V2 spec (no ST code, AGPL-safe)
- Searches Chub.ai + CharaVault APIs (both free, no auth needed)
```

**r/OpenClaw** / **r/AI_Agents**
```
Title: New skill: import SillyTavern character cards for roleplay/companion AI

Body: [Short, link to repo, emphasize soul mode as the novel feature]
```

**r/selfhosted** (if relevant)
```
Title: Open source OpenClaw skill for AI companion chat with persistent memory

Body: [Emphasize self-hosted, AGPL license, no cloud dependency, privacy]
```

### Week 3: Content & Chinese Markets

**Twitter/X:**
- Thread with screenshots/screen recording showing the flow:
  1. `/character search 温柔男友`
  2. Pick a result, auto-downloads from Chub.ai
  3. `/character soul Daniel`
  4. Chat with Daniel on WhatsApp, he remembers yesterday's conversation
- Tag @openclaw
- Use hashtags: #OpenClaw #SillyTavern #AIRoleplay #AICompanion

**Bilibili (B站):**
- Record a 5-10 min demo video in Chinese
- Title: 「用龙虾玩酒馆角色卡！三种模式：扮演/灵魂/聊天」
- Show: importing a card, soul mode with WeChat/Telegram, memory persistence
- Link to GitHub in description
- Tags: SillyTavern, 酒馆, OpenClaw, 龙虾, AI男友, 角色卡

**V2EX:**
- Post in 分享创造 (Share & Create) node
- Title: 开源 OpenClaw 技能：导入酒馆角色卡，在微信/Telegram 上和角色聊天
- Technical but accessible write-up

**小红书:**
- Visual post showing character chat screenshots
- Focus on the "AI boyfriend" angle
- Title: 用龙虾养了一个AI男朋友，他还记得我昨天说了什么
- Less technical, more lifestyle/emotional angle

### Week 4: Long-tail

**Hacker News (Show HN):**
```
Title: Show HN: OpenClaw skill for SillyTavern character cards with persistent memory

Body: [2-3 sentences. Link to repo. Emphasize the technical novelty:
character persona via SOUL.md, keyword-triggered lorebook via MEMORY.md,
clean-room TavernAI V2 parser]
```

**Dev.to / Medium:**
- Write a technical blog post: "How I Built a SillyTavern Character Card Engine for OpenClaw"
- Cover: TavernAI V2 spec, PNG tEXt chunk parsing, SOUL.md/MEMORY.md architecture, three modes
- Cross-post to both platforms

**Product Hunt:**
- Only if you have a polished demo/landing page
- Best saved for when the full OpenClaw fork (not just the skill) is ready

---

## Ongoing (Month 2+)

| Action | Frequency | Channel |
|--------|-----------|---------|
| Reply to "how to use ST on phone" threads | Ongoing | Reddit, Discord |
| Share user testimonials / cool use cases | Weekly | Twitter, Discord |
| Update skill and announce new features | Per release | ClawHub, Discord, Reddit |
| Engage with ST extension developers | Ongoing | SillyTavern Discord |
| Create character card packs (curated collections) | Monthly | GitHub, Chub.ai |

---

## Key Metrics to Track

- GitHub stars and forks
- ClawHub install count
- Discord mentions / questions
- Reddit post upvotes and comment engagement
- Bilibili video views

---

## Content Calendar

| Date | Action | Channel |
|------|--------|---------|
| Day 1 | Publish to ClawHub | ClawHub |
| Day 1 | Post in OpenClaw Discord | Discord |
| Day 2 | Post in SillyTavern Discord | Discord |
| Day 3 | Submit PRs to awesome-* lists | GitHub |
| Day 7 | Post to r/SillyTavernAI | Reddit |
| Day 8 | Post to r/LocalLLaMA | Reddit |
| Day 9 | Post to r/OpenClaw | Reddit |
| Day 14 | Twitter/X thread with demo | Twitter |
| Day 14 | B站 demo video | Bilibili |
| Day 15 | V2EX post | V2EX |
| Day 16 | 小红书 visual post | 小红书 |
| Day 21 | Show HN | Hacker News |
| Day 21 | Dev.to blog post | Dev.to |
| Day 28 | Review metrics, plan month 2 | Internal |

---

## Don't Do

- Don't spam multiple subreddits on the same day (Reddit flags this)
- Don't be salesy — frame everything as "I built this, here's how it works"
- Don't post in r/CharacterAI about leaving their platform (comes across as hostile)
- Don't post in r/selfhosted without being transparent about limitations
- Don't use marketing language on Hacker News (instant downvotes)

---

## Audience-Specific Messaging

| Audience | Hook |
|----------|------|
| **SillyTavern users** | "Use your existing cards on WhatsApp/Telegram, no port forwarding needed" |
| **OpenClaw users** | "Give your agent a personality — it remembers you like a real companion" |
| **r/LocalLLaMA** | "Clean-room TavernAI V2 parser, zero deps, works with any backend" |
| **Chinese users** | "在微信上和酒馆角色卡聊天，TA 还记得你" |
| **AI boyfriend/girlfriend seekers** | "An AI companion that actually remembers your conversations" |
| **Developers** | "AGPL-3.0, clean architecture, three interaction modes via SOUL.md" |
