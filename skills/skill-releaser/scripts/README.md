# skill-releaser/scripts

Release pipeline validation scripts. Used by the skill-releaser pipeline to
gate skills before they are staged, reviewed, and published.

---

## validate-structure.sh

Validates that a skill directory has all required structural components.
Scores 1 point per check (8 total). Exits 0 only if the score is 8/8.

### Checks (8 total)

| # | Check | What it looks for |
|---|-------|-------------------|
| 1 | `SKILL.md` exists | File present |
| 2 | `skill.yml` exists | File present |
| 3 | `README.md` exists | File present |
| 4 | `skill.yml` required fields | `name`, `description`, `version`, `triggers` |
| 5 | `SKILL.md` has `## Configuration` section | Heading present |
| 6 | `SKILL.md` references trigger words | `trigger` keyword present |
| 7 | `tests/` has at least 1 file | Directory + ≥1 file |
| 8 | `CHANGELOG.md` exists | File present |

### Usage

```bash
bash scripts/validate-structure.sh <skill-dir>
```

### Example

```bash
bash scripts/validate-structure.sh /tmp/skill-release-my-skill

# Output:
# Structure validation: /tmp/skill-release-my-skill
# ──────────────────────────────────────────
#   ✅ SKILL.md exists
#   ✅ skill.yml exists
#   ✅ README.md exists
#   ✅ skill.yml has required fields (name, description, version, triggers)
#   ✅ SKILL.md has ## Configuration section
#   ✅ SKILL.md references trigger words
#   ✅ tests/ directory exists with 1 file(s)
#   ✅ CHANGELOG.md exists
# ──────────────────────────────────────────
# Score: 8/8
#
# ✅ PASS — structure complete
```

### Exit codes

- `0` — 8/8 score (PASS)
- `1` — score below 8/8 (FAIL)

---

## validate-release-content.sh

Checks that a release directory contains no unfinished placeholder text,
no empty files, and a substantive README.md. Guards against accidentally
publishing skeleton/template content.

### Checks

| # | Check | Criteria |
|---|-------|----------|
| 1 | No placeholder text | No `{{`, `TODO`, `FIXME`, or `YOUR_` in text files |
| 2 | No empty files | All files ≥ 50 bytes |
| 3 | README.md is substantive | `README.md` ≥ 200 characters |

### Usage

```bash
bash scripts/validate-release-content.sh <skill-dir>
```

### Example

```bash
bash scripts/validate-release-content.sh /tmp/skill-release-my-skill

# Output:
# Release content validation: /tmp/skill-release-my-skill
# ──────────────────────────────────────────
#   ✅ PASS — No placeholder text found ({{, TODO, FIXME, YOUR_)
#   ✅ PASS — No empty files (all files ≥ 50 bytes)
#   ✅ PASS — README.md has 842 chars (≥ 200 required)
# ──────────────────────────────────────────
#
# ✅ PASS — release content is clean
```

### Exit codes

- `0` — all checks pass
- `1` — one or more checks failed

---

## opsec-scan.sh

Scans a skill release directory for sensitive data before public release.

**Primary mode:** delegates to
`/tmp/openclaw-knowledge/refactory/scripts/validate-job-output.py`
(the full refactory OPSEC scanner).

**Fallback mode:** grep-based scan when the Python scanner is not available.

### Fallback patterns

| Pattern | Detects | Excluded |
|---------|---------|---------|
| Personal emails | `user@domain.tld` | `@example.com`, `@localhost`, `@openclaw.ai` |
| IP addresses | `x.x.x.x` | `127.x`, `192.0.2.x`, `0.0.0.0`, `10.x`, `172.16-31.x` |
| Absolute paths | `/Users/<name>/`, `/home/<name>/` | Lines marked as examples/placeholders |
| Credential tokens | AWS keys, GitHub tokens, OpenAI keys, Google API keys | — |

### Usage

```bash
bash scripts/opsec-scan.sh <skill-dir>
```

### Example — clean

```bash
bash scripts/opsec-scan.sh /tmp/skill-release-my-skill

# OPSEC scan: /tmp/skill-release-my-skill
# ──────────────────────────────────────────
#   Using: refactory/scripts/validate-job-output.py
#
# ✅ CLEAN — refactory scanner found no violations
```

### Example — violations found

```bash
bash scripts/opsec-scan.sh /tmp/skill-release-my-skill

# OPSEC scan: /tmp/skill-release-my-skill
# ──────────────────────────────────────────
#   Refactory scanner not available — using fallback grep scan
#
#   ❌ Hardcoded absolute paths (/Users/, /home/) found:
#     README.md:12:  cp ~/skills/my-skill ~/.openclaw/skills/
#
# ❌ BLOCKED — OPSEC violations found (see above)
#    Fix violations in the release copy before proceeding.
#    Do NOT modify the source in openclaw-knowledge.
```

> **Important:** Fix violations in the **release copy** (`/tmp/skill-release-*/`)
> only. Never modify the source skill directory — internal notes and references
> are intentionally preserved in the internal repo.

### Exit codes

- `0` — CLEAN (no violations)
- `1` — BLOCKED (violations found)

---

## Pipeline Integration

These scripts are called in sequence during the skill-releaser pipeline:

```
Step 1:  validate-structure.sh      → must score 8/8
Step 5:  validate-release-content.sh → must exit 0
Step 6:  opsec-scan.sh              → must exit 0
```

All three must pass before the release is staged for user review.
