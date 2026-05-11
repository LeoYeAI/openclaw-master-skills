# CLI Reference

## Global Options

```
palaia --version    Show version
palaia --help       Show help
```

---

## `palaia init`

Initialize a `.palaia` directory.

```bash
palaia init [--path <directory>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--path` | `.` | Target directory |

---

## `palaia write`

Write a memory entry.

```bash
palaia write <text> [--scope <scope>] [--agent <name>] [--tags <tags>] [--title <title>]
```

| Argument/Flag | Default | Description |
|--------------|---------|-------------|
| `text` | (required) | Memory content |
| `--scope` | `team` | Scope tag: `private`, `team`, `shared:<name>`, `public` |
| `--agent` | `None` | Agent name (required for `private` scope) |
| `--tags` | `None` | Comma-separated tags |
| `--title` | `None` | Entry title |

Entries are automatically deduplicated by content hash.

**Examples:**

```bash
palaia write "Docker containers share the host kernel" --title "Docker basics" --tags "docker,containers"
palaia write "Secret rotation every 90 days" --scope private --agent security-bot
palaia write "Team standup at 10am" --scope team --title "Standup"
```

---

## `palaia query`

Search memories using BM25 (keyword search).

```bash
palaia query <query> [--limit <n>] [--all]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | `10` | Maximum number of results |
| `--all` | `false` | Include COLD tier in search |

**Examples:**

```bash
palaia query "docker networking"
palaia query "deployment" --limit 5
palaia query "legacy system" --all
```

---

## `palaia list`

List entries in a specific tier.

```bash
palaia list [--tier <hot|warm|cold>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--tier` | `hot` | Tier to list |

---

## `palaia status`

Show system status: entry counts per tier, WAL state, search tier.

```bash
palaia status
```

---

## `palaia gc`

Run garbage collection. Rotates entries between tiers based on decay scores and cleans up old WAL entries and stale embedding cache entries.

```bash
palaia gc
```

Tier rotation rules:

- **HOT → WARM**: Entry older than 7 days AND decay score < 0.5
- **WARM → COLD**: Entry older than 30 days AND decay score < 0.1
- **COLD → WARM / HOT**: If accessed recently, score rises above thresholds

---

## `palaia export`

Export all `scope: public` entries.

```bash
palaia export [--remote <git-url>] [--branch <name>] [--output <dir>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--remote` | `None` | Git remote URL to push to |
| `--branch` | `palaia/export/<timestamp>` | Branch name (with `--remote`) |
| `--output` | `./palaia-export/` | Local output directory |

**Examples:**

```bash
# Local export
palaia export
palaia export --output /tmp/my-export

# Git export
palaia export --remote git@github.com:org/knowledge.git
palaia export --remote git@github.com:org/knowledge.git --branch palaia/shared
```

---

## `palaia import`

Import entries from an export directory or git URL.

```bash
palaia import <source> [--dry-run]
```

| Argument/Flag | Default | Description |
|--------------|---------|-------------|
| `source` | (required) | Path to export directory or git URL |
| `--dry-run` | `false` | Preview without writing |

Import rules:

- Only `scope: public` entries are accepted
- `scope: team` entries from foreign workspaces are **rejected** with an error
- Duplicate entries (same content hash) are skipped
- Entry IDs are regenerated on import

**Examples:**

```bash
palaia import ./palaia-export/
palaia import ./palaia-export/ --dry-run
palaia import https://github.com/org/knowledge.git
```
