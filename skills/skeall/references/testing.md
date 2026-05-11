# Testing your skill

Three testing levels, from quickest to most thorough.

## Level 1: Manual testing (fastest)

Open a new session and try your trigger phrases. Verify the skill activates and produces correct output.

### Trigger testing

Test that the skill activates on expected phrases and stays quiet on irrelevant ones.

| Test type | Example | Expected |
|-----------|---------|----------|
| Exact trigger | "/my-skill" | Skill activates |
| Natural language | "help me with X" (where X is in description) | Skill activates |
| Partial match | Related but not exact keyword | Skill may or may not activate |
| Negative | Completely unrelated prompt | Skill does NOT activate |

Write 3-5 trigger test prompts per skill. Include at least one negative test.

### Functional testing

Run the skill's main workflow end-to-end. For each mode:

1. Provide realistic input
2. Check output matches expected format
3. Verify all sections/steps are present
4. Check for hallucinated content (wrong paths, phantom APIs, made-up examples)

## Level 2: Scripted testing (recommended)

Use Claude Code to run a sequence of test prompts and check outputs.

```bash
# Example: test that scan mode produces expected report format
echo "/skeall --scan ~/.claude/skills/my-skill/" | claude --print
# Check output contains: "Score:", "STRUCTURE", "FRONTMATTER", "CONTENT"
```

### What to test

| Area | Test | Pass criteria |
|------|------|---------------|
| Activation | Trigger phrases from description field | Skill loads and responds |
| Core workflow | Main mode end-to-end | Output matches documented format |
| Edge cases | Empty input, missing files, invalid paths | Helpful error message, not crash |
| Cross-platform | Same SKILL.md on different LLM platform | Same general behavior |

## Level 3: Programmatic testing (for distributed skills)

Use the Claude API to run automated test suites.

```python
# Pseudocode for API-based skill testing
test_prompts = [
    {"input": "trigger phrase 1", "expect_contains": "expected output pattern"},
    {"input": "trigger phrase 2", "expect_contains": "expected section"},
    {"input": "unrelated prompt", "expect_not_contains": "skill output"},
]

for test in test_prompts:
    response = claude_api.send(test["input"])
    assert test["expect_contains"] in response
```

## Evaluation-driven development

Build test scenarios BEFORE writing skill instructions. This is the single most effective practice from Anthropic's guide.

### The workflow

1. **Identify gaps** -- what queries should the skill handle?
2. **Create test scenarios** -- 3-5 input/expected-output pairs
3. **Baseline** -- try the queries WITHOUT the skill to see default behavior
4. **Write minimal** -- add just enough instructions to pass the tests
5. **Iterate** -- run tests again, tighten instructions where needed

### Claude A/B pattern

Use two Claude sessions:
- **Claude A** writes/edits the skill
- **Claude B** tests the skill in a fresh session (no context bleed)

This prevents the "works because I just wrote it" bias.

### Cross-model testing

Test with all Claude model tiers you plan to support:
- **Haiku** needs more explicit, step-by-step instructions
- **Sonnet** handles moderate ambiguity
- **Opus** can work with less prescriptive guidance

If your skill must work across models, aim for instructions clear enough for Haiku.

## Testing checklist

Use this after creating or improving a skill:

| # | Check | Status |
|---|-------|--------|
| 1 | All trigger phrases from description field activate the skill | |
| 2 | Main workflow produces correct output format | |
| 3 | At least one negative test (unrelated prompt) passes | |
| 4 | Error cases produce helpful messages | |
| 5 | Output contains no hallucinated paths or APIs | |
| 6 | Skill works with the target LLM platform(s) | |
| 7 | Tested with at least 2 model tiers (e.g., Haiku + Opus) | |
| 8 | Test scenarios created BEFORE skill instructions were written | |

## Test scenarios for completeness checks (C9-C11)

### C9: Routing table completeness

Create a skill with references/ containing 3 files but only 2 listed in the routing table.

```text
test-skill/
├── SKILL.md          # routing table lists api.md and examples.md
└── references/
    ├── api.md
    ├── examples.md
    └── config.md     # NOT in routing table
```

**Expected:** Scan reports `[WARN] C9 MEDIUM -- references/config.md not listed in routing table`

### C10: Internal count consistency

Create a skill whose description says "covers 6 modules" but body only documents 4.

```yaml
description: API testing tool covering 6 modules.
```

Body contains: `## Module 1`, `## Module 2`, `## Module 3`, `## Module 4` (only 4).

**Expected:** Scan reports `[WARN] C10 MEDIUM -- Description claims 6 modules, body contains 4`

### C11: Stale references

Create a skill documenting a function `getUserProfile()` that doesn't exist in the referenced SDK.

**Expected:** Scan reports `[WARN] C11 MEDIUM -- getUserProfile() not found in referenced source. Verify against actual SDK.`

**Note:** C11 is a best-effort check. Flag suspicious patterns (phantom-sounding function names, very old version numbers) but don't require full SDK verification during automated scans.

---

## Common testing pitfalls

| Pitfall | Fix |
|---------|-----|
| Testing only the happy path | Add edge cases: empty input, missing files, wrong format |
| Testing in same session as development | Start fresh session to avoid context bleed |
| Not testing trigger phrases | Users find skills through triggers, not direct invocation |
| Skipping negative tests | A skill that activates on everything is worse than one that activates on nothing |
