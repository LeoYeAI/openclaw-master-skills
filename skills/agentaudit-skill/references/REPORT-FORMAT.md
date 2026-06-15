# Report JSON Format

Complete specification for audit report JSON structure.

## Minimal Report (Backend Auto-Enriches)

```json
{
  "skill_slug": "example-package",
  "source_url": "https://github.com/owner/repo",
  "risk_score": 8,
  "result": "safe",
  "findings_count": 1,
  "findings": [...]
}
```

## Complete Report Example

```json
{
  "skill_slug": "example-package",
  "source_url": "https://github.com/owner/repo",
  "commit_sha": "a1b2c3d4...",
  "package_version": "1.0.0",
  "content_hash": "9f8e7d6c...",
  "risk_score": 75,
  "result": "unsafe",
  "findings_count": 1,
  "findings": [
    {
      "severity": "critical",
      "pattern_id": "CMD_INJECT_001",
      "title": "Shell injection via unsanitized input",
      "description": "User input is passed directly to child_process.exec() without sanitization",
      "file": "src/runner.js",
      "file_hash": "a7b3c8d9...",
      "line": 42,
      "content": "exec(`npm install ${userInput}`)",
      "confidence": "high",
      "remediation": "Use execFile() with an args array instead of string interpolation",
      "by_design": false,
      "score_impact": -25,
      "component_type": "plugin"
    }
  ]
}
```

## Required Fields

### Top-Level (Required)

- **`skill_slug`** (string): Package name (e.g., "express", "mcp-server-fetch"). Also accepts `package_name` alias.
- **`source_url`** (string, **REQUIRED**): Public URL to package source (GitHub, GitLab, npm, PyPI). **Mandatory** for public registry. Enables peer review, fixes, and verification.
  - Examples: `https://github.com/owner/repo`, `https://www.npmjs.com/package/name`
- **`risk_score`** (integer, 0-100): Sum of absolute penalties from real findings (by_design excluded)
- **`result`** (string): One of `safe` (0-25), `caution` (26-50), or `unsafe` (51-100). **Do NOT use** `clean`, `pass`, or `fail`.
- **`findings_count`** (integer): Total number of findings
- **`findings`** (array): Array of finding objects (can be empty)

### Optional (Backend Auto-Enriches)

- **`commit_sha`** (string, optional): Git commit hash. Backend extracts via `git rev-parse HEAD` if not provided.
- **`package_version`** (string, optional): Version number. Backend extracts from package.json, setup.py, pyproject.toml, or git tags.
- **`content_hash`** (string, recommended): SHA-256 of all files. Backend recomputes for verification.
  ```bash
  find . -type f ! -path '*/\.git/*' -exec sha256sum {} + | sort | sha256sum | cut -d' ' -f1
  ```

## Finding Object Structure

### Required per Finding

- **`severity`**: `critical`, `high`, `medium`, or `low`
- **`pattern_id`**: Pattern identifier (e.g., `CMD_INJECT_001`). See [DETECTION-PATTERNS.md](DETECTION-PATTERNS.md)
- **`title`**: Brief description (1-10 words)
- **`description`**: Detailed explanation (1-3 sentences)
- **`file`**: Relative path to affected file
- **`line`**: Line number where issue found
- **`content`**: Exact code snippet
- **`confidence`**: `high` (certain), `medium` (likely), or `low` (suspicious)
- **`remediation`**: Specific fix suggestion
- **`by_design`**: Boolean. `true` = expected pattern for package category, `score_impact: 0`. Default: `false`.
- **`score_impact`**: Penalty applied. By-design: `0`. Real: critical `-25`, high `-15`, medium `-8`, low `-3` (×1.2 for high-risk components)

### Optional per Finding

- **`file_hash`** (string, recommended): SHA-256 of specific file. Enables precise staleness detection.
  ```bash
  sha256sum path/to/file.js | cut -d' ' -f1
  ```
  `upload.sh` auto-calculates if omitted.
- **`component_type`** (string): Component type for risk weighting. Values: `hook`, `skill`, `agent`, `mcp`, `settings`, `plugin`, `docs`, `test`.

## Severity Classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Exploitable now, immediate damage | `curl URL \| bash`, `rm -rf /`, env exfiltration, `eval` on raw input |
| **High** | Significant risk under realistic conditions | `eval()` on partial input, base64-decoded commands, system file modification |
| **Medium** | Risk under specific circumstances | Hardcoded API keys, HTTP for credentials, overly broad permissions |
| **Low** | Best-practice violation, no direct exploit | Missing validation, verbose errors, deprecated APIs |

## Pattern ID Prefixes

Use prefixes: `CMD_INJECT`, `CRED_THEFT`, `DATA_EXFIL`, `DESTRUCT`, `OBF`, `SANDBOX_ESC`, `SUPPLY_CHAIN`, `SOCIAL_ENG`, `PRIV_ESC`, `INFO_LEAK`, `CRYPTO_WEAK`, `DESER`, `PATH_TRAV`, `SEC_BYPASS`, `PERSIST`, `AI_PROMPT`, `CORR`, `MCP_*`, `MANUAL`.

Full list: [DETECTION-PATTERNS.md](DETECTION-PATTERNS.md)

## Field Notes

- **`confidence`**: `high` = certain, `medium` = likely, `low` = suspicious
- **`risk_score`**: 0-25 safe, 26-50 caution, 51-100 unsafe
- **`component_type`**: Used for ×1.2 penalty multiplier on high-risk components

## Upload

```bash
bash scripts/upload.sh report.json
```

Backend automatically:
- Extracts `commit_sha` if Git repo
- Extracts `package_version` from package metadata
- Calculates `content_hash` for integrity verification
- Calculates `file_hash` for each finding if omitted
