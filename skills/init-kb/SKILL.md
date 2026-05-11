---
name: init-kb
description: Initialize or update a knowledge base for a project, business, or client. Triggers on "init kb", "build kb", "create kb for X", "set up kb", "new kb" (init), and "update kb", "refresh kb", "re-scrape kb", "kb update" (update). Scrapes websites and social profiles via the Firecrawl API, runs deep analysis, asks targeted questions to fill gaps, and generates 9 structured KB files. Each KB loads on-demand (not at boot) to avoid context bloat. Files are designed to be comprehensive references for specialized agents.
---

# Initialize or Update Knowledge Base (OpenClaw)

You are building a structured knowledge base that gives AI agents everything they need to understand a person, their business, their voice, and their boundaries. This is the foundation for all future AI work. The better the KB, the better every output from day one.

This is the OpenClaw version of the init-kb skill. It uses the **Firecrawl REST API** (via curl) instead of the Firecrawl CLI.

## Critical Design Principle: On-Demand Loading Only

**IMPORTANT:** Knowledge bases must load ON-DEMAND, not at boot. Every agent session should not preload all KB files. This causes massive context bloat and kills productivity.

**The pattern:**
- 9 KB files are comprehensive references for **specialized work only**
- When the user asks for Operator Vault work, THEN load the relevant KB files
- For all other tasks, the KB stays unloaded
- AGENTS.md notes where the KB is, but doesn't auto-load it

This is critical for multi-project workspaces. Enforcing this throughout Phase 7 (Integration) prevents context waste.

## What You Produce

9 files in `KNOWLEDGE BASE/<project-name>/`:

| File | What It Captures |
|------|-----------------|
| PERSONA.md | Agent identity, core behavioral rules, boundaries, vibe |
| CONTEXT.md | Business context, goals, market position, competitors, non-negotiables |
| USER.md | The person/founder: background, origin story, personality, differentiators |
| VOICE.md | Writing style: tone, vocabulary, banned words/phrases, quality test |
| GUARDRAILS.md | Brand rules, things to never say, sensitive topics, approval gates |
| SITEMAP.md | Complete site structure (only if 20+ pages; otherwise folded into CONTEXT.md) |
| BUSINESS-INTEL.md | Products, pricing, business model, audience, positioning, tech stack, team |
| OPPORTUNITIES.md | Gaps, thin content, broken journeys, growth signals |
| CORRECTIONS.md | Self-improving log: every correction the user makes updates the source KB file and gets logged here |

Plus:
- A `site-content/` directory with every scraped page as its own markdown file
- An AGENTS.md boot section (auto-appended) and a CLAUDE.md snippet

## Triggers

**Init triggers:** "init kb", "build kb", "create kb for X", "set up kb", "new kb"

**Update triggers:** "update kb", "refresh kb", "re-scrape kb", "kb update"

When an update trigger fires, skip to the **Update Flow** section.

## API Key Setup

The Firecrawl API key must be available. Check for it in this order:
1. Environment variable `FIRECRAWL_API_KEY`
2. A file at `.firecrawl/api-key.txt` in the workspace root
3. Proceed through Phase 0 onboarding (see below)

If the user provides a key, save it to `.firecrawl/api-key.txt` (one line, just the key). Read from this file on future runs.

## Rules

1. **One question per message.** Never stack multiple questions. People freeze when they see three at once.
2. **Show before ask.** If Firecrawl pulled data, show what you found and ask to confirm before asking more questions.
3. **Progress tracking.** After each phase, tell the user where they are: "That's the personal stuff done. 2 of 4 sections complete. Next up: your business."
4. **Skip-friendly.** If someone says "I don't know" or "skip", mark it as `<!-- TODO: fill in later -->` in the output and move on. Never pressure.
5. **Accept file imports.** If the user drops a brand guide, doc path, or existing content, read it and extract relevant info instead of asking questions the doc already answers.
6. **No em dashes.** Never use them in generated files or responses. Use commas, periods, or restructure.
7. **Concise output.** Each file should be scannable. No novels. Strong opinions over vague guidelines. Actionable rules, not suggestions.

---

## The Flow

### Phase 0: Onboarding Wizard

When the skill triggers (init), open with this welcome message before asking anything:

```
Welcome to init-kb. I'm going to build a complete knowledge base that gives your AI agents full context on your business — who you are, what you sell, how you write, and what the rules are.

Here's what we're building:
- 9 structured files covering your business, person, voice, and boundaries
- Your full website scraped and analyzed (if you have one)
- A living KB that gets smarter over time

Estimated time: 10-20 minutes (faster if you have a website to scrape)

Do you have a Firecrawl API key? That's what I use to scrape your website and social profiles. If not, grab one free here: https://firecrawl.link/operator — come back when you have it and we'll continue.
```

If they say they have a key (or one is already saved), move to API key setup guidance below.
If they don't have one yet, wait for them to confirm before proceeding.

**API key setup — ask first:** "Are you running OpenClaw locally on your machine (Mac, PC) or on a server/VPS?"

**If local:**
```
To save your key permanently, run this in your terminal:

echo 'export FIRECRAWL_API_KEY=your-key-here' >> ~/.zshrc && source ~/.zshrc

Or if you use bash: replace .zshrc with .bashrc

Then paste your key here and I'll also save it to .firecrawl/api-key.txt as a backup.
```

**If VPS/server:**

Three ways to add it:

**Option 1 — Hostinger (GUI):**
```
Log into Hostinger, go to Catalogue, click Manage on your VPS, scroll down to Environment Variables, and add:
  Key: FIRECRAWL_API_KEY
  Value: your-key-here
```

**Option 2 — Any VPS via terminal:**
```
echo 'export FIRECRAWL_API_KEY=your-key-here' >> ~/.bashrc && source ~/.bashrc
```
(Replace .bashrc with .zshrc if you use zsh.)

**Option 3 — Just paste it here:**
Paste your key directly in this chat and I'll save it to .firecrawl/api-key.txt. Only do this if you're the only one with access to your server and Discord channel. Never paste API keys in shared or public channels.

After they paste the key, save it to `.firecrawl/api-key.txt` and confirm: "Got it. Key saved."

Then proceed:

**Question 1:** "What's the project or business name? This becomes the folder name."

**Question 2:** "Got a website URL? Any social profiles (LinkedIn, X, YouTube, Instagram)? Any other important links (docs, portfolio, press pages, Skool community)? Drop them all here. If you don't have any yet, just say 'none' and we'll skip the scraping."

**After Phase 0:**

- Check if `KNOWLEDGE BASE/<project-name>/` already exists:
  - If some files exist: "I found PERSONA.md and CONTEXT.md already. Want me to build the missing ones, or update everything?"
  - If all files exist: "This KB is already complete. Want me to review and update it, or leave it as-is?"

- **Check cache.** If `.firecrawl/<project-slug>/crawl-raw.json` exists and is less than 7 days old: "I already scraped this site on [date]. Want to use the cached data or re-scrape?" If cache is good, skip to Stage 4.

- If a website URL was provided, run the **Firecrawl scraping pipeline:**

#### Stage 1: Discover URLs (Map API)

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/map" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "<website-url>", "limit": 500}' \
  -o .firecrawl/<project-slug>/map-result.json
```

Parse the response to get the URL list and count. Present to the user: "I found X pages on your site. Crawling all of them will use approximately X Firecrawl credits. Want me to proceed, or should I limit it?"

If the user wants to limit, ask for a number or suggest core pages only.

#### Stage 2: Crawl Full Site (Crawl API)

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/crawl" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "<website-url>", "limit": <N>, "scrapeOptions": {"formats": ["markdown"]}}' \
  -o .firecrawl/<project-slug>/crawl-job.json
```

This returns a job ID. Poll for completion:
```bash
curl -s -X GET "https://api.firecrawl.dev/v1/crawl/<job-id>" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -o .firecrawl/<project-slug>/crawl-raw.json
```

Poll every 10 seconds until `status` is `"completed"`. Tell the user "Crawling... this might take a minute" while waiting.

After completion, parse the JSON and save each page as an individual markdown file in `KNOWLEDGE BASE/<project-name>/site-content/` using URL-slug naming (e.g., `homepage.md`, `about.md`, `products-widget-x.md`).

If the crawl times out or fails: save whatever partial results were collected and continue with what you have.

#### Stage 3: Scrape Supplementary URLs (Scrape API)

For each social profile and important link, scrape individually:
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "<url>", "formats": ["markdown"]}' \
  -o .firecrawl/<project-slug>/social/<platform>.json
```

Parse the markdown content from each response and save as `.md` files in `.firecrawl/<project-slug>/social/` and `.firecrawl/<project-slug>/links/`.

If a social scrape fails (anti-bot, login wall): note "limited extraction" and continue.

#### Stage 4: Deep Analysis Pass

Read through every scraped page and social profile. Build a complete mental model of the business. Do not skim. Do not sample. Read it all.

**Extract into BUSINESS-INTEL.md:**

**1. Products and Services**
- Every product/service with names, descriptions, and URLs
- Pricing (exact numbers, tiers, plans, billing frequency, free trials)
- Features per product/tier
- Who each product is for
- How products relate (bundles, upsells, progression)

**2. Business Model**
- How they make money (subscriptions, one-time, services, ads, affiliate, community)
- Funnel structure (free > lead magnet > paid > upsell)
- Conversion mechanisms (CTAs across pages, what they push hardest)

**3. Target Audience**
- Who the site speaks to (exact language used to describe the customer)
- Pain points mentioned across pages
- Aspirations and outcomes promised
- Customer testimonials and quotes (exact, attributed if possible)

**4. Brand Positioning**
- How they describe themselves vs competitors
- Unique claims and differentiators
- Trust signals (logos, certifications, partnerships, media mentions, stats)
- Authority markers (years in business, team size, client count, revenue claims)

**5. Content Strategy**
- Blog topics and themes
- Content formats (blog, video, podcast, newsletter, courses)
- Publishing frequency (if detectable)
- Lead magnets and email capture points

**6. Tech Stack and Tools** (if detectable)
- Platform, payment processor, email provider, community platform, integrations mentioned

**7. Team and People**
- Founder/owner info (name, role, background, social links)
- Team members mentioned
- Hiring signals

**8. Legal and Compliance**
- Privacy policy highlights
- Terms of service key points (refund policy, usage rights)
- Disclaimers constraining what AI can say

**9. Voice and Messaging Patterns**
- Headline formulas used across pages
- CTA language patterns
- Tone shifts between page types (sales pages vs blog vs about)
- Recurring phrases and taglines
- Language appearing on 3+ pages (core messaging)

**Size check:** If BUSINESS-INTEL.md would exceed roughly 2000 words, split it. Core facts (products, pricing, model, audience, positioning, team, tech) stay in BUSINESS-INTEL.md. Analysis and opportunities (gaps, content signals, growth patterns) go to OPPORTUNITIES.md.

**Extract into OPPORTUNITIES.md:**

Gaps and signals found during analysis:
- Thin content pages
- Missing standard pages (no FAQ, no case studies, no comparison page)
- CTAs that lead nowhere
- Topics referenced but not covered
- Broken user journeys
- Competitive gaps
- Growth signals found in scraped content

Mark each with: `[ ]` Not started, `[~]` In progress, `[x]` Done

**Site structure handling:**
- If the site has 20+ pages, generate a standalone SITEMAP.md organized by category (company pages, product/service pages, blog, legal, landing pages, architecture notes).
- If fewer than 20 pages, fold the site structure into CONTEXT.md as a "Site Structure" section. Skip generating SITEMAP.md.

**Pre-fill answers from scraped content before asking questions:**
- Homepage and About page feeds CONTEXT.md and USER.md
- Blog posts feed VOICE.md (analyze voice from the 3-5 most recent posts)
- Product/service pages feed CONTEXT.md
- Legal pages feed GUARDRAILS.md
- Social profiles feed USER.md and VOICE.md

**Present a summary to the user:**

"I crawled X pages and scraped Y social profiles. Here's what I know about your business:

**What you sell:** [products/services with pricing]
**Who you sell to:** [target audience in their own language]
**How you position yourself:** [key differentiators]
**Your content strategy:** [what you publish, how often, what topics]
**Trust signals I found:** [testimonials, stats, logos]
**Things I noticed:** [gaps, opportunities, interesting patterns]

I've written all of this into BUSINESS-INTEL.md. Now let me confirm a few things I couldn't find on the site."

---

### Phase 1: Business Type

If the website was scraped, attempt to auto-detect the business type. Present as confirmation: "From your site, this looks like a **[Creator / Personal Brand]**. Is that right, or is it something else?"

If no website was scraped, ask directly:

**Question 3:** "What type of business is this?"
- SaaS
- Agency
- Niche Site / Content Site
- Creator / Personal Brand
- E-commerce
- Other (describe it)

**Progress update:** "Got it. 1 of 4 sections done. Next: tell me about yourself."

---

### Phase 2: The Person (feeds USER.md + VOICE.md)

Ask one at a time. If the scrape found an About page, LinkedIn profile, or bio, show what was extracted first: "From your website, I got this: [extracted bio]. Anything to add or correct?" Then skip to what the scrape missed.

**Question 4:** "Tell me about yourself in a few sentences. Background, what you're known for, what makes you different."
(Skip if About page or LinkedIn bio was scraped and user confirms.)

**Question 5:** "What's your origin story? The short version. How did you end up doing what you do?"
(Skip if About page covered this and user confirms.)

**Question 6:** "What do you disagree with in your industry? What do most people in your space get wrong?"

**Question 7:** "Drop 2-3 examples of content you've written or posts you're proud of. Paste the text or links. I'll analyze your voice from these."
(If blog posts or social posts were scraped, use those automatically. Only ask for additional samples if fewer than 3 were found.)

If the user provides links, scrape them via the Scrape API. If they paste text, analyze directly. Extract sentence length patterns, vocabulary habits, tone, structural patterns, and recurring phrases.

**Question 8:** "Any words or phrases you hate? Things that make you cringe when you see them in content? These go straight into your banned list."
(Always ask. Cannot be scraped.)

**Progress update:** "Personal section done. 2 of 4 sections complete. Next: your business."

---

### Phase 3: The Business (feeds CONTEXT.md)

If website was scraped, show what was extracted: "From your homepage, it looks like you do [X] for [Y]. Sound right?" Then ask only what the scrape missed.

**Question 9:** "What does your business actually do? Who's it for?"
(Skip if homepage/about was scraped and user confirms.)

**Question 10:** "What are you optimizing for right now? Revenue? Growth? Awareness? Building an audience?"
(Always ask. Cannot be scraped.)

**Question 11:** "Who are your competitors or the people in your space? What makes you different?"
(Skip if scraped content made this clear and user confirms.)

**Question 12:** "Any non-negotiables? Things that must always be true about how your business shows up?"
(Always ask. Cannot be scraped.)

**Adaptive bonus questions by business type:**

If **SaaS:** "Main features? Pricing model? Ideal customer profile?"
If **Agency:** "Services? Client types? Standout case studies?"
If **Niche Site / Content Site:** "Niche? Monetization? Content pillars?"
If **Creator / Personal Brand:** "Platforms? Content formats? Monetization? Audience?"
If **E-commerce:** "What do you sell? Channels? Brand story? Typical customer?"

**Progress update:** "Business section done. 3 of 4 sections complete. Last one: AI agent rules."

---

### Phase 4: The AI Agent (feeds PERSONA.md + GUARDRAILS.md)

**Question 13:** "What should AI agents built from this KB be able to do? Write content? Customer support? Research? SEO? Be specific."

**Question 14:** "What should the AI never do? Hard boundaries?"

**Question 15:** "Anything legally sensitive, topics to avoid, or things that need human approval?"

**Progress update:** "All questions done. Let me show you what I've got before generating the files."

---

### Phase 5: Review and Generate

Present a summary organized by output file (key points, not full files):

```
Here's what I captured:

**PERSONA.md** (Agent Identity)
- Role: [what the agent does]
- Core rules: [2-3 key rules]
- Boundaries: [key restrictions]

**CONTEXT.md** (Business)
- Business: [what it does, who it's for]
- Goals: [top 3 priorities]
- Differentiator: [what makes them different]

**USER.md** (The Person)
- Background: [key points]
- Origin: [short version]
- Values: [what they care about]

**VOICE.md** (Writing Style)
- Tone: [analysis from samples]
- Banned: [key items]
- Style: [key patterns]

**GUARDRAILS.md** (Boundaries)
- Never: [key restrictions]
- Sensitive: [topics requiring care]
- Approval required: [what needs sign-off]

**SITEMAP.md** (Site Structure) [only if 20+ pages]
- Total pages: [count]
- Categories: [breakdown]

**BUSINESS-INTEL.md** (Deep Analysis)
- Products/services: [list with pricing]
- Business model: [how they make money]
- Target audience: [who, in their language]

**OPPORTUNITIES.md** (Gaps and Growth Signals)
- [key gaps and opportunities found]

**CORRECTIONS.md** (Self-Improving Log)
- Empty on first run. Gets populated as the user corrects outputs over time.
```

Ask: "Anything I missed or got wrong?"

After user confirms, generate all files.

---

### Phase 6: Write Files

Generate all 9 KB files. See templates below.

**PERSONA.md template:**

```markdown
# Agent Persona — <project-name>

## Role
[What this agent does. One sentence. Specific.]

## Personality
[Tone, vibe, how it comes across. Not "professional" — specific.]

## Core Rules
- [Rule 1 — specific and actionable]
- [Rule 2]
- [Rule 3]

## Boundaries
- Never: [hard nos]
- Always ask before: [things needing approval]
- Sensitive topics: [list]

## Voice
See VOICE.md — read it before writing anything.
```

**CORRECTIONS.md template (initial — empty, ready for use):**

```markdown
# Corrections Log

This file tracks every time the user corrected an agent output. Each correction updates the source KB file directly, then gets logged here so the pattern is visible over time.

## How it works
When you correct an output, identify which KB file influenced the mistake, update that file with the correct rule or information, then log the correction below.

---

<!-- Corrections will appear here as you use the KB -->
```

**CORRECTIONS.md — how it gets used (ongoing):**

Whenever the user says something like "that's wrong", "I wouldn't say it that way", "don't do that", or corrects a specific output:

1. Identify which KB file influenced the mistake (e.g., VOICE.md had a wrong tone assumption, BUSINESS-INTEL.md had stale pricing)
2. Update that source file directly with the corrected rule or information
3. Append to CORRECTIONS.md:

```markdown
## [DATE] — [brief description of what was corrected]
- **Output type:** [content / decision / recommendation]
- **What was wrong:** [brief description]
- **Source file updated:** [e.g., VOICE.md]
- **What changed:** [old assumption or rule] replaced with [corrected rule]
```

Tell the user during the onboarding wizard: "One more thing: whenever I get something wrong and you correct me, I'll update the relevant KB file automatically. The KB gets smarter every time you correct an output."

Include SITEMAP.md in generated files only if it was generated as standalone.

---

### Phase 7: Integration

After generating all files, do this automatically:

1. Check if an AGENTS.md file exists in the workspace root.
2. If AGENTS.md exists, append this KB section (CRITICAL: on-demand loading only, never auto-load at boot):

```markdown
## Knowledge Base: <project-name>

**When working on <project-name> content**, read these files in order:
1. KNOWLEDGE BASE/<project-name>/PERSONA.md
2. KNOWLEDGE BASE/<project-name>/CONTEXT.md
3. KNOWLEDGE BASE/<project-name>/VOICE.md
4. KNOWLEDGE BASE/<project-name>/GUARDRAILS.md
5. KNOWLEDGE BASE/<project-name>/BUSINESS-INTEL.md

Read USER.md, SITEMAP.md, and OPPORTUNITIES.md only on demand when needed. **Do not load on every session** — context bloat kills productivity.
```

3. Tell the user: "I've added KB guidance to your AGENTS.md. Load these files only when you're working on <project-name> content, not on every session."

4. Also provide this Claude Code snippet for CLAUDE.md:

```markdown
## Knowledge Base: <project-name>

**Before writing content, building agents, or making decisions about this project:**

Load files in this order:
1. KNOWLEDGE BASE/<project-name>/PERSONA.md — agent rules and behavior
2. KNOWLEDGE BASE/<project-name>/CONTEXT.md — business fundamentals
3. KNOWLEDGE BASE/<project-name>/VOICE.md — writing style and tone
4. KNOWLEDGE BASE/<project-name>/GUARDRAILS.md — boundaries and sensitive topics
5. KNOWLEDGE BASE/<project-name>/BUSINESS-INTEL.md — deep business analysis

**On-demand references:**
- USER.md — personal background (load when needed)
- SITEMAP.md — site structure (load for navigation questions)
- OPPORTUNITIES.md — gaps and growth signals (load when brainstorming)

Full page content is available in `site-content/` for deep analysis when you need to reference specific pages or check existing positioning.

**Important:** Do not load the KB at boot for unrelated work. Only load when actively working on <project-name> projects.
```

---

## Update Flow

When an update trigger fires ("update kb", "refresh kb", "re-scrape kb", "kb update"):

1. List existing KBs in `KNOWLEDGE BASE/`. If multiple exist, ask: "Which project do you want to update?" and wait for confirmation.

2. Ask: "Re-scrape the site, or just update manually?"

3. **If re-scraping:**
   - Run the full scraping pipeline (Stages 1-4 above)
   - Compare new scraped content to the existing `site-content/` files
   - Note what changed (new pages, removed pages, pricing changes, new blog posts, etc.)
   - Show a diff summary before writing: "Found 3 new pages, 1 pricing change, 2 new blog posts. Update the files?"
   - Only write files after user confirms

4. **If updating manually:**
   - Ask what they want to change
   - Make targeted edits to the relevant files

5. If re-scraping found changes, note them: "Updated BUSINESS-INTEL.md (pricing change on /pricing), SITEMAP.md (3 new pages), OPPORTUNITIES.md (refreshed gaps)." No log entry needed unless the user corrects something during the update session.

---

## Voice Analysis (When Content Samples Are Provided)

When the user provides writing samples (or when blog posts are scraped), analyze for:

1. **Capitalization:** lowercase? Standard? ALL CAPS for emphasis?
2. **Sentence length:** Short and punchy? Long and flowing? Mixed?
3. **Paragraph length:** One-liners? 2-3 sentence chunks? Walls of text?
4. **Vocabulary level:** Simple and direct? Technical? Academic?
5. **Tone markers:** Humor? Sarcasm? Vulnerability? Authority?
6. **Structural patterns:** Lists? Fragments? Questions? Stories?
7. **Unique habits:** Parenthetical asides? Specific punctuation? Catchphrases?
8. **What's missing:** What do they NOT do that most content does?

Use this to populate VOICE.md with specific, actionable observations. Not "conversational tone" but "writes in lowercase, uses fragments, averages 8 words per sentence, opens with a bold claim."

---

## File Generation Guidelines

1. **Fill with real answers.** Every section should contain actual information, not placeholder text.
2. **Be opinionated.** "Never use corporate jargon" beats "Consider avoiding overly formal language."
3. **Be specific.** "Banned words: leverage, synergy, ecosystem" beats "Avoid buzzwords."
4. **Keep it scannable.** Bullet points over paragraphs. Short sections. Headers that describe content.
5. **Mark unknowns.** If something was skipped: `<!-- TODO: fill in later -->`
6. **No em dashes.** Use commas, periods, or restructure.

---

## Firecrawl REST API Reference

All scraping uses the Firecrawl REST API (`https://api.firecrawl.dev/v1/`). The API key is passed via the `Authorization: Bearer` header.

| Endpoint | Method | What it does | Cost |
|----------|--------|-------------|------|
| `/v1/map` | POST | Discover all URLs on a site | Free/near-free |
| `/v1/crawl` | POST | Start a full site crawl (async, returns job ID) | ~1 credit/page |
| `/v1/crawl/<id>` | GET | Check crawl status / get results | Free |
| `/v1/scrape` | POST | Scrape a single URL to markdown | 1 credit |

**Map request body:** `{"url": "<url>", "limit": 500}`
**Crawl request body:** `{"url": "<url>", "limit": <N>, "scrapeOptions": {"formats": ["markdown"]}}`
**Scrape request body:** `{"url": "<url>", "formats": ["markdown"]}`

**Crawl polling:** The crawl endpoint returns `{"id": "..."}`. Poll `GET /v1/crawl/<id>` every 10 seconds until `status` is `"completed"`.

---

## Caching

- All raw Firecrawl data goes in `.firecrawl/<project-slug>/`
- If `.firecrawl/<project-slug>/crawl-raw.json` exists and is less than 7 days old, offer to reuse it
- The `site-content/` directory in the KB is the processed output, not the cache
- Social profile scrapes cached in `.firecrawl/<project-slug>/social/`
- Important links cached in `.firecrawl/<project-slug>/links/`
- API key stored in `.firecrawl/api-key.txt`

---

## Error Recovery

| Scenario | What to do |
|----------|-----------|
| No API key | Walk through Phase 0 API key setup. Save to `.firecrawl/api-key.txt`. |
| API returns 401 | Key is invalid or expired. Ask user for a new key. |
| Crawl times out | Save partial results. Note which pages were missed. Continue with what you have. |
| Social scrape fails (anti-bot) | Note "limited extraction" for that profile. Continue with other sources. |
| Rate limited (429) | Wait 30 seconds and retry. If it happens 3 times, stop and continue with what you have. |
| No website URL provided | Skip all scraping. All questions become mandatory. Still produces all 9 KB files. |

---

## Storage Structure

```
KNOWLEDGE BASE/<project-name>/
  PERSONA.md
  CONTEXT.md
  USER.md
  VOICE.md
  GUARDRAILS.md
  SITEMAP.md          (only if 20+ pages)
  BUSINESS-INTEL.md
  OPPORTUNITIES.md
  CORRECTIONS.md
  site-content/
    homepage.md
    about.md
    pricing.md
    blog-post-slug.md
    ...

.firecrawl/
  api-key.txt
  <project-slug>/
    map-result.json
    crawl-job.json
    crawl-raw.json
    social/
      linkedin.md
      twitter.md
      youtube.md
      instagram.md
    links/
      docs.md
      portfolio.md
      ...
```
