# Canonical docs and how agents should learn zmail

This file is for the **end-user `/zmail` skill** (`skills/zmail/`). For **developing** zmail in Cursor, use the repo’s **`.cursor/skills/`** (`commit`, `db-dev`, `install-local`, `process-feedback`) — not this playbook.

---

## Prefer the live CLI over static cheat sheets

**Treat the installed `zmail` binary as the source of truth** for commands, flags, and defaults. Markdown in the repo or this skill can lag a release; the CLI cannot.

**Discovery order (recommended):**

1. **`zmail`**, **`zmail --help`**, **`zmail -h`**, or **`zmail help`** — full overview, including when to use **`zmail ask`** vs **`search` / `read` / `thread` / `who` / `attachment` / `inbox`**, and where to read more (`docs/ASK.md`, `docs/MCP.md`).
2. **`zmail <command> --help`** — flags and examples for that command (e.g. `zmail search --help`, `zmail who --help`, `zmail attachment list --help`).
3. **Run a command** and read the **structured output** — zmail **embeds hints** so you learn the next step without opening docs (see below).

The long-form help string is maintained in code as **`CLI_USAGE`** in **`src/lib/onboarding.ts`** (same text the CLI prints). When in doubt, compare this skill or `AGENTS.md` to that file.

---

## Progressive disclosure in CLI output (read the `hint`)

zmail is designed so **the tool teaches its own capabilities** as you use it.

- **JSON (default for `search`, `who`, `attachment list`):** Responses are often an object with **`results`** plus optional metadata. Look especially for:
  - **`hint`** — short guidance (narrower query, attachments, pagination, batch-style follow-ups, etc.).
  - **`truncated`**, **`totalMatched`**, **`returned`** — whether you are seeing a slice of a larger result set; combine with **`--limit`** / flags from **`zmail search --help`**.
- **Text / table mode (`--text`):** Some commands print a **trailing tip** after results (same ideas as JSON hints).
- **Typos / wrong verbs:** Unknown subcommands get a **compact correction** (e.g. suggesting `refresh`, `read`, `search`, `ask`).
- **Missing config:** You get an explicit pointer to **`zmail setup`** / **`zmail wizard`** — no silent failure.

**Agent habit:** After every `zmail` call, if the payload includes **`hint`**, follow it before guessing a new command.

---

## Markdown references (repo or npm package root)

Paths below are relative to the **repository root** or the **installed `@cirne/zmail` package root** (the parent of `skills/zmail/`). If you only have the global CLI, open the same paths under your global install, e.g.:

`$(npm root -g)/@cirne/zmail/AGENTS.md` (exact layout depends on npm version and OS).

| Topic | Path | Notes |
|--------|------|--------|
| **Full agent guide** — commands, env, sync, MCP overview | `AGENTS.md` | Primary maintainer-facing index; keep skill content thin and link here. |
| **Vision** — agent-first product goals | `docs/VISION.md` | Why zmail exists; not a command reference. |
| **`ask` vs primitives** — orchestration, hybrid patterns | `docs/ASK.md` | When `zmail ask` wins vs `search`/`read`/…; complements `--help`. |
| **Architecture** — SQLite, sync, indexing decisions | `docs/ARCHITECTURE.md` | Read before changing storage or sync behavior. |
| **MCP** — tools, params, token-efficient patterns | `docs/MCP.md` | Same index as CLI; hints in JSON sometimes align with MCP batch patterns. |
| **Skill packaging** — spec, hosts, `skills/zmail/` layout | `docs/opportunities/OPP-025-cross-platform-agent-skills-packaging.md` | Strategy for `/zmail` vs internal Cursor skills. |

**DRY:** Prefer updating **`AGENTS.md`**, **`docs/*.md`**, or **`src/lib/onboarding.ts`** (`CLI_USAGE` and onboarding strings) rather than duplicating long command lists in **`SKILL.md`** or this file.

---

## MCP

For a **persistent tool** connection (instead of subprocess CLI), run **`zmail mcp`** and use the tools described in **`docs/MCP.md`**. CLI and MCP share the same index; **help text and `CLI_USAGE`** still describe the underlying concepts (e.g. ask vs search).
