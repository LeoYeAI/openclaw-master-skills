# Auto-Detection Guide

This document details how the Agent proactively detects TIL-worthy moments during work sessions.

## Trigger Examples

### Debugging uncovered a non-obvious root cause

Good example: "The memory leak was caused by a goroutine referencing a closure variable that held the entire HTTP request body, not just the header field we needed."

Bad example: "Fixed the null pointer error by adding a nil check." (Obvious fix, no insight.)

### Language/framework behavior contradicts common assumptions

Good example: "Python's `defaultdict` calls the factory function even when you're just reading a key with `d[key]` -- it doesn't distinguish reads from writes."

Bad example: "JavaScript has both `==` and `===`." (Well-known, not surprising.)

### Refactoring revealed a superior pattern

Good example: "Replacing the chain of `if-else` handlers with a strategy map reduced the function from 80 lines to 15 and made adding new handlers a one-line change."

Bad example: "Renamed variables to be more descriptive." (Cosmetic, no pattern insight.)

### Performance optimization with measurable results

Good example: "Adding a compound index on (user_id, created_at) reduced the dashboard query from 2.3s to 12ms."

Bad example: "Used caching to make things faster." (Vague, no specifics.)

### Obscure but useful tool flag or API parameter

Good example: "git diff --word-diff=color shows inline character-level changes instead of full-line diffs, perfect for reviewing prose changes."

Bad example: "Used git log to see commit history." (Basic, widely known.)

### Two technologies interacting unexpectedly

Good example: "When using PostgreSQL's `jsonb_path_query` with a Rails `where` clause, the query planner can't use the GIN index because Rails wraps the expression in a type cast."

Bad example: "Used Redis with Rails for caching." (Standard pattern, no surprise.)

### Upgrade/migration breaking changes

Good example: "Ruby 3.2 changed `Struct` keyword arguments to be required by default -- all existing `Struct.new` calls with optional keyword args silently broke."

Bad example: "Updated Node from v18 to v20." (Fact, no insight.)

## What NOT to Detect

Do not suggest TIL capture for:

- Standard usage of tools/APIs (reading docs, running commands)
- Configuration that works as documented
- Bugs caused by typos or simple mistakes
- Widely known best practices (use environment variables, write tests, etc.)
- Anything the user already seems to know well
- Tasks where the user is actively frustrated or stressed -- wait for resolution

## Rate Limiting State Machine

```
[IDLE] ---(TIL-worthy moment detected)---> [EVALUATING]
  ^                                              |
  |                                    (check constraints)
  |                                              |
  |                              +-------+-------+
  |                              |               |
  |                     (constraints        (constraints
  |                       not met)             met)
  |                              |               |
  |                              v               v
  +----(stay idle)----------[IDLE]         [SUGGESTED]
                                              |
                                    +---------+---------+
                                    |                   |
                              (user accepts)      (user declines
                                    |             or ignores)
                                    v                   v
                               [CAPTURED]        [DONE_FOR_SESSION]
                                    |
                                    v
                             [DONE_FOR_SESSION]
```

**Constraints checked in EVALUATING state:**

1. Has a suggestion already been made this session? → If yes, stay IDLE
2. Is the user in the middle of active problem-solving? → If yes, stay IDLE
3. Is this a natural pause point (resolution or task boundary)? → If no, stay IDLE

Once in DONE_FOR_SESSION, the agent never suggests again until a new session starts.

## Suggestion Format

Append the suggestion at the end of your normal response. Never interrupt the workflow with a standalone suggestion message.

**Template:**
```
💡 TIL: [concise title of the insight]
   Tags: [tag1, tag2] · Capture? (yes/no)
```

**Example** (debugging root cause):
```
...so the memory leak was caused by the goroutine holding a reference to the entire request body.

💡 TIL: Goroutine closures can silently retain large objects, causing memory leaks
   Tags: go, concurrency · Capture? (yes/no)
```

**Example** (performance optimization):
```
...the compound index on (user_id, created_at) reduced the query from 2.3s to 12ms.

💡 TIL: Compound indexes with the right column order can yield 100x+ query speedups
   Tags: postgresql, indexing · Capture? (yes/no)
```

**Example** (migration breaking change):
```
...Ruby 3.2 changed Struct keyword arguments to be required by default.

💡 TIL: Ruby 3.2 makes Struct keyword args required by default, silently breaking existing code
   Tags: ruby, migration · Capture? (yes/no)
```

## Single Confirmation Flow

```
Agent: [normal response content]

       💡 TIL: [concise title]
          Tags: [tags] · Capture? (yes/no)

User:  yes / y / ok / sure

Agent: [Generates full entry: title, body, tags, lang]
       [POST to API or save locally]
       [Show result message]
```

The suggestion itself is the candidate. When the user says yes, the agent generates the full entry directly — no extract flow, no draft review step.

If the user ignores the suggestion, says "no", or continues with another topic, treat it as decline. Move on and do not ask again this session.
