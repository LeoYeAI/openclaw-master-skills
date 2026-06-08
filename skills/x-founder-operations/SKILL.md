---
name: x-founder-operations
description: Systematic X (Twitter) operations skill for founders, indie developers, and tech professionals. Implements a daily Plan-Do-Check-Act closed loop with content strategy (5-pillar system), multimodal creation, thread growth playbook, engagement and community building, product promotion integration, persona development, competitor analysis, and data-driven continuous improvement. Use when managing an X account, planning content, analyzing tweet performance, engaging with community, running competitive analysis, or optimizing posting strategy.
auto_invoke: true
examples:
  - "Plan today's X content and engagement"
  - "Review yesterday's tweet performance and iterate"
  - "Draft a thread about our latest product feature"
  - "Analyze competitor accounts and find engagement opportunities"
  - "Run weekly X operations review"
  - "Help me optimize my X profile for conversions"
  - "What content should I post this week?"
  - "Analyze my posting times and suggest improvements"
---

# X Founder Operations

Systematic X (Twitter) account operations for founders, indie developers, and tech professionals.

## Who This Is For

- **Founders**: Building a brand, generating leads, fundraising, hiring, and establishing thought leadership while running a company
- **Indie developers**: Growing an audience around products, sharing the build journey, converting followers to users
- **Tech professionals**: Building a personal brand, establishing domain expertise, expanding professional network

This skill adapts to your specific role, goals, and growth stage through configurable profiles and goals.

## Core Philosophy

### Three Pillars

1. **Authenticity First**: Your persona is a focused version of who you really are, not a character you play. People follow people, not brands.
2. **Value Before Promotion**: 80% of content should deliver genuine value. Trust is built slowly and lost quickly.
3. **Data-Driven Evolution**: Every post generates data. Every data point informs the next decision. Strategy evolves through empirical results, not gut feeling.

### Data Integrity (Non-Negotiable)

- **NEVER fabricate tweet content, metrics, or URLs**
- **NEVER guess or hallucinate to fill data gaps**
- **ALWAYS validate data through the validation workflow**
- **ALWAYS mark missing data as `null`, never assume values**

When API calls fail: STOP, report the failure honestly, and never proceed with fabricated data. See [Data Validation Script](scripts/x_data_validator.py) for the full validation workflow.

## Quick Start

### 1. Set Up Your Profile

Copy and customize the config templates:

```
config/profile.example.json → config/profile.json
config/goals.example.json → config/goals.json
config/watchlist.example.json → config/watchlist.json
config/content-calendar.example.json → config/content-calendar.json
```

Fill in your handle, role, product info, voice attributes, and target audience. See [Profile Optimization](references/profile-optimization.md) for guidance on optimizing your X profile.

### 2. Define Your Goals

In `config/goals.json`, set:
- Primary objective (brand building, lead gen, fundraising, hiring, thought leadership)
- Growth stage (early, growth, established, authority)
- Monthly and quarterly targets
- Content mix ratios

See [Growth Benchmarks](references/growth-benchmarks.md) for realistic targets by growth stage.

### 3. Build Your Watchlist

In `config/watchlist.json`, identify:
- 5-10 core circle accounts for daily engagement
- 3-5 competitor accounts to monitor
- Industry and media accounts to track
- Relevant X Communities to join

### 4. Start the Daily Loop

Follow the [Operations Methodology](references/methodology.md) PDCA loop:

```
Morning: Scan → Plan → Warm Up (30-45 min)
Daytime: Create → Post → Engage (throughout the day)
Evening: Check metrics → Reflect → Plan tomorrow (15-20 min)
```

## Daily Operations Loop

The core operating system. See [Methodology](references/methodology.md) for full details.

### Morning Phase: Plan + Warm Up

1. **Scan**: Check overnight mentions, core circle activity, trending topics
2. **Plan**: Select today's content from calendar, prepare tweet drafts
3. **Warm up**: Spend 15-20 min replying to 10-15 accounts from your core circle (this primes the algorithm before your own posts)

### Execution Phase: Create + Post + Engage

4. **Post** 2-3 tweets at optimal windows (see [Cron Schedule](references/cron-schedule.md)), spaced 2-3 hours apart
5. **Stay active** 30-60 min after each post — reply to every comment in the first hour
6. **Engage** with core circle and community 2-3 times throughout the day
7. No external links in main tweet body — always put links in the first reply

### Evening Phase: Check + Reflect

8. **Collect metrics** for today's posts
9. **Quick reflection** using [Daily Review Template](templates/daily-review.md)
10. **Plan tomorrow**: draft content, identify engagement targets

### Weekly/Monthly/Quarterly

- **Weekly** (Sunday evening): Performance review, content audit, A/B test assessment, next week planning. Use [Weekly Review Template](templates/weekly-review.md).
- **Monthly**: Goal progress evaluation, strategy assessment, competitor analysis, persona check. Use [Monthly Review Template](templates/monthly-review.md).
- **Quarterly**: Major strategy review, goal reset, persona evolution, skill updates.

## Content Strategy

See [Content Strategy](references/content-strategy.md) for the full framework.

### Five Content Pillars

| Pillar | Target % | Purpose |
|--------|----------|---------|
| Technical Depth | 40% | Tips, insights, tutorials — builds authority |
| Industry Pulse | 25% | Hot takes, predictions, trend analysis — builds thought leadership |
| Builder's Journey | 25% | Build-in-public, decisions, lessons — builds connection |
| Community Value | 10% | Questions, polls, resources — builds community |
| Personal Touch | woven in | Humor, personality, human moments — builds "活人感" |

### Content Pipeline

```
Ideation → Drafting → Review → Scheduling → Posting → Measurement
```

Each step has quality checks. See [Content Strategy: Content Pipeline](references/content-strategy.md) for details.

### Proven Content Formulas

- **Claim + Evidence + CTA**: Bold claim, specific proof, discussion prompt
- **Story + Lesson + Takeaway**: Brief narrative, what happened, actionable insight
- **Question + Context + Invitation**: Thoughtful question, why you're asking, invite perspectives
- **List + Value + CTA**: Numbered items with brief explanations, bookmark/follow prompt
- **Reaction + Analysis + Prediction**: News reference, your unique analysis, what happens next

### Content Repurposing

- High-performing thread → 5-7 standalone tweets over the following week
- Popular single tweet → expand into a full thread
- Thread → blog post or newsletter; blog → thread
- Repost top content every 3-4 weeks with fresh phrasing

## Thread Strategy

Threads are the highest-leverage growth mechanism on X. See [Thread Playbook](references/thread-playbook.md).

### Thread Architecture

```
Hook (stop the scroll) → Context → Value Delivery (one point per tweet) → Summary → CTA
```

### Key Guidelines

- Optimal length: 5-7 tweets for most founders
- Post at 08:00-10:00 in target audience timezone
- Include visuals in 60-70% of thread tweets
- Prepare day before, post Tuesday-Thursday
- Target: 1-2 threads per week

## Multimodal Content

See [Multimodal Guide](references/multimodal-guide.md) for complete guidance.

### Impact

- Native video: ~10x distribution vs text-only
- Images: 2-3x engagement vs text-only
- Visuals increase dwell time (key algorithm signal)

### Visual Types

| Type | Best For |
|------|----------|
| Screenshots | Product demos, code output, real data, dashboards |
| Diagrams | System architecture, workflows, mental models |
| Code snippets | Technical tutorials, debugging stories |
| Memes | Industry humor, personality, cultural commentary |
| Data visualizations | Research, trends, build-in-public metrics |
| Video (native) | Product demos, talking head takes, tutorials |

### The "活人感" Rule

Every visual should feel like a real person made it. Slightly imperfect screenshots, hand-drawn diagrams, and real workspace photos signal authenticity. Overly polished, stock-photo, or obviously AI-generated visuals signal corporate or fake.

## Product Integration ("夹带私货")

See [Product Integration](references/product-integration.md) for the full framework.

### Three Tiers

| Tier | What | Frequency | How |
|------|------|-----------|-----|
| Tier 1: Background | Product exists in your world, not the subject | Default mode | Bio, profile, pinned tweet do the work |
| Tier 2: Contextual | Product mentioned as example within a broader insight | ~10% of posts | "When we built [X], we found..." |
| Tier 3: Direct | Product is the subject: launches, milestones, demos | ~10% of posts | Launch threads, milestone celebrations |

### Golden Rule

If you removed the product mention, the tweet should still be valuable. The product is the proof, not the point.

### CTA Optimization

- Never put links in the main tweet (30-50% algorithm penalty)
- Soft CTAs work better than hard sells on X
- Match CTA to relationship stage: new followers → "follow for more"; engaged followers → "try it"

## Engagement Playbook

See [Engagement Playbook](references/engagement-playbook.md) for full details.

### Engagement Funnel

```
Stranger → Lurker → Follower → Fan → Advocate → Customer/Partner
```

### Core Circle

Identify 20-30 key accounts. Engage with Tier 1 accounts daily, Tier 2 accounts 3-4x/week, Tier 3 opportunistically. See [Watchlist Config](config/watchlist.example.json).

### Reply Quality Framework

| Level | Type | Impact |
|-------|------|--------|
| S | Data/Evidence | Very high |
| A | Novel Perspective | High |
| B | Personal Story | High |
| C | Thoughtful Question | Medium |
| D | Agreement + Extension | Medium |
| F | Empty Agreement ("So true!") | Zero — never do this |

### Additional Channels

- **X Spaces**: Host bi-weekly audio discussions; invite guests from core circle
- **X Communities**: Post in 3-5 relevant communities; provide value, not promotion
- **DMs**: After 3+ public interactions, send genuine (not salesy) direct messages
- **X Lists**: Private lists for competitors, industry leaders, investors, potential customers

## Persona & Voice

See [Persona & Voice Guide](references/persona-voice.md).

### Voice Attributes

Define your position on each spectrum in `config/profile.json`:

- Technical Depth: Surface ←→ Deep
- Humor: Serious ←→ Playful
- Formality: Casual ←→ Formal
- Vulnerability: Guarded ←→ Open
- Boldness: Cautious ←→ Provocative

### Consistency Rules

- Maintain consistent tone across all content (the algorithm learns your pattern)
- Adapt tone to context (technical vs personal vs promotional) while keeping core voice
- Build personality anchors: recurring themes, catchphrases, or running jokes that create recognition
- For bilingual users: English for technical/international content, native language for personal/cultural content

## Algorithm Awareness

See [Algorithm Guide](references/algorithm-guide.md) for complete details.

### Key Rules

1. **First 30 minutes determine reach**: Engagement velocity in the first 15-30 min drives 80%+ of total reach
2. **Reply > Retweet > Bookmark > Like**: Algorithm weights replies highest (~1x), likes lowest (~0.5x)
3. **External links are penalized**: 30-50% fewer impressions. Links go in first reply.
4. **Consistency rewards**: Sudden posting changes trigger spam detection. Maintain steady cadence.
5. **Niche specificity**: Stay focused on 2-3 topics. Random off-topic posts dilute your algorithm placement.
6. **Negative signals are devastating**: Mute/block/report carry ~-74x weight. Never post hostile content.
7. **Video gets priority**: Native video gets ~10x distribution vs text-only.

## Goal Framework

Configure in [goals.json](config/goals.example.json). The skill adapts recommendations based on your primary objective and growth stage.

### Primary Objectives

| Objective | Key X Activities |
|-----------|-----------------|
| Brand building | Consistent voice, thought leadership content, thread strategy |
| Lead generation | Product integration, bio link optimization, CTA strategy |
| Fundraising | Industry analysis, investor engagement, traction posts |
| Hiring | Engineering challenges, culture posts, team stories |
| Thought leadership | Deep technical content, contrarian takes, Spaces hosting |
| Community building | Questions, engagement, Spaces, community participation |

### Growth Stages

| Stage | Followers | Focus |
|-------|-----------|-------|
| Early | 0-1K | Finding voice, building core circle, posting consistently |
| Growth | 1K-10K | Thread strategy, content mix optimization, relationship depth |
| Established | 10K-50K | Authority content, Spaces hosting, selective engagement |
| Authority | 50K+ | Maintaining quality, community leadership, platform leverage |

See [Growth Benchmarks](references/growth-benchmarks.md) for realistic targets by stage.

## Automated Operations

See [Cron Schedule](references/cron-schedule.md) for the full task schedule.

### Daily Automated Tasks

| Task | Timing | Purpose |
|------|--------|---------|
| Morning Scan | 30 min before Window A | Trending topics, core circle activity, overnight mentions |
| Window A Reminder | Start of posting window | Content recommendation based on calendar + scan |
| Midday Collection | Between windows | Updated trends, Window A post metrics |
| Window B Reminder | Start of posting window | Updated recommendation for evening window |
| Engagement Follow-up | 30 min after Window B | Identify reply opportunities, quote tweet candidates |
| Mentions Check | 1 hour after Window B | Categorize and prioritize mentions |
| Evening Review | End of day | Metrics collection, daily performance summary |

### Validation Workflow

All automated data collection follows this pipeline:

```
x-timeline → Get tweet list
    ↓
x-tweet-info → Get detailed metrics per tweet
    ↓
Cross-validate → ID, author, timestamp consistency
    ↓
Sanity check → Reasonable data (likes ≤ impressions, no negatives)
    ↓
Report → Mark anomalies, never guess
```

## Competitor Analysis

See [Competitor Framework](references/competitor-framework.md).

Select 5-8 benchmark accounts across three categories:
- **Aspirational** (2-3): 10-100x your size, same niche
- **Peer** (2-3): Similar size and growth stage
- **Emerging** (1-2): Smaller but growing fast

Analyze monthly: content formulas, engagement patterns, posting times, visual strategy. Extract what works, adapt to your voice.

## Tools and Scripts

### Data Validation
**File**: `scripts/x_data_validator.py`
Validates X data through a 5-layer pipeline: API status, tweet ID presence, cross-validation, metrics completeness, data sanity checks.

### Content Planner
**File**: `scripts/content_planner.py`
Reads profile, goals, and calendar config to generate daily content recommendations with content mix compliance tracking.

### Analytics Reporter
**File**: `scripts/analytics_reporter.py`
Generates performance reports using the validation workflow. Produces weekly and monthly analytics with benchmark comparisons.

### Smoke Tests (Regression Guard)

**Location**: `tests/` — 63 unit tests covering all three scripts.

Run:
```bash
# No dependencies required — uses Python stdlib unittest
python3 -m unittest discover tests/ -v

Run after any script change before shipping.

## Emergency Protocols

### API Failures
1. Retry with exponential backoff (3 attempts max)
2. If still failing: report to user with clear error
3. NEVER proceed with fabricated data

### Content Crisis
1. Pause all automated posts
2. Review recent content for issues
3. Prepare response strategy
4. Notify user immediately

### Data Anomalies
1. Flag immediately in validation report
2. Cross-check with alternative sources
3. Don't include suspicious data in analysis
4. Alert user to investigate

## References

### Methodology & Strategy
- [Operations Methodology](references/methodology.md) — PDCA daily loop, A/B testing, review cadences
- [Content Strategy](references/content-strategy.md) — 5-pillar system, content pipeline, formulas, timing
- [Thread Playbook](references/thread-playbook.md) — Thread architecture, hooks, scheduling, repurposing
- [Multimodal Guide](references/multimodal-guide.md) — Visual types, tools, "活人感" checklist
- [Product Integration](references/product-integration.md) — 3-tier promotion, CTA optimization, launch playbook

### Growth & Engagement
- [Engagement Playbook](references/engagement-playbook.md) — Funnel, core circle, reply quality, DMs, Spaces
- [Persona & Voice Guide](references/persona-voice.md) — Voice development, consistency, language mix
- [Algorithm Guide](references/algorithm-guide.md) — How the X algorithm works, optimization tactics
- [Profile Optimization](references/profile-optimization.md) — Bio, photo, pinned tweet, header

### Analysis & Benchmarks
- [Competitor Framework](references/competitor-framework.md) — Benchmark selection, analysis template
- [Growth Benchmarks](references/growth-benchmarks.md) — Industry data by account size and content type
- [Cron Schedule](references/cron-schedule.md) — Automated task schedule, error handling

### Configuration
- [Profile Config](config/profile.example.json) — Handle, role, product, voice, audience
- [Goals Config](config/goals.example.json) — Objectives, targets, KPIs, content mix
- [Watchlist Config](config/watchlist.example.json) — Core circle, competitors, communities
- [Content Calendar](config/content-calendar.example.json) — Weekly rhythm, posting windows

### Templates
- [Daily Review](templates/daily-review.md)
- [Weekly Review](templates/weekly-review.md)
- [Monthly Review](templates/monthly-review.md)
- [Performance Report](templates/performance-report.md)

## Remember

**Trust is built through consistent reliability.** Every post, every reply, every data point matters. Never compromise on data integrity. Never sacrifice authenticity for engagement.

This skill is a living system. It evolves with every daily review, every weekly analysis, and every quarterly strategy reset. The methodology ensures you're always getting smarter about what works for YOUR specific account, audience, and goals.
