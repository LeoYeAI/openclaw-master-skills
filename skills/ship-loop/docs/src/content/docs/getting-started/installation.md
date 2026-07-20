---
title: Installation
description: How to install Ship Loop
---

## From PyPI

```bash
pip install shiploop
```

Requires Python 3.10 or higher.

## From Source

```bash
git clone https://github.com/fernando-fernandez3/ship-loop.git
cd ship-loop
pip install -e ".[dev]"
```

The `[dev]` extra includes `pytest` and `pytest-asyncio` for running tests.

## Verify Installation

```bash
shiploop --version
# shiploop 4.0.0
```

## Prerequisites

Ship Loop also needs:

- **Git** (for commits, tags, worktrees)
- **A coding agent CLI** installed and configured. Supported presets:
  - [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`claude`)
  - [Codex](https://github.com/openai/codex) (`codex`)
  - [Aider](https://aider.chat/) (`aider`)
  - Or any CLI that accepts a prompt via stdin
- **A deployment pipeline** triggered by push (Vercel, Netlify, etc.) if you want deploy verification
