---
name: credential-manager
description: MANDATORY security foundation for OpenClaw. Consolidate scattered API keys and credentials into a secure .env file with proper permissions. Includes GPG encryption for high-value secrets, credential rotation tracking, deep scanning, and backup hardening. Use when setting up OpenClaw, migrating credentials, auditing security, or enforcing the .env standard. This is not optional — centralized credential management is a core requirement for secure OpenClaw deployments.
---

# Credential Manager

**STATUS: MANDATORY SECURITY FOUNDATION**

Consolidate scattered API keys and credentials into a secure, centralized `.env` file.

## ⚠️ This Is Not Optional

Centralized `.env` credential management is a **core requirement** for OpenClaw security. If your credentials are scattered across multiple files, **stop and consolidate them now**.

**THE RULE:** All credentials MUST be in `~/.openclaw/.env` ONLY. No workspace, no skills, no scripts directories.

See:
- [CORE-PRINCIPLE.md](CORE-PRINCIPLE.md) - Why this is non-negotiable
- [CONSOLIDATION-RULE.md](CONSOLIDATION-RULE.md) - The single source principle

## The Foundation

**Every OpenClaw deployment MUST have:**
```
~/.openclaw/.env (mode 600)
```

This is your single source of truth for all credentials. No exceptions.

**Why?**
- Single location = easier to secure
- File mode 600 = only you can read
- Git-ignored = won't accidentally commit
- Validated format = catches errors
- Audit trail = know what changed

Scattered credentials = scattered attack surface. This skill fixes that.

## What This Skill Does

1. **Scans** for credentials in common locations (including deep scan for hardcoded secrets)
2. **Backs up** existing credential files (timestamped, mode 600)
3. **Consolidates** into `~/.openclaw/.env`
4. **Secures** with proper permissions (600 files, 700 directories)
5. **Validates** security, format, and entropy
6. **Encrypts** high-value secrets with GPG (wallet keys, private keys, mnemonics)
7. **Tracks** credential rotation schedules
8. **Enforces** best practices via fail-fast checks
9. **Cleans up** old files after migration

## Detection Parameters

The skill automatically detects credentials by scanning for:

**File Patterns:**
- `~/.config/*/credentials.json` — Service config directories
- `~/.config/*/*.credentials.json` — Nested credential files
- `~/.openclaw/*.json` — Credential files in OpenClaw root
- `~/.openclaw/*-credentials*` — Named credential files (e.g., farcaster-credentials.json)
- `~/.openclaw/workspace/memory/*-creds.json` — Memory credential files
- `~/.openclaw/workspace/memory/*credentials*.json` — Memory credential files
- `~/.openclaw/workspace/.env` — Workspace env files
- `~/.openclaw/workspace/*/.env` — Subdirectory env files
- `~/.openclaw/workspace/skills/*/.env` — Skill env files
- `~/.local/share/*/credentials.json` — Local share directories

**Sensitive Key Patterns:**
- API keys, access tokens, bearer tokens
- Secrets, passwords, passphrases
- OAuth consumer keys
- Private keys, signing keys, wallet keys
- Mnemonics and seed phrases

**Deep Scan (--deep flag):**
- Greps `.sh`, `.js`, `.py`, `.mjs`, `.ts` files for hardcoded secrets
- Detects high-entropy strings matching common key prefixes (`sk_`, `pk_`, `Bearer`, `0x` + 64 hex)
- Excludes `node_modules/`, `.git/`
- Reports file, line number, and key pattern matched

**Security Checks:**
- File permissions (must be `600` for files, `700` for directories)
- Backup permissions (must be `600` for backup files, `700` for backup dirs)
- Git-ignore protection
- Format validation (allows quoted values with spaces)
- Entropy analysis (flags suspiciously low-entropy secrets)
- Private key detection (flags `0x` + 64 hex char values)
- Mnemonic detection (flags 12/24 word values)
- Symlink detection (validates symlinked .env targets)

## Quick Start

### Full Migration (Recommended)

```bash
# Scan for credentials
./scripts/scan.py

# Deep scan (includes hardcoded secrets in scripts)
./scripts/scan.py --deep

# Review and consolidate
./scripts/consolidate.py

# Validate security
./scripts/validate.py

# Encrypt high-value secrets
./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,CUSTODY_PRIVATE_KEY

# Check rotation status
./scripts/rotation-check.py
```

### Individual Operations

```bash
# Scan only
./scripts/scan.py

# Consolidate specific service
./scripts/consolidate.py --service x

# Backup without removing
./scripts/consolidate.py --backup-only

# Clean up old files
./scripts/cleanup.py --confirm
```

## Common Credential Locations

The skill scans these locations:

```
~/.config/*/credentials.json
~/.openclaw/*.json
~/.openclaw/*-credentials*
~/.openclaw/workspace/memory/*-creds.json
~/.openclaw/workspace/memory/*credentials*.json
~/.openclaw/workspace/*/.env
~/.openclaw/workspace/skills/*/.env
~/.env (if exists, merges)
```

## Security Features

✅ **File permissions:** Sets `.env` to mode 600 (owner only)
✅ **Directory permissions:** Sets backup dirs to mode 700 (owner only)
✅ **Backup permissions:** Sets backup files to mode 600 (owner only)
✅ **Git protection:** Creates/updates `.gitignore`
✅ **Backups:** Timestamped backups before changes (secured)
✅ **Validation:** Checks format, permissions, entropy, and duplicates
✅ **Template:** Creates `.env.example` (safe to share)
✅ **GPG encryption:** Encrypts high-value secrets at rest
✅ **Rotation tracking:** Warns when credentials need rotation
✅ **Deep scan:** Detects hardcoded secrets in source files
✅ **Symlink-aware:** Validates symlinked .env targets

## Output Structure

After migration:

```
~/.openclaw/
├── .env                     # All credentials (secure, mode 600)
├── .env.secrets.gpg         # GPG-encrypted high-value keys (mode 600)
├── .env.meta                # Rotation metadata (mode 600)
├── .env.example             # Template (safe to share)
├── .gitignore               # Protects .env and .env.secrets.gpg
└── backups/                 # (mode 700)
    └── credentials-old-YYYYMMDD/  # (mode 700)
        └── *.bak            # Backup files (mode 600)
```

## GPG Encryption for High-Value Secrets

Private keys, wallet keys, and mnemonics should **never** exist as plaintext on disk. Use GPG encryption for these.

### Setup GPG

```bash
# First-time setup (generates OpenClaw GPG key, configures agent cache)
./scripts/setup-gpg.sh
```

### Encrypt High-Value Keys

```bash
# Encrypt specific keys (moves them from .env to .env.secrets.gpg)
./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,CUSTODY_PRIVATE_KEY,SIGNER_PRIVATE_KEY

# The .env will contain placeholders:
# MAIN_WALLET_PRIVATE_KEY=GPG:MAIN_WALLET_PRIVATE_KEY
```

### How Scripts Access Encrypted Keys

The `enforce.py` module handles this transparently:

```python
from enforce import get_credential

# Works for both plaintext and GPG-encrypted keys
key = get_credential('MAIN_WALLET_PRIVATE_KEY')
# If value starts with "GPG:", decrypts from .env.secrets.gpg automatically
```

### GPG Agent Caching

On headless servers (VPS), the GPG agent caches the passphrase:
- Default cache TTL: 8 hours
- Configurable via `setup-gpg.sh`
- Passphrase required once after reboot, then cached

### What to Encrypt

| Key Type | Encrypt? | Why |
|----------|----------|-----|
| Wallet private keys | ✅ Yes | Controls funds |
| Custody/signer private keys | ✅ Yes | Controls identity |
| Mnemonics / seed phrases | ✅ Yes | Master recovery |
| API keys (services) | ❌ No | Revocable, low damage |
| Agent IDs, names, URLs | ❌ No | Not secrets |

## Credential Rotation Tracking

### Setup Rotation Metadata

```bash
# Initialize rotation tracking for all keys
./scripts/rotation-check.py --init
```

Creates `~/.openclaw/.env.meta`:
```json
{
  "MAIN_WALLET_PRIVATE_KEY": {
    "created": "2026-01-15",
    "lastRotated": null,
    "rotationDays": 90,
    "risk": "critical"
  },
  "MOLTBOOK_API_KEY": {
    "created": "2026-02-04",
    "lastRotated": null,
    "rotationDays": 180,
    "risk": "low"
  }
}
```

### Check Rotation Status

```bash
# Check which keys need rotation
./scripts/rotation-check.py

# Output:
# 🔴 MAIN_WALLET_PRIVATE_KEY: 26 days old (critical, rotate every 90 days)
# ✅ MOLTBOOK_API_KEY: 7 days old (low, rotate every 180 days)
```

### Rotation Schedules

| Risk Level | Rotation Period | Examples |
|------------|----------------|----------|
| Critical | 90 days | Wallet keys, private keys |
| Standard | 180 days | API keys for paid services |
| Low | 365 days | Free-tier API keys, agent IDs |

### Add to Heartbeat (Optional)

Add rotation checks to `HEARTBEAT.md` for periodic monitoring:
```markdown
## Credential Rotation (weekly)
If 7+ days since last rotation check:
1. Run: ./scripts/rotation-check.py
2. If any keys overdue: notify human
3. Update lastRotationCheck timestamp
```

## Supported Services

Common services auto-detected:

- **X (Twitter):** OAuth 1.0a credentials
- **Farcaster:** Custody keys, signer keys, FID credentials
- **Molten:** Agent intent matching
- **Moltbook:** Agent social network
- **Botchan/4claw:** Net Protocol
- **OpenAI, Anthropic, Google:** AI providers
- **GitHub, GitLab:** Code hosting
- **Coinbase/CDP:** Crypto wallet credentials
- **Generic:** `API_KEY`, `*_TOKEN`, `*_SECRET` patterns

See [references/supported-services.md](references/supported-services.md) for full list.

## Scripts

All scripts support `--help` for detailed usage.

### scan.py
```bash
# Scan and report
./scripts/scan.py

# Deep scan (includes hardcoded secrets in scripts)
./scripts/scan.py --deep

# Include custom paths
./scripts/scan.py --paths ~/.myapp/config ~/.local/share/creds

# JSON output
./scripts/scan.py --format json
```

### consolidate.py
```bash
# Interactive mode (prompts before changes)
./scripts/consolidate.py

# Auto-confirm (no prompts)
./scripts/consolidate.py --yes

# Backup only
./scripts/consolidate.py --backup-only

# Specific service
./scripts/consolidate.py --service molten
```

### validate.py
```bash
# Full validation (permissions, format, entropy, security)
./scripts/validate.py

# Check permissions only
./scripts/validate.py --check permissions

# Fix issues automatically
./scripts/validate.py --fix
```

### encrypt.py
```bash
# Encrypt specific high-value keys
./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,CUSTODY_PRIVATE_KEY

# List currently encrypted keys
./scripts/encrypt.py --list

# Decrypt (move back to plaintext .env)
./scripts/encrypt.py --decrypt --keys MAIN_WALLET_PRIVATE_KEY
```

### rotation-check.py
```bash
# Check rotation status
./scripts/rotation-check.py

# Initialize tracking for all keys
./scripts/rotation-check.py --init

# Record a rotation
./scripts/rotation-check.py --rotated MOLTBOOK_API_KEY
```

### setup-gpg.sh
```bash
# First-time GPG setup for OpenClaw
./scripts/setup-gpg.sh

# Configure cache timeout (hours)
./scripts/setup-gpg.sh --cache-hours 12
```

### cleanup.py
```bash
# Dry run (shows what would be deleted)
./scripts/cleanup.py

# Actually delete old files
./scripts/cleanup.py --confirm

# Keep backups
./scripts/cleanup.py --confirm --keep-backups
```

## Migration Workflow

This is the exact step-by-step flow, tested and verified on a live OpenClaw deployment.

### Step 1: Scan for Scattered Credentials

```bash
cd /path/to/openclaw/skills/credential-manager

# Basic scan — finds credential files by path patterns
./scripts/scan.py

# Deep scan — also greps source files for hardcoded secrets
./scripts/scan.py --deep
```

**What to look for in output:**
- ⚠️ files with mode != 600 (insecure permissions)
- Symlinked `.env` files (should point to main `~/.openclaw/.env`)
- JSON credential files outside `~/.openclaw/.env`
- Deep scan hits on hardcoded keys in scripts

**Example output:**
```
⚠️ /home/user/.openclaw/farcaster-credentials.json
   Type: json
   Keys: custodyPrivateKey, signerPrivateKey, ...
   Mode: 644
   ⚠️  Should be 600 for security

✅ /home/user/.openclaw/.env
   Type: env
   Keys: API_KEY, X_CONSUMER_KEY, ...
   Mode: 600
```

### Step 2: Consolidate into .env

```bash
./scripts/consolidate.py
```

**Interactive flow:**
1. Script scans and lists all credential files found
2. Backs up existing `.env` to `~/.openclaw/backups/credentials-old-YYYYMMDD/`
3. Loads existing `.env` keys
4. Processes each credential file:
   - Auto-detects service (x, farcaster, moltbook, molten, etc.)
   - Normalizes key names (e.g., `custodyPrivateKey` → `FARCASTER_CUSTODY_PRIVATE_KEY`)
   - Shows mapping: `key → ENV_KEY`
5. Asks for confirmation: `Proceed? [y/N]`
6. Writes merged `.env` (mode 600)
7. Creates `.env.example` template (safe to share)
8. Updates `.gitignore`

**For credentials not auto-detected** (e.g., nested JSON like `farcaster-credentials.json` with multiple accounts), manually add to `.env`:
```bash
cat >> ~/.openclaw/.env << 'EOF'

# FARCASTER (Active: mr-teeclaw, FID 2700953)
FARCASTER_FID=2700953
FARCASTER_FNAME=mr-teeclaw
FARCASTER_CUSTODY_ADDRESS=0x...
FARCASTER_CUSTODY_PRIVATE_KEY=0x...
FARCASTER_SIGNER_PUBLIC_KEY=...
FARCASTER_SIGNER_PRIVATE_KEY=...

# FARCASTER LEGACY (teeclaw, FID 2684290)
FARCASTER_LEGACY_FID=2684290
FARCASTER_LEGACY_CUSTODY_ADDRESS=0x...
FARCASTER_LEGACY_CUSTODY_PRIVATE_KEY=0x...
FARCASTER_LEGACY_SIGNER_PUBLIC_KEY=...
FARCASTER_LEGACY_SIGNER_PRIVATE_KEY=...
EOF

chmod 600 ~/.openclaw/.env
```

### Step 3: Validate

```bash
./scripts/validate.py
```

**Checks performed:**
- ✅ `.env` permissions (must be 600)
- ✅ `.gitignore` coverage
- ✅ Format validation (key format, quoting, duplicates)
- ✅ Security analysis:
  - Detects plaintext private keys (`0x` + 64 hex chars) → recommends GPG
  - Detects mnemonic/seed phrases (12/24 word values) → recommends GPG
  - Entropy analysis on SECRET/PRIVATE_KEY/PASSWORD fields
  - Flags weak/placeholder values
- ✅ Backup permissions (files must be 600, directories 700)

**Fix issues automatically:**
```bash
./scripts/validate.py --fix
```
This fixes: file permissions, directory permissions, backup permissions, gitignore.
It does NOT auto-fix format issues or encrypt keys — those require manual action.

### Step 4: Setup GPG and Encrypt Private Keys

```bash
# First-time GPG setup (configures agent cache, tests encrypt/decrypt)
./scripts/setup-gpg.sh
# Optional: --cache-hours 12 (default: 8)
```

**Encrypt high-value keys:**
```bash
# Encrypt wallet + Farcaster private keys
./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,FARCASTER_CUSTODY_PRIVATE_KEY,FARCASTER_SIGNER_PRIVATE_KEY,FARCASTER_LEGACY_CUSTODY_PRIVATE_KEY,FARCASTER_LEGACY_SIGNER_PRIVATE_KEY
```

**What happens:**
1. Prompts for a GPG passphrase (or reads `OPENCLAW_GPG_PASSPHRASE` env var)
2. Extracts specified key values from `.env`
3. Stores them encrypted in `~/.openclaw/.env.secrets.gpg` (AES256, mode 600)
4. Replaces `.env` values with `GPG:KEY_NAME` placeholders
5. Scripts using `get_credential()` or `_load_cred()` decrypt transparently

**Save passphrase to .env for automated decryption:**
```bash
echo 'OPENCLAW_GPG_PASSPHRASE=your-passphrase-here' >> ~/.openclaw/.env
chmod 600 ~/.openclaw/.env
```

**Verify encryption:**
```bash
# Check .env has GPG placeholders
grep "GPG:" ~/.openclaw/.env

# List all encrypted keys
./scripts/encrypt.py --list
```

### Step 5: Initialize Rotation Tracking

```bash
./scripts/rotation-check.py --init
```

**Auto-classifies all keys by risk:**
- **Critical** (90-day rotation): `*PRIVATE_KEY`, `*MNEMONIC`, `*SEED`, `*WALLET_KEY`, `*CUSTODY*`, `*SIGNER*`
- **Standard** (180-day rotation): `*API_KEY`, `*SECRET`, `*TOKEN`, `*BEARER`, `*CONSUMER*`, `*ACCESS*`
- **Low** (365-day rotation): Everything else

Creates `~/.openclaw/.env.meta` (mode 600) with creation dates and rotation schedules.

**Check rotation status anytime:**
```bash
./scripts/rotation-check.py
```

### Step 6: Cleanup Old Credential Files

```bash
# Dry run first — see what would be deleted
./scripts/cleanup.py

# Actually delete (prompts for 'DELETE' confirmation)
./scripts/cleanup.py --confirm
```

**Also manually remove migrated files not caught by the scanner:**
```bash
# Example: farcaster-credentials.json was manually migrated
cp ~/.openclaw/farcaster-credentials.json ~/.openclaw/backups/credentials-old-YYYYMMDD/farcaster-credentials.json.bak
chmod 600 ~/.openclaw/backups/credentials-old-YYYYMMDD/farcaster-credentials.json.bak
rm ~/.openclaw/farcaster-credentials.json
```

### Step 7: Update Scripts That Referenced Old Files

Any scripts that loaded from JSON credential files or hardcoded paths need updating.

**Pattern — Bash scripts:**
```bash
# OLD (insecure):
FARCASTER_CREDS="/home/user/.openclaw/farcaster-credentials.json"
fid=$(jq -r '.fid' "$FARCASTER_CREDS")
private_key=$(jq -r '.custodyPrivateKey' "$FARCASTER_CREDS")

# NEW (secure, GPG-aware):
ENV_FILE="$HOME/.openclaw/.env"

_load_cred() {
  local key="$1"
  local value
  value=$(grep "^${key}=" "$ENV_FILE" | head -1 | cut -d= -f2-)
  if [[ "$value" == GPG:* ]]; then
    local gpg_key="${value#GPG:}"
    local passphrase="${OPENCLAW_GPG_PASSPHRASE:-}"
    if [ -n "$passphrase" ]; then
      value=$(echo "$passphrase" | gpg -d --batch --quiet --passphrase-fd 0 "$HOME/.openclaw/.env.secrets.gpg" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$gpg_key',''))")
    else
      value=$(gpg -d --batch --quiet "$HOME/.openclaw/.env.secrets.gpg" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$gpg_key',''))")
    fi
  fi
  echo "$value"
}

fid=$(_load_cred "FARCASTER_FID")
private_key=$(_load_cred "FARCASTER_CUSTODY_PRIVATE_KEY")
```

**Pattern — Node.js scripts:**
```javascript
// OLD (insecure):
const creds = JSON.parse(fs.readFileSync('~/.openclaw/farcaster-credentials.json'));
const privateKey = creds.custodyPrivateKey;

// NEW (secure, GPG-aware):
const ENV_PATH = path.join(os.homedir(), '.openclaw/.env');
const SECRETS_PATH = path.join(os.homedir(), '.openclaw/.env.secrets.gpg');

function loadCred(key) {
  const content = fs.readFileSync(ENV_PATH, 'utf8');
  for (const line of content.split('\n')) {
    if (line.startsWith(key + '=')) {
      let value = line.slice(key.length + 1).trim();
      if (value.startsWith('GPG:')) {
        const { execSync } = require('child_process');
        const passphrase = process.env.OPENCLAW_GPG_PASSPHRASE || '';
        const cmd = passphrase
          ? `echo "${passphrase}" | gpg -d --batch --quiet --passphrase-fd 0 "${SECRETS_PATH}"`
          : `gpg -d --batch --quiet "${SECRETS_PATH}"`;
        const secrets = JSON.parse(execSync(cmd, { encoding: 'utf8' }));
        return secrets[value.slice(4)] || '';
      }
      return value;
    }
  }
  return '';
}

const privateKey = loadCred('FARCASTER_CUSTODY_PRIVATE_KEY');
```

**Pattern — Python scripts:**
```python
# Use the enforce module (recommended):
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'openclaw/skills/credential-manager/scripts'))
from enforce import get_credential

private_key = get_credential('FARCASTER_CUSTODY_PRIVATE_KEY')  # Auto-decrypts GPG
```

### Step 8: Final Validation

```bash
# Run full validation — should show all green
./scripts/validate.py

# Verify encrypted keys
./scripts/encrypt.py --list

# Check rotation status
./scripts/rotation-check.py

# Test a script that uses credentials
bash /path/to/your/script.sh
```

**Expected final state:**
```
~/.openclaw/
├── .env                     # All credentials (mode 600, private keys = GPG:*)
├── .env.secrets.gpg         # GPG-encrypted private keys (mode 600)
├── .env.meta                # Rotation tracking metadata (mode 600)
├── .env.example             # Template (safe to share)
├── .gitignore               # Protects .env, .env.secrets.gpg, .env.meta
└── backups/                 # (mode 700)
    └── credentials-old-YYYYMMDD/  # (mode 700)
        └── *.bak            # Backup files (mode 600)
```

## For Skill Developers: Enforce This Standard

Other OpenClaw skills MUST validate credentials are secure before using them:

### Python Skills
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add credential-manager scripts to path
sys.path.insert(0, str(Path.home() / '.openclaw/skills/credential-manager/scripts'))

# Enforce secure .env (exits if not compliant)
from enforce import require_secure_env, get_credential

require_secure_env()

# Now safe to load credentials (handles GPG-encrypted keys transparently)
api_key = get_credential('SERVICE_API_KEY')
wallet_key = get_credential('MAIN_WALLET_PRIVATE_KEY')  # Auto-decrypts from GPG
```

### Bash Skills
```bash
#!/usr/bin/env bash
set -euo pipefail

# Validate .env exists and is secure
if ! python3 ~/.openclaw/skills/credential-manager/scripts/enforce.py; then
    exit 1
fi

# Now safe to load
source ~/.openclaw/.env
```

**This creates a fail-fast system:** If credentials aren't properly secured, skills refuse to run. Users are forced to fix it.

## Loading Credentials

After migration, load from `.env`:

### Python
```python
import os
from pathlib import Path

# Load .env
env_file = Path.home() / '.openclaw' / '.env'
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val

# Use credentials
api_key = os.getenv('SERVICE_API_KEY')
```

### Bash
```bash
# Load .env
set -a
source ~/.openclaw/.env
set +a

# Use credentials
echo "$SERVICE_API_KEY"
```

### Using Existing Loaders
If you migrated using OpenClaw scripts:
```python
from load_credentials import get_credentials
creds = get_credentials('x')
```

## Adding New Credentials

Edit `~/.openclaw/.env`:
```bash
# Add new service
NEW_SERVICE_API_KEY=your_key_here
NEW_SERVICE_SECRET=your_secret_here
```

Update template too:
```bash
# Edit .env.example
NEW_SERVICE_API_KEY=your_key_here
NEW_SERVICE_SECRET=your_secret_here
```

If the new credential is high-value (private key, wallet key):
```bash
# Add to .env first, then encrypt
./scripts/encrypt.py --keys NEW_SERVICE_PRIVATE_KEY
```

## Security Best Practices

See [references/security.md](references/security.md) for detailed security guidelines.

**Quick checklist:**
- ✅ `.env` has 600 permissions
- ✅ `.env` is git-ignored
- ✅ Backup files have 600 permissions
- ✅ Backup directories have 700 permissions
- ✅ No credentials in code or logs (use `--deep` scan to verify)
- ✅ Private keys encrypted with GPG
- ✅ Rotation schedule established and tracked
- ✅ Symlinked .env files point to the main .env only
- ✅ No credentials in shell history (use `source`, not `export KEY=val`)

## Rollback

If something goes wrong:

```bash
# Find your backup
ls -la ~/.openclaw/backups/

# Restore specific file
cp ~/.openclaw/backups/credentials-old-YYYYMMDD/x-credentials.json.bak \
   ~/.config/x/credentials.json

# Decrypt GPG secrets back to plaintext
./scripts/encrypt.py --decrypt --keys MAIN_WALLET_PRIVATE_KEY
```

## Notes

- **Non-destructive by default:** Original files backed up before removal
- **Idempotent:** Safe to run multiple times
- **Extensible:** Add custom credential patterns in scripts
- **Secure:** Never logs full credentials, only metadata
- **GPG-aware:** Transparently handles encrypted and plaintext credentials
- **Backup-hardened:** All backups secured with proper permissions
- **Symlink-aware:** Detects and validates symlinked credential files
