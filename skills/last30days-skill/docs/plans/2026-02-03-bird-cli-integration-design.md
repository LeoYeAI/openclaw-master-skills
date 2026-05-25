# Bird CLI Integration Design

**Date:** 2026-02-03
**Status:** Approved

## Overview

Add Bird CLI as an alternative X/Twitter search source for the last30days skill. Bird uses browser cookie authentication (free, no API key) and provides direct access to X's GraphQL API.

## Goals

- Provide free X search without requiring xAI API key
- Seamless fallback: Bird → xAI → WebSearch
- Interactive onboarding for users without Bird installed
- Output parity with existing xAI implementation

## Detection & Priority Flow

```
On startup:
1. Check: Is Bird installed? (`which bird`)
   ├─ No → Offer to install: "Bird CLI not found. Install for free X search? (y/n)"
   │        ├─ Yes → Run `npm install -g @steipete/bird`
   │        └─ No → Continue to step 2
   │
   └─ Yes → Check: Is Bird authenticated? (`bird whoami`)
            ├─ Success → Use Bird for X searches
            └─ Fail → Show: "Bird auth failed. Run `bird check` to diagnose."
                      Continue to step 2

2. Fall back to xAI if XAI_API_KEY exists
3. Fall back to WebSearch if nothing else available
```

**Priority order:** Bird → xAI → WebSearch

## New Module: `scripts/lib/bird_x.py`

### Functions

- `is_bird_installed()` → checks `which bird`, returns bool
- `is_bird_authenticated()` → runs `bird whoami`, returns username or None
- `install_bird()` → runs `npm install -g @steipete/bird`, returns success bool
- `search_x(topic, from_date, to_date, depth)` → runs `bird search` with JSON output
- `parse_bird_response(json)` → converts to same format as `xai_x.parse_x_response()`

### Search Command

```bash
bird search "Claude Code skills" --since 2026-01-04 -n 30 --json
```

- `--since` filters to last 30 days
- `-n 30` controls result count (maps to depth: quick=12, default=30, deep=60)
- `--json` gives machine-readable output

### Output Mapping

| Bird field | Our field |
|------------|-----------|
| `text` | `text` |
| `permanent_url` | `url` |
| `user.screen_name` | `author_handle` |
| `created_at` | `date` (parse to YYYY-MM-DD) |
| `like_count` | `engagement.likes` |
| `retweet_count` | `engagement.reposts` |
| `reply_count` | `engagement.replies` |
| `quote_count` | `engagement.quotes` |

Relevance: Default to 0.7, let `score.py` re-rank based on engagement.

## Modified Files

| File | Change |
|------|--------|
| `env.py` | Add `get_x_source()` → returns `'bird'`, `'xai'`, or `None` |
| `last30days.py` | Check Bird availability with interactive install prompt before research |
| `last30days.py` | In `_search_x()`, dispatch to `bird_x` or `xai_x` based on source |
| `ui.py` | Add `prompt_bird_install()` and `show_bird_auth_help()` |

## Unchanged Files

- `normalize.py` - Bird output matches xAI format after parsing
- `score.py` - Same scoring logic applies
- `dedupe.py` - Same deduplication logic
- `render.py` - X results labeled as "X" regardless of backend

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Bird installed but no browser cookies | Show `bird check` guidance, fall back to xAI |
| Bird search returns 0 results | Retry with simplified query (same as xAI logic) |
| Bird search times out | Fall back to xAI if available, else WebSearch |
| npm not installed (can't install Bird) | Skip Bird, continue with xAI/WebSearch |
| User declines Bird install | Remember for session, don't ask again |

**Timeout:** 30 seconds for Bird commands

## Output Labels

Results labeled as "X" regardless of whether Bird or xAI was used. Users care about the data, not the backend.
