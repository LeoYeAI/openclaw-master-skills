# Self-Improving Agent v2.1

An advanced instinct-based continuous learning system for Claude Code.

## What's New in v2.1

- **Project-scoped instincts** — React patterns stay in React projects, Python in Python projects
- **Confidence scoring** — 0.3 (tentative) to 0.9 (near-certain)
- **Hook-based observation** — PreToolUse/PostToolUse capture 100% of activity
- **Instinct evolution** — Auto-cluster into skills, commands, agents
- **Promotion workflow** — Project → Global when proven across projects

## Quick Start

### 1. Enable Observation Hooks

Add to `~/.claude/settings.json`:

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

### 2. Use v2 Commands

```bash
/instinct-status     # View learned instincts
/evolve              # Cluster into skills
/promote             # Promote to global scope
/projects            # List known projects
```

### 3. Create Instincts Manually

```yaml
---
id: my-instinct
trigger: "when to apply"
confidence: 0.7
domain: "code-style"
scope: project
---

# Title

## Action
What to do.

## Examples
[...]
```

## Directory Structure

```
~/.claude/homunculus/
├── instincts/personal/       # Global auto-learned
├── instincts/inherited/      # Global imported
├── evolved/                  # Generated skills/commands/agents
└── projects/
    └── <hash>/
        ├── instincts/        # Project-scoped
        └── evolved/          # Project-specific skills
```

## Migration from v1

v2 is fully backward compatible:
- Existing `.learnings/*.md` files still work
- Existing global instincts still work
- Gradual migration supported

## Documentation

- `SKILL.md` - Full skill documentation
- `examples/instincts/` - Sample instinct files
- `examples/commands/` - Command documentation
- `hooks/observe.sh` - Observation hook script

## References

- Based on everything-claude-code continuous-learning-v2
- Inspired by Homunculus community project
