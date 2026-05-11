---
name: evolve
description: Cluster related instincts into skills, commands, or agents. Suggests promotions for instincts seen across multiple projects.
---

# /evolve

Analyze instincts and evolve them into reusable skills, commands, or agents.

## Usage

```bash
/evolve
/evolve --from project
/evolve --suggest-promotions
/evolve --auto-create
```

## How It Works

1. **Cluster Analysis** - Groups related instincts by domain and trigger similarity
2. **Skill Generation** - Creates skill files from high-confidence clusters
3. **Command Extraction** - Identifies common workflows as slash commands
4. **Agent Creation** - Builds specialized agents for complex patterns
5. **Promotion Suggestions** - Recommends instincts for global promotion

## Example Output

```
Analyzing 12 instincts...

Clusters Found:
├─ React Patterns (3 instincts)
│  └─ Suggested: Create skill 'react-patterns'
│
├─ Testing Workflows (2 instincts)
│  └─ Suggested: Create command '/test-suite'
│
├─ Security Practices (2 instincts)
│  └─ Suggested: Promote to global (high confidence)
│
└─ Code Style (5 instincts)
   └─ Suggested: Create skill 'typescript-standards'

Promotion Candidates:
├─ always-validate-input (0.85) - Seen in 3 projects
└─ grep-before-edit (0.75) - Seen in 2 projects

Run with --auto-create to generate files, or review suggestions above.
```

## Generated Skill Example

When `/evolve` creates a skill from instincts:

```markdown
---
name: react-patterns
description: Patterns for React development based on learned instincts.
---

# React Patterns

## When to Use

- Building React components
- Managing state and side effects
- Writing tests for React code

## Patterns

### Prefer Functional Components
Confidence: 0.9 | Source: 5 instincts

Use functional components with hooks instead of classes.

### Custom Hooks for Reusable Logic
Confidence: 0.8 | Source: 3 instincts

Extract component logic into custom hooks.

[... more patterns ...]
```

## Options

| Option | Description |
|--------|-------------|
| `--from project\|global\|all` | Source instincts (default: all) |
| `--suggest-promotions` | Only show promotion candidates |
| `--auto-create` | Automatically create suggested files |
| `--dry-run` | Preview without creating files |

## Related

- `/instinct-status` - View all instincts
- `/promote` - Promote instincts to global scope
