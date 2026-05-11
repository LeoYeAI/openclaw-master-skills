# Agent Context Snippets

Use these snippets to wire Simplify & Harden into your active agent context file.
Pick one snippet per agent to avoid unnecessary prompt bloat.
These snippets are for interactive coding sessions.
For headless/CI execution, use `simplify-and-harden-ci`.

## Table of Contents

- [AGENTS.md (Generic / Multi-agent)](#agentsmd-generic--multi-agent)
- [CLAUDE.md (Claude Code)](#claudemd-claude-code)
- [.github/copilot-instructions.md (GitHub Copilot)](#githubcopilot-instructionsmd-github-copilot)
- [.cursorrules / .cursor/rules (Cursor)](#cursorrules--cursorrules-cursor)
- [.windsurfrules (Windsurf)](#windsurfrules-windsurf)
- [OpenClaw (AGENTS.md / CLAUDE.md)](#openclaw-agentsmd--claudemd)
- [Adapting for Other Agents](#adapting-for-other-agents)

### AGENTS.md (Generic / Multi-agent)

```markdown
## Post-Completion: Simplify & Harden

After completing any coding task, run the Simplify & Harden review before 
signaling done. This is mandatory for all non-trivial code changes.

**Scope:** Only review files you modified in this task. Do not touch adjacent code.

**Pass 1 -- Simplify:**
- The default action is lightweight cleanup: remove dead code, unused imports, 
  and scaffolding. Fix unclear names. Tighten control flow. Reduce unnecessary 
  public API surface. In interactive mode, apply these cosmetic fixes
  automatically. For CI/headless mode, use `simplify-and-harden-ci`.
- Refactoring (consolidation, restructuring, abstraction changes) is NOT the 
  default. Only propose a refactor when it is genuinely necessary or the benefit 
  is substantial. The bar is: would a senior engineer say the current state is 
  clearly wrong, not just imperfect? If you do propose a refactor, describe what 
  you want to change, why, and the estimated diff. Wait for explicit approval. 
  Present refactors one at a time.

**Pass 2 -- Harden:**
- In interactive mode, apply simple security patches (input validation, output
  escaping) automatically. For CI/headless mode, use `simplify-and-harden-ci`.
- For any security refactor: describe the vulnerability, severity, attack vector, 
  and proposed fix. Wait for explicit approval before proceeding.

**Pass 3 -- Document:**
- Add up to 5 single-line comments on non-obvious decisions you made during 
  implementation. If a future reader would need more than 5 seconds to understand 
  why something exists, comment it.

**Budget:** Additional changes must not exceed 20% of the original diff. If you 
hit the limit, stop and report what you found.

**Output:** End with a structured summary of what you applied, what you flagged, 
and what you left alone with reasoning.
```

### CLAUDE.md (Claude Code)

```markdown
## Post-Completion: Simplify & Harden

When you finish a coding task, do not immediately signal completion. First run 
the Simplify & Harden review on your own work.

### Rules
- Only review files you touched in this task
- Budget: max 20% additional diff on top of what you already changed
- Time: spend no more than 60 seconds on the review

### Simplify
Your default action is lightweight cleanup. Remove dead code, unused imports, 
and leftover scaffolding. Fix unclear names. Flatten unnecessary nesting. 
Reduce public surface area. In interactive mode, apply these directly -- they
are cosmetic, not structural. For CI/headless mode, use
`simplify-and-harden-ci`.

Do NOT default to refactoring. A refactor (merging functions, changing 
abstractions, restructuring logic) is only warranted when the current state is 
genuinely wrong or the improvement is substantial. If you think a refactor is 
justified: stop, describe the proposed change, explain why the current state 
is problematic (not just suboptimal), and ask me to approve before applying. 
One refactor at a time, never batched.

### Harden
Review your work for input validation gaps, injection vectors (SQL, XSS, 
command, path traversal), auth/authz issues, hardcoded secrets, error handling 
that leaks data, and race conditions. In interactive mode, apply simple patches
silently. For CI/headless mode, use `simplify-and-harden-ci`. For security
refactors that change code structure: stop, describe the vulnerability with
severity and attack vector, propose the fix, and ask me to approve.

### Document
Add up to 5 brief comments on non-obvious decisions. Especially: workarounds, 
performance choices, and anything that looks wrong but is intentional.

### Output
After the review, give me a short summary:
- What you fixed (cosmetic + patches)
- What you proposed and I approved/rejected
- What you noticed but left alone, and why
```

### .github/copilot-instructions.md (GitHub Copilot)

```markdown
## Post-Completion: Simplify & Harden

After completing a coding task, perform a self-review before marking the task 
as done. This review has three passes.

**Simplify:** Look at the code you just wrote with fresh eyes. Your default 
action is cleanup: remove dead code, unused imports, and scaffolding left over 
from iteration. Fix unclear names. Flatten unnecessarily nested logic. These 
cosmetic fixes can be applied directly in interactive mode. For CI/headless
mode, use `simplify-and-harden-ci`. Refactoring (merging functions, changing
abstractions, restructuring) is NOT the default. Only propose a refactor when 
the current code is genuinely wrong or the improvement is substantial -- not 
just "slightly better." If you do propose one, describe it and ask for approval. 
One at a time.

**Harden:** Check your work for security issues: unvalidated inputs, injection 
risks, missing auth checks, hardcoded credentials, error messages that leak 
internals, and unsafe concurrency patterns. In interactive mode, apply
straightforward fixes (adding a bounds check, escaping output) directly. For
CI/headless mode, use `simplify-and-harden-ci`. For anything that requires
structural changes, describe the issue with severity and proposed fix, and ask
for approval.

**Document:** Add up to 5 short comments explaining non-obvious decisions in the 
code you wrote. Focus on the "why", not the "what".

**Constraints:**
- Only touch files you modified in this task
- Keep additional changes under 20% of your original diff
- Refactors are rare and always require approval -- simplification is the default
```

### .cursorrules / .cursor/rules (Cursor)

```markdown
## Post-Completion: Simplify & Harden

After finishing a coding task, self-review before responding with "done."

Simplify: Default action is cleanup -- remove dead code, unused imports, fix 
naming, tighten control flow. In interactive mode, apply these directly. In
CI/headless mode, use `simplify-and-harden-ci`. Refactoring is rare. Only
propose a refactor when the code is genuinely wrong or the win is substantial.
If you do, describe it and wait for my approval. One at a time.

Harden: Fix obvious security gaps (missing validation, unescaped output, bare 
credentials) directly in interactive mode. For CI/headless mode, use
`simplify-and-harden-ci`. For structural security fixes: describe the vulnerability,
severity, and proposed fix. Wait for approval.

Document: Up to 5 comments on non-obvious decisions.

Rules:
- Only files you changed in this task
- Max 20% additional diff
- Simplify is the default, refactor is the exception
- Never apply a refactor without asking first
```

### .windsurfrules (Windsurf)

```markdown
## Post-Completion: Simplify & Harden

Before signaling task completion, review your own work:

1. Simplify -- default action is cleanup: remove dead code, fix naming, tighten 
   control flow, reduce API surface. In interactive mode, apply directly. For
   CI/headless mode, use `simplify-and-harden-ci`. Refactoring is the exception, not
   the rule. Only propose a refactor when genuinely necessary or the benefit is
   substantial. Always ask before applying.
2. Harden -- check for input validation, injection vectors, auth gaps, leaked 
   secrets, unsafe error handling. In interactive mode, apply simple patches
   directly. For CI/headless mode, use `simplify-and-harden-ci`. For structural
   security changes: ask first.
3. Document -- up to 5 comments on non-obvious decisions.

Scope: only files you touched. Budget: 20% max additional diff. Simplify is the 
default. Refactors are rare and always require explicit approval.
```

### OpenClaw (AGENTS.md / CLAUDE.md)

```markdown
## Post-Completion: Simplify & Harden

Before signaling task completion in OpenClaw, run Simplify & Harden on the 
files you changed in this task.

Use this skill for coding tasks only (writing or modifying executable source
code). Do NOT run it for general-agent work such as research, planning,
documentation-only edits, operations/admin tasks, or other non-coding requests.
If no executable code was changed, skip this skill.

**Scope and budget:**
- Only review files modified in this task
- Keep additional changes under 20% of the original diff
- Run passes in order: simplify, harden, document

**Simplify (default posture):**
- Apply lightweight cleanup first (dead code, unused imports, naming, control
  flow)
- In interactive sessions, apply cosmetic fixes directly
- Do not refactor by default
- For any refactor, STOP, describe the proposed change, and wait for explicit
  approval before applying

**Harden:**
- Check for validation gaps, injection vectors, auth/authz issues, secrets,
  data leaks, and race conditions
- In interactive sessions, apply straightforward security patches directly
- For security refactors, describe severity + attack vector and wait for
  explicit approval

**Document:**
- Add up to 5 short comments for non-obvious decisions

**Output:**
- End with a structured summary of applied fixes, approved/rejected refactors,
  and follow-up findings
```

OpenClaw repos commonly keep `CLAUDE.md` symlinked to `AGENTS.md`. If so,
update `AGENTS.md` once and keep the symlink in place.

### Adapting for Other Agents

The pattern is the same regardless of agent. Drop the relevant block into 
whatever file your agent reads for behavioral instructions. The key invariants 
that must be preserved:

1. **Scope lock** -- only files modified in the current task
2. **Budget cap** -- 20% max additional diff
3. **Simplify-first posture** -- cleanup is the default, refactoring is the exception
4. **Refactor stop hook** -- structural changes always require human approval
5. **Three passes** -- simplify, harden, document (in that order)
6. **Structured output** -- summary of applied, approved, rejected, and flagged items

> **Precaution:** The refactor stop hook depends on the agent actually pausing 
> and waiting for human input. Not all agents are equally reliable at this. Some 
> may acknowledge the instruction but proceed anyway, especially under aggressive 
> autonomy settings or in agentic loops with auto-approve enabled. Test your 
> agent's compliance before trusting it with this skill in production. If an agent 
> consistently fails to stop on refactors, reinforce the instruction with stronger 
> phrasing (e.g., "STOP. Do not proceed. Wait for my explicit approval.") or 
> restrict it to headless/flag-only mode until behavior is verified.
