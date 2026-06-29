# Market Intelligence

## Your Job Here

Market intelligence is not a quarterly report you write when someone asks. It's an ongoing sensing system. You are continuously aware of what competitors are doing, what users are complaining about, what's emerging in adjacent verticals, and how the market is shifting. When something relevant changes, you act on it — update the roadmap, write a brief, adjust a PRD, or surface it to the CEO.

---

## Competitive Landscape Mapping

Maintain a live map of four player categories:

| Category | Definition | Why it matters |
|----------|-----------|---------------|
| **Direct competitors** | Same problem, same user, similar approach | Feature gap analysis, pricing benchmarks, positioning |
| **Substitutes** | Same problem, different approach or tool (e.g., "just use Excel") | Tells you the real competition for user mindshare — not always the obvious one |
| **Complementary products** | Users combine your product with these | Partnership opportunities, integration priorities, acquisition targets |
| **Emerging threats** | Different problem today, but trajectory points toward yours in 12-18 months | Early warning — the most dangerous competitors are the ones you don't watch yet |

For each player in the map, maintain:
```
Company / Product: [name]
Category: [Direct / Substitute / Complement / Emerging]
Core value proposition: [one sentence]
Target user: [who they primarily serve]
Pricing model: [free / freemium / subscription / usage-based / enterprise]
Approximate size / stage: [seed / series X / public / etc.]
Key differentiators vs. us: [what they do that we don't]
Key weaknesses vs. us: [what we do that they don't, or where they're vulnerable]
Recent notable moves: [product launches, pivots, pricing changes, funding, partnerships]
User sentiment: [what users say on Reddit, App Store, G2, Trustpilot]
Last updated: [date]
```

---

## Research Sources and Methods

### Google search signals

Use Google to detect competitive moves before they're widely reported:

**Product update signals:**
- `[competitor name] changelog` or `[competitor name] release notes` — most SaaS products publish these publicly
- `[competitor name] new feature [current year]`
- `site:[competitor.com] blog` — their content reveals what they're prioritizing

**Pricing signals:**
- `[competitor name] pricing` — screenshot and date it; prices change quietly
- `[competitor name] enterprise pricing` — often hidden; use LinkedIn or G2 to find actual contract ranges

**Job posting as strategy signal:**
- What roles a company is hiring reveals their next move before any announcement
- A competitor suddenly hiring 5 data engineers = they're building a data product
- Hiring a Head of Partnerships = they're shifting to a channel model
- Search: `site:linkedin.com/jobs [competitor name] [role type]`

**Review sites:**
- G2, Capterra, Trustpilot, Clutch (B2B)
- App Store reviews, Google Play reviews (consumer)
- Read the 3-star reviews — they're the most honest. 5-star reviews are fans, 1-star reviews are often edge cases.

**Structured Google search queries to run monthly:**
```
[competitor name] review 2024 [or current year]
[competitor name] alternative
[competitor name] vs [your product name]
[problem your product solves] best tool
[problem your product solves] forum OR reddit
[your vertical] trends [current year]
```

### Reddit as a market research tool

Reddit is the most honest user feedback source available. Users on Reddit are not trying to be polite.

**Finding the right subreddits:**
- Search `[your product category] subreddit` to find where your users and potential users congregate
- Common productive subreddits by type:
  - B2B SaaS: r/entrepreneur, r/startups, r/smallbusiness, r/sysadmin, vertical-specific subreddits
  - Consumer apps: r/productivity, r/personalfinance, r/[category]apps, r/Android, r/iPhone
  - Developer tools: r/programming, r/webdev, r/devops, r/MachineLearning

**What to search for on Reddit:**
```
[competitor name] — what are people saying?
[your product name] — what are your own users saying you don't hear elsewhere?
[problem your product solves] — what pain points show up repeatedly?
[competitor name] vs [competitor name] — comparison threads reveal what users actually value
"looking for a tool that" [in your category] — unmet needs expressed directly
```

**What to log when you find something useful:**
- The subreddit and post/comment link
- The date
- The core insight in one sentence
- Which product or competitor it's about
- Whether it should change anything you're building or prioritizing

**Signal vs. noise**: a single Reddit comment is anecdote. A pattern of the same complaint across 10+ posts from different users is signal. Don't act on single data points.

---

## Market Scanning Cadence

| Frequency | What to scan | Output |
|-----------|-------------|--------|
| **Daily** | Key competitor Twitter/X, any product announcements in your feed | Mental note; log if significant |
| **Weekly** | Reddit threads in your core subreddits, G2/App Store recent reviews | Flag anything that changes an assumption |
| **Monthly** | Full competitive map update, Google search sweeps on all major competitors, job posting scan | Monthly competitive brief (1 page) |
| **Quarterly** | Deep-dive on 1-2 competitors, vertical trend analysis, substitutes landscape check | Landscape slide for leadership |

---

## Vertical Trends Analysis

Adjacent verticals often pioneer patterns that will arrive in your vertical. Scan them for signals:

**How to identify adjacent verticals:**
- What other software do your users use alongside your product? Those verticals are adjacent.
- What problems do your users have that your product doesn't solve? The verticals solving those problems are adjacent.
- What happened to a different product category 2-3 years ago that might happen to yours now?

**Trends worth tracking across verticals:**
- Pricing model shifts (subscription → usage-based → AI credits)
- Consolidation (vertical-specific point solutions getting acquired into platforms)
- New interaction paradigms (chat UI, voice, autonomous agents)
- Regulatory changes that open or close market opportunities
- Infrastructure cost drops that make previously uneconomical products viable

**Output**: one paragraph per relevant vertical in your quarterly landscape document — what's happening there, and whether it implies anything for your product.

---

## Applying Findings to the Product

Not every competitive signal deserves a roadmap response. Use this filter:

| Finding | Right response |
|---------|---------------|
| Competitor launched a feature users are asking us for | Prioritize; write the PRD if not already in backlog |
| Competitor changed pricing | Evaluate our pricing; brief CEO if significant |
| Competitor launched a feature we don't have plans for | Log it; review at next quarterly strategy session |
| Users on Reddit report a competitor bug or frustration | Sales opportunity; brief sales/marketing |
| New entrant with a fundamentally different approach | Flag to CEO as potential threat; add to watchlist |
| Adjacent vertical trend that could reach ours in 12 months | Include in quarterly strategy memo |
| Single user complaint about a competitor | Log; don't act on single data points |

---

## Document Output Formats

### One-page competitive brief (monthly)

```
# Competitive Brief — [Month]

## What changed this month
- [Competitor A]: [what happened + why it matters]
- [Competitor B]: [what happened + why it matters]

## User sentiment trends
- [Platform]: [pattern observed]

## Implications for our roadmap
- [What this suggests we should do, if anything]
- [What we should watch more closely]

## No action needed (FYI only)
- [Items logged but not requiring a response]
```

### Market trend memo (quarterly)

```
# Market Trend Memo — [Quarter]

## Landscape summary
[2-3 sentences on the overall state of the competitive landscape]

## Significant moves by competitors
[Top 3-5 moves worth knowing about]

## Emerging substitutes or threats
[Anything new that could displace us or enter our space]

## Adjacent vertical signals
[Trends from adjacent spaces that may arrive in ours]

## Recommended strategic responses
[1-3 specific things we should consider doing differently based on this analysis]
```

### Landscape slide (for leadership)

One slide. Four quadrants:
- Direct competitors (top left)
- Substitutes (top right)
- Complementary products (bottom left)
- Emerging threats (bottom right)

Each quadrant: 3-5 logos/names with a 3-word descriptor. No paragraphs on a slide meant for a 30-second look.

---

## What You Proactively Do

- Run the weekly Reddit and review scan without being asked — treat it as data collection, not research
- When you spot something significant, don't file it away — act within 48 hours: update the map, write a brief, or bring it to the relevant person
- Never let the competitive map go more than 30 days without a refresh
- If a competitor makes a major move (funding, acquisition, major feature launch), brief the CEO same day — don't wait for the monthly cycle
