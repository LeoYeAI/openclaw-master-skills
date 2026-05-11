# Changelog

## Version 2.0.0 (2026-02-11)

### 🔐 GPG Encryption, Deep Scanning, Rotation Tracking & Backup Hardening

**Major security upgrade.** Private keys and wallet secrets are now GPG-encrypted at rest. Scanner catches hardcoded secrets in source files. All backup permissions hardened. Credential rotation is tracked with risk-based schedules.

### Added

**New scripts:**

- **`encrypt.py`** — GPG encrypt/decrypt high-value secrets
  - Moves private keys from plaintext `.env` to `~/.openclaw/.env.secrets.gpg` (AES256)
  - Replaces values in `.env` with `GPG:KEY_NAME` placeholders
  - `--list` shows currently encrypted keys
  - `--decrypt --keys KEY` reverses encryption
  - Supports passphrase via `OPENCLAW_GPG_PASSPHRASE` env var or interactive prompt

- **`setup-gpg.sh`** — First-time GPG configuration
  - Checks GPG installation
  - Configures gpg-agent cache (default 8h, `--cache-hours N`)
  - Enables loopback pinentry for headless servers
  - Runs encrypt/decrypt test cycle

- **`rotation-check.py`** — Credential rotation tracking
  - `--init` creates `~/.openclaw/.env.meta` with auto-classified risk levels
  - Critical keys (private keys, mnemonics): 90-day rotation
  - Standard keys (API keys, tokens): 180-day rotation
  - Low-risk keys: 365-day rotation
  - `--rotated KEY` records a rotation event
  - Shows overdue/upcoming/OK status with color-coded output

**New scan capabilities:**

- **Deep scan** (`--deep` flag): Greps `.sh`, `.js`, `.py`, `.mjs`, `.ts` files for:
  - API key prefixes (`sk_`, `pk_`, `Bearer`)
  - Possible private keys (`0x` + 64 hex chars)
  - Hardcoded credential assignments
  - Mnemonic/seed phrases
  - Excludes `node_modules/`, `.git/`

- **Expanded scan patterns:**
  - `~/.openclaw/*.json` (catches `farcaster-credentials.json` etc.)
  - `~/.openclaw/*-credentials*`
  - `~/.openclaw/workspace/*/.env`
  - `~/.openclaw/workspace/*/repo/.env`

- **Symlink detection:** Reports symlinked `.env` files and validates they point to the main `.env`

**New validation checks:**

- **Entropy analysis:** Flags low-entropy values for SECRET/PRIVATE_KEY/PASSWORD fields
- **Private key detection:** Flags `0x` + 64 hex char values (recommends GPG encryption)
- **Mnemonic detection:** Flags 12/24 space-separated word values
- **Backup permission audit:** Checks all backup files (mode 600) and directories (mode 700)
- **`--fix` now works:** Actually fixes permissions, backup permissions, directory permissions, gitignore

**GPG-aware credential loading:**

- `enforce.py` `get_credential()` transparently decrypts `GPG:` prefixed values
- `is_gpg_available()` helper for checking GPG status
- Reports GPG encryption status when run directly

### Changed

- **`consolidate.py`:**
  - Backup files now created with mode 600 (was inheriting source permissions)
  - Backup directories created with mode 700 (was 755)
  - Parent backup directory also secured to 700
  - Added Farcaster to `SERVICE_MAPPINGS` (custodyPrivateKey, signerPrivateKey, etc.)
  - `.gitignore` now also covers `.env.secrets.gpg` and `.env.meta`
  - Skips symlinks that point to the main `.env`
  - Flattens nested JSON objects to compact JSON strings

- **`validate.py`:**
  - Fixed quote contradiction: now allows double-quoted values with spaces
  - Removed false "Quotes not needed" check
  - Added backup security checks as a new validation category
  - `--fix` flag now properly fixes backup permissions
  - `check_security()` upgraded from naive pattern matching to entropy + pattern analysis

- **`scan.py`:**
  - Added 4 new credential path patterns
  - Symlink detection with target validation
  - `--deep` flag for source file scanning
  - Shannon entropy calculation utility

- **`enforce.py`:**
  - `get_credential()` now handles `GPG:` prefixed values
  - Decrypts from `.env.secrets.gpg` using gpg-agent cache or passphrase
  - Reports GPG encryption status

- **`SKILL.md`:**
  - Complete rewrite of Migration Workflow with exact step-by-step flow
  - Added GPG Encryption section with setup, usage, and what-to-encrypt guide
  - Added Credential Rotation Tracking section
  - Added Deep Scan documentation
  - Added Bash/Node.js/Python patterns for GPG-aware credential loading
  - Updated security checklist
  - Added Farcaster to supported services

### Security Fixes

- 🔴 **Backup files** were created with mode 644 (world-readable) — now mode 600
- 🔴 **Backup directories** were created with mode 755 — now mode 700
- 🔴 **Scanner blind spot:** `~/.openclaw/*.json` was not scanned — now included
- 🔴 **farcaster-credentials.json** with private keys had mode 644 — detected and flagged
- 🟡 **validate.py** contradicted itself on quotes — fixed
- 🟡 **check_security()** only checked for "password123" — now does entropy + pattern analysis

### Migration Story

This update was built during a live security audit that discovered:
1. `farcaster-credentials.json` with private keys at mode 644 (world-readable!)
2. All backup files at mode 644 (should be 600)
3. All backup directories at mode 755 (should be 700)
4. Wallet private key sitting in plaintext `.env`
5. Scanner couldn't detect `~/.openclaw/*.json` files
6. `validate.py` had conflicting quote validation rules

After running the upgraded skill:
- ✅ 5 private keys GPG-encrypted (wallet + 4 Farcaster keys)
- ✅ All backup permissions fixed (12 files/dirs)
- ✅ `farcaster-credentials.json` migrated to `.env` and deleted
- ✅ 57 keys tracked with risk-based rotation schedules
- ✅ 4 scripts updated to use `.env` with GPG decryption
- ✅ All validation checks pass

### Technical Details

**New files:** 3 scripts (`encrypt.py`, `setup-gpg.sh`, `rotation-check.py`)
**Modified files:** 5 (`scan.py`, `consolidate.py`, `validate.py`, `enforce.py`, `SKILL.md`)
**New file types:** `.env.secrets.gpg` (encrypted), `.env.meta` (rotation metadata)
**Package size:** ~65 KB

---

## Version 1.3.0 (2026-02-07)

### 🎯 Consolidation Rule - Single Source Enforcement

**Major update:** Formal enforcement of the single source principle — all credentials MUST be in `~/.openclaw/.env` ONLY.

### Added

**CONSOLIDATION-RULE.md** - New comprehensive documentation:
- The single source principle explained
- Why root-only (no workspace, skills, scripts .env files)
- Enforcement workflow (scan → consolidate → cleanup → validate)
- Security rationale (one file to secure, audit, backup)
- Developer guidance (how to load from root .env)
- Exception handling (node_modules .env files are harmless)

**Enhanced scan.py detection patterns:**
- `~/.openclaw/workspace/.env`
- `~/.openclaw/workspace/.env.*`
- `~/.openclaw/workspace/skills/*/.env`
- `~/.openclaw/workspace/skills/*/repo/.env`
- `~/.openclaw/workspace/scripts/.env`

**Enhanced cleanup.py:**
- Updated header to explicitly mention rule enforcement
- Removes scattered .env files from workspace/skills/scripts
- Preserves backups for safety

**Updated SKILL.md:**
- Prominently references CONSOLIDATION-RULE.md
- Added "THE RULE" section upfront
- Emphasizes root-only requirement

### Technical Details

**New files:** 1 (CONSOLIDATION-RULE.md)
**Modified files:** 4 (scan.py, cleanup.py, SKILL.md, README.md)
**Detection patterns:** +5 workspace-specific patterns

---

## Version 1.2.0 (2026-02-06)

### 🔐 Crypto-Specific Credential Detection

**Enhanced detection patterns** for blockchain and cryptocurrency credentials.

### Added

- `private_key` / `private-key` - Wallet private keys
- `passphrase` - Seed passphrases
- `mnemonic` - BIP39 recovery phrases
- `seed_phrase` / `seed-phrase` - Wallet seed phrases
- `signing_key` / `signing-key` - Transaction signing keys
- `wallet_key` / `wallet-key` - Wallet access keys

---

## Version 1.1.0 (2026-02-05)

### 🔒 SECURITY FOUNDATION UPDATE

- Added `CORE-PRINCIPLE.md` establishing mandatory security standard
- Added `enforce.py` with `require_secure_env()` and `get_credential()`
- Repositioned as mandatory core infrastructure

---

## Version 1.0.0 (2026-02-05)

Initial release with core functionality:
- Credential scanning
- .env consolidation
- Security validation
- Old file cleanup
- Comprehensive documentation
