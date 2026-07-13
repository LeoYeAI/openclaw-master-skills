# PROCESSING LOGIC — v3.1 (Reddit-Only)
## Integrated into SKILL.md logic layer

---

## Step 0: Input Validation & Extraction

### 0.1 — Parse Spec

```
PRODUCT_NAME     = [exact name]
ONE_LINER        = [one sentence]
CORE_PROBLEM     = [pain point in user language]
TARGET_AUDIENCE  = [role + stage + context]
KEY_FEATURES     = [3-5, ranked]
PRICING_MODEL    = [free | freemium | paid | open-source]
PRODUCT_STAGE    = [pre-launch | beta | live]
PRODUCT_URL      = [link or "not yet"]
COMPETITORS      = [list with notes]
```

### 0.2 — Derive Variables

```
PAIN_PHRASES     = 3-5 phrases someone would type on Reddit when frustrated
AUDIENCE_SIGNALS = Subreddit flairs, post patterns, bio keywords
SWITCHING_COST   = low | medium | high
OFFER_TYPE       = Derived from PRICING + STAGE (see SKILL.md mapping)
MAKER_FRAMING    = "i built" (maker) or "i've been using" (user)
```

### 0.3 — Session State

```
SESSION_STATE = {
  session_id:        [unique per run]
  product:           [PRODUCT_NAME]
  phase:             [research | discovery | draft | approve | execute | monitor]
  approval_level:    [1: batch | 2: individual | 3: strict]
  thread_queue:      []
  drafts:            []
  approved:          []
  sent:              []
  contacted_users:   []    # from data/contacted_users.json
  banned_subs:       []    # from config/banned_list.json
  rate_limits: {
    replies_this_hour: 0,
    dms_today: 0,
    per_sub_today: {},     # {subreddit: count}
    session_total: 0,
    day_total: 0,
    last_action_time: null
  }
}
```

### 0.4 — Validate

```
- [ ] PAIN_PHRASES sound like real frustration
- [ ] AUDIENCE_SIGNALS map to specific subreddits
- [ ] OFFER_TYPE matches product stage/pricing
- [ ] At least 2 competitors identified
- [ ] PRODUCT_URL present or explicitly "not yet"
- [ ] contacted_users loaded
- [ ] banned_subs loaded
```

---

## Phase 1: Research

### Subreddit Map Logic

```
Step 1: Start from AUDIENCE_SIGNALS → candidate list
Step 2: Score (5 axes, 0-1): problem_discussed, audience_present, 
        activity_level, tool_friendly, dm_receptive
Step 3: VERIFY via browser/API:
        Visit subreddit, check last post, read sidebar, check DM policy
        Mark: ✅ verified | ⚠️ unverified | ❌ inaccessible
Step 4: Rank. Include only 3+/5.
Step 5: Entry strategy per sub:
        HIGH + strict → contribute 1-2 weeks first
        HIGH + open → jump in with value-first replies
        MEDIUM → lurk, learn tone, then contribute
Step 6: DM culture:
        Professional/networking → DMs likely OK
        Help/support → DMs OK if referencing a post
        Discussion/memes → DMs unwelcome
        Sidebar policy → follow explicitly
```

### Signal Logic

```
Step 1: PAIN_PHRASES → 4+ search variations each
Step 2: Assign channel via decision tree
Step 3: Generate Reddit search queries (must return real results)
Step 4: Recency: replies 7d, DMs 3d, urgent 24h
Step 5: Prioritize: conversion × volume × competition
```

---

## Phase 2: Discovery

```
For each signal:
  1. SEARCH Reddit (praw or browser)
  2. FILTER: age, status, engagement ≥ 1, not duplicate, not contacted, not banned
  3. SCORE (0-10):
     signal_match (0-3):
       3.0 = exact phrase match
       2.0 = clearly same problem
       1.0 = tangential
     freshness (0-2):
       2.0 = <6h, 1.5 = 6-24h, 1.0 = 1-3d, 0.5 = 3-7d
     engagement (0-1.5):
       1.5 = 3-15 replies, 1.0 = 1-3, 0.5 = 15-30, 0 = 30+ or 0
     community_rank (0-2): from map score
     low_competition (0-1.5):
       1.5 = no product recs, 1.0 = 1-2, 0.5 = 3-5, 0 = 5+
  4. DETERMINE action (Reply / DM / Both)
  5. ADD to thread_queue
  6. STOP at 50 items or all signals searched
```

---

## Phase 3: Drafting

```
For each selected thread:
  1. READ full thread: OP post + all replies + OP's follow-ups
  2. EXTRACT: specific situation, what tried, tone, values
  3. PICK variant: experience / comparison / problem-solving
  4. DRAFT: structure-first, thread details, product at end
  5. For DMs: reference SPECIFIC detail, calibrate by SWITCHING_COST + STAGE
  6. RUN quality gates → FAIL = rewrite (not just flag)
  7. CROSS-CHECK: different from other drafts? respects sub rules?
```

### Personalization Depth

```
Level 1 (minimum): Thread topic + OP handle
Level 2 (target): Specific details, what they tried, their constraints
Level 3 (when possible): Public post history context. NEVER stalk
```

---

## Phase 4: Approval

```
For each draft:
  1. Show: thread context, signal, score, recommended action
  2. Show: full draft text + quality check results
  3. Actions: [Approve] [Edit] [Reject] [Skip]
  4. Edit → re-run quality gates
  5. Reject + feedback → log for future calibration

After all reviewed:
  Summarize → estimate time (rate limits) → final YES required
```

---

## Phase 5: Execution

### Pre-Send (every message)

```
1. RATE LIMIT: replies_this_hour < 5? last_same_sub > 2min? dms_today < 10?
   session_total < 20? day_total < 30? → ANY fail = queue for later
2. THREAD STATUS: unlocked? accepting replies? → STALE = skip
3. DUPLICATE: user in contacted_users? already replied? → YES = hard block
4. COMMUNITY: in banned_subs? flagged recently? → YES = skip
```

### Send

```
1. EXECUTE: reddit_post.py --action [reply|dm] --thread [id] --text [text]
2. VERIFY: check response (200 = success), confirm visible
3. UPDATE: sent list, rate counters, contacted_users
4. WAIT: cooldown + random jitter (±30s)
```

### Error Handling

```
429 → Stop, parse retry-after, queue remaining
403 → Stop, check ban, inform user, watch list
404 → Skip (deleted), continue
Network → Retry once (30s), then skip
Other → Log, skip, continue
```

### Safety Triggers (after EVERY action)

```
Removal detected:
  → +1 removal count for sub, pause sub 48h
  → 2+ removals same sub → permanent ban list

Warning detected:
  → Pause ALL 24h, inform user, require explicit resume

Ban detected:
  → FULL STOP, inform user, add to banned_subs

Global removal rate > 10%:
  → FULL STOP, force review
```

---

## Phase 6: Monitor

```
Schedule: 30min (first 24h), 2h (24-72h), daily (72h+), stop at 7d

For each sent message:
  Check: new replies, DM responses, vote count, removal status

Response → alert user, draft follow-up (require approval)
Negative → priority flag, suggest response strategy
"Not interested" → add to do-not-contact

Metrics (with trend arrows ↑→↓):
  reply_response_rate, dm_response_rate, upvote_ratio, removal_rate

Thresholds:
  response < 10% after 20 actions → suggest adjusting approach
  removal > 5% → suggest reviewing strategy
  DM response > 50% → suggest increasing DM focus
```

---

## Persistence

```
Save after every phase change:
  data/subreddit_map.json     data/signals.json
  data/style_guide.json       data/thread_queue.json
  data/drafts/*.json          data/approved/*.json
  data/sent/*.json            data/contacted_users.json
  config/banned_list.json     logs/actions.log
  logs/errors.log             logs/metrics.log

On resume: load state, check queued-but-unsent, run missed monitors
```
