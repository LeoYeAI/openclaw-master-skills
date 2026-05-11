---
name: runtime-sentinel
description: >
  Runtime security guardian for OpenClaw agents. Use this skill whenever the
  user mentions security, skill safety, prompt injection, malware, suspicious
  behavior, credential leaks, network monitoring, skill integrity, or the
  ClawHavoc attack. Also trigger for phrases like "is this skill safe",
  "audit my skills", "check for threats", "my agent is acting weird",
  "scan for malware", "protect my agent", or any concern about what installed
  skills are doing at runtime. runtime-sentinel provides five active defenses:
  skill integrity hashing, prompt injection detection, credential exposure
  auditing, network egress monitoring, and process anomaly detection. Free tier
  covers hashing and basic injection scanning. Premium features (continuous
  daemon, egress monitoring, process anomaly detection) are gated via x402
  USDC micropayments on Base — no account or API key required.
compatibility:
  binaries:
    - sentinel          # compiled Rust binary in scripts/
  env:
    - SENTINEL_WALLET   # optional: Base wallet address for x402 payments
    - SENTINEL_RPC      # optional: Base RPC URL (defaults to public endpoint)
    - SENTINEL_VT_KEY   # optional: VirusTotal API key for hash lookups
  source: https://github.com/spaceman420urdog-afk/runtime-sentinel
---

# runtime-sentinel

A runtime security skill for OpenClaw. Defends against the threat landscape
exposed by ClawHavoc: backdoored skills, prompt injection via external data,
credential exfiltration, and process-level abuse.

**Free tier**: skill integrity checks, basic injection scanning.  
**Premium** (x402/USDC/Base): continuous daemon monitoring, network egress
monitoring, process anomaly detection, full audit log.

---

## Quick start

```
# One-shot audit of all installed skills (free)
sentinel audit

# Continuous guardian daemon (premium — will prompt for x402 payment)
sentinel daemon start

# Scan a single skill before installing
sentinel check <skill-path-or-clawhub-id>
```

---

## What runtime-sentinel defends against

See `references/threat-model.md` for the full threat matrix. In brief:

| Threat | Feature | Tier |
|---|---|---|
| Tampered skill files post-install | Integrity hashing | Free |
| Prompt injection via email/web/skill output | Injection scanner | Free |
| Plaintext secrets in skill dirs / SOUL.md | Credential auditor | Free |
| Unexpected outbound connections | Egress monitor | Premium |
| Shell commands outside declared behavior | Process anomaly | Premium |
| Continuous real-time protection | Daemon mode | Premium |

---

## Workflow

### 1 — First-time setup

```bash
# Install the binary (built from scripts/src/)
cargo install --path scripts/ --bin sentinel

# Verify installation and print wallet address
sentinel setup
```

`sentinel setup` will:
- Generate or import a Base wallet (BIP-39, stored in `~/.sentinel/wallet`)
- Print the wallet address so the user can fund it with USDC for premium
- Run a free baseline audit and print results

### 2 — On-demand audit (free)

When the user says anything like "scan my skills", "audit", "check for threats":

```bash
sentinel audit [--path ~/.openclaw/skills]
```

Output: a structured report of hash mismatches, injection patterns, and
exposed credentials. No payment required.

### 3 — Single skill check before install (free)

When the user wants to vet a skill before running `clawhub install`:

```bash
sentinel check <skill-directory-or-clawhub-id>
```

Prints a risk score (LOW / MEDIUM / HIGH / CRITICAL) with findings.

### 4 — Premium features via x402

When the user asks for daemon mode, egress monitoring, or process anomaly
detection, `sentinel` will automatically:

1. Hit the sentinel API endpoint
2. Receive a `402 Payment Required` with price in the `X-Payment-Request`
   header (typically $0.01–$0.05/day for daemon mode)
3. Sign the USDC transfer from `~/.sentinel/wallet`
4. Retry the request — access granted for the paid period

The user will see the price *before* their wallet signs anything. All
non-custodial. See `references/x402-payment.md` for the full payment flow.

### 5 — Daemon mode (premium)

```bash
sentinel daemon start    # runs in foreground, writes to ~/.sentinel/daemon.log
# Run in background from your shell if needed:
#   sentinel daemon start > ~/.sentinel/daemon.log 2>&1 &
#   disown
sentinel daemon status
sentinel daemon stop
sentinel daemon logs     # tail the audit log
```

The daemon watches:
- `~/.openclaw/skills/**` for file mutations (inotify / FSEvents)
- `~/.openclaw/SOUL.md` and `MEMORY.md` for unauthorized writes
- Network connections made by skill subprocesses
- Child process trees for undeclared shell commands

Alerts are delivered via OpenClaw's notification system and written to the
audit log.

---

## Interpreting results

### Risk levels

- **LOW**: No findings, or informational only (e.g. skill requests network
  but declares it)
- **MEDIUM**: Undeclared permission, suspicious pattern, or stale hash
- **HIGH**: Known malicious pattern, credential exposure, or undeclared
  egress
- **CRITICAL**: Active exfiltration attempt, reverse shell indicator, or
  SOUL.md mutation

### What to do on HIGH / CRITICAL

1. `sentinel isolate <skill-name>` — quarantines the skill (moves it out of
   the active skills directory)
2. Review the finding in `~/.sentinel/audit.log`
3. Check the skill's ClawHub VirusTotal report
4. If confirmed malicious, `clawhub uninstall <skill>` and report via
   `sentinel report <skill-name>`

---

## Reference files

Read these when you need deeper detail:

- `references/threat-model.md` — Full threat matrix and attack descriptions
  from ClawHavoc and similar campaigns
- `references/x402-payment.md` — x402 payment flow, wallet setup, and
  troubleshooting
- `references/binary-build.md` — How to build `sentinel` from source, cross-
  compilation targets, CI/CD

---

## Wallet setup for premium features

```bash
sentinel wallet show      # print address and USDC balance
sentinel wallet fund      # print QR code and address to send USDC
sentinel wallet export    # export mnemonic for backup (handle carefully)
sentinel wallet recover   # restore from mnemonic on a new machine
```

Minimum recommended balance for uninterrupted daemon mode: **$1 USDC**
(roughly 20–100 days of coverage depending on scan frequency).

---

## Privacy

`sentinel` is fully local. No skill content, file paths, or scan results are
sent to any server. The only outbound calls are:

1. x402 payment verification to the Base facilitator (amount + wallet address
   only)
2. Optional: VirusTotal hash lookups (hash only, no file content)

Both can be disabled with `--offline` for air-gapped environments (free tier
only in offline mode).
