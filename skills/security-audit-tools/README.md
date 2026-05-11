# Security Audit Tools v2.0

Professional security audit toolkit for npm packages and GitHub repositories.

## 🎯 Recommended Method: Option A (Quick Scan + Deep Review)

**Best Practice**: 5-second Quick Scan + 1-hour Deep Review of critical files.

### Workflow

1. **Quick Scan** (5 seconds) – 100% code coverage
```bash
python3 tools/quick_scan.py <target_directory>

```


2. **Deep Review** (1 hour) – Line-by-line inspection of key files:
* **Wallet Services** (Private key handling)
* **Network Clients** (External APIs)
* **Transaction Services** (Fund operations)
* **Entry Points** (Overall architecture)


3. **Comprehensive Assessment** (5 minutes) – Quantitative reporting

**Advantages**:

* ✅ **Controllable Time** (1 hour vs. 10 hours)
* ✅ **High Reliability** (9/10)
* ✅ **Detects Logical Vulnerabilities**
* ✅ **100% Code Coverage** (via Quick Scan)

---

## Tools

### 1. quick_scan.py (New) ⚡

**Ultra-fast Security Scanner** – Scans all code in 5 seconds.

**Usage**:

```bash
python3 tools/quick_scan.py <path-to-source>

```

**Example**:

```bash
# Scan npm package
python3 tools/quick_scan.py ./npm-extract/package/src

# Scan GitHub repo
python3 tools/quick_scan.py ./github-repo/src

```

**Detection Items** (10 Critical Patterns):

1. ✅ Dynamic code execution (`eval`/`Function`)
2. ✅ Process creation (`exec`/`spawn`)
3. ✅ File operations (`fs.read`/`write`)
4. ✅ Suspicious network requests (Non-official domains)
5. ✅ Hardcoded private keys
6. ✅ Hardcoded Secrets/Tokens
7. ✅ Obfuscated code (`hex`/`base64`)
8. ✅ Data exfiltration patterns
9. ✅ Command injection
10. ✅ Dangerous npm packages (`shelljs`/`sudo`)

**Output**:

```text
Files scanned: 53
Lines scanned: 32,789
Total findings: 0
Risk score: 0/100
✅ LOW RISK - Safe to install

```

**Risk Scoring**:

* **0-39**: ✅ LOW RISK (Safe to install)
* **40-69**: ⚠️ MEDIUM RISK (Manual review required)
* **70-100**: ❌ HIGH RISK (Installation prohibited)

**Key Features**:

* ✅ **Extremely Fast**: Scans 30,000+ lines in 5 seconds.
* ✅ **100% Coverage**: Comprehensive code analysis.
* ✅ **Automated**: Detects 10 types of malicious patterns.
* ✅ **Quantitative**: Provides a risk score (0-100).
* ✅ **Reportable**: Supports JSON output.

---

### 2. audit-npm-package.sh

Automated NPM package audit tool.

**Usage**:

```bash
./tools/audit-npm-package.sh <package-name> <version>

```

**Example**:

```bash
./tools/audit-npm-package.sh @catalyst-team/poly-sdk 0.5.0

```

**What it does**:

1. Fetches NPM metadata.
2. Downloads and extracts the package.
3. Clones GitHub repository (if available).
4. Compares NPM package content with GitHub source.
5. Verifies integrity hashes.

**Output**: Creates an `audit-<package>-<version>/` directory containing all audit data.

---

### 3. audit-git-history.sh

Deep Git history analysis tool.

**Usage**:

```bash
./tools/audit-git-history.sh <path-to-git-repo>

```

**What it does**:

1. **Contributor Analysis**: Detects suspicious emails/identities.
2. **Timeline Analysis**: Monitors commit frequency and anomalies.
3. **Large Change Detection**: Identifies mass refactors or hidden injections.
4. **Suspicious Patterns**: Flags `eval`, `exec`, and `spawn` in history.
5. **Recent Changes**: Analyzes the latest commits for high-risk updates.

---

### 4. audit-source-code.sh

Deep source code analysis tool.

**Usage**:

```bash
./tools/audit-source-code.sh <path-to-source>

```

**What it does**:

1. **Statistics**: File counts and lines of code.
2. **Network**: Analyzes external request patterns.
3. **File System**: Detects sensitive I/O operations.
4. **Processes**: Monitors shell command execution.
5. **Dynamic Execution**: Identifies `eval()` or `new Function()`.
6. **Environment Variables**: Tracks sensitive data usage.
7. **Secrets**: Patterns for encryption keys and secrets.
8. **Obfuscation**: Identifies minified or encoded malicious payloads.
9. **Wallets**: Searches for crypto wallet/key patterns.
10. **Imports**: Comprehensive dependency analysis.

---

## Complete Audit Workflow (Updated)

### Recommended Workflow: Option A

**The fastest and most reliable approach**:

```bash
# Step 1: Quick Scan (5 seconds)
python3 tools/quick_scan.py ./audit-package-0.5.0/npm-extract/package/src

# Step 2: If LOW RISK, proceed to analyze key metadata
# Use helper tools:
./tools/audit-git-history.sh ./audit-package-0.5.0/github-repo
./tools/audit-source-code.sh ./audit-package-0.5.0/npm-extract/package/src

# Step 3: Manual Deep Review (1 hour)
# Focus on: Wallets, Networking, Transactions, and Entry Files.

# Step 4: Final assessment and report generation.

```

**Total Time**: ~1 Hour

**Reliability**: 9/10

---

### Traditional Workflow (Legacy/Backup)

1. **Run NPM Package Audit**:
`./tools/audit-npm-package.sh <name> <version>`
2. **Analyze Git History**:
`./tools/audit-git-history.sh ./github-repo`
3. **Analyze Source Code**:
`./tools/audit-source-code.sh ./src`
4. **Manual Deep Dive**:
Use tool outputs to review network requests, encryption, and key handling.

**Total Time**: ~2-3 Hours

---

## Quick Reference

### Tool Comparison

| Tool | Time | Coverage | Detection Type | Primary Use |
| --- | --- | --- | --- | --- |
| **quick_scan.py** | 5s | 100% | Obvious Malice | Initial Screening |
| audit-npm-package.sh | 30s | NPM Meta | Package Integrity | Verification |
| audit-git-history.sh | 10s | Git History | Suspicious Commits | Historical Audit |
| audit-source-code.sh | 10s | 100% | 9-Dimension Scan | Pattern Scanning |
| **Manual Review** | 1h | 10% | Logical Flaws | Code Comprehension |

### Use Cases

* **Scenario 1: Daily NPM Review**
Run `quick_scan.py`. If **LOW RISK**, install. If **MEDIUM/HIGH**, escalate.
* **Scenario 2: Critical Dependency Audit**
Follow **Option A** complete workflow + 1 hour manual review.
* **Scenario 3: Suspicious Code Investigation**
Use `audit-source-code.sh` to locate "HIGH/CRITICAL" hits and verify manually.

---

## Requirements

* **Node.js**: npm, node
* **Git**: git CLI
* **Unix tools**: shasum, grep, awk, sed, jq
* **Python**: python3 (for Quick Scan)

---

## Limitations

**These tools do NOT replace**:

* Professional third-party security audits.
* Dynamic behavior analysis (Docker sandboxing).
* Real-time network monitoring (Charles/Fiddler).
* Known malicious code database similarity checks.

**They DO provide**:

* ✅ Automated initial screening.
* ✅ Pattern-based detection.
* ✅ Risk scoring and prioritization.
* ✅ Focused guidance for manual reviewers.

---

## Version History

### v2.0 (2026-03-02)

* ✅ Added `quick_scan.py` - Ultra-fast security scanner.
* ✅ Introduced **Option A** workflow (Quick Scan + Deep Review).
* ✅ Optimized audit flow (1 hour vs. 10 hours).

### v1.0 (2026-03-02)

* ✅ Initial release with 3 core audit scripts.

---

**Current Version**: v2.0

**Last Updated**: 2026-03-02 21:48

**Author**: Anonymvs1234

