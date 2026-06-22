# Tools Reference

Complete reference for all scripts and tools in skill-expert-skills.

**Path note**: Run commands from the **project root** using
`.claude/skills/skill-expert-skills/scripts/...`, or `cd` into the skill
directory and use `scripts/...` with `..` as the skills root.

---

## Tool Overview

| Tool | Purpose | When to use |
|------|---------|-------------|
| `init_skill.py` | Create new skill | Starting from scratch |
| `quick_validate.py` | Format + quality check | After any change |
| `universal_validate.py` | Portability check | Before packaging |
| `package_skill.py` | Create .skill file | Ready to distribute |
| `upgrade_skill.py` | Best practice analysis | Improving old skills |
| `analyze_trigger.py` | Trigger coverage | Optimizing description |
| `diff_with_official.py` | Compatibility check | Before official deploy |
| `search_skills.py` | Search installed skills | Reuse-first discovery |

---

## 1. init_skill.py

Creates a new skill directory with best-practice template.

```bash
python scripts/init_skill.py <skill-name> --path <output-dir>
# Example:
python scripts/init_skill.py my-new-skill --path .claude/skills
```

Output structure:
```
my-new-skill/
├── SKILL.md           # Pre-filled template with TODOs
├── scripts/
│   └── example.py
├── references/
│   └── api_reference.md
└── assets/
    └── example_asset.txt
```

## 2. quick_validate.py

Format, structure, and quality validation.

```bash
python scripts/quick_validate.py .claude/skills/<skill-name>
python scripts/quick_validate.py .claude/skills/<skill-name> --verbose
```

| Category | Check | Threshold |
|----------|-------|-----------|
| Structure | SKILL.md exists | Required |
| Encoding | UTF-8 (with BOM OK) | Required |
| Frontmatter | Valid YAML with name + description | Required |
| Name | hyphen-case, max 64 chars | Required |
| Description | No `<>`, max 1024 chars | Required |
| Conciseness | < 500 lines (warn), < 800 lines (error) | Recommended/Required |

Quality score (0-100): 30 pts conciseness + 25 pts description + 25 pts best
practices + 20 pts structure.

## 3. universal_validate.py

Checks for project-specific fingerprints that break portability.

```bash
python scripts/universal_validate.py .claude/skills/<skill-name>
```

Detected patterns: Windows paths (`C:\Users\...`), POSIX home paths
(`/Users/...`, `/home/...`), tilde paths (`~/...`), file:// URIs.
Patterns containing `...` as documentation examples are exempted.

## 4. package_skill.py

Creates distributable .skill file (ZIP format).

```bash
python scripts/package_skill.py .claude/skills/<skill-name>
python scripts/package_skill.py .claude/skills/<skill-name> ./dist
```

Workflow: runs quick_validate (must pass) -> runs universal_validate
(warnings only) -> creates `<skill-name>.skill` ZIP.
Excludes: `.git/`, `__pycache__/`, `node_modules/`, `.pyc`, `.DS_Store`.

## 5. search_skills.py

Searches installed skills by keyword matching against name, description,
and SKILL.md content.

```bash
python scripts/search_skills.py "code review"
python scripts/search_skills.py "frontend" --root .claude/skills
python scripts/search_skills.py "auth|oauth|jwt" --regex
```

## 6. upgrade_skill.py

Analyzes existing skills and suggests improvements with templates.

```bash
python scripts/upgrade_skill.py .claude/skills/<skill-name>
```

Detects missing: Decision Tree, Output Contract, "Use when:" in description,
Quick Start, Troubleshooting, References Navigation, Definition of Done,
"Not for:" boundary, allowed-tools.

## 7. analyze_trigger.py

Analyzes description for trigger keyword coverage (score 0-100).

```bash
python scripts/analyze_trigger.py .claude/skills/<skill-name>
```

Categories: Action verbs (30 pts), Artifact types (20 pts), Context
indicators (20 pts), "Use when:" (15 pts), "Not for:" (10 pts),
Length 200-800 chars (5 pts).

## 8. diff_with_official.py

Checks compatibility with official Agent Skills spec (name + description only).

```bash
python scripts/diff_with_official.py .claude/skills/<skill-name>
```

Reports extended fields (license, allowed-tools, metadata) that are valid
locally but not in the official spec. Provides migration guide if needed.

---

## Recommended Workflows

### New Skill

```bash
python scripts/init_skill.py my-skill --path .claude/skills
# Edit SKILL.md
python scripts/quick_validate.py .claude/skills/my-skill
python scripts/universal_validate.py .claude/skills/my-skill
python scripts/analyze_trigger.py .claude/skills/my-skill
python scripts/package_skill.py .claude/skills/my-skill ./dist
```

### Upgrade Existing Skill

```bash
python scripts/upgrade_skill.py .claude/skills/old-skill
# Apply suggestions
python scripts/quick_validate.py .claude/skills/old-skill
python scripts/diff_with_official.py .claude/skills/old-skill
```

### CI/CD

```bash
python scripts/quick_validate.py .claude/skills/my-skill && \
python scripts/universal_validate.py .claude/skills/my-skill && \
python scripts/package_skill.py .claude/skills/my-skill ./dist
```

All tools use exit code 0 for success, 1 for failure.
