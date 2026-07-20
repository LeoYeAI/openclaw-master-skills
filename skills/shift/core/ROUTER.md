# SHIFT — ROUTER
# Task classification: decides which sub-identity (if any) handles the user's message.

## Responsibilities

1. **Fast-path check**: Is this a trivial greeting/acknowledgment? If so, return `none` immediately.
2. **Keyword matching**: Score each persona's keyword list against the user's message.
3. **Confidence threshold**: Only trigger a persona if score >= `minConfidence`.
4. **Explicit override**: If user used `/delegate <persona>`, route to that persona regardless of scoring.
5. **Complexity gate for Runner**: Runner requires explicit keyword match, not just short message.

## Fast-Path: Trivial Messages

These ALWAYS return `none` (master handles directly):

```
"hi", "hey", "hello", "yo", "sup",
"thanks", "thank you", "ty",
"ok", "sure", "got it", "makes sense", "cool", "nice",
"that was fast", "nice one", "lol", "haha"
```

Any message containing only these (case-insensitive, trimmed) → `none`.

## Keyword Scoring

For each enabled persona:
1. Count keyword matches in the user's message (case-insensitive, whole-word match)
2. Divide by total keywords in the persona's list → raw score (0.0 to 1.0)
3. If raw score >= `routing.minConfidence`, add to candidates

## Tie-Breaking

If multiple personas score above threshold:
- Higher raw score wins
- If tied, prefer order: codex > researcher > runner

## Runner: Explicit-Only Gate

Runner's routing has `requireExplicit: true`. This means:
- Even if Runner keywords match, Runner is only triggered if the message is predominantly a Runner task
- The full message must match Runner's domain, not just contain a keyword
- Practical: Runner is for "quick what-is-X" type queries, not "implement binary search in Python" (that's codex)

## Explicit Override

User can force delegation with `/delegate <persona> <task>`:
- Extract `<persona>` from the command (codex | researcher | runner)
- Validate persona is enabled
- Route to that persona, ignore keyword scoring

## Cost Budget Check

Before routing, ROUTER checks:
```
if costManagement.enabled AND hourlySpend >= costBudgetPerHour:
    return "none"  # master handles everything
```

## Output

Returns a routing decision:

```
{
  persona: "codex" | "researcher" | "runner" | null,
  confidence: 0.0-1.0,
  reason: "keyword_match:code,debug" | "explicit_override" | "fast_path:trivial",
  fastPathReason: null | "greeting" | "acknowledgment"  # if persona is null
}
```

If `persona` is `null`, the master handles the message directly.

## Edge Cases

| Input | Decision |
|---|---|
| "hi" | `none` (greeting) |
| "thanks!" | `none` (acknowledgment) |
| "write a function to sort a list" | `codex` (code keywords) |
| "analyze the pros and cons of microservices" | `researcher` |
| "what is python" | `runner` (explicit) |
| "implement quicksort in python" | `codex` (code dominates) |
| "thanks but can you also check the git log" | `codex` (code keyword present) |
| Empty message | `none` (master handles gracefully) |
| Message in foreign language | Route based on keywords (language-agnostic) |
