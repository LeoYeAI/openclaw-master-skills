---
name: sparkey
description: Time-limited, self-destructing SSH access for AI agents. Four-layer defense-in-depth: certificate TTL, OS account expiry, command-restricted dispatch, and automated cleanup. Zero session artifacts survive.
license: MIT
homepage: https://github.com/sanjeevneo/sparkey
files:
  - scripts/*
metadata: {"openclaw":{"requires":{"bins":["ssh-keygen","useradd","userdel","usermod","passwd","pkill","getent"],"anyBins":["at","systemd-run"]}},"clawdbot":{"requires":{"bins":["ssh-keygen","useradd","userdel","usermod","passwd","pkill","getent"]}}}
---

# Temporary SSH Access for AI Agent Support

Defense-in-depth temporary SSH access for AI agents — combines certificate TTL, OS account expiration, command-restricted dispatch, and automated cleanup. Zero session artifacts survive — all agent accounts, keys, certificates, dispatch shells, and cleanup timers are destroyed on session end or TTL expiry. The CA private key is a persistent operator-side credential requiring separate protection (see Security Considerations).

**Platform:** Linux (requires standard user-management tools).

## Prerequisites

Scripts check for required tools at startup and report what is missing. Install them on common distributions:

**Debian / Ubuntu:**
```bash
sudo apt-get update && sudo apt-get install -y openssh-client coreutils passwd at e2fsprogs procps
```

**Alpine Linux:**
```bash
apk add openssh-keygen bash shadow coreutils util-linux procps at e2fsprogs
```

**RHEL / CentOS / Fedora:**
```bash
sudo dnf install -y openssh-clients coreutils shadow-utils at e2fsprogs procps-ng
```

| Tool | Package (Debian) | Package (Alpine) | Required |
| ---- | ---------------- | ----------------- | -------- |
| `ssh-keygen` | `openssh-client` | `openssh-keygen` | Yes |
| `useradd` / `userdel` | `passwd` | `shadow` | Yes |
| `passwd` | `passwd` | `shadow` | Yes |
| `pkill` | `procps` | `procps` | Yes |
| `getent` | `libc-bin` | `musl-utils` | Yes |
| `at` | `at` | `at` | One of `at` or `systemd-run` |
| `shred` | `coreutils` | `coreutils` | Optional (falls back to `rm`) |
| `chattr` | `e2fsprogs` | `e2fsprogs` | Optional (for immutable authorized\_keys) |

If a required tool is missing, the script exits with an error listing missing dependencies. Optional tools produce warnings but do not block execution.

### Target Host Requirements

The target server (the machine the agent will SSH into) must have:

- **sshd running** and reachable on port 22 (or a configured port)
- **`~/.ssh/` directory** for the user whose `authorized_keys` will receive the agent's public key (the agent's one-liner creates this if missing)
- For CA-based access: `TrustedUserCAKeys` configured in `/etc/ssh/sshd_config` pointing to the CA public key

If the target is a fresh container or VM, install and start sshd first:

```bash
# Alpine
apk add openssh && ssh-keygen -A && rc-service sshd start

# Debian/Ubuntu
apt-get install -y openssh-server && systemctl start sshd
```

## When to Use

- An AI agent needs temporary shell access to diagnose or remediate a remote server
- You require auditable, time-boxed access that self-revokes
- You need to restrict what the agent can execute — no arbitrary commands
- You want zero persistent credentials once the session ends

## Agent-Initiated Access Flow (Recommended)

When an AI agent determines it needs shell access, it briefly states its intent: *"I need shell access to [target] to [reason]. I'll generate a temporary key — you decide where it goes. What username should I connect as?"* Then:

1. **Verify target is reachable** — `nc -z -w 2 TARGET 22` (or equivalent). If the port is closed, stop and inform the user: *"Port 22 is not open on [target]. Please start sshd, then I'll continue."*
2. **Check for existing session** — look for stale keys in `/tmp/agent_access_key*`. If found, test connectivity (`ssh -i /tmp/agent_access_key ... 'echo ok'`). If the key still works, skip to step 7. If expired or revoked, shred stale keys and continue.
3. **Generate keypair locally** — Ed25519, stored in `/tmp/` with a session-tagged comment.
4. **Ask for the connect username** — default to the current user on the target, not root. Ask: *"What username should I connect as? (default: your current user)"*. If the task requires root, inform the user: *"This task requires root. Please add the key to root's authorized_keys (or use `sudo`)."*
5. **Present public key with expiry** — provide a one-liner with `expiry-time` for crash safety. The one-liner creates `~/.ssh/` if absent and is tailored to the target username:
   ```
   mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo 'expiry-time="YYYYMMDDHHMMSS" ssh-ed25519 AAAA... agent-session-SID' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
   ```
   `expiry-time` (OpenSSH 8.2+) ensures the key is server-rejected after the timestamp, even if the agent crashes and never cleans up.

   **Important:** The one-liner must run as the target user so `~/.ssh/` resolves to the correct home directory. If adding the key for a different account (e.g., root), either `su - root` first or use the absolute path (e.g., `/root/.ssh/authorized_keys`).
6. **User adds the key** — the user decides where and how to grant access (maintains control).
7. **Verify connection** — connect as the agreed username: `ssh -i /tmp/agent_access_key USER@TARGET 'echo ok'`
8. **Schedule dead-man cleanup** — immediately after connecting, schedule automatic key removal on the target:
   ```bash
   echo "sed -i '/agent-session-SID/d' ~/.ssh/authorized_keys" | at now + 4 hours
   ```
   This fires independently of the agent. If the agent finishes early, it cancels the job and cleans up itself.
9. **Run fast recon** — OS, key packages, `screen`/`tmux` availability. Under 10 seconds.
10. **Create shared session** — start a `screen` or `tmux` session on the target so the user can attach and observe in real time.
11. **Work** — run diagnostics, remediation, or other tasks within the granted scope.
12. **Clean up** — remove the public key from `authorized_keys`, cancel the `at` job, destroy the local keypair.

### Crash Safety (Simple Mode)

Two independent mechanisms protect against agent crashes:

| Safeguard | Fires without agent? | Mechanism |
|-----------|---------------------|-----------|
| `expiry-time` in authorized_keys | Yes | Server-side — OpenSSH rejects the key after the timestamp |
| Scheduled `at` job | Yes | Runs on target's scheduler — removes the key entry on timer |

If the agent crashes and restarts, it reuses the stale keys from `/tmp/` (step 2) rather than re-provisioning, avoiding repeated user interaction.

This flow requires no script transfer to the target and leaves no persistent artifacts. For stronger guarantees (certificate TTL, command restriction, scheduled cleanup), layer the CA-based workflow below on top.

### Observability

After establishing access, the agent should create a shared terminal session:

```bash
# On the target — agent creates a named session
screen -dmS agent-work
screen -S agent-work -X multiuser on
screen -S agent-work -X acladd root

# User attaches to watch
screen -x agent-work
```

If `screen` is unavailable, `tmux` works similarly:
```bash
tmux new-session -d -s agent-work
# User attaches:
tmux attach -t agent-work
```

The agent should check for `screen`/`tmux` availability during initial recon and install if needed (with user permission).

## Architecture: Defense in Depth

Four independent expiration and restriction mechanisms ensure no single failure leaves access open:

| Layer | Mechanism | What It Does |
|-------|-----------|--------------|
| 1 | **SSH Certificate TTL** | Cryptographically enforced expiry (`-V +Nh`) — server rejects expired certs |
| 2 | **OS Account Expiration** | `useradd --expiredate` — login denied after date |
| 3 | **Forced Command / Safe Dispatch** | Exact command-name matching, path-restricted arguments, no `eval` |
| 4 | **Scheduled Cleanup** | `at` or `systemd-run` timer — removes account, keys, and config after TTL |

## Quick Start

All scripts run on the **operator's machine** (the admin/signing host), not on the target server. Only public artifacts (CA public key, dispatch shell, agent account) are deployed to the target.

```bash
# 1. One-time: Initialize the SSH Certificate Authority (run on admin/signing host)
sudo bash scripts/setup-ca.sh

# 2a. Preview what would happen (no changes made):
sudo bash scripts/grant-access.sh --host TARGET_HOST --duration 4h --agent-pubkey /path/to/agent_key.pub --dry-run

# 2b. Grant access using the agent's existing public key (recommended):
sudo bash scripts/grant-access.sh --host TARGET_HOST --duration 4h --agent-pubkey /path/to/agent_key.pub

# 2c. Or generate a keypair (you must securely deliver the private key to the agent):
sudo bash scripts/grant-access.sh --host TARGET_HOST --duration 4h --allow diagnostic

# 3. Revoke access: Immediately revoke before TTL expires (if needed)
sudo bash scripts/revoke-access.sh --session SESSION_ID

# 4. Audit: Scan for orphaned artifacts from previous sessions
sudo bash scripts/audit.sh
```

## Detailed Workflow

### Phase 1: Certificate Authority Setup (One-Time)

Run `scripts/setup-ca.sh` once on the signing host (your admin machine, **not** the target server).

This script:
1. Generates an Ed25519 CA key pair at `/etc/ssh/agent_ca` (private) and `/etc/ssh/agent_ca.pub` (public)
2. Sets strict permissions (`chmod 400`) on the private key
3. Outputs the public key for distribution to target servers

On each target server, add to `/etc/ssh/sshd_config`:
```
TrustedUserCAKeys /etc/ssh/agent_ca.pub
```
Then restart sshd to trust certificates signed by your CA.

### Phase 2: Granting Access

Run `scripts/grant-access.sh` to provision a temporary session:

#### Step 2a: Create Ephemeral Agent Account
```bash
# Create account with OS-level expiration (Layer 2)
# Account suffix uses 4 bytes of entropy (8 hex chars) with collision check
sudo useradd \
  --expiredate "$(date -d '+5 hours' +%Y-%m-%d)" \
  --shell /bin/bash \
  --create-home \
  --comment "AI Agent Support [SESSION_ID]" \
  agent_support_XXXXXXXX
```

- Account name includes a random 8-hex-char suffix with collision detection
- `--expiredate` sets an OS-level hard cutoff (rounded to midnight — a safety net, not the primary TTL)
- Home directory resolved via `getent passwd` (no `eval`)

#### Step 2b: Key Material

**Recommended: Agent provides its own public key (`--agent-pubkey`)**

The agent retains its private key — no secret transfer required. The script signs the agent's public key with the CA (or installs it in authorized_keys).

```bash
sudo bash scripts/grant-access.sh --host TARGET --duration 4h --agent-pubkey /path/to/agent.pub
```

**Alternative: Script generates a keypair**

If `--agent-pubkey` is omitted, the script generates an ephemeral Ed25519 keypair in `/tmp/`. The operator must then securely deliver the private key to the agent.

```bash
ssh-keygen -t ed25519 -N "" -f /tmp/agent_session_XXXX -C "agent-support-SESSION_ID"
```

- Empty passphrase (`-N ""`) — the AI agent cannot enter passphrases interactively
- Keypair persists in `/tmp/` until cleanup (securely deleted with `shred -u`)

#### Step 2c: Sign Certificate with TTL (Layer 1)
```bash
# Sign the public key with the CA, enforcing time limit
ssh-keygen -s /etc/ssh/agent_ca \
  -I "agent-support-SESSION_ID" \
  -n agent_support_XXXXXXXX \
  -V +4h \
  -O no-port-forwarding \
  -O no-x11-forwarding \
  -O no-agent-forwarding \
  -O no-pty \
  -O force-command=/usr/local/bin/agent-support-shell-SESSION_ID \
  /path/to/agent.pub
```

**Certificate options explained:**
- `-s /etc/ssh/agent_ca` — sign with the CA private key
- `-I "agent-support-SESSION_ID"` — identity string for audit logs
- `-n agent_support_XXXXXXXX` — principal must match the account name
- `-V +4h` — certificate valid for exactly 4 hours (cryptographic enforcement)
- `-O no-port-forwarding` — prevent SSH tunneling
- `-O no-x11-forwarding` — no GUI forwarding
- `-O no-agent-forwarding` — no agent key forwarding
- `-O no-pty` — omit if the agent needs an interactive shell (`--with-pty`)
- `-O force-command=...` — all commands routed through the safe dispatch shell

#### Step 2d: Command Restriction Shell (Layer 3)

Each session receives its own restriction shell at `/usr/local/bin/agent-support-shell-SESSION_ID`. The shell uses **safe dispatch** — no `eval`, no prefix matching:

1. **Shell metacharacters blocked** — `;`, `|`, `&`, `$`, backticks, `()`, `{}`, `<>`, `\` all rejected before parsing
2. **Command parsed into name + arguments** via `read -ra`
3. **Command name matched exactly** via `case` statement (not prefix matching)
4. **Subcommands validated** for multi-part commands (`systemctl status` allowed, `systemctl enable` denied)
5. **Path arguments validated** against allowed directory prefixes
6. **Commands executed directly** as `"$COMMAND" "${ARGS[@]}"` with a 5-minute timeout
7. **Absolute paths rejected** as command names (prevents `/sbin/shutdown`)

For broader access profiles, use the `--allow` flag:

| Profile | Commands Permitted |
|---------|-------------------|
| `diagnostic` | Read-only: system info, logs (path-restricted to `/var/log/`, `/proc/`, `/sys/`, `/run/`, `/tmp/`), service status, network diagnostics, Docker inspect |
| `remediation` | Diagnostic + service restarts, process kills, file operations (path-restricted to `/etc/`, `/var/`, `/tmp/`), Docker management, curl/wget |
| `full` | Unrestricted (use with extreme caution — no restriction shell installed) |

#### Step 2e: Schedule Automatic Cleanup (Layer 4)

```bash
# Scheduled via at(1) or systemd-run with ceiling-rounded delay
echo "bash /usr/local/sbin/agent-cleanup-SESSION_ID.sh" | at now + 80 minutes
```

Each session receives its own cleanup script (`agent-cleanup-SESSION_ID.sh`) to prevent concurrent-session collisions.

### Phase 3: Agent Connects

The AI agent uses the session credentials:

```bash
# With agent-provided key:
ssh -i ~/.ssh/agent_key agent_support_XXXXXXXX@TARGET_HOST 'uptime'

# With generated key:
ssh -i /tmp/agent_session_XXXX agent_support_XXXXXXXX@TARGET_HOST 'df -h'
```

### Phase 4: Access Revocation

Access terminates automatically through multiple independent mechanisms and can also be revoked on demand.

#### Automatic Expiration
- **Certificate TTL** (Layer 1): Server rejects the cert after `-V` window. Server logs: `error: Certificate invalid: expired`
- **Account expiration** (Layer 2): OS denies login after `--expiredate`. Logs: `User account has expired`
- **Scheduled cleanup** (Layer 4): Removes account, keys, support shell, and cleanup script

#### Immediate Revocation
```bash
sudo bash scripts/revoke-access.sh --session SESSION_ID
# or
sudo bash scripts/revoke-access.sh --user agent_support_XXXXXXXX
# or revoke all:
sudo bash scripts/revoke-access.sh --all
```

The revocation script:
1. Locks the account (`usermod -L`)
2. Kills active SSH sessions for the user
3. Removes immutable-file protections (`chattr -i`)
4. Archives session logs to `/var/log/agent-support-archive/`
5. Removes the account and home directory (`userdel -r`)
6. Securely deletes session keys (`shred -u`; falls back to `rm -f`)
7. Cancels scheduled cleanup timers and removes session-specific files

### Phase 5: Audit

All agent activity is logged to `/var/log/agent-support.log` with sanitized entries (via `printf '%q'` to prevent log injection):

```
[2026-03-15T16:00:00Z] SESSION_START: 20260315160000-a1b2c3d4 user=agent_support_e5f6g7h8 host=TARGET ttl=4h profile=diagnostic
[2026-03-15T16:00:05Z] AGENT_EXEC: uptime
[2026-03-15T16:00:10Z] AGENT_EXEC: df\ -h
[2026-03-15T16:00:15Z] AGENT_BLOCKED: rm\ -rf\ /
[2026-03-15T20:00:00Z] SESSION_END: 20260315160000-a1b2c3d4 reason=ttl_expired
```

## Manual Approach (Without Scripts)

### Grant Access Manually

```bash
# 1. Create temporary account (expires tomorrow as safety net)
sudo useradd --expiredate "$(date -d '+1 day' +%Y-%m-%d)" \
  --shell /bin/bash --create-home agent_support

# 2. Accept the agent's public key (recommended) or generate a keypair
# Option A: Agent provides their pubkey
PUBKEY="/path/to/agent_pubkey.pub"
# Option B: Generate
ssh-keygen -t ed25519 -N "" -f /tmp/agent_key -C "agent-support"
PUBKEY="/tmp/agent_key.pub"

# 3. Sign with CA (4-hour window, restricted)
ssh-keygen -s /etc/ssh/agent_ca \
  -I "agent-manual-session" \
  -n agent_support \
  -V +4h \
  -O no-port-forwarding \
  -O no-x11-forwarding \
  -O no-agent-forwarding \
  "$PUBKEY"

# 4. Verify the certificate
ssh-keygen -L -f "${PUBKEY%.pub}-cert.pub"

# 5. Schedule cleanup
echo "userdel -r agent_support && shred -u /tmp/agent_key*" | at now + 5 hours

# 6. Deliver the certificate (and private key if generated) to the AI agent
```

### Revoke Access Manually

```bash
# Lock the account immediately
sudo usermod -L agent_support

# Kill active sessions
sudo pkill -u agent_support

# Remove account and home directory
sudo userdel -r agent_support

# Destroy session keys
shred -u /tmp/agent_key /tmp/agent_key-cert.pub /tmp/agent_key.pub 2>/dev/null

# Remove scheduled cleanup
atq | grep agent && atrm JOB_NUMBER
```

## Alternative: authorized_keys-Only Approach (No CA)

For environments where a CA is not feasible:

```bash
sudo bash scripts/grant-access.sh --host TARGET --duration 4h --no-ca --agent-pubkey /path/to/agent.pub
```

This installs the agent's public key in `authorized_keys` with the following restrictions:

```
expiry-time="YYYYMMDDHHMMSS",restrict,command="/usr/local/bin/agent-support-shell-SID" ssh-ed25519 AAAA...
```

- `expiry-time` — key rejected after this UTC timestamp
- `restrict` — disables port/agent/X11 forwarding and PTY allocation
- `command="..."` — forces all commands through the safe dispatch shell
- `chattr +i` makes the file immutable to prevent modification

**Limitation:** `expiry-time` is server-side only and lacks cryptographic enforcement. Always pair with `chattr +i`.

## Security Considerations

### AI Agent-Specific Concerns

1. **No passphrase on session keys** — mitigated by short-lived certificates (hours, not days), immediate key destruction, and immutable authorized_keys

2. **Command injection** — the dispatch shell blocks all shell metacharacters, matches command names exactly via `case` (not prefix), validates argument paths against directory allowlists, resolves symlinks before comparison, and rejects absolute paths as command names; commands execute directly without `eval`

3. **Key delivery** — use `--agent-pubkey` (recommended) so the private key never leaves the agent; if generating keys, the operator must deliver the private key securely

4. **Scope creep** — start with `diagnostic`; escalate to `remediation` or `full` only when explicitly needed

5. **Symlink traversal** — path validation resolves symlinks via `readlink -f` before checking directory prefixes; a symlink from `/var/log/evil` → `/etc/shadow` is resolved and rejected

### Break-Glass Recovery

If the agent loses access mid-session (certificate expired, context lost, network failure):

1. **Console access** — use hypervisor/cloud console (LXC `lxc-attach`, AWS SSM, GCP serial console) to regain access
2. **Revoke stale sessions** — run `sudo bash scripts/revoke-access.sh --all` to clean up orphaned accounts
3. **Re-provision** — run `grant-access.sh` again for a fresh session

**Critical rule:** never disable existing access paths (e.g., root SSH) before verifying the agent's own access works. Always keep at least one independent recovery path available.

### General Hardening

- Keep the CA private key on a separate, secured host — never on the target server
- Use Ed25519 keys for all operations
- Set `MaxSessions 1` for the agent account in `sshd_config`
- Set `MaxAuthTries 3` to limit brute-force attempts
- Set `AuthenticationMethods publickey` to restrict to key-based auth
- Enable `LogLevel VERBOSE` in `sshd_config`
- Monitor `/var/log/auth.log` and `/var/log/agent-support.log` during active sessions

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Certificate invalid: expired` | Certificate TTL elapsed | Re-run `grant-access.sh` for a new session |
| `Certificate invalid: name is not a listed principal` | Username mismatch between cert `-n` and account | Ensure `-n` matches the created account name |
| `User account has expired` | OS-level `--expiredate` passed | Create a new account with later expiry |
| `Permission denied (publickey)` | CA public key not in `TrustedUserCAKeys` | Verify server config and restart sshd |
| `WARNING: UNPROTECTED PRIVATE KEY FILE` | Key file permissions too open | `chmod 600 /tmp/agent_session_XXXX` |
| `Shell metacharacters are not allowed` | Agent sent `;`, `\|`, `$`, etc. | Send simple commands without shell operators |
| `Command not in allowlist` | Agent tried an unlisted command | Use a broader `--allow` profile or add the command |
| `Path outside allowed directories` | Agent accessed a path outside allowed prefixes | Restrict to `/var/log/`, `/proc/`, `/sys/` (diagnostic) or add `/etc/` (remediation) |
| `Missing required dependencies` | Linux tools not installed | Install `openssh-client`, `coreutils`, `at` or `systemd` |
| `Connection reset by peer` (before auth) | IP auto-blocked by brute-force protection | Unblock the IP (fail2ban, Synology autoblock, etc.), then retry |
| Key added but auth fails | `AuthorizedKeysFile` points elsewhere | Check `sshd_config`; Proxmox uses `/etc/pve/priv/authorized_keys` |

### Platform-Specific Notes

**Synology DSM** — not fully compatible. DSM wraps sshd behind `synorelayd`, which intercepts SSH on port 22 and may silently block connections after repeated failures:

- Dual sshd instances: port 22 (via synorelayd) and port 222 (SFTP-only, pubkey)
- Home directories at `/var/services/homes/USER/` (symlinked from `/volume1/homes/USER/`)
- DSM may reset `sshd_config` on service restart
- Default home directory permissions are `777` — SSH silently rejects pubkey auth; fix with `chmod 755`
- `PubkeyAuthentication yes` must be explicitly uncommented in `sshd_config`
- Connect as `admin` (not `root`) via the DSM-configured SSH port
- If connections reset, restart synorelayd: `sudo /usr/syno/bin/synosystemctl restart synorelayd`

**Proxmox VE** — may store authorized keys in `/etc/pve/priv/authorized_keys` instead of `~/.ssh/`. Check `AuthorizedKeysFile` in `sshd_config`.

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| `setup-ca.sh` | `scripts/` | One-time CA key pair generation (warns on key age >90 days) |
| `grant-access.sh` | `scripts/` | Provision temporary agent access (supports `--dry-run`, sshd pre-flight check) |
| `revoke-access.sh` | `scripts/` | Immediate access revocation with post-removal verification |
| `audit.sh` | `scripts/` | Scan for orphaned artifacts (accounts, keys, shells, at jobs) |
| CA private key | `/etc/ssh/agent_ca` | Signs session certificates (keep secure) |
| CA public key | `/etc/ssh/agent_ca.pub` | Distributed to target servers |
| Support shell | `/usr/local/bin/agent-support-shell-SID` | Per-session command dispatch |
| Cleanup script | `/usr/local/sbin/agent-cleanup-SID.sh` | Per-session auto-cleanup |
| Session log | `/var/log/agent-support.log` | Audit trail of all agent commands |
| Archive | `/var/log/agent-support-archive/` | Archived logs from expired sessions |

## Security Manifest

| Category | Details |
|----------|---------|
| **Environment variables** | None accessed |
| **External endpoints** | None — this skill makes zero network calls |
| **Local files read** | `/etc/passwd` (user lookup), `/etc/ssh/agent_ca` (CA signing), agent public key (if provided) |
| **Local files written** | `/etc/ssh/agent_ca{,.pub}` (setup-ca.sh), `/usr/local/bin/agent-support-shell-SID` (per-session), `/usr/local/sbin/agent-cleanup-SID.sh` (per-session), `/tmp/agent_session_SID{,.pub,-cert.pub}` (ephemeral keys), `/var/log/agent-support.log` (audit), `~agent/.ssh/authorized_keys` (no-ca mode) |
| **OS state mutated** | Creates/deletes Linux user accounts (`useradd`/`userdel`), schedules cleanup timers (`at`/`systemd-run`) |
| **Data transmitted** | No data leaves the local machine. All operations are local to the host. |

## Trust & Privacy

This skill operates entirely offline — no telemetry, no analytics, no data transmitted to external services. All sensitive material (private keys, certificates) is destroyed after session expiration via `shred -u` (falling back to `rm -f`). Audit logs remain on the local filesystem under `/var/log/` for operator review.
