# Research: anyBins Pattern for Optional Dependencies

**Date:** 2026-02-28  
**Context:** Issue #24 - Fix metadata/documentation inconsistency  
**Goal:** Verify `anyBins` is an acceptable pattern for ClawHub skills

---

## Official Documentation Confirmation

### Source: OpenClaw Skills Documentation
**URL:** https://www.learnclawdbot.org/docs/tools/skills

### Quote:
> **requires.anyBins — list; at least one must exist on PATH.**

### Context:
The documentation lists `anyBins` alongside other requirement types:

- `requires.bins` — list; **each must exist on PATH** (mandatory, all-or-nothing)
- `requires.anyBins` — list; **at least one must exist on PATH** (optional, one-of-many)
- `requires.env` — list; env var must exist or be provided in config
- `requires.config` — list of openclaw.json paths that must be truthy

---

## Semantic Difference

### `bins` (current Tide Watch metadata):
```json
"requires": {
  "bins": ["node", "npm"]
}
```
**Meaning:** BOTH `node` AND `npm` MUST exist on PATH for the skill to be eligible.  
**Effect:** Skill is disabled if either is missing.  
**Problem:** Contradicts "Directives-Only" mode (no Node required).

### `anyBins` (proposed fix):
```json
"requires": {
  "bins": [],
  "anyBins": ["node"]
}
```
**Meaning:** AT LEAST ONE of the listed binaries should exist (node is helpful but not mandatory).  
**Effect:** Skill is always eligible; presence of `node` enables CLI mode.  
**Benefit:** Accurately represents optional CLI tooling.

---

## Alternative: Remove Binary Requirements Entirely

```json
"requires": {
  "bins": []
}
```
**Meaning:** No binary requirements for skill eligibility.  
**Effect:** Skill always loads; Node requirement documented in install spec only.  
**Benefit:** Simplest solution, clearest intent.

---

## Install Spec Pattern (Document Requirements There)

Many skills declare binary requirements in the **install spec label** instead of `requires.bins`:

```json
"install": [{
  "id": "npm",
  "kind": "node",
  "package": ".",
  "bins": ["tide-watch"],
  "label": "Install tide-watch CLI (requires Node.js 14+)"
}]
```

**Advantages:**
- Binary requirement lives in the install context
- Doesn't gate skill eligibility
- Clear user-facing message about what's needed
- Matches pattern of many ClawHub skills

---

## Recommended Fix

### Step 1: Remove from requires.bins
```json
"requires": {
  "bins": [],  // Remove node/npm
  "config": ["~/.openclaw/agents/main/sessions/"]
}
```

### Step 2: Document in install spec
```json
"install": [{
  "id": "npm",
  "kind": "node",
  "package": ".",
  "bins": ["tide-watch"],
  "label": "Install tide-watch CLI for manual capacity checks (requires Node.js 14+, optional)"
}]
```

### Step 3: Use anyBins if needed for advanced detection
```json
"requires": {
  "bins": [],
  "anyBins": ["node"]  // Enables runtime detection for CLI mode
}
```

**Rationale:**
- `anyBins: ["node"]` allows runtime detection (CLI vs Directives mode)
- Install spec label documents the actual requirement
- No false mandatory gating on Node.js

---

## ClawHub Scan Impact

**Current scan result:** Suspicious (medium confidence) due to metadata/docs mismatch

**After fix:**
- ✅ Metadata no longer declares Node as mandatory
- ✅ Documentation matches metadata (Directives-Only mode truly optional)
- ✅ Expected scan result: BENIGN (high confidence)

---

## Implementation Plan (All Three Steps from Issue #24)

### 1. Metadata Fix
- Remove `node` and `npm` from `requires.bins`
- Optionally add `anyBins: ["node"]` for detection

### 2. Documentation Fix
- Remove all "instruction-only (no code)" references
- Add comparison table: Directives-Only vs CLI Tools
- Clarify Node requirement lives in install spec

### 3. Install Spec Clarity
- Update install label to mention Node 14+ requirement
- Mark as "(optional - Directives-Only mode requires no installation)"

---

## Conclusion

**`anyBins` is an official, documented OpenClaw pattern.**

**Best approach for Tide Watch:**
1. Remove `node`/`npm` from `requires.bins` entirely
2. Document Node requirement in install spec label
3. Optionally use `anyBins: ["node"]` if runtime detection is valuable
4. Update all docs to remove "instruction-only" claims

**Expected outcome:** BENIGN scan rating with clear user guidance.
