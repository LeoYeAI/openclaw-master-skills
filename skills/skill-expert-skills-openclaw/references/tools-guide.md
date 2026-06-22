# Skill Expert Tools Guide

Complete reference for all tools in skill-expert-skills.

Note on paths:
- If you run commands from the **project root**, call scripts via `.claude/skills/skill-expert-skills/scripts/...`.
- If you `cd .claude/skills/skill-expert-skills`, you can call scripts via `scripts/...` and use `..` as the skills root.

## Tool Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `init_skill.py` | Create new skill | Starting from scratch |
| `quick_validate.py` | Format + quality check | After any change |
| `universal_validate.py` | Portability check | Before packaging |
| `package_skill.py` | Create .skill file | Ready to distribute |
| `upgrade_skill.py` | Best practice analysis | Improving old skills |
| `analyze_trigger.py` | Trigger coverage | Optimizing description |
| `diff_with_official.py` | Compatibility check | Before official deploy |
| `search_skills.py` | Search installed skills | Reuse-first discovery (before creating) |

---

## 1. init_skill.py

Creates a new skill directory with best-practice template.

### Usage

```bash
python scripts/init_skill.py <skill-name> --path <output-dir>

# Example
python scripts/init_skill.py my-new-skill --path .claude/skills
```

### Output Structure

```
my-new-skill/
├── SKILL.md           # Pre-filled with decision tree, output contract, etc.
├── scripts/
│   └── example.py     # Placeholder script
├── references/
│   └── api_reference.md
└── assets/
    └── example_asset.txt
```

### Template Features

The generated SKILL.md includes:
- ✅ Description with "Use when:" template
- ✅ Decision tree (ASCII art)
- ✅ Quick start commands
- ✅ Workflow steps
- ✅ Output contract
- ✅ References navigation table
- ✅ Troubleshooting table
- ✅ Definition of Done checklist

---

## 2. quick_validate.py

Enhanced validation with quality scoring.

### Usage

```bash
# Basic
python scripts/quick_validate.py .claude/skills/<skill-name>

# Verbose (show metrics)
python scripts/quick_validate.py .claude/skills/<skill-name> --verbose
```

### Checks Performed

| Category | Check | Threshold |
|----------|-------|-----------|
| Structure | SKILL.md exists | Required |
| Encoding | UTF-8 (with BOM OK) | Required |
| Frontmatter | Valid YAML | Required |
| Name | hyphen-case, ≤64 chars | Required |
| Description | No `<>`, ≤1024 chars | Required |
| Conciseness | <500 lines (warn), <800 lines (error) | Recommended/Required |

### Quality Score (0-100)

- **30 pts**: Conciseness (line count)
- **25 pts**: Description quality
- **25 pts**: Best practices (allowed-tools, references, etc.)
- **20 pts**: Structure (decision tree, output contract, etc.)

### Output Example

```
======================================================================
✅ SKILL VALIDATION PASSED
======================================================================

📊 Quality Score: 85/100 ████████░░ (Good)

🟡 Warnings (Should Fix):
   ⚠️  WARNING: 'allowed-tools' is missing

💡 Recommendations (Nice to Have):
   💡 RECOMMENDATION: Add 'Not for:' section to set clear boundaries

======================================================================
```

---

## 3. universal_validate.py

Checks for project-specific fingerprints that break portability.

### Usage

```bash
python scripts/universal_validate.py .claude/skills/<skill-name>
```

### Detected Patterns

| Pattern | Example | Issue |
|---------|---------|-------|
| Windows paths | `C:\Users\john\...` | User-specific |
| POSIX home paths | `/Users/john/...`, `/home/john/...` | User-specific |
| Tilde paths | `~/projects/...` | User-specific |
| file:// URIs | `file:///C:/...` | Local reference |

### Placeholder Exemption

Patterns containing `...` are treated as documentation examples and ignored:
- ✅ `C:\...` in documentation (OK)
- ❌ `C:\Users\...\project` (flagged without proper placeholder)

---

## 4. package_skill.py

Creates distributable .skill file (ZIP format).

### Usage

```bash
# Default output: current directory
python scripts/package_skill.py .claude/skills/<skill-name>

# Custom output directory
python scripts/package_skill.py .claude/skills/<skill-name> ./dist
```

### Workflow

1. Runs `quick_validate.py` → must pass
2. Runs `universal_validate.py` → warnings only
3. Creates `<skill-name>.skill` ZIP file

### Excluded Files

- `.git/`, `__pycache__/`, `node_modules/`
- `.pyc`, `.pyo` files
- `.DS_Store`

---

## 5. upgrade_skill.py

## 6. search_skills.py

Searches for matching `SKILL.md` files under a skills root directory and ranks results.

### Usage

```bash
# Default root: .claude/skills
python scripts/search_skills.py "code review"

# Custom root
python scripts/search_skills.py "frontend" --root .claude/skills

# Treat query as regex
python scripts/search_skills.py "auth|oauth|jwt" --regex
```

Analyzes existing skills and suggests improvements.

### Usage

```bash
python scripts/upgrade_skill.py .claude/skills/<skill-name>
```

### Detected Missing Elements

| Element | Priority | Template Provided |
|---------|----------|-------------------|
| Decision Tree | High | ✅ |
| Output Contract | High | ✅ |
| "Use when:" in description | High | ✅ |
| Quick Start | Medium | ✅ |
| Troubleshooting | Medium | ✅ |
| References Navigation | Medium | ✅ |
| Definition of Done | Low | ✅ |
| "Not for:" boundary | Low | ✅ |
| allowed-tools | Medium | ✅ |

### Output Example

```
======================================================================
🔍 SKILL UPGRADE ANALYSIS
======================================================================

Skill: my-old-skill
Suggestions: 4

🔴 HIGH PRIORITY (Must Fix):

  [best_practice] Missing: Decision Tree
  → Add a decision tree for clear workflow guidance

  Suggested template:
    ## Decision Tree
    
    ```
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        Task Decision Tree                            │
    ...

🟡 MEDIUM PRIORITY (Should Fix):

  [frontmatter] Missing allowed-tools field
  → Add allowed-tools for least-privilege security

======================================================================
```

---

## 6. analyze_trigger.py

Analyzes description for trigger keyword coverage.

### Usage

```bash
python scripts/analyze_trigger.py .claude/skills/<skill-name>
```

### Analysis Categories

| Category | Examples | Weight |
|----------|----------|--------|
| Action Verbs | create, analyze, validate, debug | 30 pts |
| Artifact Types | .md, .py, api, config, report | 20 pts |
| Context Indicators | skill, SKILL.md, frontmatter | 20 pts |
| "Use when:" section | - | 15 pts |
| "Not for:" boundary | - | 10 pts |
| Length (200-800 chars) | - | 5 pts |

### Output Example

```
======================================================================
🎯 TRIGGER ANALYSIS REPORT
======================================================================

Skill: skill-expert-skills
Description length: 450 chars

📊 Trigger Score: 85/100 ████████░░ (Good)
   Feedback: Add 'Not for:' to set scope boundaries

📌 KEYWORD COVERAGE:
   ✅ Action Verbs: create, optimize, validate, package
   ✅ Artifact Types: skill, .md, frontmatter
   ⚠️  Context Indicators: (none detected)

💡 SUGGESTED TRIGGER PHRASES:
   1. "Creating a new skill"
   2. "How to write a skill"
   3. "Validate my skill structure"
```

---

## 7. diff_with_official.py

Checks compatibility with official Agent Skills spec.

### Usage

```bash
python scripts/diff_with_official.py .claude/skills/<skill-name>
```

### Compatibility Rules

| Field | Official Spec | Extended (this skill) |
|-------|--------------|----------------------|
| name | ✅ Required | ✅ Required |
| description | ✅ Required | ✅ Required |
| license | ❌ Not allowed | ✅ Allowed |
| allowed-tools | ❌ Not allowed | ✅ Allowed |
| metadata | ❌ Not allowed | ✅ Allowed |

### Output Example

```
======================================================================
📋 OFFICIAL COMPATIBILITY CHECK
======================================================================

Skill: my-skill

⚠️  NOT FULLY OFFICIAL COMPATIBLE
   This skill uses extended fields from skill-expert-skills

🟡 WARNINGS (Extended features):
   • Extended field 'allowed-tools' - OK for skill-expert-skills, 
     but NOT supported by official Agent Skills
   • Extended field 'metadata' - OK for skill-expert-skills,
     but NOT supported by official Agent Skills

📌 INFO (Extended features in use):
   • Uses allowed-tools: ['read', 'write', 'execute']
   • Uses metadata: ['display_name_zh', 'language']

======================================================================
💡 MIGRATION GUIDE (if needed for official Agent Skills):
   1. Keep only 'name' and 'description' in frontmatter
   2. Remove 'allowed-tools', 'license', 'metadata' fields
   3. Move any removed metadata to SKILL.md body or references/
======================================================================
```

---

## Recommended Workflow

### Creating New Skill

```bash
# 1. Initialize
python scripts/init_skill.py my-skill --path .claude/skills

# 2. Edit SKILL.md (fill TODOs)

# 3. Validate
python scripts/quick_validate.py .claude/skills/my-skill
python scripts/universal_validate.py .claude/skills/my-skill

# 4. Check trigger coverage
python scripts/analyze_trigger.py .claude/skills/my-skill

# 5. Package
python scripts/package_skill.py .claude/skills/my-skill ./dist
```

### Upgrading Existing Skill

```bash
# 1. Analyze gaps
python scripts/upgrade_skill.py .claude/skills/old-skill

# 2. Apply suggested changes

# 3. Validate
python scripts/quick_validate.py .claude/skills/old-skill

# 4. Check trigger coverage
python scripts/analyze_trigger.py .claude/skills/old-skill

# 5. Check official compatibility (if deploying to official)
python scripts/diff_with_official.py .claude/skills/old-skill
```

---

## Exit Codes

All tools follow consistent exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success / Pass |
| 1 | Failure / Issues found |

Use in CI/CD:

```bash
python scripts/quick_validate.py .claude/skills/my-skill && \
python scripts/universal_validate.py .claude/skills/my-skill && \
python scripts/package_skill.py .claude/skills/my-skill ./dist
```

