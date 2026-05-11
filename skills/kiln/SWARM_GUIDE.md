# Kiln — Agent Swarm System Guide

**Version:** 1.0
**Date:** February 10, 2026
**Author:** Adam Arreola + Claude

---

## What Is This?

This is the development system for Kiln. It gives Claude Code a structured operating framework with crash-prevention rules, quality gates, and the ability to split work across parallel agent teammates.

The system has ~400 lines across 12 files. It provides: Hard Laws (safety rules that prevent printer damage and data loss), automated quality gates (linting, build checks, learning loop), and slash commands for dispatching work to parallel agent teams.

---

## System Architecture

```
+---------------------------------------------------+
|  CLAUDE.md  (Universal Rules - every session)      |
|  Hard Laws, git workflow, build rules,             |
|  communication style, swarm decisions.             |
+-------------------------+-------------------------+
                          |
+-------------------------v-------------------------+
|  .claude/skills/  (Slash Commands)                |
|  /debug          - Solo focused investigation      |
|  /swarm-debug    - Parallel whitehat audit         |
|  /swarm-feature  - Build features with a team      |
|  /swarm-bugbash  - Fix multiple bugs in parallel   |
|  /swarm-release  - Coordinate a release            |
+-------------------------+-------------------------+
                          |
+-------------------------v-------------------------+
|  .dev/roles/  (Slim Role References)              |
|  LOGIC.md, INTERFACE.md, QA.md, INTEGRATION.md    |
|  ~20 lines each. Used in teammate spawn prompts.  |
+-------------------------+-------------------------+
                          |
+-------------------------v-------------------------+
|  .dev/LESSONS_LEARNED.md  (Technical Patterns)    |
|  Grows automatically. Hard-won bug fixes.          |
|  Consulted when hitting unfamiliar issues.         |
+---------------------------------------------------+
```

**Automated enforcement** (runs without you thinking about it):
- `.claude/settings.json` runs `py_compile` on every Python file edit
- `.claude/settings.json` blocks session exit with a 4-part quality gate:
  1. **Build check** — Were Python edits verified?
  2. **Learning check** — If you corrected Claude, did it file the lesson to LESSONS_LEARNED.md?
  3. **Quality check** — Are changes root-cause fixes (not band-aids)? Minimal blast radius?
  4. **Self-challenge check** — Did Claude self-critique before presenting non-trivial work?

---

## Getting Started

### Prerequisites
- [Claude Code](https://claude.ai/claude-code) installed
- Python 3.10+ with both packages installed: `pip install -e ./kiln && pip install -e ./octoprint-cli`

### Your First Session
Just open Claude Code in the Kiln repo. CLAUDE.md loads automatically. The hooks in `.claude/settings.json` are active. You don't need to do anything special.

For a normal task (fix a bug, add a feature, investigate an issue), just describe what you want. Claude follows the rules in CLAUDE.md automatically.

For structured workflows, use the slash commands below.

---

## Quick Reference: All Commands

| Command | Type | When to Use |
|---------|------|-------------|
| `/debug` | Solo | Focused investigation on one bug or one area. Sequential phases. |
| `/swarm-debug` | Team (3-5 agents) | Broad audit of a subsystem. Parallel whitehat stress testing. |
| `/swarm-feature` | Team (2-4 agents) | Building a feature that spans multiple files/layers. |
| `/swarm-bugbash` | Team (1 per bug) | Fixing 3+ independent bugs in parallel. |
| `/swarm-release` | Team (3 agents) | Preparing a tagged release. |

---

## Command Details

### /debug — Solo Investigation

**What it does:** One Claude session systematically investigates a bug, then stress-tests the surrounding area like a whitehat tester.

**Phases:**
1. Context Lock — checks git branch, status, recent commits
2. Bug Investigation — traces end-to-end through all layers (MCP tool -> server.py -> adapter -> HTTP -> printer API)
3. Whitehat Stress Test — checks data flow, edge cases, security, adapter contracts, MCP layer
4. Report — severity-rated findings, auto-fixes CRITICAL/HIGH

**Example prompts:**
```
/debug The OctoPrint adapter returns UNKNOWN state when printer is heating

/debug Audit the entire upload flow for error handling gaps

/debug (no specific bug - just audit whatever I changed recently)
```

**Best for:** Single bug, single file area, focused investigation. When you want depth over breadth.

---

### /swarm-debug — Parallel Whitehat Audit

**What it does:** Spawns up to 5 specialist teammates that simultaneously audit different dimensions of your code.

**Teammates spawned:**
| Teammate | Checks |
|----------|--------|
| data-flow | API response parsing, type coercion, dataclass completeness, state mapping |
| edge-cases | Printer offline, mid-operation conflicts, empty responses, concurrent calls, retry exhaustion |
| security | Credential exposure, path traversal, G-code safety, config permissions, input validation |
| adapter-contract | Abstract method coverage, return types, error handling, state enum exhaustiveness |
| mcp-layer | Tool registration, response format, error propagation, lazy init safety |

(adapter-contract and mcp-layer only spawn if relevant to the scope)

**Example prompts:**
```
/swarm-debug Audit the entire OctoPrint adapter end-to-end

/swarm-debug Full security audit before release

/swarm-debug Stress test the MCP server layer
```

**Best for:** Broad scope, pre-release audits, post-refactor validation. When you want breadth and thoroughness.

---

### /swarm-feature — Build a Feature

**What it does:** The lead breaks down your feature into tasks, spawns specialist teammates with strict file ownership, and coordinates integration.

**Teammates spawned:**
| Teammate | Owns | Forbidden |
|----------|------|-----------|
| logic | `kiln/src/kiln/printers/**`, `server.py` (handlers) | `octoprint-cli/**` |
| interface | `octoprint-cli/**`, `server.py` (tool defs) | `kiln/src/kiln/printers/**` |
| integration | New adapter files, adapter registry | `octoprint-cli/**` |
| qa | `*/tests/**` (read access to everything) | — |

Not all are always needed. If your feature doesn't touch external APIs, no integration teammate is spawned.

**Example prompts:**
```
/swarm-feature Add a Klipper/Moonraker adapter with full PrinterAdapter implementation

/swarm-feature Add job queue support - queue multiple print jobs and execute sequentially

/swarm-feature Add fleet management - discover and manage multiple printers
```

**Best for:** Multi-file features where logic, interface, and possibly integration work can happen in parallel without editing the same files.

---

### /swarm-bugbash — Parallel Bug Fixing

**What it does:** Takes a list of bugs, assigns one teammate per bug (or bug group if they share files), and fixes them all in parallel.

**How file conflicts are avoided:** If two bugs affect the same file, they go to the SAME teammate and are fixed sequentially. Different files = different teammates = parallel.

**Example prompts:**
```
/swarm-bugbash Fix these 4 bugs:
1. State mapping returns UNKNOWN for heating state in OctoPrint adapter
2. upload_file doesn't validate file extension
3. CLI --json mode missing from preflight command
4. Config file created with world-readable permissions

/swarm-bugbash Find and fix all # TODO stubs in critical paths

/swarm-bugbash Fix all type annotation issues across the codebase
```

**Best for:** Clearing a batch of known issues fast. Bug triage days. Pre-release cleanup.

---

### /swarm-release — Release Pipeline

**What it does:** Coordinates version bumping, content updates, and validation in parallel, with validation gating the final tag.

**Teammates spawned:**
| Teammate | Tasks |
|----------|-------|
| version | Bump version in pyproject.toml + __init__.py for both packages |
| content | Update changelog (append only), README, docs |
| validation | py_compile all files, run pytest, scan for TODOs, verify adapter completeness |

**Critical rule:** Validation MUST pass before the lead creates the git tag. This is a hard dependency.

**The lead does NOT push to remote.** You decide when to push.

**Example prompts:**
```
/swarm-release Prepare v0.2.0 for PyPI

/swarm-release Bump to v1.0.0 and validate everything

/swarm-release Quick release - just bump patch version and validate
```

**Best for:** Any tagged release. Ensures nothing ships broken.

---

## Decision Guide: When to Swarm vs Solo

| Situation | Use |
|-----------|-----|
| One bug in one file | Just fix it (no command needed) |
| One bug, want thorough investigation | `/debug` |
| Audit a whole subsystem | `/swarm-debug` |
| Small feature, 1-2 files | Just build it (no command needed) |
| Feature spanning 3+ files | `/swarm-feature` |
| One bug to fix | Just fix it |
| 3+ independent bugs | `/swarm-bugbash` |
| Preparing a release | `/swarm-release` |

**Rule of thumb:** If teammates would need to edit the same file, don't swarm. Use solo with sequential edits.

---

## Built-In Behaviors (You Get These for Free)

These are baked into CLAUDE.md and enforced automatically. You don't invoke them — they're always active.

### Self-Improvement Loop (Learning Reflex)

When Claude makes a mistake and you correct it, Claude is required to:
1. Immediately append the pattern to `.dev/LESSONS_LEARNED.md`
2. Write it as a reusable rule (what went wrong, why, the correct pattern)
3. This is enforced by the Stop hook — Claude can't finish a session without filing the lesson

**What this means for you:** Every correction you make becomes permanent institutional knowledge. Claude won't make the same mistake twice across sessions. The more you correct, the smarter the system gets.

**Triggers:** You say "no, that's wrong" / "actually you should..." / a fix takes multiple attempts / a test fails for a non-obvious reason.

### Self-Challenge Gate

Before presenting any non-trivial work, Claude runs a mandatory self-check. If any check fails, it **iterates silently** until it passes — you never see the rough draft.

The checks:
1. Code valid? (imports, syntax, types)
2. Root cause addressed (not a band-aid)?
3. Minimal blast radius (only necessary files touched)?
4. Edge cases handled (None, empty, offline printer, timeout)?
5. Simpler solution exists?
6. **Staff engineer test:** Would a senior infrastructure engineer approve this on first review?

### Code Discipline

Claude follows these principles on every code change:
- **Root causes only** — No band-aid fixes.
- **Minimal blast radius** — Only touches what's necessary.
- **Simplicity first** — Prefers the simplest correct solution.

### Subagent Strategy

Claude uses lightweight subagents (not full swarm teammates) to keep its main context window clean:
- **Research tasks** — Grepping across the codebase, reading multiple files
- **Parallel hypotheses** — Multiple possible causes investigated simultaneously
- **One task per subagent** — Focused and specific

You don't need to tell Claude to use subagents. It does this automatically.

---

## Hard Laws (Always Enforced)

These are in CLAUDE.md and apply to every session and every teammate. They exist because violating them can cause real hardware damage or data loss.

1. **Printer Safety First** — Pre-flight checks mandatory. Confirm before destructive ops. Validate G-code.
2. **Adapter Interface Contract** — All adapters implement ALL abstract methods. Return correct types. Handle failures gracefully.
3. **Error Boundary Discipline** — Network calls always wrapped. Structured error responses. No silent failures.
4. **Configuration Safety** — No hardcoded credentials. Validate config on load. Check file permissions.
5. **No-TODO Critical Paths** — Print submission, upload, temperature, G-code, auth — fully implemented or error-stubbed.
6. **Type Safety at Boundaries** — Normalize external data. Validate before forwarding. Enum exhaustiveness.

---

## File Reference

| File | Purpose | When to Consult |
|------|---------|-----------------|
| `CLAUDE.md` | Universal workflow rules | Auto-loaded every session |
| `.dev/LESSONS_LEARNED.md` | Technical patterns & bug fixes | When hitting unfamiliar issues |
| `.dev/SWARM_GUIDE.md` | This file — system guide | When learning the system |
| `.dev/roles/LOGIC.md` | Logic teammate constraints | When customizing a logic teammate |
| `.dev/roles/INTERFACE.md` | Interface teammate constraints | When customizing an interface teammate |
| `.dev/roles/QA.md` | QA teammate constraints | When customizing a QA teammate |
| `.dev/roles/INTEGRATION.md` | Integration teammate constraints | When customizing an integration teammate |

---

## Tips

- **Correct Claude aggressively.** Every correction gets filed to LESSONS_LEARNED.md by the self-improvement loop. The more you correct, the smarter it gets across sessions.
- **Check LESSONS_LEARNED.md periodically.** It grows automatically. You can edit/clean it up anytime.
- **The Stop hook is your safety net.** It blocks Claude from finishing if it forgot to verify code, file a lesson, or if the fix looks like a band-aid. You'll see the block reason and can override if needed.
- **Swarms use more tokens** than solo sessions. For quick fixes, just ask Claude directly without invoking a skill.
- **Agent teams are experimental.** If a teammate stops unexpectedly, tell the lead to spawn a replacement.
- **You can always override.** These skills are guidelines for Claude, not constraints on you. Tell Claude to do something differently and it will.
