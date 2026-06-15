# Security Analysis: Tide Watch

> **⚠️ OUTDATED:** This analysis is from v1.0.0 (pre-release). See [SECURITY-ASSESSMENT-v1.1.0.md](./SECURITY-ASSESSMENT-v1.1.0.md) for current security assessment.

**Date:** 2026-02-23  
**Analyst:** Navi (OpenClaw AI Assistant)  
**Reference:** [ClawHub Security Prompt](https://github.com/openclaw/clawhub/blob/9c31462f15ebadd7e808b3b32b23a518e8f1edc1/convex/lib/securityPrompt.ts)

---

## Executive Summary

**Verdict:** ✅ **BENIGN**  
**Confidence:** 🟢 **HIGH**

Tide Watch is an instruction-only monitoring skill with perfect alignment between its stated purpose and actual capabilities. It requests zero system access beyond OpenClaw's built-in `session_status` tool, has no install mechanism, and stays strictly within its monitoring scope.

---

## Five-Dimension Analysis

### 1. Purpose–Capability Alignment

**Status:** ✅ **OK**

**Claimed purpose:**
> "Proactive session capacity monitoring for OpenClaw. Get warned at 75%, 85%, 90%, and 95% capacity thresholds before context windows overflow."

**What it actually requests/requires:**
- **Binaries:** None
- **Environment variables:** None
- **Config paths:** None
- **Install mechanism:** None (instruction-only)
- **Dependencies:** Uses only OpenClaw's built-in `session_status` tool

**Assessment:**
Perfect alignment. A monitoring skill that *only monitors* is exactly what you'd expect. No disproportionate requests, no unrelated capabilities, no scope creep.

---

### 2. Instruction Scope

**Status:** ✅ **OK**

**What the instructions tell the agent to do:**
1. Check `session_status` approximately once per hour
2. Calculate capacity percentage (tokens_used / tokens_max)
3. Compare against thresholds (75%, 85%, 90%, 95%)
4. Issue warnings when thresholds are crossed
5. Suggest actions:
   - Save context to `memory/YYYY-MM-DD.md`
   - Switch to lower-usage channels
   - Back up session files (user's own files)
   - Generate session resumption prompts

**Scope boundaries:**
- ✅ All actions relate directly to session monitoring
- ✅ File operations limited to user's workspace (`memory/` folder, session backups)
- ✅ No external data transmission
- ✅ No credential access
- ✅ No system-wide file reads
- ✅ No command execution beyond built-in OpenClaw tools

**Assessment:**
Instructions stay strictly within the stated purpose. The skill helps users manage their own session data without accessing anything outside the session management domain.

---

### 3. Install Mechanism Risk

**Status:** ✅ **OK** (lowest risk)

**Install spec:** None  
**Code files:** None  
**Type:** Instruction-only skill

**Risk assessment:**
- Nothing is written to disk
- No binaries created
- No external downloads
- No archive extraction
- No executable code

**Assessment:**
Zero risk from install mechanism. This is the safest possible skill type—pure instructions with no code execution.

---

### 4. Environment and Credential Proportionality

**Status:** ✅ **OK**

**Requested environment variables:** None  
**Requested config paths:** None  
**Primary credential:** None  
**Credential access in instructions:** None

**Assessment:**
Perfect proportionality. A monitoring tool that checks publicly available session status needs zero credentials. The skill accesses only what OpenClaw already exposes through the `session_status` tool.

---

### 5. Persistence and Privilege

**Status:** ✅ **OK**

**Privilege flags:**
- `always: true` → Not set (no force-inclusion)
- `disable-model-invocation` → Not set (model can invoke)
- `user-invocable` → Not set (default)

**System presence:** Normal eligibility, triggered only when relevant

**Assessment:**
No privilege escalation. The skill does not request permanent presence, does not bypass eligibility gates, and does not require special system access. It follows the standard skill lifecycle.

**Note on model invocation:**
The skill is model-invocable (can be triggered autonomously), but this is appropriate for a monitoring tool. The agent needs to check capacity proactively. Since the skill has zero external access and only reads session state, autonomous invocation poses no risk.

---

## Static Scan Findings

**Injection patterns detected:** None  
**Code files present:** None (instruction-only)  
**Regex scan results:** N/A (no code to scan)

---

## Threat Model Analysis

### What could go wrong?

**Scenario 1: Excessive warnings**
- **Risk:** Skill warns too frequently, annoying the user
- **Severity:** Low (UX issue, not security issue)
- **Mitigation:** Configurable thresholds (issue #11)

**Scenario 2: Memory file bloat**
- **Risk:** Repeated context saves fill `memory/` folder
- **Severity:** Low (user's own workspace)
- **Mitigation:** User controls what gets saved

**Scenario 3: Session backup disk usage**
- **Risk:** Automatic backups (future feature) consume disk space
- **Severity:** Low (user's own session files)
- **Mitigation:** Retention policies, compression (issue #2)

**Scenario 4: Malicious AGENTS.md modification**
- **Risk:** Attacker modifies threshold logic in user's AGENTS.md
- **Severity:** Medium (requires filesystem access)
- **Mitigation:** Out of scope—if attacker has write access to AGENTS.md, they already control the agent

### What can't go wrong?

- ✅ **No credential theft** — skill requests no credentials
- ✅ **No data exfiltration** — no external network access in instructions
- ✅ **No code execution** — instruction-only, no binaries
- ✅ **No privilege escalation** — no `always: true`, no special access
- ✅ **No filesystem tampering** — only writes to user's workspace (`memory/`)

---

## Comparison to Known Patterns

### Similar benign skills:
- `session-logs`: Logs session activity (reads session state)
- `healthcheck`: Monitors system health (reads status)
- `memory_search`: Searches user's memory files (reads workspace)

### Pattern match:
Tide Watch follows the same safe pattern: read-only access to OpenClaw's built-in state, write-only access to user's own workspace, no external dependencies.

---

## User Guidance

**Plain-language summary:**

> Tide Watch monitors how full your conversation sessions are getting and warns you before they max out. It's like a fuel gauge for your AI's memory.
>
> **What it can access:** Only the session status that OpenClaw already shows you (token counts, percentages).
>
> **What it can do:** Write reminders to your workspace memory folder, help you back up conversations before resetting.
>
> **What it cannot do:** Read your files outside the workspace, access credentials, send data anywhere, or run code on your system.
>
> **Bottom line:** This is an instruction-only monitoring tool with zero external access. Installing it is like adding a reminder system—it helps you manage your own data without touching anything sensitive.

---

## Recommendations

### For v1.0.0 release:
- ✅ **Approve for publication** — skill is benign with high confidence
- ✅ **No changes required** — current implementation is secure

### For future enhancements:
- ⚠️ **Issue #2 (Auto-backup):** When implementing automatic backups, ensure:
  - Backups stay in user's session folder (no external writes)
  - Retention policies prevent disk bloat
  - User can disable auto-backup
  
- ⚠️ **Issue #5 (Heartbeat integration):** Ensure heartbeat checks don't:
  - Execute with elevated privileges
  - Access data outside the monitoring scope
  - Bypass normal tool policies

- ⚠️ **Issue #6 (Notifications):** If external notifications are added:
  - Require explicit user configuration (email, webhooks)
  - Never send credentials or session content
  - Validate notification endpoints

---

## Conclusion

**Tide Watch passes security review for v1.0.0 publication.**

The skill is internally coherent, requests no disproportionate access, stays within its stated purpose, and follows OpenClaw's security best practices. It represents the safest skill type: instruction-only, read-only access to built-in tools, write-only access to user's workspace.

**Verdict:** BENIGN  
**Confidence:** HIGH  
**Cleared for ClawHub publication:** YES ✅

---

**Next step:** Complete functional testing (issue #10, checklist items 2-6)
