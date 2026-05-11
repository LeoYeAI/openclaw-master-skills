# Migration Guide

How to move your agent's memory into Palaia — from flat files, other memory systems, or a fresh start.

## 5-Step Migration

### 1. Inventory

Figure out what you have. Common sources:

- `memory/*.md` files (OpenClaw smart-memory)
- JSON-based memory stores
- Flat markdown notes in workspace directories
- Conversation logs with embedded knowledge

```bash
# Check what palaia doctor finds
palaia doctor --fix

# Count your existing files
find ~/. openclaw/workspace/memory -name "*.md" | wc -l
```

### 2. Ingest

Bulk-import your existing files. Palaia chunks them automatically for search.

```bash
# Single file
palaia ingest ~/docs/architecture.md --project myapp --scope team

# Entire directory (recursive)
palaia ingest ~/. openclaw/workspace/memory/ --project legacy-notes --scope private

# With custom chunking for large docs
palaia ingest ~/docs/api-spec.md --project myapp --chunk-size 300 --chunk-overlap 30

# Preview first (dry run)
palaia ingest ~/docs/ --project myapp --dry-run
```

**Tip:** `--project` auto-creates the project if it doesn't exist. No need to run `palaia project create` first.

### 3. Verify

Check that your data made it in:

```bash
# See what's stored
palaia list --project myapp
palaia list --project legacy-notes

# Test search
palaia query "database connection" --project myapp

# Check overall health
palaia status
```

### 4. Cleanup

Once verified, remove or archive the old files:

```bash
# Archive (recommended — keep a backup)
tar czf ~/memory-backup-$(date +%Y%m%d).tar.gz ~/. openclaw/workspace/memory/

# Or just move them aside
mv ~/. openclaw/workspace/memory ~/. openclaw/workspace/memory-archived

# Run doctor to confirm clean state
palaia doctor
```

### 5. Integration

Point your agent to use Palaia for all memory operations:

```bash
# If using OpenClaw, the skill handles this automatically
# For custom setups, use the CLI or Python API:

# Write new memories
palaia write "Deploy uses port 8080 on staging" --project infra --tags deploy,staging

# Query in scripts
palaia query "staging port" --project infra --json

# Multi-agent? Set up shared access:
palaia setup --multi-agent ~/.openclaw/agents/
```

## Migrating from Smart-Memory

If you're coming from the OpenClaw smart-memory skill:

```bash
# 1. Palaia can auto-detect and import smart-memory format
palaia migrate ~/.openclaw/workspace/memory/ --format smart-memory --dry-run

# 2. If it looks good, run for real
palaia migrate ~/.openclaw/workspace/memory/ --format smart-memory

# 3. Verify
palaia status
palaia query "test search"

# 4. Run doctor to check for leftover legacy patterns
palaia doctor --fix
```

## Migrating from JSON Memory

```bash
# Generic JSON import
palaia migrate ./memory-export.json --format json-memory

# With scope override (make everything private)
palaia migrate ./data/ --format generic-md --scope private
```

## Tips

- **Start with `--dry-run`** on any bulk operation to preview what will happen.
- **Use projects** to keep imported data organized and separate from new entries.
- **Run `palaia doctor`** after migration to catch any leftover issues.
- **Don't delete originals immediately** — archive them first, verify Palaia search works, then clean up.
