# Patrol Check Reference — OpenClaw Daily Security Patrol

Detailed commands, patterns, and thresholds for the 8 patrol checks. This document is the reference for the `patrol` subcommand.

**Path convention**: `$OC` = `${OPENCLAW_STATE_DIR:-$HOME/.openclaw}`

---

## Check 1: Skill/Plugin Integrity

**Purpose**: Detect tampered, unregistered, or drifted skill packages.

### Steps

1. Discover skill directories:
   ```bash
   ls -d $OC/skills/*/ ~/.openclaw/skills/*/ 2>/dev/null
   ```
   Each directory containing a `SKILL.md` is a skill.

2. For each skill, compute hash:
   ```bash
   node scripts/trust-cli.ts hash --path <skill_dir>
   ```

3. Look up attested hash in trust registry:
   ```bash
   node scripts/trust-cli.ts lookup --source <skill_dir> --version <version>
   ```

4. Compare hashes. If mismatch, run quick re-scan:
   ```bash
   # Use Grep + scan rules on the skill directory (same as /agentguard scan)
   ```

### Findings

| Tag | Severity | Condition |
|-----|----------|-----------|
| `INTEGRITY_DRIFT` | HIGH | Computed hash differs from attested hash |
| `UNREGISTERED_SKILL` | MEDIUM | Skill directory exists but has no trust record |
| `NEWLY_CRITICAL` | CRITICAL | Re-scan of drifted skill finds CRITICAL findings |

---

## Check 2: Secrets Exposure

**Purpose**: Detect plaintext secrets leaked in workspace files, memory logs, and sensitive directories.

### Scan Targets

| Path | Scope |
|------|-------|
| `$OC/workspace/` | Full recursive (especially `memory/`, `logs/`) |
| `$OC/.env*` | Any dotenv files in OC root |
| `~/.ssh/` | Permission check only |
| `~/.gnupg/` | Permission check only |

### Patterns (cross-ref scan-rules.md)

| Rule ID | Tag | Pattern Summary |
|---------|-----|-----------------|
| Rule 7 | PRIVATE_KEY_PATTERN | `['"\x60]0x[a-fA-F0-9]{64}['"\x60]`, `private[_\s]?key\s*[:=]` |
| Rule 8 | MNEMONIC_PATTERN | 12/24 BIP-39 words, `seed[_\s]?phrase`, `mnemonic\s*[:=]` |
| Rule 5 | READ_SSH_KEYS | `\.ssh/id_rsa`, `\.ssh/id_ed25519` in workspace files |

### Additional Patterns (cross-ref action-policies.md)

| Type | Pattern | Severity |
|------|---------|----------|
| AWS Secret Key | `[A-Za-z0-9/+=]{40}` near AWS context | HIGH |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | HIGH |
| GitHub Token | `gh[pousr]_[A-Za-z0-9_]{36,}` | HIGH |
| DB Connection String | `(postgres\|mysql\|mongodb)://` | MEDIUM |

### Permission Checks

```bash
# SSH directory — should be 700
stat -f "%Lp" ~/.ssh/ 2>/dev/null || stat -c "%a" ~/.ssh/ 2>/dev/null
# GnuPG — should be 700
stat -f "%Lp" ~/.gnupg/ 2>/dev/null || stat -c "%a" ~/.gnupg/ 2>/dev/null
```

| Condition | Severity |
|-----------|----------|
| `~/.ssh/` permissions > 700 | HIGH |
| `~/.gnupg/` permissions > 700 | MEDIUM |

---

## Check 3: Network Exposure

**Purpose**: Detect dangerous port exposure, missing firewall, and suspicious connections.

### Listening Ports

```bash
# Linux
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
# macOS
lsof -i -P -n | grep LISTEN 2>/dev/null
```

### High-Risk Default Ports

Flag if bound to `0.0.0.0` or `*` (not `127.0.0.1`):

| Port | Service | Severity |
|------|---------|----------|
| 22 | SSH (default port) | MEDIUM |
| 3306 | MySQL | HIGH |
| 5432 | PostgreSQL | HIGH |
| 6379 | Redis | CRITICAL |
| 27017 | MongoDB | HIGH |
| 9200 | Elasticsearch | HIGH |
| 2375/2376 | Docker API | CRITICAL |
| 8080 | Generic HTTP | LOW |

### Firewall Status

```bash
# Linux (UFW)
ufw status 2>/dev/null
# Linux (iptables) — check for ACCEPT all on INPUT
iptables -L INPUT -n 2>/dev/null | head -20
# macOS
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null
```

| Condition | Severity |
|-----------|----------|
| Firewall disabled / inactive | HIGH |
| Redis/Docker API on 0.0.0.0 | CRITICAL |
| Database on 0.0.0.0 without auth | HIGH |
| SSH on default port 22 | MEDIUM (informational) |

### Outbound Connection Check

```bash
# Established outbound connections
ss -tnp state established 2>/dev/null || netstat -tnp 2>/dev/null | grep ESTABLISHED
```

Cross-reference remote IPs/domains against:
- action-policies.md webhook/exfil domain list (Discord, Telegram, ngrok, webhook.site, etc.)
- scan-rules.md Rule 23 SUSPICIOUS_IP validation (exclude private ranges)
- action-policies.md high-risk TLDs (`.xyz`, `.top`, `.tk`, `.ml`, `.ga`, `.cf`, `.gq`)

---

## Check 4: Cron & Scheduled Tasks

**Purpose**: Detect malicious or unauthorized scheduled tasks, especially download-and-execute patterns.

### Data Collection

```bash
# OpenClaw cron jobs
openclaw cron list 2>/dev/null

# System crontab
crontab -l 2>/dev/null

# System cron directories
ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/ 2>/dev/null

# Systemd timers
systemctl list-timers --all 2>/dev/null

# User systemd units
ls -la ~/.config/systemd/user/ 2>/dev/null
```

### Scan Patterns (cross-ref scan-rules.md Rule 2: AUTO_UPDATE)

Scan cron command bodies for:

| Pattern | Description | Severity |
|---------|-------------|----------|
| `curl.*\|\s*(bash\|sh)` | curl pipe to shell | CRITICAL |
| `wget.*\|\s*(bash\|sh)` | wget pipe to shell | CRITICAL |
| `fetch.*then.*eval` | Fetch and eval | CRITICAL |
| `download.*execute` (i) | Download-and-execute | HIGH |
| `base64 -d \| bash` | Decode and execute | CRITICAL |
| `eval "$(curl`  | eval curl output | CRITICAL |

### Additional Checks

| Condition | Severity |
|-----------|----------|
| Unknown cron job touching `$OC/` as root | HIGH |
| Cron job downloading from external URL | HIGH |
| Cron job not present in `openclaw cron list` but touches `$OC/` | MEDIUM |

---

## Check 5: File System Changes

**Purpose**: Detect suspicious file modifications in the last 24 hours.

### Scan Targets

```bash
# Files modified in last 24h
find $OC/ -type f -mtime -1 2>/dev/null
find ~/.ssh/ -type f -mtime -1 2>/dev/null
find ~/.gnupg/ -type f -mtime -1 2>/dev/null
find /etc/cron.d/ -type f -mtime -1 2>/dev/null
```

### Analysis

1. **Count and list** all modified files
2. For files matching scannable extensions (`.js`, `.ts`, `.py`, `.sh`, `.md`, `.json`, `.yaml`):
   - Run the full scan rule set against each file (same rules as `/agentguard scan`)
   - Report any findings with the relevant rule IDs
3. **Permission check** on critical files:

| File | Expected Permission |
|------|-------------------|
| `$OC/openclaw.json` | 600 |
| `$OC/devices/paired.json` | 600 |
| `~/.ssh/authorized_keys` | 600 |
| `/etc/ssh/sshd_config` | 644 |

4. **New executable detection**:
   ```bash
   find $OC/workspace/ -type f -perm +111 -mtime -1 2>/dev/null
   ```

---

## Check 6: Audit Log Analysis

**Purpose**: Analyze AgentGuard's own audit trail for attack patterns and anomalies.

### Data Source

```
~/.agentguard/audit.jsonl
```

Each line: `{"timestamp":"...","tool_name":"...","decision":"...","risk_level":"...","risk_tags":[...],"initiating_skill":"..."}`

### Analysis (last 24h)

1. **Aggregate statistics**:
   - Total events, deny count, confirm count, allow count
   - Group denials by `risk_tags`
   - Group denials by `initiating_skill`

2. **Pattern detection**:

| Pattern | Condition | Severity |
|---------|-----------|----------|
| Repeated denial | Same skill denied 3+ times | HIGH |
| Critical event | Any event with `risk_level: critical` | CRITICAL |
| Exfiltration attempt | `WEBHOOK_EXFIL` or `NET_EXFIL_UNRESTRICTED` tag | HIGH |
| Prompt injection | `PROMPT_INJECTION` tag in events | CRITICAL |
| Unrevoked violator | Skill with 5+ denials still not revoked in registry | MEDIUM |

3. **Recommendation generation**:
   - For skills with high deny rates: suggest `/agentguard trust revoke`
   - For critical events: suggest immediate investigation

---

## Check 7: Environment & Configuration

**Purpose**: Verify OpenClaw and AgentGuard configuration security.

### Environment Variable Scan

```bash
# List env vars with sensitive names (names only, values masked)
env | grep -iE 'API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE|CREDENTIAL' | awk -F= '{print $1 "=(masked)"}'
```

### Configuration Checks

| Check | Command | Expected |
|-------|---------|----------|
| AgentGuard protection level | Read `~/.agentguard/config.json` | Not `permissive` for production |
| GoPlus API configured | Check `GOPLUS_API_KEY` exists | Set if Web3 features used |
| Config baseline hash | `sha256sum -c $OC/.config-baseline.sha256` | All OK (if baseline exists) |

### Severity

| Condition | Severity |
|-----------|----------|
| Protection level = `permissive` | MEDIUM |
| Sensitive env var with `PRIVATE_KEY` or `MNEMONIC` in name | HIGH |
| Config baseline hash mismatch | HIGH |
| Config baseline missing | LOW (informational) |

---

## Check 8: Trust Registry Health

**Purpose**: Verify the trust registry is well-maintained and no over-privileged skills exist.

### Data Collection

```bash
node scripts/trust-cli.ts list
```

### Analysis

| Check | Condition | Severity |
|-------|-----------|----------|
| Expired attestation | `expires_at` < now | MEDIUM |
| Stale trusted skill | `trust_level: trusted` + `updated_at` > 30 days ago | LOW |
| Installed but untrusted | Skill directory exists + `trust_level: untrusted` | MEDIUM |
| Over-privileged | `exec: allow` AND `network_allowlist: ["*"]` | HIGH |
| Empty registry | No records at all despite installed skills | MEDIUM |

### Statistics Output

- Total trust records
- Distribution: trusted / restricted / untrusted / revoked
- Skills with Web3 capabilities enabled

---

## Overall Status Calculation

| Condition | Status |
|-----------|--------|
| Any check has CRITICAL findings | **FAIL** |
| Any check has HIGH findings | **WARN** |
| Only MEDIUM/LOW findings | **PASS** (with notes) |
| No findings | **PASS** |
