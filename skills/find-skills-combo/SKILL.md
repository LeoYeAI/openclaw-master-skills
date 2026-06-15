---
name: find-skills-combo
description: Discover and recommend **combinations** of agent skills to complete complex, multi-faceted tasks. Provides two recommendation strategies — **Maximum Quality** (best skill per subtask) and **Minimum Dependencies** (fewest installs). Use this skill whenever the user wants to find skills, asks "how do I do X", "find a skill for X", or describes a task that likely requires multiple capabilities working together. Also use when the user mentions composing workflows, building pipelines, or needs help across several domains at once — even if they only say "find me a skill". This skill supersedes simple single-skill search by decomposing the task into subtasks and assembling an optimal skill portfolio.
---

# Find Skills Combo

Discover and install **skill combinations** from the open agent skills ecosystem. Unlike single-skill search, this skill decomposes complex tasks into subtasks, searches for candidates per subtask, evaluates coverage, and recommends two strategies: **Maximum Quality** (best skill per subtask, highest output quality) and **Minimum Dependencies** (fewest installs, lean setup). Users pick the strategy that fits their priorities.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X involves multiple capabilities or domains
- Says "find a skill for X" or "is there a skill for X"
- Describes a task that spans several concerns (e.g., "build a quarterly report with charts, risk analysis, and executive summary")
- Wants to compose a workflow from multiple skills
- Asks "can you do X" where X is a complex, multi-step task
- Expresses interest in extending agent capabilities for a non-trivial project

**Fallback**: If the task is genuinely single-domain and simple (one clear capability), skip the decomposition — run a single `npx skills find` query, present results, and offer to install. Don't over-engineer simple requests.

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem.

**Key commands:**

- `npx skills find [query]` — Search for skills by keyword
- `npx skills add <package>` — Install a skill from GitHub or other sources
- `npx skills add <package> -g -y` — Install globally, skip confirmation
- `npx skills check` — Check for skill updates
- `npx skills update` — Update all installed skills

**Browse skills at:** https://skills.sh/

---

## The 5-Phase Pipeline

For complex tasks, follow all five phases in order. For simple tasks, see the Fallback section above.

### Phase 1: Task Decomposition

Break the user's request into independent subtasks. Each subtask represents a distinct capability needed to complete the overall task.

**Step 1: Extract Task-Specific Constraints**

Before decomposing, scan the user's request for **task-specific constraints** — these are requirements that narrow the problem space and must be preserved in the subtasks. Look for:

- **Domain-specific terminology**: Jargon, proper nouns, named standards, or specialized vocabulary the user explicitly uses (e.g., "WCAG 2.1 AA compliance", "GAAP reporting", "OpenAPI 3.1 spec"). These terms signal that generic skills won't suffice — the subtask must target this exact domain.
- **Scenario constraints**: Environmental or contextual restrictions (e.g., "offline-only", "must run in CI", "single-page app with no backend", "monorepo with pnpm workspaces"). These filter out skills that technically do the right thing but in the wrong context.
- **Format / output requirements**: Specific file formats, templates, or delivery formats (e.g., "output as PDF", "Helm chart", "Jupyter notebook", "Markdown with Mermaid diagrams").
- **Toolchain lock-ins**: Explicit technology choices the user has already committed to (e.g., "using Svelte, not React", "PostgreSQL only", "must integrate with our existing FastAPI backend").

Collect these into a **Constraints List** — a flat list of non-negotiable requirements extracted verbatim (or near-verbatim) from the user's request. Every subtask you create must trace back to at least one constraint, and no constraint should be orphaned.

**Step 2: Decompose into Subtasks**

1. Read the user's request carefully. Identify every distinct outcome or deliverable they need.
2. Group related outcomes into subtasks. Each subtask should be a "capability unit" — something one skill could plausibly handle.
3. Write a short completion criterion for each subtask so you know what "covered" means later.
4. **Attach relevant constraints** from the Constraints List to each subtask. A subtask without any attached constraint is likely too generic — refine it. A constraint not attached to any subtask is a gap — either create a subtask for it or fold it into an existing one.

**Constraints:**

- Aim for 2–7 subtasks. Fewer than 2 means the task is simple — use the fallback. More than 7 means you're splitting too fine — merge related items.
- Each subtask needs a clear boundary. If two subtasks always require the same skill, merge them.
- **Preserve the user's own words**: When a subtask maps to a domain-specific term the user used, keep that term in the subtask description and completion criteria — don't paraphrase it into a generic synonym. This ensures Phase 2 keyword generation stays precise.

**Output format** (present this to the user for confirmation):

Constraints List:
- C1: `[verbatim constraint from user]`
- C2: `[verbatim constraint from user]`
- ...

| ID | Subtask | Completion Criteria | Constraints |
|----|---------|---------------------|-------------|
| S1 | ... | ... | C1, C3 |
| S2 | ... | ... | C2 |

Before proceeding to Phase 2, briefly show the user the decomposition and constraints list: "I've identified N constraints and broken this into M subtasks — does this look right?" If they want to adjust, iterate. Don't spend too long here — a reasonable decomposition is better than a perfect one.

### Phase 2: Precision-Focused Search

For each subtask, the goal is **precision over recall** — find the skills that most closely match the subtask's specific requirements, not just loosely related ones.

**Step 1: Subtask Intent Analysis**

Before generating keywords, write a one-sentence **intent statement** for each subtask that captures:
- The **specific action** (e.g., "generate", "analyze", "validate", not vague terms like "handle" or "process")
- The **domain object** (e.g., "Sharpe ratio", "Docker container", "React component")
- The **expected output format** (e.g., "a chart", "a score", "a config file")
- The **attached constraints from Phase 1** — weave the user's domain-specific terms and scenario restrictions directly into the intent statement

This intent statement is the anchor for keyword generation — every keyword group must map back to it. Constraints ensure the intent stays grounded in the user's actual context rather than drifting to generic descriptions.

| ID | Subtask | Constraints | Intent Statement |
|----|---------|-------------|-----------------|
| S1 | ... | C1, C3 | "Calculate portfolio risk metrics (Sharpe, beta, drawdown) under GAAP standards and output a summary table" |
| S2 | ... | C2 | "Generate interactive Mermaid-based charts from time-series data in a Svelte SPA" |

**Step 2: Keyword Generation (Precision-First)**

For each subtask, generate 2–3 keyword groups using different precision levels:

- **Exact-match keywords**: Use the most specific terms from the intent statement — tool names, metric names, framework names, file formats. These find skills purpose-built for the subtask. (e.g., `sharpe ratio beta drawdown calculator`)
- **Functional-match keywords**: Describe the capability at one level of abstraction higher — what the skill *does* rather than what it *is*. These catch skills that solve the same problem with different terminology. (e.g., `portfolio risk analysis metrics`)
- **Domain-match keywords** (only if exact + functional return < 3 results): Broaden to the domain level as a safety net. (e.g., `quantitative finance`)

**Priority rule**: Always run exact-match first. Only fall back to broader keywords if the precise search returns too few results (< 3 candidates).

**Step 3: Search Execution**

1. Build a keyword plan table with precision level annotated:

| Subtask | Exact-Match | Functional-Match | Domain-Match (if needed) |
|---------|-------------|------------------|--------------------------|
| S1 | `sharpe ratio beta drawdown` | `portfolio risk metrics` | `quantitative finance` |
| S2 | `interactive chart time-series dashboard` | `data visualization web` | — |

2. Run all exact-match searches in parallel first:

```bash
npx skills find "<exact-match-keywords>"
```

3. Check result counts. For any subtask with < 3 candidates from exact-match, run the functional-match search. If still < 3, run domain-match.

4. Merge and deduplicate results. For each candidate, record:
   - Which subtask found it
   - Which precision level matched (exact > functional > domain)
   - The skill's self-described purpose (from search output)

**Step 4: Relevance Pre-Filter**

Before passing candidates to Phase 3, do a quick relevance check per candidate:

1. Re-read the candidate's one-line description from the search output.
2. Compare it against the subtask's intent statement.
3. **Keep** if the description shares at least one specific term (tool name, metric, framework) with the intent statement, OR if it describes the same functional capability.
4. **Drop** if the connection is only at the domain level (e.g., a skill about "financial news aggregation" found via domain-match for a "risk metrics" subtask).

Keep the top 3–5 candidates per subtask after filtering. Fewer but more precise candidates produce better evaluations in Phase 3.

### Phase 3: Candidate Evaluation

Build a **Subtask × Candidate** coverage matrix with two extra columns for combination planning.

**For each candidate skill:**

1. Look up its description on skills.sh or read its SKILL.md if installed.
2. Rate its relevance to each subtask as **High**, **Medium**, or **Low**:
   - **High** — The skill directly addresses this subtask with dedicated features or workflows
   - **Medium** — The skill partially covers this subtask or addresses it as a secondary concern
   - **Low** — The skill has minimal or no relevance to this subtask
3. Write a one-line justification for each rating.
4. Compute two additional metrics per candidate:
   - **Breadth** — Count of subtasks where the skill rates High or Medium (higher = more versatile, valuable for minimum-dependency strategy)
   - **Peak** — Count of subtasks where the skill is the top-rated candidate (higher = more irreplaceable, valuable for best-effect strategy)

**Output the matrix:**

| Candidate | S1 | S2 | S3 | Breadth | Peak |
|-----------|----|----|-----|---------|------|
| Skill A | High: ... | Low | High: ... | 2 | 1 |
| Skill B | Medium: ... | High: ... | Low | 2 | 1 |
| Skill C | Low | High: ... | Medium: ... | 2 | 1 |
| Skill D | Low | Low | High: ... | 1 | 1 |

**Pruning**: Drop candidates that are Low across all subtasks — they are noise.

### Phase 4: Dual-Strategy Planning

Produce exactly **two** recommended strategies targeting different user priorities.

---

**Strategy A — Maximum Quality (追求最强效果)**

Goal: Every subtask gets its best-fit skill. Accept more installs to maximize output quality.

Algorithm:
1. For each subtask, pick the candidate with the highest rating (use Peak column to break ties — prefer skills that are uniquely best at something).
2. If multiple candidates tie at High for a subtask, prefer the one with higher community popularity or more recent maintenance.
3. List all selected skills (may include one skill per subtask if they're all different).

This strategy is for users who want the highest-quality result and don't mind installing several skills.

**Strategy B — Minimum Dependencies (最少外部依赖)**

Goal: Cover all subtasks with as few skills as possible. Accept Medium coverage where it avoids adding an extra skill.

Algorithm:
1. Sort candidates by Breadth descending (most versatile first).
2. Greedily select: pick the highest-Breadth skill, mark its High/Medium subtasks as covered, repeat until all subtasks are covered.
3. If a subtask can only reach Medium coverage with the greedy set but has a dedicated High-coverage skill, do NOT add that skill — keep the set minimal. Only flag the trade-off.
4. Target ceiling: if the task has N subtasks, this strategy should ideally use ≤ ⌈N/2⌉ skills.

This strategy is for users who want to keep their environment lean and are comfortable with "good enough" coverage on some subtasks.

---

**For both strategies, document:**

- Which skills are included and total install count
- A subtask → skill mapping table
- A one-sentence rationale
- A quality delta summary: where Strategy B trades quality for fewer installs compared to Strategy A

**Coverage gap check**: If any subtask has no High or Medium candidate in either strategy, flag it: "⚠ Subtask SX has no strong skill coverage — you may need to handle this manually or create a custom skill."

**Conflict detection**: If two skills in Strategy A overlap significantly on the same subtask, note it: "Skills X and Y both cover S2 — you only need one; keeping the higher-rated one."

### Phase 5: Present Results

Structure the final output with these sections:

---

**1. Task Decomposition Summary**

Show the subtask table from Phase 1 (brief, since the user already confirmed it).

**2. Side-by-Side Comparison**

Start with a quick comparison table so the user can choose a strategy immediately:

```
| | Strategy A: Maximum Quality | Strategy B: Minimum Dependencies |
|---|---|---|
| Skills to install | N skills | M skills |
| All-High coverage | X of Y subtasks | P of Y subtasks |
| Trade-offs | More installs | Some subtasks at Medium |
| Best for | Critical/production tasks | Quick exploration, lean setup |
```

**3. Strategy A — Maximum Quality (Recommended for critical tasks)**

```
Every subtask gets its best-fit skill for the highest-quality output.

| Subtask | Handled By | Coverage |
|---------|-----------|----------|
| S1 | skill-name-a | High |
| S2 | skill-name-b | High |
| S3 | skill-name-c | High |

### Install (N skills)
​```bash
npx skills add owner/repo@skill-a -g -y
npx skills add owner/repo@skill-b -g -y
npx skills add owner/repo@skill-c -g -y
​```
```

**4. Strategy B — Minimum Dependencies (Recommended for lean setup)**

```
Cover all subtasks with the fewest skills possible.

| Subtask | Handled By | Coverage | vs Strategy A |
|---------|-----------|----------|---------------|
| S1 | skill-name-a | High | Same |
| S2 | skill-name-a | Medium | ↓ High → Medium |
| S3 | skill-name-a | Medium | ↓ High → Medium |

### Install (M skills)
​```bash
npx skills add owner/repo@skill-a -g -y
​```
```

The `vs Strategy A` column makes the trade-off transparent — users see exactly what they give up by installing fewer skills.

**5. Coverage Gaps & Risks**

- List any subtasks without strong coverage in either strategy
- Suggest workarounds (manual steps, creating a custom skill with `npx skills init`)
- If Strategy B downgrades a subtask from High to Medium, briefly explain the practical impact

**6. Next Steps**

Ask the user:
- "Which strategy do you prefer — Maximum Quality or Minimum Dependencies?"
- "Want me to install your chosen strategy now?"
- "Want me to search deeper for any specific subtask?"
- "Want to adjust the decomposition?"

---

## Fallback: Simple Single-Skill Search

When the task is straightforward (single domain, one clear capability):

1. Run `npx skills find [query]` with 1–2 relevant keyword sets
2. Present the top 2–3 results with name, description, and install command
3. Offer to install

This is the same behavior as the basic find-skills workflow — no decomposition needed.

## Common Skill Categories

When generating keywords, draw from these domains:

| Category | Example Keywords |
|----------|-----------------|
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog, api-docs |
| Code Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |
| Data & Analytics | data, visualization, charts, analysis |
| Finance | portfolio, trading, risk, investment |
| Productivity | workflow, automation, git |

## Tips

1. **Precision beats recall**: 3 highly relevant candidates are more useful than 10 loosely related ones. Always start with the most specific keywords and only broaden if needed.
2. **Intent statements are your anchor**: A good intent statement in Phase 2 prevents keyword drift. If your keywords don't map back to the intent, they're too broad.
3. **Parallel search matters**: Running all keyword groups simultaneously saves significant time. Use subagents when available.
4. **Don't over-decompose**: 3–5 subtasks is the sweet spot for most tasks. More than that creates noise.
5. **Skills.sh is your friend**: When evaluating candidates, quickly check `https://skills.sh/<owner>/<repo>/<skill-name>` for descriptions.
6. **User confirmation at Phase 1 is critical**: A wrong decomposition cascades into bad search and bad recommendations. Take 30 seconds to verify.
7. **Always present both strategies**: Users have different priorities — some want the best possible result, others want a lean setup. Let them choose.
8. **Make the trade-off explicit**: The `vs Strategy A` column in Strategy B is the most important part of the output. It turns an abstract choice into a concrete comparison.
9. **Breadth and Peak drive strategy selection**: High-Breadth skills are MVPs for Strategy B (minimum dependencies); High-Peak skills are essential for Strategy A (maximum quality). Computing both in Phase 3 makes Phase 4 mechanical.

## When No Skills Are Found

If a subtask has no relevant skills:

1. Flag it in the coverage gaps section
2. Offer to help with that subtask directly using general capabilities
3. Suggest the user create a custom skill: `npx skills init my-custom-skill`
4. If the entire task has no skills at all, acknowledge it honestly and pivot to direct assistance
