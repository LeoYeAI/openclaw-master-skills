---
name: personal-brand-builder
description: >
  Transforms any OpenClaw agent into a personal brand authority engine.
  Defines the principal's unique positioning, manages presence across
  Twitter/X, LinkedIn, Instagram, YouTube, TikTok, and Podcast, and
  builds authority through strategic content, social proof, and network
  expansion. Three autonomous engines: Identity (who you are), Presence
  (how you show up), and Authority (why people trust you). Designed for
  entrepreneurs at the intersection of business, trading, and AI automation.
version: 1.0.0
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "🏆"
    security_level: L2
    required_paths:
      read:
        - /workspace/brand/identity.json
        - /workspace/brand/platforms/
        - /workspace/brand/content/
        - /workspace/brand/network/
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/brand/references/positioning.md
      write:
        - /workspace/brand/identity.json
        - /workspace/brand/platforms/
        - /workspace/brand/content/
        - /workspace/brand/network/
        - /workspace/brand/AUDIT.md
        - /workspace/.learnings/
    network_behavior:
      makes_requests: true
      request_targets:
        - https://api.telegram.org (Telegram Bot API — requires TELEGRAM_BOT_TOKEN)
        - https://api.twitter.com (Twitter/X API — requires TWITTER_API_KEY)
        - https://api.linkedin.com (LinkedIn API — optional)
      uses_agent_telegram: true
    requires.env:
      - TELEGRAM_BOT_TOKEN
      - TELEGRAM_CHAT_ID
      - TWITTER_API_KEY
      - TWITTER_API_SECRET
      - TWITTER_ACCESS_TOKEN
      - TWITTER_ACCESS_SECRET
---

# Personal Brand Builder — Authority at Scale

> "Your personal brand is what people say about you when you're not in the room."
> — Jeff Bezos

This skill transforms [PRINCIPAL_NAME] from an operator into a recognized
authority — automatically, consistently, at scale.

```
ENGINE 1 — IDENTITY
  Who you are, what you stand for, why people should follow you
  → Positioning, story, pillars, unique angle, promise
  → Stored in /workspace/brand/identity.json

ENGINE 2 — PRESENCE
  How you show up on every platform — consistently
  → Profile optimization: bio, headline, pinned posts
  → Visual coherence, tone consistency, platform-specific tactics
  → 6 platforms: Twitter/X, LinkedIn, Instagram, YouTube, TikTok, Podcast

ENGINE 3 — AUTHORITY
  Why people trust you and buy from you
  → Social proof engine, testimonials, case studies
  → Strategic networking with niche influencers
  → Guest appearances, podcast outreach, collaborations
  → Credibility content: results, data, transformations
```

---

## ENGINE 1 — IDENTITY

### The [PRINCIPAL_NAME] Brand Architecture

```
CORE POSITIONING
  Who:    Entrepreneur who uses AI + trading to build financial freedom
  For:    People who want to escape the 9-5 through systems, not hustle
  Why:    Because [PRINCIPAL_NAME] has built real autonomous revenue systems
          and documents the journey transparently

UNIQUE ANGLE (the intersection)
  Business  ×  Trading  ×  AI Automation
  = The "Autonomous Wealth" positioning
  → Nobody else teaches all three as a unified system
  → This intersection is [PRINCIPAL_NAME]'s unfair advantage

BRAND PROMISE
  "I show you how to build income systems that work while you sleep —
   using AI agents, market signals, and automated funnels."

BRAND PERSONALITY
  Tone:       Direct, real, no-fluff
  Style:      Builder who shows the work, not just the results
  Energy:     Ambitious but grounded — wealth is a tool, not a trophy
  Anti-brand: No gurus, no fake screenshots, no "passive income" clichés
```

### Brand Pillars (Content Foundation)

```
PILLAR 1 — AI AUTOMATION (40% of content)
  Topics: agents, workflows, tools, results, tutorials
  Hook:   "Here's how I automated [task] with AI"
  Goal:   Position as the practitioner who actually builds

PILLAR 2 — TRADING & MARKETS (30% of content)
  Topics: signals, setups, performance, market reads
  Hook:   "Market signal spotted — here's what I'm watching"
  Goal:   Position as a disciplined, data-driven trader

PILLAR 3 — ENTREPRENEURSHIP & FREEDOM (20% of content)
  Topics: revenue milestones, systems, mindset, lessons
  Hook:   "Month [X] building autonomous revenue — honest update"
  Goal:   Build trust through radical transparency

PILLAR 4 — BEHIND THE SCENES (10% of content)
  Topics: tools, failures, pivots, the real process
  Hook:   "What nobody tells you about [topic]"
  Goal:   Humanize the brand, increase loyalty
```

### Identity Bootstrap

```
Run this once to initialize identity.json:

python3 /workspace/brand/scripts/brand_manager.py init \
  --name "[PRINCIPAL_NAME]" \
  --positioning "autonomous-wealth" \
  --niches "business,trading,ai-automation" \
  --platforms "twitter,linkedin,instagram,youtube,tiktok,podcast"
```

---

## ENGINE 2 — PRESENCE

### Platform Strategy Overview

```
PLATFORM      ROLE                    FREQUENCY    CONTENT TYPE
───────────────────────────────────────────────────────────────
Twitter/X     Real-time authority     2-3x/day     Threads, signals, takes
LinkedIn      Professional trust      1x/day       Long-form, results, B2B
Instagram     Visual brand + reach    1x/day       Reels, carousels, stories
YouTube       Deep authority          2x/week      Tutorials, case studies
TikTok        Viral reach + discovery 1-2x/day     Hooks, quick wins, trends
Podcast       Maximum authority       1x/week      Deep dives, interviews
```

### Twitter/X — The Authority Feed

```
PROFILE OPTIMIZATION
  Name:     [PRINCIPAL_NAME] | AI × Trading × Freedom
  Bio:      Building autonomous revenue with AI agents + markets 🤖📈
            [Revenue milestone or credibility marker]
            [CTA: link to funnel or newsletter]
  Pinned:   Best-performing thread OR latest revenue update
  Banner:   Clean, professional, shows the positioning

CONTENT MIX
  40% — AI automation threads (step-by-step, show the build)
  30% — Market signals and trading takes (with data)
  20% — Entrepreneurship lessons (transparent, numbers-based)
  10% — Personal/behind the scenes (builds connection)

THREAD FORMULA
  Hook:     Bold claim or surprising result
  Body:     3-7 tweets with evidence, steps, or data
  Close:    CTA → newsletter, DM, or funnel

POSTING SCHEDULE
  08h00 — Market morning take or AI automation tip
  12h00 — Thread or long-form insight
  19h00 — Engagement post or behind-the-scenes

GROWTH TACTICS
  → Reply to top voices in AI, trading, entrepreneurship daily
  → Quote-tweet with added value (never empty quotes)
  → Space mentions with complementary creators
  → Pin updated thread every 30 days
```

### LinkedIn — The Trust Engine

```
PROFILE OPTIMIZATION
  Headline:   Building autonomous revenue systems | AI + Trading + Funnels
  About:      3-paragraph story:
              P1 — The struggle (relatable)
              P2 — The turning point (AI + trading intersection)
              P3 — The mission + CTA
  Featured:   Top case study or revenue milestone post
  Banner:     Professional, consistent with Twitter branding

CONTENT MIX
  50% — Detailed case studies and results posts
  30% — Educational posts (how-to, frameworks)
  20% — Opinion posts on AI, markets, entrepreneurship

POST FORMULA
  Line 1:   Scroll-stopping hook (short, bold)
  Lines 2-5: Context or story
  Lines 6-10: The insight or lesson
  Close:    Question for comments + CTA

GROWTH TACTICS
  → Comment on 5 posts per day in niche (value-first)
  → Connect with 10 targeted profiles per day
  → Publish articles bi-weekly for SEO + authority
  → Engage within first 30 minutes after posting
```

### Instagram — Visual Authority

```
PROFILE OPTIMIZATION
  Username:   @[principal_handle]
  Bio:        🤖 AI systems + 📈 Trading signals + 💰 Autonomous revenue
              → [benefit statement]
              👇 [CTA link]
  Profile pic: Professional, consistent with other platforms
  Highlights: Results / Tools / Daily / Behind the scenes

CONTENT MIX
  40% — Reels (educational, 15-60 seconds, hook in first 3s)
  30% — Carousels (how-to, lists, step-by-step)
  20% — Static posts (quotes, results, milestones)
  10% — Stories (daily, behind the scenes, polls)

REEL FORMULA
  0-3s:   Pattern interrupt hook ("I made €X in Y days with this")
  3-15s:  Promise or context
  15-50s: The value / the how
  50-60s: CTA (follow, link in bio, DM)

GROWTH TACTICS
  → 3 Reels per week minimum for algorithmic push
  → Stories daily to maintain engagement rate
  → Carousel saves = organic reach boost
  → Collab posts with complementary creators
```

### YouTube — Deep Authority

```
CHANNEL OPTIMIZATION
  Name:       [PRINCIPAL_NAME] — AI × Trading × Freedom
  About:      Full brand story + keywords + links
  Playlists:  "AI Automation Tutorials" / "Trading Signals" /
              "Building Autonomous Revenue" / "Tools & Systems"
  Banner:     Upload schedule + brand positioning
  Trailer:    60-second brand manifesto video

CONTENT TYPES
  Tutorial videos:   "How I built [system] with AI" (15-30 min)
  Case studies:      "Month X update — what worked, what didn't"
  Tool reviews:      "Best AI tools for [use case] in [year]"
  Trading recaps:    "Weekly market review + my signals"

VIDEO FORMULA
  0-30s:   Hook — bold promise or surprising result
  30s-2m:  What you'll learn / why it matters
  2m-end:  The value / the how (with screen recording or visuals)
  End:     CTA → subscribe + comment + link in description

SEO STRATEGY
  → Research keywords: "AI automation [year]", "how to [outcome]"
  → Title formula: [Number] + [Keyword] + [Benefit]
  → Description: first 2 lines = hook + keyword-rich
  → Tags: mix of broad and specific keywords

POSTING SCHEDULE
  2 videos per week — Tuesday and Friday
  Shorts: 1-2 per week (repurposed from Reels or clips)
```

### TikTok — Viral Reach Machine

```
PROFILE OPTIMIZATION
  Bio:        AI + Trading + Freedom 🤖📈
              [One-line proof statement]
              [Link to funnel]

CONTENT APPROACH
  → Fast, punchy, value-dense (15-60 seconds)
  → Native TikTok style — not repurposed from other platforms
  → Trending sounds + original content hybrid
  → Hook in the FIRST WORD — TikTok has zero patience

HOOK FORMATS THAT WORK
  "POV: you built an AI agent that..."
  "Things I wish I knew before trading..."
  "AI tools that [outcome] in [timeframe]"
  "Why 99% of people fail at [topic]"

POSTING SCHEDULE
  1-2 videos per day
  Best times: 07h-09h, 12h-14h, 19h-21h

GROWTH TACTICS
  → Duet and stitch top creators in niche
  → Reply to comments with video replies
  → Jump on trends within 24 hours
  → Cross-post best TikToks as YouTube Shorts and Instagram Reels
```

### Podcast — Maximum Authority

```
SHOW CONCEPT
  Name:       "Autonomous Wealth" or "[PRINCIPAL_NAME] Unfiltered"
  Format:     Solo episodes + guest interviews
  Length:     20-45 minutes
  Frequency:  Weekly (every Monday)

SOLO EPISODE FORMULA
  Topic:      Deep dive on one pillar (AI, trading, or entrepreneurship)
  Structure:
    Intro (2m):   Hook + what you'll learn
    Context (5m): Why this matters now
    Core (25m):   The framework, the how, the proof
    Close (3m):   Summary + action step + CTA

GUEST STRATEGY
  Target:     Complementary creators (AI, trading, biz)
  Ask:        Start with peers, build to bigger names
  Outreach:   Personalized DM via acquisition-master
  Format:     30-min focused conversation, one topic

DISTRIBUTION
  → Spotify, Apple Podcasts, YouTube (with video)
  → Clips → Twitter/X threads, Instagram Reels, TikTok
  → Guest cross-promotion (they share to their audience)

HOSTING
  → Buzzsprout or Anchor (free) for distribution
  → Record with Riverside.fm or Zencastr
  → Edit with Descript or outsource
```

---

## ENGINE 3 — AUTHORITY

### Social Proof System

```
PROOF TYPES (ranked by impact)
  1. Revenue screenshots / P&L statements       → hardest proof
  2. Before/after results (yours or clients)    → transformation proof
  3. Testimonials from students or followers    → social proof
  4. Engagement metrics (views, followers)      → reach proof
  5. Media mentions / podcast appearances       → authority proof
  6. Partnership logos                          → credibility proof

PROOF COLLECTION PROCESS
  Weekly:  Screenshot P&L, agent performance metrics, revenue data
  Monthly: Collect 2-3 testimonials from community members
  Ongoing: Screenshot every viral post, media mention, milestone

PROOF STORAGE
  /workspace/brand/proof/
    revenue/      ← monthly P&L screenshots
    testimonials/ ← written + video testimonials
    milestones/   ← follower counts, revenue milestones
    media/        ← podcast appearances, mentions, features

PROOF DEPLOYMENT
  → Pinned posts updated monthly with latest proof
  → Story highlights kept fresh with recent results
  → Funnel landing pages updated with new testimonials
  → Email sequences include proof at decision points
```

### Strategic Networking

```
TIER 1 — MICRO INFLUENCERS (1K-50K followers)
  Target:   Active creators in AI, trading, or biz niche
  Action:   Genuine engagement for 2 weeks before outreach
  Outreach: DM with specific compliment + collaboration idea
  Goal:     Cross-promotion, collab content, introductions

TIER 2 — MID INFLUENCERS (50K-500K followers)
  Target:   Established voices in the niche
  Action:   Quote-tweet, mention, comment value for 30 days
  Outreach: Only after they've noticed you (reply, like)
  Goal:     Podcast guest spot, co-creation, mention

TIER 3 — MACRO INFLUENCERS (500K+)
  Target:   Top 10 voices in each niche
  Action:   Long-term relationship building (3-6 months)
  Outreach: Through warm introductions from Tier 2
  Goal:     One mention = thousands of followers

NETWORKING AUTOMATION
  → acquisition-master handles outreach sequences
  → Track contacts in /workspace/brand/network/contacts.json
  → Weekly review: who to nurture, who to reach out to
```

### Authority Content Calendar

```
WEEK STRUCTURE
  Monday:    Podcast episode drops → clip → share everywhere
  Tuesday:   YouTube tutorial → clips for all platforms
  Wednesday: Deep LinkedIn article → repurpose as thread
  Thursday:  Case study or result reveal (any platform)
  Friday:    Community engagement + week recap
  Saturday:  Behind the scenes or tool review
  Sunday:    Week preview + upcoming content tease

MONTHLY ANCHOR CONTENT
  Week 1:   Revenue/performance update (transparency = trust)
  Week 2:   Tutorial or system breakdown (value = authority)
  Week 3:   Interview or collaboration (reach = growth)
  Week 4:   Opinion piece or prediction (takes = positioning)

QUARTERLY MILESTONES
  → "X months of autonomous revenue" thread/video
  → Annual strategy video (most viewed content type)
  → Community challenge or free workshop
```

---

## Autonomous Brand Operations

### Daily Routine (automated)

```
07h30 — brand-manager.py morning-brief
  → Check: mentions, DMs to reply to, trending topics in niche
  → Generate: 1 Twitter/X post for 08h00
  → Log: engagement metrics from yesterday

12h00 — brand-manager.py midday-push
  → Post scheduled LinkedIn content
  → Reply to top comments on morning post
  → Queue TikTok content for afternoon

19h00 — brand-manager.py evening-review
  → Analyze: best performing content of the day
  → Queue: tomorrow morning post
  → Log: to /workspace/brand/AUDIT.md
  → Notify: principal via Telegram with daily summary
```

### Weekly Routine (automated)

```
Monday 07h00 — Weekly brand audit
  → Performance report: reach, engagement, follower growth
  → Best content of the week → candidate for repurposing
  → Networking queue: who to engage this week
  → Telegram summary to principal

Sunday 21h00 — Weekly content planning
  → Generate next week's content ideas per pillar
  → Cross-platform repurposing map
  → Save to /workspace/brand/content/queue.json
```

### CLI Usage

```bash
# Initialize brand identity
python3 /workspace/brand/scripts/brand_manager.py init

# Morning brief
python3 /workspace/brand/scripts/brand_manager.py morning-brief

# Generate content for a platform
python3 /workspace/brand/scripts/brand_manager.py content \
  --platform twitter \
  --pillar ai-automation \
  --format thread

# Run weekly audit
python3 /workspace/brand/scripts/brand_manager.py audit --period weekly

# Update proof vault
python3 /workspace/brand/scripts/brand_manager.py proof \
  --type revenue \
  --note "March P&L: +€X"

# Network outreach queue
python3 /workspace/brand/scripts/brand_manager.py network --action queue

# Full status
python3 /workspace/brand/scripts/brand_manager.py status
```

---

## Integration with Other Skills

```
content-creator-pro
  → All content generated must align with identity.json pillars
  → Brand voice from /workspace/brand/platforms/voice_guide.md
  → Anti-AI writing patterns applied to all brand content

acquisition-master
  → Uses brand positioning as credibility anchor in outreach
  → "As seen by X followers on [platform]" social proof hook
  → Networking outreach sequences use brand story

funnel-builder
  → Landing pages reference brand identity and proof vault
  → Email sequences reinforce brand positioning
  → High-ticket close uses authority content as trust builder

voice-agent-pro-v3
  → Podcast episodes use cloned voice
  → Video narrations match brand tone from voice_guide.md
  → Call scripts reference brand positioning

agent-shark-mindset
  → Market signals shared on Twitter/X as authority content
  → Trading performance = proof vault entry
  → Weekly signals = pillar 2 content (trading authority)

proof-engine (future)
  → Feeds social proof directly into brand presence
  → Automates testimonial collection and deployment
```

---

## Setup & Bootstrap

### What You Need

```
MINIMUM (brand identity + content strategy):
  → Run brand_manager.py init (no credentials needed)
  → Answer 5 questions about positioning
  → Identity stored in /workspace/brand/identity.json

FOR TWITTER/X AUTOMATION (add):
  TWITTER_API_KEY         → developer.twitter.com
  TWITTER_API_SECRET      → developer.twitter.com
  TWITTER_ACCESS_TOKEN    → developer.twitter.com
  TWITTER_ACCESS_SECRET   → developer.twitter.com

AGENT ALREADY HAS:
  TELEGRAM_BOT_TOKEN  → already in agent .env
  TELEGRAM_CHAT_ID    → already in agent .env
```

### Bootstrap Checklist

```
[ ] python3 brand_manager.py init (creates identity.json)
[ ] Review /workspace/brand/identity.json — adjust positioning
[ ] Review /workspace/brand/platforms/ — customize per platform
[ ] (Optional) Add Twitter API keys for automation
[ ] Set up proof vault: mkdir /workspace/brand/proof/
[ ] Schedule daily crons (see below)
[ ] Verify: python3 brand_manager.py status
```

### Cron Schedule

```
# Daily morning brief — 07h30
30 7 * * 1-5   personal-brand-builder → morning-brief

# Daily evening review — 19h00
0 19 * * 1-5   personal-brand-builder → evening-review

# Weekly brand audit — Monday 07h00
0 7 * * 1      python3 brand_manager.py audit --period weekly

# Weekly content planning — Sunday 21h00
0 21 * * 0     python3 brand_manager.py content --action plan-week
```

---

## Files Written By This Skill

| File | Frequency | Content |
|---|---|---|
| `/workspace/brand/identity.json` | Once + updates | Positioning, pillars, voice |
| `/workspace/brand/platforms/*.json` | Per update | Platform-specific config |
| `/workspace/brand/content/queue.json` | Weekly | Planned content |
| `/workspace/brand/network/contacts.json` | Ongoing | Networking targets |
| `/workspace/brand/proof/` | Weekly | Screenshots, testimonials |
| `/workspace/brand/AUDIT.md` | Daily | Performance log |
| `/workspace/.learnings/LEARNINGS.md` | Weekly | What's working |

---

## Workspace Structure

```
/workspace/brand/
├── identity.json             ← Core brand: positioning, pillars, voice
├── platforms/
│   ├── twitter.json          ← Twitter/X config + schedule
│   ├── linkedin.json         ← LinkedIn config + schedule
│   ├── instagram.json        ← Instagram config + schedule
│   ├── youtube.json          ← YouTube config + schedule
│   ├── tiktok.json           ← TikTok config + schedule
│   ├── podcast.json          ← Podcast config + schedule
│   └── voice_guide.md        ← Brand voice: tone, style, DO/DON'T
├── content/
│   └── queue.json            ← Upcoming content queue
├── network/
│   └── contacts.json         ← Networking targets + status
├── proof/
│   ├── revenue/              ← P&L screenshots + notes
│   ├── testimonials/         ← Written + video testimonials
│   ├── milestones/           ← Follower/revenue milestones
│   └── media/                ← Press, podcasts, mentions
├── references/
│   └── positioning.md        ← Brand positioning guide (this file)
└── AUDIT.md                  ← Daily performance log
```

---

## Constraints

```
❌ Never publish content that contradicts identity.json positioning
❌ Never fabricate testimonials, results, or proof
❌ Never post on behalf of [PRINCIPAL_NAME] without content approval
   (unless principal has enabled autonomous posting mode)
❌ Never engage in controversies or political debates on behalf of brand
✅ Always align content with the 4 brand pillars
✅ Always log every published post to AUDIT.md
✅ Always notify principal via Telegram before autonomous posting
✅ If identity.json missing → run init, notify principal
✅ If proof vault empty → remind principal to add proof monthly
✅ Cross-check with content-creator-pro for anti-AI writing patterns
```

---

## Error Handling

```
ERROR: identity.json missing or empty
  Action: Run brand_manager.py init
  Notify: Telegram → "Brand identity not configured — run init"
  Log: AUDIT.md → "Identity missing [date]"

ERROR: Twitter API rate limit (429)
  Action: Queue post for +1 hour
  Log: ERRORS.md → "Twitter rate limit — post queued [date]"

ERROR: Platform API credentials missing
  Action: Operate in manual mode (generate content, no auto-post)
  Notify: Telegram → "Twitter API not configured — manual mode"

ERROR: Content queue empty
  Action: Generate 3 content ideas from top-performing pillar
  Log: LEARNINGS.md → "Queue empty — auto-generated [date]"
```
