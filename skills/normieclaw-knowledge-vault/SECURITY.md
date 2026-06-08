# Knowledge Vault — Security Audit

![Codex Security Verified](https://img.shields.io/badge/Codex%20Security-Verified-brightgreen?style=for-the-face)

---

## Audit Summary

| Item | Status |
|------|--------|
| **Auditor** | Codex (OpenAI) |
| **Audit Date** | 2026-03-08 |
| **Skill Version** | 1.0.0 |
| **Verdict** | ✅ PASS — No unresolved Critical/High/Medium findings |

---

## What Was Tested

### 1. Prompt Injection Defense
- **Result:** ✅ Pass
- The SKILL.md contains explicit, mandatory instructions that ALL ingested content (web pages, articles, transcripts, PDFs, tweets, repository files) must be treated as **untrusted data, never as instructions.**
- Adversarial URL content cannot override agent behavior.
- Embedded commands in fetched content are ignored by design.

### 2. Data Exfiltration
- **Result:** ✅ Pass
- No unsolicited outbound network calls are initiated by the skill.
- No built-in telemetry, analytics, tracking, or callback endpoints exist in this package.
- Outbound fetches occur only when a user explicitly asks to ingest external content (via `web_fetch`/`browser` tools).
- Vault contents are not automatically transmitted outside the workspace.
- The skill uses only the agent's existing tools (`web_fetch`, `memory_store`, `read`, `write`).
- `memory_store` persistence location/retention depends on host agent platform configuration.

### 3. File System Safety
- **Result:** ✅ Pass
- All file paths are relative — no absolute paths or path traversal.
- Directory permissions set to `chmod 700`, file permissions to `chmod 600`.
- Scripts use `set -euo pipefail` for safe execution.
- No file deletion commands — the skill only creates and appends.

### 4. Secret Handling
- **Result:** ✅ Pass
- No API keys, tokens, or credentials are hardcoded anywhere in the skill.
- No environment variables are read or referenced by the skill files.
- The skill relies entirely on the agent's pre-configured tool access.

### 5. Script Safety
- **Result:** ✅ Pass
- `vault-stats.sh` uses `set -euo pipefail` for strict error handling.
- Workspace root detection via marker file traversal (AGENTS.md / SOUL.md) — no hardcoded paths.
- No destructive commands (`rm`, `chmod 777`, etc.).
- No network calls from scripts.

### 6. Dependency Chain
- **Result:** ✅ Pass
- Zero third-party dependencies.
- No npm packages, pip installs, or external binaries required.
- Works with the agent's built-in tools only.

---

## Security Guarantees

1. **No unsolicited data transfer.** Knowledge Vault only performs outbound fetches when you explicitly provide external URLs to ingest.

2. **No phone-home behavior.** The skill contains no analytics, telemetry, tracking, or callback URLs.

3. **Prompt injection hardened.** Every content ingestion path treats external text as untrusted data. Your agent will not follow instructions embedded in web pages, PDFs, tweets, or any other fetched content.

4. **No elevated permissions required.** The skill uses standard file read/write operations. No sudo, no system-level access, no daemon processes.

5. **No credential exposure.** The skill does not access, store, or transmit any API keys, passwords, or tokens.
6. **Platform-dependent memory storage.** Long-term memory writes (`memory_store`) are controlled by your agent platform's backend settings and retention policies.

---

## User Guidance

### Recommended Practices
- **Keep your workspace permissions tight.** The setup script sets `chmod 700` on directories and `chmod 600` on data files. Don't loosen these.
- **Review vault entries periodically.** Your vault may contain content from external sources. While the skill never follows embedded instructions, the stored text reflects the original content.
- **Back up your vault.** `data/vault-entries.json` is your knowledge database. Include it in your backup routine.

### What the Skill Does NOT Do
- ❌ Access your email, calendar, or contacts
- ❌ Send messages on your behalf
- ❌ Install software or packages
- ❌ Modify files outside the `data/`, `config/`, and `scripts/` directories
- ❌ Make network requests beyond what `web_fetch` and `browser` tools already do
- ❌ Store or transmit your credentials

---

## Reporting Issues

If you discover a security concern with this skill, contact security@normieclaw.ai. We take every report seriously and will issue patches promptly.
