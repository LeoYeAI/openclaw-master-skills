# 🎢 FreeRide

### Stop paying for AI. Start riding free.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://github.com/openclaw/openclaw)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-30%2B%20Free%20Models-orange.svg)](https://openrouter.ai)

---

**FreeRide** gives you unlimited free AI in [OpenClaw](https://github.com/openclaw/openclaw) by automatically managing OpenRouter's free models.

```
You: *hits rate limit*
FreeRide: "I got you." *switches to next best model*
You: *keeps coding*
```

## The Problem

You're using OpenClaw. You love it. But:

- 💸 API costs add up fast
- 🚫 Free models have rate limits
- 😤 Manually switching models is annoying
- 🤷 You don't know which free model is actually good

## Installation

```bash
npx clawhub@latest install free-ride
```

Or clone manually:

```bash
git clone https://github.com/Shaivpidadi/FreeRide.git
cd FreeRide
pip install -r requirements.txt
```

## The Solution

One command. Free AI. Forever.

```bash
freeride auto
```

That's it. FreeRide:

1. **Finds** the 30+ free models on OpenRouter
2. **Ranks** them by quality (context length, capabilities, speed)
3. **Sets** the best one as your primary
4. **Configures** smart fallbacks for when you hit rate limits
5. **Preserves** your existing OpenClaw config

## Quick Start

### 1. Get a Free OpenRouter Key

Go to [openrouter.ai/keys](https://openrouter.ai/keys) → Create account → Generate key

No credit card. No trial. Actually free.

### 2. Set Your Key

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### 3. Run FreeRide

```bash
freeride auto
```

### 4. Restart OpenClaw

Done. You're now running on free AI with automatic fallbacks.

## What You Get

```
Primary Model: nvidia/nemotron-3-nano-30b-a3b:free (256K context)

Fallbacks:
  1. openrouter/free         ← Smart router (auto-picks best available)
  2. qwen/qwen3-coder:free   ← Great for coding
  3. stepfun/step-3.5:free   ← Fast responses
  4. deepseek/deepseek:free  ← Strong reasoning
  5. mistral/mistral:free    ← Reliable fallback
```

When you hit a rate limit, OpenClaw automatically tries the next model. You keep working. No interruptions.

## Commands

| Command | What it does |
|---------|--------------|
| `freeride auto` | Auto-configure best model + fallbacks |
| `freeride list` | See all 30+ free models ranked |
| `freeride switch <model>` | Use a specific model |
| `freeride status` | Check your current setup |

### Pro Tips

```bash
# Already have a model you like? Just add fallbacks:
freeride auto -f

# Want more fallbacks for maximum uptime?
freeride auto -c 10

# Coding? Switch to the best coding model:
freeride switch qwen3-coder

# See what's available:
freeride list -n 30
```

## How It Ranks Models

FreeRide scores each model (0-1) based on:

| Factor | Weight | Why |
|--------|--------|-----|
| Context Length | 40% | Longer = handle bigger codebases |
| Capabilities | 30% | Vision, tools, structured output |
| Recency | 20% | Newer models = better performance |
| Provider Trust | 10% | Google, Meta, NVIDIA, etc. |

The **smart fallback** `openrouter/free` is always first - it auto-selects based on what your request needs.

## FAQ

**Is this actually free?**

Yes. OpenRouter provides free tiers for many models. You just need an account (no credit card).

**What about rate limits?**

That's the whole point. FreeRide configures multiple fallbacks. When one model rate-limits you, OpenClaw automatically switches to the next.

**Will it mess up my OpenClaw config?**

No. FreeRide only touches the model settings. Your gateway, channels, plugins, workspace - all preserved.

**Which models are free?**

Run `freeride list` to see current availability. It changes, which is why FreeRide exists.

## The Math

| Scenario | Monthly Cost |
|----------|--------------|
| GPT-4 API | $50-200+ |
| Claude API | $50-200+ |
| OpenClaw + FreeRide | **$0** |

You're welcome.

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed
- Python 3.8+
- `requests` library (`pip install requests`)
- Free OpenRouter account

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  You         │ ──→ │  FreeRide    │ ──→ │  OpenRouter API  │
│  "freeride   │     │              │     │  (30+ free       │
│   auto"      │     │  • Fetch     │     │   models)        │
└──────────────┘     │  • Rank      │     └──────────────────┘
                     │  • Configure │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ ~/.openclaw/ │
                     │ openclaw.json│
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  OpenClaw    │
                     │  (free AI!)  │
                     └──────────────┘
```

## Contributing

Found a bug? Want a feature? PRs welcome.

```bash
# Run tests
python main.py list
python main.py status
python main.py auto --help
```

## Related Projects

- [OpenClaw](https://github.com/openclaw/openclaw) - The AI coding agent
- [OpenRouter](https://openrouter.ai) - The model router
- [ClaHub](https://github.com/clawhub) - Skill marketplace

## License

MIT - Do whatever you want.

---

<p align="center">
  <b>Stop paying. Start riding.</b>
  <br>
  <br>
  <a href="https://github.com/Shaivpidadi/FreeRide">⭐ Star us on GitHub</a>
  ·
  <a href="https://openrouter.ai/keys">🔑 Get OpenRouter Key</a>
  ·
  <a href="https://github.com/openclaw/openclaw">🦞 Install OpenClaw</a>
</p>
