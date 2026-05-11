---
name: proof-engine
description: >
  Transforms every result [PRINCIPAL_NAME] achieves into deployable proof
  across all business domains. Captures P&L, agent performance, funnel
  revenue, testimonials, milestones, and media mentions. Converts raw data
  into compelling stories via the Storytelling Engine. Generates
  proof-based content ready for all platforms. Tracks a multi-channel
  financial dashboard. Scans high-potential business opportunities for
  2026. Deploys proof automatically into funnels, brand, outreach, and
  VSL scripts. The credibility engine that makes everything else convert.
version: 1.1.0
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "💎"
    security_level: L2
    required_paths:
      read:
        - /workspace/proof/
        - /workspace/brand/
        - /workspace/CASHFLOW/
        - /workspace/voice/
        - /workspace/memory/
        - /workspace/revenue/
        - /workspace/content/
        - /workspace/.learnings/
      write:
        - /workspace/proof/vault/
        - /workspace/proof/dashboard.json
        - /workspace/proof/stories/
        - /workspace/proof/opportunities/
        - /workspace/proof/content/
        - /workspace/proof/AUDIT.md
    network_behavior:
      makes_requests: true
      request_targets:
        - https://api.telegram.org (Telegram Bot API — requires TELEGRAM_BOT_TOKEN)
      uses_agent_telegram: true
    requires.env:
      - TELEGRAM_BOT_TOKEN
      - TELEGRAM_CHAT_ID
---

# Proof Engine — Credibility at Scale

> "Nobody believes what you say. Everyone believes what you prove."

This skill turns every result [PRINCIPAL_NAME] achieves — in any business,
on any platform — into automated credibility that feeds every other skill.

```
ENGINE 1 — CAPTURE
  Collects proof from all business domains automatically
  Sources: trading, agents, funnels, content, clients, media

ENGINE 2 — VAULT
  Structured storage with impact scoring
  Multi-channel financial dashboard — all revenue in one view

ENGINE 3 — STORYTELLING
  Transforms raw data into compelling narratives
  Before → Trigger → Result → Mission arcs ready to deploy

ENGINE 4 — CONTENT PROOF
  Generates proof-based content for all platforms
  Real numbers, real results — zero hype

ENGINE 5 — OPPORTUNITY
  Scans high-potential business opportunities for 2026
  Filter: digital, automatable, scalable, high-margin

ENGINE 6 — DEPLOY
  Injects proof at the right moment into every other skill
  Funnels, brand, outreach, VSL, email sequences
```

---

## ENGINE 1 — CAPTURE

### Proof Sources — All Business Domains

```
DOMAIN 1 — TRADING & CRYPTO
  Source:    /workspace/CASHFLOW/ (crypto-executor output)
  Captures:  Monthly P&L, win rate, max drawdown, best trade
  Format:    { domain, date, metric, value, context, impact_score }
  Schedule:  Daily auto-capture at 06h00

DOMAIN 2 — AI AGENTS & AUTOMATION
  Source:    /workspace/ agent logs, AUDIT.md files
  Captures:  Tasks automated, time saved, errors resolved autonomously,
             skills deployed, uptime percentage
  Format:    { domain, date, task, outcome, hours_saved, impact_score }
  Schedule:  Weekly auto-capture Monday 08h00

DOMAIN 3 — FUNNELS & DIGITAL SALES
  Source:    /workspace/CASHFLOW/ funnel revenue data
  Captures:  Revenue per funnel, conversion rates, leads generated,
             best-performing offer, email open rates
  Format:    { domain, date, funnel, revenue, conversions, impact_score }
  Schedule:  Weekly auto-capture Monday 08h00

DOMAIN 4 — CONTENT & AUDIENCE
  Source:    /workspace/brand/AUDIT.md
  Captures:  Follower milestones, viral posts, engagement rates,
             platform growth (Twitter, LinkedIn, Instagram, YouTube, TikTok)
  Format:    { domain, platform, date, metric, value, impact_score }
  Schedule:  Weekly auto-capture

DOMAIN 5 — CLIENTS & TESTIMONIALS
  Source:    Manual entry + /workspace/proof/vault/testimonials/
  Captures:  Written testimonials, video testimonials, client results,
             before/after transformations
  Format:    { domain, date, client, result, quote, impact_score }
  Schedule:  On-demand (manual trigger)

DOMAIN 6 — PRODUCTS & DIGITAL ASSETS
  Source:    Manual entry + revenue data
  Captures:  Product sales, downloads, reviews, refund rate,
             revenue per product
  Format:    { domain, date, product, sales, revenue, reviews }
  Schedule:  Monthly auto-capture

DOMAIN 7 — MEDIA & AUTHORITY
  Source:    Manual entry
  Captures:  Podcast appearances, press mentions, newsletter features,
             speaking invitations, partnership deals
  Format:    { domain, date, source, type, reach, link }
  Schedule:  On-demand (manual trigger)

DOMAIN 8 — PARTNERSHIPS & COLLABS
  Source:    Manual entry
  Captures:  Deals signed, revenue generated, reach amplified,
             affiliate commissions
  Format:    { domain, date, partner, type, outcome, revenue }
  Schedule:  On-demand (manual trigger)
```

### Impact Scoring System

```
IMPACT SCORE (1-10) — determines deployment priority

Score 9-10 : HERO PROOF — deploy everywhere immediately
  Examples: First €10K month, 100K followers, viral post 1M+ views

Score 7-8  : STRONG PROOF — deploy in funnels + brand
  Examples: Consistent €3K/month, testimonial with specific results

Score 5-6  : SUPPORTING PROOF — deploy in content + outreach
  Examples: New tool working well, 10% conversion rate

Score 3-4  : CONTEXT PROOF — use in nurture sequences
  Examples: Learning moment, process improvement, milestone progress

Score 1-2  : ARCHIVE — store but don't deploy actively
  Examples: Small wins, early-stage data
```

### Auto-Capture CLI

```bash
# Capture from all domains
python3 /workspace/proof/scripts/proof_manager.py capture --all

# Capture specific domain
python3 /workspace/proof/scripts/proof_manager.py capture \
  --domain trading

# Manual entry
python3 /workspace/proof/scripts/proof_manager.py add \
  --domain clients \
  --metric testimonial \
  --value "Client went from €0 to €2K/month in 6 weeks" \
  --impact 8
```

---

## ENGINE 2 — VAULT & FINANCIAL DASHBOARD

### Vault Structure

```
/workspace/proof/vault/
├── trading/
│   └── YYYY-MM.json          ← Monthly P&L entries
├── agents/
│   └── YYYY-WW.json          ← Weekly agent performance
├── funnels/
│   └── YYYY-MM.json          ← Monthly funnel revenue
├── content/
│   └── YYYY-MM.json          ← Monthly audience metrics
├── testimonials/
│   └── [client_id].json      ← Individual testimonials
├── products/
│   └── [product_id].json     ← Per-product metrics
├── media/
│   └── YYYY-MM.json          ← Media mentions + appearances
├── partnerships/
│   └── [partner_id].json     ← Partnership outcomes
└── index.json                ← Master index with impact scores
```

### Multi-Channel Financial Dashboard

```
dashboard.json structure:
{
  "period": "2026-03",
  "total_revenue": 0,
  "by_channel": {
    "trading": { "revenue": 0, "trend": "up/down/stable" },
    "funnels": { "revenue": 0, "trend": "" },
    "products": { "revenue": 0, "trend": "" },
    "services": { "revenue": 0, "trend": "" },
    "affiliates": { "revenue": 0, "trend": "" },
    "content_monetization": { "revenue": 0, "trend": "" }
  },
  "top_proof_items": [],
  "hero_proof": null,
  "last_updated": ""
}
```

### Dashboard CLI

```bash
# View current dashboard
python3 /workspace/proof/scripts/proof_manager.py dashboard

# Update a channel
python3 /workspace/proof/scripts/proof_manager.py dashboard \
  --update funnels --revenue 3200

# Monthly summary
python3 /workspace/proof/scripts/proof_manager.py dashboard \
  --period monthly
```

---

## ENGINE 3 — STORYTELLING

### The Proof-to-Story Framework

```
Every proof item can become a story. The story makes the proof human.

ARC 1 — THE TRANSFORMATION ARC
  Before:    "I was [struggling with X]"
  Trigger:   "Then I [built/discovered/tried] Y"
  Result:    "Now I [specific outcome with numbers]"
  Mission:   "That's why I share this — so you can too"

ARC 2 — THE SYSTEM ARC
  Problem:   "Most people do X the hard way"
  System:    "I built a system that [does X automatically]"
  Proof:     "[Specific result] in [timeframe]"
  Offer:     "Here's how to build yours"

ARC 3 — THE MISTAKE ARC
  Mistake:   "I spent €X / wasted X months on [thing]"
  Learning:  "What I discovered was [insight]"
  Fix:       "Now I do [new approach]"
  Result:    "[Better outcome]"

ARC 4 — THE MILESTONE ARC
  Context:   "X months/weeks ago I [starting point]"
  Journey:   "3 things that made the difference:"
  Today:     "[Current milestone with numbers]"
  Next:      "Where this is going"

ARC 5 — THE PROOF ARC (for sales)
  Claim:     "[Bold promise of the offer]"
  Skeptic:   "You might be thinking [objection]"
  Proof:     "[Specific result that addresses objection]"
  Bridge:    "Here's exactly how [client/I] did it"
```

### Story Generation

```bash
# Generate story from a proof item
python3 /workspace/proof/scripts/proof_manager.py story \
  --proof-id trading_2026-03 \
  --arc transformation \
  --platform twitter

# Generate VSL story (for voice-agent-pro-v3)
python3 /workspace/proof/scripts/proof_manager.py story \
  --proof-id funnels_2026-03 \
  --arc system \
  --platform vsl \
  --output /workspace/voice/scripts/vsl_proof.md

# Generate all stories from hero proof items
python3 /workspace/proof/scripts/proof_manager.py story \
  --filter-impact 8 \
  --arc all
```

### Story Output Format

```
Stories saved to /workspace/proof/stories/[arc]_[platform]_[date].md

Each story includes:
  → Raw version (data-first, for personal-brand-builder)
  → Polished version (narrative, for content-creator-pro)
  → Ultra-short version (hook only, for TikTok/Twitter)
  → VSL version (spoken word, for voice-agent-pro-v3)
```

---

## ENGINE 4 — CONTENT PROOF

### Proof-Based Content Generation

```
PRINCIPLE : Every piece of content should be anchored in real proof.
Not "here's how to make money" but "here's how I made €X — step by step"

CONTENT TYPES generated from proof:

THREAD (Twitter/X)
  Hook:    The result (number-first)
  Body:    The 5-7 steps that led to the result
  Proof:   Screenshot reference or specific metric
  Close:   What to do if you want the same

CAROUSEL (Instagram/LinkedIn)
  Slide 1: Bold result claim
  Slides 2-6: The system breakdown
  Slide 7: Before vs After visual
  Slide 8: CTA

REEL SCRIPT (Instagram/TikTok)
  0-3s:   "I [result] in [timeframe] — here's how"
  3-30s:  The 3 key moves
  30-45s: The proof moment
  45-60s: CTA

EMAIL (for funnel sequences)
  Subject: "[Result] — what actually happened"
  Body:    Story arc + proof + lesson + soft CTA

VSL SEGMENT (for voice-agent-pro-v3)
  Opening: The biggest result
  Story:   Full transformation arc
  Proof:   Multiple stacked evidence points
  Offer:   Natural transition to the solution
```

### Content Generation CLI

```bash
# Generate thread from best proof
python3 /workspace/proof/scripts/proof_manager.py content \
  --type thread \
  --domain trading \
  --platform twitter

# Generate carousel from testimonial
python3 /workspace/proof/scripts/proof_manager.py content \
  --type carousel \
  --domain testimonials \
  --platform instagram

# Generate full content batch (all formats, top proof items)
python3 /workspace/proof/scripts/proof_manager.py content \
  --batch \
  --filter-impact 7
```

---

## ENGINE 5 — OPPORTUNITY SCANNER

### High-Potential Business Opportunities 2026

```
FILTER CRITERIA
  ✅ Digital-first (no physical inventory)
  ✅ Automatable with AI agents
  ✅ Scalable without linear time input
  ✅ High margin (> 60%)
  ✅ Proven demand in 2025-2026
  ✅ Achievable with Wesley's current skills stack

OPPORTUNITY CATEGORIES

CAT 1 — AI-POWERED SERVICES (very high potential)
  AI Agent as a Service (AaaS)
    → Build custom OpenClaw agents for businesses
    → €500-5K per setup + €200-500/month maintenance
    → Demand: exploding in 2026
    → Wesley's edge: already does it for himself

  Automated Content Agency
    → content-creator-pro + voice-agent-pro-v3 as a service
    → €1K-3K/month per client for automated content
    → Wesley's edge: full stack already built

  AI Automation Consulting
    → Audit business processes, deploy agents
    → €2K-10K per project
    → Wesley's edge: proven results with his own systems

CAT 2 — DIGITAL PRODUCTS (passive + scalable)
  Trading Signal Newsletter (paid)
    → agent-shark-mindset signals monetized
    → €29-99/month per subscriber
    → 100 subscribers = €3K-10K/month recurring
    → Wesley's edge: real signals, real performance data

  AI Automation Course / Program
    → "Build Your First Agent" or "Autonomous Wealth System"
    → €297-997 one-time or €97/month
    → funnel-builder already set up
    → Wesley's edge: documented real results

  Prompt & Agent Template Marketplace
    → Sell proven OpenClaw skill packages
    → €47-197 per template bundle
    → Wesley's edge: proven skills already built

CAT 3 — COMMUNITY & MEMBERSHIP
  Private Community (Discord/Telegram)
    → "Autonomous Wealth" inner circle
    → €47-97/month per member
    → 50 members = €2.5K-5K/month recurring
    → Content: weekly agent insights + signals + strategies

  Mastermind / Coaching Group
    → High-ticket: €500-2K/month per person
    → 10 members = €5K-20K/month
    → Wesley's edge: real P&L, real systems, proof-first

CAT 4 — AFFILIATE & PARTNERSHIPS
  AI Tools Affiliation
    → OpenClaw, ElevenLabs, Systeme.io, trading platforms
    → 20-40% recurring commission
    → €500-2K/month with audience of 5K+
    → Wesley's edge: authentic user + documented results

  White-Label Agent Solutions
    → License Wesley's agent stack to other operators
    → Revenue share model
    → Wesley's edge: proven infrastructure
```

### Opportunity Scoring

```
Each opportunity scored on:
  Alignment with Wesley's skills (1-10)
  Time to first revenue (1-10, higher = faster)
  Scalability potential (1-10)
  Automation level (1-10)
  Market demand 2026 (1-10)
  → TOTAL SCORE / 50

Top opportunities updated quarterly in:
  /workspace/proof/opportunities/ranked_2026.json
```

### Opportunity CLI

```bash
# View ranked opportunities
python3 /workspace/proof/scripts/proof_manager.py opportunities \
  --action view \
  --filter-score 35

# Add new opportunity
python3 /workspace/proof/scripts/proof_manager.py opportunities \
  --action add \
  --name "AI Agent as a Service" \
  --category ai-services \
  --score 42

# Generate opportunity report
python3 /workspace/proof/scripts/proof_manager.py opportunities \
  --action report
```

---

## ENGINE 6 — DEPLOY

### Proof Injection Points

```
FUNNEL-BUILDER
  → Hero proof → landing page headline
  → Testimonials → social proof section
  → P&L data → credibility block
  → Auto-inject on funnel_builder audit trigger

PERSONAL-BRAND-BUILDER
  → All proof items → /workspace/brand/proof/ sync
  → Hero proof → pinned post candidate
  → Milestone proof → "Month X update" content
  → Auto-sync weekly Sunday 20h00

ACQUISITION-MASTER
  → Testimonials → outreach credibility line
  → Revenue proof → "as someone who [result]..." hook
  → Media mentions → authority signal in cold outreach
  → Auto-inject on outreach sequence generation

VOICE-AGENT-PRO-V3
  → Story arcs → VSL scripts in /workspace/voice/scripts/
  → Hero proof → call script credibility moment
  → Testimonials → social proof in call flow
  → Auto-generate VSL segment weekly

CONTENT-CREATOR-PRO
  → Proof items → content briefs with real data
  → Story arcs → long-form content outlines
  → Milestone proof → monthly update post
  → Auto-brief daily before content generation
```

### Deploy CLI

```bash
# Deploy all hero proof (impact 8+) across all skills
python3 /workspace/proof/scripts/proof_manager.py deploy \
  --filter-impact 8 \
  --targets all

# Deploy to specific skill
python3 /workspace/proof/scripts/proof_manager.py deploy \
  --proof-id testimonials_001 \
  --target funnel-builder

# Weekly full deploy
python3 /workspace/proof/scripts/proof_manager.py deploy \
  --action weekly-sync
```

---

## Autonomous Operations

### Daily Routine

```
06h00 — Auto-capture trading domain
  → Read /workspace/CASHFLOW/TRACKING/tracker_state.json
  → Extract P&L, compute impact score
  → Update dashboard.json
  → If new hero proof (score 8+) → Telegram alert to principal

08h00 — Morning proof brief
  → Summary of proof vault status
  → Top 3 deployable proof items today
  → Telegram: "💎 Proof Brief — [X] items ready to deploy"
```

### Weekly Routine

```
Monday 08h00 — Full capture all domains
  → Agents performance, funnels, content metrics
  → Update dashboard.json with weekly totals
  → Score all new items

Monday 09h00 — Story generation
  → Generate stories from new proof items (score 7+)
  → Save to /workspace/proof/stories/

Sunday 20h00 — Weekly deploy sync
  → Push proof to personal-brand-builder vault
  → Generate VSL segment if new hero proof
  → Brief acquisition-master with latest social proof
  → Telegram: "💎 Weekly Proof Sync — [X] items deployed"
```

### Monthly Routine

```
1st of month 07h00 — Monthly dashboard
  → Consolidate all channels revenue
  → Generate monthly story (transformation arc)
  → Flag new opportunities based on monthly performance
  → Telegram: "📊 Monthly Dashboard — Total: €X across [N] channels"
```

### CLI Usage

```bash
# Full status
python3 /workspace/proof/scripts/proof_manager.py status

# Morning brief
python3 /workspace/proof/scripts/proof_manager.py morning-brief

# Weekly sync (all engines)
python3 /workspace/proof/scripts/proof_manager.py weekly-sync

# View top proof items
python3 /workspace/proof/scripts/proof_manager.py vault \
  --filter-impact 7 \
  --sort date
```

---

## Integration Map

```
proof-engine reads FROM:
  crypto-executor       → /workspace/CASHFLOW/TRACKING/
  agent-shark-mindset   → /workspace/CASHFLOW/ASSETS/
  funnel-builder        → /workspace/CASHFLOW/
  personal-brand-builder → /workspace/brand/AUDIT.md
  revenue-tracker       → /workspace/revenue/

proof-engine writes TO:
  personal-brand-builder → /workspace/brand/proof/
  funnel-builder         → proof items for landing pages
  voice-agent-pro-v3     → /workspace/voice/scripts/ (VSL)
  content-creator-pro    → proof briefs for content
  acquisition-master     → social proof for outreach
```

---

## Setup & Bootstrap

### What You Need

```
MINIMUM (all engines work without API keys):
  → Run proof_manager.py init
  → All engines operate on local files only
  → Telegram for notifications (already in agent .env)

AGENT ALREADY HAS:
  TELEGRAM_BOT_TOKEN  → already in agent .env
  TELEGRAM_CHAT_ID    → already in agent .env
```

### Bootstrap Checklist

```
[ ] python3 proof_manager.py init
[ ] python3 proof_manager.py capture --all (first capture)
[ ] python3 proof_manager.py dashboard (verify dashboard)
[ ] python3 proof_manager.py opportunities --action view
[ ] Add first testimonial manually (if available)
[ ] python3 proof_manager.py status
[ ] Schedule crons (see below)
```

### Cron Schedule

```
# Daily trading capture — 06h00
0 6 * * 1-5    proof-engine → capture --domain trading

# Morning proof brief — 08h00
0 8 * * 1-5    python3 proof_manager.py morning-brief

# Weekly full capture — Monday 08h00
0 8 * * 1      python3 proof_manager.py capture --all

# Weekly story generation — Monday 09h00
0 9 * * 1      python3 proof_manager.py story --filter-impact 7 --arc all

# Weekly deploy sync — Sunday 20h00
0 20 * * 0     python3 proof_manager.py deploy --action weekly-sync

# Monthly dashboard — 1st of month 07h00
0 7 1 * *      python3 proof_manager.py dashboard --period monthly
```

---

## Files Written By This Skill

| File | Frequency | Content |
|---|---|---|
| `/workspace/proof/vault/*/` | Daily/Weekly | Proof items by domain |
| `/workspace/proof/dashboard.json` | Daily | Multi-channel revenue dashboard |
| `/workspace/proof/stories/*.md` | Weekly | Generated story arcs |
| `/workspace/proof/content/*.md` | Weekly | Proof-based content briefs |
| `/workspace/proof/opportunities/ranked_2026.json` | Quarterly | Opportunity rankings |
| `/workspace/proof/AUDIT.md` | Daily | Capture + deploy log |
| `/workspace/.learnings/LEARNINGS.md` | Weekly | What proof converts best |

---

## Workspace Structure

```
/workspace/proof/
├── dashboard.json              ← Multi-channel financial dashboard
├── vault/
│   ├── index.json              ← Master index with impact scores
│   ├── trading/                ← P&L entries
│   ├── agents/                 ← Agent performance
│   ├── funnels/                ← Funnel revenue
│   ├── content/                ← Audience metrics
│   ├── testimonials/           ← Client testimonials
│   ├── products/               ← Product metrics
│   ├── media/                  ← Press, podcasts, mentions
│   └── partnerships/           ← Partnership outcomes
├── stories/                    ← Generated story arcs
├── content/                    ← Proof-based content briefs
├── opportunities/
│   └── ranked_2026.json        ← Scored business opportunities
├── references/
│   └── storytelling.md         ← Storytelling frameworks reference
└── AUDIT.md                    ← Daily log
```

---

## Constraints

```
❌ Never fabricate proof — only real, verifiable data
❌ Never deploy proof with impact score < 5 in hero positions
❌ Never share client testimonials without explicit consent
❌ Never use proof from other people's businesses without permission
✅ Always timestamp every proof item at capture
✅ Always log every deploy action to AUDIT.md
✅ Always notify principal via Telegram when hero proof captured
✅ Cross-check with personal-brand-builder before deploying to brand
✅ If vault empty → prompt principal to add first proof items
```

---

## Error Handling

```
ERROR: /workspace/CASHFLOW/ not found (crypto-executor not running)
  Action: Skip trading capture, log to ERRORS.md
  Notify: "Trading data unavailable — is crypto-executor running?"

ERROR: Vault empty on first run
  Action: Run init, create folder structure, prompt manual entry
  Notify: "Proof vault initialized — add your first proof item"

ERROR: Story generation with no proof items
  Action: Generate template stories with [PLACEHOLDER] data
  Log: "Story generated with placeholders — add real proof"

ERROR: Deploy target skill files not found
  Action: Log which skills are missing, skip gracefully
  Notify: "Deploy skipped for [skill] — skill not installed"
```
