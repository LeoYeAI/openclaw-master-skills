---
name: promote
description: Promote project-scoped instincts to global scope when proven across multiple projects.
---

# /promote

Promote project instincts to global scope when they prove broadly applicable.

## Usage

```bash
/promote
/promote instinct-id
/promote --auto
/promote --dry-run
```

## When to Promote

Promote an instinct to global when:
- Same instinct ID in 2+ projects
- Average confidence >= 0.8
- Pattern is not project-specific

## Auto-Promotion Criteria

```
Instinct qualifies for auto-promotion when:
- Seen in 2+ different projects
- Average confidence >= 0.8
- No conflicting instincts
```

## Example

```bash
# Promote a specific instinct
/promote always-validate-input

# Output:
# Promoting 'always-validate-input' to global scope...
# - Original: project my-react-app (0.85)
# - Merged with: project my-api (0.82)
# - New global confidence: 0.84
# - Copied to: ~/.claude/homunculus/instincts/personal/
# - Removed from: 2 project scopes
```

## Manual Review

Without arguments, `/promote` shows promotion candidates:

```
Promotion Candidates:

1. always-validate-input
   ├─ Projects: my-react-app (0.85), my-api (0.82)
   ├─ Average confidence: 0.84
   └─ [Promote? y/n]

2. grep-before-edit
   ├─ Projects: my-react-app (0.75), my-docs (0.70)
   ├─ Average confidence: 0.73
   └─ [Promote? y/n] (confidence below threshold)
```

## Options

| Option | Description |
|--------|-------------|
| `--auto` | Auto-promote all qualifying instincts |
| `--dry-run` | Preview without making changes |
| `--force` | Promote even if below confidence threshold |

## Related

- `/instinct-status` - View instincts and their scopes
- `/evolve` - Cluster instincts before promotion
- `/projects` - View all known projects
