---
name: issue-prioritizer
description: Prioritize GitHub issues by ROI, solution sanity, and architectural impact. Use when triaging or ranking issues to identify quick wins, over-engineered proposals, and actionable bugs. Don't use when managing forks (use fork-manager) or general GitHub queries (use github). Read-only — never modifies repositories.
metadata: {"openclaw": {"requires": {"bins": ["gh"]}}}
---

# Issue Prioritizer

Analyze issues from a GitHub repository and rank them by **Adjusted Score** — ROI penalized by Tripping Scale (solution sanity), Architectural Impact, and Actionability.

This is a **read-only skill**. It analyzes and presents information. The user makes all decisions.

## When to use
- Triaging or ranking issues in a repository
- Identifying quick wins for contributors
- Filtering out non-actionable items (questions, duplicates)
- Detecting over-engineered proposals
- Matching issues to contributor skill levels

## When NOT to use
- Managing forks or syncing with upstream → use `fork-manager` instead
- General GitHub CLI queries (PR status, CI runs) → use `github` instead
- Reviewing code changes before publishing → use `pr-review` instead

## Requirements

- `gh` CLI authenticated (`gh auth login`)

## Instructions

### Step 1: Get Repository

If the user didn't specify a repository, ask which one to analyze (format: `owner/repo`).

### Step 2: Fetch Issues

**Basic fetch (most recent):**
```bash
gh issue list --repo {owner/repo} --state open --limit {limit} --json number,title,body,labels,createdAt,comments,url
```

Default limit is 30. Store the full JSON response.

**Targeted fetch with `--topic`:**

When the user specifies `--topic <keyword>` (e.g. `--topic telegram`, `--topic agents`), use GitHub search to find issues matching that topic instead of just fetching the most recent:

```bash
# Search by topic keywords in title and body
gh issue list --repo {owner/repo} --state open --limit {limit} --search "{topic} in:title,body" --json number,title,body,labels,createdAt,comments,url
```

Multiple topics can be combined: `--topic "telegram agents"` searches for issues containing either term.

**Targeted fetch with `--search`:**

When the user specifies `--search <query>`, pass it directly as a GitHub search query for full control:

```bash
gh issue list --repo {owner/repo} --state open --limit {limit} --search "{query}" --json number,title,body,labels,createdAt,comments,url
```

Examples:
- `--search "telegram in:title"` — only title matches
- `--search "label:bug telegram"` — bugs mentioning telegram
- `--search "label:bug,enhancement telegram agents"` — bugs or enhancements about telegram/agents
- `--search "comments:>5 telegram"` — active discussions about telegram

**Label-based fetch with `--label`:**

```bash
gh issue list --repo {owner/repo} --state open --limit {limit} --label "{label}" --json number,title,body,labels,createdAt,comments,url
```

All fetch modes can be combined: `--topic telegram --label bug --limit 50` fetches up to 50 open bugs about telegram.

**Error handling:**
- Auth error → tell user to run `gh auth login`
- Rate limited → inform user, suggest reducing `--limit`
- Repo not found → check format `owner/repo`
- No issues → report and exit (if using --topic/--search, suggest broadening the query)
- Missing fields → treat null/missing body and labels as empty

### Step 3: Filter Issues with Existing PRs

**Note:** If user specified `--include-with-prs`, skip this entire step and proceed to Step 4 with all fetched issues.

Before analyzing, check for open PRs that already address issues to avoid duplicate work.

```bash
gh pr list --repo {owner/repo} --state open --json number,title,body,url
```

**Detect linked issues** using ALL of these methods:

**Method 1 — Explicit Keywords** (high confidence):
Scan PR title and body (case-insensitive):
- `fixes #N`, `fix #N`, `fixed #N`
- `closes #N`, `close #N`, `closed #N`
- `resolves #N`, `resolve #N`, `resolved #N`

**Method 2 — Issue References** (medium confidence):
- `#N` anywhere in text
- `issue N`, `issue #N`, `related to #N`, `addresses #N`

**Method 3 — Title Similarity** (fuzzy):
Normalize titles (lowercase, remove punctuation/common words). If 70%+ word overlap → likely linked.

**Method 4 — Semantic Matching** (ambiguous cases):
Extract key terms from issue (error names, function names, components). Check if PR body discusses same things.

**Confidence icons:**
- 🔗 Explicit link (fixes/closes/resolves)
- 📎 Referenced (#N mentioned)
- 🔍 Similar title (fuzzy match)
- 💡 Semantic match (same components)

Remove linked issues from analysis. Report them separately before the main report.

If all issues have PRs, report that and exit.

### Step 4: Analyze Each Issue

For each remaining issue, score the following:

#### Difficulty (1-10)

Base score: 5. Adjustments:

| Signal | Adjustment |
|--------|-----------|
| Documentation only | -3 |
| Has proposed solution | -2 |
| Has reproduction steps | -1 |
| Clear error message | -1 |
| Unknown root cause | +3 |
| Architectural change | +3 |
| Race condition/concurrency | +2 |
| Security implications | +2 |
| Multiple systems involved | +2 |

#### Importance (1-10)

| Range | Level | Examples |
|-------|-------|---------|
| 8-10 | Critical | Crash, data loss, security vulnerability, service down |
| 6-7 | High | Broken functionality, errors, performance issues |
| 4-5 | Medium | Enhancements, feature requests, improvements |
| 1-3 | Low | Cosmetic, documentation, typos |

#### Tripping Scale (1-5) — Solution Sanity (How "Out There" Is It?)

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Total Sanity | Proven approach, standard patterns |
| 2 | Grounded w/Flair | Practical with creative touches |
| 3 | Dipping Toes | Exploring cautiously |
| 4 | Wild Adventure | Bold, risky, unconventional |
| 5 | Tripping | Questionable viability |

**Red Flags** (+score): rewrite from scratch, buzzwords (blockchain, AI-powered, ML-based), experimental/unstable, breaking change, custom protocol
**Green Flags** (-score): standard approach, minimal change, backward compatible, existing library, well-documented

#### Architectural Impact (1-5)

Always ask: "Is there a simpler way?" before scoring.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Surgical | Isolated fix, 1-2 files, no new abstractions |
| 2 | Localized | Small addition, follows existing patterns exactly |
| 3 | Moderate | New component within existing architecture |
| 4 | Significant | New subsystem, new patterns, affects multiple modules |
| 5 | Transformational | Restructures core, changes paradigms, migration needed |

**Red Flags** (+score): "rewrite", "refactor entire", new framework for existing capability, changes across >5 files, breaking API changes, scope creep
**Green Flags** (-score): single file fix, uses existing utilities, follows established patterns, backward compatible, easily revertible

**Critical:** If a simple solution exists, architectural changes are wrong. Don't create a "validation framework" when a single if-check suffices.

#### Actionability (1-5) — Can it be resolved with a PR?

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Not Actionable | Question, discussion, duplicate, support request |
| 2 | Needs Triage | Missing info, unclear scope, needs clarification |
| 3 | Needs Investigation | Root cause unknown, requires debugging first |
| 4 | Ready to Work | Clear scope, may need some design decisions |
| 5 | PR Ready | Solution is clear, just needs implementation |

**Blockers** (-score): questions ("how do I?"), discussions ("thoughts?"), labels (duplicate, wontfix, question), missing repro
**Ready signals** (+score): action titles ("fix:", "add:"), proposed solution, repro steps, good-first-issue label, specific files mentioned

#### Derived Values

```
issueType: "bug" | "feature" | "docs" | "other"
suggestedLevel:
  - "beginner": difficulty 1-3, no security/architecture changes
  - "intermediate": difficulty 4-6
  - "advanced": difficulty 7+ OR security implications OR architectural changes
```

#### Calculation Formulas

```
ROI = Importance / Difficulty
AdjustedScore = ROI × TripMultiplier × ArchMultiplier × ActionMultiplier
```

**Tripping Scale Multiplier:**

| Score | Label | Multiplier |
|-------|-------|------------|
| 1 | Total Sanity | 1.00 (no penalty) |
| 2 | Grounded w/Flair | 0.85 |
| 3 | Dipping Toes | 0.70 |
| 4 | Wild Adventure | 0.55 |
| 5 | Tripping | 0.40 |

**Architectural Impact Multiplier:**

| Score | Label | Multiplier |
|-------|-------|------------|
| 1 | Surgical | 1.00 (no penalty) |
| 2 | Localized | 0.90 |
| 3 | Moderate | 0.75 |
| 4 | Significant | 0.50 |
| 5 | Transformational | 0.25 |

**Actionability Multiplier:**

| Score | Label | Multiplier |
|-------|-------|------------|
| 5 | PR Ready | 1.00 (no penalty) |
| 4 | Ready to Work | 0.90 |
| 3 | Needs Investigation | 0.70 |
| 2 | Needs Triage | 0.40 |
| 1 | Not Actionable | 0.10 |

### Step 5: Categorize

- **Quick Wins**: ROI ≥ 1.5 AND Difficulty ≤ 5 AND Trip ≤ 3 AND Arch ≤ 2 AND Actionability ≥ 4
- **Critical Bugs**: issueType = "bug" AND Importance ≥ 8
- **Tripping Issues**: Trip ≥ 4
- **Over-Engineered**: Arch ≥ 4 (simpler solution likely exists)
- **Not Actionable**: Actionability ≤ 2

Sort all issues by AdjustedScore descending.

### Step 6: Present Results

```
═══════════════════════════════════════════════════════════════
  ISSUE PRIORITIZATION REPORT
  Repository: {owner/repo}
  Filter: {topic/search/label or "latest"}
  Analyzed: {count} issues
  Excluded: {excluded} issues with existing PRs
═══════════════════════════════════════════════════════════════

  Quick Wins: {n} | Critical Bugs: {n} | Tripping: {n} | Over-Engineered: {n} | Not Actionable: {n}

═══════════════════════════════════════════════════════════════
  TOP 10 BY ADJUSTED SCORE
═══════════════════════════════════════════════════════════════

  #123 [Adj: 3.50] ⭐ Quick Win
  Fix typo in README
  ├─ Difficulty: 1/10 | Importance: 4/10 | ROI: 4.00
  ├─ Trip: ✅ Total Sanity (1/5) | Arch: ✅ Surgical (1/5)
  ├─ Act: ✅ PR Ready (5/5) | Level: beginner
  └─ https://github.com/owner/repo/issues/123

═══════════════════════════════════════════════════════════════
  QUICK WINS (High Impact, Low Effort, Sane & Actionable)
═══════════════════════════════════════════════════════════════

  #123: Fix typo in README [Adj: 3.50]
        Difficulty: 1 | Importance: 4 | beginner

═══════════════════════════════════════════════════════════════
  RECOMMENDATIONS BY LEVEL
═══════════════════════════════════════════════════════════════

  BEGINNER (Difficulty 1-3, no security/architecture):
  - #123: Fix typo - Low risk, good first contribution

  INTERMEDIATE (Difficulty 4-6):
  - #456: Add validation - Medium complexity, clear scope

  ADVANCED (Difficulty 7-10 or security/architecture):
  - #789: Refactor auth - Architectural knowledge needed

═══════════════════════════════════════════════════════════════
  CRITICAL BUGS (Importance ≥ 8)
═══════════════════════════════════════════════════════════════

  #111 [Adj: 1.67] 🔴 Critical
  App crashes on startup with large datasets
  ├─ Difficulty: 6/10 | Importance: 9/10 | ROI: 1.50
  ├─ Trip: ✅ (2/5) | Arch: ✅ (2/5) | Act: ⚠️ (3/5)
  └─ https://github.com/owner/repo/issues/111

═══════════════════════════════════════════════════════════════
  TRIPPING ISSUES (Trip ≥ 4 — Review Carefully)
═══════════════════════════════════════════════════════════════

  #999 [Trip: 🚨 5/5 — Tripping]
  Rewrite entire backend in Rust with blockchain storage
  ├─ Red Flags: "rewrite from scratch", "blockchain"
  ├─ Adjusted Score: 0.12 (heavily penalized)
  └─ Consider: Is this complexity really needed?

═══════════════════════════════════════════════════════════════
  OVER-ENGINEERED (Arch ≥ 4 — Simpler Solution Likely Exists)
═══════════════════════════════════════════════════════════════

  #777 [Arch: 🏗️ 5/5 — Transformational]
  Add form validation
  ├─ Proposed: New validation framework with schema definitions
  ├─ Simpler Alternative: Single validation function, 20 lines
  └─ Ask: Why create a framework for one form?

  💡 TIP: Maintainers often reject PRs that change architecture
     unnecessarily. Always start with the simplest fix.

═══════════════════════════════════════════════════════════════
  NOT ACTIONABLE (Actionability ≤ 2)
═══════════════════════════════════════════════════════════════

  - #222: "How do I deploy to Kubernetes?" (Act: 1/5 — question)
  - #333: Duplicate of #111 (Act: 1/5 — duplicate)

═══════════════════════════════════════════════════════════════
  EXCLUDED — EXISTING PRs
═══════════════════════════════════════════════════════════════

  #123: Login crashes on empty password
        └─ 🔗 PR #456: "Fix login validation" (explicit: fixes #123)

  Detection: 🔗 Explicit link | 📎 Referenced | 🔍 Similar title | 💡 Semantic match

═══════════════════════════════════════════════════════════════
  SCALE LEGEND
═══════════════════════════════════════════════════════════════

  Trip (Solution Sanity):        Arch (Structural Impact):
  ✅ 1-2 = Sane                  ✅ 1-2 = Minimal change
  ⚠️  3  = Cautious              ⚠️  3  = Moderate
  🚨 4-5 = Risky                 🏗️ 4-5 = Over-engineered

  Actionability:
  ✅ 4-5 = Ready for PR
  ⚠️  3  = Needs Investigation
  ❌ 1-2 = Not Actionable

  AdjustedScore = ROI × TripMult × ArchMult × ActionMult
  Higher = Better (prioritize first)

  🎯 SIMPLICITY PRINCIPLE: If a 10-line fix exists,
     a 200-line refactor is wrong.

  Mode: SKILL (read-only) — analyzes only, never modifies.
═══════════════════════════════════════════════════════════════
```

## Options

- `--json`: Raw JSON output
- `--markdown` / `--md`: Markdown table output
- `--quick-wins`: Show only quick wins
- `--level beginner|intermediate|advanced`: Filter by contributor level
- `--limit N`: Number of issues to analyze (default: 30)
- `--topic <keywords>`: Search issues by topic (e.g. `--topic telegram`, `--topic "agents telegram"`)
- `--search <query>`: Raw GitHub search query for full control (e.g. `--search "label:bug telegram in:title"`)
- `--label <name>`: Filter by GitHub label (e.g. `--label bug`)
- `--include-with-prs`: Skip PR filtering, include all issues

## LLM Deep Analysis (Optional)

For higher-quality scoring, use an LLM to analyze each issue individually. For each issue, prompt the model with the issue details and scoring criteria, requesting structured JSON output:

```json
{
  "number": 123,
  "difficulty": 5,
  "difficultyReasoning": "base 5; has repro (-1); unknown cause (+3) = 7",
  "importance": 7,
  "importanceReasoning": "broken functionality affecting users",
  "tripScore": 2,
  "tripLabel": "Grounded with Flair",
  "tripRedFlags": [],
  "tripGreenFlags": ["minimal change", "standard approach"],
  "archScore": 2,
  "archLabel": "Localized",
  "archRedFlags": [],
  "archGreenFlags": ["uses existing patterns"],
  "archSimplerAlternative": null,
  "actionScore": 4,
  "actionLabel": "Ready to Work",
  "actionBlockers": [],
  "actionReadySignals": ["has proposed solution"],
  "issueType": "bug",
  "suggestedLevel": "intermediate",
  "roi": 1.40,
  "adjustedScore": 0.96
}
```

Truncate issue bodies longer than 2000 characters before sending to the model.

**When to use LLM Deep Analysis:**
- Complex repositories with nuanced issues
- When accuracy matters more than speed
- For repositories you're unfamiliar with

**Tradeoffs:** Slower (~2-5s per issue) but more accurate. 1 API call per issue.

**Integration:** For each issue, call the LLM with the analysis prompt, parse the JSON response, and merge into results before Step 5 (Categorize).
