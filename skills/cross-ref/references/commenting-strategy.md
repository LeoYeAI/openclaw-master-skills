# Commenting Strategy & Rate Limits

## GitHub API Rate Limits

GitHub enforces several rate limits relevant to commenting:

### REST API Limits
- **Authenticated requests**: 5,000 per hour
- **Comment creation**: Subject to secondary rate limits (abuse detection)
- **Secondary rate limit**: ~20 content-creating requests per minute (undocumented
  but observed — GitHub may throttle or 403 earlier)

### Practical Observed Limits
- GitHub's abuse detection triggers on fixed-interval patterns
- The 403 "secondary rate limit" response has no Retry-After header
- **Never use fixed intervals** — jitter-based timing is mandatory

## Anti-Abuse Approach

The posting script (`post-comments.sh`) uses three mechanisms to avoid abuse
detection while maintaining throughput:

### Jitter-Based Intervals
Every comment is followed by a random pause (default 75-135s). The base target
is ~90s between comments, but ±45s of jitter makes the pattern look organic
rather than automated. Fixed-rate patterns (e.g., exactly 120s between comments)
are exactly what GitHub's abuse detection targets.

### Breathing Pauses
After every 30-50 comments (randomized), the script takes a longer pause of
8-15 minutes. This simulates a human taking a break. Without this, sustained
commenting for >1 hour often triggers abuse detection even within rate limits.
The interval is re-randomized after each pause.

### Exponential Backoff
On API failure (403/429), the script retries with exponential backoff:
2min → 4min → 8min → 16min → 30min (cap). After 5 failed attempts, it saves
progress and exits. On resume after a rate-limit exit, there is a 5-minute
grace period before the first comment.

## Commenting Tiers

### Tier 1: Conservative (Recommended)
```
Rate:     1 comment per 75-135s (jitter, ~40/hour)
Daily:    60 comments max
Duration: ~90 min for 60 comments
Trigger:  High confidence only
```

Best for first-time runs and repos you don't own. Stays well below abuse
detection. If you have 300 high-confidence links, this takes 5 days.

### Tier 2: Moderate
```
Rate:     1 comment per 75-135s (jitter, ~40/hour)
Daily:    60 comments max
Duration: ~90 min for 60 comments
Trigger:  High + medium confidence
```

Same rate but includes more links. For repos where you're confident in
the analysis quality.

### Tier 3: Dry Run
```
Rate:     —
Daily:    —
Comments: 0
Duration: Instant
```

Generates the approved-comments.json but posts nothing. Always the default
mode — user must explicitly opt into posting.

## Daily Budget Calculation

```
daily_budget = 60          # configurable via arg 5
avg_jitter   = 90          # midpoint of 75-135s default
comments_per_hour ≈ 40     # 3600 / 90

# For N total comments:
days_needed = ceil(N / daily_budget)

# Time per day (approximate, not counting breathing pauses):
time_for_daily_budget ≈ daily_budget * avg_jitter / 60  # ~90 minutes
# With breathing pauses (~10 min every ~40 comments):
time_with_pauses ≈ 90 + 10 = ~100 minutes for 60 comments
```

## Scheduling Across Multiple Days

When total comments exceed the daily budget:

```
Day 1: Comments 1-60    (links #1 through #60)
Day 2: Comments 61-120  (links #61 through #120)
Day 3: Comments 121-180 (links #121 through #180)
...
```

The skill saves progress to `comment-progress.json` after each comment.
On resume, it reads the progress file and continues from where it stopped.

**Important**: The daily counter resets based on UTC midnight. The skill
tracks `day_start_utc` in the progress file and resets `day_count` when
a new UTC day begins.

## Comment Format

Comment templates are defined in SKILL.md Phase 6. This file only covers
rate limiting strategy. See SKILL.md for the canonical comment format,
opener rotation, and tone guidelines.

## User Presentation

When presenting the strategy to the user, show a table:

```
┌─────────────┬───────────────────┬──────────┬───────────┬──────────────┐
│ Strategy    │ Rate              │ Daily    │ Comments  │ Est. Time    │
│             │                   │ Max      │ to Post   │              │
├─────────────┼───────────────────┼──────────┼───────────┼──────────────┤
│ Conservative│ 1/75-135s (jitter)│ 60       │ {high}    │ {calc}       │
│ Moderate    │ 1/75-135s (jitter)│ 60       │ {h+m}     │ {calc}       │
│ Dry Run     │ —                 │ —        │ 0         │ Instant      │
│ Manual Pick │ 1/75-135s (jitter)│ 60       │ {custom}  │ {calc}       │
└─────────────┴───────────────────┴──────────┴───────────┴──────────────┘
```

Then let the user choose. If total > daily max, show the multi-day plan.
