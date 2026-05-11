---
name: afrexai-conversion-copywriting
description: Write high-converting copy for any surface — landing pages, emails, ads, sales pages, product descriptions, CTAs, video scripts, and more. Complete conversion copywriting system with research methodology, 12 proven frameworks, swipe-file templates, scoring rubrics, and A/B testing protocols. Use when you need to write or review any copy meant to drive action.
---

# Conversion Copywriting Engine

> Copy is salesmanship in print. This isn't about writing — it's about selling. Every word earns its place or gets cut.

## Quick Health Check

Rate the copy 1-5 on each dimension. Score < 24 = rewrite needed:

| # | Dimension | Question |
|---|-----------|----------|
| 1 | Clarity | Can a 12-year-old understand the offer in 5 seconds? |
| 2 | Specificity | Are there numbers, timeframes, and concrete outcomes? |
| 3 | Desire | Does the reader WANT the outcome described? |
| 4 | Proof | Is there evidence (testimonials, data, logos, case studies)? |
| 5 | Urgency | Is there a reason to act NOW vs later? |
| 6 | Friction | Are objections addressed before they arise? |
| 7 | Voice | Does it sound like a human, not a corporation? |
| 8 | CTA | Is the next step crystal clear and low-risk? |

**Score: /40** — Below 32 = significant opportunity. Below 24 = copy is actively losing money.

---

## Phase 1: Research Before Writing

Never write a single word until you complete this. Bad research = bad copy, no matter how clever.

### 1.1 Voice of Customer (VoC) Mining

The goal: steal your customer's EXACT words and mirror them back.

**Sources (ranked by value):**

| Source | What to Extract | Where to Find |
|--------|----------------|---------------|
| Support tickets | Pain language, frustration words | Helpdesk, Intercom, Zendesk |
| Sales call recordings | Objections, "I wish...", buying triggers | Gong, call notes |
| Review sites | Praise patterns, complaint patterns | G2, Capterra, Trustpilot, Amazon |
| Reddit/forums | Unfiltered problems, slang, emotional language | r/[industry], Quora, niche forums |
| Competitor reviews | What competitors fail at (your opportunity) | G2, App Store, Amazon |
| Survey responses | Direct answers to "why did you buy/not buy?" | Typeform, post-purchase surveys |
| Social comments | Reaction language, share triggers | Twitter replies, LinkedIn comments |

**VoC Extraction Template:**

```yaml
voC_research:
  product: "[Product name]"
  date: "YYYY-MM-DD"
  
  pain_statements:  # Exact quotes about the problem
    - quote: "I spend 3 hours every morning just reconciling invoices"
      source: "G2 review - AccountingSoft competitor"
      frequency: "high"  # How often this sentiment appears
    - quote: ""
      source: ""
      frequency: ""
  
  desire_statements:  # What they WANT (outcome language)
    - quote: "I just want to click one button and have it done"
      source: "Reddit r/smallbusiness"
      frequency: "medium"
    - quote: ""
      source: ""
      frequency: ""
  
  objection_statements:  # Why they hesitate
    - quote: "Every tool like this requires a PhD to set up"
      source: "Support ticket"
      frequency: "high"
    - quote: ""
      source: ""
      frequency: ""
  
  trigger_events:  # What made them start looking
    - "Hired 5th employee and spreadsheets broke"
    - "Missed a tax deadline"
    - ""
  
  words_they_use:  # Industry/audience vocabulary
    - "reconciliation" not "financial harmonization"
    - "setup" not "onboarding flow"
    - ""
  
  competitors_they_mention: []
  
  buying_criteria:  # What matters most (ranked)
    - "Easy to set up (< 1 hour)"
    - "Integrates with QuickBooks"
    - ""
```

### 1.2 Awareness Levels (Eugene Schwartz)

Every piece of copy must match the reader's awareness level. Writing "Buy now!" to someone who doesn't know they have a problem = wasted words.

| Level | They Know... | Your Job | Lead With |
|-------|-------------|----------|-----------|
| **Unaware** | Nothing about the problem | Educate about the pain | Story, shocking stat, question |
| **Problem-Aware** | They have a problem | Agitate the pain, introduce solution category | "Tired of X? Here's why..." |
| **Solution-Aware** | Solutions exist | Differentiate YOUR solution | "Unlike other tools, we..." |
| **Product-Aware** | Your product exists | Overcome objections, prove value | Social proof, comparison, demo |
| **Most Aware** | Your product, ready to buy | Remove final friction | Deal, guarantee, urgency |

**Rule:** The less aware they are, the longer the copy needs to be. Unaware = long-form education. Most Aware = short CTA + offer.

### 1.3 One Reader, One Offer, One Action

Before writing, fill this in:

```yaml
copy_brief:
  surface: ""  # Landing page, email, ad, sales page, etc.
  one_reader: ""  # Specific person (not "small businesses" — "Sarah, ops manager at 50-person agency")
  awareness_level: ""  # Unaware / Problem / Solution / Product / Most Aware
  one_offer: ""  # What exactly are you offering?
  one_action: ""  # What exactly should they DO?
  primary_emotion: ""  # Fear, desire, curiosity, frustration, hope
  proof_available: []  # Testimonials, case studies, data points you can use
  objections_to_address: []  # Top 3 reasons they'd say no
  word_count_target: ""  # Constraint forces clarity
```

---

## Phase 2: Headline Writing

The headline does 80% of the work. If the headline fails, nothing else matters.

### 2.1 Headline Formulas (12 Proven Patterns)

| # | Formula | Example |
|---|---------|---------|
| 1 | **[Number] Ways to [Desired Outcome] Without [Pain]** | "7 Ways to Cut Hiring Time Without Lowering Standards" |
| 2 | **How [Specific Person] [Achieved Result] in [Timeframe]** | "How a 3-Person Agency Landed $240K in Clients in 90 Days" |
| 3 | **Stop [Bad Thing]. Start [Good Thing].** | "Stop Guessing at Pricing. Start Charging What You're Worth." |
| 4 | **The [Adjective] Way to [Outcome]** | "The Lazy Way to Write Emails That Get Replies" |
| 5 | **[Outcome] in [Timeframe] — or [Bold Guarantee]** | "Double Your Pipeline in 30 Days — or We Work Free Until You Do" |
| 6 | **Why [Counterintuitive Claim]** | "Why Your Best Salesperson Is Costing You Revenue" |
| 7 | **[Pain Statement] → [Outcome Statement]** | "From 60-Hour Weeks → Automated Operations in 14 Days" |
| 8 | **What [Respected Group] Knows About [Topic] That You Don't** | "What Top 1% of SaaS Founders Know About Pricing" |
| 9 | **Are You Making These [Number] [Mistake Type] Mistakes?** | "Are You Making These 5 Cold Email Mistakes?" |
| 10 | **[Big Number/Stat] + Implication** | "83% of Proposals Lose on Price. Here's How to Win on Value." |
| 11 | **The [Framework/Secret/Method] Behind [Impressive Result]** | "The 3-Step Method Behind $50M in Closed Deals" |
| 12 | **[Direct Command] + [Specific Benefit]** | "Cut Your Client Reporting Time by 80% This Week" |

### 2.2 Headline Quality Test

Score each headline candidate 0-2 per criterion:

| Criterion | 0 | 1 | 2 |
|-----------|---|---|---|
| **Specific** | Vague/generic | Somewhat specific | Has numbers, timeframes, or concrete nouns |
| **Benefit-driven** | Feature-focused | Implied benefit | Explicit outcome the reader wants |
| **Curiosity gap** | No reason to read on | Mild interest | "I NEED to know more" |
| **Believable** | Sounds like hype | Plausible | Backed by specificity or proof |
| **Emotional** | Flat/corporate | Slightly engaging | Hits fear, desire, curiosity, or frustration |

**Score: /10** — Ship at 7+. Below 5 = rewrite.

### 2.3 Subheadline Rules

The subheadline expands on the headline promise. It should:
- Add specificity the headline couldn't fit
- Address the reader directly ("you")
- Lower the perceived effort/risk
- Create a "nodding" effect (reader thinks "yes, that's me")

**Pattern:** `[Expand on headline promise] + [For whom] + [Without the main objection]`

Example: Headline: "Double Your Pipeline in 30 Days"  
Subheadline: "The AI-powered outreach system that books qualified calls for B2B founders — without cold calling or hiring SDRs."

---

## Phase 3: Copy Frameworks (The Arsenal)

### 3.1 Core Frameworks

**AIDA — Attention, Interest, Desire, Action**
Best for: Landing pages, sales pages, long-form emails

```
ATTENTION: Hook with the biggest pain or boldest promise
INTEREST: "Here's why this matters to YOU specifically..."
DESIRE: Paint the after-state. Make them feel the transformation.
ACTION: Single, clear, low-risk next step.
```

**PAS — Problem, Agitate, Solution**
Best for: Short emails, ads, social posts, pain-driven products

```
PROBLEM: State the problem in their words (from VoC research)
AGITATE: What happens if they don't solve it? Cost of inaction.
SOLUTION: Your product/offer as the bridge from pain to relief.
```

**BAB — Before, After, Bridge**
Best for: Case studies, testimonials, transformation stories

```
BEFORE: Paint their current painful reality (specific details)
AFTER: Paint the future they want (specific results)
BRIDGE: Your product is the bridge between the two.
```

**PASTOR — Problem, Amplify, Story, Transformation, Offer, Response**
Best for: Long-form sales pages, webinar scripts

```
PROBLEM: Identify the core pain
AMPLIFY: Consequences of not solving (emotional + financial)
STORY: Tell a relevant story (yours, a customer's, or a parable)
TRANSFORMATION: Show before → after with proof
OFFER: Present the solution with everything included
RESPONSE: Clear CTA with urgency
```

**4Ps — Promise, Picture, Proof, Push**
Best for: Ads, product pages, short landing pages

```
PROMISE: What will the reader get? (Specific outcome)
PICTURE: Help them visualize having it (sensory language)
PROOF: Evidence it works (testimonials, data, case studies)
PUSH: CTA with urgency or scarcity
```

**Star-Story-Solution**
Best for: Email sequences, personality-driven brands

```
STAR: Introduce the character (your customer or you)
STORY: The struggle and the journey
SOLUTION: How the product solved the problem
```

### 3.2 Framework Selection Guide

| Situation | Best Framework | Why |
|-----------|---------------|-----|
| Cold audience, long page | PASTOR | Needs full education arc |
| Warm audience, quick action | PAS | They know the pain, move fast |
| Case study / testimonial | BAB | Transformation is the proof |
| Product launch | AIDA | Classic structure, works everywhere |
| Ad copy (< 100 words) | 4Ps | Compact but complete |
| Email nurture sequence | Star-Story-Solution | Builds relationship through narrative |
| Retargeting / remarketing | PAS (short) | They already know you, agitate to return |

---

## Phase 4: Surface-Specific Templates

### 4.1 Landing Page Structure

```
[HERO SECTION]
├── Headline (formula from Phase 2)
├── Subheadline (expand + specify + de-risk)
├── Hero image or demo GIF
├── Primary CTA button
└── Social proof bar (logos, "Trusted by X companies", star rating)

[PROBLEM SECTION]
├── "Sound familiar?" or "You're here because..."
├── 3-4 pain bullets (from VoC, in their words)
└── Cost of inaction statement

[SOLUTION SECTION]
├── "Here's how [Product] fixes this"
├── 3 key benefits (NOT features) with icons
├── Each benefit: [Benefit headline] + [1-2 sentence expansion] + [Proof point]
└── Screenshot or visual

[SOCIAL PROOF SECTION]
├── 2-3 testimonials (name, company, result, photo)
├── OR case study snippet (Before → After with numbers)
└── Trust badges (security, integrations, awards)

[OBJECTION HANDLING SECTION]
├── FAQ or "Common questions" (address top 3-5 objections)
└── Each answer is a mini-sale (reframe objection → benefit)

[FINAL CTA SECTION]
├── Restate the core promise
├── Risk reversal (guarantee, free trial, no CC required)
├── CTA button (same as hero)
└── Urgency element if genuine (limited spots, price going up, deadline)
```

### 4.2 Email Copy Templates

**Cold Email (first touch):**
```
Subject: [Specific observation about their business]

[First name],

[Observation about their company — proves you did research, 1 sentence]

[Problem you solve — framed as "companies like yours" + specific pain, 1-2 sentences]

[Result you've delivered — specific number/outcome, 1 sentence]

[Soft CTA — question or offer, not "let me know if you want to chat"]

[Name]

P.S. [Proof point or curiosity hook]
```

**Welcome Email (post-signup):**
```
Subject: You're in — here's your [thing] + what to do first

[First name],

Welcome to [Product]. You just made a smart move.

Here's your [thing they signed up for]:
→ [Link or attachment]

**Your next step (takes 2 minutes):**
[Single specific action that gets them to first value]

If you hit any snags, reply to this email — I read every one.

[Name]
[Title] at [Company]
```

**Abandoned Cart / Trial Expiring:**
```
Subject: Still thinking it over?

[First name],

You [started a trial / added X to cart] [timeframe] ago but didn't [complete / continue].

Totally fine — here's what you might be wondering:

**"Is it worth the price?"**
[1-2 sentences with proof point / ROI calculation]

**"What if it doesn't work for me?"**
[Risk reversal — guarantee, refund policy, support]

**"I don't have time right now"**
[Time-to-value statement — "takes 10 minutes to set up"]

[CTA — "Pick up where you left off →"]

[Name]
```

### 4.3 Ad Copy Templates

**Facebook/Instagram Ad:**
```
[Hook — first line must stop the scroll, max 125 chars]
↓
[Problem — 1-2 lines, relatable pain]
↓
[Solution — what your product does differently, 1-2 lines]
↓
[Proof — number, testimonial snippet, or social proof]
↓
[CTA — "Click [Link] to [specific outcome]"]
```

**Google Search Ad:**
```
Headline 1: [Primary keyword + benefit] (30 chars)
Headline 2: [Proof/number + differentiator] (30 chars)
Headline 3: [CTA or offer] (30 chars)
Description: [Expand on benefit] + [Address objection] + [CTA] (90 chars)
```

**LinkedIn Ad:**
```
[Pattern interrupt — stat, question, or contrarian take]

[2-3 lines expanding on the problem — professional tone, specific to role]

[What we built / discovered / proved — 1-2 lines]

[CTA with specific value exchange — "Download the playbook" not "Learn more"]
```

### 4.4 Sales Page (Long-Form)

```
1. HEADLINE — Biggest promise or transformation
2. SUBHEADLINE — For whom + timeframe + de-risk
3. OPENING STORY — Paint the painful "before" state (2-3 paragraphs)
4. AGITATION — Cost of staying stuck (emotional + financial)
5. INTRODUCTION — "There's a better way" (introduce your solution concept)
6. WHAT'S INCLUDED — Bullet list of everything, each bullet = mini benefit
7. BONUSES — Additional value stacked on top
8. SOCIAL PROOF — 3-5 testimonials with results
9. PRICE REVEAL — Anchor high first, then show actual price
10. GUARANTEE — Risk reversal (money-back, satisfaction, results-based)
11. FAQ — Overcome remaining objections
12. FINAL CTA — Urgency + restate the transformation
13. P.S. — Restate the best benefit + guarantee (many people skip to P.S.)
```

### 4.5 Product Description

```
[One-line benefit headline — what it DOES for the buyer]

[2-3 sentences: who it's for, what problem it solves, key differentiator]

Key features:
• [Feature] — [Why it matters to the buyer]
• [Feature] — [Why it matters to the buyer]
• [Feature] — [Why it matters to the buyer]

[Social proof snippet — "Used by X", review quote, or stat]

[CTA]
```

### 4.6 Video Script (VSL / Demo)

```
[0:00-0:10] HOOK — Bold claim or question that creates curiosity gap
[0:10-0:45] PROBLEM — Paint the pain (specific, relatable scenario)
[0:45-1:30] AGITATE — What happens if they don't solve it (costs, risks)
[1:30-3:00] SOLUTION — Introduce your product, show it working
[3:00-4:00] PROOF — Results, testimonials, before/after
[4:00-4:30] OFFER — What they get, what it costs, guarantee
[4:30-5:00] CTA — Tell them exactly what to do next
```

---

## Phase 5: Persuasion Techniques

### 5.1 Power Words by Emotion

| Emotion | Words That Trigger It |
|---------|----------------------|
| **Urgency** | Now, today, deadline, before, expires, limited, last chance, final |
| **Curiosity** | Secret, hidden, little-known, discover, revealed, behind-the-scenes |
| **Fear** | Mistake, avoid, warning, risk, lose, miss, fail, never |
| **Desire** | Imagine, transform, unlock, achieve, breakthrough, freedom |
| **Trust** | Proven, guaranteed, tested, backed, certified, research-backed |
| **Exclusivity** | Exclusive, invitation-only, limited, handpicked, insider |
| **Simplicity** | Easy, simple, quick, effortless, done-for-you, turnkey, one-click |

### 5.2 Objection Handling in Copy

Every piece of copy must preemptively address objections. The top 5 universal objections:

| Objection | How to Handle It in Copy |
|-----------|-------------------------|
| **"Too expensive"** | Anchor to higher price first, show ROI, cost of NOT buying, payment plans |
| **"I don't have time"** | State time-to-value ("set up in 10 minutes"), show automation |
| **"I don't trust you"** | Social proof, guarantee, "cancel anytime", transparent pricing |
| **"I don't need it now"** | Cost of delay, urgency (genuine), "every day you wait = $X lost" |
| **"It won't work for me"** | Case studies from THEIR industry/role, guarantee, personalization |

### 5.3 Social Proof Hierarchy

Not all proof is equal. Use the highest-tier proof available:

| Tier | Type | Example | Power |
|------|------|---------|-------|
| 1 | Named result + photo | "Sarah at Acme grew revenue 40% in 90 days" [photo] | ★★★★★ |
| 2 | Specific metric | "Clients average 3.2x ROI in the first quarter" | ★★★★ |
| 3 | Volume proof | "Used by 2,400+ companies" | ★★★ |
| 4 | Logo bar | [Company logos] | ★★★ |
| 5 | Star ratings | "4.8/5 on G2 (200+ reviews)" | ★★ |
| 6 | Generic testimonial | "Great product, highly recommend!" | ★ |

**Rule:** Always aim for Tier 1-2. If you only have Tier 5-6, go get better proof before writing more copy.

### 5.4 CTA Writing Rules

| Rule | Bad | Good |
|------|-----|------|
| Be specific about what happens | "Submit" | "Get My Free Report" |
| Use first person | "Start your trial" | "Start my free trial" |
| Reduce perceived risk | "Buy now" | "Try it free for 14 days" |
| Show value, not action | "Sign up" | "Start saving 10 hours/week" |
| Add urgency if genuine | "Learn more" | "Claim your spot (12 left)" |
| One CTA per section | 3 different buttons | Same CTA repeated |

### 5.5 Price Anchoring

Always anchor before revealing price:

```
Pattern 1 — Value Stack:
"You'd normally pay $500/hr for a consultant to do this.
 You could hire a full-time person for $80K/year.
 Or you can get [Product] for $47/month."

Pattern 2 — Cost of Problem:
"The average company loses $23K/year to [problem].
 [Product] costs $97/month. That's a 19x return."

Pattern 3 — Competitor Anchor:
"[Competitor] charges $299/month for half the features.
 [Product] gives you everything for $97/month."
```

---

## Phase 6: Editing & Scoring

### 6.1 The Editing Checklist (run on every piece)

**Clarity Pass:**
- [ ] Remove every word that doesn't earn its place
- [ ] Replace jargon with plain language
- [ ] One idea per sentence. One point per paragraph.
- [ ] Read it aloud. If you stumble, rewrite.

**Specificity Pass:**
- [ ] Replace "many" with actual numbers
- [ ] Replace "quickly" with actual timeframes
- [ ] Replace "improve" with actual outcomes
- [ ] Replace "leading" with actual rankings or proof

**Engagement Pass:**
- [ ] First sentence hooks (would YOU keep reading?)
- [ ] Vary sentence length. Short. Then a longer one that builds. Then short again.
- [ ] Use "you" more than "we" (3:1 ratio minimum)
- [ ] Break up walls of text (no paragraph > 3 lines on mobile)

**Conversion Pass:**
- [ ] CTA is above the fold AND repeated
- [ ] Every section ends with a reason to keep reading or a CTA
- [ ] Objections are addressed BEFORE the CTA
- [ ] Guarantee or risk reversal is prominent

**Trust Pass:**
- [ ] No hype words without proof backing them up
- [ ] Testimonials have names, companies, and specific results
- [ ] Claims are believable (extraordinary claims need extraordinary proof)
- [ ] No AI-speak: cut "leverage", "streamline", "seamlessly", "I'd be happy to"

### 6.2 Copy Scoring Rubric (0-100)

| Dimension | Weight | 0-2 (Weak) | 3-4 (Average) | 5 (Strong) |
|-----------|--------|------------|----------------|------------|
| **Headline** | x4 | Generic, no hook | Has a benefit, somewhat specific | Specific, emotional, curiosity gap |
| **Clarity** | x3 | Confusing, jargon-heavy | Generally clear, some filler | Crystal clear, concise, scannable |
| **Persuasion** | x3 | Lists features only | Some benefits mentioned | Full desire arc with proof |
| **Proof** | x3 | No social proof | Generic testimonials | Named results, specific metrics |
| **CTA** | x3 | Missing or weak | Present but generic | Specific, low-risk, urgent |
| **Voice** | x2 | Corporate/robotic | Acceptable | Sounds like a human who cares |
| **Objection Handling** | x2 | None | FAQ section exists | Woven throughout the copy |

**Score = Sum of (rating × weight).** Max = 100.

| Score | Grade | Action |
|-------|-------|--------|
| 85-100 | A | Ship it |
| 70-84 | B | Minor tweaks, then ship |
| 55-69 | C | Significant rewrite needed |
| 40-54 | D | Fundamental structure problems |
| 0-39 | F | Start over with research |

---

## Phase 7: A/B Testing Protocol

### 7.1 What to Test (Impact Order)

Test the highest-impact element first:

| Priority | Element | Typical Lift |
|----------|---------|-------------|
| 1 | Headline | 20-100%+ |
| 2 | CTA text + placement | 10-40% |
| 3 | Social proof type/placement | 10-30% |
| 4 | Price anchoring | 10-50% |
| 5 | Page length (long vs short) | 5-30% |
| 6 | Image/video | 5-20% |
| 7 | Color/design | 2-10% |

### 7.2 Test Design

```yaml
ab_test:
  element: "Headline"
  hypothesis: "Pain-focused headline will convert better than benefit-focused"
  control: "Automate Your Client Reporting in Minutes"
  variant: "Tired of Spending 10 Hours on Reports Nobody Reads?"
  metric: "click-through rate to pricing page"
  traffic_split: "50/50"
  minimum_sample: 500  # per variant for statistical significance
  duration: "2 weeks or until significance reached"
  confidence_threshold: "95%"
```

### 7.3 Statistical Significance Rules

- **Minimum 100 conversions** per variant before reading results
- **95% confidence** minimum to declare a winner
- **Don't peek** — set the duration and wait. Early stopping = false positives
- **Test one variable** at a time (headline A vs B, not headline A + CTA A vs headline B + CTA B)
- **Document everything** — what you tested, what won, by how much, what you learned

---

## Phase 8: Industry-Specific Copy Angles

### 8.1 B2B SaaS
- Lead with time saved or revenue gained (quantified)
- Speak to the buyer's BOSS (they need to justify the purchase)
- Integration and security are objections, not features (address them, don't lead with them)
- Free trial or freemium = expected. If no free tier, need stronger proof.

### 8.2 Professional Services (Consulting, Agencies)
- Lead with results from similar clients (specificity wins)
- Authority positioning > feature lists
- Case studies are your #1 asset
- Price = value-based, never hourly (frame accordingly)

### 8.3 E-commerce / DTC
- Lead with the transformation, not the product
- Social proof = user photos, reviews, influencer endorsements
- Urgency must be genuine (fake scarcity = brand damage)
- Mobile-first — above-the-fold must convert on a phone

### 8.4 Healthcare / Legal
- Compliance language is mandatory but doesn't have to be boring
- Trust and credentials > bold claims
- Education-first approach (content marketing → conversion)
- Risk reversal = critical (consequences of bad choice are high)

### 8.5 Financial Services
- Regulatory disclaimers are non-negotiable
- Lead with pain of current situation + cost of inaction
- Social proof from peers in similar situations
- Simplify complexity — if they need a glossary, you've lost them

---

## Phase 9: Swipe File — Ready-to-Use Copy Blocks

### 9.1 Guarantee Templates

```
30-Day Money-Back:
"Try [Product] for 30 days. If it doesn't [specific outcome], 
email us and we'll refund every penny. No questions, no hassle."

Results-Based:
"If you don't see [specific measurable result] within [timeframe], 
we'll work with you for free until you do — or refund in full."

Risk Reversal:
"You risk nothing. We risk everything. That's how confident we are 
that [Product] will [outcome]."
```

### 9.2 Urgency Templates (Genuine Only)

```
Scarcity (real):
"We onboard 5 new clients per month to maintain quality. 
[X] spots left for [Month]."

Deadline (real):
"This pricing expires [Date] when we launch v2.0. 
Lock in the current rate now."

Cost of Delay:
"Every week without [solution], you're losing roughly [$ amount]. 
That's [$X * weeks until decision] by the time you decide."
```

### 9.3 Transition Phrases

Use these to maintain momentum between sections:

```
Problem → Solution:  "Here's the thing..."  |  "But it doesn't have to be this way."
Proof → CTA:         "Ready to see the same results?"  |  "Your turn."
Feature → Benefit:   "Which means..."  |  "In plain English:"  |  "Translation:"
Section → Section:   "But that's not all."  |  "It gets better."  |  "Here's where it gets interesting."
```

### 9.4 Opening Lines That Hook

```
Stat hook:      "83% of proposals lose on price. Yours doesn't have to."
Question hook:  "What if your biggest competitor's weakness was your biggest opportunity?"
Story hook:     "Last Tuesday, a 3-person agency closed a $240K deal. Here's exactly how."
Contrarian:     "Most advice about [topic] is wrong. Here's what actually works."
Pain hook:      "You know that sinking feeling when [specific pain moment]?"
```

---

## Phase 10: Anti-Patterns (Copy Killers)

| Anti-Pattern | Why It Kills | Fix |
|-------------|-------------|-----|
| Starting with "We are..." | Nobody cares about you. They care about themselves. | Start with the reader's problem or desired outcome |
| Feature dumping | Features don't sell. Benefits sell. | Every feature → "which means [benefit for reader]" |
| Weak CTA ("Learn more") | Doesn't tell them what they GET | "[Verb] + [Specific value]" — "Get My Free Playbook" |
| Wall of text | Nobody reads dense paragraphs on screens | Max 3 lines per paragraph. Use bullets, bold, whitespace |
| Fake urgency | Erodes trust when they see the "deadline" pass | Only use genuine scarcity/deadlines. Preferably cost-of-delay instead |
| No social proof | Claims without evidence = marketing fluff | Add proof or lower the claim to what you can prove |
| Multiple CTAs | Confused readers don't convert | One CTA per page (can repeat, but always the SAME action) |
| AI-speak | "Leverage", "streamline", "empower", "I'd be happy to" | Sound like a human. Read it aloud. Would a person say this? |
| Being clever over clear | Puns and wordplay sacrifice clarity | If they have to think about your headline, you lost |
| Ignoring mobile | 60%+ of readers are on phones | Short sentences, ample whitespace, thumb-friendly CTA buttons |

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Write a landing page for [product]" | Full landing page copy using Phase 4.1 structure |
| "Write a cold email to [person/company]" | Cold email using Phase 4.2 template |
| "Score this copy" | Run Phases 1 health check + Phase 6.2 rubric |
| "Write headlines for [offer]" | Generate 10+ headlines using Phase 2.1 formulas |
| "Write a sales page for [product]" | Long-form sales page using Phase 4.4 |
| "Write ad copy for [platform]" | Platform-specific ad using Phase 4.3 templates |
| "Write a product description for [product]" | Phase 4.5 template |
| "Write an email sequence for [goal]" | Multi-email sequence with Phase 4.2 templates |
| "Rewrite this copy to convert better" | Edit using Phase 6.1 checklist + fix anti-patterns |
| "Run VoC research for [product/market]" | Phase 1.1 research using web search |
| "Write a video script for [product]" | Phase 4.6 VSL template |
| "A/B test plan for [page/email]" | Phase 7 test design |
