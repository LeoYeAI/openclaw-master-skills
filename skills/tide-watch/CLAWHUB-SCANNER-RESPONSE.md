# ClawHub Scanner Response - Tide Watch

**Date:** 2026-02-24  
**Scan Result:** Suspicious (medium confidence)  
**Response:** Complete clarification of architecture and code

---

## Scanner Concerns Addressed

### 1. ✅ Documentation/Code Mismatch (PRIMARY CONCERN)

**Scanner finding:**
> "SECURITY-ANALYSIS.md and parts of SKILL.md describe the skill as 'instruction-only' with 'no code files', but the manifest includes lib/*.js, examples, tests, and a package.json"

**Response:** **VALID CONCERN** - Documentation has been corrected.

**Clarification:**
- Tide Watch is a **HYBRID SKILL** with two components:
  1. AGENTS.md directives (runtime instructions for automatic monitoring)
  2. Optional Node.js CLI tool (for manual capacity checks)
- Earlier versions of SECURITY-SCAN.md incorrectly used "instruction-only" terminology
- This was a documentation error, not a security issue
- **Fixed in commit 3d57c85** (2026-02-24)

**Code files present:**
```
bin/tide-watch          # CLI entry point (Node.js)
lib/capacity.js         # Session parsing and calculations
lib/resumption.js       # Resumption prompt management
tests/*.js              # Test suite (113 passing tests)
package.json            # npm manifest
```

**No code is hidden or obfuscated.** All files are human-readable JavaScript.

---

### 2. ✅ Install Mechanism Ambiguity

**Scanner finding:**
> "There is no formal install spec in the skill metadata (install: none), yet README describes npm link"

**Response:** **VALID CONCERN** - Install process clarified below.

**Two-tier installation model:**

**Tier 1: Basic Monitoring (No Code Execution)**
```bash
# Copy directives to workspace AGENTS.md
cat skills/tide-watch/AGENTS.md.template >> ~/clawd/AGENTS.md

# Optional: Add heartbeat task
cat skills/tide-watch/HEARTBEAT.md.template >> ~/clawd/HEARTBEAT.md
```
- No code execution
- No npm packages installed
- Pure directive-based monitoring
- Agent reads session files directly using built-in tools

**Tier 2: CLI Tools (Optional - Requires Node.js)**
```bash
# Clone repository
git clone https://github.com/chrisagiddings/openclaw-tide-watch ~/clawd/skills/tide-watch

# Optional: Link CLI globally
cd ~/clawd/skills/tide-watch
npm link  # Creates global tide-watch command
```
- Executable code installed (lib/*.js, bin/tide-watch)
- Requires Node.js runtime
- **Users should inspect code before linking** (standard practice)

**Why no formal install spec?**
- Basic monitoring works without any code installation
- CLI tool is optional enhancement
- User controls when/if to run npm link
- This gives users maximum transparency and control

---

### 3. ✅ Network Activity

**Scanner concern:**
> "Verify the code doesn't already implement outbound network calls"

**Response:** **Code verified - Zero network activity.**

**Verification:**
```bash
# Search for network-related modules
grep -r "require.*http\|require.*net\|require.*axios\|require.*fetch" lib/ bin/
# Result: No matches

# Search for child_process curl/wget
grep -r "child_process\|exec.*curl\|exec.*wget" lib/ bin/
# Result: No matches

# Search for network keywords
grep -r "http://\|https://\|fetch(\|axios\|net\.connect" lib/ bin/
# Result: No matches
```

**All operations are local:**
- Read: `~/.openclaw/agents/main/sessions/*.jsonl`
- Write: `~/.openclaw/agents/main/sessions/resume-prompts/*.md`
- Write: `~/.openclaw/agents/main/sessions/archive/*/`
- No external API calls
- No data exfiltration
- No phone-home behavior

**Future features (not yet implemented):**
- README mentions potential future notifications (Discord/email)
- These are NOT implemented in v1.0.0
- Will be opt-in if added in future versions

---

### 4. ✅ Environment Variables & File Access

**Scanner concern:**
> "Verify that the code doesn't opportunistically read other paths or environment variables at runtime"

**Response:** **Code verified - Restricted access only.**

**Environment variables accessed:**
```javascript
// lib/capacity.js:11-12
const DEFAULT_SESSION_DIR = path.join(
  os.homedir(),
  '.openclaw',
  'agents',
  'main',
  'sessions'
);
```
- Only reads `HOME` environment variable (via `os.homedir()`)
- Used solely to construct path to OpenClaw sessions directory
- No other environment variables accessed

**File system access:**
```javascript
// Read access
~/.openclaw/agents/main/sessions/*.jsonl           // Session files
~/.openclaw/agents/main/sessions/sessions.json    // Session registry

// Write access
~/.openclaw/agents/main/sessions/resume-prompts/*.md      // Resumption prompts
~/.openclaw/agents/main/sessions/archive/YYYY-MM-DD/     // Archived sessions
```

**Code does NOT access:**
- User's home directory (except ~/.openclaw)
- Shell history files
- SSH keys or credentials
- Browser data
- Other application data

**Verification:**
```bash
# Search for suspicious file access patterns
grep -r "\.ssh\|\.aws\|\.env\|bash_history\|zsh_history" lib/ bin/
# Result: No matches
```

---

### 5. ✅ Package.json Scripts

**Scanner concern:**
> "Check package.json scripts (preinstall/postinstall/test) that run commands automatically"

**Response:** **Verified clean - Test scripts only.**

**Complete package.json scripts:**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

**No install hooks:**
- ❌ No `preinstall`
- ❌ No `postinstall`
- ❌ No `prepare`
- ❌ No `prepublish`

**Only test scripts:**
- ✅ `test` - Runs test suite (manual trigger only)
- ✅ `test:watch` - Runs tests in watch mode
- ✅ `test:coverage` - Generates coverage report

**Nothing executes automatically during npm install or npm link.**

---

### 6. ✅ Autonomous Invocation

**Scanner concern:**
> "If you allow autonomous invocation and then install the CLI blindly, the agent could run monitoring tasks without repeated confirmations"

**Response:** **By design - This is the intended feature.**

**How autonomous invocation works:**

1. **User enables monitoring (AGENTS.md):**
   ```markdown
   ## 🌊 TIDE WATCH: Context Window Monitoring
   
   **Monitoring schedule:**
   - Check `session_status` approximately **once per hour**
   ```

2. **User enables heartbeat (HEARTBEAT.md - optional):**
   ```markdown
   # Tide Watch: Check capacity every hour
   - Check session capacity via session_status
   - Warn if approaching thresholds
   ```

3. **Agent checks capacity using built-in tools:**
   - Calls `session_status` (OpenClaw native tool)
   - Reads session JSONL files (local filesystem)
   - Compares usage to thresholds
   - Warns user if needed

**No CLI execution during autonomous monitoring:**
- Agent does NOT run `tide-watch` command
- Agent reads session files directly
- CLI tool is for manual use only

**User control:**
- Monitoring only happens if user adds directives to AGENTS.md
- User sets thresholds and schedule
- User can disable at any time (remove directives)
- All actions are local (no external calls)

---

### 7. ✅ Code Inspection Guidance

**Scanner recommendation:**
> "Inspect the code locally (lib/*.js and package.json) before running npm link"

**Response:** **Excellent advice - Here's what to look for.**

**Pre-install checklist:**

**1. Check package.json (no malicious scripts):**
```bash
cat ~/clawd/skills/tide-watch/package.json | jq '.scripts'
# Should only show test scripts, no install hooks
```

**2. Inspect main library files:**
```bash
# Check capacity.js (session parsing)
less ~/clawd/skills/tide-watch/lib/capacity.js
# Look for: file I/O limited to ~/.openclaw/agents/main/sessions/
# Verify: no network calls, no credential access

# Check resumption.js (resumption prompts)
less ~/clawd/skills/tide-watch/lib/resumption.js
# Look for: writes limited to resume-prompts/ directory
# Verify: no external data transmission
```

**3. Verify no network modules:**
```bash
cd ~/clawd/skills/tide-watch
grep -r "http\|net\|axios\|fetch" lib/ bin/
# Should return no matches (or only in comments/strings)
```

**4. Check dependencies:**
```bash
cat ~/clawd/skills/tide-watch/package.json | jq '.dependencies, .devDependencies'
# Should only show: jest (devDependencies)
# No production dependencies
```

**5. Run tests before linking:**
```bash
cd ~/clawd/skills/tide-watch
npm test
# Should show: 113 tests passing
# If tests fail, investigate before linking
```

**Red flags to watch for (none present):**
- Network-related modules (http, https, net, axios, node-fetch)
- Child process execution (child_process, exec, spawn)
- Credential access (reading .env, .aws, .ssh)
- File access outside ~/.openclaw
- Obfuscated code (base64, eval, Function constructor)
- Install hooks (preinstall, postinstall)

**Green flags (all present):**
- Human-readable code
- Comprehensive tests (113 passing)
- No production dependencies
- No install hooks
- Restricted file access
- Zero network activity

---

## Reconciling Documentation vs. Code

**Original confusion:**
- SECURITY-SCAN.md used "instruction-only" terminology
- This was incorrect and has been fixed

**Accurate description:**
- **Hybrid skill:** Directives + optional CLI tool
- **Two install tiers:** Basic (no code) or Full (with CLI)
- **Code present:** lib/*.js, bin/tide-watch
- **All code inspectable:** Plain JavaScript, no obfuscation

**Updated documentation:**
- SECURITY-SCAN.md now correctly describes hybrid architecture
- Added "Hybrid Skill Architecture" clarification section
- Removed all "instruction-only" references
- Commit: 3d57c85 (2026-02-24)

---

## Summary for Users

**Safe to install if:**
1. ✅ You want session capacity monitoring to prevent lockups
2. ✅ You trust local-only operations (no network activity)
3. ✅ You inspect the code first (standard practice for any CLI tool)
4. ✅ You understand this includes executable code (lib/*.js)

**Risk level:** **LOW**
- No network activity
- No credential requirements
- Local filesystem access only (OpenClaw session directory)
- No install hooks
- Fully inspectable code

**Recommendation:**
1. Read this document
2. Inspect lib/*.js and package.json
3. Run tests (`npm test`) to verify behavior
4. Install basic monitoring (directives only) first
5. Add CLI tool later if desired (`npm link`)

**Questions or concerns?**
- GitHub Issues: https://github.com/chrisagiddings/openclaw-tide-watch/issues
- Email: chris@chrisgiddings.net
- Security concerns: Please open a GitHub issue with tag "security"

---

**Maintainer note:** The ClawHub scanner's feedback was valuable and accurate. The documentation inconsistency has been fixed. Thank you for the thorough review.

**Signed:** Chris Giddings  
**Date:** 2026-02-24  
**Commit:** 3d57c85
