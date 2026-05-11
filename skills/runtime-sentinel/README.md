# runtime-sentinel

**Runtime security guardian for OpenClaw agents.**

Defends against the threat landscape exposed by the ClawHavoc campaign: backdoored skills, prompt injection via external data, credential exfiltration, and process-level abuse. Integrates with VirusTotal (via the existing OpenClaw partnership) for hash-based malware detection.

---

## What it protects against

| Threat | Feature | Tier |
|---|---|---|
| Skill files tampered after install | Integrity hashing (SHA-256) | Free |
| Prompt injection via email / web / skill output | Injection scanner | Free |
| Plaintext secrets in skill dirs or SOUL.md | Credential auditor | Free |
| Unexpected outbound connections | Egress monitor | Premium |
| Shell commands outside declared behavior | Process anomaly detection | Premium |
| Continuous real-time protection | Daemon mode | Premium |
| SOUL.md / MEMORY.md poisoning | File watch + rollback | Premium |

---

## Quick start

```bash
# First-time setup (free — generates local wallet, runs baseline audit)
sentinel setup

# Audit all installed skills
sentinel audit

# Check a skill before installing it
sentinel check author/skill-name

# Start the guardian in foreground (premium)
sentinel daemon start

# Optional: run it in background at the shell level
sentinel daemon start > ~/.sentinel/daemon.log 2>&1 &
disown
```

---

## Payment

Premium features use [x402](https://github.com/coinbase/x402) — pay per day with USDC on Base. No account, no subscription, no API key. Your wallet is generated locally on setup and stays non-custodial.

| Feature | Price |
|---|---|
| Full premium bundle (daemon + egress + process anomaly) | $0.015 / day |
| On-demand deep scan | $0.02 / scan |
| Free tier (integrity, injection, credential scan) | Free, always |

Minimum recommended balance: **$1 USDC** (~66 days of full coverage).

---

## Security model

Three encrypted files live in `~/.sentinel/`:

- **`machine.key`** — 32-byte CSPRNG secret, never leaves the machine
- **`wallet/keystore.json`** — private key, AES-128-CTR + scrypt, passphrase derived via Argon2id from `machine.key`
- **`wallet/mnemonic.enc`** — 12-word recovery phrase, AES-256-GCM, separate Argon2id derivation

Back up your recovery phrase with `sentinel wallet export`. Recovery on a new machine: `sentinel wallet recover`.

---

## Privacy

`sentinel` is fully local. The only outbound calls are:

1. x402 payment verification (wallet address + amount only)
2. VirusTotal hash lookups (file hash only — no file content ever leaves your machine)

Both can be disabled with `--offline` (free tier only in offline mode).

---

## Installing manually

ClawHub installs the binary automatically. To install manually, download the correct binary for your platform from the [latest release](https://github.com/spaceman420urdog-afk/runtime-sentinel/releases/latest):

```bash
# macOS Apple Silicon
curl -L https://github.com/spaceman420urdog-afk/runtime-sentinel/releases/latest/download/sentinel-aarch64-apple-darwin -o sentinel
chmod +x sentinel && sudo mv sentinel /usr/local/bin/

# macOS Intel
curl -L https://github.com/spaceman420urdog-afk/runtime-sentinel/releases/latest/download/sentinel-x86_64-apple-darwin -o sentinel
chmod +x sentinel && sudo mv sentinel /usr/local/bin/

# Linux x86_64
curl -L https://github.com/spaceman420urdog-afk/runtime-sentinel/releases/latest/download/sentinel-x86_64-unknown-linux-gnu -o sentinel
chmod +x sentinel && sudo mv sentinel /usr/local/bin/

# Linux ARM64 (Raspberry Pi, cloud VMs)
curl -L https://github.com/spaceman420urdog-afk/runtime-sentinel/releases/latest/download/sentinel-aarch64-unknown-linux-gnu -o sentinel
chmod +x sentinel && sudo mv sentinel /usr/local/bin/
```

Verify the download: `sha256sum -c sentinel-checksums.txt`

---

## Building from source

Requires Rust 1.77+.

```bash
git clone https://github.com/spaceman420urdog-afk/runtime-sentinel
cd runtime-sentinel/scripts
cargo build --release
# binary at: target/release/sentinel
```

---

## License

MIT-0 — see [LICENSE](LICENSE).

---

## Reporting malicious skills

If `sentinel` flags a skill as malicious, you can report it to ClawHub directly:

```bash
sentinel report author/skill-name
```
