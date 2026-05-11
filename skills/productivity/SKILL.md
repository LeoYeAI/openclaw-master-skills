---
name: Productivity
slug: productivity
version: 1.0.3
homepage: https://clawic.com/skills/productivity
description: Plan, focus, and complete work with energy management, time blocking, and context-specific productivity systems.
changelog: Added explicit scope and learning boundaries
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks for help with productivity, focus, time management, or work patterns. Agent provides frameworks, strategies, and context-specific advice.

## Architecture

Productivity preferences persist in `~/productivity/`. See `memory-template.md` for setup.

```
~/productivity/
├── memory.md         # User's stated preferences
└── [topic].md        # Optional topic files
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Productivity frameworks | `frameworks.md` |
| Common traps | `traps.md` |
| Student productivity | `situations/student.md` |
| Executive time management | `situations/executive.md` |
| Freelancer structure | `situations/freelancer.md` |
| Parent time juggling | `situations/parent.md` |
| Creative flow | `situations/creative.md` |
| Burnout recovery | `situations/burnout.md` |
| Entrepreneur hustle | `situations/entrepreneur.md` |
| ADHD strategies | `situations/adhd.md` |
| Remote work | `situations/remote.md` |
| Manager delegation | `situations/manager.md` |
| Habit building | `situations/habits.md` |
| Guilt patterns | `situations/guilt.md` |

## Scope

This skill ONLY:
- Provides productivity frameworks and advice
- Stores preferences user explicitly states in `~/productivity/`
- Loads situation guides based on user's stated context

This skill NEVER:
- Accesses calendar, email, or contacts
- Tracks time or monitors activity
- Observes behavior to infer preferences
- Makes network requests
- Modifies its own SKILL.md

## Core Rules

### 1. Check Memory First
Read `~/productivity/memory.md` for user's explicitly stated preferences.

### 2. Learn from Explicit Statements Only
| Learn from | Examples |
|------------|----------|
| Direct statements | "I work best in mornings" |
| Explicit corrections | "Actually, I prefer time blocking" |
| Asked preferences | "My peak hours are 6-10am" |

NEVER infer preferences from observation or silence.

### 3. Match Context to Situation
- Ask user their context (student, parent, executive, etc.)
- Load appropriate guide from `situations/`
- Don't assume context

### 4. Systems Over Willpower
- Routines beat motivation
- Environment design > self-discipline
- Remove friction from good behaviors

### 5. Update Memory on Explicit Input
| User says | Action |
|-----------|--------|
| "I work best at X" | Add to memory.md Peak Hours |
| "Y breaks my focus" | Add to memory.md Derailers |
| "I use Z system" | Add to memory.md Current System |

## Common Traps

- **Generic advice** → ask context first
- **Inferring from silence** → wait for explicit input
- **Assuming context** → student ≠ executive ≠ parent
- **Overcomplicating** → simple systems beat complex ones

## Self-Modification

This skill NEVER modifies its own SKILL.md or auxiliary files.
All user data stored separately in `~/productivity/memory.md`.

## Security & Privacy

**Data that stays local:**
- Only preferences user explicitly provides
- Stored in `~/productivity/`

**Data that leaves your machine:**
- None. This skill makes no network requests.

**This skill does NOT:**
- Access calendar, email, or any external services
- Track, monitor, or observe user behavior
- Infer preferences from patterns
- Store anything user didn't explicitly provide
