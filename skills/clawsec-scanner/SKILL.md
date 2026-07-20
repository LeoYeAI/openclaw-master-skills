---
name: clawsec-scanner
version: 0.0.2
description: Automated vulnerability scanner for agent platforms. Performs dependency scanning (npm audit, pip-audit), multi-database CVE lookup (OSV, NVD, GitHub Advisory), SAST analysis (Semgrep, Bandit), and agent-specific DAST hook execution testing for OpenClaw hooks.
homepage: https://clawsec.prompt.security
clawdis:
  emoji: "🔍"
  requires:
    bins: [node, npm, python3, pip-audit, semgrep, bandit, jq, curl]
---

# ClawSec Scanner

Comprehensive security scanner for agent platforms that automates vulnerability detection across multiple dimensions:

- **Dependency Scanning**: Analyzes npm and Python dependencies using `npm audit` and `pip-audit` with structured JSON output parsing
- **CVE Database Integration**: Queries OSV (primary), NVD 2.0, and GitHub Advisory Database for vulnerability enrichment
- **SAST Analysis**: Static code analysis using Semgrep (JavaScript/TypeScript) and Bandit (Python) to detect hardcoded secrets, command injection, path traversal, and unsafe deserialization
- **DAST Framework**: Agent-specific dynamic analysis with real OpenClaw hook execution harness (malicious input, timeout, output bounds, event mutation safety)
- **Unified Reporting**: Consolidated vulnerability reports with severity classification and remediation guidance
- **Continuous Monitoring**: OpenClaw hook integration for automated periodic scanning

## Features

### Multi-Engine Scanning

The scanner orchestrates four complementary scan types to provide comprehensive vulnerability coverage:

1. **Dependency Scanning**
   - Executes `npm audit --json` and `pip-audit -f json` as subprocesses
   - Parses structured output to extract CVE IDs, severity, affected versions
   - Handles edge cases: missing package-lock.json, zero vulnerabilities, malformed JSON

2. **CVE Database Queries**
   - **OSV API** (primary): Free, no authentication, broad ecosystem support (npm, PyPI, Go, Maven)
   - **NVD 2.0** (optional): Requires API key to avoid 6-second rate limiting
   - **GitHub Advisory Database** (optional): GraphQL API with OAuth token
   - Normalizes all API responses to unified `Vulnerability` schema

3. **Static Analysis (SAST)**
   - **Semgrep** for JavaScript/TypeScript: Detects security issues using `--config auto` or `--config p/security-audit`
   - **Bandit** for Python: Leverages existing `pyproject.toml` configuration
   - Identifies: hardcoded secrets (API keys, tokens), command injection (`eval`, `exec`), path traversal, unsafe deserialization

4. **Dynamic Analysis (DAST)**
   - Real hook execution harness for OpenClaw hook handlers discovered from `HOOK.md` metadata
   - Verifies: malicious input resilience, timeout behavior, output amplification bounds, and core event mutation safety
   - Note: Traditional web DAST tools (ZAP, Burp) do not apply to agent platforms - this provides agent-specific testing

### Unified Reporting

All scan types emit a consistent `ScanReport` JSON schema:

```typescript
{
  scan_id: string;         // UUID
  timestamp: string;       // ISO 8601
  target: string;          // Scanned path
  vulnerabilities: Vulnerability[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  }
}
```

Each `Vulnerability` object includes:
- `id`: CVE-2023-12345 or GHSA-xxxx-yyyy-zzzz
- `source`: npm-audit | pip-audit | osv | nvd | github | sast | dast
- `severity`: critical | high | medium | low | info
- `package`: Package name (or 'N/A' for SAST/DAST)
- `version`: Affected version
- `fixed_version`: First version with fix (if available)
- `title`: Short description
- `description`: Full advisory text
- `references`: URLs for more info
- `discovered_at`: ISO 8601 timestamp

### OpenClaw Integration

Automated continuous monitoring via hook:

- Runs scanner on configurable interval (default: 86400s / 24 hours)
- Triggers on `agent:bootstrap` and `command:new` events
- Posts findings to `event.messages` array with severity summary
- Rate-limited by `CLAWSEC_SCANNER_INTERVAL` environment variable

## Installation

### Prerequisites

Verify required binaries are available:

```bash
# Core runtimes
node --version  # v20+
npm --version
python3 --version  # 3.10+

# Scanning tools
pip-audit --version  # Install: uv pip install pip-audit
semgrep --version    # Install: pip install semgrep OR brew install semgrep
bandit --version     # Install: uv pip install bandit

# Utilities
jq --version
curl --version
```

### Option A: Via clawhub (recommended)

```bash
npx clawhub@latest install clawsec-scanner
```

### Option B: Manual installation with verification

```bash
set -euo pipefail

VERSION="${SKILL_VERSION:?Set SKILL_VERSION (e.g. 0.1.0)}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/.openclaw/skills}"
DEST="$INSTALL_ROOT/clawsec-scanner"
BASE="https://github.com/prompt-security/clawsec/releases/download/clawsec-scanner-v${VERSION}"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

# Pinned release-signing public key
# Fingerprint (SHA-256 of SPKI DER): 711424e4535f84093fefb024cd1ca4ec87439e53907b305b79a631d5befba9c8
cat > "$TEMP_DIR/release-signing-public.pem" <<'PEM'
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAS7nijfMcUoOBCj4yOXJX+GYGv2pFl2Yaha1P4v5Cm6A=
-----END PUBLIC KEY-----
PEM

ZIP_NAME="clawsec-scanner-v${VERSION}.zip"

# Download release archive + signed checksums
curl -fsSL "$BASE/$ZIP_NAME" -o "$TEMP_DIR/$ZIP_NAME"
curl -fsSL "$BASE/checksums.json" -o "$TEMP_DIR/checksums.json"
curl -fsSL "$BASE/checksums.sig" -o "$TEMP_DIR/checksums.sig"

# Verify checksums manifest signature
openssl base64 -d -A -in "$TEMP_DIR/checksums.sig" -out "$TEMP_DIR/checksums.sig.bin"
if ! openssl pkeyutl -verify \
  -pubin \
  -inkey "$TEMP_DIR/release-signing-public.pem" \
  -sigfile "$TEMP_DIR/checksums.sig.bin" \
  -rawin \
  -in "$TEMP_DIR/checksums.json" >/dev/null 2>&1; then
  echo "ERROR: checksums.json signature verification failed" >&2
  exit 1
fi

EXPECTED_SHA="$(jq -r '.archive.sha256 // empty' "$TEMP_DIR/checksums.json")"
if [ -z "$EXPECTED_SHA" ]; then
  echo "ERROR: checksums.json missing archive.sha256" >&2
  exit 1
fi

ACTUAL_SHA="$(shasum -a 256 "$TEMP_DIR/$ZIP_NAME" | awk '{print $1}')"
if [ "$EXPECTED_SHA" != "$ACTUAL_SHA" ]; then
  echo "ERROR: Archive checksum mismatch" >&2
  exit 1
fi

echo "Checksums verified. Installing..."

mkdir -p "$INSTALL_ROOT"
rm -rf "$DEST"
unzip -q "$TEMP_DIR/$ZIP_NAME" -d "$INSTALL_ROOT"

chmod 600 "$DEST/skill.json"
find "$DEST" -type f ! -name "skill.json" -exec chmod 644 {} \;

echo "Installed clawsec-scanner v${VERSION} to: $DEST"
echo "Next step: Run a scan or set up continuous monitoring"
```

## Usage

### On-Demand CLI Scanning

```bash
SCANNER_DIR="${INSTALL_ROOT:-$HOME/.openclaw/skills}/clawsec-scanner"

# Scan all skills with JSON output
"$SCANNER_DIR/scripts/runner.sh" --target ./skills/ --output report.json --format json

# Scan specific directory with human-readable output
"$SCANNER_DIR/scripts/runner.sh" --target ./my-skill/ --format text

# Check available flags
"$SCANNER_DIR/scripts/runner.sh" --help
```

**CLI Flags:**
- `--target <path>`: Directory to scan (required)
- `--output <file>`: Write results to file (optional, defaults to stdout)
- `--format <json|text>`: Output format (default: json)
- `--check`: Verify all required binaries are installed

### OpenClaw Hook Setup (Continuous Monitoring)

Enable automated periodic scanning:

```bash
SCANNER_DIR="${INSTALL_ROOT:-$HOME/.openclaw/skills}/clawsec-scanner"
node "$SCANNER_DIR/scripts/setup_scanner_hook.mjs"
```

This creates a hook that:
- Scans on `agent:bootstrap` and `command:new` events
- Respects `CLAWSEC_SCANNER_INTERVAL` rate limiting (default: 86400 seconds / 24 hours)
- Posts findings to conversation with severity summary
- Recommends remediation for high/critical vulnerabilities

Restart the OpenClaw gateway after enabling the hook, then run `/new` to trigger an immediate scan.

### Environment Variables

```bash
# Optional - NVD API key to avoid rate limiting (6-second delays without key)
export CLAWSEC_NVD_API_KEY="your-nvd-api-key"

# Optional - GitHub OAuth token for Advisory Database queries
export GITHUB_TOKEN="ghp_your_token_here"

# Optional - Scanner hook interval in seconds (default: 86400 / 24 hours)
export CLAWSEC_SCANNER_INTERVAL="86400"

# Optional - Allow unsigned advisory feed during development (from clawsec-suite)
export CLAWSEC_ALLOW_UNSIGNED_FEED="1"
```

## Architecture

### Modular Design

Each scan type is an independent module that can run standalone or as part of unified scan:

```
scripts/runner.sh              # Orchestration layer
├── scan_dependencies.mjs      # npm audit + pip-audit
├── query_cve_databases.mjs    # OSV/NVD/GitHub API queries
├── sast_analyzer.mjs          # Semgrep + Bandit static analysis
├── dast_runner.mjs            # Dynamic security testing orchestration
└── dast_hook_executor.mjs     # Isolated real hook execution harness

lib/
├── report.mjs                 # Result aggregation and formatting
├── utils.mjs                  # Subprocess exec, JSON parsing, error handling
└── types.ts                   # TypeScript schema definitions

hooks/clawsec-scanner-hook/
├── HOOK.md                    # OpenClaw hook metadata
└── handler.ts                 # Periodic scan trigger
```

### Fail-Open Philosophy

The scanner prioritizes availability over strict failure propagation:

- Network failures → emit partial results, log warnings
- Missing tools → skip that scan type, continue with others
- Malformed JSON → parse what's valid, log errors
- API rate limits → implement exponential backoff, fallback to other sources
- Zero vulnerabilities → emit success report with empty array

**Critical failures** that exit immediately:
- Target path does not exist
- No scanning tools available (all bins missing)
- Concurrent scan detected (lockfile present)

### Subprocess Execution Pattern

All external tools run as subprocesses with structured JSON output:

```javascript
import { spawn } from 'node:child_process';

// Example: npm audit execution
const proc = spawn('npm', ['audit', '--json'], {
  cwd: targetPath,
  stdio: ['ignore', 'pipe', 'pipe']
});

// Handle non-zero exit codes gracefully
// npm audit exits 1 when vulnerabilities found (not an error!)
proc.on('close', code => {
  if (code !== 0 && stderr.includes('ERR!')) {
    // Actual error
    reject(new Error(stderr));
  } else {
    // Vulnerabilities found or success
    resolve(JSON.parse(stdout));
  }
});
```

## Troubleshooting

### Common Issues

**"Missing package-lock.json" warning**
- `npm audit` requires lockfile to run
- Run `npm install` in target directory to generate
- Scanner continues with other scan types if npm audit fails

**"NVD API rate limit exceeded"**
- Set `CLAWSEC_NVD_API_KEY` environment variable
- Without API key: 6-second delays enforced between requests
- OSV API used as primary source (no rate limits)

**"pip-audit not found"**
- Install: `uv pip install pip-audit` or `pip install pip-audit`
- Verify: `which pip-audit`
- Add to PATH if installed in non-standard location

**"Semgrep binary missing"**
- Install: `pip install semgrep` OR `brew install semgrep`
- Requires Python 3.8+ runtime
- Alternative: use Docker image `returntocorp/semgrep`

**"TypeScript hook not executable in DAST harness"**
- The DAST harness executes real hook handlers and transpiles `handler.ts` files when a TypeScript compiler is available
- Install TypeScript in the scanner environment: `npm install -D typescript` (or provide `handler.js`/`handler.mjs`)
- Without a compiler, scanner reports an `info`-level coverage finding instead of a high-severity vulnerability

**"Concurrent scan detected"**
- Lockfile exists: `/tmp/clawsec-scanner.lock`
- Wait for running scan to complete or manually remove lockfile
- Prevents overlapping scans that could produce inconsistent results

### Verification

Check scanner is working correctly:

```bash
# Verify required binaries
./scripts/runner.sh --check

# Run unit tests
node test/dependency_scanner.test.mjs
node test/cve_integration.test.mjs
node test/sast_engine.test.mjs
node test/dast_harness.test.mjs

# Validate skill structure
python ../../utils/validate_skill.py .

# Scan test fixtures (should detect known vulnerabilities)
./scripts/runner.sh --target test/fixtures/ --format text
```

## Development

### Running Tests

```bash
# All tests (vanilla Node.js, no framework)
for test in test/*.test.mjs; do
  node "$test" || exit 1
done

# Individual test suites
node test/dependency_scanner.test.mjs  # Dependency scanning
node test/cve_integration.test.mjs     # CVE database APIs
node test/sast_engine.test.mjs         # Static analysis
node test/dast_harness.test.mjs        # DAST harness execution
```

### Linting

```bash
# JavaScript/TypeScript
npx eslint . --ext .ts,.tsx,.js,.jsx,.mjs --max-warnings 0

# Python (Bandit already configured in pyproject.toml)
ruff check .
bandit -r . -ll

# Shell scripts
shellcheck scripts/*.sh
```

### Adding Custom Semgrep Rules

Create custom rules in `.semgrep/rules/`:

```yaml
rules:
  - id: custom-security-rule
    pattern: dangerous_function($ARG)
    message: Avoid dangerous_function - use safe_alternative instead
    severity: WARNING
    languages: [javascript, typescript]
```

Update `scripts/sast_analyzer.mjs` to include custom rules:

```javascript
const proc = spawn('semgrep', [
  'scan',
  '--config', 'auto',
  '--config', '.semgrep/rules/',  // Add custom rules
  '--json',
  targetPath
]);
```

## Integration with ClawSec Suite

The scanner works standalone or as part of the ClawSec ecosystem:

- **clawsec-suite**: Meta-skill that can install and manage clawsec-scanner
- **clawsec-feed**: Advisory feed for malicious skill detection (complementary)
- **openclaw-audit-watchdog**: Cron-based audit automation (similar pattern)

Install the full ClawSec suite:

```bash
npx clawhub@latest install clawsec-suite
# Then use clawsec-suite to discover and install clawsec-scanner
```

## Security Considerations

### Scanner Security

- No hardcoded secrets in scanner code
- API keys read from environment variables only (never logged or committed)
- Subprocess arguments use arrays to prevent shell injection
- All external tool output parsed with try/catch error handling

### Vulnerability Prioritization

**Critical/High severity findings** should be addressed immediately:
- Known exploits in dependencies (CVSS 9.0+)
- Hardcoded API keys or credentials in code
- Command injection vulnerabilities
- Path traversal without validation

**Medium/Low severity findings** can be addressed in normal sprint cycles:
- Outdated dependencies without known exploits
- Missing security headers
- Weak cryptography usage

**Info findings** are advisory only:
- Deprecated API usage
- Code quality issues flagged by linters

## Roadmap

### v0.0.2 (Current)
- [x] Dependency scanning (npm audit, pip-audit)
- [x] CVE database integration (OSV, NVD, GitHub Advisory)
- [x] SAST analysis (Semgrep, Bandit)
- [x] Real OpenClaw hook execution harness for DAST
- [x] Unified JSON reporting
- [x] OpenClaw hook integration

### Future Enhancements
- [ ] Automatic remediation (dependency upgrades, code fixes)
- [ ] SARIF output format for GitHub Code Scanning integration
- [ ] Web dashboard for vulnerability tracking over time
- [ ] CI/CD GitHub Action for PR blocking on high-severity findings
- [ ] Container image scanning (Docker, OCI)
- [ ] Infrastructure-as-Code scanning (Terraform, CloudFormation)
- [ ] Comprehensive agent workflow DAST (requires deeper platform integration)

## Contributing

Found a security issue? Please report privately to security@prompt.security.

For feature requests and bug reports, open an issue at:
https://github.com/prompt-security/clawsec/issues

## License

AGPL-3.0-or-later

See LICENSE file in repository root for full text.

## Resources

- **ClawSec Homepage**: https://clawsec.prompt.security
- **Documentation**: https://clawsec.prompt.security/scanner
- **GitHub Repository**: https://github.com/prompt-security/clawsec
- **OSV API Docs**: https://osv.dev/docs/
- **NVD API Docs**: https://nvd.nist.gov/developers/vulnerabilities
- **Semgrep Registry**: https://semgrep.dev/explore
- **Bandit Documentation**: https://bandit.readthedocs.io/
