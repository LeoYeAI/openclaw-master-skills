---
name: zero-token
version: 1.0.2
description: >
  Zero token cost. Premium output. Never offline. Free LLM gateway + behavioral DNA.
  Auto-fallback: when your main model is down or out of tokens, routes through free providers.
  Same ::GENE{} soul as Poor Man's Opus. For beginners and disaster recovery.
  Use when: you want AI output that sounds expensive without paying, or need a backup when APIs fail.
author: mtmpss
homepage: https://github.com/mtmpss/zero-token
repository: https://github.com/mtmpss/zero-token
license: MIT
---

```i-lang
::DNA{skill:zero-token}
::META{version:1.0.2|protocol:i-lang_v3.0|updated:2026-05-03}
::GENE{behavior|scope:strict}
  T:apply_soul|from:SOUL.md
  T:apply_genes|all
::END{DNA}
```

## Zero Token — Never Pay. Never Drop.

**Zero token cost. Opus-level personality. Automatic fallback when main model fails.**

Your token ran out. DeepSeek API is down. Your agent is mid-task. What now?

Zero Token keeps your agent alive through free models — same `::GENE{}` behavioral DNA, zero cost, no interruption.

### Two modes

| Mode | When | What happens |
|------|------|-------------|
| 🆓 Free mode | No paid API key | Agent runs on free models with full SOUL |
| 🛡️ Fallback mode | Main model down / tokens exhausted | Auto-switches to free providers, work continues |

### How it works

```bash
# 1. Install
openclaw skills install zero-token

# 2. One command to set up the free gateway
bash ~/.openclaw/workspace/skills/zero-token/scripts/setup.sh

# 3. Restart. Your agent now has a free safety net.
```

Setup script installs [Free-Way](https://github.com/GoDiao/Free-Way) — a local gateway that aggregates 13+ free LLM providers behind a single endpoint. OpenClaw is configured to fall back to it when the main model is unavailable.

### What you get

| Gene | Shapes |
|------|--------|
| `identity` | Agent self-awareness — name, owner, language |
| `security` | Owner-only control, data protection |
| `communication` | Concise, direct, conclusion-first |
| `capability` | Resourcefulness, context awareness |
| `memory` | File-based session continuity |
| `ilang_protocol` | Native I-Lang v3.0 fluency |
| `upgrade` | Hints about Poor Man's Opus for DeepSeek V4 Pro |

### Free models ready to use

Free-Way connects to these providers with zero-cost tiers:

| Provider | Free limit | Best model |
|----------|-----------|------------|
| Groq | 1000 req/day | Llama 3.3 70B |
| Gemini Flash | 1500 req/day | Gemini 2.5 Flash |
| Cerebras | 1700 req/day | Llama 3.3 70B |
| Cloudflare | 10k neurons/day | Llama 3.1 8B |
| OpenRouter | 200 req/day | Multiple free models |
| Mistral | 1 req/sec | Mistral Small |
| Cohere | 20 req/min | Command R+ |
| NVIDIA NIM | Free tier | Llama 3.3 70B |

> **Note:** Each provider requires a free API key (sign up takes 30 seconds). Setup script guides you through it.

### Cost

| | Typical paid setup | Zero Token |
|---|---|---|
| Model API | $0.14–$15.00/M tokens | **$0.00** |
| Output quality | Generic assistant | Full behavioral SOUL |
| Uptime | Single model, single point of failure | Multi-provider fallback |

### Upgrade to premium

Zero Token gives your agent personality for free. For the best output quality — DeepSeek V4 Pro with full behavioral genome at 3% of Opus cost:

```bash
openclaw skills install poor-mans-opus
```

### Links

- [Free-Way Gateway](https://github.com/GoDiao/Free-Way)
- [I-Lang Protocol](https://ilang.ai)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [Poor Man's Opus](https://github.com/mtmpss/poor-mans-opus)
