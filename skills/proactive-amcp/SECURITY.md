# Security & Data Flow Documentation

This document describes what proactive-amcp collects, where it sends data, what it persists on disk, and how to audit or uninstall it.

---

## Data Collected

Checkpoints bundle the following files from your workspace and AMCP configuration:

| File / Path | Description | Included In |
|-------------|-------------|-------------|
| `SOUL.md` | Agent identity and principles | Quick + Full checkpoint |
| `MEMORY.md` | Accumulated agent knowledge | Quick + Full checkpoint |
| `USER.md` | User preferences and context | Quick + Full checkpoint |
| `TOOLS.md` | Tool configurations | Quick + Full checkpoint |
| `AGENTS.md` | Agent behavior definitions | Quick + Full checkpoint |
| `memory/*.md` | Daily notes, context files | Quick + Full checkpoint |
| `memory/ontology/graph.jsonl` | Typed knowledge graph | Quick + Full checkpoint |
| `memory/learning/*.jsonl` | Problems and learnings | Quick + Full checkpoint |
| `memory/venvs-manifest.json` | Virtual environment manifest | Full checkpoint |
| `~/.amcp/identity.json` | Ed25519 signing keypair | Full checkpoint |
| `~/.amcp/config.json` | Settings (secrets extracted separately) | Full checkpoint (secrets encrypted) |
| OpenClaw config metadata | Gateway config (sanitized — API keys stripped) | Full checkpoint |

### Secrets Handling

`full-checkpoint.sh` extracts secrets from config files before bundling. Secrets are encrypted separately using X25519 + ChaCha20-Poly1305 AEAD via the AMCP CLI. The checkpoint itself is then signed with your Ed25519 identity.

Secret patterns scanned (11 regex patterns in `scan-secrets.sh`): GitHub PAT, OpenAI key, Solvr API key, AgentMail key, AWS keys, JWTs, Telegram tokens, Pinata JWT, and more.

---

## Data NOT Collected (Quick Mode)

Quick checkpoints (default) include ONLY workspace files:

| Excluded from Quick Mode | Reason |
|--------------------------|--------|
| `~/.openclaw/openclaw.json` API keys | Quick mode = workspace only |
| `~/.amcp/config.json` secrets | Quick mode = workspace only |
| Auth profiles, OAuth tokens | Quick mode = workspace only |
| AgentMemory vault contents | Not part of AMCP workspace |
| System files outside workspace | Only `~/.openclaw/workspace/` scoped |
| SSH keys, GPG keys | Not in scan scope |
| Other users' home directories | Scripts only operate on `$HOME` |
| `.git/` directories | Excluded from rsync |
| Node modules, `.venv/` | Excluded from rsync |

## Data INCLUDED in Full Checkpoints (--full)

⚠️ **FULL checkpoints include ALL secrets for complete resurrection:**

| Included in Full Mode | Purpose |
|-----------------------|---------|
| `~/.openclaw/openclaw.json` skill API keys | Restore other skills' credentials |
| `~/.amcp/config.json` (Pinata, Solvr keys) | Restore AMCP configuration |
| `~/.openclaw/auth-profiles.json` OAuth tokens | Restore authentication |
| All secrets from AgentMemory CLI | Complete credential restoration |

**Use `--full` only when you need complete resurrection capability and understand secrets will be bundled (encrypted).**

---

## Network Endpoints

All network calls are made via `curl`. No persistent connections or background daemons phone home.

| Endpoint | Purpose | When Called |
|----------|---------|------------|
| `https://api.solvr.dev/v1` | Agent registration, knowledge search/post, IPFS pinning, Groq key distribution, checkpoint metadata, heartbeat | Registration, checkpoint, resurrection, learning capture |
| `https://api.pinata.cloud` | Direct IPFS pinning (alternative to Solvr) | Checkpoint (when `pinning.provider` is `pinata` or `both`) |
| `https://ipfs.solvr.dev/ipfs/<CID>` | IPFS gateway — fetch checkpoints | Resurrection |
| `https://ipfs.io/ipfs/<CID>` | IPFS gateway — fallback fetch | Resurrection (if Solvr gateway fails) |
| `https://cloudflare-ipfs.com/ipfs/<CID>` | IPFS gateway — second fallback | Resurrection (if previous gateways fail) |
| `https://api.groq.com/openai/v1` | Memory pruning, error condensing, smart checkpoint filtering | Optional — only if Groq API key configured |
| `https://api.telegram.org` | Death/recovery notifications | Optional — only if `notify.target` configured |
| AgentMail API | Email notifications on resurrection | Optional — only if `notify.emailOnResurrect` enabled |

**No data is sent unless you configure the corresponding API key.** Without keys, scripts degrade gracefully (no network calls made).

---

## Persistent Components

### Systemd Units (preferred, when available)

| Unit | Type | Purpose |
|------|------|---------|
| `amcp-watchdog.service` | User service | Health monitoring — checks gateway, triggers resurrection |
| `amcp-checkpoint.service` | User service | Checkpoint creation |
| `amcp-checkpoint.timer` | User timer | Scheduled checkpoint trigger (default: every 4 hours) |

Installed to `~/.config/systemd/user/`. Managed via `systemctl --user`.

### Cron Jobs (fallback)

If systemd user services are unavailable, equivalent cron entries are created:

| Entry | Purpose |
|-------|---------|
| Watchdog cron | Runs `watchdog.sh` at configured interval |
| Checkpoint cron | Runs `checkpoint.sh` on schedule (default: `0 */4 * * *`) |

### Files Created on Disk

| Path | Permissions | Purpose |
|------|-------------|---------|
| `~/.amcp/identity.json` | 0600 | Ed25519 keypair — **loss means checkpoints become unreadable** |
| `~/.amcp/config.json` | 0600 | Settings and API keys |
| `~/.amcp/last-checkpoint.json` | 0644 | Latest checkpoint CID and metadata |
| `~/.amcp/checkpoints/` | 0700 | Local checkpoint copies |
| `~/.amcp/watchdog-state.json` | 0644 | Watchdog runtime state |
| `~/.amcp/groq-usage.json` | 0644 | Groq token usage tracking (if Groq enabled) |
| `~/.amcp/error-cache.json` | 0644 | Condensed error cache (if Groq enabled) |
| `~/.amcp/batch-jobs.json` | 0644 | Batch pruning job tracking (if Groq enabled) |
| `~/.amcp/soul-drift.log` | 0644 | SOUL.md change detection log |
| `~/.amcp/resurrection.lock` | 0644 | Lock file to prevent concurrent recovery |

---

## Encryption

**Current state:** Checkpoints created via the AMCP CLI (`amcp checkpoint create`) use Ed25519-to-X25519 key conversion with ChaCha20-Poly1305 AEAD encryption. Secrets within checkpoints are encrypted separately before the full checkpoint is signed.

**What this means:**
- Checkpoint contents are encrypted with your identity key
- Only someone with your `identity.json` can decrypt checkpoints
- The checkpoint is signed — tampering is detectable
- CIDs (content addresses) are computed over the encrypted+signed bundle

**Plaintext exposure:** During staging (before `amcp checkpoint create` runs), files exist temporarily in a staging directory. The staging directory is cleaned up on exit (including on error) via a trap handler.

---

## How to Audit

Before running any script, inspect what it does:

```bash
# Read any script before executing
cat scripts/checkpoint.sh
cat scripts/full-checkpoint.sh
cat scripts/resuscitate.sh

# Check what network calls a script makes
grep -n 'curl' scripts/*.sh

# Check what files a script reads/writes
grep -n 'cp \|rsync\|mv \|rm ' scripts/*.sh

# Verify no hidden downloads or eval
grep -n 'eval\|source.*http\|curl.*| *bash\|wget.*| *sh' scripts/*.sh

# Check systemd units that would be installed
grep -A5 'ExecStart' scripts/install.sh scripts/init.sh

# Dry-run checkpoint to see what would be collected (without pinning)
CHECKPOINT_DIR=/tmp/audit-checkpoint bash scripts/checkpoint.sh
ls -la /tmp/audit-checkpoint/

# Check secret scanning patterns
cat scripts/scan-secrets.sh
```

---

## How to Uninstall

### 1. Stop Services

```bash
# Systemd
systemctl --user stop amcp-watchdog.service
systemctl --user stop amcp-checkpoint.timer
systemctl --user disable amcp-watchdog.service
systemctl --user disable amcp-checkpoint.timer
rm -f ~/.config/systemd/user/amcp-watchdog.service
rm -f ~/.config/systemd/user/amcp-checkpoint.service
rm -f ~/.config/systemd/user/amcp-checkpoint.timer
systemctl --user daemon-reload

# Cron (if used instead of systemd)
crontab -l | grep -v 'amcp\|checkpoint\|watchdog' | crontab -
```

### 2. Remove AMCP Data

```bash
# Remove all AMCP state (identity, config, checkpoints, logs)
rm -rf ~/.amcp/

# WARNING: This deletes your identity.json — you will NOT be able
# to decrypt existing checkpoints after this. Back up first if needed:
#   cp ~/.amcp/identity.json ~/identity-backup.json
```

### 3. Remove Skill

```bash
# If installed via OpenClaw
openclaw skills uninstall proactive-amcp

# If installed manually
rm -rf ~/.openclaw/skills/proactive-amcp
```

### 4. Remove Git Hooks (if installed)

```bash
# Check for AMCP pre-commit hook
cat .git/hooks/pre-commit
# Remove if it references scan-secrets.sh or proactive-amcp
rm -f .git/hooks/pre-commit
```

---

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Identity key theft | `identity.json` at 0600 permissions; back up offline |
| Checkpoint tampering | Ed25519 signatures; CID integrity (content-addressed) |
| Secret leakage in checkpoint | 11-pattern secret scanner blocks commits; secrets encrypted separately |
| Man-in-the-middle on IPFS pin | HTTPS to Solvr/Pinata; CID verification on fetch |
| Stale credentials in config | Secrets in `~/.amcp/config.json` (0600), never in identity file |
| Concurrent resurrection corruption | Lock file + PID tracking prevents parallel recovery |

---

## Security Scanner False Positives

### Unicode Control Characters (ZWJ)

Some security scanners may flag SKILL.md for "unicode control characters" or "prompt injection patterns." This is a **false positive** caused by the pirate emoji 🏴‍☠️.

**Technical explanation:**
- The pirate flag emoji is a compound emoji: 🏴 (black flag) + ZWJ + ☠️ (skull)
- ZWJ = Zero Width Joiner (U+200D), used to combine emojis
- Scanners detecting "invisible unicode" may flag ZWJ

**This is safe:** ZWJ is a standard Unicode character used in all compound emojis (family emojis, skin tone modifiers, flag sequences). It has no effect on LLM behavior or prompt interpretation.

**Verification:** View the raw bytes of SKILL.md to confirm only the pirate emoji contains ZWJ:
```bash
hexdump -C SKILL.md | grep "e2 80 8d"  # ZWJ bytes
```
