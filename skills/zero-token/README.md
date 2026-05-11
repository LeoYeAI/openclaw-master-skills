# Zero Token

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![I-Lang Protocol](https://img.shields.io/badge/I--Lang-v3.0-green.svg)](https://ilang.ai)

🌐 [简体中文](README.zh-CN.md)

**Zero cost. Premium output. Never offline.**

Your token ran out. DeepSeek API is down. Your agent is mid-task. What now?

Zero Token gives your agent two things:
1. A personality — the same `::GENE{}` behavioral DNA from Poor Man's Opus
2. A safety net — automatic fallback through free LLM providers when the main model fails

One install. One setup command. Your agent survives API outages, token exhaustion, and bill shock.

---

## Why this exists

Poor Man's Opus makes DeepSeek output like Opus at 3% cost. Zero Token makes ANY model output premium — for free. Use it as your entry point, your backup, or both.

---

## Install & activate

```bash
# 1. Install the skill
openclaw skills install zero-token

# 2. Run setup
bash ~/.openclaw/workspace/skills/zero-token/scripts/setup.sh

# 3. Get at least one free API key (30 seconds):
#    - Gemini: https://aistudio.google.com/apikey
#    - Groq: https://console.groq.com/keys
#    - Cerebras: https://cloud.cerebras.ai

# 4. Add the key in Free-Way web console:
#    http://localhost:8787 → API Keys tab

# 5. Restart. Your agent has a free safety net.
```

---

## How it works

```
Your prompt
    │
    ▼
OpenClaw tries your main model (DeepSeek V4 Pro)
    │
    ├── ✅ Working → Normal response
    │
    └── ❌ Down / No key / Tokens exhausted
            │
            ▼
        Free-Way Gateway (localhost:8787)
            │
            ├── Groq (Llama 3.3 70B)
            ├── Gemini Flash 2.5
            ├── Cerebras
            ├── OpenRouter
            ├── Cloudflare
            └── ... 13+ providers
            │
            ▼
        Response — same ::GENE{} DNA applied
```

---

## Free model lineup

| Provider | Free daily limit | Best model | Signup time |
|----------|-----------------|------------|-------------|
| Gemini Flash | 1,500 req | Gemini 2.5 Flash | 30 sec |
| Groq | 1,000 req | Llama 3.3 70B | 30 sec |
| Cerebras | 1,700 req | Llama 3.3 70B | 30 sec |
| OpenRouter | 200 req | Multiple | 30 sec |
| Cloudflare | 10k neurons | Llama 3.1 8B | 1 min |
| Mistral | 1 req/sec | Mistral Small | 30 sec |
| Cohere | 20 req/min | Command R+ | 30 sec |
| NVIDIA NIM | Free tier | Llama 3.3 70B | 1 min |

---

## When to use what

| Scenario | Use |
|----------|-----|
| First time trying agent skills | **Zero Token** — free, instant |
| Main model daily production | **Poor Man's Opus** — DeepSeek V4 Pro, $1.74/M |
| Backup when API is down | **Zero Token** — auto-switches to free models |
| Max output quality | **Poor Man's Opus** — full behavioral genome |

---

## Upgrade path

Zero Token has the same behavioral DNA. When you want the best:

```bash
openclaw skills install poor-mans-opus
```

DeepSeek V4 Pro + full SOUL genome = Opus output at 3% cost.

---

## What's inside

- `SOUL.md` — 7-gene behavioral profile (ClawScan-safe)
- `SKILL.md` — Skill manifest
- `scripts/setup.sh` — One-command Free-Way gateway installer

---

## Links

- [Free-Way Gateway](https://github.com/GoDiao/Free-Way) — local free LLM aggregator
- [Poor Man's Opus](https://github.com/mtmpss/poor-mans-opus) — premium version
- [I-Lang Protocol](https://ilang.ai)

MIT License
