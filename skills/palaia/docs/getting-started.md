# Getting Started

## Installation

```bash
pip install palaia
```

Or install from source:

```bash
git clone https://github.com/iret77/palaia.git
cd palaia
pip install -e .
```

## Initialize

Create a `.palaia` directory in your workspace:

```bash
palaia init
```

This creates the directory structure:

```
.palaia/
├── config.json
├── hot/
├── warm/
├── cold/
├── wal/
└── index/
```

## Write Your First Memory

```bash
palaia write "Python's GIL prevents true multi-threading for CPU-bound tasks" \
  --title "Python GIL" \
  --scope team \
  --tags "python,concurrency"
```

Output:

```
Written: a1b2c3d4-...
```

## Query Memories

```bash
palaia query "python threading"
```

Output:

```
🔥 [3.1415] Python GIL
  ID: a1b2c3d4-...
  Scope: team | Decay: 0.693147
  Tags: python, concurrency
  Python's GIL prevents true multi-threading for CPU-bound tasks

1 result(s) found. (Search tier: BM25)
```

## List Entries

```bash
# List HOT tier (default)
palaia list

# List WARM tier
palaia list --tier warm

# List COLD tier
palaia list --tier cold
```

## Check Status

```bash
palaia status
```

Output:

```
Palaia v0.1.0
Root: /path/to/.palaia

Entries:
  🔥 HOT:  1
  🌤  WARM: 0
  ❄️  COLD: 0
  Total: 1

Search: BM25 (Python)
```

## Garbage Collection

Rotate entries between tiers based on decay scores:

```bash
palaia gc
```

## Export & Import

Share public memories across workspaces:

```bash
# Export public entries to a directory
palaia export

# Export to a git remote
palaia export --remote git@github.com:org/knowledge.git

# Import from a directory
palaia import ./palaia-export/

# Preview what would be imported
palaia import ./palaia-export/ --dry-run
```

## Scope Tags

Every entry has a scope that controls visibility:

| Scope | Visibility |
|-------|-----------|
| `private` | Only the writing agent |
| `team` | All agents in the workspace (default) |
| `shared:<name>` | Agents with access to project `<name>` |
| `public` | Exportable via `palaia export` |

```bash
palaia write "API key rotation procedure" --scope private --agent ops-bot
palaia write "Team coding standards" --scope team
palaia write "Public API docs" --scope public
```

## Next Steps

- Read the [CLI Reference](cli-reference.md) for all commands and flags
- Check [Architecture](../ARCHITECTURE.md) for design details
- Browse the [ADRs](adr/001-semantic-search-tiered.md) for decision records
