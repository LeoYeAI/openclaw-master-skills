# Advanced patterns

Patterns for complex skills: categories, instruction freedom, distribution, MCP integration, and workflow design.

## Contents

- [Skill categories](#skill-categories)
- [Degrees of freedom](#degrees-of-freedom)
- [Distribution](#distribution)
- [MCP integration](#mcp-integration)
- [Workflow patterns](#workflow-patterns)
- [OpenAI Codex extensions](#openai-codex-extensions)
- [Reference file structure](#reference-file-structure)

---

## Skill categories

Classify your skill before writing it. Category affects structure and frontmatter choices.

| Category | Description | Typical frontmatter | Example |
|----------|-------------|--------------------|---------|
| Reference | Conventions, knowledge, style guides | (none extra) | humanizer-enhanced, seo-optimizer |
| Task | Step-by-step workflows, pipelines | `context: fork`, `agent: general-purpose` | blogger, reprompter |
| MCP Enhancement | Wraps MCP tool access with methodology | `allowed-tools: "ToolName"` | 0g-compute-skills |
| Hybrid | Reference + task modes combined | varies by mode | skeall (scan = reference, create = task) |

**How category affects decisions:**
- Reference skills run inline (no fork needed). Keep instructions declarative.
- Task skills often fork into subagents. Include explicit output formats and file paths.
- MCP Enhancement skills document tool-specific patterns. Always use fully qualified tool names.
- Hybrid skills need clear mode separation. Each mode should have its own section.

---

## Degrees of freedom

How prescriptive should your skill's instructions be? Match instruction style to task fragility.

| Freedom level | Style | When to use | Example |
|---------------|-------|-------------|---------|
| High | Text guidelines, principles | Creative tasks, varied approaches valid | "Write in active voice, keep paragraphs short" |
| Medium | Pseudocode, parameter lists | Structured tasks with some flexibility | "Call API with these params, handle errors" |
| Low | Exact scripts, copy-paste code | Fragile integrations, specific APIs | "Run this exact curl command with these headers" |

**Rules:**
- Pick ONE freedom level per section. Do not mix "follow these exact steps" with "use your judgment" in the same block.
- When consistency is critical (API calls, SDK patterns), use low freedom with verbatim code blocks.
- When multiple approaches are valid (architecture, naming, refactoring), use high freedom with constraints.
- If unsure, default to medium. Add constraints to narrow scope without dictating exact steps.

**Anti-pattern: mixed freedom**
```markdown
# BAD -- mixes exact code with vague guidance
Follow this exact pattern:
```python
client.send(data)
```
But feel free to handle errors however you think is best.

# GOOD -- consistent low freedom
```python
try:
    client.send(data)
except TimeoutError:
    retry(max_attempts=3)
except AuthError:
    raise  # Do not retry auth failures
```
```

---

## Distribution

Preparing skills for sharing beyond personal use.

### Distribution channels

| Channel | Scope | How |
|---------|-------|-----|
| Personal | Your machine only | `~/.claude/skills/{name}/` |
| Project | Everyone who clones the repo | `.claude/skills/{name}/` committed to git |
| Organization | Managed by admin | Claude Code managed settings, Codex admin panel |
| Public | Anyone on GitHub | GitHub repo with README, license, install instructions |

### Distribution readiness checklist

| Check | Required for |
|-------|-------------|
| README.md with install instructions for 3+ platforms | Public, Organization |
| `license` field in frontmatter | Public |
| `metadata.author` and `metadata.version` in frontmatter | Public, Organization |
| No hardcoded paths or machine-specific references | All shared |
| No secrets, API keys, or personal data in any file | All shared |
| Multi-platform install paths in README | Public |
| `.gitignore` excludes `.DS_Store`, `node_modules`, etc. | Public |

### Create mode integration

When the user says the skill will be shared, generate:
1. README.md with multi-platform install instructions
2. `license` and `metadata` fields in frontmatter
3. `.gitignore` at skill root

---

## MCP integration

MCP (Model Context Protocol) provides tools. Skills provide methodology. Together they are more effective than either alone.

### When to reference MCP tools in skills

| Situation | Approach |
|-----------|----------|
| Skill wraps a specific MCP server | Document tool names, parameter patterns, common workflows |
| Skill uses MCP tools optionally | Mention tool names in relevant sections, provide fallback for platforms without MCP |
| Skill has nothing to do with MCP | Do not mention MCP |

### MCP tool naming

Always use fully qualified names in skills:

```markdown
# BAD -- ambiguous, breaks if multiple servers have similar tools
Use the `search` tool to find documents.

# GOOD -- fully qualified, unambiguous
Use `mcp__memory__memory_search` to find stored memories.
Use `mcp__0g-docs__0gDocs` to query 0G documentation.
```

### MCP dependency documentation

If a skill requires MCP servers, document them in the skill:

```markdown
## Required MCP servers

This skill requires the following MCP servers to be configured:

| Server | Purpose | Config key |
|--------|---------|-----------|
| `memory` | Store and retrieve context | `mcpServers.memory` |
| `0g-docs` | Query 0G documentation | `mcpServers.0g-docs` |

Without these servers, the skill falls back to web search and file-based storage.
```

---

## Workflow patterns

For skills that guide multi-step processes, use these proven patterns.

### Copyable progress checklist

Give the LLM a checklist it can copy and track:

```markdown
## Pipeline

- [ ] Step 1: Gather inputs
- [ ] Step 2: Validate inputs
- [ ] Step 3: Process data
- [ ] Step 4: Generate output
- [ ] Step 5: Verify output

Mark each step complete as you finish it. If a step fails, stop and report the error.
```

**Why it works:** LLMs can copy the checklist into their response and check items off, making progress visible and preventing skipped steps.

### Validation feedback loop

For tasks that need quality control:

```markdown
## Quality loop

1. Generate output
2. Score against success criteria (list criteria here)
3. If score >= threshold: deliver to user
4. If score < threshold: identify gaps, fix them, go to step 2
5. Maximum 2 retries (3 total attempts)
```

**Real example (from reprompter):**
- Score each agent prompt (target 8+/10)
- If under threshold, add more context/constraints and re-score
- After 3 attempts, deliver best version with score disclosure

### Plan-validate-execute

For batch operations or destructive actions:

```markdown
## Batch process

1. **Plan**: List all files/items to process. Show the plan to user.
2. **Validate**: Run a dry-run on 1-2 items. Confirm output format is correct.
3. **Execute**: Process remaining items.
4. **Report**: Summarize results (success count, failures, skipped).
```

### Argument-based routing

For skills with multiple modes triggered by arguments:

```markdown
## Routing

| Argument | Mode | Action |
|----------|------|--------|
| `--create` | Create | Interview + scaffold |
| `--scan <path>` | Scan | Audit and report |
| `--improve <path>` | Improve | Analyze + propose edits |
| (no argument) | Default | Show help text |
```

Use `$ARGUMENTS` in SKILL.md to capture user input. Parse the first token as mode selector.

---

## OpenAI Codex extensions

Codex adopted the agentskills.io standard but adds an `openai.yaml` file for platform-specific metadata:

```yaml
# openai.yaml (Codex-specific, alongside SKILL.md)
interface: chat            # How the skill interacts (chat, tool, agent)
policy: suggest            # How aggressive (suggest, enforce, auto)
dependencies:              # Required tools/packages
  - name: node
    version: ">=18"
```

**Skeall guidance:**
- `openai.yaml` is optional. Only generate it when the user targets Codex specifically.
- Scan mode: note (informational, not a fail) when `openai.yaml` is present alongside SKILL.md.
- The SKILL.md itself remains cross-platform. Codex reads both files.

---

## Reference file structure

### Table of contents for long files

Reference files over 100 lines should include a table of contents at the top. The LLM may preview files with partial reads; a TOC ensures it can see all available sections.

```markdown
# Topic reference

## Contents

- [Section 1: Setup](#section-1-setup)
- [Section 2: Configuration](#section-2-configuration)
- [Section 3: Troubleshooting](#section-3-troubleshooting)

---

## Section 1: Setup
...
```

### File size guidance

| File length | Action |
|-------------|--------|
| Under 100 lines | No TOC needed |
| 100-300 lines | Add a TOC at the top |
| 300-700 lines | Add TOC + consider splitting into multiple files |
| Over 700 lines | Split into multiple reference files |
