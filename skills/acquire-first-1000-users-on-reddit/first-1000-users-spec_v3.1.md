# SPEC DOCUMENT — `first-1000-users`

**An OpenClaw Skill for AI-Powered Reddit Seeding**

Platform: OpenClaw (ClawBot)
Version 3.1 | February 2026
Status: Draft — Pending Supervisor Approval

---

## 1. Overview

`first-1000-users` is an OpenClaw skill that helps founders seed their product into real Reddit conversations. The AI agent analyzes a product spec, maps relevant subreddits, finds real threads, drafts personalized replies and DMs, and executes approved outreach via Reddit API.

### 1.1 Core Idea

Find people who are **already looking** for what you built on Reddit. Show up with a helpful reply in the thread and a thoughtful DM to the person who raised the problem. AI handles research, discovery, and drafting. Human approves every message before it goes out.

### 1.2 Two Engagement Channels

| Channel | When to Use | Conversion |
|---------|------------|------------|
| **Public Reply** | Thread is active, multiple people have the problem | Lower per-reply, visible to many |
| **Direct Message** | One person clearly has the pain point | Higher per-message, 1-on-1 |

### 1.3 What This Skill Is

- ✅ AI agent: researches subreddits, finds real threads, drafts personalized outreach
- ✅ Executes approved outreach on Reddit via API / browser automation
- ✅ Human-in-the-loop: every message requires explicit approval

### 1.4 What This Skill Is NOT

- ❌ Not fully autonomous — every action requires human approval
- ❌ Not a spam tool — hard-coded rate limits and anti-abuse protections
- ❌ Not a fake-account system — user's real Reddit account only

### 1.5 Execution Model

```
AI does:    Research, Search, Draft, Post (after approval), Monitor
Human does: Approve, Edit, Reject, Handle follow-up conversations

Rule: AI NEVER sends anything without explicit approval
```

---

## 2. How It Works — 6-Phase Pipeline

```
Phase 1: RESEARCH   → Analyze spec, map subreddits, generate signals
Phase 2: DISCOVERY  → Search Reddit for real matching threads
Phase 3: DRAFT      → Personalized reply/DM per thread
Phase 4: APPROVE    → Human reviews each draft [GATE]
Phase 5: EXECUTE    → Post approved messages
Phase 6: MONITOR    → Track engagement, alert on responses
```

### 2.1 Input

A `.md` file describing the product:

| Section | What to Include |
|---------|----------------|
| Product name & one-liner | What it is in one sentence |
| Problem it solves | Pain point in user's language |
| Who it's for | Target audience (specific) |
| Key features | Top 3–5 differentiators |
| Pricing | Free / freemium / paid |
| Current stage | Pre-launch / beta / live |
| Product URL | Link or "not yet" |
| Competitors | What people use today instead |

### 2.2 Outputs per Phase

| Phase | Output |
|-------|--------|
| 1. Research | Subreddit Map, Buying Signals, Style Guide |
| 2. Discovery | Ranked Thread Queue (real threads) |
| 3. Draft | Personalized messages per thread |
| 4. Approve | Human-vetted message queue |
| 5. Execute | Action log with statuses |
| 6. Monitor | Engagement report |

---

## 3. Phase 1: Research

### 3.1 Subreddit Map

Ranked list of subreddits, verified via browser/API:
- Verified size, relevance score, self-promo rules, DM culture, entry strategy
- Scored on 5 axes: problem discussed, audience present, activity, tool-friendly, DM-receptive
- Only include 3+/5 scores
- Target: **5–8 subreddits**

### 3.2 Buying Signal Library

Categorized search phrases, specific to the product:
- 5 categories: Direct Request → Comparison → Pain Point → Workflow Question → Discussion
- Each signal includes: pattern, Reddit search query, real example, engagement channel, recency filter
- At least 4 signals per category

### 3.3 Style Guide

Derived variables: OFFER_TYPE, MAKER_FRAMING, SWITCHING_COST, tone notes.

---

## 4. Phase 2: Discovery

Search Reddit for real threads matching signals. Filter by recency, engagement, competition. Score 0-10. Present ranked Thread Queue to user.

Max 50 threads per session. Refresh daily.

---

## 5. Phase 3: Draft

Read full thread → draft personalized message (not template fill-in).

**Reply structure:** Acknowledge → Help → Bridge → Soft close
**DM structure:** Reference → Empathize → Value → Introduce → Low-pressure close

Automated quality gates run before presenting to user.

**Tone:** Lowercase "i", no em dashes, human filler, messy numbers, product mention at end. 3-6 sentences for replies, 3-4 max for DMs.

---

## 6. Phase 4: Approve

Human reviews each draft: Approve / Edit / Reject / Skip. Final confirmation before execution.

---

## 7. Phase 5: Execute

Post via Reddit API or browser. Rate limits enforced:

| Action | Limit |
|--------|-------|
| Replies | 5/hour |
| Same subreddit | 2/day, 2 min cooldown |
| DMs | 10/day, 5 min between |
| Per session | 20 max |
| Per day | 30 max |

**Safety triggers:** removal → pause 48h, warning → pause all 24h, ban → full stop, removal rate > 10% → full stop.

---

## 8. Phase 6: Monitor

Track responses every 30 min (first 24h), then daily. Alert on replies. Draft follow-ups (still require approval). Never auto-reply. Never follow up on unanswered DMs.

---

## 9. Ethical Guidelines

### 9.1 Hard-Coded Rules

- Human approval required for every message
- One DM per person (contacted_users database)
- Rate limits cannot be overridden
- No fake accounts
- Every message personalized per thread
- Bans permanently block community
- No follow-up DMs on no-reply
- Auto-pause on removals/warnings

### 9.2 Disclosure

User is the sender. AI is a drafting tool. User approves every message. Analogous to having an assistant draft messages. If Reddit rules change to require AI disclosure, skill should be updated.

---

## 10. Technical Requirements

### 10.1 Skill Structure

```
~/.openclaw/skills/first-1000-users/
├── SKILL.md                    # Main instructions (OpenClaw format)
├── scripts/
│   ├── reddit_search.py        # Search for matching threads
│   ├── reddit_post.py          # Post replies, send DMs
│   ├── reddit_verify.py        # Verify subreddit status/rules
│   ├── engagement_tracker.py   # Track responses
│   └── rate_limiter.py         # Enforce rate limits
├── config/
│   ├── rate_limits.json
│   ├── approval_level.json
│   └── banned_list.json
├── data/
│   ├── product_spec.md
│   ├── subreddit_map.json
│   ├── signals.json
│   ├── style_guide.json
│   ├── thread_queue.json
│   ├── drafts/
│   ├── approved/
│   ├── sent/
│   └── contacted_users.json
└── logs/
    ├── actions.log
    ├── errors.log
    └── metrics.log
```

### 10.2 Dependencies

```yaml
requires:
  env: [REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]
  bins: [python3, playwright-cli]
  python: [praw, playwright]
```

---

## 11. Build Plan — 2-Day Sprint

### Day 1: Research + Discovery + Draft (Phase 1-3)

**Morning:**
- Set up OpenClaw skill directory and SKILL.md with YAML frontmatter
- Implement Step 0: spec parsing, variable extraction, validation
- Implement Phase 1: subreddit mapping with live verification, signal generation, style guide
- Write `reddit_verify.py` for subreddit rule/status checking
- Test: feed product spec → verify research output quality

**Afternoon:**
- Write `reddit_search.py` for thread discovery using signal phrases
- Implement thread scoring (signal_match + freshness + engagement + competition)
- Implement Phase 3: per-thread drafting with quality gates
- Implement approval presentation format
- Test: signal → real threads → personalized drafts → approval flow

**Day 1 Deliverable:** Working pipeline from spec input through draft approval.

### Day 2: Execute + Monitor + Safety (Phase 4-6)

**Morning:**
- Write `reddit_post.py` for posting replies and sending DMs
- Implement `rate_limiter.py` with hard limits
- Build contacted_users database for duplicate prevention
- Implement safety triggers (removal/ban detection, auto-pause)
- Implement error handling (429, 403, 404, network failures)
- Test: approved draft → execute → verify posted → log

**Afternoon:**
- Write `engagement_tracker.py` for response monitoring
- Implement follow-up draft suggestions (with approval gate)
- Full pipeline test: spec → research → discover → draft → approve → execute → monitor
- Test edge cases: thread locked, user deleted, rate limit hit, post removed
- Write documentation and example output
- Package and submit

**Day 2 Deliverable:** Complete skill with execution, monitoring, and safety.

---

## 12. Success Criteria

| Criteria | Target |
|----------|--------|
| Subreddit relevance | 4/5 top suggestions are active + on-topic |
| Signal accuracy | 5+ real threads per top 3 signals |
| Thread discovery | 10+ threads per session |
| Draft quality | 90%+ pass automated gates |
| Human approval rate | 70%+ approved without major edits |
| Execution success | 95%+ messages post successfully |
| Engagement | 30%+ reply response rate |
| Safety | 0 bans, < 5% removal rate in first 50 actions |

---

*End of Specification — first-1000-users v3.1 (Reddit-only)*
