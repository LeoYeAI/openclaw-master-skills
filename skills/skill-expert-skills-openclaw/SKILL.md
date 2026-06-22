---
name: skill-expert-skills
description: |
  Creates, optimizes, validates, and packages AI Agent Skills (SKILL.md format).

  Mandatory 6-Phase workflow with quality gates:
  Phase 0: Task Classification + Hypothesis Generation
  Phase 1: Deep Requirement Mining + 5 Whys
  Phase 2: Knowledge Acquisition + Validation
  Phase 3: Skill Writing + Quality Check
  Phase 4: Validation + User Confirmation
  Phase 5: Self-Reflection + Knowledge Precipitation

  Use when:
  - Creating a new Skill (writing a SKILL.md)
  - Optimizing an existing Skill (structure, triggers, portability)
  - Validating a Skill package
  - Packaging or distributing a Skill

  Not for: regular programming or business logic (use domain-specific skills).
license: Apache-2.0
compatibility: Python 3.8+ for validation scripts
allowed-tools: Read Write Bash Grep Glob
metadata:
  version: 4.0.0
  last_updated: 2026-03-06
  enhancement:
    - v4.0 Added Fast Track Decision (Simple/Standard/Complex classification)
    - v4.0 Adopted reference pointer pattern (-> references/xxx.md)
    - v4.0 Added SKILL.md Positioning rules (NON-NEGOTIABLE)
    - v4.0 Added Conciseness Checklist (5-point)
    - v4.0 Consolidated references navigation (phase-based)
    - v4.0 Kept Definition of Done and Source Credibility Tiers
---

# Skill Expert v4.0 — Universal Edition

Transform "create/optimize a Skill" requests into **triggerable, reusable,
maintainable, verifiable** Skill packages with quality gates.

> **Principles**: Expertise First | User Confirmation First | Conciseness | Universality

---

## Pre-Flight Check

| # | Checkpoint | Status |
|---|------------|--------|
| 1 | Read this SKILL.md? | [ ] |
| 2 | Identified task type? (Create / Optimize / Validate / Package) | [ ] |
| 3 | Ready to classify complexity? (Simple / Standard / Complex) | [ ] |

---

## Fast Track Decision

After identifying task type, classify complexity to choose the execution path:

```
Task Classification
    |
    +-- Simple Skill (minimal template, < 100 lines, well-known domain)
    |   -> FAST TRACK: Phase 0 -> Phase 3 -> Phase 4
    |
    +-- Standard Skill (with references, 100-500 lines)
    |   -> STANDARD: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5
    |
    +-- Complex Skill (knowledge-intensive, domain expertise needed)
    |   -> FULL: All phases with deep research
    |
    +-- Validate/Package Only
        -> Jump to Phase 4 / Command Reference
```

---

## Phase 0: Discovery + Hypothesis

**Goal**: Understand the real need, check for existing skills.

### 0.1 Task Classification

| Type | Action |
|------|--------|
| **Create New** | Continue to 0.2 |
| **Optimize Existing** | Continue to 0.2 |
| **Validate Only** | Skip to Command Reference |
| **Package Only** | Skip to Command Reference |

### 0.2 Skill Discovery (Reuse First)

-> `references/skill-discovery-protocol.md`

Search local skills first, then trusted external sources.

### 0.3 Hypothesis Generation + 5 Whys

-> `references/hypothesis-ladder-for-skills.md`

Generate 3-5 hypotheses about what the user really wants:

| Hypothesis Type | Example Question |
|-----------------|-----------------|
| **Scope** | Full solution or single function? |
| **Audience** | Novice or expert user? |
| **Trigger** | What scenarios activate this skill? |
| **Output** | Code, document, decision, or report? |
| **Depth** | Quick utility or comprehensive workflow? |

Validate with user. Use 5 Whys to uncover the deep need behind the surface request.

### GATE: Hypothesis Validation

| Condition | On Failure |
|-----------|------------|
| At least 1 hypothesis confirmed by user | Continue questioning |

---

## Phase 1: Requirement Mining

**Goal**: Get to the REAL problem, validate it, confirm with user.

### 1.1 Three-Stage Elicitation

-> `references/requirement-elicitation-protocol.md`

```
Stage 1: Explicit (5W1H)  ->  Stage 2: Implicit (4 methods)  ->  Stage 3: Validation
```

### 1.2 Skill Type Classification

-> `references/skill-type-taxonomy.md`

Quick question to determine type (~80% accuracy):
```
1) Comprehensive "summary"    2) Key-only "insight/diagnosis"
3) Produce "new content"      4) Reach a "conclusion"
```

### 1.3 Non-Technical Methodology (if applicable)

-> `references/non-technical-methodology-research.md`

For judgment-heavy domains: find experts, golden examples, anti-patterns.

### 1.4 User Confirmation

-> `references/user-confirmation-protocol.md`

Present requirements summary → get explicit user confirmation.

### GATE: Requirement Gate

| Condition | On Failure |
|-----------|------------|
| User explicitly confirms requirements | Redo mining |

---

## Phase 2: Knowledge Acquisition

**Goal**: Become an expert BEFORE writing.

### 2.1 Research Workflow

-> `references/knowledge-acquisition-guide.md`

```
LLM baseline -> Extract domains -> Research with tools -> Cross-validate -> Gate -> Self-check
```

**Use whatever tools are available in your environment:**
- Documentation lookup tools (official docs first)
- Web search tools (for latest practices, at least 3 sources)
- Code search tools (for real-world examples)
- URL fetch tools (for specific references)

If no external tools available, rely on own knowledge but mark it as "unverified".

### 2.2 Source Credibility Tiers

| Tier | Source Type | Trust Level |
|------|-----------|-------------|
| S | Official docs, official blog | Highest — use directly |
| A | Official GitHub, official examples | High — use directly |
| B | Known tech blogs, high-vote StackOverflow | Medium — cross-validate |
| C | Personal blogs, forums | Low — must multi-source verify |
| D | Unknown source, AI-generated | Lowest — must verify against official |

### 2.3 Deep Research (Complex skills only)

-> `references/deep-research-methodology.md`

Five-layer knowledge pyramid: Basics -> Principles -> Practice -> Expert -> Frontier.

### GATE: Knowledge Gate (Composite)

All 4 sub-checks must pass as a single gate:

| Sub-Check | Pass Condition |
|-----------|----------------|
| Freshness | Source date < 1 year, grade A/B |
| Accuracy | Official source + 2 independent confirmations |
| Completeness | Core features 100%, scenarios 80%+ |
| Fusion | LLM vs fresh knowledge compared, conflicts resolved |

-> `references/knowledge-validation-checklist.md` for details

---

## Phase 3: Skill Writing

**Goal**: Write the skill following enterprise patterns.

### 3.1 SKILL.md Positioning (NON-NEGOTIABLE)

```
SKILL.md SHOULD be:
  ✅ Scannable in 30 seconds (table of contents)
  ✅ Decision tree: "what situation → which action/file"
  ✅ Command reference: one-line key commands
  ✅ Minimal necessary constraints/contracts

SKILL.md should NOT be:
  ❌ Detailed knowledge base or tutorials
  ❌ Complete protocol explanations
  ❌ Long examples or code blocks
  ❌ Background knowledge

→ All detailed content MUST go to references/
```

### 3.2 Conciseness Checklist

- [ ] New content > 20 lines? → Move to references/
- [ ] Does AI need this every invocation? → If not, move to references/
- [ ] Can it be a one-line pointer? → Use `→ references/xxx.md`
- [ ] Body < 500 lines? → Hard limit 800 lines
- [ ] Contains tech-stack specific content? → Abstract or move to references/

### 3.3 Template Selection

-> `references/skill-templates.md`

| Template | When | Complexity | Files |
|----------|------|-----------|-------|
| **Minimal** | Quick utility, personal preference | Low | 1 |
| **Read-only** | Analysis, audit, review (no file changes) | Low | 1-2 |
| **Script-driven** | Automation, repeatable tasks | Medium | 3+ |
| **Knowledge-intensive** | Expert domain, multi-phase workflow | High | 5+ |

### 3.4 Frontmatter Specification

```yaml
---
name: my-skill              # Required. hyphen-case, ≤64 chars, matches directory name
description: |               # Required. ≤1024 chars, third person, no < >
  What this skill does.
  Use when:
  - scenario 1
  - scenario 2
  Not for: X, Y.
license: MIT                 # Optional
compatibility: Python 3.8+   # Optional. ≤500 chars
allowed-tools: Read Write    # Optional. space-delimited tool names
metadata:                    # Optional. extension fields
  version: 1.0.0
---
```

### 3.5 Directory Structure

```
my-skill/
├── SKILL.md              # Required: instructions + metadata
├── scripts/              # Optional: executable code
│   ├── main.py
│   └── requirements.txt
├── references/           # Optional: detailed docs (loaded into context)
│   ├── patterns.md
│   └── checklist.md
└── assets/               # Optional: templates, images (NOT loaded into context)
    └── template.md
```

### 3.6 Writing Standards

-> `references/writing-style-guide.md`
-> `references/universality-guide.md`

### GATE: Writing Gate

| Condition | On Failure |
|-----------|------------|
| Pre-invocation check passed | Fix parameters, retry |
| Post-invocation check passed | Log warning, retry |

---

## Phase 4: Quality Validation + User Confirmation

**Goal**: Ensure output meets quality standards and user needs.

### 4.1 Structural Validation Checklist

| Check | Criteria |
|-------|----------|
| Frontmatter | Has `name` + `description`, valid YAML |
| Name | hyphen-case, ≤64 chars, matches directory |
| Description | Third person, 3-5 triggers, has "Use when" + "Not for" |
| Body length | < 500 lines (warn at 500, error at 800) |
| No angle brackets | Description has no `<` or `>` |
| References used | Detailed content in references/, not SKILL.md body |
| Output Contract | Defined what the skill produces |
| Decision Tree | AI knows "what situation → which action" |

### 4.2 Portability Checklist

| Check | Criteria |
|-------|----------|
| No hardcoded paths | No absolute paths or project-specific directories |
| No hardcoded tool names | Uses generic tool categories, not specific MCP servers |
| No project-specific context | Works without knowledge of a specific codebase |
| Synthetic examples | Examples are self-contained, not from a real project |
| Platform-agnostic | Works in any AI coding assistant environment |

### 4.3 User Final Confirmation

-> `references/user-confirmation-protocol.md`

Present: validation results + deliverables + features summary. Get explicit confirmation.

### GATE: Delivery Gate

| Condition | On Failure |
|-----------|------------|
| Validation checks pass | Fix and re-validate |
| User explicitly confirms | Fix and re-confirm |

---

## Phase 5: Self-Reflection + Knowledge Precipitation

**Goal**: Learn from the experience.

### 5.1 Self-Reflection Report

```markdown
## Self-Reflection

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Requirement Understanding | [1-5] | [notes] |
| Knowledge Completeness | [1-5] | [notes] |
| Output Quality | [1-5] | [notes] |
| User Satisfaction | [1-5] | [notes] |
| **Total** | **[/20]** | |

| Problem | Cause | Prevention |
|---------|-------|------------|
| [issue] | [why] | [measure] |
```

### 5.2 Knowledge Precipitation

- [ ] Document lessons learned
- [ ] Update references if new patterns discovered
- [ ] Note what worked well for future skills

### GATE: Reflection Complete

| Condition | On Failure |
|-----------|------------|
| Score + analysis documented | Complete before closing |

---

## Decision Tree

```
【Create New Skill】
  Phase 0: Classify task → Generate hypotheses → [Fast Track?] → User confirms
  Phase 1: 5 Whys → Skill Type → Validate requirements → User confirms
  Phase 2: Research domain → 4-Layer knowledge gate
  Phase 3: Select template → Write SKILL.md → Conciseness check
  Phase 4: Structural validation → Portability check → User confirms
  Phase 5: Self-reflect → Precipitate knowledge

【Optimize Existing Skill】
  Phase 0: Classify → Hypothesize what to improve → [Fast Track?] → User confirms
  Phase 1: 5 Whys on current pain points → User confirms
  Phase 2: Research latest patterns → 4-Layer gate
  Phase 3: Modify SKILL.md → Conciseness check
  Phase 4: Validate → User confirms
  Phase 5: Self-reflect → Document changes

【Validate / Package Only】
  -> Phase 4: Run validation scripts → Report results
```

---

## Command Reference

Run from **project root**:

```bash
# Search installed skills (reuse-first)
python scripts/search_skills.py "<keyword>" --root <skills-directory>

# Initialize new skill
python scripts/init_skill.py <skill-name> --path <skills-directory>

# Validate (required before delivery)
python scripts/quick_validate.py <skill-directory>
python scripts/universal_validate.py <skill-directory>

# Package for distribution (optional)
python scripts/package_skill.py <skill-directory> ./dist

# Maintenance
python scripts/upgrade_skill.py <skill-directory>
python scripts/diff_with_official.py <skill-directory>
python scripts/analyze_trigger.py <skill-directory>
```

---

## Key Constraints

| Item | Constraint |
|------|------------|
| `name` | hyphen-case, ≤64 chars, must match directory name |
| `description` | No `< >`, ≤1024 chars, third person, 3-5 triggers |
| `license` | Optional, license name or reference to bundled file |
| `compatibility` | Optional, ≤500 chars, environment requirements |
| `allowed-tools` | Optional, space-delimited tool names |
| SKILL.md body | < 500 lines recommended, hard limit 800 |
| Universality | No project paths, no hardcoded tool names, portable examples |

---

## Output Contract

**Required**: Updated `SKILL.md` + change summary (triggers, domains, validation results)

**On-demand**: `references/` | `scripts/` | `assets/`

---

## Gate System Summary

| Gate | Phase | Pass Condition | On Failure |
|------|-------|----------------|------------|
| Hypothesis Validation | 0 | ≥1 hypothesis confirmed by user | Keep asking |
| User Confirmation | 1 | User explicitly confirms requirements | Redo mining |
| Knowledge Freshness | 2 | Source < 1 year old | Re-acquire |
| Knowledge Accuracy | 2 | Official + 2 independent sources | Cross-validate |
| Knowledge Completeness | 2 | Core 100%, scenarios 80%+ | Supplement |
| Knowledge Fusion | 2 | Own vs new knowledge compared | Must compare |
| Writing Gate | 3 | Pre/post invocation checks pass | Fix and retry |
| Delivery Gate | 4 | Scripts pass + user confirms | Fix and redo |
| Reflection Complete | 5 | Score + analysis done | Complete it |

---

## Definition of Done

**Complete ALL before declaring done:**

### Phase 0-1: Understanding
- [ ] Task type identified
- [ ] 3-5 hypotheses generated, ≥1 confirmed
- [ ] 5 Whys completed
- [ ] User explicitly confirmed requirements

### Phase 2: Knowledge
- [ ] Domain researched (used available tools or marked as unverified)
- [ ] Freshness, accuracy, completeness gates passed
- [ ] Own knowledge vs findings compared

### Phase 3: Writing
- [ ] SKILL.md body < 500 lines
- [ ] Frontmatter valid (name, description)
- [ ] Detailed content in references/ (not body)
- [ ] Has decision tree or workflow
- [ ] Has output contract

### Phase 4: Validation
- [ ] Structural checks passed
- [ ] Portability checks passed (no hardcoded paths/tools/projects)
- [ ] User explicitly confirmed output

### Phase 5: Reflection
- [ ] Quality score calculated
- [ ] Improvement areas documented
- [ ] Lessons captured

**Self-check**: Did I follow Phase 0 → 1 → 2 → 3 → 4 → 5 in order?
If phases were skipped → go back and complete them.

---

## References Navigation

### Core Phase References

| File | Purpose | Phase |
|------|---------|-------|
| `hypothesis-ladder-for-skills.md` | Hypothesis generation + 5 Whys | 0 |
| `skill-discovery-protocol.md` | Skill discovery (reuse-first) | 0 |
| `task-narrowing-framework.md` | Task narrowing (5-layer) | 0 |
| `requirement-elicitation-protocol.md` | Requirement elicitation | 1 |
| `user-requirement-validation.md` | Requirement validation | 1 |
| `user-confirmation-protocol.md` | User confirmation template | 1, 4 |
| `skill-type-taxonomy.md` | Skill type taxonomy | 1 |
| `knowledge-acquisition-guide.md` | Research protocol + 4-layer gate | 2 |
| `knowledge-validation-checklist.md` | Knowledge validation | 2 |
| `deep-research-methodology.md` | Deep research + domain expertise | 2 |
| `skill-templates.md` | Skill structure templates | 3 |
| `writing-style-guide.md` | Writing standards + style | 3 |
| `universality-guide.md` | Portability guide | 3 |

### Supporting References

| File | Purpose |
|------|---------|
| `non-technical-methodology-research.md` | Non-technical methodology |
| `methodology-seed-database.md` | Methodology seed database |
| `learn-from-github-protocol.md` | Learn from GitHub protocol |
| `domain-expertise-protocol.md` | Domain expertise protocol |
| `docs-generation-workflow.md` | Docs generation workflow |
| `examples.md` | Complete examples + patterns |
| `patterns.md` | Workflow patterns |
| `troubleshooting.md` | Common issues and fixes |
| `official-best-practices.md` | Anthropic official guidelines |

### Official Resources

| Resource | URL |
|----------|-----|
| AgentSkills.io | https://agentskills.io/ |
| Skills Overview | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Best Practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Anthropic Skills Repo | https://github.com/anthropics/skills |
