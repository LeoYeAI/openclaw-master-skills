---
name: self-improving-agent
description: "Instinct-based continuous learning system. Captures atomic learnings (instincts) with confidence scoring, supports project-scoped vs global scope, and evolves instincts into skills/commands/agents. Use when: (1) A command fails, (2) User corrects you, (3) Discovering patterns, (4) Need to review or evolve learned behaviors. Supports both v1 (markdown-based) and v2 (instinct-based) modes."
metadata:
  version: "2.1"
  origin: "ECC + OpenClaw"
---

# Self-Improving Agent Skill

An advanced learning system that turns Claude Code sessions into reusable knowledge through atomic "instincts" - small learned behaviors with confidence scoring and project scope isolation.

**v2.1** adds **project-scoped instincts** — React patterns stay in your React project, Python conventions stay in your Python project, and universal patterns are shared globally.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log instinct or v1 learning |
| User corrects you | Create instinct with `correction` trigger |
| Discovering patterns | Log instinct with confidence score |
| Review learned behaviors | `/instinct-status` |
| Evolve instincts to skills | `/evolve` |
| Promote project → global | `/promote` |
| Setup observation hooks | Enable PreToolUse/PostToolUse hooks |

## Two Learning Modes

### Mode 1: Instinct-Based (v2) - RECOMMENDED

Atomic, confidence-weighted behaviors with project isolation:

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
scope: project
project_id: "a1b2c3d4e5f6"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach on 2025-01-15
```

### Mode 2: Markdown-Based (v1) - LEGACY

Traditional learning entries for complex, narrative learnings:

```markdown
## [LRN-YYYYMMDD-XXX] category
**Priority**: high | **Status**: pending | **Area**: backend

### Summary
Detailed description of what was learned

### Details
Full context and explanation
```

Use v2 (instincts) for behavioral patterns, v1 (markdown) for complex incident analysis.

---

## Instinct-Based Learning (v2)

### The Instinct Model

An instinct is a small, atomic learned behavior:

**Properties:**
- **Atomic** — one trigger, one action
- **Confidence-weighted** — 0.3 = tentative, 0.9 = near certain
- **Domain-tagged** — code-style, testing, git, debugging, workflow, security, etc.
- **Evidence-backed** — tracks what observations created it
- **Scope-aware** — `project` (default) or `global`

### Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

**Confidence increases when:**
- Pattern is repeatedly observed
- User doesn't correct the suggested behavior
- Similar instincts from other sources agree

**Confidence decreases when:**
- User explicitly corrects the behavior
- Pattern isn't observed for extended periods
- Contradicting evidence appears

### Scope Decision Guide

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| Language/framework conventions | **project** | "Use React hooks", "Follow Django REST patterns" |
| File structure preferences | **project** | "Tests in `__tests__`/", "Components in src/components/" |
| Code style | **project** | "Use functional style", "Prefer dataclasses" |
| Security practices | **global** | "Validate user input", "Sanitize SQL" |
| General best practices | **global** | "Write tests first", "Always handle errors" |
| Tool workflow preferences | **global** | "Grep before Edit", "Read before Write" |
| Git practices | **global** | "Conventional commits", "Small focused commits" |

### Project Detection

The system automatically detects your current project:

1. **`CLAUDE_PROJECT_DIR` env var** (highest priority)
2. **`git remote get-url origin`** — hashed to create a portable project ID
3. **`git rev-parse --show-toplevel`** — fallback using repo path
4. **Global fallback** — if no project detected, instincts go to global scope

Each project gets a 12-character hash ID (e.g., `a1b2c3d4e5f6`).

## v2 Commands

| Command | Description |
|---------|-------------|
| `/instinct-status` | Show all instincts (project-scoped + global) with confidence |
| `/evolve` | Cluster related instincts into skills/commands, suggest promotions |
| `/instinct-export` | Export instincts (filterable by scope/domain) |
| `/instinct-import <file>` | Import instincts with scope control |
| `/promote [id]` | Promote project instincts to global scope |
| `/projects` | List all known projects and their instinct counts |

### /instinct-status Example

```
Project: my-react-app (a1b2c3d4e5f6)
├─ prefer-functional-style.yaml (0.7) [project]
├─ use-react-hooks.yaml (0.9) [project]
└─ jest-testing-patterns.yaml (0.6) [project]

Global Instincts:
├─ always-validate-input.yaml (0.85) [global]
├─ grep-before-edit.yaml (0.6) [global]
└─ conventional-commits.yaml (0.75) [global]
```

### /evolve Workflow

Clusters related instincts and generates:
- **Skills** — domain-specific workflows
- **Commands** — slash commands for common tasks
- **Agents** — specialized sub-agents

```bash
/evolve
# Analyzes instincts and suggests:
# - "Create skill: react-testing-workflow.md"
# - "Create command: /test-component"
# - "Promote prefer-functional-style to global (seen in 3 projects)"
```

### /promote Workflow

Promote project-scoped instincts to global when proven across projects:

```bash
/promote prefer-explicit-errors
# Promotes the instinct from current project to global scope
```

**Auto-promotion criteria:**
- Same instinct ID in 2+ projects
- Average confidence >= 0.8

## File Structure (v2)

```
~/.claude/homunculus/
├── identity.json           # Your profile, technical level
├── projects.json           # Registry: project hash → name/path/remote
├── observations.jsonl      # Global observations (fallback)
├── instincts/
│   ├── personal/           # Global auto-learned instincts
│   └── inherited/          # Global imported instincts
├── evolved/
│   ├── agents/             # Global generated agents
│   ├── skills/             # Global generated skills
│   └── commands/           # Global generated commands
└── projects/
    ├── a1b2c3d4e5f6/       # Project hash
    │   ├── observations.jsonl
    │   ├── observations.archive/
    │   ├── instincts/
    │   │   ├── personal/   # Project-specific auto-learned
    │   │   └── inherited/  # Project-specific imported
    │   └── evolved/
    │       ├── skills/
    │       ├── commands/
    │       └── agents/
    └── f6e5d4c3b2a1/       # Another project
```

## Enabling Observation Hooks (v2)

Add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/self-improving-agent/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/self-improving-agent/hooks/observe.sh"
      }]
    }]
  }
}
```

**Why hooks?** Hooks fire **100% of the time**, deterministically. Skills fire ~50-80% based on Claude's judgment.

---

OpenClaw is the primary platform for this skill. It uses workspace-based prompt injection with automatic skill loading.

### Installation

**Via ClawdHub (recommended):**
```bash
clawdhub install self-improving-agent
```

**Manual:**
```bash
git clone https://github.com/peterskoett/self-improving-agent.git ~/.openclaw/skills/self-improving-agent
```

Remade for openclaw from original repo : https://github.com/pskoett/pskoett-ai-skills - https://github.com/pskoett/pskoett-ai-skills/tree/main/skills/self-improvement

### Workspace Structure

OpenClaw injects these files into every session:

```
~/.openclaw/workspace/
├── AGENTS.md          # Multi-agent workflows, delegation patterns
├── SOUL.md            # Behavioral guidelines, personality, principles
├── TOOLS.md           # Tool capabilities, integration gotchas
├── MEMORY.md          # Long-term memory (main session only)
├── memory/            # Daily memory files
│   └── YYYY-MM-DD.md
└── .learnings/        # This skill's log files
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

### Create Learning Files

```bash
mkdir -p ~/.openclaw/workspace/.learnings
```

Then create the log files (or copy from `assets/`):
- `LEARNINGS.md` — corrections, knowledge gaps, best practices
- `ERRORS.md` — command failures, exceptions
- `FEATURE_REQUESTS.md` — user-requested capabilities

### Promotion Targets

When learnings prove broadly applicable, promote them to workspace files:

| Learning Type | Promote To | Example |
|---------------|------------|---------|
| Behavioral patterns | `SOUL.md` | "Be concise, avoid disclaimers" |
| Workflow improvements | `AGENTS.md` | "Spawn sub-agents for long tasks" |
| Tool gotchas | `TOOLS.md` | "Git push needs auth configured first" |

### Inter-Session Communication

OpenClaw provides tools to share learnings across sessions:

- **sessions_list** — View active/recent sessions
- **sessions_history** — Read another session's transcript  
- **sessions_send** — Send a learning to another session
- **sessions_spawn** — Spawn a sub-agent for background work

### Optional: Enable Hook

For automatic reminders at session start:

```bash
# Copy hook to OpenClaw hooks directory
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement

# Enable it
openclaw hooks enable self-improvement
```

See `references/openclaw-integration.md` for complete details.

---

## Generic Setup (Other Agents)

For Claude Code, Codex, Copilot, or other agents, create `.learnings/` in your project:

```bash
mkdir -p .learnings
```

Copy templates from `assets/` or create files with headers.

### Add reference to agent files AGENTS.md, CLAUDE.md, or .github/copilot-instructions.md to remind yourself to log learnings. (this is an alternative to hook-based reminders)

#### Self-Improvement Workflow

When errors or corrections occur:
1. Log to `.learnings/ERRORS.md`, `LEARNINGS.md`, or `FEATURE_REQUESTS.md`
2. Review and promote broadly applicable learnings to:
   - `CLAUDE.md` - project facts and conventions
   - `AGENTS.md` - workflows and automation
   - `.github/copilot-instructions.md` - Copilot context

## Logging Formats

### v2: Instinct Format (RECOMMENDED for behavioral patterns)

Create atomic instinct files in `~/.claude/homunculus/instincts/personal/` or project-scoped:

```yaml
---
id: unique-instinct-id
trigger: "when to apply this instinct"
confidence: 0.7
domain: "code-style|testing|git|debugging|workflow|security|infra"
source: "session-observation|user-correction|pattern-detection"
scope: "project|global"
project_id: "a1b2c3d4e5f6"  # if scope: project
project_name: "my-project"
created_at: "2025-01-15T10:00:00Z"
updated_at: "2025-01-15T10:00:00Z"
evidence_count: 3
---

# Instinct Title

## Action
What to do when triggered.

## Rationale
Why this behavior is preferred.

## Examples

### Positive
```typescript
// Good example
```

### Negative
```typescript
// Bad example
```

## Evidence
- Observed 3 instances of this pattern
- User corrected opposite approach on 2025-01-10
```

**File naming:** `~/.claude/homunculus/instincts/personal/{instinct-id}.yaml`

### v1: Markdown Format (for complex learnings)

#### Learning Entry

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback | simplify-and-harden
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001
- Pattern-Key: simplify.dead_code | harden.input_validation

---
```

## v2 vs v1 Comparison

| Feature | v1 (Markdown) | v2 (Instincts) |
|---------|---------------|----------------|
| Granularity | Full skills | Atomic "instincts" |
| Confidence | None | 0.3-0.9 weighted |
| Scope | Global only | Project-scoped + global |
| Observation | Stop hook (session end) | PreToolUse/PostToolUse (100% reliable) |
| Analysis | Main context | Background agent (Haiku) |
| Evolution | Direct to skill | Instincts → cluster → skill/command/agent |
| Sharing | None | Export/import instincts |
| Best for | Complex incidents | Behavioral patterns |

## Migration from v1 to v2

**For existing v1 users:** v2 is fully backward compatible:
- Existing global instincts still work
- Existing `.learnings/*.md` files still work
- Gradual migration: run both in parallel

**Recommended approach:**
1. Start using v2 instincts for new behavioral patterns
2. Keep v1 markdown for complex incident analysis
3. Use `/evolve` to convert related v1 learnings into v2 instincts
4. Promote high-confidence instincts to skills

---

### Error Entry

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
```
Actual error message or output
```

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)

---
```

### Feature Request Entry

Append to `.learnings/FEATURE_REQUESTS.md`:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built, what it might extend

### Metadata
- Frequency: first_time | recurring
- Related Features: existing_feature_name

---
```

## ID Generation

Format: `TYPE-YYYYMMDD-XXX`
- TYPE: `LRN` (learning), `ERR` (error), `FEAT` (feature)
- YYYYMMDD: Current date
- XXX: Sequential number or random 3 chars (e.g., `001`, `A7B`)

Examples: `LRN-20250115-001`, `ERR-20250115-A3F`, `FEAT-20250115-002`

## Resolving Entries

When an issue is fixed, update the entry:

1. Change `**Status**: pending` → `**Status**: resolved`
2. Add resolution block after Metadata:

```markdown
### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: abc123 or #42
- **Notes**: Brief description of what was done
```

Other status values:
- `in_progress` - Actively being worked on
- `wont_fix` - Decided not to address (add reason in Resolution notes)
- `promoted` - Elevated to CLAUDE.md, AGENTS.md, or .github/copilot-instructions.md

## Promoting to Project Memory

When a learning is broadly applicable (not a one-off fix), promote it to permanent project memory.

### When to Promote

- Learning applies across multiple files/features
- Knowledge any contributor (human or AI) should know
- Prevents recurring mistakes
- Documents project-specific conventions

### Promotion Targets

| Target | What Belongs There |
|--------|-------------------|
| `CLAUDE.md` | Project facts, conventions, gotchas for all Claude interactions |
| `AGENTS.md` | Agent-specific workflows, tool usage patterns, automation rules |
| `.github/copilot-instructions.md` | Project context and conventions for GitHub Copilot |
| `SOUL.md` | Behavioral guidelines, communication style, principles (OpenClaw workspace) |
| `TOOLS.md` | Tool capabilities, usage patterns, integration gotchas (OpenClaw workspace) |

### How to Promote

1. **Distill** the learning into a concise rule or fact
2. **Add** to appropriate section in target file (create file if needed)
3. **Update** original entry:
   - Change `**Status**: pending` → `**Status**: promoted`
   - Add `**Promoted**: CLAUDE.md`, `AGENTS.md`, or `.github/copilot-instructions.md`

### Promotion Examples

**Learning** (verbose):
> Project uses pnpm workspaces. Attempted `npm install` but failed. 
> Lock file is `pnpm-lock.yaml`. Must use `pnpm install`.

**In CLAUDE.md** (concise):
```markdown
## Build & Dependencies
- Package manager: pnpm (not npm) - use `pnpm install`
```

**Learning** (verbose):
> When modifying API endpoints, must regenerate TypeScript client.
> Forgetting this causes type mismatches at runtime.

**In AGENTS.md** (actionable):
```markdown
## After API Changes
1. Regenerate client: `pnpm run generate:api`
2. Check for type errors: `pnpm tsc --noEmit`
```

## Recurring Pattern Detection

If logging something similar to an existing entry:

1. **Search first**: `grep -r "keyword" .learnings/`
2. **Link entries**: Add `**See Also**: ERR-20250110-001` in Metadata
3. **Bump priority** if issue keeps recurring
4. **Consider systemic fix**: Recurring issues often indicate:
   - Missing documentation (→ promote to CLAUDE.md or .github/copilot-instructions.md)
   - Missing automation (→ add to AGENTS.md)
   - Architectural problem (→ create tech debt ticket)

## Simplify & Harden Feed

Use this workflow to ingest recurring patterns from the `simplify-and-harden`
skill and turn them into durable prompt guidance.

### Ingestion Workflow

1. Read `simplify_and_harden.learning_loop.candidates` from the task summary.
2. For each candidate, use `pattern_key` as the stable dedupe key.
3. Search `.learnings/LEARNINGS.md` for an existing entry with that key:
   - `grep -n "Pattern-Key: <pattern_key>" .learnings/LEARNINGS.md`
4. If found:
   - Increment `Recurrence-Count`
   - Update `Last-Seen`
   - Add `See Also` links to related entries/tasks
5. If not found:
   - Create a new `LRN-...` entry
   - Set `Source: simplify-and-harden`
   - Set `Pattern-Key`, `Recurrence-Count: 1`, and `First-Seen`/`Last-Seen`

### Promotion Rule (System Prompt Feedback)

Promote recurring patterns into agent context/system prompt files when all are true:

- `Recurrence-Count >= 3`
- Seen across at least 2 distinct tasks
- Occurred within a 30-day window

Promotion targets:
- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `SOUL.md` / `TOOLS.md` for OpenClaw workspace-level guidance when applicable

Write promoted rules as short prevention rules (what to do before/while coding),
not long incident write-ups.

## Periodic Review

Review `.learnings/` at natural breakpoints:

### When to Review
- Before starting a new major task
- After completing a feature
- When working in an area with past learnings
- Weekly during active development

### Quick Status Check
```bash
# Count pending items
grep -h "Status\*\*: pending" .learnings/*.md | wc -l

# List pending high-priority items
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["

# Find learnings for a specific area
grep -l "Area\*\*: backend" .learnings/*.md
```

### Review Actions
- Resolve fixed items
- Promote applicable learnings
- Link related entries
- Escalate recurring issues

## Detection Triggers

Automatically log when you notice:

**Corrections** (→ learning with `correction` category):
- "No, that's not right..."
- "Actually, it should be..."
- "You're wrong about..."
- "That's outdated..."

**Feature Requests** (→ feature request):
- "Can you also..."
- "I wish you could..."
- "Is there a way to..."
- "Why can't you..."

**Knowledge Gaps** (→ learning with `knowledge_gap` category):
- User provides information you didn't know
- Documentation you referenced is outdated
- API behavior differs from your understanding

**Errors** (→ error entry):
- Command returns non-zero exit code
- Exception or stack trace
- Unexpected output or behavior
- Timeout or connection failure

## Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| `critical` | Blocks core functionality, data loss risk, security issue |
| `high` | Significant impact, affects common workflows, recurring issue |
| `medium` | Moderate impact, workaround exists |
| `low` | Minor inconvenience, edge case, nice-to-have |

## Area Tags

Use to filter learnings by codebase region:

| Area | Scope |
|------|-------|
| `frontend` | UI, components, client-side code |
| `backend` | API, services, server-side code |
| `infra` | CI/CD, deployment, Docker, cloud |
| `tests` | Test files, testing utilities, coverage |
| `docs` | Documentation, comments, READMEs |
| `config` | Configuration files, environment, settings |

## Best Practices

1. **Log immediately** - context is freshest right after the issue
2. **Be specific** - future agents need to understand quickly
3. **Include reproduction steps** - especially for errors
4. **Link related files** - makes fixes easier
5. **Suggest concrete fixes** - not just "investigate"
6. **Use consistent categories** - enables filtering
7. **Promote aggressively** - if in doubt, add to CLAUDE.md or .github/copilot-instructions.md
8. **Review regularly** - stale learnings lose value

## Gitignore Options

**Keep learnings local** (per-developer):
```gitignore
.learnings/
```

**Track learnings in repo** (team-wide):
Don't add to .gitignore - learnings become shared knowledge.

**Hybrid** (track templates, ignore entries):
```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

## Hook Integration

Enable automatic reminders through agent hooks. This is **opt-in** - you must explicitly configure hooks.

### Quick Setup (Claude Code / Codex)

Create `.claude/settings.json` in your project:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }]
  }
}
```

This injects a learning evaluation reminder after each prompt (~50-100 tokens overhead).

### Full Setup (With Error Detection)

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/error-detector.sh"
      }]
    }]
  }
}
```

### Available Hook Scripts

| Script | Hook Type | Purpose |
|--------|-----------|---------|
| `scripts/activator.sh` | UserPromptSubmit | Reminds to evaluate learnings after tasks |
| `scripts/error-detector.sh` | PostToolUse (Bash) | Triggers on command errors |

See `references/hooks-setup.md` for detailed configuration and troubleshooting.

## Automatic Skill Extraction

When a learning is valuable enough to become a reusable skill, extract it using the provided helper.

### Skill Extraction Criteria

A learning qualifies for skill extraction when ANY of these apply:

| Criterion | Description |
|-----------|-------------|
| **Recurring** | Has `See Also` links to 2+ similar issues |
| **Verified** | Status is `resolved` with working fix |
| **Non-obvious** | Required actual debugging/investigation to discover |
| **Broadly applicable** | Not project-specific; useful across codebases |
| **User-flagged** | User says "save this as a skill" or similar |

### Extraction Workflow

1. **Identify candidate**: Learning meets extraction criteria
2. **Run helper** (or create manually):
   ```bash
   ./skills/self-improvement/scripts/extract-skill.sh skill-name --dry-run
   ./skills/self-improvement/scripts/extract-skill.sh skill-name
   ```
3. **Customize SKILL.md**: Fill in template with learning content
4. **Update learning**: Set status to `promoted_to_skill`, add `Skill-Path`
5. **Verify**: Read skill in fresh session to ensure it's self-contained

### Manual Extraction

If you prefer manual creation:

1. Create `skills/<skill-name>/SKILL.md`
2. Use template from `assets/SKILL-TEMPLATE.md`
3. Follow [Agent Skills spec](https://agentskills.io/specification):
   - YAML frontmatter with `name` and `description`
   - Name must match folder name
   - No README.md inside skill folder

### Extraction Detection Triggers

Watch for these signals that a learning should become a skill:

**In conversation:**
- "Save this as a skill"
- "I keep running into this"
- "This would be useful for other projects"
- "Remember this pattern"

**In learning entries:**
- Multiple `See Also` links (recurring issue)
- High priority + resolved status
- Category: `best_practice` with broad applicability
- User feedback praising the solution

### Skill Quality Gates

Before extraction, verify:

- [ ] Solution is tested and working
- [ ] Description is clear without original context
- [ ] Code examples are self-contained
- [ ] No project-specific hardcoded values
- [ ] Follows skill naming conventions (lowercase, hyphens)

## Multi-Agent Support

This skill works across different AI coding agents with agent-specific activation.

### Claude Code

**Activation**: Hooks (UserPromptSubmit, PostToolUse)
**Setup**: `.claude/settings.json` with hook configuration
**Detection**: Automatic via hook scripts

### Codex CLI

**Activation**: Hooks (same pattern as Claude Code)
**Setup**: `.codex/settings.json` with hook configuration
**Detection**: Automatic via hook scripts

### GitHub Copilot

**Activation**: Manual (no hook support)
**Setup**: Add to `.github/copilot-instructions.md`:

```markdown
## Self-Improvement

After solving non-obvious issues, consider logging to `.learnings/`:
1. Use format from self-improvement skill
2. Link related entries with See Also
3. Promote high-value learnings to skills

Ask in chat: "Should I log this as a learning?"
```

**Detection**: Manual review at session end

### OpenClaw

**Activation**: Workspace injection + inter-agent messaging
**Setup**: See "OpenClaw Setup" section above
**Detection**: Via session tools and workspace files

### Agent-Agnostic Guidance

Regardless of agent, apply self-improvement when you:

1. **Discover something non-obvious** - solution wasn't immediate
2. **Correct yourself** - initial approach was wrong
3. **Learn project conventions** - discovered undocumented patterns
4. **Hit unexpected errors** - especially if diagnosis was difficult
5. **Find better approaches** - improved on your original solution

### Copilot Chat Integration

For Copilot users, add this to your prompts when relevant:

> After completing this task, evaluate if any learnings should be logged to `.learnings/` using the self-improvement skill format.

Or use quick prompts:
- "Log this to learnings"
- "Create a skill from this solution"
- "Check .learnings/ for related issues"
- "/instinct-status" (v2)
- "/evolve" (v2)

---

## Privacy

- **Observations stay local** on your machine
- **Project-scoped instincts are isolated** per project
- **Only instincts (patterns) can be exported** — not raw observations
- **No actual code or conversation content is shared**
- You control what gets exported and promoted

## References

| Resource | Description |
|----------|-------------|
| everything-claude-code | ECC project that inspired v2 instinct-based architecture |
| Homunculus | Community project that influenced v2 design |
| OpenClaw | Workspace-based multi-agent platform |
| Agent Skills Spec | https://agentskills.io/specification |

---

*Instinct-based learning: teaching Claude your patterns, one project at a time.*
