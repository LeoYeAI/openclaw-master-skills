| allowed-tools | description |
|---|---|
| Bash(gh issue*), Bash(gh pr*), Bash(gh api*), Read, Glob, Grep, Task | Analyze GitHub issues with parallel Sonnet agents (up to 7x speed) |

# Issue Prioritizer Skill (Parallel Edition)

Analyze issues from a GitHub repository and rank them by **Adjusted Score** (ROI penalized by Tripping Scale).

**Performance:** Uses up to 7 parallel Sonnet agents for fast analysis.

## Modes

This is a **read-only skill**. It analyzes and presents information. YOU make all decisions and implement changes.

## Instructions

### Step 1: Get Repository

If the user didn't specify a repository, ask which repository to analyze (format: `owner/repo`).

### Step 2: Fetch ALL Issues First

Use `gh issue list` to fetch open issues:

```bash
gh issue list --repo {owner/repo} --state open --limit {limit} --json number,title,body,labels,createdAt,comments,url
```

Default limit is 30. Store the full JSON response - you'll distribute it to agents.

**Error Handling:**
- If `gh` returns an authentication error, tell user to run `gh auth login`
- If rate limited, inform user: "GitHub API rate limit reached. Try again in a few minutes or reduce --limit"
- If repository not found, display: "Repository not found. Check the format: owner/repo"
- If no issues returned, report "No open issues found in {repo}" and exit gracefully

### Step 2.5: Filter Issues with Existing PRs

**IMPORTANT:** Before analyzing issues, check for open PRs that already address them to avoid duplicate work.

**Fetch open PRs:**
```bash
gh pr list --repo {owner/repo} --state open --json number,title,body,url
```

**Detect linked issues** using MULTIPLE detection methods (apply ALL):

**Method 1 - Explicit Keywords** (high confidence):
Scan PR title and body for these patterns (case-insensitive):
- `fixes #123`, `fix #123`, `fixed #123`
- `closes #123`, `close #123`, `closed #123`
- `resolves #123`, `resolve #123`, `resolved #123`

**Method 2 - Issue References** (medium confidence):
Scan PR title and body for any mention of issue numbers:
- `#123` anywhere in text (even without keywords)
- `issue 123`, `issue #123`
- `related to #123`, `addresses #123`, `for #123`

**Method 3 - Title Similarity** (fuzzy matching):
Compare PR title with issue titles for high similarity:
- Normalize both titles: lowercase, remove punctuation, remove common words (fix, add, update, bug, feature)
- If 70%+ word overlap OR PR title contains issue number → likely duplicate
- Example: Issue "Login crashes on empty password" ↔ PR "Fix login crash with empty password"

**Method 4 - Semantic Matching** (for ambiguous cases):
If issue title contains distinctive keywords, search PR bodies:
- Extract key terms from issue (error names, function names, component names)
- Check if PR body discusses same components/errors

**Build a map** of issue numbers to linked PRs (track detection method):
```
linkedPRs = {
  123: { prNumber: 456, prTitle: "Fix login bug", prUrl: "...", method: "explicit keyword" },
  789: { prNumber: 101, prTitle: "Add validation", prUrl: "...", method: "title similarity" }
}
```

**Confidence Reporting:**
- 🔗 Explicit link (fixes/closes/resolves)
- 📎 Referenced (#123 mentioned)
- 🔍 Similar title (fuzzy match)
- 💡 Semantic match (same components)

**Filter the issues list:**
1. Remove any issue whose number appears in `linkedPRs`
2. Track the filtered issues for reporting

**Report filtered issues** (show before analysis begins):
```
═══════════════════════════════════════════════════════════════
  ISSUES WITH EXISTING PRs (excluded from ranking)
═══════════════════════════════════════════════════════════════

  #123: Login crashes on empty password
        └─ 🔗 PR #456: "Fix login validation" (explicit: fixes #123)
           https://github.com/owner/repo/pull/456

  #789: Add email validation
        └─ 📎 PR #101: "Add form validation" (referenced: #789 in body)
           https://github.com/owner/repo/pull/101

  #555: Button styling broken
        └─ 🔍 PR #202: "Fix button styles" (title similarity: 85%)
           https://github.com/owner/repo/pull/202

  {N} issues excluded. Analyzing remaining {M} issues...
═══════════════════════════════════════════════════════════════
```

**If all issues have PRs:** Report "All {N} issues already have open PRs addressing them. Nothing to prioritize." and exit gracefully.

**Continue with filtered list** - pass only the remaining issues to Step 3.

### Step 3: Parallel Analysis with Sonnet Agents

**CRITICAL: This is the parallel processing step.**

1. **Count issues** fetched from Step 2
2. **Calculate batches**: Divide issues into batches
3. **Spawn up to 7 Sonnet agents in parallel** using the Task tool

**Agent Distribution Strategy:**

| Total Issues | Agents to Spawn | Issues per Agent | Waves |
|--------------|-----------------|------------------|-------|
| 1-7          | N (one per issue) | 1              | 1     |
| 8-14         | 7               | 1-2              | 1     |
| 15-35        | 7               | 2-5              | 1     |
| 36-70        | 7               | 5-10             | 1     |
| 71-140       | 7               | 10               | 2     |
| 141+         | 7               | 10               | 3+    |

**Batch Calculation Formula:**
```
batch_size = ceil(total_issues / 7)
num_agents = min(7, total_issues)
```

**IMPORTANT:** Launch ALL agents in a SINGLE message with multiple Task tool calls for maximum parallelism.

**Task Tool Parameters:**
```
Task tool call:
- description: "Analyze issues batch N"
- prompt: (see Agent Prompt Template below)
- subagent_type: "general-purpose"
- model: "sonnet"
```

**Agent Prompt Template:**

For each batch of issues, create a Task with this prompt (fill in the placeholders):

```
You are an issue analysis agent. Analyze the following GitHub issues and return ONLY a valid JSON array.

REPOSITORY: {owner/repo}
BATCH: {batch_number} of {total_batches}

ISSUES TO ANALYZE (JSON):
{paste the JSON array for this batch - truncate issue bodies longer than 2000 chars}

For EACH issue, analyze and score:

## 1. Difficulty Score (1-10)
Base score: 5
Adjustments:
- Documentation only: -3
- Has proposed solution: -2
- Has reproduction steps: -1
- Clear error message: -1
- Unknown root cause: +3
- Architectural change: +3
- Race condition/concurrency: +2
- Security implications: +2
- Multiple systems involved: +2

## 2. Importance Score (1-10)
- Critical (8-10): crash, data loss, security vulnerability, service down
- High (6-7): broken functionality, errors, performance issues
- Medium (4-5): enhancements, feature requests, improvements
- Low (1-3): cosmetic, documentation, typos

## 3. Tripping Scale (1-5) - Solution Sanity
1 = Total Sanity (proven patterns, standard approach)
2 = Grounded with Flair (practical with creative touches)
3 = Dipping Toes (exploring new territory cautiously)
4 = Wild Adventure (bold, risky, unconventional)
5 = Tripping (questionable if it makes sense)

Red Flags (increase score): rewrite from scratch, blockchain/AI/ML buzzwords, experimental, breaking change, custom protocol
Green Flags (decrease score): standard, minimal change, backward compatible, well-documented, existing library

## 3.5. Architectural Impact (1-5) - How Much Does This Change Structure?

IMPORTANT: Always ask "Is there a simpler way?" before scoring. Prefer minimal-change solutions.

1 = Surgical (isolated fix, touches 1-2 files, no new abstractions)
2 = Localized (small addition, follows existing patterns exactly, no new concepts)
3 = Moderate (new component BUT within existing architecture, respects boundaries)
4 = Significant (new subsystem, introduces new patterns, affects multiple modules)
5 = Transformational (restructures core, changes paradigms, migration required)

Red Flags (increase score):
- "rewrite", "refactor entire", "new architecture"
- Introduces new framework/library for existing capability
- Creates new abstraction layers
- Requires changes across >5 files
- Adds new configuration complexity
- Breaking changes to APIs/interfaces
- "we should also..." scope creep

Green Flags (decrease score):
- Bug fix in single file
- Uses existing utilities/helpers
- Follows established patterns in codebase
- Backward compatible
- No new dependencies
- Self-contained change
- Could be reverted easily

CRITICAL: If a simple solution exists, architectural changes are WRONG.
Example: Don't create a "validation framework" when a single if-check suffices.

## 4. Actionability Score (1-5) - Can it be PRed?
1 = Not Actionable (question, discussion, duplicate, support request)
2 = Needs Triage (missing info, unclear scope)
3 = Needs Investigation (unknown root cause, needs debugging)
4 = Ready to Work (clear scope, some design decisions needed)
5 = PR Ready (solution is clear, just implement)

Blockers (decrease): questions in title, "how do I?", duplicate label, wontfix label, missing repro
Ready signals (increase): "fix:", "add:" in title, proposed solution, repro steps, good-first-issue label

## 5. Derived Values
- issueType: "bug" | "feature" | "docs" | "other"
- suggestedLevel: "beginner" (diff 1-3) | "intermediate" (diff 4-6) | "advanced" (diff 7-10 or security/architecture)
- ROI = importance / difficulty (round to 2 decimals)
- TripMultiplier: use this table:
  | Trip Score | Multiplier |
  |------------|------------|
  | 1          | 1.00       |
  | 2          | 0.85       |
  | 3          | 0.70       |
  | 4          | 0.55       |
  | 5          | 0.40       |
- ArchMultiplier (Architectural Impact penalty): use this table:
  | Arch Score | Multiplier |
  |------------|------------|
  | 1          | 1.00       |
  | 2          | 0.90       |
  | 3          | 0.75       |
  | 4          | 0.50       |
  | 5          | 0.25       |
- ActionMultiplier: use this table:
  | Action Score | Multiplier |
  |--------------|------------|
  | 1            | 0.10       |
  | 2            | 0.40       |
  | 3            | 0.70       |
  | 4            | 0.90       |
  | 5            | 1.00       |
- AdjustedScore = ROI * TripMultiplier * ArchMultiplier * ActionMultiplier (round to 2 decimals)

## OUTPUT FORMAT

Return ONLY a valid JSON array. No markdown fences. No explanation. Just the array:

[
  {
    "number": 123,
    "title": "Issue title here",
    "url": "https://github.com/owner/repo/issues/123",
    "difficulty": 5,
    "difficultyReasoning": "base score; has reproduction (-1); unknown cause (+3)",
    "importance": 7,
    "importanceReasoning": "broken functionality affecting users",
    "tripScore": 2,
    "tripLabel": "Grounded with Flair",
    "tripRedFlags": [],
    "tripGreenFlags": ["minimal change", "standard approach"],
    "archScore": 2,
    "archLabel": "Localized",
    "archRedFlags": [],
    "archGreenFlags": ["uses existing patterns", "single file change"],
    "archSimplerAlternative": null,
    "actionScore": 4,
    "actionLabel": "Ready to Work",
    "actionBlockers": [],
    "actionReadySignals": ["has proposed solution"],
    "issueType": "bug",
    "suggestedLevel": "intermediate",
    "roi": 1.40,
    "tripMultiplier": 0.85,
    "archMultiplier": 0.90,
    "actionMultiplier": 0.90,
    "adjustedScore": 0.96
  }
]

IMPORTANT: Return ONLY the JSON array. No other text.
```

### Step 4: Collect and Merge Results

Wait for all agents to complete. For each agent response:

1. **Clean the response:**
   - If wrapped in markdown code fences (```json ... ```), extract the content
   - If wrapped in ```...```, extract the content
   - Trim whitespace

2. **Parse JSON:**
   - Attempt to parse as JSON array
   - If parsing fails, log which batch failed and continue with other results

3. **Merge results:**
   - Combine all successful arrays into a single array
   - Deduplicate by issue number (if same issue appears twice, keep first occurrence)

4. **Track failures:**
   - Note which batches failed to parse
   - Report: "Warning: Batch N failed to parse. Issues #X-#Y may be missing from results."

**If ALL agents fail:** Report error and suggest user retry with smaller --limit.

### Step 5: Categorize

From the merged results, categorize issues:

- **Quick Wins**: ROI ≥ 1.5 AND Difficulty ≤ 5 AND Trip ≤ 3 AND Arch ≤ 2 AND Actionability ≥ 4
- **Critical Bugs**: issueType = "bug" AND Importance ≥ 8
- **Tripping Issues**: Trip Score ≥ 4 (proceed with caution)
- **Over-Engineered**: Arch Score ≥ 4 (simpler solution likely exists)
- **Not Actionable**: Actionability ≤ 2 (questions/discussions/needs triage)

Sort all issues by AdjustedScore descending.

### Step 6: Present Results

Output a formatted report:

```
═══════════════════════════════════════════════════════════════
  ISSUE PRIORITIZATION REPORT
  Repository: {owner/repo}
  Analyzed: {count} issues (via {N} parallel Sonnet agents)
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

  #456 [Adj: 1.89]
  Add input validation to login form
  ├─ Difficulty: 4/10 | Importance: 7/10 | ROI: 1.75
  ├─ Trip: ✅ Grounded (2/5) | Arch: ✅ Localized (2/5)
  ├─ Act: ✅ Ready to Work (4/5) | Level: intermediate
  └─ https://github.com/owner/repo/issues/456

  ...

═══════════════════════════════════════════════════════════════
  QUICK WINS (High Impact, Low Effort, Sane & Actionable)
═══════════════════════════════════════════════════════════════

  #123: Fix typo in README [Adj: 3.50]
        Difficulty: 1 | Importance: 4 | beginner

  #789: Update deprecated API call [Adj: 2.80]
        Difficulty: 2 | Importance: 5 | beginner

═══════════════════════════════════════════════════════════════
  RECOMMENDATIONS BY LEVEL
═══════════════════════════════════════════════════════════════

  BEGINNER (Difficulty 1-3, no security/architecture):
  - #123: Fix typo - Low risk, good first contribution
  - #789: Update API - Clear scope, well-documented

  INTERMEDIATE (Difficulty 4-6):
  - #456: Add validation - Medium complexity, clear requirements

  ADVANCED (Difficulty 7-10 or security/architecture):
  - #999: Refactor auth system - Architectural knowledge required

═══════════════════════════════════════════════════════════════
  CRITICAL BUGS (Importance ≥ 8)
═══════════════════════════════════════════════════════════════

  #111 [Adj: 1.67] 🔴 Critical
  App crashes on startup with large datasets
  ├─ Difficulty: 6/10 | Importance: 9/10 | ROI: 1.50
  ├─ Trip: ✅ (2/5) | Arch: ✅ (2/5) | Act: ⚠️ (3/5)
  └─ https://github.com/owner/repo/issues/111

═══════════════════════════════════════════════════════════════
  TRIPPING ISSUES (Trip ≥ 4 - Review Carefully)
═══════════════════════════════════════════════════════════════

  #999 [Trip: 🚨 5/5 - Tripping]
  Rewrite entire backend in Rust with blockchain storage
  ├─ Red Flags: "rewrite from scratch", "blockchain", over-engineering
  ├─ Adjusted Score: 0.12 (heavily penalized)
  └─ Consider: Is this complexity really needed?

  #888 [Trip: ⚠️ 4/5 - Wild Adventure]
  Replace REST API with GraphQL + real-time subscriptions
  ├─ Red Flags: "breaking change", "migration required"
  └─ Consider: Worth the migration effort?

═══════════════════════════════════════════════════════════════
  OVER-ENGINEERED (Arch ≥ 4 - Simpler Solution Likely Exists)
═══════════════════════════════════════════════════════════════

  #777 [Arch: 🏗️ 5/5 - Transformational]
  Add form validation
  ├─ Proposed: New validation framework with schema definitions
  ├─ Red Flags: "new abstraction layer", "introduces patterns"
  ├─ Simpler Alternative: Single validation function, 20 lines
  └─ Ask: Why create a framework for one form?

  #666 [Arch: ⚠️ 4/5 - Significant]
  Fix button click not working
  ├─ Proposed: Refactor entire event system
  ├─ Red Flags: "affects multiple modules", "new event bus"
  ├─ Simpler Alternative: Fix the event handler directly
  └─ Ask: Is the event system actually the problem?

  💡 TIP: Maintainers often reject PRs that change architecture
     unnecessarily. Always start with the simplest fix.

═══════════════════════════════════════════════════════════════
  NOT ACTIONABLE (Actionability ≤ 2)
═══════════════════════════════════════════════════════════════

  - #222: "How do I deploy to Kubernetes?" (Act: 1/5 - question)
  - #333: Duplicate of #111 (Act: 1/5 - duplicate)
  - #444: "Thoughts on adding feature X?" (Act: 2/5 - discussion)

═══════════════════════════════════════════════════════════════
  EXCLUDED - EXISTING PRs ({excluded} issues)
═══════════════════════════════════════════════════════════════

  #123: Login crashes on empty password
        └─ 🔗 PR #456: "Fix login validation" (explicit: fixes #123)
           https://github.com/owner/repo/pull/456

  #789: Add email validation
        └─ 📎 PR #101: "Add form validation" (referenced: #789 in body)
           https://github.com/owner/repo/pull/101

  #555: Button styling broken
        └─ 🔍 PR #202: "Fix button styles" (title similarity: 85%)
           https://github.com/owner/repo/pull/202

  Detection Methods:
  🔗 Explicit link (fixes/closes/resolves #N)
  📎 Referenced (mentions #N in text)
  🔍 Similar title (fuzzy match ≥70%)

  (These issues already have open PRs - review/merge them instead)

═══════════════════════════════════════════════════════════════
  SCALE LEGEND
═══════════════════════════════════════════════════════════════

  Trip (Solution Sanity):        Arch (Structural Impact):
  ✅ 1-2 = Sane                  ✅ 1-2 = Minimal change
  ⚠️  3  = Cautious              ⚠️  3  = Moderate
  🚨 4-5 = Risky                 🏗️ 4-5 = Over-engineered

  Actionability (PR-Ready):
  ✅ 4-5 = Ready for PR
  ⚠️  3  = Needs Investigation
  ❌ 1-2 = Not Actionable

  Adjusted Score = ROI × TripMultiplier × ArchMultiplier × ActionMultiplier
  Higher = Better (prioritize these first)

  🎯 SIMPLICITY PRINCIPLE: If a 10-line fix exists, a 200-line
     refactor is wrong. Always ask "is there a simpler way?"

═══════════════════════════════════════════════════════════════
  Performance: {N} parallel Sonnet agents, {W} wave(s)
  Mode: SKILL (read-only) - This shows info. YOU decide and act.
═══════════════════════════════════════════════════════════════
```

## Output Options

Command flags:
- `--json`: Output raw JSON data (merged from all agents)
- `--markdown` or `--md`: Output as markdown table
- `--quick-wins`: Show only quick wins section
- `--level beginner|intermediate|advanced`: Filter recommendations by level
- `--limit N`: Analyze N issues (default: 30)
- `--include-with-prs`: Include issues that already have open PRs (skip Step 2.5 filtering)

## Multi-Wave Processing

For large repositories (>70 issues):

1. **Wave 1:** Spawn 7 agents for first 70 issues
2. **Wait** for all Wave 1 agents to complete
3. **Wave 2:** Spawn agents for next batch (up to 70 more)
4. **Repeat** until all issues processed
5. **Merge** all wave results before presenting

Track progress:
- "Processing Wave 1/2: issues #1-#70..."
- "Processing Wave 2/2: issues #71-#100..."

If a wave partially fails:
- Continue with successful batches
- Report which issue ranges failed
- Don't retry automatically (user can re-run with specific range if needed)

## Important

- This is a **READ-ONLY** skill - never create PRs, write code, or modify repositories
- Present information objectively - let the user decide what to work on
- Flag "tripping" solutions but don't dismiss them outright - user has final say
- **Launch parallel agents in a SINGLE message** for maximum speed
- **Truncate long issue bodies** (>2000 chars) before sending to agents
- Always use **model: "sonnet"** for Task agents

## Example Usage

```
/issue-prioritizer:issue-prioritizer anthropics/claude-code
/issue-prioritizer:issue-prioritizer owner/repo --quick-wins
/issue-prioritizer:issue-prioritizer owner/repo --level beginner
/issue-prioritizer:issue-prioritizer owner/repo --limit 50
/issue-prioritizer:issue-prioritizer owner/repo --limit 100   # 2 waves
/issue-prioritizer:issue-prioritizer owner/repo --json        # Raw data
```
