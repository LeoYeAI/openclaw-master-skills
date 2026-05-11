# Credential Consolidation Rule

**RULE: All credentials MUST be consolidated to `/home/phan_harry/.openclaw/.env`**

## The Single Source Principle

There is exactly **ONE** location for all OpenClaw credentials:

```
~/.openclaw/.env
```

**No exceptions.** Not workspace, not skills, not scripts. Root only.

## Why Root Only?

1. **Security:** One file to secure (mode 600), one file to audit
2. **Simplicity:** Scripts know exactly where to look
3. **Git safety:** Single .gitignore rule protects everything
4. **Backup:** One file to backup/restore
5. **Portability:** Copy one file, move entire credential set

## What Gets Consolidated

**ALL of these must be merged into root .env:**

- `~/.openclaw/workspace/.env` ❌ → Root
- `~/.openclaw/workspace/skills/*/.env` ❌ → Root
- `~/.openclaw/workspace/skills/*/repo/.env` ❌ → Root
- `~/.openclaw/workspace/scripts/.env` ❌ → Root
- `~/.config/*/credentials.json` ❌ → Root
- Any scattered API key files ❌ → Root

## Enforcement

The credential-manager skill enforces this rule:

1. **Scan:** Detects ALL .env files and credential files
2. **Consolidate:** Merges everything into `~/.openclaw/.env`
3. **Cleanup:** Removes scattered files (after backup)
4. **Validate:** Ensures no scattered files remain

## Running Consolidation

```bash
cd ~/openclaw/skills/credential-manager

# Scan for scattered credentials
./scripts/scan.py

# Consolidate to root (with backup)
./scripts/consolidate.py --yes

# Clean up scattered files
./scripts/cleanup.py --confirm

# Validate security
./scripts/validate.py
```

## After Consolidation

✅ **Only these files should exist:**

- `~/.openclaw/.env` (mode 600) - Your credentials
- `~/.openclaw/.env.example` - Template (safe to share)
- `~/.openclaw/backups/credentials-old-YYYYMMDD/` - Backups

❌ **These should NOT exist:**

- `~/.openclaw/workspace/.env`
- `~/.openclaw/workspace/skills/*/.env`
- Any other .env files outside node_modules

## For Skill Developers

**DO NOT create .env files in your skill directories.**

Load credentials from root:

```bash
#!/bin/bash
# Load from root .env
source ~/.openclaw/.env

# Use credentials
echo "$SERVICE_API_KEY"
```

```python
#!/usr/bin/env python3
# Load from root .env
from pathlib import Path
env_file = Path.home() / '.openclaw' / '.env'
# ... load and use
```

## Exception: node_modules

.env files inside `node_modules/` are package defaults (e.g., bottleneck's Redis config). These are harmless and ignored by the scanner.

## Rationale

Scattered credentials create scattered attack surface. A single .env file:
- Is easier to secure (one chmod 600)
- Is easier to audit (one file to check)
- Is easier to backup (one file to save)
- Is easier to gitignore (one rule)
- Is easier to rotate (change in one place)

**Consolidation is not optional. It's a core security requirement.**
