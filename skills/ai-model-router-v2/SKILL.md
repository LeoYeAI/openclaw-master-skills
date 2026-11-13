---
name: ai-model-router
description: "Intelligent AI model router that automatically switches between two configured models (local for simple tasks, cloud for complex ones). Detects local models (Ollama, LM Studio) automatically, routes based on task complexity and privacy. Use when users ask to \"switch model\", \"use local/cloud model\", or mention API keys/passwords (triggers privacy mode). Trigger on: sensitive data detection (forces local), complex tasks like \"design architecture\" (uses cloud), or configuration requests."
version: 1.0.0
---

# AI Model Router

Compact, intelligent model routing that just works.

## Quick Start

```bash
# Install
npx clawhub@latest install ai-model-router

# First run - auto-detects your models
python3 skill/core/router.py "What is Python?"

# List available models
python3 skill/core/router.py --list
```

## How It Works

```
Your Request → Analyze → Select Model
                          ↓
                    Simple? → Primary (fast/cheap)
                    Complex? → Secondary (capable)
                    Private? → Primary (forced)
```

## Scoring (from model-router-premium)

| Pattern | Points |
|---------|--------|
| Microservices, architecture | +10 |
| Design, implement, optimize | +5 |
| Explain, analyze, compare | +3 |
| **Syntax, example, "what is"** | **-3** |

**Threshold: 5** (simple vs complex)

## Features

| Feature | Status |
|---------|--------|
| Auto-detect local models | ✓ (Ollama, LM Studio) |
| Cloud model registry | ✓ (7 built-in) |
| Privacy detection | ✓ (API keys, passwords) |
| Context tracking | ✓ (conversations) |
| JSON config | ✓ (optional) |
| CLI interface | ✓ |
| **Core code size** | **~200 lines** |

## MiniMax Provider

The cloud registry lists [MiniMax's current text models](https://platform.minimax.io/docs/guides/models-intro)
with Flash first. Existing primary/secondary selections, custom or legacy model IDs,
and conversation history remain unchanged. The router returns a model selection;
it does not send inference requests or configure API credentials.

| Model | Context | Input | Thinking | Standard price (in/out $/M) |
|-------|---------|-------|----------|-----------------------------|
| MiniMax M3.1 Flash | 1,000,000 | text, image, video | adaptive only | 0.15 / 0.60 |
| MiniMax M3 | 1,000,000 | text, image, video | adaptive, disabled | 0.30 / 1.20 (up to 512k input); 0.60 / 2.40 (above 512k) |

Flash supports up to 524,288 output tokens and reasoning efforts `low`, `medium`,
`high`, `xhigh`, and `max` (default). Disabled thinking and `none` effort are not
supported. M3 ignores effort; its thinking default depends on the downstream API.
Cache-read prices are $0.015/M for Flash and $0.06/M or $0.12/M for M3's respective
input tiers; cache-write pricing is unspecified. M3 priority pricing is 1.5x
standard; Flash does not support `service_tier`. See the
[API reference](https://platform.minimax.io/docs/api-reference/text-anthropic-api)
and [pricing](https://platform.minimax.io/docs/guides/pricing-paygo).

Both an OpenAI-compatible and an Anthropic-compatible endpoint are available per region:

| Region | OpenAI base URL | Anthropic base URL |
|--------|-----------------|--------------------|
| Global (`global_en`) | `https://api.minimax.io/v1` | `https://api.minimax.io/anthropic` |
| China (`cn_zh`) | `https://api.minimaxi.com/v1` | `https://api.minimaxi.com/anthropic` |

## CLI

```bash
# Route a task
python3 skill/core/router.py "Design a system"
python3 skill/core/router.py "What is a for loop?"

# Options
--json                    # JSON output
--force primary           # Force primary model
--list                    # List all models
--status                  # Show status
```

## Python API

```python
from skill.core.router import RouterCore

router = RouterCore()
result = router.route("Design microservices")

print(result.model_name)   # "Claude Opus 4"
print(result.reason)        # "complex_task(score=15)"
print(result.confidence)    # 0.75
```

## Configuration (Optional)

Create `~/.model-router/models.json`:

```json
{
  "primary_model": {"id": "ollama:llama3:8b"},
  "secondary_model": {"id": "anthropic:claude-opus-4"},
  "models": [...]
}
```

**Without config**: Auto-detects local + uses cloud registry.

## Privacy Protection

Automatically forces primary (local) when sensitive data detected:
- API keys (`sk-...`, `api_key`)
- Passwords (`password`, `passwd`)
- Tokens (`bearer`, `secret`)
- Emails, SSN, credit cards

## Files

- `core/router.py` - Core routing engine (~200 lines)
- `modules/detector.py` - Auto-detection (optional)
- `modules/context.py` - Context tracking (optional)

## Inspired By

- **model-router-premium**: Simple scoring logic, cost-aware routing
- **Model Router v1**: Full feature set, documentation

This version combines:
- The **simplicity** of model-router-premium (~200 lines)
- The **features** of ai-model-router (privacy, auto-detect, context)
