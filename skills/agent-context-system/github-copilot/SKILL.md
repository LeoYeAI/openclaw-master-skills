---
name: agent-context-system
description: Persistent local-only memory for AI coding agents. AGENTS.md (committed) + .agents.local.md (gitignored) = context that persists across sessions. Read both at start, update scratchpad at end, promote stable patterns over time.
license: See LICENSE file in repository root
metadata:
  author: AndreaGriffiths11
  version: "1.0.0"
allowed-tools: file_reader, file_writer, terminal
---

# Agent Context System

Agents start from zero every session. This skill solves that with two markdown files: one committed (`AGENTS.md`), one gitignored (`.agents.local.md`). You read both at session start, update the scratchpad at session end, and promote stable patterns over time.

## The Two-File System

- **`AGENTS.md`** — Project source of truth. Committed and shared. Under 120 lines. Contains compressed project knowledge (patterns, boundaries, gotchas, commands, architecture).
- **`.agents.local.md`** — Personal scratchpad. Gitignored. Grows over time as you log what you learn each session. Session notes, dead ends, preferences, patterns waiting for promotion.

## Workflow

### 1. Initialize

Run `./scripts/init-agent-context.sh` to create `.agents.local.md` from template, ensure it's gitignored, and wire up agent tool configs.

### 2. Work

Read both files at session start. `AGENTS.md` gives compressed project knowledge. `.agents.local.md` gives accumulated learnings from past sessions.

### 3. Grow

At session end, append to the scratchpad's Session Log: what changed, what worked, what didn't, decisions made, patterns learned.

### 4. Compress

When the scratchpad hits 300 lines, compress: deduplicate, merge related entries, keep it tight.

### 5. Promote

During compression, if a pattern recurs across 3+ sessions, flag it in the scratchpad's "Ready to Promote" section. The human decides when to move it into `AGENTS.md`.

## Get Started

When a user asks about setting up agent context:

1. **Check if `AGENTS.md` exists.** If not, they need to copy it from this template or create from scratch. Read the template at the root of this repo for reference.

2. **Check if `.agents.local.md` exists.** If not, run `./scripts/init-agent-context.sh` to set it up from template.

3. **Check if `.agents.local.md` is gitignored.** If not, add `.agents.local.md` to `.gitignore`.

4. **Ask which agents they use.** The init script can wire up Claude Code (CLAUDE.md symlink), Cursor (.cursorrules), Windsurf (.windsurfrules), or Copilot (copilot-instructions.md).

## Key Resources

- **Full knowledge base:** `../SKILL.md` (root level) — comprehensive guide with research foundation
- **Project template:** `../AGENTS.md` — the committed file structure and format
- **Scripts:** `../scripts/` — init, compress, promote, validate, publish
- **Deep docs:** `../agent_docs/` — conventions, architecture, gotchas (load on demand)

## Important Context

- **Instruction budget:** Frontier LLMs follow ~150-200 instructions. Claude Code's system prompt uses ~50. Keep `AGENTS.md` under 120 lines.
- **Passive context wins:** Vercel evals: 100% pass rate with embedded context vs 53% when agents decide to look things up.
- **Subagent-ready:** Subagents don't inherit conversation history. They only get the root instruction file. Tell them explicitly to read `.agents.local.md` too.
- **Compressed format:** Use pipe-delimited patterns (`pattern | where-to-see-it`), boundaries (`rule | reason`), gotchas (`trap | fix`). Dense beats verbose.

## Session Protocol

1. Read `AGENTS.md` and `.agents.local.md` (if it exists) before starting any task
2. Follow project conventions and boundaries defined in compressed format
3. **At session end, append to `.agents.local.md` Session Log.** This is the most commonly missed step. If the user appears to be ending the session without asking you to log, proactively offer to update the scratchpad.
   - Done: (what changed)
   - Worked: (reuse this)
   - Didn't work: (avoid this)
   - Decided: (choices and reasoning)
   - Learned: (new patterns or gotchas)
4. When scratchpad exceeds 300 lines, compress and flag recurring patterns (3+ sessions) for promotion

> **Known gap:** Most agent tools (Copilot Chat, Cursor, Windsurf) end sessions silently — no hook fires. Session logging depends on the agent seeing Rule 7 in AGENTS.md and acting on it, or the user prompting "log this session." Claude Code's auto memory handles this automatically.
