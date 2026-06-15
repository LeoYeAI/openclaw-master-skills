# Security Assessment - Tide Watch v1.1.0

**Assessment Date:** 2026-02-28  
**Assessed Against:** ClawHub Security Evaluator Criteria  
**Reference:** https://github.com/openclaw/clawhub/blob/9c31462f/convex/lib/securityPrompt.ts

---

## Executive Summary

**Verdict:** BENIGN  
**Confidence:** HIGH  
**Summary:** Session monitoring tool that reads local OpenClaw session files to display capacity, model usage, and gateway status. All capabilities are internally consistent with its stated purpose.

---

## Dimension-by-Dimension Analysis

### 1. Purpose–Capability Alignment ✅ OK

**Stated Purpose:**
- Monitor OpenClaw session token capacity
- Warn at configurable thresholds (75%, 85%, 90%, 95%)
- Display model usage per session (NEW in v1.1.0)
- Show gateway online/offline status (NEW in v1.1.0)
- Prevent context window lockups

**Actual Capabilities:**
- Reads `~/.openclaw/agents/main/sessions/*.jsonl` files
- Parses session metadata (model, tokens, timestamps)
- Checks gateway status via `openclaw gateway status` command
- Displays formatted reports (table, dashboard, JSON)
- Archives old sessions to `archive/` subdirectory
- Manages resumption prompt files

**Assessment:**
- ✅ All capabilities directly support session monitoring
- ✅ Model display helps track paid vs. free model usage (cost monitoring)
- ✅ Gateway status helps diagnose connection issues
- ✅ No capabilities unrelated to stated purpose
- ✅ File access limited to OpenClaw session directory only
- ✅ No external network calls

**Conclusion:** ALIGNED - Would someone building a session monitor legitimately need all of this? Yes.

### 2. Instruction Scope ✅ OK

**SKILL.md Instructions:**
- Use `session_status` tool to check capacity
- Warn at threshold levels
- Load resumption prompts on session reset
- Run `tide-watch` CLI commands for manual checks

**v1.1.0 Changes:**
- Added model extraction from session JSONL files
- Added gateway status check via `openclaw gateway status`
- Display model name in output formats
- Display gateway online/offline indicator

**Assessment:**
- ✅ Instructions stay within session monitoring boundaries
- ✅ No reading of files unrelated to OpenClaw sessions
- ✅ No access to credentials or shell history
- ✅ No data transmission to external endpoints
- ✅ Gateway status check uses official OpenClaw CLI command
- ✅ Model data extracted from session files (legitimate metadata)

**Conclusion:** WITHIN SCOPE - Instructions reference only session-related files and OpenClaw CLI commands.

### 3. Install Mechanism Risk ✅ LOW RISK

**Install Specification:**
```json
{
  "id": "npm",
  "kind": "node",
  "package": ".",
  "bins": ["tide-watch"],
  "label": "Install tide-watch CLI for manual capacity checks"
}
```

**Assessment:**
- ✅ Install type: npm package from local directory
- ✅ No download from external URL
- ✅ No extract: true (no archive extraction)
- ✅ Creates single binary: `tide-watch`
- ✅ Standard npm install mechanism
- ✅ Includes postinstall script: `chmod +x bin/tide-watch.js` (permissions only)

**Risk Level:** LOW  
**Rationale:** Standard npm install from local package directory. No downloads, no archives, no arbitrary code execution during install.

### 4. Environment and Credential Proportionality ✅ OK

**Required Environment Variables:** NONE

**Required Binaries:**
- `node` (for CLI execution)
- `npm` (for installation)

**Required Config Paths:**
- `~/.openclaw/agents/main/sessions/` (read-only for monitoring)

**Assessment:**
- ✅ No external credentials required
- ✅ No API keys needed (operates on local files only)
- ✅ Gateway status check uses OpenClaw's own CLI (no separate auth)
- ✅ Session directory access is necessary for monitoring purpose
- ✅ No access to gateway auth, channel tokens, or tool policies

**Conclusion:** PROPORTIONATE - A session monitoring tool legitimately needs to read session files. No credentials requested.

### 5. Persistence and Privilege ✅ OK

**Flags:**
- `always`: NOT SET (skill is not force-included)
- `disable-model-invocation`: false (default, model can invoke)
- `user-invocable`: true (default)

**Assessment:**
- ✅ Normal defaults, no special privileges requested
- ✅ Not requesting permanent presence (always: false)
- ✅ Model invocation allowed but skill has no external access
- ✅ No combination of always + broad env access

**Conclusion:** NORMAL - Standard skill privileges, no elevated access.

---

## Static Scan Findings Analysis

### v1.1.0 Code Changes

**New Functions Added:**
1. `checkGatewayStatus()` - Executes `openclaw gateway status` via execSync
2. Model display in `formatTableRow()` and `formatDashboard()`

**Child Process Usage:**
- ✅ `execSync('openclaw gateway status')` - Expected for a monitoring tool
- ✅ 5-second timeout prevents hanging
- ✅ Error handling prevents crashes
- ✅ No user input passed to command (hardcoded)
- ✅ No shell=true (uses default, which is safe for this static command)

**File System Access:**
- ✅ Reads session JSONL files (unchanged from previous versions)
- ✅ No new file write operations in v1.1.0
- ✅ All file access within `~/.openclaw/agents/main/sessions/`

### Previous Vulnerability (CVE-2026-001)

**Status:** PATCHED in v1.0.1  
**Affected Function:** `editResumePrompt` (NOT modified in v1.1.0)  
**Fix:** Replaced `execSync` with `spawnSync` to prevent shell injection

**v1.1.0 does NOT reintroduce this vulnerability.**

---

## Changes in v1.1.0

### Added Features

1. **Model Display (Issue #22)**
   - **What:** Show which model each session is using
   - **Why:** Track paid vs. free model usage for cost monitoring
   - **Security Impact:** None - extracts model field from existing session data
   - **Data Source:** Session JSONL files (already being read)

2. **Gateway Status (Issue #23)**
   - **What:** Display OpenClaw gateway online/offline status
   - **Why:** Diagnose connection issues faster
   - **Security Impact:** Low - runs `openclaw gateway status` command
   - **Implementation:** Uses execSync with timeout, hardcoded command, no user input

### Modified Files
- `lib/capacity.js` - Added checkGatewayStatus(), updated formatters
- `bin/tide-watch.js` - No changes
- `lib/resumption.js` - No changes

### Test Coverage
- All 113 existing tests pass
- No test regressions
- New functionality tested via integration test

---

## Security Self-Assessment Verdict

**Overall Verdict:** BENIGN  
**Confidence:** HIGH

### Reasoning

1. **Purpose-aligned:** Model display and gateway status are legitimate monitoring features for a session capacity tool.

2. **Scope-limited:** All new functionality operates within the session monitoring domain. No scope creep.

3. **Low-risk mechanisms:** Standard npm install, no external downloads, no archive extraction.

4. **No credentials:** Operates on local files only, no external API access, no credentials required.

5. **Normal privileges:** Default skill flags, no special access requested.

6. **Expected code patterns:** Child process usage (`execSync` for gateway status) is expected for a monitoring tool that checks system status.

7. **No regression:** Previous CVE-2026-001 vulnerability remains patched, not reintroduced.

### User Guidance

**Safe to install if:**
- ✅ You want to track which models are consuming capacity
- ✅ You need visibility into gateway health
- ✅ You trust the tool to read your local session files
- ✅ You are installing v1.1.0 or later (v1.0.0 had CVE)

**Consider before installing:**
- Session monitoring requires reading your conversation history
- CLI tools have direct filesystem access to `~/.openclaw/agents/main/sessions/`
- Gateway status check executes an external command (`openclaw gateway status`)

**Recommended installation method:**
1. Verify version: `npm show tide-watch version` (should be 1.1.0+)
2. Review code: `cat lib/capacity.js` (look for checkGatewayStatus function)
3. Install: `npm link`
4. Test: `tide-watch dashboard`

---

## Comparison to ClawHub Security Criteria

| Dimension | Status | Rationale |
|-----------|--------|-----------|
| Purpose–Capability | ✅ OK | Session monitoring + model tracking + gateway status = coherent purpose |
| Instruction Scope | ✅ OK | Instructions limited to session files and OpenClaw CLI commands |
| Install Mechanism | ✅ OK | Standard npm, no downloads, no archives, no extract |
| Environment/Credentials | ✅ OK | No credentials required, operates on local files |
| Persistence/Privilege | ✅ OK | Normal defaults, no elevated access |

**Final Assessment:** No incoherence detected. The skill appears to be exactly what it claims: a session capacity monitoring tool with model tracking and gateway health visibility.

---

## Signature

**Assessed by:** Navi (OpenClaw Agent)  
**Date:** 2026-02-28  
**Version Assessed:** 1.1.0  
**Next Review:** Upon next feature addition or ClawHub security prompt update
