# Security Assessment: Yatta! v0.2.2 (Registry Metadata Sync)

**Version:** 0.2.2  
**Date:** 2026-02-28  
**Assessment Type:** Registry metadata synchronization  
**Previous Version:** 0.2.1 (SUSPICIOUS - missing package.json metadata)  
**Issue:** #19

---

## Executive Summary

**v0.2.2 synchronizes package.json with SKILL.md metadata to fix ClawHub registry display.**

### Problem

ClawHub registry reads **package.json** for submission summary, NOT SKILL.md metadata JSON.

**Scanner reported:**
- "Required env vars: none" ❌
- "Primary credential: none" ❌
- Metadata inconsistency flagged as suspicious

**Actual requirements (in SKILL.md):**
- Required env vars: YATTA_API_KEY, YATTA_API_URL ✅
- Primary credential: YATTA_API_KEY ✅

### Solution

Added missing fields to `package.json` openclaw section:
- `requires.env`: ["YATTA_API_KEY", "YATTA_API_URL"]
- `requires.anyBins`: ["openssl", "dig"]
- `primaryEnv`: "YATTA_API_KEY"

---

## Assessment Against ClawHub Security Criteria

### 1. Purpose-Capability Alignment

**Finding:** ✅ **IMPROVED - BENIGN**

**Before v0.2.2:**
- Registry showed no credential requirements
- Users couldn't see what env vars needed
- Mismatch between registry and documentation

**After v0.2.2:**
- Registry correctly displays YATTA_API_KEY as required
- primaryEnv declared
- Full transparency about requirements

**Verdict:** BENIGN - Improved transparency

---

### 2. Instruction Scope

**Finding:** ✅ **NO CHANGE - BENIGN**

**Changes:** None (metadata only)

**Verdict:** BENIGN

---

### 3. Install Mechanism Risk

**Finding:** ✅ **NO CHANGE - BENIGN**

**Changes:** None (metadata only)

**Verdict:** BENIGN

---

### 4. Environment/Credentials

**Finding:** ✅ **SIGNIFICANTLY IMPROVED - BENIGN**

**Before v0.2.2:**
- Registry: "Required env vars: none"
- SKILL.md: Requires YATTA_API_KEY
- **Users might not realize API key needed**
- Potential for surprise when skill doesn't work

**After v0.2.2:**
- Registry: Shows YATTA_API_KEY and YATTA_API_URL required
- primaryEnv: YATTA_API_KEY declared
- Full transparency upfront

**Verdict:** BENIGN - Critical transparency improvement

---

### 5. Persistence & Privilege

**Finding:** ✅ **NO CHANGE - BENIGN**

**Changes:** None (metadata only)

**Verdict:** BENIGN

---

## Changes Analysis

### What Changed

**package.json openclaw section:**

```diff
 "openclaw": {
   "skillName": "yatta",
   "emoji": "✅",
   "disable-model-invocation": true,
   "requires": {
     "bins": ["curl", "jq"],
+    "env": ["YATTA_API_KEY", "YATTA_API_URL"],
+    "anyBins": ["openssl", "dig"]
   },
+  "primaryEnv": "YATTA_API_KEY"
 }
```

### Why This Matters

**ClawHub registry display:**
- Reads package.json for "submission summary"
- SKILL.md metadata used internally, but not for user-facing summary
- Users see package.json metadata first

**Before fix:**
- User sees: "Required env vars: none"
- User thinks: "Great, no setup needed!"
- User installs skill
- Skill doesn't work (missing API key)
- User confused

**After fix:**
- User sees: "Required env vars: YATTA_API_KEY, YATTA_API_URL"
- User thinks: "I need to set up API credentials first"
- User reads setup docs
- User configures correctly
- Skill works

---

## Metadata Consistency Verification

### v0.2.2 Status

**package.json:**
```json
"openclaw": {
  "disable-model-invocation": true,  ✅
  "requires": {
    "bins": ["curl", "jq"],           ✅
    "env": ["YATTA_API_KEY", "YATTA_API_URL"],  ✅
    "anyBins": ["openssl", "dig"]     ✅
  },
  "primaryEnv": "YATTA_API_KEY"       ✅
}
```

**SKILL.md frontmatter:**
```yaml
disable-model-invocation: true       ✅
```

**SKILL.md metadata JSON:**
```json
"openclaw": {
  "disable-model-invocation": true,  ✅
  "requires": {
    "bins": ["curl", "jq"],           ✅
    "env": ["YATTA_API_KEY", "YATTA_API_URL"],  ✅
    "anyBins": ["openssl", "dig"]     ✅
  },
  "primaryEnv": "YATTA_API_KEY"       ✅
}
```

**All three locations now consistent:** ✅

---

## Overall Security Classification

### Self-Assessment

**Classification:** ✅ **BENIGN** (High Confidence)

**Rationale:**

1. **Metadata synchronization only** - No code changes
2. **Improved transparency** - Credentials now visible in registry
3. **User protection** - Clear upfront about requirements
4. **No new risks** - Only adds visibility
5. **Follows proven pattern** - Same structure as other BENIGN skills

### Confidence Factors

**High confidence because:**
- ✅ v0.2.0 code already assessed as BENIGN (VirusTotal confirmed)
- ✅ v0.2.1 metadata improvements assessed as BENIGN
- ✅ v0.2.2 only adds missing package.json fields
- ✅ No capability expansion
- ✅ No code changes
- ✅ Critical transparency improvement for users

---

## Comparison: v0.2.1 vs v0.2.2

### Registry Display

**v0.2.1:**
- Required env vars: ❌ none (incorrect)
- Primary credential: ❌ none (incorrect)
- Optional tools: ❌ not shown

**v0.2.2:**
- Required env vars: ✅ YATTA_API_KEY, YATTA_API_URL
- Primary credential: ✅ YATTA_API_KEY
- Optional tools: ✅ openssl, dig

### Metadata Locations

**v0.2.1:**
- package.json: ❌ Incomplete (missing env/anyBins/primaryEnv)
- SKILL.md frontmatter: ✅ Complete
- SKILL.md metadata: ✅ Complete

**v0.2.2:**
- package.json: ✅ Complete (synced)
- SKILL.md frontmatter: ✅ Complete
- SKILL.md metadata: ✅ Complete

---

## Expected Scanner Response

### Current Issues (v0.2.1)

**ClawHub scanner flagged:**
1. ✅ "Required env vars: none" (registry shows none, SKILL.md shows YATTA_API_KEY)
2. ✅ "Primary credential: none" (registry shows none, SKILL.md shows YATTA_API_KEY)

### After v0.2.2

**Expected resolution:**
1. ✅ Registry will show: "Required env vars: YATTA_API_KEY, YATTA_API_URL"
2. ✅ Registry will show: "Primary credential: YATTA_API_KEY"
3. ✅ Scanner should no longer flag metadata mismatch
4. ✅ Expected rating: BENIGN

---

## Recommendations

### For Publication

**✅ READY TO PUBLISH TO CLAWHUB**

**Expected outcome:**
- ClawHub scan: SUSPICIOUS → BENIGN
- VirusTotal scan: BENIGN (no code changes)
- Registry metadata: Correctly displays requirements

**Publication command:**
```bash
clawhub publish ~/clawd/openclaw-yatta-skill \
  --slug openclaw-yatta-skill \
  --name "Yatta! - Task & Capacity Management" \
  --version 0.2.2 \
  --changelog "Registry metadata sync: Add requires.env, requires.anyBins, and primaryEnv to package.json. Fixes 'Required env vars: none' display issue."
```

### For Users

**Migration from v0.2.1:**
- No action required
- Update: `clawhub update openclaw-yatta-skill`
- No breaking changes
- Same functionality

### For Maintenance

**Lesson learned:**
- **ClawHub registry reads package.json, not SKILL.md metadata**
- Always sync package.json openclaw section with SKILL.md metadata
- Test fresh installs to verify registry display

**Going forward:**
- Keep package.json and SKILL.md metadata identical
- Check ClawHub skill page after publication
- Verify "Required env vars" and "Primary credential" display correctly

---

## Conclusion

**v0.2.2 successfully synchronizes package.json with SKILL.md metadata.**

**Security status:**
- Code: Unchanged from v0.2.0 (BENIGN)
- Metadata: Fixed (package.json synced)
- Transparency: Significantly improved (credentials visible)

**Expected ratings:**
- VirusTotal: BENIGN (confirmed for v0.2.0, no code changes)
- ClawHub: BENIGN (metadata mismatch resolved)

**Critical fix:** Users will now see credential requirements upfront in registry.

**Ready for production use.**

---

*Assessment completed: 2026-02-28*  
*Assessed by: Navi*  
*Issue: #19*  
*Version: 0.2.2*
