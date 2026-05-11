# Migration Guide: CLAUDE.md → CC_GodMode Skill

How to migrate from using CC_GodMode via CLAUDE.md to the OpenClaw Skill.

## Overview

| Aspect | CLAUDE.md (Claude Code) | OpenClaw Skill |
|--------|------------------------|----------------|
| Installation | Copy to project root | `clawdhub install cc-godmode` |
| Updates | Manual copy | `clawdhub update cc-godmode` |
| Scope | Per-project | System-wide |
| Discovery | Must know about it | ClawHub marketplace |
| Agent files | `~/.claude/agents/` | Same (unchanged) |

## Migration Steps

### Step 1: Install the Skill

```bash
clawdhub install cc-godmode
```

### Step 2: Verify Installation

```bash
clawdhub list | grep cc-godmode
```

You should see:
```
cc-godmode  5.11.1  Self-orchestrating multi-agent development workflows
```

### Step 3: Agent Files (No Change Needed!)

Your agent files in `~/.claude/agents/` continue to work:
- `researcher.md`
- `architect.md`
- `api-guardian.md`
- `builder.md`
- `validator.md`
- `tester.md`
- `scribe.md`
- `github-manager.md`

The skill references the same agents you already have.

### Step 4: Remove Project CLAUDE.md (Optional)

If you only used CLAUDE.md for CC_GodMode orchestration:

```bash
# In your project directory
rm CLAUDE.md
```

If your CLAUDE.md has project-specific instructions, keep it! The skill and project CLAUDE.md can coexist.

### Step 5: Test the Migration

Start an OpenClaw session and try:

```
New Feature: Test feature for migration verification
```

The orchestrator should:
1. Recognize the command
2. Select appropriate workflow
3. Call agents via Task tool

## What Changes

### Commands (Same!)

All commands work identically:

| Command | CLAUDE.md | Skill |
|---------|-----------|-------|
| `New Feature: X` | ✓ | ✓ |
| `Bug Fix: X` | ✓ | ✓ |
| `API Change: X` | ✓ | ✓ |
| `Research: X` | ✓ | ✓ |
| `Process Issue #X` | ✓ | ✓ |
| `Prepare Release` | ✓ | ✓ |

### Agent Calls (Same!)

Agents are still called via Task tool with `subagent_type`:

```
subagent_type: "researcher"
subagent_type: "architect"
subagent_type: "builder"
...
```

### Report Structure (Same!)

Reports still go to:
```
reports/
└── v[VERSION]/
    ├── 00-researcher-report.md
    ├── 01-architect-report.md
    ...
```

## Coexistence Mode

**CLAUDE.md and the Skill can coexist!**

Use this when:
- Your project has project-specific CLAUDE.md instructions
- You want to override certain skill behaviors
- You're testing before full migration

### Priority Order

1. Project `CLAUDE.md` (highest)
2. OpenClaw Skill `SKILL.md`
3. Agent files in `~/.claude/agents/`

### Example Coexistence

**Project CLAUDE.md:**
```markdown
# Project-Specific Instructions

## This Project Uses
- React 18 with TypeScript
- Tailwind CSS
- Prisma ORM

## Special Rules
- All components must be in `src/components/`
- Use Zustand for state management
- No Redux allowed

[CC_GodMode orchestration comes from the skill]
```

**The skill provides:** Orchestration, workflows, agent coordination
**Project CLAUDE.md provides:** Project-specific rules and context

## Rollback

If you need to go back to CLAUDE.md:

### Step 1: Uninstall Skill

```bash
clawdhub uninstall cc-godmode
```

### Step 2: Restore CLAUDE.md

Copy from CC_GodMode repository:
```bash
cp ~/Projects/ClawdBot-GodMode/CLAUDE.md ./CLAUDE.md
```

## Version Mapping

| CC_GodMode | Skill | Status |
|------------|-------|--------|
| v5.11.1 | 5.11.1 | Current |
| v5.10.x | - | Not available as skill |
| v5.9.x | - | Not available as skill |

Skills start from v5.11.1. For older versions, use CLAUDE.md directly.

## FAQ

### Q: Will my existing projects break?

No! The skill is additive. Your existing CLAUDE.md files continue to work.

### Q: Can I use different skill versions for different projects?

Currently, skills are system-wide. For project-specific versions, use CLAUDE.md.

### Q: What about custom agents?

Custom agents in `~/.claude/agents/` continue to work. The skill only provides orchestration.

### Q: Do I need to update agent files?

No. Agent files are separate from the skill. Update them independently when CC_GodMode releases new agent versions.

### Q: How do I get skill updates?

```bash
clawdhub update cc-godmode
```

Or for specific version:
```bash
clawdhub install cc-godmode@5.12.0
```

## Getting Help

- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Complete Skill Documentation](../SKILL.md)
- [CC_GodMode Repository](https://github.com/clawdbot/ClawdBot-GodMode)
