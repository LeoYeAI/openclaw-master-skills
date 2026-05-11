---
name: afrexai-sales-playbook
version: 1.0.0
description: "Complete B2B sales system — from ICP to closed-won. Discovery frameworks, objection handling, pipeline management, forecasting, and deal acceleration. Works for any B2B company."
author: afrexai
tags: sales, b2b, pipeline, crm, deals, closing, objections, forecasting, revenue
---

# B2B Sales Playbook ⚡

**The complete system for running a repeatable, scalable B2B sales operation.**

Not a CRM wrapper. Not a template collection. This is a full sales methodology — from identifying your ideal customer to closing the deal and expanding the account.

---

## Phase 1: Ideal Customer Profile (ICP) & Territory

### ICP Definition Template

```yaml
icp:
  company:
    industry: [SaaS, Fintech, Healthcare, etc.]
    size_employees: [50-500]
    size_revenue: [$5M-$50M ARR]
    geography: [US, UK, DACH, etc.]
    tech_stack: [signals they use tools you integrate with]
    growth_stage: [Series A-C, post-PMF, scaling]
    
  pain_indicators:  # Observable signals, not assumptions
    - hiring_for: [roles that signal the pain you solve]
    - tech_adoption: [recently adopted X tool = need for Y]
    - org_changes: [new VP of X = budget for initiatives]
    - regulatory: [upcoming compliance deadline]
    - public_statements: [earnings call mentions, press releases]
    
  buyer_personas:
    economic_buyer:  # Signs the check
      title_patterns: [VP Sales, CRO, CEO]
      cares_about: [revenue growth, cost reduction, competitive advantage]
      speaks_in: [ROI, board metrics, market share]
      
    champion:  # Fights for you internally
      title_patterns: [Director, Head of, Senior Manager]
      cares_about: [team productivity, career advancement, solving daily pain]
      speaks_in: [workflow, efficiency, team capacity]
      
    technical_evaluator:  # Validates feasibility
      title_patterns: [Engineering Manager, Architect, IT Director]
      cares_about: [integration, security, maintenance burden]
      speaks_in: [APIs, uptime, migration effort]
      
    end_user:  # Uses it daily
      title_patterns: [Individual contributors]
      cares_about: [ease of use, time saved, fewer context switches]
      
  anti-signals:  # DO NOT pursue
    - company_size_under: 20  # too small, long sales cycle for low ACV
    - no_budget_indicator: [startup pre-revenue, recent layoffs >30%]
    - tech_mismatch: [on-prem only, legacy stack incompatible]
    - cultural: [committee-driven decisions with 6+ stakeholders at low ACV]
```

### Territory Planning

**Account Tiering:**

| Tier | Criteria | Accounts | Time Allocation | Touch Frequency |
|------|----------|----------|-----------------|-----------------|
| **Tier 1** | Perfect ICP fit + active pain signals | 20-30 | 50% of time | 2-3x/week |
| **Tier 2** | Good ICP fit, no active signals yet | 50-80 | 30% of time | 1x/week |
| **Tier 3** | Partial fit, worth monitoring | 100-200 | 15% of time | 2x/month |
| **Inbound** | Any qualified inbound | Variable | 5% of time | Respond <1hr |

**Monthly Territory Review:**
1. Re-score all Tier 1 accounts — any demote to Tier 2?
2. Scan Tier 2 for new signals — any promote to Tier 1?
3. Remove dead accounts from Tier 3 (no engagement in 90 days)
4. Add new accounts from prospecting
5. Calculate territory coverage: (accounts with activity / total) — target >80% for Tier 1

---

## Phase 2: Prospecting & Outreach

### Multi-Channel Sequence Framework

**Principle:** No single channel works. Layer them.

**Standard Tier 1 Sequence (14 days):**

| Day | Channel | Action | Goal |
|-----|---------|--------|------|
| 1 | Email | Personalized cold email (see template below) | Open + reply |
| 1 | LinkedIn | View profile + connect (NO pitch in connect msg) | Warm the name |
| 3 | Email | Follow-up with value add (article, insight, data) | Demonstrate expertise |
| 5 | LinkedIn | Comment on their recent post (genuine, not salesy) | Build familiarity |
| 7 | Phone | Cold call (see script below) | Live conversation |
| 7 | Email | Voicemail follow-up email | Multi-touch reinforcement |
| 10 | LinkedIn | Send message referencing your email/call attempts | Channel switch |
| 12 | Email | Breakup email (creates urgency) | Force response |
| 14 | Phone | Final attempt | Last touch |

**Sequence Rules:**
- STOP the sequence the moment they reply (positive OR negative)
- Never send more than 1 email per day to the same person
- Personalization must reference something SPECIFIC (their company, role, recent news)
- If they open but don't reply 3x → they're reading, switch to phone
- If zero engagement after full sequence → move to Tier 3, retry in 90 days

### Cold Email Templates

**Template 1: The Trigger Event**
```
Subject: [Trigger event] → quick thought

[First name],

Saw [specific trigger — new hire, funding, product launch, earnings mention].

When [companies in their situation] hit this stage, [specific problem] usually becomes the bottleneck — [data point or example].

[One sentence on how you solve this, tied to the trigger.]

Worth a 15-min call to see if this applies to [company]?

[Your name]
```

**Template 2: The Peer Reference**
```
Subject: How [similar company] solved [problem]

[First name],

[Similar company in their industry] was dealing with [specific problem] — [quantify: X hours/week, $Y lost, Z% error rate].

They [brief result: cut X by 40%, saved $Y/month, shipped Z days faster].

Happy to share what they did differently — no pitch, just the playbook.

15 min this week?

[Your name]
```

**Template 3: The Breakup**
```
Subject: Closing the loop

[First name],

I've reached out a few times about [problem/topic] — I'll assume the timing isn't right.

If [problem] becomes a priority later, I'm here. 

Deleting your reminder from my CRM now.

[Your name]
```

**Why breakup emails work:** 30-40% reply rate. People respond to loss aversion. "Deleting your reminder" creates fear of losing access.

### Cold Call Script

**Opening (first 10 seconds decide everything):**
```
"Hi [Name], this is [You] from [Company]. 
Did I catch you at an okay time?"

[If yes:]
"I'll be brief. I noticed [trigger/signal] and wanted to ask —
are you currently dealing with [specific problem]?"

[If they confirm the problem:]
"Got it. What's that costing you right now — in time, money, or headaches?"

[Let them talk. Take notes. Ask follow-up questions.]

"That's exactly what we help with. [One sentence proof point.]
Would it make sense to set up 20 minutes this week to dig into this properly?"
```

**Common cold call responses + rebuttals:**

| They Say | You Say |
|----------|---------|
| "Not interested" | "Totally fair — can I ask, is it because [problem] isn't a priority, or you've already solved it?" |
| "Send me an email" | "Happy to — what specifically would be most useful to include? That way I don't waste your time." |
| "We already have a solution" | "Good — how's it working? Most companies I talk to have something in place but still have gaps in [specific area]." |
| "Bad timing" | "When would be better? I can put a reminder in for [suggested date]." |
| "How did you get my number?" | "LinkedIn / your website. I know cold calls aren't fun — I'll keep it under 2 minutes." |

---

## Phase 3: Discovery — The Most Important Meeting

### MEDDPICC Qualification Framework

Score each element 1-3 (1=unknown, 2=partially known, 3=fully confirmed):

```yaml
deal_qualification:
  metrics:  # Quantifiable impact they care about
    score: [1-3]
    detail: "[What numbers matter? Revenue increase, cost reduction, time saved?]"
    source: "[Who told you? Validated how?]"
    
  economic_buyer:  # Person with budget authority
    score: [1-3]
    name: "[Name and title]"
    access: "[Have you spoken to them directly?]"
    priority: "[Is this in their top 3 priorities?]"
    
  decision_criteria:  # How they'll evaluate options
    score: [1-3]
    technical: "[Integration, security, performance requirements]"
    business: "[ROI threshold, payback period, risk tolerance]"
    political: "[Internal politics, competing priorities]"
    
  decision_process:  # How they'll make the decision
    score: [1-3]
    steps: "[What happens between now and signed contract?]"
    timeline: "[When do they need to decide? Hard deadline?]"
    stakeholders: "[Who's involved? Who has veto power?]"
    
  paper_process:  # Legal/procurement steps
    score: [1-3]
    procurement: "[Standard terms or custom negotiation?]"
    legal_review: "[How long does legal take? Past precedent?]"
    security_review: "[Required? How long?]"
    
  identified_pain:  # The problem driving this
    score: [1-3]
    pain: "[What hurts? What breaks?]"
    impact: "[Cost of inaction — quantified]"
    urgency: "[Why now? What happens if they wait?]"
    
  champion:  # Your internal advocate
    score: [1-3]
    name: "[Who is it?]"
    motivation: "[Why do THEY personally care?]"
    power: "[Can they influence the economic buyer?]"
    coached: "[Have you prepped them for internal selling?]"
    
  competition:  # What you're up against
    score: [1-3]
    competitors: "[Named competitors in the evaluation]"
    status_quo: "[Doing nothing is always a competitor]"
    differentiation: "[Why you win against each]"
    
  total_score: "[X/24]"
  # 20-24 = Strong deal, forecast confidently
  # 15-19 = Gaps to fill, work the unknowns
  # 10-14 = At risk, needs significant work
  # <10 = Unqualified, don't invest time
```

### Discovery Questions by Category

**Situation (understand current state):**
1. Walk me through how [process] works today, start to finish.
2. What tools/systems are involved?
3. How many people touch this process?
4. How long has it been this way?

**Problem (surface the pain):**
5. Where does it break down?
6. What's the impact when it fails? (Get a NUMBER)
7. How often does that happen?
8. What have you tried to fix it?
9. Why didn't that work?

**Implication (expand the pain):**
10. If this doesn't get fixed in the next 6 months, what happens?
11. How does this affect [their boss / their team / the company]?
12. What's the cost of doing nothing? (Force them to quantify)
13. What other initiatives depend on solving this?

**Need-Payoff (let THEM sell the solution):**
14. If you could wave a magic wand, what would this look like?
15. What would it mean for your team if [pain] went away?
16. If you could get [specific metric improvement], what would that unlock?
17. How would [their boss] react to those results?

**Process (map the buying journey):**
18. Besides you, who else needs to weigh in on this?
19. What's happened before when you've bought software like this?
20. Is there a budget allocated, or would this need approval?
21. What's the ideal timeline for having this running?
22. What would kill this deal?

### Discovery Call Structure (30 min)

| Segment | Time | What You Do |
|---------|------|-------------|
| Opening | 2 min | Confirm agenda, set expectations, get permission to ask questions |
| Context | 5 min | Ask situation questions — understand their world |
| Pain | 10 min | Ask problem + implication questions — go DEEP on 1-2 pains |
| Vision | 5 min | Ask need-payoff questions — paint the future state |
| Process | 5 min | Map decision process, timeline, stakeholders |
| Next Steps | 3 min | Agree on SPECIFIC next action with date |

**Golden Rule:** Talk <30% of the time. If you're talking more, you're pitching, not discovering.

---

## Phase 4: Demo & Presentation

### The Problem-Solution-Proof Framework

Never demo features. Demo outcomes.

**Structure:**
1. **Mirror their pain** (2 min) — "You told me [specific pain from discovery]. Here's what that costs you: [quantified impact]."
2. **Show the solution** (15 min) — Walk through their USE CASE, not a generic tour. Use THEIR data, THEIR terminology, THEIR workflow.
3. **Prove it works** (5 min) — Case study of similar company. Before/after numbers. "Company X had the same problem. Here's what happened."
4. **Address risks** (3 min) — Proactively surface the top concern they haven't raised yet. "Most companies at your stage worry about [X]. Here's how we handle that."
5. **Next step** (2 min) — Never end without a committed next action.

### Demo Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Show every feature | Show only what maps to their pain |
| Start with "let me share my screen" | Start with "let me recap what you told me" |
| Say "and we also do..." | Say "you mentioned [pain] — here's exactly how that works" |
| Demo to the whole committee at once | Demo to champion first, then do joint session |
| Let the demo run long | End 5 min early — scarcity signals confidence |
| Send a recording after | Send a 1-page summary with their specific ROI |

### Mutual Action Plan (MAP)

After demo, create a shared doc with the prospect:

```yaml
mutual_action_plan:
  deal: "[Company Name] + [Your Company]"
  target_go_live: "[Date]"
  
  steps:
    - step: "Technical deep-dive with engineering team"
      owner: "[Prospect technical contact]"
      date: "[Date]"
      status: pending
      
    - step: "Security review / questionnaire"
      owner: "[You — send completed questionnaire]"
      date: "[Date]"
      status: pending
      
    - step: "Business case presentation to [Economic Buyer]"
      owner: "[Champion + You]"
      date: "[Date]"
      status: pending
      
    - step: "Proposal / pricing review"
      owner: "[You]"
      date: "[Date]"
      status: pending
      
    - step: "Legal / contract review"
      owner: "[Prospect legal]"
      date: "[Date]"
      status: pending
      
    - step: "Signature"
      owner: "[Economic Buyer]"
      date: "[Date]"
      status: pending
      
    - step: "Kickoff call"
      owner: "[Your CS team]"
      date: "[Date]"
      status: pending
```

**Why MAPs work:** Shared accountability. Visible timeline. Champion can use it to drive internal momentum. You can reference specific dates when things stall.

---

## Phase 5: Objection Handling

### The LAER Framework

Every objection follows this pattern:

1. **Listen** — Let them finish. Don't interrupt. Nod.
2. **Acknowledge** — "That's a fair concern" / "I hear you" (NOT "I understand but...")
3. **Explore** — "Help me understand — is it [X] specifically, or more about [Y]?" (Diagnose the REAL objection)
4. **Respond** — Address the real concern, not the surface one.

### Objection Playbook

**Price Objections:**

| Objection | Real Meaning | Response |
|-----------|-------------|----------|
| "Too expensive" | They don't see the value yet | "Compared to what? Help me understand what you're measuring against." Then re-anchor to cost of doing nothing. |
| "Can you do a discount?" | Testing your confidence | "Our pricing reflects the value we deliver. [Company X] saw [Y result] — the ROI was [Z]x. What specifically feels misaligned?" |
| "We don't have budget" | Not a priority OR wrong buyer | "Is this a timing issue, or is [problem] not a priority this quarter?" If priority: "When budgets reset, can we plan for that?" |
| "Competitor is cheaper" | Using you for leverage OR genuinely price-sensitive | "They may be. The question is what [missing capability] costs you over 12 months. Would you like me to map that out?" |

**Timing Objections:**

| Objection | Real Meaning | Response |
|-----------|-------------|----------|
| "Not now, maybe next quarter" | No urgency | "What changes next quarter? If [problem] costs you [X/month], that's [3X] by next quarter. What would it take to move this up?" |
| "We're in the middle of [other project]" | Genuinely busy OR smokescreen | "Totally get it. When does [project] wrap? Let's lock in a date now so it doesn't slip." |
| "We need to think about it" | Unresolved concern they haven't voiced | "Of course. What specifically do you need to think through? I might be able to address it now." |

**Authority Objections:**

| Objection | Real Meaning | Response |
|-----------|-------------|----------|
| "I need to run this by my boss" | You're not talking to the decision-maker | "Absolutely. What's their biggest concern likely to be? Let's prep for that together." Then: "Would it help if I joined that conversation?" |
| "Our committee decides" | Multi-stakeholder deal | "Who's on the committee? What does each person care about most? Let's make sure the proposal speaks to all of them." |

**Status Quo Objections:**

| Objection | Real Meaning | Response |
|-----------|-------------|----------|
| "We're fine with what we have" | Fear of change > desire for improvement | "How long have you had it? What's changed in your business since then? Most companies I talk to outgrow [current solution] when they hit [their growth stage]." |
| "We built our own" | Pride in internal solution | "That's impressive. What's the maintenance cost? Most teams I talk to find their engineers are spending [X%] of time maintaining instead of building product." |

### The "Negative Reverse" Technique

When objections keep coming, flip the script:

> "It sounds like this might not be the right fit. Should we just call it?"

This does two things:
1. Takes pressure off — they stop defending
2. Forces them to either agree (you saved time) or sell THEMSELVES on why it IS a fit

---

## Phase 6: Closing & Negotiation

### Closing Signals (When to Ask)

**Verbal:**
- "What would implementation look like?"
- "How does pricing work?"
- "Can we do a pilot?"
- "What's the contract length?"
- "When could we start?"

**Behavioral:**
- They introduce you to additional stakeholders
- They ask for references
- They share internal documents/requirements
- Response time gets faster
- They start using "we" and "when" instead of "if"

### Closing Techniques

**1. The Summary Close**
```
"So to recap — [problem] is costing you [X/month], you need a solution 
by [date] for [reason], and [your product] addresses [their top 3 criteria]. 
Shall I send the agreement?"
```

**2. The Next Step Close**
```
"Based on everything we've discussed, the next step would be 
[specific action — contract review, pilot setup, intro to CS]. 
Should I kick that off?"
```

**3. The Assumptive Close**
```
"Great — I'll have the proposal over by end of day. 
Would you prefer monthly or annual billing?"
```

**4. The Puppy Dog Close (for hesitant buyers)**
```
"Tell you what — let's do a 14-day pilot with [specific use case]. 
You'll see [expected result] in the first week. 
If it doesn't deliver, no hard feelings. Fair?"
```

### Negotiation Rules

1. **Never negotiate against yourself.** If they ask for a discount, ask what they'd give in return (longer term, case study, referral, faster signature).
2. **Trade, don't cave.** Every concession must get something back.
3. **Anchor high.** Start with your full price. The first number sets the range.
4. **Silence is power.** After stating your price, STOP TALKING. Let them respond.
5. **Know your walk-away.** Before any negotiation, set your floor. Below that = no deal.
6. **Bundle value, don't discount price.** Add a month free, add training, add premium support — don't cut the sticker price.
7. **Create deadline.** "This pricing is valid through [date]" or "I have 2 onboarding slots left this quarter."

### Discount Decision Tree

```
Prospect asks for discount
├── Do they have budget? 
│   ├── YES → Don't discount. Anchor to value.
│   └── NO → Is the deal strategic (logo, case study, expansion potential)?
│       ├── YES → Offer trade: discount for [annual commit / case study / referral]
│       └── NO → Walk away or defer to next quarter
├── Is this a competitive situation?
│   ├── YES → Don't discount on price. Win on value + risk reduction.
│   └── NO → They're testing. Hold firm. "Our pricing reflects..."
└── Final rule: NEVER discount more than 20% on any deal. 
    Below that, you're training them to negotiate hard every renewal.
```

---

## Phase 7: Pipeline Management

### Pipeline Stages & Exit Criteria

| Stage | Definition | Exit Criteria | Probability |
|-------|-----------|---------------|-------------|
| **Prospecting** | Initial outreach, no meeting yet | Meeting booked | 5% |
| **Discovery** | First meeting held | Pain confirmed, ICP match validated | 15% |
| **Evaluation** | Active evaluation, demo delivered | Champion identified, decision criteria known | 30% |
| **Proposal** | Proposal/pricing sent | Budget confirmed, decision process mapped | 50% |
| **Negotiation** | Terms being discussed | Verbal commit, legal/procurement started | 75% |
| **Closed Won** | Contract signed | ✅ Revenue recognized | 100% |
| **Closed Lost** | Deal lost | Reason documented, next steps noted | 0% |

**Stage Hygiene Rules:**
- No deal stays in a stage for more than 2x the average time for that stage
- Every deal must have a next step with a date
- If a deal has no activity for 14 days → flag for review
- Update stages based on BUYER actions, not your actions (you sending a proposal ≠ Proposal stage; them REVIEWING it does)

### Weekly Pipeline Review Template

```yaml
pipeline_review:
  date: "[YYYY-MM-DD]"
  
  summary:
    total_pipeline: "$[X]"
    weighted_pipeline: "$[X]"
    new_this_week: [X deals, $Y]
    advanced_this_week: [X deals moved forward]
    closed_won: [X deals, $Y]
    closed_lost: [X deals, $Y — reasons]
    slipped: [X deals pushed from this month]
    
  deals_to_review:  # Top 10 by size
    - company: "[Name]"
      value: "$[X]"
      stage: "[Stage]"
      age_in_stage: "[X days]"
      next_step: "[Action]"
      risk: "[red/yellow/green]"
      risk_reason: "[Why]"
      
  actions:
    - "[Deal]: [Specific action to take this week]"
    
  pipeline_health:
    coverage_ratio: "[X]x"  # Pipeline / Quota — target 3-4x
    avg_deal_size: "$[X]"
    avg_sales_cycle: "[X days]"
    win_rate: "[X%]"
    stage_conversion:
      discovery_to_eval: "[X%]"
      eval_to_proposal: "[X%]"
      proposal_to_closed: "[X%]"
```

### Forecast Categories

| Category | Definition | Rules |
|----------|-----------|-------|
| **Commit** | WILL close this period | Verbal yes, contract in legal, no blockers |
| **Best Case** | High probability this period | Champion pushing, decision process active, some risk |
| **Pipeline** | Could close this period, needs work | In evaluation, not yet at proposal stage |
| **Upside** | Unlikely this period but possible | Early stage, right ICP, uncertain timeline |

**Forecast Accuracy Rule:** Your commit number should be within 10% of actual. If it's consistently off, your qualification is broken.

---

## Phase 8: Deal Acceleration Tactics

### When Deals Stall — Diagnostic Checklist

```
Deal is stalled. Ask yourself:

1. [ ] Do I have a champion? (If no → find one or walk away)
2. [ ] Have I talked to the economic buyer? (If no → get access)
3. [ ] Is there a compelling event / deadline? (If no → create urgency)
4. [ ] Do they understand the cost of doing nothing? (If no → quantify it)
5. [ ] Are there unresolved objections? (If yes → LAER them)
6. [ ] Is there a competitor blocking? (If yes → differentiate or reframe)
7. [ ] Is my champion still engaged? (If no → re-engage with new value)
8. [ ] Have I multi-threaded? (If no → engage other stakeholders)
```

### Multi-Threading Strategy

**Rule:** Never have just one contact in a deal. If your champion leaves, gets sick, or goes on vacation — your deal dies.

**Minimum contacts by deal size:**
- <$25K ACV → 2 contacts (champion + economic buyer)
- $25K-$100K → 3-4 contacts (champion, economic buyer, technical evaluator, end user)
- $100K+ → 5+ contacts (add: procurement, legal, executive sponsor)

### Urgency Creation (Ethical)

| Technique | How | When to Use |
|-----------|-----|-------------|
| **Cost of delay** | "Every month this isn't solved costs you $[X]. That's $[3X] by Q[next]." | When they have no timeline |
| **Capacity constraint** | "We're onboarding 3 clients this quarter. After that, next slot is [date]." | When true (never lie) |
| **Price timeline** | "Current pricing is locked through [date]." | When price changes are planned |
| **Competitive risk** | "Your competitor [name] just signed with us." | When true and relevant |
| **Regulatory deadline** | "[Regulation] takes effect [date]. You need [X weeks] to implement." | When compliance is a factor |

---

## Phase 9: Post-Sale & Expansion

### Handoff to Customer Success

```yaml
deal_handoff:
  company: "[Name]"
  closed_date: "[Date]"
  contract_value: "$[X] / [term]"
  
  key_contacts:
    - name: "[Champion]"
      role: "[Title]"
      communication_preference: "[email/slack/phone]"
      personality: "[detail-oriented/big picture/hands-on]"
      
    - name: "[Executive Sponsor]"
      role: "[Title]"
      engagement_level: "[high/medium/low]"
      success_metrics: "[What they told you success looks like]"
      
  context:
    pain_points_solved: "[List from discovery]"
    promised_outcomes: "[Specific commitments made during sales]"
    known_risks: "[Anything that could cause churn]"
    expansion_opportunity: "[What else they could buy]"
    competitor_considered: "[Who else they evaluated and why they chose you]"
    
  implementation:
    priority_use_cases: "[What to set up first]"
    technical_requirements: "[Integrations, SSO, data migration]"
    timeline_expectations: "[What you committed to]"
    
  DO_NOT:
    - "[Any sensitive topics to avoid]"
    - "[Things that were contentious during sales]"
```

### Expansion Revenue Playbook

**When to upsell (signals):**
- Usage hits >80% of their current tier/limit
- They ask about features in higher tiers
- New team/department asks to join
- They hit a milestone (growing headcount, new market)
- Renewal is 90 days away (bundle expansion with renewal)

**Expansion conversation:**
```
"I noticed [specific usage signal]. That usually means [outcome they care about] 
is going well. 

Other companies at your stage typically [expand to X / add Y] to [benefit].
Would it make sense to explore that?"
```

**Never upsell:**
- When they have unresolved support issues
- During the first 60 days
- When they're at risk of churning
- Without data showing they'll get value from the expansion

---

## Phase 10: Metrics & Self-Improvement

### Activity Metrics (Leading Indicators)

| Metric | Target | Why It Matters |
|--------|--------|---------------|
| Outbound emails/day | 30-50 | Pipeline generation |
| Calls/day | 15-25 | Pipeline generation |
| Meetings booked/week | 8-12 | Pipeline conversion |
| Discovery calls/week | 5-8 | Qualified pipeline |
| Demos/week | 3-5 | Active evaluation |
| Proposals sent/week | 2-3 | Close to money |

### Outcome Metrics (Lagging Indicators)

| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| Win rate | Won / (Won + Lost) | 20-35% |
| Avg deal size | Total revenue / Deals closed | Trending up |
| Sales cycle | Avg days from first touch to close | Trending down |
| Pipeline coverage | Open pipeline / Quota | 3-4x |
| Activity-to-meeting ratio | Meetings / (Emails + Calls) | >5% |
| Meeting-to-opportunity ratio | Opportunities / Meetings | >50% |
| Forecast accuracy | Actual / Committed | >90% |

### Win/Loss Analysis Template

```yaml
deal_analysis:
  company: "[Name]"
  outcome: "[Won/Lost]"
  value: "$[X]"
  cycle_length: "[X days]"
  
  won_because:  # or lost_because
    - "[Primary reason]"
    - "[Secondary reason]"
    
  competitor: "[Who they went with / considered]"
  
  what_worked:
    - "[Specific thing that moved the deal forward]"
    
  what_didnt:
    - "[Specific mistake or gap]"
    
  lesson:
    - "[What to do differently next time]"
    
  process_score:  # Self-assessment
    prospecting: [1-5]
    discovery: [1-5]
    demo: [1-5]
    objection_handling: [1-5]
    closing: [1-5]
    relationship: [1-5]
```

### Monthly Self-Review Questions

1. What's my win rate trend? (Improving, flat, declining)
2. Where do deals die most? (Which stage has the biggest drop-off)
3. Am I talking to the right people? (Economic buyer access rate)
4. Are my deals getting bigger or smaller?
5. What objection am I weakest at handling?
6. Which outreach channel converts best for me?
7. Am I spending time on the right deals? (80/20 — are 80% of results from 20% of deals?)
8. What did I learn from my last 3 losses?

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Build my ICP" | Walk through ICP definition template |
| "Write outreach for [company]" | Generate personalized multi-channel sequence |
| "Prep me for discovery with [company]" | Build discovery question set based on what you know |
| "Qualify this deal" | Run MEDDPICC assessment with scoring |
| "Help me handle [objection]" | Pull relevant playbook + practice response |
| "Review my pipeline" | Generate weekly pipeline review |
| "Why am I losing deals?" | Run win/loss analysis on recent losses |
| "Forecast this quarter" | Categorize deals into commit/best case/pipeline/upside |
| "Prep a proposal for [company]" | Generate proposal based on discovery notes |
| "Write a follow-up after [meeting type]" | Generate appropriate follow-up email |
| "Coach me on [call recording/notes]" | Analyze a sales conversation and give feedback |
| "How do I close [company]?" | Assess deal state and recommend closing strategy |
