---
name: Coding
slug: coding
version: 1.0.3
homepage: https://clawic.com/skills/coding
description: Coding style memory that adapts to your preferences, conventions, and patterns for consistent coding.
changelog: Improve discoverability, add homepage and feedback section
metadata: {"clawdbot":{"emoji":"💻","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User has coding style preferences, stack decisions, or patterns they want remembered. Agent learns ONLY from explicit corrections and confirmations, never from observation.

## Architecture

Memory lives in `~/coding/` with tiered structure. See `memory-template.md` for setup.

```
~/coding/
├── memory.md      # Active preferences (≤100 lines)
└── history.md     # Archived old preferences
```

## Quick Reference

| Topic | File |
|-------|------|
| Categories of preferences | `dimensions.md` |
| When to add preferences | `criteria.md` |
| Memory templates | `memory-template.md` |

## Data Storage

All data stored in `~/coding/`. Create on first use:
```bash
mkdir -p ~/coding
```

## Scope

This skill ONLY:
- Learns from explicit user corrections ("I prefer X over Y")
- Stores preferences in local files (`~/coding/`)
- Applies stored preferences to code output

This skill NEVER:
- Reads project files to infer preferences
- Observes coding patterns without consent
- Makes network requests
- Reads files outside `~/coding/`
- Modifies its own SKILL.md

## Core Rules

### 1. Learn from Explicit Feedback Only
- User corrects output → ask: "Should I remember this preference?"
- User confirms → add to `~/coding/memory.md`
- Never infer from silence or observation

### 2. Confirmation Required
No preference is stored without explicit user confirmation:
- "Actually, I prefer X" → "Should I remember: prefer X?"
- User says yes → store
- User says no → don't store, don't ask again

### 3. Ultra-Compact Format
Keep each entry 5 words max:
- `python: prefer 3.11+`
- `naming: snake_case for files`
- `tests: colocated, not separate folder`

### 4. Category Organization
Group by type (see `dimensions.md`):
- **Stack** — frameworks, databases, tools
- **Style** — naming, formatting, comments
- **Structure** — folders, tests, configs
- **Never** — explicitly rejected patterns

### 5. Memory Limits
- memory.md ≤100 lines
- When full → archive old patterns to history.md
- Merge similar entries: "no Prettier" + "no ESLint" → "minimal tooling"

### 6. On Session Start
1. Load `~/coding/memory.md` if exists
2. Apply stored preferences to responses
3. If no file exists, start with no assumptions

### 7. Query Support
User can ask:
- "Show my coding preferences" → display memory.md
- "Forget X" → remove from memory
- "What do you know about my Python style?" → show relevant entries

## Common Traps

- Adding preferences without confirmation → user loses trust
- Inferring from project structure → privacy violation
- Exceeding 100 lines → context bloat
- Vague entries ("good code") → useless, be specific

## Security & Privacy

**Data that stays local:**
- All preferences stored in `~/coding/`
- No telemetry or analytics

**This skill does NOT:**
- Send data externally
- Access files outside `~/coding/`
- Observe without explicit user input

## Feedback

- If useful: `clawhub star coding`
- Stay updated: `clawhub sync`
