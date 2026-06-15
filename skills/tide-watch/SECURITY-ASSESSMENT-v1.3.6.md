# Security Assessment: Tide Watch v1.3.6

**Version:** 1.3.6  
**Date:** 2026-03-01  
**Assessment Type:** Metadata fix (environment variable declaration)  
**Previous Version:** 1.3.5 (BENIGN code, SUSPICIOUS scan due to metadata)

---

## Executive Summary

**Tide Watch v1.3.6 declares the optional OPENCLAW_SESSION_ID environment variable in metadata.**

### Changes

**Problem:**
- v1.3.4 added `--current` flag that reads `OPENCLAW_SESSION_ID`
- Code and documentation described this feature
- Metadata did NOT declare the environment variable
- ClawHub scan flagged: UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID
- Rating downgraded: BENIGN/BENIGN → BENIGN/SUSPICIOUS

**Solution:**
- Added `env` section to `requires` in SKILL.md frontmatter
- Declared `OPENCLAW_SESSION_ID` as **optional**
- Added notes explaining usage and modes

**No code changes** - This is a metadata-only fix.

---

## ClawHub Scan Analysis (v1.3.5 → v1.3.6)

### v1.3.5 Scan Results

**Overall:** BENIGN/SUSPICIOUS (medium confidence)

**Findings:**

1. **[UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID]** unexpected
   - SKILL.md/changelog indicate CLI reads OPENCLAW_SESSION_ID
   - Skill metadata listed NO required env vars
   - Metadata omission could affect automated gating

2. **[DOCUMENTATION_CODE_MISMATCH]** unexpected (historical)
   - Previously flagged mismatch (docs vs repo)
   - Acknowledged as "hybrid" skill (directives + optional CLI)
   - Remediation notes provided

3. **[CVE-2026-001_SHELL_INJECTION]** unexpected (historical)
   - v1.0.0 vulnerability, patched in v1.0.1
   - Current version: 1.3.5 (not affected)

**Scanner verdict:**
- Code is benign
- Documentation/metadata mismatch raised suspicion
- Recommendation: Declare env var in metadata

---

### v1.3.6 Fix

**Added to SKILL.md frontmatter:**

```json
"requires": {
  "bins": [],
  "anyBins": ["node"],
  "config": ["~/.openclaw/agents/main/sessions/"],
  "env": {
    "optional": ["OPENCLAW_SESSION_ID"],
    "notes": "OPENCLAW_SESSION_ID is optional for auto-detection in CLI mode (v1.3.4+). Not required for Directives-Only mode."
  }
}
```

**Key points:**
- `optional` array (not required)
- Clear notes about usage
- Explains when needed (CLI mode, v1.3.4+)
- States NOT required for Directives-Only mode

---

## Assessment Against ClawHub Security Criteria

### 1. Purpose-Capability Alignment

**Finding:** ✅ **IMPROVED - BENIGN**

**Changes:**
- Metadata now accurately declares all dependencies
- No change to actual capabilities
- Transparency improvement

**Verdict:** BENIGN - Improved documentation

---

### 2. Instruction Scope

**Finding:** ✅ **IMPROVED - BENIGN**

**Changes:**
- Env var dependency now declared
- Resolves documentation/metadata mismatch
- No code changes

**Verdict:** BENIGN - Metadata correction

---

### 3. Install Mechanism Risk

**Finding:** ✅ **NO CHANGE - BENIGN**

**Changes:** Metadata-only (no install changes)

**Verdict:** BENIGN

---

### 4. Environment/Credentials

**Finding:** ✅ **IMPROVED - BENIGN**

**Changes:**
- **Before:** Used OPENCLAW_SESSION_ID but didn't declare it
- **After:** Declared in metadata as optional

**Transparency:**
- ✅ Optional vs required (correctly flagged)
- ✅ Usage explained (auto-detection)
- ✅ Mode-specific (CLI only, not Directives-Only)

**Verdict:** BENIGN - Proper declaration

---

### 5. Persistence & Privilege

**Finding:** ✅ **NO CHANGE - BENIGN**

**Changes:** Metadata-only (no privilege changes)

**Verdict:** BENIGN

---

## Code Changes Analysis

**No code changes in v1.3.6.**

Only metadata updated:
- SKILL.md frontmatter (added env declaration)
- CHANGELOG.md (v1.3.6 entry)
- package.json (version bump)

---

## Behavior Changes

**No behavior changes.**

The env var was already being read in v1.3.4+. This release just declares it in metadata.

**User impact:**
- More accurate eligibility checks
- Clearer expectations
- Better automated gating

---

## Expected ClawHub Scan Results (v1.3.6)

### Predicted Rating

**Overall:** BENIGN/BENIGN (high confidence)

**Expected resolution:**

1. **[UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID]** → **RESOLVED**
   - Env var now declared in metadata
   - Marked as optional (correct)
   - Notes explain usage

2. **[DOCUMENTATION_CODE_MISMATCH]** → **ACCEPTABLE**
   - Hybrid mode documented
   - Remediation notes provided
   - Known and explained

3. **[CVE-2026-001_SHELL_INJECTION]** → **NOT APPLICABLE**
   - Fixed in v1.0.1
   - Current version: 1.3.6
   - Not affected

---

## Overall Security Classification

### Self-Assessment

**Classification:** ✅ **BENIGN** (High Confidence)

**Rationale:**

1. **Metadata fix only** - No code changes
2. **Improved transparency** - Env var now declared
3. **Accurate documentation** - Metadata matches behavior
4. **Optional dependency** - Correctly flagged as optional
5. **Mode-specific** - Clear about when needed

### Confidence Factors

**High confidence because:**
- ✅ No code changes
- ✅ Metadata now matches actual behavior
- ✅ Resolves ClawHub scan finding
- ✅ Improves transparency
- ✅ No new capabilities or risks

---

## Recommendations

### For Publication

**✅ READY TO PUBLISH TO CLAWHUB**

**Expected outcome:**
- ClawHub scan: BENIGN/BENIGN (metadata corrected)
- VirusTotal scan: BENIGN (expected)
- Rating improvement: SUSPICIOUS → BENIGN

**Publication command:**
```bash
clawhub publish ~/clawd/openclaw-tide-watch \
  --slug tide-watch \
  --name "Tide Watch" \
  --version 1.3.6 \
  --changelog "Metadata fix: Declared optional OPENCLAW_SESSION_ID env var. Resolves ClawHub scan finding."
```

---

### For Users

**Upgrade from v1.3.5:**
```bash
clawhub update tide-watch
```

**No behavior changes:**
- Same functionality as v1.3.5
- More accurate metadata
- Better automated checks

---

### For ClawHub Scan

**Addressing scan findings:**

1. **UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID:**
   - ✅ Now declared in `requires.env.optional`
   - ✅ Notes explain usage (CLI mode, v1.3.4+)
   - ✅ Correctly marked optional (not required for Directives-Only)

2. **Documentation/metadata alignment:**
   - ✅ Metadata matches SKILL.md
   - ✅ Metadata matches CHANGELOG.md
   - ✅ Metadata matches actual code behavior

3. **Transparency:**
   - ✅ All dependencies declared
   - ✅ Optional vs required clear
   - ✅ Mode-specific requirements explained

---

## Conclusion

**Tide Watch v1.3.6 resolves the metadata/documentation mismatch flagged by ClawHub scan.**

**Security status:**
- Code: Unchanged (same as v1.3.5)
- Metadata: Corrected (env var declared)
- Impact: None (metadata-only)
- Benefits: Improved transparency, accurate eligibility checks

**Expected ratings:**
- ClawHub: BENIGN (metadata corrected)
- VirusTotal: BENIGN (expected)

**Scan finding resolution:**
- UNDECLARED_ENV_VAR_OPENCLAW_SESSION_ID: **RESOLVED**
- Metadata now matches actual behavior
- Automated gating will be accurate

**Ready for production use.**

**No migration needed:** Users on v1.3.5 can update with no behavior changes.

---

*Assessment completed: 2026-03-01*  
*Assessed by: Navi*  
*Version: 1.3.6*  
*Previous: 1.3.5 (BENIGN code, SUSPICIOUS scan)*  
*Change type: Metadata correction*
