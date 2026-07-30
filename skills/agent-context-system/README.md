# Agent Context System

Coding agents are good at using context. They are terrible at keeping it consistent.

Tools like GitHub Copilot Memory are doing great work on the individual side. Copilot remembers your preferences, your patterns, your stack. That's a real step forward for developer experience.

But there's a layer that built-in memory doesn't cover: shared, reviewable, version-controlled project context. The stuff that lives in your repo and works across every agent your team uses. Teams still hit the same walls:

- The "rules of the repo" live in chat threads and tribal knowledge
- A new agent or subagent starts without the constraints that matter
- The agent learns something once, then you can't review it like code
- Context drifts because nobody promotes stable decisions into a shared source of truth

This project is a small, boring fix. It doesn't replace built-in memory. It complements it. Built-in memory handles what the tool learns about *you*. This handles what every agent needs to know about *your project*. It makes that context explicit, reviewable, and portable.

## What this is

Two markdown files. One committed, one gitignored. The agent reads both at the start of every session and updates the local one at the end.

- `AGENTS.md` is your project's source of truth. Committed and shared. Always in the agent's prompt.
- `.agents.local.md` is your personal scratchpad. Gitignored. It grows over time as the agent logs what it learns each session.

That's it. No plugins, no infrastructure, no background processes. The convention lives inside the files themselves, and the agent follows it.

```
your-repo/
├── AGENTS.md                    # Committed. Always loaded. Under 120 lines.
├── .agents.local.md             # Gitignored. Personal scratchpad.
├── agent-context                # CLI: init, validate, promote commands.
├── agent_docs/                  # Deeper docs. Read only when needed.
│   ├── conventions.md
│   ├── architecture.md
│   └── gotchas.md
├── scripts/
│   └── init-agent-context.sh    # Wrapper → calls agent-context init (for npx skills)
└── CLAUDE.md                    # Symlink → AGENTS.md (created by init)
```

**Note:** `agent-context` is the main CLI. `scripts/init-agent-context.sh` is a thin wrapper for backwards compatibility with `npx skills add` installs — it just calls `agent-context init`.

## Install

### GitHub Template (new project)

```bash
gh repo create my-project --template AndreaGriffiths11/agent-context-system
cd my-project
./agent-context init
```

### Existing project

```bash
# Clone the files into your project
git clone https://github.com/AndreaGriffiths11/agent-context-system.git /tmp/acs
cp /tmp/acs/AGENTS.md /tmp/acs/agent-context .
cp -r /tmp/acs/agent_docs /tmp/acs/scripts .
rm -rf /tmp/acs
./agent-context init
```

### OpenClaw users

Clone into your skills directory:

```bash
git clone https://github.com/AndreaGriffiths11/agent-context-system.git skills/agent-context-system
```

OpenClaw will pick it up as a workspace skill on the next session.

### Copilot Custom Skill

```bash
npx skills add AndreaGriffiths11/agent-context-system
bash .agents/skills/agent-context-system/scripts/init-agent-context.sh
```

Or copy `github-copilot/SKILL.md` to `.github/skills/agent-context-system/SKILL.md`.

## CLI Commands

```bash
agent-context init      # Set up context system in current project
agent-context validate  # Check setup is correct
agent-context promote   # Find patterns to move from scratchpad to AGENTS.md
agent-context promote --autopromote  # Auto-append patterns recurring 3+ times
```

## How knowledge moves

<img width="955" height="502" alt="knowledge flow" src="https://github.com/user-attachments/assets/a5c29763-9eb4-48ef-878d-935797b6febe" />

1. **Write**: Agent logs learnings to `.agents.local.md` at session end
2. **Compress**: Scratchpad compresses when it hits 300 lines
3. **Flag**: Patterns recurring 3+ times get flagged "Ready to Promote"
4. **Promote**: Run `agent-context promote` to review, or `--autopromote` to auto-append to `AGENTS.md`

---

<details>
<summary><strong>The Research (Why this works)</strong></summary>

### Agents have an instruction budget (~150-200 instructions)

HumanLayer found frontier LLMs reliably follow about 150-200 instructions. Claude Code's system prompt eats ~50. That's why `AGENTS.md` stays under 120 lines.

### Available docs ≠ used docs

Vercel ran evals:
- No docs: 53% pass rate
- Skills where agent decides when to read: **53%** (identical to nothing)
- Compressed docs embedded in root file: **100%**

When docs are embedded directly, the agent cannot miss them.

### Context has a lifecycle

LangChain's framework: Write, Select, Compress, Isolate.

- **Write**: Scratchpad at session end
- **Select**: Read both files at start
- **Compress**: At 300 lines, dedupe and merge
- **Isolate**: Project vs personal (committed vs gitignored)

### Deep docs load on demand

AGENTS.md every time. `agent_docs/` only when the task needs depth.

### One file, every tool

AGENTS.md: Cursor, Copilot, Codex, Windsurf all read it. Claude Code still needs CLAUDE.md (symlink handled by init).

</details>

<details>
<summary><strong>Agent Compatibility</strong></summary>

| Agent | Setup |
|-------|-------|
| OpenClaw | Clone into `skills/` directory — reads AGENTS.md natively |
| Claude Code | `CLAUDE.md` symlink → `AGENTS.md` |
| Cursor | `.cursorrules` pointing to AGENTS.md |
| Windsurf | `.windsurfrules` pointing to AGENTS.md |
| GitHub Copilot | `.github/copilot-instructions.md` pointing to AGENTS.md |

**Claude Code note:** Auto memory (late 2025) handles session-to-session learning in `~/.claude/projects/<project>/memory/`. If you use Claude exclusively, auto memory covers the scratchpad's job. The value here is AGENTS.md itself: structured promotion pathway, instruction budget discipline, and cross-agent compatibility.

</details>

<details>
<summary><strong>Subagents: When one becomes five</strong></summary>

Claude Code has subagents. Copilot CLI has `/fleet` (experimental). Both dispatch parallel agents that don't inherit conversation history.

<img width="855" height="635" alt="subagent context isolation" src="https://github.com/user-attachments/assets/c561960b-6f87-4753-9381-8762c35cbcb6" />

Each subagent starts fresh. The only shared brain is your root instruction file. AGENTS.md goes from "helpful context" to "the only thing preventing five agents from making conflicting decisions."

This is why the template explicitly tells subagents to read `.agents.local.md` too. They won't get it otherwise.

</details>

<details>
<summary><strong>Session Logging Reality</strong></summary>

Agents don't have session-end hooks. Sessions end when you stop talking. Logging only happens if:

1. Agent proactively logs before conversation ends (rare), or
2. **You prompt it:** "log this session" or "update the scratchpad"

Claude Code handles this well with auto memory. For others, get in the habit of prompting for the log when meaningful work was done.

</details>

---

## After setup

1. **Edit `AGENTS.md`** — Fill in your project name, stack, commands. Replace placeholders with real patterns from your codebase.
2. **Fill in `agent_docs/`** — Add deeper references. Delete what doesn't apply.
3. **Customize `.agents.local.md`** — Add your preferences.
4. **Work** — Agent reads both files, does the task, updates scratchpad.
5. **Promote** — Run `agent-context promote` to see flagged patterns. Move stable ones to AGENTS.md.

## Sources

| Finding | Source |
|---------|--------|
| Instruction budgets | [HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md) |
| Passive context 100% pass rate | [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) |
| 2,500+ repos analyzed | [GitHub](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) |
| Context lifecycle framework | [LangChain](https://blog.langchain.com/context-engineering-for-agents/) |
| Three-tier progressive disclosure | [Anthropic](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |

## License

MIT
