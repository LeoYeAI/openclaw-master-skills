# Changelog

All notable changes to the Yatta! OpenClaw skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-02-28

### Fixed

#### ClawHub Registry Metadata Sync (Issue #19)

**Problem:** ClawHub registry reads `package.json`, not SKILL.md metadata JSON.

**Scanner reported:**
- "Required env vars: none" (incorrect)
- "Primary credential: none" (incorrect)
- SKILL.md declared YATTA_API_KEY as required, but registry didn't show it

**Root cause:** `package.json` openclaw section was missing:
- `requires.env` (credential requirements)
- `requires.anyBins` (optional verification tools)
- `primaryEnv` (primary credential declaration)

**Fix applied:** Synced `package.json` with SKILL.md metadata

**Now includes:**
```json
"openclaw": {
  "requires": {
    "bins": ["curl", "jq"],
    "env": ["YATTA_API_KEY", "YATTA_API_URL"],  // ← Added
    "anyBins": ["openssl", "dig"]                // ← Added
  },
  "primaryEnv": "YATTA_API_KEY"                  // ← Added
}
```

**Expected result:** ClawHub registry correctly displays credential requirements

---

## [0.2.1] - 2026-02-28

### Fixed

#### ClawHub Registry Metadata (Issue #18)

**Added top-level `disable-model-invocation` field:**
- ClawHub registry was showing `disable-model-invocation: false` despite being set in metadata JSON
- Added top-level YAML field to SKILL.md frontmatter (same pattern as other BENIGN-rated skills)
- Ensures registry correctly reflects manual-only invocation policy

**Declared optional verification tools:**
- Added `anyBins: ["openssl", "dig"]` to requirements
- These tools are used by `scripts/verify-endpoint.sh` but are optional
- Skill works without them (verification script gracefully skips missing checks)

### Changed

**Updated description to document security fixes:**
- Added security notice: "v0.2.0 eliminates RCE vulnerability from v0.1.3"
- Documents shell/JSON injection fix, endpoint verification, safe patterns
- Similar to how Tide Watch documents CVE-2026-001 fix

### Security

**VirusTotal Rating:** ✅ **BENIGN**

> "The OpenClaw Yatta! skill (v0.2.0) is classified as benign. The developers have demonstrated a strong commitment to security by explicitly documenting and fixing critical shell and JSON injection vulnerabilities (RCE risk) present in previous versions."

**ClawHub Rating:** Expected BENIGN after metadata fix

---

## [0.2.0] - 2026-02-28

### 🔒 Security Fixes (CRITICAL)

**This release addresses THREE security findings from VirusTotal scan.**

#### Fixed: Shell and JSON Injection Vulnerabilities (Issue #15 - CRITICAL)

**Impact:** Remote Code Execution (RCE) risk, API key exfiltration

**Changes:**
- ✅ Replaced ALL unsafe curl examples with jq-based safe patterns
- ✅ Added comprehensive SECURITY.md documentation
- ✅ Created `scripts/yatta-safe-api.sh` with reusable safe wrapper functions
- ✅ Added prominent "Security: Input Validation" section to SKILL.md

**Safe patterns implemented:**
- JSON construction: `jq -n --arg` (prevents JSON injection)
- URL encoding: `jq -sRr @uri` (prevents shell injection)
- No direct string interpolation in JSON or URLs

**Before (VULNERABLE):**
```bash
curl -d "{\"title\": \"$TITLE\"}"  # JSON injection
curl "$API_URL/tasks/$TASK_ID"     # Shell injection
```

**After (SAFE):**
```bash
PAYLOAD=$(jq -n --arg title "$TITLE" '{title: $title}')
curl -d "$PAYLOAD"

TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$API_URL/tasks/$TASK_ID_ENCODED"
```

**Files modified:**
- `SKILL.md` - All curl examples updated with safe patterns
- `SECURITY.md` (new) - Comprehensive vulnerability documentation
- `scripts/yatta-safe-api.sh` (new) - Safe wrapper functions

**Related:** VirusTotal security finding - Shell/JSON injection (P0)

---

#### Fixed: Opaque Supabase URL Documentation (Issue #16 - MEDIUM)

**Impact:** Trust gap, users couldn't verify endpoint legitimacy

**Changes:**
- ✅ Added "API Endpoint Verification" section to SKILL.md
- ✅ Documented Supabase URL ownership (Chris Giddings)
- ✅ Created `scripts/verify-endpoint.sh` for automated verification
- ✅ Explained infrastructure choice and branded URL roadmap

**Verification script checks:**
- SSL certificate validity
- DNS resolution
- HTTP connectivity
- Supabase project ID match (zunahvofybvxpptjkwxk)

**Files modified:**
- `SKILL.md` - Added endpoint verification section
- `scripts/verify-endpoint.sh` (new) - Automated verification tool

**Related:** VirusTotal security finding - Opaque endpoint (P1)

---

#### Fixed: Metadata Inconsistency (Issue #17 - LOW)

**Impact:** Unclear invocation policy, risk of autonomous operations

**Changes:**
- ✅ Added `"disable-model-invocation": true` to package.json
- ✅ Added comprehensive "Invocation Policy" section to SKILL.md
- ✅ Documented manual-only requirement and security rationale

**Metadata now consistent:**
- `package.json`: `disable-model-invocation: true` ✅
- `SKILL.md`: `disable-model-invocation: true` ✅
- ClawHub registry will show: `disable-model-invocation: true` ✅

**Why manual-only:**
- Yatta! API keys grant full account access
- No read-only scopes available
- Destructive operations require explicit user intent
- Prevents accidental data loss

**Files modified:**
- `package.json` - Added disable-model-invocation field
- `SKILL.md` - Added Invocation Policy section

**Related:** VirusTotal security finding - Metadata inconsistency (P2)

---

### 📊 Security Ratings

**Before v0.2.0:**
- ClawHub: BENIGN (low confidence)
- VirusTotal: **SUSPICIOUS** (justified - had RCE vulnerability)

**After v0.2.0:**
- ClawHub: BENIGN (expected high confidence)
- VirusTotal: **BENIGN** (expected - all vulnerabilities fixed)

---

### 📚 Documentation

**New files:**
- `SECURITY.md` - Vulnerability documentation with examples and safe patterns
- `scripts/yatta-safe-api.sh` - Reusable safe wrapper functions  
- `scripts/verify-endpoint.sh` - Endpoint verification tool
- `SECURITY-ASSESSMENT-ISSUE-15.md` - Security analysis (RCE fix)
- `SECURITY-ASSESSMENT-ISSUE-16.md` - Security analysis (endpoint verification)
- `SECURITY-ASSESSMENT-ISSUE-17.md` - Security analysis (metadata consistency)

**Enhanced files:**
- `SKILL.md` - Security section, endpoint verification, invocation policy

---

### 🛠️ Migration Guide

**For users upgrading from v0.1.x:**

1. **Update the skill:**
   ```bash
   clawhub update openclaw-yatta-skill
   ```

2. **Review security documentation:**
   - Read `SECURITY.md` to understand vulnerabilities and safe patterns
   - Review updated SKILL.md examples (all now use safe patterns)

3. **Update custom scripts:**
   - Replace direct string interpolation with jq patterns
   - Use `scripts/yatta-safe-api.sh` wrapper functions
   - Test with malicious input to verify injection is blocked

4. **Verify endpoint (optional):**
   ```bash
   bash scripts/verify-endpoint.sh
   ```

5. **Confirm metadata:**
   ```bash
   jq '.openclaw["disable-model-invocation"]' package.json
   # Should output: true
   ```

**Breaking changes:** None - backward compatible

---

### 🔗 Links

- **GitHub Issues:** [#15](https://github.com/chrisagiddings/openclaw-yatta-skill/issues/15), [#16](https://github.com/chrisagiddings/openclaw-yatta-skill/issues/16), [#17](https://github.com/chrisagiddings/openclaw-yatta-skill/issues/17)
- **VirusTotal Scan:** Addressed CRITICAL RCE vulnerability
- **ClawHub:** https://clawhub.ai/chrisagiddings/openclaw-yatta-skill

---

## [0.1.3] - 2026-02-XX

Initial public release with basic Yatta! API integration.

### Added
- Task management operations (create, update, archive, batch)
- Project management operations
- Context management
- Comment management
- Follow-up and delegation features
- Calendar subscription management
- Analytics and insights
- Eisenhower Matrix view

### Security
- Initial security warnings documented
- API key configuration guidance

---

[0.2.0]: https://github.com/chrisagiddings/openclaw-yatta-skill/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/chrisagiddings/openclaw-yatta-skill/releases/tag/v0.1.3
