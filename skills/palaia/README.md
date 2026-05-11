# Palaia — The Knowledge OS for OpenClaw Agent Teams

**Crash-safe. Local-first. Zero-cloud. The memory system that makes your agents smarter over time.**

[![CI](https://github.com/iret77/palaia/actions/workflows/ci.yml/badge.svg)](https://github.com/iret77/palaia/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/palaia)](https://pypi.org/project/palaia/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Plugin](https://img.shields.io/badge/OpenClaw-Plugin-blueviolet)](https://openclaw.ai)

---

## Install

### Recommended (OpenClaw)

Paste this prompt into your OpenClaw agent:

> Install or update the Palaia memory skill from ClawHub to the latest version (even if already present). Read the SKILL.md completely and follow it step by step. Run `palaia init`, then `palaia doctor --fix` and resolve all warnings — don't stop until the doctor report is clean. Set up completely.

That's it. The agent handles everything: installation, plugin setup, configuration, and verification.

### Manual / Expert Setup

> **Note:** Manual installation must achieve the same result as the prompt above. Follow all steps — skipping any will leave you with a partial setup.

1. Install CLI and plugin:
```bash
pip install "palaia[fastembed]"
npm install -g @byte5ai/palaia@latest
```

2. Configure OpenClaw plugin (read-then-append, never overwrite existing arrays):
```bash
PALAIA_PATH="$(npm root -g)/@byte5ai/palaia"
```
Add to your `openclaw.json`:
```json
{
  "plugins": {
    "load": { "paths": ["<PALAIA_PATH>"] },
    "allow": ["..existing..", "palaia"],
    "slots": { "memory": "palaia" },
    "entries": { "palaia": { "enabled": true } }
  }
}
```

3. Initialize and verify:
```bash
openclaw gateway restart
palaia init
palaia doctor --fix        # Resolve ALL warnings
palaia warmup
```

4. Read the SKILL.md bundled with the plugin — it contains the complete usage guide, onboarding flow, and agent field guide that the recommended prompt would walk through automatically.

**Upgrading from v1.x?** Run `palaia doctor --fix` to get the new optimized defaults.

## Quick Start

```bash
palaia init                                         # Initialize store
palaia write "API rate limit is 100 req/min" \
  --type memory --tags api,limits                   # Save knowledge
palaia query "what's the rate limit"                # Find it by meaning
```

---

## Why Palaia?

### WAL-Backed Crash Safety
Every write goes through a write-ahead log before touching storage. Power loss mid-write? Palaia recovers automatically on next startup. No data loss. No corruption. No "oops."

### Intelligent Tiering
Memories automatically organize by usage: HOT (active), WARM (recent), COLD (archived). Frequently accessed entries stay fast. Nothing gets deleted — old memories fade to background storage.

### Structured Entry Types
Not all knowledge is equal. Classify entries as `memory` (facts, decisions), `process` (workflows, checklists), or `task` (action items with status, priority, assignee). Query by type for focused results.

### Multi-Agent Collaboration
Multiple agents share one store with scope-based access control. Private entries stay private. Team entries are shared. Projects group related knowledge. Inter-agent memos enable async communication.

### Zero-Cloud Architecture
Everything runs on your machine. No API keys required for core functionality. No database server. No cloud dependency. Your data never leaves your infrastructure.

### Adaptive Nudging
Palaia teaches agents good habits through CLI output hints — then stops once they learn. The graduation system tracks consecutive successes and retires nudges when agents demonstrate independence. Regression detection re-activates nudges if habits slip.

### OpenClaw-Native
Built as a first-class OpenClaw plugin. Auto-capture of significant exchanges. Query-based contextual recall before each prompt. LLM-powered knowledge extraction. Configurable capture levels from conservative to aggressive.

---

## Features

| Feature | Details |
|---------|---------|
| **Semantic Search** | Find by meaning, not keywords. Providers: fastembed, sentence-transformers, OpenAI, Gemini, Ollama, BM25 |
| **Crash-Safe Writes** | WAL-backed — survives power loss, kills, OOM |
| **Auto-Capture** | OpenClaw plugin captures significant exchanges automatically |
| **Structured Types** | memory, process, task — with status, priority, assignee fields |
| **Multi-Agent** | Shared store, scopes (private/team/public), agent aliases, inter-agent memos |
| **Smart Tiering** | HOT → WARM → COLD rotation based on access patterns |
| **Garbage Collection** | Automatic tier rotation, WAL cleanup, stale entry management |
| **OpenClaw Plugin** | Drop-in replacement for built-in memory — query-based recall, auto-capture, LLM extraction |
| **Embedding Server** | Long-lived subprocess keeps the model loaded — queries in ~0.5s instead of 6-16s |
| **Projects** | Group entries by project with default scopes and ownership |
| **Document Ingestion** | Index PDFs, HTML, Markdown for RAG search |
| **Adaptive Nudging** | Teaches agents best practices, graduates when they learn |

---

## Comparison

| Feature | Palaia | Stock Memory | Mem0 | Engram |
|---------|--------|-------------|------|--------|
| Local-first | Yes | Yes | No (cloud) | Yes |
| Crash-safe (WAL) | Yes | No | N/A | No |
| Auto-Capture | Yes (plugin) | No | Yes | No |
| Structured Types | Yes (memory/process/task) | No | No | No |
| Multi-Agent Scopes | Yes (private/team/public) | No | Per-user | No |
| Smart Tiering | Yes (HOT/WARM/COLD) | No | No | No |
| Garbage Collection | Yes (automatic) | Manual | Managed | Manual |
| OpenClaw Plugin | Native | Built-in | No | No |
| Semantic Search | Hybrid (embedding + BM25) | None | Embedding | Embedding |
| Zero-Cloud | Yes | Yes | No | Yes |

---

## Configuration

### Plugin Config (OpenClaw)

Set in `openclaw.json` under `plugins.entries.palaia.config`:

| Key | Default | Description |
|-----|---------|-------------|
| `memoryInject` | `true` | Inject relevant memories into agent context |
| `maxInjectedChars` | `8000` | Max characters for injected memory context |
| `autoCapture` | `true` | Capture significant exchanges automatically |
| `captureFrequency` | `"significant"` | `"every"` or `"significant"` |
| `captureMinTurns` | `2` | Minimum turns before capture |
| `captureModel` | auto | Model for LLM extraction (e.g. `"anthropic/claude-haiku-3"`) |
| `recallMode` | `"query"` | `"list"` (tier-based) or `"query"` (semantic) |
| `recallTypeWeight` | `{process:1.5, task:1.2, memory:1.0}` | Type-aware result weighting |
| `embeddingServer` | `true` | Keep embedding model loaded in a long-lived subprocess for fast queries (~0.5s vs ~6s). Falls back to CLI on failure. |

### Capture Levels

Configure via `palaia init --capture-level`:

| Level | autoCapture | Frequency | Min Turns |
|-------|-------------|-----------|-----------|
| `off` | false | — | — |
| `sparsam` | true | significant | 5 |
| `normal` | true | significant | 2 |
| `aggressiv` | true | every | 1 |

---

## Agent Alias System

Multiple agent identities can share entries through aliases. An alias maps one agent name to another, so queries and scope checks match both.

```bash
# Set alias: "default" is treated as "HAL"
palaia alias set default HAL

# List aliases
palaia alias list

# Remove alias
palaia alias remove default
```

When agent "HAL" queries, entries owned by "default" (and vice versa) are included. Useful when agents run under different names in different contexts but should share the same memory.

## Project Locking

Advisory locks prevent multiple agents from working on the same project simultaneously. Locks have a configurable TTL (default: 30 min) and auto-expire.

```bash
# Lock a project
palaia project lock myproject --agent CyberClaw --reason "refactoring"

# Check lock status
palaia project lock-status myproject

# Release lock
palaia project unlock myproject

# Force-break a stuck lock
palaia project break-lock myproject

# List all active locks
palaia project locks
```

Locks are advisory — they don't prevent writes, but agents should check before starting work on a project.

---

## CLI Reference

```
palaia init [--agent NAME] [--capture-level LEVEL]   Initialize store
palaia write "text" [--type TYPE] [--tags a,b]       Save a memory
palaia query "search" [--type TYPE] [--project P]    Search by meaning
palaia get <id>                                       Read specific entry
palaia list [--tier T] [--type T] [--status S]       List entries
palaia edit <id> [--status done]                      Edit entry
palaia status                                         System health
palaia doctor [--fix]                                 Diagnose + fix
palaia project create|list|show|query|delete          Manage projects
palaia memo send|inbox|ack|broadcast                  Inter-agent messaging
palaia ingest <source> [--project P]                  Index documents (RAG)
palaia detect                                         Available providers
palaia warmup                                         Pre-build search index
palaia migrate [--suggest]                            Import / suggest types
```

All commands support `--json` for machine-readable output.

---

## Development

```bash
git clone https://github.com/iret77/palaia.git
cd palaia
pip install -e ".[dev]"
pytest
```

640+ tests. Contributions welcome.

## Links

- [GitHub](https://github.com/iret77/palaia) — Source + Issues
- [PyPI](https://pypi.org/project/palaia/) — Package registry
- [ClawHub](https://clawhub.com/skills/palaia) — Install via agent skill
- [OpenClaw](https://openclaw.ai) — The agent platform Palaia is built for
- [CHANGELOG](CHANGELOG.md) — Release history

---

MIT — (c) 2026 [byte5 GmbH](https://byte5.de)
