# Skeall

Build, improve, and audit [Agent Skills](https://agentskills.io) for cross-platform LLM coding agents.

Skeall encodes real-world lessons from building and restructuring production skills across Claude Code, OpenAI Codex, Cursor, Gemini CLI, OpenClaw, and 20+ other platforms that support the Agent Skills open standard.

## What it does

- **Create** new skills from scratch with guided interviews and scaffolding
- **Improve** existing skills with specific before/after edit proposals
- **Scan** skills for spec compliance, LLM-friendliness, and cross-platform issues
- **Batch scan** your entire skill collection at once
- **Health check** runtime issues that static scan misses: orphans, duplicates, broken deps, stale endpoints

## Installation

```bash
# Claude Code
git clone https://github.com/dorukardahan/skeall ~/.claude/skills/skeall

# OpenAI Codex
git clone https://github.com/dorukardahan/skeall ~/.agents/skills/skeall

# OpenClaw
git clone https://github.com/dorukardahan/skeall ~/.openclaw/skills/skeall
```

## Usage

```text
/skeall --create              # Interview + scaffold new skill
/skeall --improve <path>      # Analyze and improve existing skill
/skeall --scan <path>         # Audit only, severity-tagged report
/skeall --scan-all            # Batch scan all skills
/skeall --healthcheck <path>  # Runtime check single skill
/skeall --healthcheck-all     # Runtime check all skills
```

## What it checks

**Static scan:** 42 checklist items across 6 categories:

| Category | Checks | Examples |
|----------|--------|---------|
| Structure | 8 | SKILL.md exists, name matches dir, references/ dir, no junk files |
| Frontmatter | 6 | Description length (spec + recommended), trigger phrases, naming |
| Content | 11 | Token budget, redundancy, framing style, routing table, count consistency, stale refs |
| LLM-friendliness | 8 | Tables vs bullets, emoji, heading style |
| Security | 5 | No XML injection, no reserved names, no secrets, credential pattern detection |
| Cross-platform | 4 | No baseDir, relative paths, standard links |

**Runtime health check:** 7 additional checks that static scan cannot catch:

| Check | What it catches |
|-------|----------------|
| R1 Orphan detection | Skills that exist but never activate |
| R2 Duplicate detection | Same skill name in multiple directories |
| R3 Trigger collision | Two skills matching the same input |
| R4 Broken dependencies | Referenced scripts/files that don't exist |
| R5 Stale endpoints | curl URLs returning 404/timeout |
| R6 Missing env vars | $VAR references without matching environment |
| R7 Cost estimation | Token budget per skill per session |

**Total: 49 checks** (42 static + 7 runtime). Plus 29 documented anti-patterns with before/after examples.

## Scoring

Base score: 10. Deductions: HIGH (-1.5), MEDIUM (-0.5, capped at -3), LOW (-0.2, capped at -1).

| Score | Rating |
|-------|--------|
| 9-10 | Excellent |
| 7-8 | Good (PASS) |
| 5-6 | Needs work |
| 0-4 | Major rewrite needed |

## Structure

```text
skeall/
├── SKILL.md                    # Core skill (always loaded)
├── references/
│   ├── anti-patterns.md        # 29 anti-patterns with before/after
│   ├── healthcheck.md          # Runtime check algorithms and real examples
│   ├── template.md             # Copy-paste SKILL.md template
│   ├── scoring.md              # Scoring methodology details
│   ├── testing.md              # Testing patterns and examples
│   └── advanced-patterns.md   # Categories, freedom, distribution, MCP, workflows
└── README.md                   # This file
```

## Built on real experience

Skeall was born from restructuring [0gfoundation/0g-compute-skills](https://github.com/0gfoundation/0g-compute-skills):
- Audited 19 documentation issues (phantom APIs, wrong model names, parameter order bugs)
- Restructured from flat layout to Agent Skills standard (references/ directory)
- Reduced SKILL.md from 373 lines (~4,800 tokens) to 177 lines (~2,500 tokens)
- Achieved 62% token savings through progressive disclosure

### Field testing: 22 production skills

Skeall was used to audit 22 production skills across OpenClaw and custom skill directories:

- **22 skills scanned**, 14 needed work, 8 passed
- Top issues found: hardcoded credentials (4 skills), name/directory mismatches (3), platform-specific placeholders (2)
- 3 new anti-patterns documented from findings (#27-#29)
- 1 credential detection check added (SEC5)
- Average score improved from 5.2 to 7.8 after fixes

Runtime healthcheck then surfaced what static linting missed:

- 1 ghost skill found (installed for weeks, never activated)
- 2 duplicate skills found across directories
- 3 trigger collisions between similar skills
- 4 skills with broken script dependencies

Static linting catches formatting issues. Healthcheck catches the bugs that actually break your workflow.

### Paired with RePrompter

The audit agents, self-review teams, and skill restructuring work above were all orchestrated through [RePrompter](https://github.com/AytuncYildizli/reprompter) — a prompt engineering skill that turns rough instructions into structured, scored agent prompts. Every multi-agent run in skeall's development used RePrompter's Repromptception mode to generate per-agent prompts, score them (target 8+/10), and retry on misses.

Skeall's `--create` mode optionally hands off to RePrompter for description optimization after scaffolding. If you're building skills and want tighter prompts, it's worth having both installed.

Research sources: [agentskills.io spec](https://agentskills.io), [Anthropic skills guide](https://claude.com/blog/complete-guide-to-building-skills-for-claude), [OpenAI Codex docs](https://developers.openai.com/codex/skills/), [OpenClaw docs](https://docs.openclaw.ai/tools/skills).

## License

MIT
