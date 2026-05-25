---
title: "feat: Add Codex CLI compatibility"
type: feat
date: 2026-02-14
---

# feat: Add Codex CLI Compatibility

## Overview

Make /last30days work as a Codex CLI skill alongside Claude Code. Both platforms use `SKILL.md` with YAML frontmatter — the gap is small but the details matter. Inspired by PR #24 (el-analista) and PR #5 (jblwilliams) on the public repo, applied to the v2.1 codebase.

## Research Findings

### How Codex Skills Work (from [official docs](https://developers.openai.com/codex/skills))

**Format:** Identical to Claude Code — `SKILL.md` with YAML frontmatter + Markdown body.

**Required frontmatter:** Only `name` and `description`. The official skill-creator guidance says "Do not include any other fields in YAML frontmatter." This is stricter than Claude Code which allows `version`, `allowed-tools`, `argument-hint`, etc.

**Discovery:** Codex uses "progressive disclosure" — it reads ONLY the `description` field to decide whether to invoke a skill. The body loads only after triggering. This means the description must be comprehensive about when to use/not use the skill.

**Invocation:** Users invoke with `$skill-name` or `/skills` menu. Codex can also implicitly match based on the description (configurable via `agents/openai.yaml`).

**Installation paths** (scanned in order):
| Scope | Path |
|-------|------|
| Folder | `$CWD/.agents/skills/` |
| Repo | `$REPO_ROOT/.agents/skills/` |
| User | `$HOME/.agents/skills/` |
| Admin | `/etc/codex/skills/` |
| System | Bundled |

Note: Some docs also mention `~/.codex/skills/` as an alias for `$HOME/.agents/skills/`. Both should be checked.

**`agents/openai.yaml`** (optional sidecar):
```yaml
interface:
  display_name: "User-facing name"
  short_description: "Brief description"
  default_prompt: "Surrounding prompt template"
  brand_color: "#hex"
policy:
  allow_implicit_invocation: true
dependencies:
  tools:
    - type: "mcp"
      value: "toolName"
```

**Size guidance:** Keep SKILL.md under 500 lines. Use `references/` directory for detailed docs that load on demand.

**Scripts:** Put executable code in `scripts/`. These can run without being loaded into context — good for our Python research engine.

### What Real Codex Skills Look Like (from [openai/skills catalog](https://github.com/openai/skills))

**openai-docs skill** — Uses MCP tools (`mcp__openaiDeveloperDocs__search_openai_docs`). Has a workflow section, fallback instructions if MCP isn't set up, and quality rules. Clean and focused.

**pdf skill** — Runs scripts (`pdftoppm`, `reportlab`), has file conventions (`tmp/pdfs/`, `output/pdf/`), specifies dependencies. Good example of a skill that shells out to tools like we do.

**skill-creator** — The meta-skill. Emphasizes "the context window is a public good" and treating the LLM as "already very smart — only add information it genuinely lacks." Has 6 creation steps, validation scripts, and naming conventions.

### Key Insight: Frontmatter Compatibility Problem

Claude Code SKILL.md uses:
```yaml
name: last30days
version: "2.1"
description: Research a topic...
argument-hint: 'nano banana pro prompts...'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
```

Codex wants only `name` and `description`. The question: does Codex error on unknown frontmatter fields, or ignore them?

**Safe answer:** Codex uses standard YAML parsing and likely ignores unknown keys. But the official guidance says "Do not include any other fields" — meaning it's untested territory and could break in future Codex updates.

**Our approach:** Keep one SKILL.md with Claude-specific fields. If Codex chokes, we add a thin wrapper. This is pragmatic — maintaining two SKILL.md files defeats the purpose of cross-platform compatibility.

### PR #24 Analysis (el-analista)

Good ideas to incorporate:
- Portable script path resolution (repo → Claude → Codex → agents)
- `agents/openai.yaml` for Codex discovery
- Platform-neutral output text ("assistant" instead of "Claude")
- Sandbox-friendly cache/output dir fallbacks with env var overrides
- Last-chance retry for Bird search (better query noise stripping)

Not applicable to v2.1:
- Based on v2.0 codebase — doesn't have YouTube, vendored Bird, or pipeline changes
- We'll cherry-pick the ideas, not the code

### PR #5 Analysis (jblwilliams)

Not needed:
- Codex JWT auth — our OpenAI API calls work natively in Codex already
- SSE response handling — we don't stream responses
- The 403 enrichment issues they hit are specific to Codex-hosted auth, not our use case

## Proposed Solution

Five changes, all additive — zero impact on existing Claude Code behavior:

### 1. Add `agents/openai.yaml` for Codex discovery

```yaml
interface:
  display_name: "Last 30 Days"
  short_description: "Research any topic across Reddit, X, YouTube, and the web from the last 30 days. Returns synthesized expert answers and copy-paste prompts."
  default_prompt: "Research this topic from the last 30 days across Reddit, X, YouTube, and web. Synthesize what people are actually saying, upvoting, and sharing right now."
  brand_color: "#FF6B35"

policy:
  allow_implicit_invocation: true
```

### 2. Make SKILL.md script path portable

Replace the hardcoded Claude path with a lookup that checks multiple install locations:

```bash
# Find the skill root
for dir in \
  "." \
  "${CLAUDE_PLUGIN_ROOT:-}" \
  "$HOME/.claude/skills/last30days" \
  "$HOME/.agents/skills/last30days" \
  "$HOME/.codex/skills/last30days"; do
  [ -n "$dir" ] && [ -f "$dir/scripts/last30days.py" ] && SKILL_ROOT="$dir" && break
done

if [ -z "${SKILL_ROOT:-}" ]; then
  echo "ERROR: Could not find scripts/last30days.py" >&2
  exit 1
fi

python3 "${SKILL_ROOT}/scripts/last30days.py" "$ARGUMENTS" --emit=compact 2>&1
```

### 3. Platform-neutral Python output text

Replace "Claude" with "assistant" in LLM-facing output strings only. Human-facing docs (README, etc.) stay as-is.

Files:
- `scripts/last30days.py` — web search marker text (~3 lines)
- `scripts/lib/render.py` — docstrings + web-only banner (~4 lines)
- `scripts/lib/http.py` — User-Agent string (~1 line)

### 4. Sandbox-friendly cache/output dirs

Codex runs sandboxed. Add env var overrides + tempdir fallback (from PR #24):

**`scripts/lib/cache.py`:**
- Check `LAST30DAYS_CACHE_DIR` env var
- Catch `PermissionError`, fall back to `tempfile.gettempdir()/last30days/cache`

**`scripts/lib/render.py`:**
- Check `LAST30DAYS_OUTPUT_DIR` env var
- Catch `PermissionError`, fall back to `tempfile.gettempdir()/last30days/out`

### 5. README + installation docs

Add a "Codex Compatibility" section to README:

```markdown
## Codex Compatibility

This skill works in both Claude Code and OpenAI Codex CLI.

**Claude Code:** `git clone` into `~/.claude/skills/last30days`
**Codex CLI:** `git clone` into `~/.agents/skills/last30days`

Both use the same SKILL.md, same Python engine, same scripts.
The `agents/openai.yaml` provides Codex-specific discovery metadata.
```

## What We're NOT Doing

- **Separate SKILL.md for Codex** — One file, both platforms. Claude-specific frontmatter fields (`allowed-tools`, `version`, `argument-hint`) are likely ignored by Codex's YAML parser. If this breaks, we'll address it then.
- **Codex JWT auth (PR #5)** — Our OpenAI Responses API calls work natively in Codex. No special handling needed.
- **SSE streaming (PR #5)** — Not our use case.
- **Codex-specific tool names in SKILL.md** — Both LLMs understand "do a web search" and "run this bash command." The instructions work cross-platform as-is.
- **Publishing to openai/skills catalog** — Out of scope for now. Users install via git clone.

## Acceptance Criteria

- [x] `agents/openai.yaml` exists with proper `interface` and `policy` sections
- [x] SKILL.md uses portable path resolution (repo checkout, `~/.claude/skills/`, `~/.agents/skills/`, `~/.codex/skills/`)
- [x] Python scripts use "assistant" instead of "Claude" in LLM-facing output (~8 string replacements)
- [x] Cache dir falls back gracefully in sandboxed environments (`LAST30DAYS_CACHE_DIR` env var + `PermissionError` catch)
- [x] Output dir falls back gracefully in sandboxed environments (`LAST30DAYS_OUTPUT_DIR` env var + `PermissionError` catch)
- [x] Existing Claude Code behavior is unchanged (zero regressions)
- [x] README documents Codex installation path (`~/.agents/skills/last30days`)
- [x] `python3 scripts/last30days.py "test topic" --mock --emit=compact` still works

## Files to Create/Modify

### New Files
- `agents/openai.yaml` — Codex discovery metadata (~10 lines)

### Modified Files
- `SKILL.md` — Portable script path resolution (~15 lines changed)
- `README.md` — Add "Codex Compatibility" section (~15 lines)
- `scripts/last30days.py` — "Claude" → "assistant" in output strings (~3 lines)
- `scripts/lib/render.py` — "Claude" → "assistant" + output dir fallback (~15 lines)
- `scripts/lib/cache.py` — Cache dir env override + fallback (~12 lines)
- `scripts/lib/http.py` — User-Agent string (~1 line)

### Total scope: ~70 lines changed across 7 files. Small, additive, low risk.

## Dependencies & Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Codex rejects unknown YAML frontmatter (`allowed-tools`, etc.) | Low-Medium | Standard YAML parsers ignore unknown keys. If it breaks, strip Claude-specific fields and use `agents/openai.yaml` for metadata. |
| Codex sandbox blocks Node.js (vendored Bird) | Medium | Bird failure already falls back to xAI API. If no xAI key, X search skipped gracefully. |
| yt-dlp not in Codex sandbox PATH | Medium | YouTube already degrades gracefully — "yt-dlp not installed, skipping YouTube." |
| Codex sandbox blocks `~/.cache/` writes | Medium | Env var override + tempdir fallback handles this. (Proven approach from PR #24) |
| Codex changes skill discovery paths | Low | We check 5 paths. Easy to add more. |
| Codex description matching triggers on wrong queries | Low | Write description with clear "use when" / "do not use when" boundaries per official guidance. |

## References

### Community PRs
- [PR #24](https://github.com/mvanhorn/last30days-skill/pull/24) (el-analista) — Codex compatibility, portable paths, platform-neutral text
- [PR #5](https://github.com/mvanhorn/last30days-skill/pull/5) (jblwilliams) — Codex auth support

### Official Codex Docs
- [Agent Skills](https://developers.openai.com/codex/skills) — SKILL.md format, discovery, installation paths
- [AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md/) — Custom instructions, hierarchical loading
- [Codex CLI Features](https://developers.openai.com/codex/cli/features/) — Overview of CLI capabilities
- [Configuration Reference](https://developers.openai.com/codex/config-reference/) — config.toml, skill enable/disable

### Examples
- [openai/skills catalog](https://github.com/openai/skills) — Official curated skills
- [skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) — Meta-skill for creating skills, best practices
- [pdf skill](https://github.com/openai/skills/blob/main/skills/.curated/pdf/SKILL.md) — Example of skill that runs external scripts
- [openai-docs skill](https://github.com/openai/skills/blob/main/skills/.curated/openai-docs/SKILL.md) — Example of MCP-backed skill

### Community Analysis
- [Skills in OpenAI Codex](https://blog.fsck.com/2025/12/19/codex-skills/) — Jesse Vincent's deep dive on skill internals
- [Simon Willison on skills adoption](https://simonw.substack.com/p/openai-are-quietly-adopting-skills) — Cross-platform skill format analysis
- [SkillsMP marketplace](https://skillsmp.com/) — Community marketplace supporting both Claude Code and Codex skills
