# Business Strategy Frameworks

## Your Job Here

Every product decision has a strategic dimension. When you prioritize a feature, you're making a bet on what will differentiate you. When you set pricing, you're signaling market position. When you choose what not to build, you're making a moat choice. MBA-level strategy frameworks give you the language and structure to think through these bets deliberately rather than implicitly.

This file covers three layers: universal strategy (applies to all products), B2B-specific, and consumer-specific.

---

## Universal Strategy

### Porter's Five Forces — Applied to Product Decisions

Use this to assess the competitive environment and understand where you have leverage.

| Force | What it measures | PM implication |
|-------|-----------------|---------------|
| **Supplier power** | How much your inputs can be controlled by others | APIs, platforms, infrastructure providers you depend on. If Stripe raises prices or OpenAI changes API terms, what happens to your product and unit economics? |
| **Buyer power** | How much leverage customers have over you | Enterprise buyers with 12-month contract cycles have more power than individual consumers. Higher buyer power = more pressure on pricing and feature requests. |
| **Threat of substitutes** | Can users solve the problem a completely different way? | The real competition is often "just use Excel" or "hire someone" — not your direct competitors. If substitutes are strong, you must be dramatically better, not incrementally better. |
| **Threat of new entrants** | How easy is it for new players to enter? | Low barriers = you need to build a moat fast. High barriers = you have more time but shouldn't be complacent. |
| **Competitive rivalry** | How intense is direct competition? | Intense rivalry compresses margins and accelerates feature races. Use this to decide whether to differentiate or compete on execution. |

**Ask for every major product decision**: which of these forces does this decision address? Does it strengthen or weaken our position on any force?

---

### Strategic Positioning: You Can Only Be One Thing Well

The three generic strategies (Porter):

| Position | What it means | Product implications |
|----------|--------------|---------------------|
| **Cost leader** | Cheapest option that does the job | Minimize features, maximize reliability, optimize unit economics obsessively |
| **Differentiator** | Better in ways users will pay more for | Every feature decision must ask: does this increase perceived differentiation? Cutting quality to reduce cost is a strategic error. |
| **Niche / Focus** | Best for a specific segment, not everyone | Deep specificity beats broad mediocrity. Resist the pressure to generalize. |

**The trap**: trying to be all three. A product that tries to be cheap AND premium AND everything to everyone is none of those things. Know which one you are, and be consistent.

**If you're a differentiator**: the roadmap should systematically build and deepen the moat. Features that reduce switching costs or add data advantages are strategic. Features that are table stakes for the category are just maintenance.

---

### Moat Analysis

For every significant feature decision, ask: **does this increase or decrease how sticky the product is?**

| Moat type | How it works | Product signal |
|-----------|-------------|---------------|
| **Switching costs** | It becomes painful for users to leave | Deep integrations, proprietary data formats, workflows that depend on your specific product |
| **Network effects** | More users = more value for all users | Does this feature get more useful as we add more users? |
| **Data advantage** | Your data gets better than competitors over time | Does this feature generate data that makes our product smarter? |
| **Brand trust** | Users choose you because they trust you | Does this feature reinforce our credibility, or does it create a trust risk? |
| **Workflow lock-in** | Your product becomes embedded in daily operations | Does this feature create a new daily habit that makes the product indispensable? |

A feature that adds moat is worth more than its direct user value suggests. A feature that reduces moat (e.g., makes data portable in a way that makes it trivially easy to leave) should be questioned even if users ask for it.

---

### Build vs. Buy vs. Partner

When a capability is needed, your default is not always "build it." Use this framework:

| Option | When to choose it | Risk |
|--------|------------------|------|
| **Build** | Core differentiator, requires deep customization, no adequate external option | Engineering cost, time, maintenance burden forever |
| **Buy / License** | Commodity capability, available externally at reasonable cost, not a differentiator | Vendor dependency, integration complexity, ongoing cost |
| **Partner** | Both sides have something the other needs, neither should own it outright | Alignment risk, slower execution, splitting value |

**The trap**: building everything because "we can do it better." Ask whether users actually want you to be better at this, or whether they just need it to work. Authentication, payments, notifications, and email delivery are almost always buy/partner decisions.

**The other trap**: buying/partnering for core differentiators because it's faster. If the capability is what makes you better than competitors, you need to own it.

---

### Ansoff Matrix: Risk Profile of Each Roadmap Item

Every roadmap item lives in one of four quadrants. Knowing which one helps calibrate the right level of investment and risk management.

| | Existing product | New product |
|---|---|---|
| **Existing market** | Market penetration (lower risk) | Product development (medium risk) |
| **New market** | Market development (medium risk) | Diversification (highest risk) |

- **Market penetration**: improving the existing product for existing users. Most of your roadmap should live here.
- **Product development**: new features/products for your existing users. Good expansion path; users are known.
- **Market development**: taking your existing product to a new customer segment. Requires understanding new user needs.
- **Diversification**: new product for new users. Highest risk. Should be rare and require strong strategic justification.

**Red flag**: if the roadmap is full of diversification bets without strong penetration performance, the company is avoiding the hard work of making the core product better.

---

## B2B-Specific Strategy

### Enterprise Sales Dynamics — How They Affect PM Work

In B2B, the person who uses your product and the person who buys it are often different people. The PM must understand all three buyer types:

| Role | Who they are | What they need from your product |
|------|-------------|--------------------------------|
| **Champion** | The person inside the company who wants to buy | Proof that this solves their problem, ammunition to sell internally |
| **Economic buyer** | The person who controls budget and signs the contract | ROI, risk reduction, vendor stability |
| **Technical buyer** | IT, security, infrastructure | Compliance, integrations, security certifications, uptime SLAs |

**PM implication**: your roadmap needs items in all three categories, not just features for the end user. Security certifications, admin dashboards, SSO, and audit logs are not glamorous, but they unblock the technical buyer. ROI calculators and case studies help the economic buyer. Deep workflow features help the champion.

**Features that close deals vs. features that retain accounts**: these are different. Landing a deal often requires table-stakes features competitors already have. Retaining and expanding accounts requires deep workflow integration and switching costs. Know which category each roadmap item is in.

---

### Land and Expand

In a land-and-expand model, the initial sale is a foothold — not the goal. The economics depend on expansion revenue.

**Land features**: minimum viable product to win the initial contract. Focus on solving the core problem well for one team or use case.

**Expand features**: what gets more teams, departments, or seats onto the platform. Often driven by: collaboration features (bringing in colleagues), administrative features (making the platform manageable at scale), integrations (connecting to the rest of the company's stack).

**PM decision rule**: when evaluating a feature request, ask whether it helps land, expand, or neither. "Neither" features compete for roadmap space with both and rarely win.

**NRR (Net Revenue Retention) as a PM metric**: if your NRR is below 100%, your product is contracting with existing customers — that's a product failure signal, not just a sales signal. PM owns this number alongside customer success.

---

### Contract Economics — When to Say Yes to Custom Work

Enterprise customers will request custom features. Most should be declined. The framework:

**Say yes when:**
- The requirement is shared by multiple enterprise customers (builds product surface that has broad value)
- It's in a strategic category (security, compliance, admin) that you need to build anyway
- The customer is large enough that their ARR justifies the engineering investment explicitly

**Say no when:**
- It's specific to one customer's internal process
- It creates technical debt or branching logic that makes the product harder to maintain
- You'd have to maintain a separate version or configuration for this customer forever
- Saying yes sets a precedent that will attract more custom requests from other customers

When you say no to a custom request: be direct and explain why. "We've decided not to build this because [reason]. Here's what we are building that will address the underlying need."

---

## Consumer-Specific Strategy

### Network Effects — Build Toward Them Deliberately

Network effects are the most powerful moat in consumer products, but they must be designed in.

| Type | How it works | Product examples |
|------|-------------|-----------------|
| **Direct** | More users → more value for each user | Messaging apps, social networks |
| **Indirect** | More users on one side → more value for the other side | Marketplace (more sellers → better for buyers) |
| **Data** | More usage → better product for everyone | Recommendations, search, fraud detection |

**PM questions for every major consumer feature:**
- Does this feature create a reason for users to invite others?
- Does this feature become more valuable as more users adopt it?
- Does this feature generate data that improves the experience for everyone?

If the answer to all three is no, the feature doesn't advance the network effect moat. That doesn't mean you shouldn't build it, but you should know the moat isn't being served.

---

### Growth Loops — Map Yours and Find Where It Leaks

A growth loop is a compounding mechanism where one user action leads to more users. Unlike linear funnels, loops compound over time.

**Common loop types:**

- **Viral loop**: User does X → user invites others → new users join and do X → they invite others
- **Content loop**: User creates content → content gets indexed → new users discover via search → they create more content
- **Paid loop**: Revenue → paid acquisition → new users → more revenue
- **Word-of-mouth loop**: User has a great experience → tells others → others join → have great experiences → tell others

**How to find where your loop leaks:**
1. Map your loop explicitly: where does each step hand off to the next?
2. Measure each handoff: what % of users at step N reach step N+1?
3. The lowest-converting handoff is where you invest first.

**PM implication**: features that accelerate loop velocity (speed up the cycle) or improve conversion at bottleneck steps have compounding impact over time. Prioritize them above linear-value features when the loop is the growth engine.

---

### Hook Model — Evaluating Whether Features Build Habits

The Hook Model (Nir Eyal) gives PMs a framework for designing habit-forming products:

| Stage | What it is | Product design question |
|-------|-----------|------------------------|
| **Trigger** | What prompts users to open the product | Is the trigger internal (emotion/habit) or external (notification)? External triggers are weaker long-term. |
| **Action** | The simplest behavior to get a variable reward | How easy is the action? Reduce friction here. |
| **Variable reward** | Unpredictable positive outcome | Is the reward variable enough to be compelling? Predictable rewards lose pull. |
| **Investment** | User puts something in that makes the product better for them | Does the user store something (data, relationships, content) that would be lost if they left? |

**PM use**: evaluate any proposed feature against the Hook Model. Does it reduce friction on the action? Does it increase investment? Features that increase investment increase retention and switching costs simultaneously.

---

### Consumer Unit Economics: Do Them by Cohort

Aggregate LTV/CAC is almost always misleading. Users acquired 2 years ago behave differently from users acquired last month.

**What to track by acquisition cohort:**
- D1, D7, D30, D90 retention curves — does this cohort retain at the same rate as prior cohorts?
- Time to first value (activation metric) — is it improving or degrading for recent cohorts?
- Revenue per user at 3, 6, 12 months — are newer cohorts monetizing at similar rates?

**Red flags in cohort analysis:**
- Retention curves are declining across cohorts (your product is getting relatively less sticky)
- D1 retention is fine but D30 drops faster in recent cohorts (activation improved but core value didn't)
- Revenue per user is declining in recent cohorts (you're attracting lower-value users)

**PM implication**: cohort degradation is a product problem. It means something about how users experience the product is getting worse over time, even if aggregate numbers look fine because old cohorts are propping them up.

---

### Consumer Pricing Strategy

| Approach | How it works | When to use |
|----------|-------------|------------|
| **Freemium** | Free tier + paid upgrade | When the free tier genuinely delivers value and creates upgrade motivation; requires strong conversion funnel from free to paid |
| **Free trial** | Full product, time-limited | When the full product value is obvious quickly; requires fast time-to-value |
| **Usage-based** | Pay for what you use | When value is directly proportional to usage; aligns cost with value but creates revenue unpredictability |
| **Subscription** | Fixed recurring fee | Predictable revenue; works when users have consistent ongoing value from the product |

**Willingness-to-pay research methods:**
- **Van Westendorp Price Sensitivity Meter**: ask users "at what price would this be too cheap?" / "too expensive?" / "expensive but acceptable?" / "good value?" — generates a range and optimal price point
- **Conjoint analysis**: present users with different feature/price combinations and measure preferences — reveals which features justify higher prices
- **Direct ask + discount test**: quote price, measure drop-off, offer discount and measure take-up — reveals price elasticity

---

## Financial Impact of PM Decisions

Every major roadmap decision has a financial model attached to it, even if nobody has made it explicit. You should be able to sketch the P&L impact of any significant choice:

```
Feature / Initiative: [name]

Revenue impact:
- Enables / protects: [what revenue does this defend or unlock?]
- Estimated value: [rough ARR or LTV impact]
- Time to realize: [when would we see this in the numbers?]

Cost:
- Engineering effort: [person-weeks]
- Opportunity cost: [what are we not building instead?]
- Ongoing maintenance: [is this a one-time or recurring cost?]

Strategic value (non-financial):
- Moat impact: [does this increase switching costs, network effects, data advantage?]
- Competitive response: [does not building this give a competitor an opening?]

Directional ROI: [positive / neutral / negative — and why]
```

**ROI framing for leadership**: when presenting a roadmap choice, give a directional ROI estimate. Even rough numbers are more useful than no financial framing. "This feature unlocks an estimated $500K in ARR from deals currently blocked by this gap" is a different conversation than "this feature is important."
