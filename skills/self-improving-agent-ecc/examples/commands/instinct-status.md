---
name: instinct-status
description: Show all learned instincts (project-scoped + global) with confidence scores and metadata.
---

# /instinct-status

Display all learned instincts across project and global scopes.

## Usage

```bash
/instinct-status
/instinct-status --scope project
/instinct-status --scope global
/instinct-status --domain code-style
/instinct-status --confidence-above 0.7
```

## Output Format

```
Project: my-react-app (a1b2c3d4e5f6)
├─ prefer-functional-style.yaml (0.7) [project] [code-style]
│  └─ trigger: "when writing new functions"
├─ use-react-hooks.yaml (0.9) [project] [code-style]
│  └─ trigger: "when writing React components"
└─ jest-testing-patterns.yaml (0.6) [project] [testing]
   └─ trigger: "when writing tests"

Global Instincts:
├─ always-validate-input.yaml (0.85) [global] [security]
│  └─ trigger: "when handling user input"
├─ grep-before-edit.yaml (0.6) [global] [workflow]
│  └─ trigger: "when about to modify code"
└─ conventional-commits.yaml (0.75) [global] [git]
   └─ trigger: "when creating commits"

Summary:
- Project instincts: 3
- Global instincts: 3
- Total confidence average: 0.73
```

## Options

| Option | Description |
|--------|-------------|
| `--scope project\|global\|all` | Filter by scope (default: all) |
| `--domain <name>` | Filter by domain tag |
| `--confidence-above <0.0-1.0>` | Show only instincts above threshold |
| `--json` | Output as JSON for scripting |

## Related

- `/evolve` - Cluster instincts into skills
- `/promote` - Promote project instincts to global
- `/projects` - List all known projects
