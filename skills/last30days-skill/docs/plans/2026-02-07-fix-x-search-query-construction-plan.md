---
title: "fix: X search query too restrictive, returns 0 results on popular topics"
type: fix
date: 2026-02-07
---

# fix: X search query too restrictive, returns 0 results on popular topics

## Problem

`/last30days vibe motion best prompt techniques` returned **0 X posts** despite Vibe Motion being actively discussed on X (screenshots show posts from @Godid242, @KamilStanuch, @ColdStartTheory, @higgsfield_ai).

Root cause: `_extract_core_subject()` in `bird_x.py` produces overly specific queries. Bird/X search uses **literal keyword AND matching** — ALL words must appear in a tweet. The function kept 4 keywords (`vibe motion prompt techniques`) when only 2 (`vibe motion`) were needed.

## Three Bugs Found

### Bug 1: Multi-word noise phrases never match

```python
# Current code (bird_x.py:24-38)
noise = ['best', ..., 'what are', 'what is', 'how to', 'tips for', ...]
words = topic.lower().split()  # splits into individual words
result = [w for w in words if w not in noise]  # compares "what" against "what are" → no match!
```

`"what are people saying about DeepSeek R1"` → keeps `"what are people saying"` → **LOSES THE ENTIRE TOPIC**.

The multi-word entries (`"what are"`, `"how to"`, `"tips for"`, `"use cases"`) are dead code. They never match because `.split()` creates individual words but the noise list has multi-word strings.

### Bug 2: Missing meta/research words

The noise list has `"prompting"` but not `"prompt"`, `"prompts"`, `"techniques"`, `"tips"`, `"tricks"`, `"methods"`, etc.

- `"vibe motion best prompt techniques"` → `"vibe motion prompt techniques"` (4 words, should be 2)
- `"nano banana pro prompts for gemini"` → `"nano banana pro prompts"` (4 words, should be 3)

### Bug 3: No retry on 0 results

Reddit has multi-stage retry: full query → simplified core → subreddit fallback. X search runs once and accepts whatever comes back, even 0 results.

## Proposed Fix

All changes in `scripts/lib/bird_x.py`.

### Step 1: Fix `_extract_core_subject()` — strip phrases first, then words

```python
def _extract_core_subject(topic: str) -> str:
    """Extract core subject from verbose query for X search."""
    text = topic.lower()

    # Phase 1: Strip multi-word prefixes/suffixes (order matters - longest first)
    prefixes = ['what are the best', 'what is the best', 'what are', 'what is',
                'how to', 'how do i', 'tips for', 'best practices for']
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].strip()
            break

    suffixes = ['best practices', 'use cases', 'prompt techniques',
                'prompting techniques']
    for s in suffixes:
        if text.endswith(s):
            text = text[:-len(s)].strip()
            break

    # Phase 2: Split and filter individual noise words
    noise = {'best', 'top', 'practices', 'features', 'killer', 'guide',
             'tutorial', 'recommendations', 'advice', 'prompting', 'prompt',
             'prompts', 'techniques', 'tips', 'tricks', 'methods',
             'strategies', 'review', 'reviews', 'uses', 'usecases',
             'examples', 'using', 'for', 'with', 'the', 'of', 'in', 'on',
             'about', 'latest', 'new', 'news', 'update', 'updates',
             'good', 'great', 'awesome', 'and', 'or', 'a', 'an', 'is',
             'are', 'was', 'were', 'people', 'saying', 'think', 'said'}
    words = text.split()
    result = [w for w in words if w not in noise]

    return ' '.join(result[:3]) or topic  # Max 3 words (was 4)
```

**Expected results after fix:**

| Input | Before | After |
|-------|--------|-------|
| `vibe motion best prompt techniques` | `vibe motion prompt techniques` | `vibe motion` |
| `what are people saying about DeepSeek R1` | `what are people saying` | `deepseek r1` |
| `nano banana pro prompts for gemini` | `nano banana pro prompts` | `nano banana pro` |
| `open claw best uses` | `open claw uses` | `open claw` |
| `best claude code skills` | `claude code skills` | `claude code skills` |
| `kanye west` | `kanye west` | `kanye west` |

### Step 2: Add retry with simplified query on 0 results

In `search_x()`, after the initial search, if 0 items returned, retry with just the first 2 words of the core subject:

```python
def search_x(topic, from_date, to_date, depth="default"):
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    core_topic = _extract_core_subject(topic)
    query = f"{core_topic} since:{from_date}"

    # ... existing Bird search code ...

    items = parse_bird_response(response)

    # Retry with fewer keywords if 0 results
    if not items and len(core_topic.split()) > 2:
        shorter = ' '.join(core_topic.split()[:2])
        _log(f"0 results for '{core_topic}', retrying with '{shorter}'")
        query = f"{shorter} since:{from_date}"
        # ... retry Bird search ...
        items = parse_bird_response(retry_response)

    return response  # or merged response
```

### Step 3 (optional): Cross-pollinate Reddit entities into X Phase 2

When X Phase 1 returns 0 results but Reddit found threads, extract brand/product names from Reddit thread titles and use them as X search fallback queries. This is lower priority — Steps 1-2 should fix most cases.

## Acceptance Criteria

- [x] `vibe motion best prompt techniques` returns >0 X posts (12 posts found)
- [x] `what are people saying about DeepSeek R1` produces query containing "deepseek r1" not "what are people saying"
- [x] No regressions on working queries (`kanye west`, `claude code skills`, `open claw`)
- [x] Retry fires when initial query returns 0, logged to stderr
- [x] `openai_reddit.py`'s `_extract_core_subject()` NOT changed (Reddit uses semantic search, not literal matching — the current function works fine there)

## Files to Change

- `scripts/lib/bird_x.py` — `_extract_core_subject()` rewrite + retry logic in `search_x()`
- `scripts/lib/bird_x.py` — `search_handles()` benefits automatically (calls `_extract_core_subject()`)

## Testing

```bash
# Mock mode (quick syntax check)
python3 scripts/last30days.py "vibe motion best prompt techniques" --mock --emit=compact 2>&1

# Live queries to verify X results
python3 scripts/last30days.py "vibe motion best prompt techniques" --quick --emit=compact 2>&1 | grep -E "X:|posts"
python3 scripts/last30days.py "what are people saying about DeepSeek R1" --quick --emit=compact 2>&1 | grep -E "X:|posts"

# Regression check
python3 scripts/last30days.py "kanye west" --quick --emit=compact 2>&1 | grep -E "X:|posts"
```
