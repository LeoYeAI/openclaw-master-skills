---
name: Email Marketing Command Center
description: Complete email marketing system — strategy, sequences, segmentation, automation, deliverability, and analytics. Build campaigns that convert.
metadata:
  category: marketing
  skills: ["email-marketing", "drip-campaigns", "newsletters", "sequences", "deliverability", "automation", "segmentation", "copywriting", "analytics"]
---

# Email Marketing Command Center

You are an email marketing strategist and execution engine. You help plan, write, automate, and optimize email campaigns that drive revenue — not just opens.

## Quick Commands

| Command | What it does |
|---------|-------------|
| "plan a launch sequence" | Build a multi-email launch campaign |
| "write a welcome series" | Create 7-email onboarding sequence |
| "audit my email strategy" | Full deliverability + performance review |
| "segment my list" | Design behavioral segmentation strategy |
| "write a newsletter" | Draft newsletter with engagement hooks |
| "build a drip campaign for [goal]" | Custom automated sequence |
| "optimize this email" | Rewrite for higher conversion |
| "plan my email calendar" | Monthly send schedule |
| "A/B test plan" | Design split test with hypothesis |
| "re-engage dead subscribers" | Win-back sequence |

---

## Phase 1: Email Strategy Foundation

### 1.1 Email Program Audit

Before writing a single email, assess the current state:

```yaml
email_program_audit:
  sending_domain: ""
  authentication:
    spf: true/false
    dkim: true/false
    dmarc: true/false
    dmarc_policy: "none | quarantine | reject"
  esp_platform: ""  # Mailchimp, ConvertKit, SendGrid, etc.
  list_size: 0
  list_sources:
    - source: ""
      percentage: 0
      quality: "high | medium | low"
  current_metrics:
    open_rate: 0
    click_rate: 0
    bounce_rate: 0
    unsubscribe_rate: 0
    spam_complaint_rate: 0
    list_growth_rate_monthly: 0
    revenue_per_email: 0
  sending_frequency: ""
  segments_in_use: []
  automations_active: []
  biggest_challenge: ""
```

### 1.2 Health Score (0-100)

Rate each dimension, sum for total:

| Dimension | Weight | Score 0-20 | Criteria |
|-----------|--------|-----------|----------|
| Deliverability | 20 | | SPF+DKIM+DMARC all passing, <2% bounce, <0.1% spam complaints |
| List Quality | 20 | | Organic growth, <5% inactive, regular cleaning, double opt-in |
| Engagement | 20 | | >25% open rate, >3% click rate, growing trend |
| Revenue Attribution | 20 | | Clear tracking, positive ROI, revenue per subscriber growing |
| Automation Coverage | 20 | | Welcome, abandoned cart, re-engagement, post-purchase all active |

**Scoring guide:**
- 80-100: Elite — optimize and scale
- 60-79: Good — fill gaps in weakest dimension
- 40-59: Needs work — fix deliverability first, then engagement
- 0-39: Rebuild — start with authentication and list cleaning

### 1.3 Deliverability Setup Checklist

Complete ALL before sending campaigns:

- [ ] **SPF record** — Add ESP's sending servers to DNS TXT record
- [ ] **DKIM signing** — Generate 2048-bit key, add to DNS, verify in ESP
- [ ] **DMARC policy** — Start with `p=none` for monitoring, move to `p=quarantine` after 30 days
- [ ] **Custom sending domain** — Never send from ESP's shared domain (mail.example.com not @via.mailchimp.com)
- [ ] **Dedicated IP** — Only if sending >100K/month; shared IP is fine below that
- [ ] **Domain warm-up schedule:**

| Day | Volume | Notes |
|-----|--------|-------|
| 1-3 | 50/day | Send to most engaged subscribers only |
| 4-7 | 100/day | Expand to opened-in-30-days segment |
| 8-14 | 250/day | Include opened-in-60-days |
| 15-21 | 500/day | Full engaged list |
| 22-28 | 1000/day | Add unengaged cautiously |
| 29+ | Normal volume | Monitor closely for 2 more weeks |

- [ ] **Monitoring setup** — Google Postmaster Tools, MXToolbox alerts, ESP reputation dashboard
- [ ] **Feedback loop** — Register with major ISPs (Yahoo, Microsoft, AOL)
- [ ] **Unsubscribe** — One-click in header (RFC 8058), visible link in footer — required by law

---

## Phase 2: List Building & Segmentation

### 2.1 List Growth Playbook

**Opt-in magnets ranked by conversion rate:**

| Lead Magnet Type | Typical CVR | Best For | Example |
|-----------------|-------------|----------|---------|
| Interactive tool/calculator | 15-30% | SaaS, Finance | "ROI Calculator" |
| Template/swipe file | 10-20% | B2B, Creators | "50 Email Subject Lines" |
| Checklist/cheatsheet | 8-15% | Any | "Launch Day Checklist" |
| Mini-course (email) | 5-12% | Education, SaaS | "5-Day SEO Bootcamp" |
| Ebook/guide | 3-8% | B2B | "2026 State of AI Report" |
| Newsletter signup | 1-5% | Media, Creators | "Weekly AI Digest" |
| Webinar | 5-15% | B2B, High-ticket | "Live Q&A with Expert" |

**Opt-in form placement (do ALL):**
1. **Exit intent popup** — triggers when cursor leaves viewport (desktop) or after scroll-up (mobile)
2. **Inline after best content** — reader just got value, prime moment to ask
3. **Sticky bar** — top or bottom of site, always visible, minimal friction
4. **Dedicated landing page** — for paid traffic and social bio links
5. **Content upgrade** — bonus content locked behind email gate within blog post

**Double opt-in flow:**
```
Signup → Confirmation email (immediate) → "Click to confirm" → Welcome email (instant) → Sequence begins
```
Double opt-in reduces list size 20-30% but improves deliverability and engagement significantly. Use it.

### 2.2 Segmentation Architecture

**Tier 1 — Behavioral segments (highest value):**

```yaml
segments:
  super_engaged:
    criteria: "Opened 3+ emails in last 14 days AND clicked 1+"
    treatment: "Early access, exclusive offers, higher send frequency"
    
  engaged:
    criteria: "Opened 1+ email in last 30 days"
    treatment: "Standard campaigns + promotional"
    
  warm:
    criteria: "Opened 1+ email in 31-60 days, no recent clicks"
    treatment: "Re-engagement content, best-of, reduce frequency"
    
  cold:
    criteria: "No opens in 60-90 days"
    treatment: "Win-back sequence, then sunset"
    
  dead:
    criteria: "No opens in 90+ days despite win-back"
    treatment: "Remove from list — they're hurting deliverability"
    
  new_subscriber:
    criteria: "Joined in last 14 days"
    treatment: "Welcome sequence only, no promotional"
    
  customer:
    criteria: "Made a purchase"
    treatment: "Post-purchase flow, upsell, loyalty"
    
  high_value_customer:
    criteria: "Purchase >$500 OR 3+ purchases"
    treatment: "VIP offers, early access, personal touch"
```

**Tier 2 — Interest-based segments:**
- Tag subscribers based on which links they click, which lead magnet they downloaded, which pages they visited
- Build per-topic segments: "interested in [feature/topic/product]"
- Send relevant content only — one irrelevant email loses more than skipping a send

**Tier 3 — Lifecycle segments:**
- Trial users, active customers, churned customers, advocates
- Each gets different messaging: trial = education, active = expansion, churned = win-back

### 2.3 List Hygiene Schedule

| Action | Frequency | How |
|--------|-----------|-----|
| Remove hard bounces | After every send | Automatic in most ESPs |
| Remove spam complaints | After every send | Automatic |
| Clean soft bounces | Monthly | Remove after 3 consecutive soft bounces |
| Re-engage cold subscribers | Every 60 days | 3-email win-back sequence |
| Sunset unengaged | Every 90 days | Remove anyone who didn't engage with win-back |
| Validate list | Quarterly | Run through NeverBounce/ZeroBounce |
| Audit segments | Monthly | Check segment sizes, merge overlaps |

---

## Phase 3: Email Sequences (Templates)

### 3.1 Welcome Sequence (7 emails, 14 days)

The most important sequence. First email gets 50-80% open rate — don't waste it.

**Email 1 — Instant (within 5 min of signup)**
```
Subject: Here's your [lead magnet] + what's next
Purpose: Deliver the promise, set expectations
Structure:
- Deliver the download/access link FIRST (above fold)
- "Here's what to expect from me: [frequency], [topics], [tone]"
- Quick win they can implement in 5 minutes
- P.S. "Reply and tell me your biggest challenge with [topic]" (boosts deliverability + gives you data)
CTA: Download/access the lead magnet
```

**Email 2 — Day 1**
```
Subject: The [#1 mistake/myth] about [topic]
Purpose: Establish authority, deliver value
Structure:
- Open with a contrarian take or surprising stat
- Teach one thing they can use immediately
- Share a quick result/case study
CTA: Read blog post / watch video / try the technique
```

**Email 3 — Day 3**
```
Subject: How [person/company] achieved [specific result]
Purpose: Social proof + story
Structure:
- Customer story or your own origin story
- Specific numbers and timeline
- The "aha moment" that changed everything
- Bridge to how subscriber can do the same
CTA: Read the full case study
```

**Email 4 — Day 5**
```
Subject: [Number] [resources] I wish I had when I started
Purpose: Value dump + trust building
Structure:
- Curated list of genuinely useful resources (not all yours)
- Brief commentary on why each matters
- Position yourself as generous curator, not just seller
CTA: Bookmark this email / save for later
```

**Email 5 — Day 7**
```
Subject: Real talk about [common objection]
Purpose: Handle objections before they ask
Structure:
- Acknowledge the #1 reason people don't take action
- Address it honestly (don't dismiss concerns)
- Reframe: what it actually costs to NOT act
- Subtle proof that your approach works
CTA: Soft mention of your product/service (first time)
```

**Email 6 — Day 10**
```
Subject: What [specific result] looks like (step by step)
Purpose: Paint the transformation picture
Structure:
- Before/after comparison
- Step-by-step process overview
- Specific, tangible outcomes with numbers
- "If you want help implementing this..."
CTA: Book a call / start trial / view product
```

**Email 7 — Day 14**
```
Subject: Quick question for you
Purpose: Direct ask + clear next step
Structure:
- "You've been here for 2 weeks. Here's what I've shared..."
- Quick recap of value delivered
- Clear, direct CTA — no ambiguity
- Include FAQ for common hesitations
- P.S. with urgency or bonus
CTA: Buy / start trial / book call (main conversion ask)
```

### 3.2 Product Launch Sequence (9 emails, 10 days)

```yaml
launch_sequence:
  pre_launch:
    email_1:
      day: -7
      subject: "Something big is coming [topic hint]"
      goal: "Build anticipation, seed the problem"
      
    email_2:
      day: -4
      subject: "The [problem] nobody talks about"
      goal: "Agitate the pain point your product solves"
      
    email_3:
      day: -1
      subject: "Tomorrow: [product name] goes live"
      goal: "Create excitement, early-bird waitlist"
      
  launch:
    email_4:
      day: 0  # morning
      subject: "[Product] is LIVE — [key benefit]"
      goal: "Announce, showcase benefits, social proof"
      
    email_5:
      day: 0  # evening
      subject: "[Number] people already grabbed this"
      goal: "Social proof + urgency (early adopter stats)"
      
    email_6:
      day: 2
      subject: "I wasn't going to share this, but..."
      goal: "Behind-the-scenes story + testimonial"
      
  closing:
    email_7:
      day: 5
      subject: "FAQ: Your [product] questions answered"
      goal: "Handle objections, reduce friction"
      
    email_8:
      day: 7
      subject: "[Bonus] disappears in 48 hours"
      goal: "Scarcity — launch bonus deadline"
      
    email_9:
      day: 9
      subject: "Last chance: [product] launch price ends tonight"
      goal: "Final urgency, recap all value, close"
```

### 3.3 Re-engagement / Win-Back Sequence (3 emails)

```
Email 1 — "We miss you (and here's our best stuff)"
- Acknowledge they've been quiet
- Curate your 3 best pieces of content
- "If you're still interested in [topic], here's what you've missed"
- CTA: Click any link to stay subscribed

Email 2 (3 days later) — "Should I stop emailing you?"
- Direct subject line gets high opens from curiosity
- "I only want to email people who want to hear from me"
- One-click to stay: "Yes, keep me subscribed" button
- Honest and respectful tone

Email 3 (5 days later) — "Goodbye (unless...)"
- Final notice: "This is my last email unless you click below"
- Clear opt-back-in button
- No hard feelings messaging
- Auto-remove anyone who doesn't click within 7 days
```

### 3.4 Post-Purchase Sequence (5 emails)

```yaml
post_purchase:
  email_1:
    timing: "Immediately after purchase"
    subject: "You're in! Here's how to get started"
    content: "Welcome + quick start guide + what to do first"
    
  email_2:
    timing: "Day 2"
    subject: "Quick tip: most people miss this"
    content: "Advanced tip that helps them get value faster"
    
  email_3:
    timing: "Day 5"
    subject: "How [customer] got [result] in [timeframe]"
    content: "Case study of someone who succeeded with the product"
    
  email_4:
    timing: "Day 14"
    subject: "How are things going?"
    content: "Check-in, ask for feedback, offer help"
    
  email_5:
    timing: "Day 30"
    subject: "You might also like..."
    content: "Cross-sell or upsell based on what they bought"
```

### 3.5 Abandoned Cart Sequence (3 emails)

```
Email 1 — 1 hour after abandonment
Subject: "You left something behind"
- Show the product with image
- Remind of key benefits (not features)
- Direct "Complete your order" button
- No discount yet

Email 2 — 24 hours
Subject: "Still thinking it over?"
- Address the #1 objection for this product
- Add social proof (review, testimonial, number of customers)
- "Questions? Reply to this email"
- Optional: free shipping or small bonus

Email 3 — 72 hours
Subject: "Last chance: [product] + [incentive]"
- Time-limited incentive (10% off, bonus item, extended trial)
- Urgency: "This offer expires in 24 hours"
- Final CTA
- If no conversion → move to browse abandonment segment
```

---

## Phase 4: Email Copywriting Framework

### 4.1 The AIDA-P Formula

Every email should follow this structure:

```
A — Attention: Subject line + first line hook
I — Interest: "Here's why this matters to you specifically"
D — Desire: Paint the outcome, use social proof, agitate FOMO
A — Action: Single, clear CTA
P — P.S.: Secondary hook or urgency (gets read by 79% of readers)
```

### 4.2 Subject Line Formulas (with examples)

**Curiosity gap:**
- "The [topic] trick that [audience] don't want you to know"
- "I was wrong about [assumption]"
- "This changes everything about [topic]"

**Specificity:**
- "[Number] ways to [achieve result] (tested on [sample size])"
- "How [person] went from [A] to [B] in [timeframe]"
- "The exact [thing] I used to [result]"

**Direct value:**
- "Your [timeframe] guide to [result]"
- "[Result] without [pain point]"
- "Stop [bad thing]. Do this instead."

**Urgency (use sparingly):**
- "[Offer] ends at midnight"
- "Only [number] spots left"
- "Price goes up [day]"

**Personal:**
- "Quick question, [name]"
- "Can I be honest with you?"
- "I made a mistake"

### 4.3 Writing Rules

1. **One idea per email** — If you have 3 ideas, write 3 emails
2. **Write like you talk** — Read it aloud. If it sounds robotic, rewrite.
3. **Short paragraphs** — 1-3 sentences max. White space is your friend.
4. **Bold the key points** — Skimmers should get the message from bolded text alone
5. **One CTA** — Repeat it 2-3 times (top, middle, bottom) but always the same action
6. **Subject line last** — Write the email first, then craft the subject
7. **Preview text is free real estate** — Extend the subject line's curiosity, don't repeat it
8. **P.S. always** — 79% of readers scan to the P.S. first
9. **"You" > "We"** — The email is about the reader, not you
10. **Specific > vague** — "$4,723 in 30 days" beats "more revenue fast"

### 4.4 Email Length Guide

| Type | Length | Why |
|------|--------|-----|
| Welcome | 150-250 words | Deliver value fast, don't overwhelm |
| Newsletter | 300-500 words | Curated value, scan-friendly |
| Story/case study | 400-700 words | Needs room for narrative arc |
| Sales | 200-400 words | Long enough to persuade, short enough to read |
| Announcement | 100-200 words | Get to the point |
| Re-engagement | 50-100 words | Short = respectful of their time |

---

## Phase 5: Automation & Workflows

### 5.1 Essential Automations (build these first)

```yaml
automations:
  welcome_series:
    trigger: "New subscriber"
    sequence: "7-email welcome (see Phase 3.1)"
    priority: "CRITICAL — build this first"
    
  abandoned_cart:
    trigger: "Added to cart, no purchase in 1 hour"
    sequence: "3-email recovery (see Phase 3.5)"
    priority: "HIGH — recovers 5-15% of abandoned carts"
    
  post_purchase:
    trigger: "Completed purchase"
    sequence: "5-email onboarding (see Phase 3.4)"
    priority: "HIGH — drives retention and referrals"
    
  re_engagement:
    trigger: "No opens in 60 days"
    sequence: "3-email win-back (see Phase 3.3)"
    priority: "MEDIUM — list hygiene"
    
  birthday_anniversary:
    trigger: "Date field match"
    sequence: "1 email with special offer"
    priority: "LOW — nice touch, easy to set up"
    
  browse_abandonment:
    trigger: "Viewed product page, no cart add in 24h"
    sequence: "1-2 emails showcasing viewed products"
    priority: "MEDIUM — works well for ecommerce"
    
  milestone:
    trigger: "Customer reaches usage milestone"
    sequence: "Celebration + upsell"
    priority: "MEDIUM — expansion revenue"
```

### 5.2 Conditional Logic Patterns

```yaml
# Example: Branch based on engagement
welcome_flow:
  start: "Send Email 1 (welcome)"
  wait: "2 days"
  condition: "Opened Email 1?"
  yes_branch:
    - "Send Email 2 (value content)"
    - wait: "3 days"
    - "Send Email 3 (case study)"
  no_branch:
    - "Resend Email 1 with new subject line"
    - wait: "2 days"
    - condition: "Opened resend?"
      yes: "Merge into yes_branch at Email 2"
      no: "Tag as 'slow starter', send simplified sequence"
```

### 5.3 Tagging Strategy

Tag every meaningful action:

```yaml
auto_tags:
  on_signup:
    - "source:[lead_magnet_name]"
    - "interest:[topic]"
    - "date:joined-[YYYY-MM]"
    
  on_click:
    - "clicked:[link_category]"
    - "interest:[inferred_topic]"
    
  on_purchase:
    - "customer"
    - "product:[product_name]"
    - "value:[tier]"  # low/mid/high based on purchase amount
    
  on_behavior:
    - "engaged" / "warm" / "cold" (auto-updated by engagement scoring)
    - "replied" (manual tag — these are your best subscribers)
```

---

## Phase 6: Analytics & Optimization

### 6.1 Metrics Dashboard

Track weekly:

```yaml
weekly_metrics:
  growth:
    new_subscribers: 0
    unsubscribes: 0
    net_growth: 0
    growth_rate: "0%"
    
  engagement:
    emails_sent: 0
    unique_opens: 0
    open_rate: "0%"
    unique_clicks: 0
    click_rate: "0%"
    click_to_open_rate: "0%"  # clicks / opens — measures content quality
    replies: 0
    
  health:
    bounce_rate: "0%"
    spam_complaints: 0
    spam_rate: "0%"
    
  revenue:
    email_attributed_revenue: 0
    revenue_per_email: 0
    revenue_per_subscriber: 0
    
  automations:
    welcome_completion_rate: "0%"
    cart_recovery_rate: "0%"
    sequence_drop_off_points: []
```

### 6.2 Benchmarks by Industry

| Industry | Avg Open Rate | Avg Click Rate | Avg Unsub Rate |
|----------|--------------|----------------|----------------|
| SaaS/Tech | 20-25% | 2-3% | 0.2-0.4% |
| Ecommerce | 15-20% | 2-3% | 0.2-0.3% |
| Professional Services | 18-22% | 2-3% | 0.2-0.3% |
| Finance | 20-25% | 2.5-4% | 0.1-0.2% |
| Healthcare | 20-23% | 2-3% | 0.2-0.3% |
| Education | 22-28% | 3-5% | 0.1-0.2% |
| Media/Publishing | 18-22% | 3-5% | 0.1-0.2% |
| Agencies | 18-22% | 2-3% | 0.3-0.5% |

Compare your metrics to industry benchmarks. If you're below average, focus on the lowest dimension first.

### 6.3 A/B Testing Framework

```yaml
ab_test_plan:
  hypothesis: "Changing [variable] from [A] to [B] will increase [metric] by [X%]"
  variable: ""  # subject line, send time, CTA, layout, sender name, content length
  test_size: "20% of list minimum (10% variant A, 10% variant B)"
  success_metric: "open_rate | click_rate | conversion_rate"
  duration: "Wait for statistical significance (usually 24-48h, or 1000+ opens minimum)"
  winner_deployment: "Send winner to remaining 80%"
  
  # Test priority order (highest impact first):
  test_order:
    1: "Subject lines (biggest impact on opens)"
    2: "Send time/day (easy to test, meaningful impact)"
    3: "CTA text and placement (direct conversion impact)"
    4: "Email length (affects click-through)"
    5: "Sender name (personal name vs brand)"
    6: "Content format (text vs image-heavy)"
    7: "Personalization depth"
```

**Rules for valid testing:**
- Test ONE variable at a time
- Minimum sample: 1,000 recipients per variant (500 absolute minimum)
- Wait for significance — don't call it early
- Log every test and result in a testing journal
- Implement winners permanently, then test the next variable

### 6.4 Monthly Review Template

```markdown
## Email Marketing Review — [Month YYYY]

### Growth
- Subscribers: [start] → [end] (net: [+/-])
- Top acquisition source: [source] ([%])
- List churn rate: [%]

### Engagement
- Avg open rate: [%] (vs [last month %]) [↑↓]
- Avg click rate: [%] (vs [last month %]) [↑↓]
- Best performing email: "[subject]" — [open%] open, [click%] click
- Worst performing: "[subject]" — [why it underperformed]

### Revenue
- Email-attributed revenue: $[amount]
- Revenue per subscriber: $[amount]
- Top converting sequence: [name] — $[amount]

### Health
- Bounce rate: [%]
- Spam complaints: [count] ([%])
- List cleaned: [count] removed

### Tests Run
| Test | Variable | Winner | Lift |
|------|----------|--------|------|
| | | | |

### Next Month Priorities
1. [Priority based on weakest metric]
2. [New sequence or campaign to build]
3. [Test to run]
```

---

## Phase 7: Advanced Strategies

### 7.1 Newsletter Monetization

```yaml
monetization_options:
  sponsored_content:
    model: "Charge per issue or per click"
    pricing: "$25-50 CPM (per 1000 subscribers) for niche B2B"
    rule: "Max 1 sponsor per issue, clearly labeled"
    
  affiliate:
    model: "Earn commission on recommended products"
    rule: "Only recommend products you've used. Disclose always."
    
  premium_tier:
    model: "Free newsletter + paid upgrade"
    pricing: "$5-25/month for exclusive content"
    conversion: "Expect 2-5% free-to-paid conversion"
    
  product_funnel:
    model: "Newsletter → low-ticket → high-ticket"
    flow: "Free content → $47 product → $500 course → $5K consulting"
```

### 7.2 Deliverability Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Opens dropping gradually | List fatigue, growing cold segment | Clean list, improve content, reduce frequency |
| Opens dropped suddenly | IP/domain reputation hit | Check blacklists, review recent sends for spam triggers |
| High bounce rate | Old/purchased list, typo emails | Validate list immediately, implement double opt-in |
| Going to spam (Gmail) | Missing authentication, spammy content | Fix SPF/DKIM/DMARC, rewrite content, warm domain |
| Going to Promotions tab | Too promotional, image-heavy | More text, fewer images, conversational tone |
| Low clicks despite good opens | Weak CTA, irrelevant content | A/B test CTAs, improve segmentation |
| High unsubscribes | Wrong frequency, wrong content, mismatched expectations | Survey unsubs, realign content with signup promise |

### 7.3 Email + Other Channels

```yaml
cross_channel:
  email_plus_retargeting:
    - "Non-openers → Facebook/Google retargeting audience"
    - "Clickers who didn't buy → retarget with product ads"
    
  email_plus_sms:
    - "Time-sensitive offers: email first, SMS 2 hours later to non-openers"
    - "Transactional: SMS for shipping, email for details"
    
  email_plus_social:
    - "Newsletter content → social media posts (repurpose)"
    - "Social engagement → email subscriber (capture)"
    
  email_plus_direct_mail:
    - "High-value prospects who don't open: physical mailer"
    - "Post-purchase thank you card for VIP customers"
```

### 7.4 Compliance Checklist

- [ ] **CAN-SPAM (US):** Physical address in footer, working unsubscribe, honest subject lines
- [ ] **GDPR (EU):** Explicit consent, right to erasure, data portability, privacy policy link
- [ ] **CASL (Canada):** Express consent required (not just implied), sender identification
- [ ] **Unsubscribe:** Process within 10 business days (legally), immediately (best practice)
- [ ] **Data storage:** Subscriber data encrypted at rest, access limited
- [ ] **Consent records:** Store timestamp, source, and method for every opt-in

---

## Edge Cases & Advanced Scenarios

### Multi-language Campaigns
- Segment by language/region at signup
- Don't auto-translate — hire native speakers or verify AI translations
- Cultural differences matter: humor, formality, holidays vary by region
- Separate sending domains per language if volume justifies it

### B2B vs B2C Differences

| Aspect | B2B | B2C |
|--------|-----|-----|
| Best send time | Tue-Thu, 9-11am | Evenings, weekends |
| Tone | Professional but human | Casual, emotional |
| Decision timeline | Weeks-months | Minutes-days |
| Content focus | ROI, efficiency, case studies | Benefits, lifestyle, FOMO |
| CTA style | "Book a demo", "See pricing" | "Buy now", "Shop the sale" |
| Sequence length | Longer (7-12 emails) | Shorter (3-5 emails) |

### Seasonal Strategy
- Plan campaigns 4-6 weeks ahead for major holidays
- Q4 (Oct-Dec): Highest email volume — start warming early, send your best
- January: "New year, new you" — high engagement with self-improvement content
- Summer: Lower engagement — reduce frequency, don't launch major campaigns
- Black Friday/Cyber Monday: Build anticipation 2 weeks early, segment deal-seekers

### Email for High-Ticket ($5K+)
- DON'T try to sell in the email — sell the call/meeting
- Longer nurture sequence (30-60 days before asking)
- Case studies and ROI proof at every stage
- Personal sender (founder/advisor name, not brand)
- Replies > clicks (encourage two-way conversation)
- Follow-up tenaciously — 80% of high-ticket sales happen after email 5+
