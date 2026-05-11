---
name: ai-model-router
description: Intelligent AI model router that automatically switches between two configured models (local for simple tasks, cloud for complex ones). Detects local models (Ollama, LM Studio) automatically, routes based on task complexity and privacy. Use when users ask to "switch model", "use local/cloud model", or mention API keys/passwords (triggers privacy mode). Trigger on: sensitive data detection (forces local), complex tasks like "design architecture" (uses cloud), or configuration requests.
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
