# SPEC DOCUMENT — `first-1000-users`

**A Prompt-Based Skill for AI-Assisted Community Seeding**

Platform: Claude Project / Custom GPT
Version 2.3 | February 2026
Status: Draft — Pending Supervisor Approval

---

## 1. Overview

`first-1000-users` is a prompt-based skill that helps founders and marketers find the right communities, detect buying signals, and generate authentic outreach content to seed their product into real conversations — all without writing a single line of code.

The user feeds a product spec file (`.md`) into a Claude Project or Custom GPT. The AI analyzes the product and returns a complete seeding playbook: community map, buying signals, public reply templates, **and direct message (DM) templates** for reaching out to people who raised a relevant problem.

### 1.1 Core Idea

Instead of broadcasting content to everyone, find the people who are **already looking** for what you built — then show up with a helpful reply in the thread **and** a thoughtful DM to the person who raised the problem.

### 1.2 Two Engagement Channels

| Channel | When to Use | Conversion |
|---------|------------|------------|
| **Public Reply** | Thread is active, multiple people have the same problem | Lower per-reply, but visible to many readers |
| **Direct Message** | One person clearly has the pain point your product solves | Higher per-message, one-on-one relationship |

Both channels work together: a public reply builds credibility, a DM starts a real conversation.

### 1.3 What This Skill Is

- ✅ A strategic research tool that maps communities, signals, and engagement angles
- ✅ Generates both public reply templates AND DM templates customized to your product
- ✅ Runs on Claude Project or Custom GPT — no code, no API keys, no setup

### 1.4 What This Skill Is NOT

- ❌ Not a bot that auto-posts or auto-DMs on your behalf
- ❌ Not a software system requiring engineering work
- ❌ Not a generic template — outputs are customized to your specific product

---

## 2. How It Works

```
User feeds product spec (.md)
        ↓
AI analyzes product → identifies ideal customers, pain points, use cases
        ↓
Output 1: Community Map — where your users hang out
        ↓
Output 2: Buying Signals — what they say when they need you
        ↓
Output 3: Reply Templates — what to post publicly, per signal type
        ↓
Output 4: DM Templates — what to message directly to the person
```

### 2.1 Input

A single `.md` file describing the product:

| Section | What to Include | Why It Matters |
|---------|----------------|----------------|
| **Product name & one-liner** | What it is in one sentence | Used in templates |
| **Problem it solves** | The pain point, in the user's language | Maps to buying signals |
| **Who it's for** | Target audience / ideal customer description | Drives community mapping |
| **Key features** | Top 3–5 features or differentiators | Shapes reply and DM angles |
| **Pricing** | Free / freemium / paid | Affects DM offer (free trial? demo?) |
| **Current stage** | Pre-launch / beta / live | Sets DM tone (early access invite vs. recommendation) |
| **Competitors** | What people use today instead | Powers comparison-based signals |

### 2.2 Four Outputs

| Output | What You Get | How to Use It |
|--------|-------------|---------------|
| **Community Map** | Ranked list of Reddit + Slack communities | Know where to spend your time |
| **Buying Signals** | Phrases people use when they need your product | Know what to search for |
| **Reply Templates** | Public replies for threads (value-first) | Post in the thread to build credibility |
| **DM Templates** | Direct messages to the person who raised the problem | Start a 1-on-1 conversation |

---

## 3. Output 1 — Community Map

### 3.1 What It Delivers

For each platform (Reddit and Slack), a ranked list of communities with:

- Community name and link
- Estimated audience size
- Relevance score (High / Medium / Low)
- Best channel or flair to target
- Community self-promotion rules and constraints
- DM culture: does this community accept cold DMs or is it frowned upon?
- Suggested entry strategy

### 3.2 Selection Criteria

**Reddit:**
- Topic alignment — Does this subreddit discuss the problem the product solves?
- Audience match — Are the members part of the target audience?
- Activity level — Recent posts with engagement in the last week?
- Openness to tools — Does the community welcome tool recommendations?
- DM receptiveness — Do users in this subreddit respond well to helpful DMs?

**Slack:**
- Professional relevance — Is this a workspace where the ideal customer hangs out?
- Channel structure — Does it have #help, #tools, or similar channels?
- Accessibility — Is it an open community anyone can join?
- DM norms — Is DMing other members acceptable in this workspace?

### 3.3 Limitations & Verification

The community map is generated based on AI knowledge and may not reflect real-time status. Users **must verify** before engaging:

- [ ] Is the subreddit still active? (Check last post date)
- [ ] Have the community rules changed? (Read sidebar/pinned post)
- [ ] Is the Slack community still open for new members? (Visit join link)
- [ ] Is the estimated size roughly accurate? (Check subscriber count)
- [ ] What are the DM norms? (Check community guidelines on direct outreach)

If the skill runs on Claude with web search enabled, it will attempt to verify these automatically. Otherwise, verification is manual.

---

## 4. Output 2 — Buying Signal Library

### 4.1 What It Delivers

A categorized library of phrases and patterns that indicate someone needs the product. Signals are **customized to the specific product** — not generic placeholders.

### 4.2 Signal Categories

| Signal Type | Priority | Best Channel |
|-------------|----------|-------------|
| **Direct Request** | Highest | Reply + DM |
| **Comparison** | High | Reply + DM |
| **Pain Point** | High | DM first (personal problem, personal outreach) |
| **Workflow Question** | Medium | Reply (public answer helps many) |
| **Discussion** | Low | Reply only (DM would be intrusive) |

Note: **Pain Point** signals are the strongest DM triggers — someone sharing a personal frustration is most receptive to a direct, helpful message.

### 4.3 Output Format

Each signal includes the pattern, a real-world example, and which engagement channel to use:

```
Signal: Pain Point
Pattern: "I've been struggling with [problem] and nothing works"
Real example: "I spend 3 hours a day manually tracking feedback from 5 channels"
→ Engagement: Reply with a helpful tip + DM with product intro
```

---

## 5. Output 3 — Public Reply Templates

### 5.1 Reply Structure

Every public reply follows this framework:

1. **Acknowledge** — Show you understand their problem or question
2. **Help** — Provide genuine value independent of any product
3. **Bridge** — Naturally connect to the product as one relevant option
4. **Soft close** — Offer to share more, no hard sell

### 5.2 Platform Tone

| Aspect | Reddit | Slack |
|--------|--------|-------|
| Tone | Casual, peer-to-peer, opinionated | Professional, friendly, concise |
| Length | 3–5 sentences | 1–3 sentences |
| Product mention | "I've been using X for this" | "You might want to check out X" |
| Avoid | Sounding like a marketer | Walls of text, unsolicited pitches |

### 5.3 Template Variants

For each signal type, the skill generates **3 variants**:

- **Experience-based** — "I've used X and here's what happened"
- **Comparison-based** — "I tried A, B, and C — here's the breakdown"
- **Problem-solving** — Solution first, product mention as afterthought

---

## 6. Output 4 — DM Templates

### 6.1 Why DMs Matter

Public replies are visible but passive — you wait for the person to read your comment. DMs are proactive — you bring the solution directly to the person who has the problem. When done right, DMs have significantly higher conversion because they feel personal, not promotional.

### 6.2 DM Structure

Every DM follows this framework:

1. **Reference** — Mention their specific post/message so they know why you're reaching out
2. **Empathize** — Show you genuinely understand their problem (not just pitching)
3. **Offer value** — Share a specific insight, resource, or tip before mentioning the product
4. **Introduce product** — Briefly explain how it solves their exact stated problem
5. **Low-pressure close** — Make it easy to say no ("no worries if not relevant" / "just thought it might help")

### 6.3 DM Tone Guide

| Aspect | Reddit DM | Slack DM |
|--------|-----------|----------|
| Tone | Friendly stranger, casual | Professional peer, collegial |
| Opener | "Hey, saw your post about..." | "Hi [name], noticed your question in #channel..." |
| Length | 3–4 sentences max | 2–3 sentences max |
| Product mention | "I actually built something for this" (maker framing) | "We've been using X for this" (team framing) |
| Close | "Happy to share more if useful" | "Let me know if you'd like to take a look" |
| Avoid | Long paragraphs, multiple links, follow-up if no reply | Pitching in first message, cold DM without context |

### 6.4 DM vs Reply — When to Use Which

| Scenario | Reply | DM | Both |
|----------|-------|-----|------|
| Someone asks "what tool do you use for X?" in a thread with 20+ comments | ✅ | | |
| Someone posts a detailed frustration about their current workflow | | ✅ | |
| Someone asks for recommendations and only has 2–3 replies | | | ✅ |
| Someone compares competitors and asks for experiences | ✅ | ✅ | |
| General discussion about the industry | ✅ | | |
| Someone says "I wish there was a tool that..." | | ✅ | |

**Rule of thumb:** If the person shared a **personal** problem, DM them. If they asked a **general** question, reply publicly.

### 6.5 DM Ethical Guardrails

- **One DM per person** — Never follow up if they don't respond
- **Reference their post** — Never send a DM without context; they must know why you're reaching out
- **Respect "no"** — If they're not interested, thank them and move on
- **No bulk DMs** — Every DM must be personalized to the specific person and their specific post
- **Check platform rules** — Some subreddits and Slack workspaces prohibit unsolicited DMs

---

## 7. End-to-End Example

This example uses **first-1000-users itself** as the product — the skill is its own demo.

### 7.1 Example Input — Product Spec

```markdown
# Product Spec: first-1000-users

**One-liner:** An AI skill that helps founders find the right communities, 
detect buying signals, and generate outreach content to seed their product 
into real conversations.

**Problem:** Founders know they should engage in communities where their 
users hang out, but the process is painfully manual — finding the right 
subreddits, monitoring conversations, writing replies that don't sound 
like spam, and DMing people without being creepy. Most give up after a 
few days or resort to copy-paste templates that get downvoted or ignored.

**Who it's for:** Non-technical founders, solo makers, and early-stage 
marketers who need their first 1,000 users but don't have a growth team 
or ad budget.

**Key features:**
- Community mapping: identifies best Reddit + Slack communities
- Buying signal detection: customized phrases and patterns to watch for
- Public reply templates: value-first drafts in 3 variants per signal
- DM templates: personal outreach messages for high-intent signals
- Ethical guardrails: built-in checklist to prevent spam

**Pricing:** Free (open-source skill).

**Stage:** Pre-launch, building for a skill competition.

**Competitors:** Manual community seeding (time-consuming), generic ChatGPT 
prompts (not specialized), growth agencies ($5k+/mo), social listening 
tools like Mention/Brand24 (monitoring only, no reply/DM drafting).
```

### 7.2 Example Output — Community Map (Excerpt)

```
## Reddit Communities

1. r/SaaS (180k members) — Relevance: HIGH
   - Why: Founders constantly ask "how did you get your first users?"
   - Best for: "First users" and "community-led growth" threads
   - Self-promo rules: Weekly thread for promos; helpful mentions OK elsewhere
   - DM culture: Acceptable if you reference their post; don't cold pitch
   - Entry strategy: Answer growth questions for 1 week first

2. r/EntrepreneurRideAlong (120k members) — Relevance: HIGH
   - Why: Builders documenting their journey — many stuck at "how do I get users?"
   - Best for: "I built X but have zero users" threads
   - Self-promo rules: Supportive community, genuine recommendations welcome
   - DM culture: Very receptive — members often appreciate personal outreach
   - Entry strategy: Share your own experience using the skill

3. r/indiehackers (55k members) — Relevance: HIGH
   - Why: Solo makers actively seeking scrappy growth tactics
   - Best for: "How do you find your first customers?" threads
   - Self-promo rules: Open to tools made by community members
   - DM culture: Common and accepted, especially for mutual help
   - Entry strategy: Post a "Show IH" with your own results

## Slack Communities

1. Indie Hackers Slack (~5k members) — Relevance: HIGH
   - Why: Makers sharing tools and growth strategies daily
   - Best channel: #growth, #tools, #show-your-work
   - DM culture: Normal — members regularly DM each other after channel discussions
   - Entry strategy: Contribute in channels first, DM people who share relevant problems

2. Product Hunt Makers Slack (~3k members) — Relevance: HIGH
   - Why: Pre-launch founders prepping for launch, need early users
   - Best channel: #launch-prep, #feedback
   - DM culture: Expected — people DM for launch support regularly
   - Entry strategy: Offer to run a community map for someone's product as a free demo
```

### 7.3 Example Output — Buying Signals (Excerpt)

```
## Direct Request Signals (for first-1000-users)
- "How do you find communities to promote your product in?"
  → Reply + DM
- "Any tools for community-led growth?"
  → Reply + DM
- "What's the best way to seed a product on Reddit without being spammy?"
  → Reply + DM

## Pain Point Signals (for first-1000-users) — BEST FOR DM
- "I've been posting in subreddits for weeks and getting zero traction"
  → DM first, reply optional
- "Every time I mention my product on Reddit I get downvoted"
  → DM first (personal frustration = personal outreach)
- "I spend 3 hours a day browsing Reddit for relevant threads and it's exhausting"
  → DM first
- "I tried community seeding but my replies all sound like a sales pitch"
  → DM first

## Comparison Signals (for first-1000-users)
- "Is it worth hiring a growth agency or can I do it myself?"
  → Reply + DM
- "ChatGPT vs custom prompt for writing community replies?"
  → Reply only (too generic for DM)

## Workflow Question Signals (for first-1000-users)
- "What's your process for engaging in communities without coming off as spammy?"
  → Reply (public answer helps many)
- "How do you decide which subreddits to focus on?"
  → Reply (public answer helps many)
```

### 7.4 Example Output — Public Reply Template (Excerpt)

```
## Template: Pain Point — "Getting downvoted on Reddit" (Reddit)

Variant 1 (Experience-based):
"Been there — I used to drop links to my product in every relevant 
thread and wondered why I kept getting downvoted. The issue wasn't 
the product, it was the approach. What worked for me was flipping 
the structure: answer the question first, share a useful tip second, 
and only mention your product as 'one thing that helped me' at the 
end. I actually built a skill called first-1000-users that generates 
this kind of reply structure automatically — maps your communities, 
detects buying signals, and drafts value-first replies. Open source 
if you want to try it."

Variant 2 (Problem-solving):
"The downvotes usually mean the reply reads like an ad, not a 
conversation. A good test: would your reply still be useful if you 
removed the product mention entirely? If not, rewrite it. Lead with 
genuine help, then bridge naturally. There's a free AI skill called 
first-1000-users that structures replies this way — might save you 
some trial and error."

Variant 3 (Comparison-based):
"I've tried a few approaches to community seeding:
- Manual browsing + writing replies: authentic but takes 3+ hrs/day
- Generic ChatGPT prompts: fast but replies sound robotic
- Growth agency: great results but $5k/mo minimum
- first-1000-users (AI skill): maps communities, finds signals, 
  drafts replies you can customize — free and open source
For solo founders, the last one hit the sweet spot."
```

### 7.5 Example Output — DM Template (Excerpt)

```
## DM Template: Pain Point — "Getting downvoted" (Reddit)

"Hey — saw your post about getting downvoted when mentioning your 
product on Reddit. I had the exact same problem a while back.

What fixed it for me was restructuring replies: lead with a genuine 
answer to their question, add a useful tip, then mention your product 
as just 'one option that worked for me' at the very end. The ratio 
should be 80% help, 20% product.

I actually built a free skill (first-1000-users) that generates this 
kind of reply structure — also maps which communities to target and 
what buying signals to look for. Happy to share if useful, no worries 
if not your thing."

---

## DM Template: Pain Point — "Spending hours browsing Reddit" (Slack)

"Hi [name] — saw your message in #growth about spending 3+ hours a 
day browsing Reddit for relevant threads. I felt that pain too.

Built an open-source AI skill that does the research part for you — 
maps communities, identifies buying signals, and drafts reply 
templates. Cuts the research from hours to minutes.

Here's the link if you want to take a look: [link]. Let me know if 
you have any questions!"
```

---

## 8. Ethical Guidelines

### 8.1 Non-Negotiable Rules

- **Value first** — Every reply and DM must help the person even if they never use the product
- **Authenticity** — Templates are starting points; users must personalize before sending
- **Transparency** — Never pretend to be someone you're not
- **Respect community rules** — Follow self-promotion and DM policies from the community map
- **No spam** — Never send identical content to multiple people
- **One DM per person** — If they don't respond, move on. Never follow up.

### 8.2 Quality Checklist — Public Replies

- [ ] Does this reply help the person even if they ignore the product mention?
- [ ] Is the product mention natural and contextual?
- [ ] Have I personalized the template with my own words?
- [ ] Am I following this community's self-promotion rules?
- [ ] Would I be comfortable if someone posted this reply to me?

### 8.3 Quality Checklist — DMs

- [ ] Did I reference their specific post/message? (They must know why I'm reaching out)
- [ ] Does this DM provide value before mentioning the product?
- [ ] Is it under 4 sentences? (Short = respectful of their time)
- [ ] Would I appreciate receiving this DM if I were them?
- [ ] Have I checked if this community allows unsolicited DMs?
- [ ] Am I prepared to accept "no" or silence gracefully?

---

## 9. Build Plan — 2-Day Sprint

**Timeline:** 2 working days
**Platform:** Claude Project or Custom GPT
**Deliverable:** A working Claude Project (or Custom GPT) with system prompt + example product spec as project knowledge

### Day 1 — Core Skill & All 4 Outputs

**Morning:**
- Create Claude Project (or Custom GPT)
- Write system prompt covering all 4 outputs: community map, signals, reply templates, DM templates
- Define input spec format and output structure
- Include DM culture assessment in community mapping logic

**Afternoon:**
- Feed the first-1000-users example spec (Section 7.1) and validate output quality
- Iterate on community mapping — ensure DM norms are included per community
- Iterate on signal detection — ensure each signal specifies Reply vs DM vs Both
- Validate DM templates follow the Reference → Empathize → Value → Introduce → Low-pressure structure
- Test with 1–2 additional product specs (different industries) to confirm adaptability

**Day 1 Deliverable:** Working skill that accepts a product spec and returns all 4 outputs with DM/Reply channel guidance.

### Day 2 — Quality, Testing & Polish

**Morning:**
- Refine reply templates — ensure value-first structure, platform-appropriate tone
- Refine DM templates — ensure they feel personal, not automated
- Test DM templates: would you actually send this to a stranger? If not, rewrite.
- Verify DM vs Reply guidance makes sense for each signal type

**Afternoon:**
- Write SKILL.md with complete instructions
- Create ai-showcase examples (screenshots of all 4 outputs)
- Final test: full workflow — feed spec → review community map → check signals → read replies → read DMs
- Package all files and submit

**Day 2 Deliverable:** Polished, tested skill ready for submission.

---

## 10. Success Criteria

| Criteria | How to Measure | Target |
|----------|---------------|--------|
| **Community relevance** | Check top 5 Reddit suggestions — are they active and on-topic? | 4 out of 5 are relevant |
| **DM culture accuracy** | Verify DM norms for top 3 communities — does the assessment match reality? | 3 out of 3 are accurate |
| **Signal accuracy** | Search top 3 signals on Reddit — do matching posts exist? | At least 5 real posts found per signal |
| **Signal → channel mapping** | Review DM vs Reply recommendations — do they make sense? | Logical for all signal types |
| **Reply template quality** | Read 3 reply drafts — would you post it as-is? | 2 out of 3 pass |
| **DM template quality** | Read 3 DM drafts — would you send this to a stranger? | 2 out of 3 pass the "would I send this?" test |
| **Customization** | Compare outputs for 2 different products — are they meaningfully different? | No overlap between outputs |

---

## 11. File Structure

```
first-1000-users/
├── README.md              # Skill introduction & how to use
├── SKILL.md               # System prompt & instructions for Claude Project / Custom GPT
├── spec.md                # This file — technical specification (v2.3)
├── skill-card.md          # Quick-reference card
└── ai-showcase/           # Example inputs, outputs, and screenshots
    └── README.md          # Guide for adding examples
```

---

*End of Specification — first-1000-users v2.3*
