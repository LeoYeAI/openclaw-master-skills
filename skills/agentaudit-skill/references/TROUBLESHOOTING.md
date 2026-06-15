# Troubleshooting Guide

Common issues and edge cases when using AgentAudit.

## Error Handling & Edge Cases

| Situation | Behavior | Rationale |
|-----------|----------|-----------|
| API down (timeout, 5xx) | **Default-warn** (exit 2). Agent pauses, shows warning: "AgentAudit API unreachable. Cannot verify package safety. Retry in 5 minutes or proceed at your own risk?" Package is NOT auto-installed. | Security over convenience |
| Upload fails (network error) | Retry once. If still fails, save report to `reports/<package>-<date>.json` locally. Warn user. | Don't lose audit work |
| Hash mismatch | **Hard stop.** But note: could be a legitimate update if package version changed since last audit. Check if version differs → if yes, re-audit. If same version → likely tampered. | Version-aware integrity |
| Rate limited (HTTP 429) | Wait 2 minutes, retry. If still limited, save locally and upload later. | Respect API limits |
| No internet | Warn user: "No network access. Cannot verify against AgentAudit registry. Proceeding without verification — use caution." Let user decide. | Never silently skip security |
| Large packages (500+ files) | Focus audit on: (1) entry points, (2) install/build scripts, (3) config files, (4) files with `eval`/`exec`/`spawn`/`system`. Skip docs, tests, assets. | Practical time management |
| `jq` or `curl` not installed | Scripts will fail with clear error. Inform user: "Required tool missing: install jq/curl first." | Documented dependency |
| `credentials.json` corrupt | Delete and re-register: `rm config/credentials.json && bash scripts/register.sh <name>` | Clean recovery |

## Installation Issues

### Skill not loading

**Checklist:**
- ✅ Did you restart your editor completely? (not just reload)
- ✅ Check frontmatter has `---` delimiters
- ✅ Verify directory name matches `name:` field in frontmatter

### "bash: scripts/gate.sh: No such file or directory"

**Solutions:**
- ✅ Use absolute paths: `bash ~/.claude/skills/agentaudit/scripts/gate.sh npm express`
- ✅ Or change to skill directory first: `cd ~/.claude/skills/agentaudit && bash scripts/gate.sh npm express`
- ✅ Verify you cloned the full repo, not just SKILL.md

### "jq: command not found" or "curl: command not found"

**Install required tools:**

**macOS:**
```bash
brew install jq  # curl/bash pre-installed
```

**Ubuntu/Debian/WSL:**
```bash
sudo apt-get update && sudo apt-get install -y curl jq
```

**Fedora/RHEL:**
```bash
sudo dnf install -y curl jq
```

**Windows:**
Use [WSL](https://learn.microsoft.com/windows/wsl/install) or [Git Bash](https://git-scm.com/download/win)

## API Issues

### Authentication failures

If you get 401 errors:

1. Check if credentials exist:
   ```bash
   cat config/credentials.json
   ```

2. Re-register if needed:
   ```bash
   bash scripts/register.sh your-agent-name
   ```

3. Or set environment variable:
   ```bash
   export AGENTAUDIT_API_KEY="your-key-here"
   ```

### Rate limiting (429 errors)

If you hit rate limits:
- Wait 2 minutes before retrying
- Save reports locally: `reports/<package>-<date>.json`
- Upload later when limits reset

### Network connectivity

If API is unreachable:
- Check internet connection
- Verify firewall settings
- Try manual curl: `curl -s https://agentaudit.dev/api/health`
- Consider using manual pre-checks before running gate script

## Verification Issues

### Hash mismatch errors

When integrity check fails:

1. Check if package version changed:
   ```bash
   # Compare local version to audited version
   ```

2. If same version → likely tampered, DO NOT PROCEED

3. If different version → needs re-audit

### Unknown package (exit code 3)

This is NOT an error - it means no audit data exists yet.

**Required actions:**
1. Warn the user explicitly
2. Check red flags (age, downloads, author, typosquat)
3. Require explicit user confirmation
4. Trigger auto-audit if user confirms

See SKILL.md "Exit Code 3 — The Audit Gap" section for full guidance.

## Performance Issues

### Large packages taking too long

For packages with 500+ files:

**Focus on:**
1. Entry points (main, index files)
2. Install/build scripts
3. Config files
4. Files containing `eval`/`exec`/`spawn`/`system`

**Skip:**
- Documentation
- Tests
- Assets (images, fonts, etc.)

### Slow API responses

If API calls are slow:
- Check network latency
- Consider caching results locally
- Use integrity checks to avoid redundant full audits
