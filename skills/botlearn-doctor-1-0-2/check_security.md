# Domain: Security Risks

> Deep reference for Domain 3 in SKILL.md.
> Load this file when running L3 analysis or when SKILL.md thresholds need clarification.
>
> **Input:** `DATA.security`, `DATA.gateway_err_log`, `DATA.identity`, `DATA.config`
> **Output:** status (✅/⚠️/❌) + score (0–100) + risk classification + findings + fix hints
> **Privacy rule:** NEVER print credential values. Report type + file path + line number only.

---

## Analysis Checklist

### 1. Credential Exposure

From `DATA.security.credentials` (each item: `type`, `file`, `line` — value always redacted):

| Location | Severity | Score Impact |
|----------|----------|-------------|
| Config files | ❌ Critical | -30 per finding (max -60) |
| Log files | ❌ High | -20 per finding (max -40) |
| Workspace files | ⚠️ Medium | -10 per finding (max -20) |

Also scan `DATA.gateway_err_log` for credential patterns the script may have missed.
Redact before storing: replace matched values with `[REDACTED]`.

**Report format per finding:**
```
[type] credential in [file]:[line] — value REDACTED
```

---

### 2. File Permissions

From `DATA.security.file_permissions`:

| Permission Issue | Status | Score Impact |
|-----------------|--------|-------------|
| Sensitive file world-readable (o+r) | ⚠️ | -10 per file (max -30) |
| Sensitive file group-writable (g+w) | ⚠️ | -5 per file (max -20) |
| Identity credential file world-readable | ❌ | -20 per file |

From `DATA.identity` (directory listing only):
- Any `.pem`, `.key`, `.p12`, `.cert` with `o+r` in `ls -la` output → ❌ (-20 each)

**Fix:** `chmod 600 <file>`
**Rollback:** `chmod <original-mode> <file>` (note the original mode before applying fix)

---

### 3. Network Exposure

From `DATA.config.gateway` + `DATA.security.network_exposure`:

| Configuration | Risk Level | Status | Score Impact |
|--------------|------------|--------|-------------|
| `bind=loopback`, any auth | Low | ✅ | 0 |
| `bind=lan`, jwt/token auth | Medium | ⚠️ | -10 |
| `bind=lan`, `auth.type=none` | Critical | ❌ | -35 |
| `bind=tailnet`, any auth | Low-Medium | ⚠️ | -5 |
| `controlUI=true` on non-loopback | Critical | ❌ | -25 |

**Risk:** Unauthenticated LAN-exposed gateway allows any network device to invoke agent commands
and read memory contents. This is the highest-severity misconfiguration.

---

### 4. Dependency Vulnerabilities

From `DATA.security.vulnerabilities`:

| Finding | Score Impact |
|---------|-------------|
| Critical CVE (CVSS ≥ 9.0) | -15 per CVE (max -45) |
| High CVE (CVSS 7.0–8.9) | -5 per CVE (max -20) |
| Outdated packages (no known CVE) | -2 per package (max -10) |

**Fix:** `clawhub update` or `npm audit fix` (review breaking changes before applying)

---

### 5. VCS Sensitive Info

From `DATA.security.vcs`:

| Finding | Status | Score Impact |
|---------|--------|-------------|
| Sensitive files tracked in git | ❌ | -25 |
| `.env` or `*.key` without `.gitignore` coverage | ⚠️ | -10 |

---

## Risk Classification

Classify the overall risk level after scoring all 5 checks:

| Classification | Condition | Required Action |
|---------------|-----------|----------------|
| **Critical** | Any ❌ from credential exposure or unauthenticated LAN bind | Fix immediately |
| **High** | Any other ❌ | Fix before production use |
| **Medium** | Any ⚠️ without ❌ | Fix within this maintenance cycle |
| **Low** | All ✅ | Fix when convenient |

---

## Scoring

```
Base score: 100
Apply all score impacts (cumulative).
Floor: 0. Ceiling: 100.
```

| Score Range | Status |
|-------------|--------|
| ≥ 85 | ✅ |
| 65–84 | ⚠️ |
| < 65 | ❌ |

---

## Output Format

Produce in REPORT_LANG (domain label, risk label, and descriptions translated; paths and commands in English):

```
[Security Risks — translated domain label] [STATUS] — Score: XX/100
[Risk Level label in REPORT_LANG]: [Critical/High/Medium/Low — translated]
[One-sentence summary in REPORT_LANG]

[Credentials label in REPORT_LANG]:
  [type] in [file]:[line] — REDACTED     (if any)
  [Clean message in REPORT_LANG]         (if none)

[Permissions label in REPORT_LANG]:
  [file]: mode [XXX] — should be 600    (if any)
  [Clean message in REPORT_LANG]        (if none)

[Network label in REPORT_LANG]:
  Gateway: bind=[mode], auth=[type] — [risk note in REPORT_LANG]

[Vulnerabilities label in REPORT_LANG]:
  [X critical, X high CVEs]  (if any)
  [Clean message in REPORT_LANG] (if none)

[Identity label in REPORT_LANG]:
  [X devices registered]
  [Permission issue note if any]

[If any ⚠️/❌ — Findings label in REPORT_LANG, ordered by severity:]
1. [CRITICAL/HIGH/MEDIUM — translated] — [description with evidence]
   Fix: [command]
   Rollback: [rollback command]
```
