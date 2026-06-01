---
name: product-marketing-context
description: "When the user wants to create or update their product marketing context document. Also use when the user mentions 'product context,' 'service context,' 'marketing context,' 'set up context,' 'positioning,' 'who is my target audience,' 'describe my product,' 'describe my service,' 'ICP,' 'ideal customer profile,' or wants to avoid repeating foundational information across marketing tasks. Works for products, services, or hybrid offerings — B2B and B2C. Use this at the start of any new project before using other marketing skills — it creates `.agents/product-marketing-context.md` that all other skills reference for offering, audience, and positioning context."
metadata:
  version: 2.0.0
---

# Product Marketing Context

You help users create and maintain a product marketing context document. This captures foundational positioning and messaging information that other marketing skills reference, so users don't repeat themselves. Works for products, services, or hybrid offerings — B2B and B2C alike.

The document is stored at `.agents/product-marketing-context.md`.

## Workflow

### Step 1: Check for Existing Context

First, check if `.agents/product-marketing-context.md` already exists. Also check `.claude/product-marketing-context.md` for older setups — if found there but not in `.agents/`, offer to move it.

**If it exists:**
- Read it and summarize what's captured
- Ask which sections they want to update
- Only gather info for those sections

**If it doesn't exist, offer two options:**

1. **Auto-draft from codebase** (recommended): You'll study the repo—README, landing pages, marketing copy, package.json, etc.—and draft a V1 of the context document. The user then reviews, corrects, and fills gaps. This is faster than starting from scratch.

2. **Start from scratch**: Walk through each section conversationally, gathering info one section at a time.

Most users prefer option 1. After presenting the draft, ask: "What needs correcting? What's missing?"

### Step 2: Gather Information

**If auto-drafting:**
1. Read the codebase: README, landing pages, marketing copy, about pages, meta descriptions, package.json, any existing docs
2. Draft all sections based on what you find
3. Present the draft and ask what needs correcting or is missing
4. Iterate until the user is satisfied

**If starting from scratch:**
Walk through each section below conversationally, one at a time. Don't dump all questions at once.

For each section:
1. Briefly explain what you're capturing
2. Ask relevant questions using the right question format (see below)
3. Confirm accuracy
4. Move to the next

Push for verbatim customer language — exact phrases are more valuable than polished descriptions because they reflect how customers actually think and speak, which makes copy more resonant.

**Question design — reduce friction, get better answers:**
- **Select one**: When a field has known options (stage, offering type, business model), present them as a lettered list: "(a) ... (b) ... (c) ...". Faster than open-ended, and the user can still say something different.
- **Select all that apply**: When multiple values are valid (discovery channels, pain cost types), present common options as a numbered or bulleted list and ask the user to pick all that apply, plus "other." In the sections below, ☐ marks indicate the options to present — format them as a clean list for the user, not inline.
- **Finish this sentence**: When users freeze on open-ended questions, offer a fill-in-the-blank: "We help ___ do ___ so they can ___." This scaffolds without constraining.
- **Constraining prompts**: When answers tend to sprawl, add a length constraint: "In one sentence..." or "Pick your top 3."
- **Spectrum selection**: When capturing degree/preference, offer a scale: "Where do you fall? More formal ← → more casual."
- **Examples as anchors**: Show one concrete example of a good answer before asking, especially for open-ended fields. This sets the bar and unblocks the user.
- **Confirm by summarizing**: After each section, summarize what you captured in 2-3 sentences and ask: "Does this capture it? Anything to adjust?" Don't just say "confirm."
- **Stay conversational**: These patterns are tools to reach for, not a rigid form. If the user gives a rich, detailed answer unprompted, don't force them through a select-all list — capture what they said and move on. Use structured prompts when the user seems stuck, gives a vague answer, or needs help articulating what they mean.
- Don't use all patterns in every section — match the pattern to the question type. Sections below use `→ *pattern*:` annotations to indicate which pattern to use — these are instructions for you, not text to show the user.

**Important: Adapt to offering type.** Section 1 establishes whether this is a product, service, or hybrid — and whether it's B2B or B2C. Use that to guide which questions you emphasize and which you skip in all subsequent sections. Don't force product language on a service business, and don't ask B2C founders about buying committees. If the user doesn't explicitly label their offering type, infer it from their description ("we send doctors to your house" → service; "we built an app" → product; "we sell boxes and have a companion app" → hybrid) and confirm: "It sounds like this is a B2C service — is that right?"

**If the user is setting this up on behalf of someone else** (consultant, agency, new hire), ask what they know and flag sections that need input from the founder or customer-facing team. Mark those sections as "[needs founder input]" in the output.

---

## Sections to Capture

**Priority guide:** Sections 1-6 are essential — they form the core that downstream skills depend on. Sections 7-12 are high-value but can be marked "[to revisit]" if the user runs out of time or patience. Always capture 1-6 before moving to 7-12.

### 1. Offering Overview
- Company or brand name
- One-line description → *finish this sentence*: "We help ___ do ___ so they can ___."
- What it does (2-3 sentences) → *constraining prompt*: "Explain what you do as if you had 30 seconds with a stranger."
- Why it exists — the founding insight or personal experience that sparked this, and what makes the team uniquely qualified (this often becomes your most powerful marketing story)
- Category → *finish this sentence*: "When someone searches for what we do, they'd type ___." (This is the "shelf" you sit on.)
- Offering type → *select one*: (a) Product (b) Service (c) Hybrid — then give an example: "e.g., SaaS, home tutoring service, subscription box + companion app"
- Business model → *select one + details*: (a) Subscription/SaaS (b) One-time purchase (c) Freemium (d) Marketplace/commission (e) Retainer/hourly (f) Pay-per-use (g) Other — then ask for price points or tiers
- Stage → *select one*: (a) Pre-launch (b) Early traction (c) Growth (d) Established — this shapes what proof points and strategies are credible
- For services: delivery model → *select one*: (a) On-demand (b) Scheduled (c) Subscription (d) Retainer — and coverage area if relevant

### 2. Target Audience

Adapt these fields based on offering type:

**For B2B:**
- Target company type (industry, size, stage)
- Target decision-makers (roles, departments)

**For B2C:**
- Target customer segments (demographics, life stage, situation)
- Who makes the decision — often the user themselves, but not always (e.g., a family member choosing home care for a parent, a parent choosing a tutor for a child)

**For all:**
- Primary use case → *finish this sentence*: "Most customers come to us because they need to ___."
- Jobs to be done → *constraining prompt*: "Name 2-3 things customers 'hire' you to do for them."
- Specific use cases or scenarios
- How they find you → *select all that apply*:
  ☐ Google search ☐ Word-of-mouth ☐ Professional referral
  ☐ Social media ☐ Communities/forums ☐ Content/blog
  ☐ Paid ads ☐ Events/trade shows ☐ App store ☐ Other: ___
- Where they spend time → *select all + add your own* (online and offline):
  ☐ LinkedIn ☐ Facebook groups ☐ Reddit ☐ Twitter/X
  ☐ YouTube ☐ TikTok ☐ Industry forums
  ☐ Conferences/trade shows ☐ Professional associations
  ☐ Specific communities: ___ ☐ Offline locations: ___
- How they buy → *ask for a step-by-step journey*: "Walk me through how a customer goes from 'I have this problem' to choosing you. What are the steps?" Show an example: "e.g., Google search → read reviews → book a demo → free trial → purchase." Then ask: Is this typically a quick decision (minutes/hours) or a long consideration (days/weeks/months)?

### 3. Personas
Capture 2-4 distinct personas — the people who interact with your offering. Think about who uses it, who pays for it, and who influences the choice — these may be different people.

**For B2B** — organizational buying roles:
- User, Champion, Decision Maker, Financial Buyer, Technical Influencer

**For B2C** — user segments and decision stakeholders:
- e.g., Primary user, Family decision-maker, Referring professional, Gift buyer
- For services especially, the person receiving the service and the person choosing/paying may differ

For each persona, capture: what they care about, their challenge, and the value you promise them.

*Example*: "The Family Decision-Maker — cares about safety and trust, challenged by navigating confusing care options, we promise peace of mind and vetted professionals."

### 4. Problems & Pain Points
- Core challenge → *finish this sentence*: "Before finding us, customers were stuck because ___."
- Why current solutions or alternatives fall short
- What it costs them → *select all that apply, then ask "which is the biggest?"*:
  ☐ Time ☐ Money ☐ Health/wellbeing ☐ Peace of mind
  ☐ Missed opportunities ☐ Reputation ☐ Relationships ☐ Other: ___
- Emotional tension → *select all that apply*:
  ☐ Frustration ☐ Anxiety/worry ☐ Overwhelm ☐ Distrust
  ☐ Guilt ☐ Embarrassment ☐ Fear ☐ Helplessness ☐ Other: ___
- For services: what's broken about the current experience → *select all that apply*:
  ☐ Hard to access ☐ Long wait times ☐ Can't trust quality
  ☐ Inconvenient ☐ Impersonal ☐ Too expensive ☐ Poor communication ☐ Other: ___

### 5. Competitive Landscape

Help the user think in three tiers — show examples for each to unblock them:

- **Direct competitors**: Same solution, same problem (e.g., Calendly vs SavvyCal, or one dog-walking service vs another)
- **Secondary competitors**: Different solution, same problem (e.g., dog-walking service vs doggy daycare)
- **Indirect competitors**: Conflicting approach or inaction (e.g., dog-walking service vs "just let the dog out in the yard")
- For each: "How does this option fall short for your customers?"

*Prompt*: "Name 1-2 for each tier. If you're not sure, think about what your customers were doing before they found you — that's your indirect competitor."

### 6. Differentiation
- Key differentiators (capabilities or qualities alternatives lack) → *constraining prompt*: "Name your top 3 differentiators — things competitors can't or don't offer."
- How you solve it differently
- Why that's better (benefits)
- Why customers choose you over alternatives → *finish this sentence*: "Customers pick us over alternatives because ___."
- For services: what makes the experience different → *select all that apply*:
  ☐ More convenient ☐ More trustworthy ☐ Better credentials
  ☐ Higher quality ☐ Faster ☐ Easier access
  ☐ More personalized ☐ Better communication ☐ Other: ___

### 7. Objections & Anti-Personas
- Top 3 objections → *show common categories to jog memory*: "What pushback do you hear? Common ones include: price ('too expensive'), trust ('how do I know it works?'), switching cost ('too hard to change'), timing ('not now'), complexity ('seems complicated'), risk ('what if it doesn't work?'). What are your top 3?"
- For each objection, ask: "How do you respond to that?"
- Who is NOT a good fit (anti-persona) → *ask directly*: "Describe a customer you'd turn away. Who wastes your time or churns fast?"

### 8. Switching Dynamics
Compile the JTBD Four Forces from what you've already captured — do NOT re-ask questions the user already answered:
- **Push** ← pull from Section 4 (pain points, emotional tension, what it costs them)
- **Pull** ← pull from Section 6 (differentiators, why customers choose you)
- **Habit** ← what keeps them stuck (often not yet captured — ask if missing)
- **Anxiety** ← what worries them about switching (often not yet captured — ask if missing)

Present your compiled draft of all four forces and ask: "Does this capture the dynamics? What's missing?" Only probe for Habit and Anxiety directly — Push and Pull should already be covered.

### 9. Customer Language
- How customers describe the problem → *finish this sentence*: "A customer would tell a friend: 'I was struggling with ___ and then I found ___.'"
- How they describe your solution (verbatim) → ask: "When customers recommend you, what do they actually say? Not your marketing — their words."
- Words/phrases to use → ask: "What words does your audience use? What resonates?"
- Words/phrases to avoid → ask: "Any words that would make your audience cringe or tune out?"
- Glossary of key terms specific to your offering

For early-stage companies with few customers: "How would your ideal customer describe this problem to a friend? Just make it up — what would they say?"

### 10. Brand Voice
- Brand personality: "If your brand were a person, how would you describe them?" (3-5 adjectives, but push for a one-sentence character sketch too)
- Voice attributes (pick 2-3 core attributes — `/brand-voice` expands to 3-5 with full examples): for each, capture what it means and what it does NOT mean. E.g., "Approachable — friendly and jargon-free, but not dumbed-down or overly casual"
- Tone direction → *spectrum selection*: "Where do you fall on each? (a) Formal ← → Casual (b) Technical ← → Accessible (c) Bold ← → Measured (d) Warm ← → Direct"
- Voice do's and don'ts (1-2 each): e.g., "We explain, we don't lecture" or "We're confident, never arrogant"
- Sample sentence: ask for one sentence that sounds like the brand at its best — this is the most useful reference for downstream skills
- Tone shifts: does the voice change for different audiences or channels? (e.g., warmer with patients, more clinical with referring doctors; casual on social, professional in email)

**When is this section enough?** For most teams, these essentials are sufficient — downstream skills can produce consistent content from this. Run `/brand-voice` when you need grammar/style rules, detailed terminology governance, channel-by-channel tone tables, or have multiple writers who need a shared reference document.

### 11. Proof Points
- What proof do you have? → *select all that apply*:
  ☐ Metrics/results (revenue, users, growth) ☐ Customer logos ☐ Case studies
  ☐ Testimonials/quotes ☐ Ratings/reviews ☐ Certifications/credentials
  ☐ Awards ☐ Press/media mentions ☐ Research/data
  ☐ Founder expertise ☐ Pilot/beta results ☐ Waitlist size ☐ Other: ___
- For each type selected, ask for specifics
- Main value themes and supporting evidence

For early-stage: "What proof do you have so far, even if small? Anything counts — beta user feedback, waitlist numbers, founder credentials, a pilot result."

### 12. Goals
- Primary business goal → *select one or two*: (a) Grow revenue (b) Acquire customers/users (c) Increase retention (d) Build awareness/brand (e) Enter new market (f) Launch new offering (g) Raise funding (h) Other: ___
- Key conversion action → *select one*: What's the #1 thing you want someone to do? (a) Sign up / create account (b) Start free trial (c) Book a demo/call (d) Make a purchase (e) Request a quote (f) Download something (g) Join waitlist (h) Subscribe (i) Other: ___
- Current metrics (if known) — ask: "Any numbers you're tracking? Revenue, users, conversion rate, traffic — whatever you have."

---

## Step 3: Create the Document

After gathering information, create `.agents/product-marketing-context.md` with this structure:

```markdown
# Product Marketing Context

*Last updated: [date]*

## Offering Overview
**Company/brand:**
**One-liner:**
**What it does:**
**Why it exists:**
**Category:**
**Offering type:**
**Stage:**
**Business model & pricing:**
**Delivery model:** *(if service/hybrid)*
**Coverage area:** *(if service/hybrid)*

## Target Audience
**Target customers:**
**Who decides:**
**How they find us:**
**Where they spend time:**
**How they buy:**
**Primary use case:**
**Jobs to be done:**
-
**Use cases:**
-

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| | | | |

## Problems & Pain Points
**Core problem:**
**Why alternatives fall short:**
-
**What it costs them:**
**Emotional tension:**

## Competitive Landscape
**Direct:** [Competitor] — falls short because...
**Secondary:** [Approach] — falls short because...
**Indirect:** [Alternative] — falls short because...

## Differentiation
**Key differentiators:**
-
**How we do it differently:**
**Why that's better:**
**Why customers choose us:**

## Objections
| Objection | Response |
|-----------|----------|
| | |

**Anti-persona:**

## Switching Dynamics
**Push:**
**Pull:**
**Habit:**
**Anxiety:**

## Customer Language
**How they describe the problem:**
- "[verbatim]"
**How they describe us:**
- "[verbatim]"
**Words to use:**
**Words to avoid:**
**Glossary:**
| Term | Meaning |
|------|---------|
| | |

## Brand Voice
**Personality:** [3-5 adjectives + one-sentence character sketch]
**Voice attributes:**
| Attribute | We are | We are not |
|-----------|--------|------------|
| | | |
**Tone direction:**
**Voice do's:**
**Voice don'ts:**
**Sample sentence:**
**Tone shifts:** [how voice adapts by audience or channel]

## Proof Points
**Metrics:**
**Customers/Credentials:**
**Testimonials:**
> "[quote]" — [who]
**Value themes:**
| Theme | Proof |
|-------|-------|
| | |

## Goals
**Business goal:**
**Conversion action:**
**Current metrics:**
```

---

## Step 4: Confirm and Save

- Show the completed document
- Ask if anything needs adjustment
- Save to `.agents/product-marketing-context.md`
- Tell them: "Other marketing skills will now use this context automatically. Run `/product-marketing-context` anytime to update it."

---

## Tips

- **Be specific**: Ask "What's the #1 frustration that brings them to you?" not "What problem do they solve?"
- **Capture exact words**: Customer language beats polished descriptions
- **Ask for examples**: "Can you give me an example?" unlocks better answers
- **Validate as you go**: Summarize each section and confirm before moving on
- **Skip what doesn't apply**: Not every offering needs all sections — adapt to the offering type
- **Adapt to the offering**: For services, lean into trust, access, experience, and relationship. For products, lean into features, capabilities, and integrations. Hybrid offerings need both. Let offering type (from Section 1) guide your emphasis throughout.
- **Match depth to stage**: Pre-launch companies will have sparse Proof Points and Customer Language — that's fine. Capture what exists and mark gaps to revisit later.
