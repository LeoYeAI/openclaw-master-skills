---
name: eigenskill-builder
description: 'Meta-skill for building and publishing agent skills on ClawHub. Covers skill structure, YAML frontmatter specification, references directory convention, negative boundaries, installation instructions, ClawHub CLI workflow, and quality checklist. The skill that teaches agents to build skills. Do NOT use for prompt engineering, agent memory, or orchestration — those have their own dedicated skills.'
license: MIT
metadata:
  openclaw:
    emoji: '🔄'
---

# Eigenskill Builder

The meta-skill. This skill teaches AI agents how to build, validate, and publish skills on ClawHub. If you're creating a new skill, this is your blueprint.

## When to Use

- Creating a new skill from scratch
- Validating an existing skill against quality standards
- Publishing a skill to ClawHub
- Designing skill descriptions with proper trigger/exclusion boundaries
- Setting up references/ directories for supplementary material
- Planning skill graphs for large skill libraries (50+)

## When NOT to Use

- Writing prompts or prompt templates (use a prompt-engineering skill)
- Building agent memory systems (use agent-memory-architecture)
- Orchestrating multiple agents (use agent-orchestration)
- Fine-tuning models or training data preparation
- Building MCP servers or tools (that's tool development, not skill development)

---

## 1. Skill Anatomy

Every skill is a directory containing at minimum a `SKILL.md` file. The directory name should be kebab-case and match the skill name.

### Directory Structure

```
skills/
  my-skill-name/
    SKILL.md              # Required: the skill definition
    references/           # Optional: supplementary material
      api-docs.md
      examples.md
      cheatsheet.md
    scripts/              # Optional: automation scripts
      validate.sh
      install.sh
```

### SKILL.md Structure

```markdown
---
name: my-skill-name
description: 'One paragraph. What it does. When to trigger. When NOT to trigger.'
license: MIT
metadata:
  openclaw:
    emoji: '🔧'
---

# Skill Title

[Brief overview — 2-3 sentences max]

## When to Use
[Bulleted list of trigger conditions]

## When NOT to Use
[Bulleted list of exclusion conditions — REQUIRED]

---

## Section 1: [Topic]
[Content with examples]

## Section 2: [Topic]
[Content with examples]

...
```

---

## 2. YAML Frontmatter Specification

The frontmatter block is the machine-readable identity of the skill. It must be valid YAML between `---` delimiters.

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Kebab-case identifier, unique on ClawHub | `financial-analysis-agent` |
| `description` | string | Single-quoted paragraph. Must include trigger AND exclusion. | See below |
| `license` | string | SPDX identifier | `MIT`, `Apache-2.0`, `CC-BY-4.0` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `version` | string | Semver | `1.0.0` |
| `author` | string | Creator name or handle | `@openclaw` |
| `tags` | list | Discovery tags | `[finance, analysis, cfp]` |
| `depends` | list | Other skills this depends on | `[agent-memory-architecture]` |
| `metadata.openclaw.emoji` | string | Display emoji on ClawHub | `'💰'` |
| `metadata.openclaw.tier` | string | Complexity tier | `foundational`, `intermediate`, `advanced` |
| `metadata.openclaw.models` | list | Models this skill works best with | `[claude-opus-4-6, claude-sonnet-4-6]` |

### Description Best Practices

The description field is the most important field. It's what agents use to decide whether to load the skill. It must be:

1. **Specific** — list the concrete things the skill covers
2. **Bounded** — say what it does NOT cover
3. **Trigger-rich** — include keywords an agent would search for

**Good:**
```yaml
description: 'Financial analysis skill for AI agents. Covers variance analysis, cash flow forecasting, month-end close automation, CFO commentary generation. Do NOT use for tax preparation, audit opinions, or regulatory filings.'
```

**Bad:**
```yaml
description: 'A skill for finance stuff.'
```

**Bad:**
```yaml
description: 'Comprehensive enterprise-grade financial analysis solution leveraging AI-powered insights for transformative business intelligence.'
```

---

## 3. References Directory Convention

The `references/` directory holds supplementary material that the skill can point to but that shouldn't be in the main SKILL.md (to keep it focused).

### Rules

1. **One level deep only** — `references/file.md` is fine. `references/sub/file.md` is not.
2. **Never chain references** — a reference file should not reference another reference file. References are leaves, not nodes.
3. **Keep references self-contained** — each file should make sense on its own without reading SKILL.md first.
4. **Name descriptively** — `api-authentication.md` not `ref1.md`.

### When to Use References vs Inline Content

| Content Type | Location | Rationale |
|-------------|----------|-----------|
| Core methodology | SKILL.md | Agent needs this to execute |
| Quick reference tables | SKILL.md | Frequently accessed |
| Detailed API docs | references/ | Only needed for specific tasks |
| Extended examples | references/ | Useful but not essential |
| Cheat sheets | references/ | Quick lookup, not learning |
| Historical context | references/ | Background, not action |

### Example References Directory

```
skills/financial-analysis-agent/
  SKILL.md
  references/
    gaap-ifrs-differences.md      # Detailed comparison table
    ratio-benchmarks-by-industry.md  # Industry-specific ratio ranges
    asc-606-checklist.md           # Revenue recognition deep dive
    sample-board-package.md        # Example board reporting package
```

---

## 4. Negative Boundaries

Every skill MUST define what it does NOT do. This is not optional — it's the most important part of skill design after the core content.

### Why Negative Boundaries Matter

Without negative boundaries:
- Agents load wrong skills for tasks → bad output
- Skills overlap silently → conflicts and confusion
- Users don't know where one skill ends and another begins

### The Exclusion Checklist

For every skill, explicitly answer:

1. **Adjacent skills** — What similar skills exist that this one is NOT?
2. **Common misconceptions** — What do people assume this covers that it doesn't?
3. **Scope ceiling** — What's the most complex thing this skill can handle? What's above that ceiling?
4. **Scope floor** — What's too simple for this skill? (e.g., "don't use this to add two numbers")

### Template

```markdown
## When NOT to Use

- [Adjacent skill 1] — use [other-skill-name] instead
- [Adjacent skill 2] — use [other-skill-name] instead
- [Common misconception] — this skill does not cover [X]
- Tasks requiring [thing above scope ceiling] — escalate to [human/specialist]
- Simple [thing below scope floor] — just do it directly, no skill needed
```

### Example

```markdown
## When NOT to Use

- Tax preparation or tax advisory — use crypto-tax-agent or consult a CPA
- Audit opinions or attestation — requires human CPA, not an agent skill
- Regulatory filings (SEC 10-K, etc.) — use a compliance-specific skill
- Simple arithmetic or unit conversions — just calculate directly
- Investment advice or stock picks — this is analysis, not advisory
```

---

## 5. Description Interview Process

When building a new skill, interview yourself (or the skill author) with these questions to produce a high-quality description.

### The Interview

#### Step 1: Define Triggers

```
Q: What specific phrases would someone say that should activate this skill?
A: List 5-10 trigger phrases.

Example:
- "Analyze the variance between budget and actual"
- "Generate a 13-week cash flow forecast"
- "Write CFO commentary for the board package"
- "Review the financial statements before close"
```

#### Step 2: Define Exclusions

```
Q: What phrases sound similar but should NOT activate this skill?
A: List 5-10 exclusion phrases.

Example:
- "File our tax return" → tax skill, not this one
- "Should we invest in X stock?" → not advisory
- "Audit the financial statements" → requires CPA
```

#### Step 3: Define Dependencies

```
Q: What other skills or knowledge does this skill assume?
A: List prerequisites.

Example:
- Basic accounting knowledge (debits/credits)
- Access to financial data (GL, subledger)
- Familiarity with Excel/Sheets for output formatting
```

#### Step 4: Write the Description

Combine triggers, exclusions, and dependencies into a single paragraph:

```yaml
description: '[What it does — 1 sentence]. Covers [trigger keywords]. Assumes [dependencies]. Do NOT use for [exclusions].'
```

#### Step 5: Test the Description

Ask: "If an agent read only this description, would it correctly decide to load or skip this skill for these 10 test queries?"

Test with 5 queries that SHOULD trigger and 5 that should NOT.

---

## 6. Scripts Directory

The `scripts/` directory holds automation for skill lifecycle operations.

### Common Scripts

```bash
# scripts/validate.sh — Check skill quality
#!/bin/bash
set -euo pipefail

SKILL_DIR="$(dirname "$0")/.."
SKILL_FILE="$SKILL_DIR/SKILL.md"

# Check SKILL.md exists
[[ -f "$SKILL_FILE" ]] || { echo "FAIL: SKILL.md not found"; exit 1; }

# Check frontmatter exists
head -1 "$SKILL_FILE" | grep -q "^---$" || { echo "FAIL: Missing frontmatter"; exit 1; }

# Check required fields
grep -q "^name:" "$SKILL_FILE" || { echo "FAIL: Missing name field"; exit 1; }
grep -q "^description:" "$SKILL_FILE" || { echo "FAIL: Missing description field"; exit 1; }
grep -q "^license:" "$SKILL_FILE" || { echo "FAIL: Missing license field"; exit 1; }

# Check negative boundaries exist
grep -q "When NOT to Use" "$SKILL_FILE" || { echo "FAIL: Missing negative boundaries"; exit 1; }

# Check description includes exclusions
DESC=$(grep "^description:" "$SKILL_FILE")
echo "$DESC" | grep -qi "not\|don't\|do not\|except\|exclud" || {
    echo "WARN: Description may lack exclusion language"
}

# Check references depth
if [[ -d "$SKILL_DIR/references" ]]; then
    DEPTH=$(find "$SKILL_DIR/references" -mindepth 2 -type f | wc -l)
    [[ "$DEPTH" -eq 0 ]] || { echo "FAIL: References nested >1 level deep"; exit 1; }
fi

echo "PASS: Skill validation complete"
```

```bash
# scripts/install.sh — Install skill into agent workspace
#!/bin/bash
set -euo pipefail

SKILL_NAME="$(basename "$(dirname "$0")/..")"
TARGET="${1:-$HOME/.openclaw/workspace/skills}"

echo "Installing $SKILL_NAME to $TARGET/$SKILL_NAME"
cp -r "$(dirname "$0")/.." "$TARGET/$SKILL_NAME"
echo "Done. Skill available at $TARGET/$SKILL_NAME/SKILL.md"
```

---

## 7. ClawHub CLI Workflow

ClawHub is the registry for discovering, installing, and publishing skills.

### Commands

```bash
# Search for skills
clawhub search "financial analysis"
clawhub search --tag finance
clawhub search --emoji 💰

# View skill details
clawhub info financial-analysis-agent
clawhub info financial-analysis-agent --versions

# Install a skill
clawhub install financial-analysis-agent
clawhub install financial-analysis-agent@1.2.0
clawhub install financial-analysis-agent --path ./my-skills/

# Publish a skill
clawhub publish ./skills/my-skill/
clawhub publish ./skills/my-skill/ --dry-run  # Validate without publishing

# Update skills
clawhub update                          # Update all installed skills
clawhub update financial-analysis-agent  # Update specific skill
clawhub outdated                         # List skills with available updates

# List installed skills
clawhub list
clawhub list --format json
```

### Publishing Checklist (Pre-publish)

Before running `clawhub publish`:

1. `scripts/validate.sh` passes
2. Description includes trigger AND exclusion language
3. All examples are tested and working
4. References are one level deep only
5. No secrets, API keys, or credentials in any file
6. License is specified and compatible
7. Version is bumped if updating existing skill

### Publishing Flow

```
1. Author creates skill locally
2. Run: clawhub publish ./skills/my-skill/ --dry-run
3. Fix any validation errors
4. Run: clawhub publish ./skills/my-skill/
5. ClawHub assigns a unique ID and indexes the skill
6. Skill appears in search results within 5 minutes
7. Other agents can install via: clawhub install my-skill
```

---

## 8. Quality Checklist

Score every skill against these 10 criteria before publishing.

| # | Criterion | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 1 | **SKILL.md exists** with valid YAML frontmatter | Required | Must parse without errors |
| 2 | **Name is kebab-case** and unique | Required | Check `clawhub search` first |
| 3 | **Description is specific** with triggers AND exclusions | Required | >50 chars, <500 chars |
| 4 | **"When to Use" section** with 3+ bullet points | Required | Concrete, not vague |
| 5 | **"When NOT to Use" section** with 3+ bullet points | Required | Names alternative skills |
| 6 | **Actionable content** — agent can execute, not just read | Required | Include templates, formulas, steps |
| 7 | **Examples** for every major concept | Recommended | Show input → output |
| 8 | **References one level deep** (if references/ exists) | Required | No nested references |
| 9 | **No secrets or credentials** in any file | Required | Scan before publish |
| 10 | **License specified** and SPDX-valid | Required | MIT, Apache-2.0, etc. |

### Scoring

```
10/10 — Ready to publish
8-9/10 — Minor fixes needed, publishable
6-7/10 — Needs work, don't publish yet
<6/10 — Fundamental issues, redesign needed
```

---

## 9. Version Management

### Semver for Skills

```
MAJOR.MINOR.PATCH

MAJOR — Breaking changes to skill structure or content that would change agent behavior
MINOR — New content sections, expanded examples, new references
PATCH — Typo fixes, clarifications, formatting improvements
```

### Version Bump Rules

| Change | Bump | Example |
|--------|------|---------|
| Fix a typo in an example | PATCH | 1.0.0 → 1.0.1 |
| Add a new section on ratio analysis | MINOR | 1.0.1 → 1.1.0 |
| Restructure from 5 sections to 10 | MAJOR | 1.1.0 → 2.0.0 |
| Change the description triggers | MAJOR | 2.0.0 → 3.0.0 |
| Add a reference file | MINOR | 1.0.0 → 1.1.0 |
| Update examples for new API version | MINOR | 1.1.0 → 1.2.0 |

### Changelog Convention

Add a `## Changelog` section at the bottom of SKILL.md for significant versions:

```markdown
## Changelog

### 2.0.0 (2026-03-15)
- Restructured from 5 to 9 sections
- Added aging analysis and bank reconciliation
- Breaking: removed deprecated ratio shortcuts

### 1.1.0 (2026-03-01)
- Added CFO commentary templates
- New reference: sample-board-package.md

### 1.0.0 (2026-02-15)
- Initial release
```

---

## 10. Skill Graphs

When your skill library grows past ~50 skills, you need a way to discover relationships between skills. Skill graphs solve this.

### Concept

Each skill can declare relationships to other skills using two mechanisms:

1. **YAML `depends` field** — hard dependencies (skill won't work without these)
2. **Wikilinks in content** — soft references (related but not required)

### YAML Dependencies

```yaml
depends:
  - agent-memory-architecture    # Required: this skill uses memory patterns
  - agent-orchestration          # Required: this skill uses orchestration patterns
```

### Wikilinks in Content

Use `[[skill-name]]` syntax to create soft links:

```markdown
For memory patterns used in financial analysis workflows, see [[agent-memory-architecture]].

When orchestrating multiple financial analysis agents, apply the patterns in [[agent-orchestration]].
```

### Graph Queries

With a skill graph, you can answer:

```
"What skills does financial-analysis-agent depend on?"
  → agent-memory-architecture, agent-orchestration

"What skills reference financial-analysis-agent?"
  → eigenskill-builder (as example), cfo-reporting-agent

"What's the shortest path from crypto-tax-agent to agent-orchestration?"
  → crypto-tax-agent → financial-analysis-agent → agent-orchestration

"What are the foundational skills (most depended on)?"
  → agent-memory-architecture (12 dependents)
  → agent-orchestration (8 dependents)
  → eigenskill-builder (6 dependents)
```

### Building the Graph

```python
import yaml
import re
from pathlib import Path

def build_skill_graph(skills_dir: Path) -> dict:
    """Build a dependency graph from all skills."""
    graph = {"nodes": {}, "edges": []}

    for skill_dir in skills_dir.iterdir():
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text()

        # Parse frontmatter
        fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            continue
        fm = yaml.safe_load(fm_match.group(1))

        name = fm.get("name", skill_dir.name)
        graph["nodes"][name] = {
            "description": fm.get("description", ""),
            "emoji": fm.get("metadata", {}).get("openclaw", {}).get("emoji", ""),
        }

        # Hard dependencies (YAML)
        for dep in fm.get("depends", []):
            graph["edges"].append({
                "from": name, "to": dep, "type": "depends"
            })

        # Soft references (wikilinks)
        for link in re.findall(r'\[\[([\w-]+)\]\]', content):
            if link != name:  # No self-links
                graph["edges"].append({
                    "from": name, "to": link, "type": "references"
                })

    return graph
```

### Visualization

For small libraries (<20), a simple ASCII graph works:

```
eigenskill-builder ──depends──▶ agent-orchestration
       │                              ▲
       │                              │
       ▼                              │
financial-analysis-agent ──references─┘
       │
       ▼
crypto-tax-agent
```

For larger libraries, export to DOT format and render with Graphviz, or use a JSON graph viewer.
