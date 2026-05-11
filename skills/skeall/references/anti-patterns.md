# Anti-patterns in Agent Skills

Real examples from auditing and restructuring production skills. Each pattern includes before/after text.

## Contents

- [Structure anti-patterns](#structure-anti-patterns) (#1-3)
- [Frontmatter anti-patterns](#frontmatter-anti-patterns) (#4-6)
- [Content anti-patterns](#content-anti-patterns) (#7-10)
- [LLM-friendliness anti-patterns](#llm-friendliness-anti-patterns) (#11-17)
- [Cross-platform anti-patterns](#cross-platform-anti-patterns) (#18-21)
- [Maintenance anti-patterns](#maintenance-anti-patterns) (#22-23)
- [Completeness anti-patterns](#completeness-anti-patterns) (#24-26)
- [Security anti-patterns](#security-anti-patterns) (#27-29)

---

## Structure anti-patterns

### 1. Flat file layout (no references/ directory)

All .md files dumped at skill root instead of organized in references/.

```text
# BAD
my-skill/
├── SKILL.md
├── inference.md
├── fine-tuning.md
├── account-management.md
└── examples.md

# GOOD
my-skill/
├── SKILL.md
├── references/
│   ├── inference.md
│   ├── fine-tuning.md
│   ├── account-management.md
│   └── examples/
│       └── README.md
└── README.md
```

### 2. Monolithic SKILL.md (everything in one file)

Entire skill crammed into SKILL.md. No progressive disclosure. LLM loads 20,000 tokens when 3,000 would suffice.

**Fix:** Keep core patterns in SKILL.md (~70% of requests). Move detailed workflows, complete examples, and edge cases to references/.

### 3. Broken internal links after file moves

When files move to references/, links break silently. Markdown renderers don't warn about dead links.

```markdown
# Before move (from root)
See [inference.md](inference.md)

# After move to references/ (from SKILL.md at root)
See [references/inference.md](references/inference.md)

# Common mistake: forgetting to update
See [inference.md](inference.md)  ← BROKEN
```

---

## Frontmatter anti-patterns

### 4. Persona-style description

```yaml
# BAD — persona-based, vague triggers
description: Expert in building web applications with React and Node.js.

# GOOD — instruction-based, specific triggers
description: React and Node.js development guide. Covers component patterns,
  API routes, state management, testing, and deployment. Use for any React,
  Next.js, Express, or full-stack JavaScript question.
```

### 5. Description too long (spec limit 1024 chars, recommended under 300)

Over 1024 breaks spec compliance (HIGH). Over 300 hurts matching on some platforms (LOW). Long descriptions bury trigger phrases.

### 6. Missing trigger phrases

The description must include phrases users actually type. If users say "how do I deploy" but description only says "infrastructure management", the skill won't activate.

---

## Content anti-patterns

### 7. Repeated content across sections

The same concept explained in multiple places. Tokens wasted, contradiction risk.

```markdown
# BAD — processResponse explained 3 times
## SDK Quick Start
...call processResponse(provider, content, chatID)...

## Response Verification
...always call processResponse(provider, content, chatID)...

## Best Practices
...remember to call processResponse(provider, content, chatID)...

# GOOD — single source of truth
## processResponse (critical)
Call after EVERY response. Parameter order: provider, content, chatID.

## SDK Quick Start
...see processResponse section above...
```

### 8. Deprecation notice at the top

Wastes prime token space. Primes the LLM to distrust the skill.

```markdown
# BAD — first thing LLM reads
> WARNING: This skill is deprecated. Use new-skill instead.

# GOOD — at the bottom, soft note
> Note: A newer unified skill exists at [new-skill]. This skill covers X specifically.
```

### 9. Phantom API documentation

Documenting functions that don't exist in the actual SDK/codebase. LLMs will generate code that crashes at runtime.

**Prevention:** Verify every API, function, and method against actual source code before documenting.

### 10. Stale data (wrong model names, old addresses, outdated versions)

Data that was correct at writing time but has changed. Especially common with:
- Model names (on-chain names change)
- Provider addresses (rotate frequently)
- Package versions (breaking changes)

**Fix:** Add a note: "Model availability changes frequently. Always use `list` commands to check current state." Don't hardcode lists that go stale.

---

## LLM-friendliness anti-patterns

### 11. Bullet lists with arrows instead of tables

```markdown
# BAD — LLMs parse inconsistently
- **Chatbot**: Try `ZG-Res-Key` header → fallback to `data.id`
- **Image**: Always use `ZG-Res-Key` → no fallback

# GOOD — clean table, all LLMs parse correctly
| Service Type | Primary Source | Fallback |
|---|---|---|
| Chatbot | `ZG-Res-Key` header | `data.id` from response |
| Image | `ZG-Res-Key` header | none |
```

### 12. Persona-based framing

```markdown
# BAD — Claude-leaning, other LLMs respond differently
You are an expert in distributed systems. You specialize in...

# GOOD — universal instruction framing
This skill provides instructions for building distributed systems.
Follow these patterns exactly when generating code.
```

### 13. Emoji in structural elements

```markdown
# BAD — tokens wasted, parsed inconsistently
## 🔧 Configuration
## ✅ Verification Steps
## ⚠️ Important Warnings

# GOOD — clean headings
## Configuration
## Verification steps
## Important warnings
```

### 14. Long checklists instead of tables

```markdown
# BAD — 12-item checklist, critical rules buried
When generating code:
1. Always import ethers
2. Use environment variables
3. Never hardcode secrets
4. Call processResponse after every response
5. Check balance before operations
6. Handle streaming correctly
7. Use correct model names
8. Acknowledge providers first
9. Monitor fund levels
10. Handle errors gracefully
11. Log usage for debugging
12. Test on testnet first

# GOOD — 4 hard rules, details in references
## Code generation rules

1. Copy code patterns from this skill verbatim. Do NOT generate from training data.
2. Call processResponse() after every API response.
3. Use environment variables for private keys. Never hardcode secrets.
4. Route users to testnet for initial development.
```

### 15. Vague modifiers instead of specifics

```markdown
# BAD
The token budget should be reasonable. Keep the file relatively short.

# GOOD
The token budget must be under 5000 tokens. Keep the file under 500 lines.
```

### 16. Nested blockquotes

```markdown
# BAD — some LLMs lose track of nesting
> Note: This is important.
> > Especially this nested part.
> > > And this triple-nested warning.

# GOOD — flat structure
**Note:** This is important. The nested detail goes here as regular text.
```

### 17. Inconsistent code block language tags

```markdown
# BAD — no language tag, inconsistent
```
const x = 1;
```

# GOOD — always tag
```typescript
const x = 1;
```
```

---

## Cross-platform anti-patterns

### 18. baseDir placeholder

```markdown
# BAD — only OpenClaw resolves this
See {baseDir}/references/guide.md

# GOOD — relative path works everywhere
See [references/guide.md](references/guide.md)
```

### 19. Platform-specific instructions

```markdown
# BAD
To use this skill in Claude Code, type /my-skill. In Codex, it auto-activates.

# GOOD (in README.md, not SKILL.md)
## Installation
- Claude Code: ~/.claude/skills/my-skill/
- Codex: ~/.agents/skills/my-skill/
```

### 20. Hardcoded absolute paths

```markdown
# BAD
Read the config at /Users/john/.claude/skills/my-skill/config.json

# GOOD
Read the config at references/config.json (relative to this SKILL.md)
```

### 21. Time-sensitive information

Instructions that expire or change meaning over time. Common with API versions, migration deadlines, and feature flags.

```markdown
# BAD -- becomes wrong after the deadline passes
If you're doing this before August 2025, use the old API endpoint.
After August 2025, switch to v2.

# GOOD -- version-based, not date-based
Use API v2 (`/api/v2/`). If the codebase still uses v1 imports,
migrate them: `import { client } from '@sdk/v2'`.
```

**Fix:** Use version numbers or feature detection instead of dates. If dates are unavoidable, add: "Check the official docs for current migration status."

---

## Maintenance anti-patterns

### 22. Unverified claim placeholders

Placeholder markers left in published skills. LLMs may include them in generated output or treat them as real data.

```markdown
# BAD -- placeholders shipped to users
The API processes 10,000 requests per second [source needed].
Average latency is 50ms [TODO: verify].

# GOOD -- either verify or remove
The API processes 10,000 requests per second (measured via load test, Jan 2026).
```

**Fix:** Search all skill files for `[source needed]`, `[TODO]`, `[TBD]`, `[verify]`, `[citation needed]` before publishing.

### 23. Non-standard reference directory

Using a directory name other than `references/` for on-demand detail files. Other tools and platforms expect `references/`.

```text
# BAD -- non-standard path
my-skill/
├── SKILL.md
└── docs/references/
    └── guide.md

# GOOD -- standard path
my-skill/
├── SKILL.md
└── references/
    └── guide.md
```

**Fix:** Move files to `references/` at skill root. Update all internal links.

---

## Completeness anti-patterns

### 24. Incomplete routing table (C9)

SKILL.md has a routing table but it doesn't cover all files in references/.

```markdown
# BAD -- references/ has 5 files, routing table lists 3
## References
- [API guide](references/api.md)
- [Examples](references/examples.md)
- [Config](references/config.md)

# (references/troubleshooting.md and references/migration.md exist but aren't listed)

# GOOD -- every file in references/ appears in routing table
## References
- [API guide](references/api.md)
- [Examples](references/examples.md)
- [Config](references/config.md)
- [Troubleshooting](references/troubleshooting.md)
- [Migration guide](references/migration.md)
```

**Fix:** List the contents of references/ and verify each file appears in the routing table. Add missing entries.

### 25. Count mismatch between claims and content (C10)

Description or body claims a specific number that doesn't match reality.

```yaml
# BAD -- description says 34 but body only has 28
description: Detects and removes 34 AI writing patterns from blog content.
# (actual patterns numbered 1-28 in the body)

# GOOD -- count matches
description: Detects and removes 28 AI writing patterns from blog content.
# (patterns 1-28 documented in body and references)
```

**Fix:** Search for numeric claims in description and body. Count the actual items. Update the claim or add the missing items.

### 26. Stale API/function references (C11)

Documenting functions, model names, or versions that no longer exist.

```markdown
# BAD -- function doesn't exist in actual SDK
## Health monitoring
Call `getProviderHealth(address)` to check provider status.

# (SDK source code has no getProviderHealth function -- it was removed in v2)

# GOOD -- verified against source
## Health monitoring
Call `listServiceWithDetail()` to check provider availability.
Provider health is inferred from service listing status.
```

**Fix:** Verify every documented API, function, and method against actual source code. Remove phantom references. Add a note if data changes frequently: "Use `list` commands to check current state."

---

## Security anti-patterns

### 27. Hardcoded credentials in skill files

Real API keys, JWT tokens, or secrets written directly into SKILL.md. Found in 4 of 22 production skills audited — including HA JWT tokens and API keys committed and visible to anyone with repo access.

```markdown
# BAD — real credential in SKILL.md
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOi..." \
  http://homeassistant.local/api/states

# GOOD — environment variable reference
curl -H "Authorization: Bearer $HA_TOKEN" \
  http://homeassistant.local/api/states
```

**Fix:** Always reference environment variables by name. Never put real tokens in SKILL.md, even for "local only" or "personal" skills — skill files get committed to git, synced, and shared. Add a setup section documenting which env vars are required and how to set them.

```markdown
## Setup

Set required environment variables before using this skill:

    export HA_TOKEN="your-home-assistant-token"
    export HA_URL="http://homeassistant.local"
```

### 28. Silent skill deactivation from name/directory mismatch

The `name` field in SKILL.md frontmatter does not match the parent directory name. The platform cannot locate the skill by name, so it silently ignores it. The skill appears installed but never activates — no error, no warning.

Found in 3 of 22 production skills audited. This is the sneakiest bug in the list.

```yaml
# BAD — directory is home-assistant/, but name says homeassistant
# The platform looks for a skill named "homeassistant" in a directory
# named "homeassistant" — it never finds it.
---
name: homeassistant
description: Home Assistant control skill.
---
```

```yaml
# GOOD — name matches directory exactly
# Directory: home-assistant/
# Name: home-assistant
---
name: home-assistant
description: Home Assistant control skill.
---
```

**Fix:** The `name` field must be an exact match for the parent directory name — same hyphens, same casing (lowercase). When renaming one, always update the other. Run `--scan` after any rename; S8 catches this.

Common mismatch patterns:

| Directory name | Wrong `name` value | Correct `name` value |
|---|---|---|
| `home-assistant/` | `homeassistant` | `home-assistant` |
| `self-improving-agent/` | `self-improvement` | `self-improving-agent` |
| `denizevi-speakers/` | `denizevi` | `denizevi-speakers` |

### 29. Platform-specific path placeholders

Using `{baseDir}` or similar template variables that only one platform resolves. Skills with `{baseDir}` work on OpenClaw but silently fail everywhere else — the placeholder is treated as a literal string.

Found in 2 of 22 production skills audited, with `{baseDir}` appearing 8–13 times per skill.

```markdown
# BAD — only OpenClaw resolves {baseDir}
Run the analysis script:

    bash {baseDir}/scripts/analyze.sh

Load the config from `{baseDir}/references/config.json`.
```

```markdown
# GOOD — relative path from SKILL.md, works everywhere
Run the analysis script:

    bash scripts/analyze.sh

Load the config from `references/config.json`.
```

**Fix:** Use relative paths from the SKILL.md location. If an absolute path is unavoidable (e.g., cron jobs, system scripts), document it in a setup section rather than inline in instructions:

```markdown
## Setup

After cloning, note the full path to this skill directory and set it as an env var:

    export SKILL_DIR="/path/to/my-skill"

All script references in this skill are relative to that path.
```

**Do not use:** `{baseDir}`, `${SKILL_ROOT}`, `$SKILL_PATH`, or any other placeholder that requires platform-specific resolution.
