---
name: afrexai-lead-hunter
description: "Enterprise-grade B2B lead generation, enrichment, scoring, and outreach sequencing for AI agents. Find ideal prospects, enrich with verified data, score against your ICP, and generate personalized outreach — all autonomously."
tags: [leads, sales, b2b, prospecting, enrichment, outreach, pipeline, crm, cold-email, icp]
author: AfrexAI
version: 1.0.0
license: MIT
---

# AfrexAI Lead Hunter Pro

> Turn your AI agent into a full B2B sales development machine. Discovery → Enrichment → Scoring → Outreach → CRM. Zero manual work.

---

## Architecture

```
DEFINE ICP ──▶ DISCOVER ──▶ ENRICH ──▶ SCORE ──▶ SEGMENT ──▶ OUTREACH ──▶ CRM
    │              │            │          │          │            │          │
    ▼              ▼            ▼          ▼          ▼            ▼          ▼
 Persona      Multi-source  Email+Phone  ICP fit   Tier A/B/C  Sequences  Pipeline
 Builder      Web Research  Company Data  Intent    Campaigns   Templates  Tracking
```

---

## Phase 1: Define Your Ideal Customer Profile (ICP)

Before hunting, know WHO you're hunting. Answer these:

### Company-Level ICP
```yaml
# Copy and customize this ICP template
company:
  industries: [SaaS, fintech, legal-tech, prop-tech]
  employee_range: [50, 500]        # sweet spot for AI adoption
  revenue_range: [$5M, $100M]      # can afford $120K+ contracts
  funding_stage: [Series A, Series B, Series C]
  tech_signals:                     # tools that indicate AI readiness
    positive: [Salesforce, HubSpot, Snowflake, AWS, Python]
    negative: [no-website, wordpress-only]
  geography: [US, UK, Canada, Australia]
  pain_signals:                     # problems they're likely facing
    - "manual data entry"
    - "compliance overhead"
    - "scaling operations"
    - "document processing"
```

### Buyer Persona
```yaml
persona:
  titles: [CEO, CTO, COO, VP Operations, Head of Innovation, Director of IT]
  seniority: [C-Suite, VP, Director]
  decision_authority: true          # can sign $50K+ without board approval
  linkedin_activity:                # signals they're actively looking
    - posts about AI/automation
    - comments on digital transformation content
    - recently changed roles (first 90 days = buying window)
  anti-signals:                     # skip these
    - "consultant" in title (not buyers)
    - company < 10 employees (no budget)
    - already has AI vendor (check for competitors in their stack)
```

### Scoring Weights
```yaml
scoring:
  icp_company_match: 30             # how well company matches
  icp_persona_match: 20             # right title + seniority
  intent_signals: 25                # actively looking for solutions
  engagement_recency: 15            # recent activity online
  timing_bonus: 10                  # new role, funding round, hiring
  
  thresholds:
    tier_a: 80                      # hot — outreach immediately
    tier_b: 60                      # warm — nurture sequence
    tier_c: 40                      # cool — add to newsletter
    disqualify: below 40            # don't waste time
```

---

## Phase 2: Multi-Source Discovery

### Source Priority Matrix

| Source | Best For | How To Search | Data Quality | Cost |
|--------|----------|---------------|-------------|------|
| **Web Search** | Any industry | `"[industry] companies" site:linkedin.com/company` | High | Free |
| **GitHub** | Dev tools, tech companies | Search repos, org pages, contributor profiles | High | Free |
| **Product Hunt** | Startups, SaaS | Browse launches, upvoters (they're buyers too) | Medium | Free |
| **Industry Lists** | Targeted verticals | "Top 50 [industry] companies 2026", Clutch, G2 | High | Free |
| **Job Boards** | Hiring = growing = buying | `"AI" OR "automation" site:lever.co OR site:greenhouse.io` | High | Free |
| **Crunchbase** | Funded startups | Recently funded companies in target verticals | High | Freemium |
| **Conference Speakers** | Active industry leaders | Speaker lists from industry events | Very High | Free |
| **Podcast Guests** | Thought leaders with budget | Search "[industry] podcast" transcripts | High | Free |

### Discovery Search Templates

**Find companies by pain signal:**
```
"[industry]" "manual process" OR "time-consuming" OR "looking for solutions" site:linkedin.com
```

**Find companies by hiring signal (they're growing = they're buying):**
```
"[company type]" "hiring" "AI" OR "automation" OR "data" site:linkedin.com/jobs
```

**Find recently funded companies (flush with cash):**
```
"[industry]" "raises" OR "Series A" OR "funding" OR "investment" 2026
```

**Find companies using competitor tools (ripe for switching):**
```
"[competitor tool]" "alternative" OR "switching from" OR "replaced"
```

**Find decision makers directly:**
```
"[title]" "[industry]" "[city/region]" site:linkedin.com/in
```

### Discovery Workflow

```
FOR each search query:
  1. Run web_search with the query
  2. Extract company names + URLs from results
  3. Deduplicate against existing leads
  4. For each NEW company:
     a. Visit company website → extract: industry, size estimate, tech signals
     b. Search "[company name] CEO" OR "[company name] founder" → get decision maker
     c. Search "[company name] funding" → get financial signals
     d. Create lead record (see schema below)
  5. Rate limit: 2-3 second delay between searches
```

---

## Phase 3: Enrichment Engine

For each discovered lead, enrich with verified data:

### Company Enrichment Checklist
- [ ] **Website** — Load homepage, extract value prop, tech stack (check `<meta>` tags, JS frameworks)
- [ ] **Employee Count** — LinkedIn company page, Crunchbase, or website "About" page
- [ ] **Revenue Estimate** — Funding amount × 3-5x multiplier, or industry benchmarks
- [ ] **Tech Stack** — Check BuiltWith, Wappalyzer data, or job postings for tech mentions
- [ ] **Recent News** — Last 90 days: funding, launches, executive changes, partnerships
- [ ] **Pain Indicators** — Job postings mentioning problems you solve, blog posts about challenges
- [ ] **Competitor Usage** — Do they use a competitor? Which one? (Check G2 reviews, case studies)

### Contact Enrichment Checklist
- [ ] **Full Name** — First + Last from LinkedIn or company page
- [ ] **Title** — Current role (verify it matches your buyer persona)
- [ ] **Email Pattern** — Determine company pattern: first@, first.last@, firstlast@, f.last@
- [ ] **Email Verification** — Test pattern with known format, check MX records
- [ ] **LinkedIn URL** — Direct profile link
- [ ] **Recent Activity** — What have they posted/shared in last 30 days?
- [ ] **Mutual Connections** — Anyone in your network connected to them?
- [ ] **Content Interests** — What topics do they engage with? (Use for personalization)

### Email Pattern Detection
```
Common patterns (test in order of likelihood):
1. first.last@company.com     (most common, ~40%)
2. first@company.com          (startups, ~25%)
3. firstlast@company.com      (~15%)
4. flast@company.com           (~10%)
5. first_last@company.com     (~5%)
6. last.first@company.com     (~3%)
7. first.l@company.com        (~2%)

Verification approach:
- Check if company has public team page with email format
- Look for email in GitHub commits from company domain
- Check email format on Hunter.io or similar (if available)
- Search "[person name] email [company]" 
- Check their personal website/blog for contact
```

---

## Phase 4: Lead Scoring Algorithm

Score each lead 0-100 using this rubric:

### Company Score (0-30 points)

| Signal | Points | How to Check |
|--------|--------|-------------|
| Industry matches ICP exactly | +10 | Compare to ICP config |
| Employee count in sweet spot | +5 | LinkedIn/website |
| Revenue in target range | +5 | Crunchbase/estimate |
| Located in target geography | +3 | Website/LinkedIn |
| Uses compatible tech stack | +4 | Job posts, BuiltWith |
| No competitor currently | +3 | Research, case studies |

### Persona Score (0-20 points)

| Signal | Points | How to Check |
|--------|--------|-------------|
| Title matches buyer persona | +8 | LinkedIn |
| C-Suite or VP level | +5 | LinkedIn |
| Has decision authority | +4 | Title + company size |
| Active on LinkedIn (posts monthly) | +3 | LinkedIn activity |

### Intent Score (0-25 points)

| Signal | Points | How to Check |
|--------|--------|-------------|
| Recently posted about relevant pain | +8 | LinkedIn/Twitter |
| Company hiring for roles you'd replace | +7 | Job boards |
| Attended relevant industry event | +5 | Conference lists |
| Downloaded competitor content | +3 | Hard to verify, skip if unknown |
| Searched for solution keywords | +2 | Hard to verify, skip if unknown |

### Timing Score (0-15 points)

| Signal | Points | How to Check |
|--------|--------|-------------|
| New in role (< 90 days) | +5 | LinkedIn start date |
| Company just raised funding | +4 | Crunchbase/news |
| End of quarter (budget flush) | +3 | Calendar |
| Company growing fast (hiring surge) | +3 | Job postings count |

### Engagement Score (0-10 points)

| Signal | Points | How to Check |
|--------|--------|-------------|
| Opened previous email | +4 | Email tracking |
| Visited your website | +3 | Analytics |
| Connected on LinkedIn | +2 | LinkedIn |
| Referred by someone | +1 | CRM notes |

---

## Phase 5: Segmentation & Campaign Assignment

### Tier A (Score 80-100) — HOT LEADS
```
Action: Immediate personalized outreach
Sequence: 5-touch hyper-personalized campaign
Timeline: Contact within 24 hours
Channel: Email → LinkedIn → Phone (if available)
Template: "CEO-to-CEO" or "Specific Pain" (see below)
```

### Tier B (Score 60-79) — WARM LEADS
```
Action: Nurture sequence
Sequence: 7-touch value-first campaign  
Timeline: Start within 48 hours
Channel: Email → LinkedIn
Template: "Value Insight" or "Case Study" (see below)
```

### Tier C (Score 40-59) — COOL LEADS
```
Action: Add to newsletter + long-term nurture
Sequence: Monthly value content
Timeline: Bi-weekly touchpoints
Channel: Email only
Template: "Industry Report" or "Educational" (see below)
```

---

## Phase 6: Outreach Sequence Templates

### Template 1: The Specific Pain (Tier A)

**Email 1 — Day 0 (The Hook)**
```
Subject: [specific pain point] at [Company]?

Hi [First Name],

Noticed [Company] is [specific observation — hiring for X role / posted about Y challenge / using Z tool].

That usually means [pain point they're likely feeling].

We built [solution] that [specific result with number]. [Client name] cut their [metric] by [X%] in [timeframe].

Worth a 15-min call to see if it fits [Company]?

[Your name]
```

**Email 2 — Day 3 (The Proof)**
```
Subject: Re: [original subject]

[First Name] — quick follow-up.

Here's exactly what we did for [similar company]: [1-sentence case study with specific numbers].

[Link to case study or calculator]

Happy to walk through how this maps to [Company].

[Your name]
```

**Email 3 — Day 7 (The Angle)**
```
Subject: [industry trend] + [Company]

[First Name],

[Industry trend or stat that's relevant]. Companies like [Company] are [what smart companies are doing about it].

We help [type of company] [specific outcome]. Takes about [timeframe] to see results.

Open to a quick chat this week?

[Your name]
```

**Email 4 — Day 14 (The Breakup)**
```
Subject: Should I close your file?

[First Name],

I've reached out a few times — totally understand if the timing isn't right.

If [pain point] becomes a priority, here's a [free resource] that might help: [link]

Either way, I'll stop filling your inbox. Just reply "yes" if you'd like to chat sometime.

[Your name]
```

### Template 2: The Value-First (Tier B)

**Email 1 — Lead with insight, not a pitch**
```
Subject: [number] [industry] companies are doing [thing] wrong

Hi [First Name],

We analyzed [X] companies in [industry] and found that [surprising insight].

The ones getting it right are [what top performers do differently].

Put together a quick breakdown: [link to free resource/calculator]

Thought it'd be useful given what [Company] is building.

[Your name]
```

### Template 3: The LinkedIn Warm-Up

**Step 1:** View their profile (creates notification)
**Step 2 (Day 2):** Like/comment on their recent post (genuine, not generic)
**Step 3 (Day 4):** Send connection request with note:
```
Hi [Name] — been following [Company]'s work in [space]. 
Particularly liked your take on [specific post topic]. 
Would love to connect.
```
**Step 4 (Day 7, after accepted):** Send value message (NOT a pitch):
```
[Name] — saw you mentioned [challenge] in your recent post. 
We put together [free resource] that addresses exactly that. 
Thought you might find it useful: [link]
```

---

## Phase 7: CRM & Pipeline Management

### Lead Record Schema
```json
{
  "id": "lead-001",
  "created": "2026-02-13",
  "source": "web-search",
  
  "company": {
    "name": "Acme Corp",
    "website": "https://acme.com",
    "industry": "SaaS",
    "employees": 150,
    "revenue_est": "$20M",
    "funding": "Series B — $15M (2025)",
    "tech_stack": ["Salesforce", "AWS", "React"],
    "location": "San Francisco, CA"
  },
  
  "contact": {
    "first_name": "Jane",
    "last_name": "Smith",
    "title": "VP of Operations",
    "email": "jane.smith@acme.com",
    "email_verified": false,
    "linkedin": "https://linkedin.com/in/janesmith",
    "phone": null
  },
  
  "scoring": {
    "company_score": 25,
    "persona_score": 18,
    "intent_score": 15,
    "timing_score": 8,
    "engagement_score": 0,
    "total": 66,
    "tier": "B"
  },
  
  "enrichment": {
    "pain_signals": ["hiring 3 data analysts", "blog about manual reporting"],
    "recent_news": ["Raised Series B in Jan 2026"],
    "competitor_usage": "None detected",
    "content_interests": ["data automation", "operational efficiency"]
  },
  
  "outreach": {
    "status": "not_started",
    "sequence": "value-first",
    "emails_sent": 0,
    "last_contacted": null,
    "next_action": "2026-02-14",
    "replies": [],
    "notes": ""
  },
  
  "pipeline": {
    "stage": "prospect",
    "deal_value": null,
    "probability": 0,
    "next_step": "Initial outreach"
  }
}
```

### Pipeline Stages
```
PROSPECT → CONTACTED → REPLIED → MEETING_BOOKED → QUALIFIED → PROPOSAL → NEGOTIATION → CLOSED_WON / CLOSED_LOST
```

### Tracking Metrics
Track these weekly to optimize your machine:
- **Discovery rate**: leads found per search session
- **Enrichment completeness**: % of fields filled per lead
- **Score distribution**: what % are Tier A vs B vs C?
- **Response rate**: replies / emails sent (target: 5-15%)
- **Meeting rate**: meetings / replies (target: 30-50%)
- **Conversion rate**: deals / meetings (target: 20-30%)
- **Pipeline velocity**: days from discovery → closed deal

---

## Phase 8: Automation & Scheduling

### Daily Autopilot Routine
```
MORNING (agent runs autonomously):
  1. Run 3-5 discovery searches (rotate queries)
  2. Enrich any un-enriched leads from yesterday
  3. Score new leads
  4. Send Day-N emails for active sequences
  5. Check for replies → flag for human review
  6. Update pipeline stages
  7. Report: "Found X leads, sent Y emails, Z replies"

WEEKLY:
  1. Review Tier C leads — any moved to B/A?
  2. Clean dead leads (no response after full sequence)
  3. Analyze response rates by template — A/B test
  4. Refresh ICP based on closed deals
  5. Add new search queries based on wins
```

### Agent Integration
```
# In your agent's heartbeat or cron:
1. Load ICP config
2. Run discovery for 1 search query
3. Enrich top 5 new leads
4. Score all unscored leads
5. Queue outreach for Tier A leads
6. Log results to daily brief
```

---

## Output Formats

### CSV Export
```csv
company,contact,title,email,linkedin,score,tier,industry,employees,pain_signal
Acme Corp,Jane Smith,VP Ops,jane@acme.com,linkedin.com/in/jane,66,B,SaaS,150,hiring analysts
```

### Weekly Report Template
```markdown
# Lead Hunter Weekly Report — Week of [DATE]

## Pipeline Summary
- Total leads in system: [N]
- New leads this week: [N]  
- Tier A: [N] | Tier B: [N] | Tier C: [N]

## Outreach Performance
- Emails sent: [N]
- Reply rate: [X%]
- Meetings booked: [N]
- Pipeline value added: $[X]

## Top Leads This Week
1. [Company] — [Contact] — Score: [X] — [Why they're hot]
2. [Company] — [Contact] — Score: [X] — [Why they're hot]
3. [Company] — [Contact] — Score: [X] — [Why they're hot]

## Insights
- Best performing search query: [query]
- Best performing email template: [template]
- Recommendation: [action to take]
```

---

## Pro Tips

1. **The 90-Day Window**: New executives are 10x more likely to buy in their first 90 days. Prioritize "new role" signals.
2. **Hiring = Buying**: If a company is hiring for the role your product replaces, they have budget AND pain. These are your hottest leads.
3. **Competitor's Customers**: Search for reviews/complaints about competitors. Unhappy customers switch fastest.
4. **Conference Lists**: Speaker and attendee lists from industry events are gold. These people are actively engaged in the space.
5. **The "Reply to Anything" Rule**: Any reply (even "not interested") is valuable. It confirms the email works and the person exists. Log it.
6. **Personalization > Volume**: 20 hyper-personalized emails outperform 200 generic ones. Always reference something specific about the prospect.
7. **Multi-Thread**: Don't rely on one contact per company. Find 2-3 decision-makers and approach from different angles.
8. **Timing Matters**: Tuesday-Thursday, 8-10 AM local time gets the best open rates. Avoid Mondays and Fridays.

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI agents that actually sell.*
