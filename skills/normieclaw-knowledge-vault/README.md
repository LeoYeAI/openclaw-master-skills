# Knowledge Vault

**Don't have an hour? Your agent does.**

Send your agent any video, article, podcast, or document. It instantly digests the content, extracts the key takeaways, and stores it in a personal, searchable vault that grows smarter every day.

![Codex Security Verified](https://img.shields.io/badge/Codex%20Security-Verified-brightgreen?style=for-the-badge)

---

## What It Does

Stop feeling guilty about the tabs you never read and the videos you never watch. Just paste the link.

Your agent reads or watches the content in seconds, giving you the salient points, key takeaways, and exact timestamps you need. Everything is automatically categorized, tagged, and saved into your own secure vault.

The killer feature: **your agent actually learns the content.** Next time you need to recall a stat from a report you saved three months ago, just ask.

---

## Quick Start

1. **Copy the skill folder** into your agent's `skills/` directory
2. **Paste the setup prompt** from `SETUP-PROMPT.md` into your agent's chat
3. **Send a link** — any article, video, or document
4. **That's it.** Your agent digests it and stores it in your vault.

Total setup time: under 5 minutes.

---

## What You Can Digest

- 📄 **Articles & Web Pages** — strips the noise, keeps the signal
- 🎬 **YouTube Videos** — full transcript extraction with timestamps
- 📑 **PDFs & Research Papers** — handles pagination and formatting
- 🎙️ **Podcasts** — transcription and key moment extraction
- 🐦 **Twitter/X Threads** — captures the full thread with context
- 💬 **Reddit Discussions** — OP + top comments synthesized
- 💻 **GitHub Repos** — README and core logic breakdown

---

## Key Features

### Instant Digestion
Every piece of content gets the same treatment:
- **Executive Summary** — what it's about in 2-4 sentences
- **Key Takeaways** — the 3-5 things that actually matter
- **Timestamps** — jump to the exact moment (video/podcast)
- **Actionable Insights** — what you can DO with this knowledge
- **Auto-Tagging** — 3-5 semantic tags for easy retrieval

### Semantic Search
Find anything by describing what you remember. "What was that video about dopamine and habits?" works just as well as searching by title.

### Agent Memory Integration
Your agent doesn't just store bookmarks — it **learns** the content. Ask questions about things you saved weeks ago and get instant answers, no digging required.

### Collections
Organize your vault into collections like "work-research", "side-projects", or "inspiration". Or just let everything live in the default collection — your call.

### Read Later Queue
Not ready to digest now? Save it for later. Come back and process your queue whenever you're ready.

### Bulk Ingestion
Dump 10 URLs at once. Your agent processes them all and gives you a summary of what it learned.

---

## Files Included

```
knowledge-vault/
├── SKILL.md ← The brain (your agent reads this)
├── SETUP-PROMPT.md ← Copy-paste setup instructions
├── README.md ← You're reading it
├── SECURITY.md ← Security audit details
├── config/
│ └── vault-config.json ← Settings you can customize
├── scripts/
│ └── vault-stats.sh ← Generate vault statistics
├── examples/
│ ├── url-ingestion-example.md
│ ├── youtube-digestion-example.md
│ └── vault-search-example.md
└── dashboard-kit/
 └── DASHBOARD-SPEC.md ← Spec for the visual dashboard add-on
```

---
