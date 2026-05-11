# Init-KB Walkthrough (OpenClaw Version)

What this skill does, how it works, and what you get at the end.

---

## What It Is

A conversational skill that builds a complete knowledge base for any project, business, or client. It scrapes their website + social profiles via the Firecrawl API, runs a deep analysis on everything it finds, then walks you through a Q&A to fill in the gaps. The result is 7 structured markdown files that give any AI agent full context on who you are, what your business does, how you write, and what the rules are.

## Why It Matters

Without a knowledge base, every AI session starts from zero. It doesn't know your business, your voice, your pricing, your competitors, or your boundaries. With a KB, every output is informed from the first prompt. Better content, better decisions, fewer corrections.

---

## What You Get

7 files written to `KNOWLEDGE BASE/<project-name>/`:

| File | What's Inside |
|------|--------------|
| **SOUL.md** | Agent identity. How the AI should behave, what rules it follows, what its personality is. This is the OpenClaw agent's core identity file. |
| **CONTEXT.md** | Business context. What the business does, who it serves, what it's optimizing for, competitors, non-negotiables. |
| **USER.md** | The person behind the business. Background, origin story, personality, what makes them different. |
| **VOICE.md** | Writing style rules. Tone, vocabulary, banned words, sentence patterns, formatting habits. Built from real writing samples. |
| **GUARDRAILS.md** | Boundaries. Things the AI should never say, sensitive topics, legal constraints, what needs human approval before going out. |
| **SITEMAP.md** | Full site structure. Every page URL organized by category (products, blog, company, legal). Plus architecture notes like content gaps and orphan pages. |
| **BUSINESS-INTEL.md** | The deep analysis. Pricing, features, services, target audience, business model, content strategy, tech stack, team info, competitive signals, and gaps/opportunities. |

Plus a `site-content/` folder with every scraped page saved as its own markdown file for on-demand deep reading.

---

## How It Works (Step by Step)

### Step 1: You Trigger It

Say something like:
- "init kb"
- "build a knowledge base"
- "create kb for [business name]"
- "set up kb"

### Step 2: Two Setup Questions

The agent asks you two things (one at a time, never stacked):

1. **"What's the project or business name?"** This becomes the folder name.
2. **"Got a website URL? Social profiles? Other important links?"** Drop everything here. LinkedIn, X, YouTube, Instagram, docs, portfolio, press pages. If you have nothing yet, say "none" and it skips scraping.

### Step 3: API Key Check

The agent needs a Firecrawl API key to scrape. It checks in this order:
1. `FIRECRAWL_API_KEY` environment variable
2. `.firecrawl/api-key.txt` in the workspace
3. Asks you for it (and saves it for next time)

### Step 4: Cache Check

If you've already scraped this site in the last 7 days, it asks: "Want to reuse the cached data or re-scrape?" Saves credits.

### Step 5: The Scraping Pipeline (4 Stages)

**Stage 1: Discover URLs**
Uses Firecrawl's Map API to find every page on the site. Shows you the count and estimated credit cost. You approve before it spends anything.

**Stage 2: Crawl the Full Site**
Crawls every page (or a limited set if you chose). Extracts all content as markdown. Each page becomes its own file in `site-content/`. This is async, so it polls every 10 seconds and tells you "Crawling... this might take a minute."

**Stage 3: Scrape Social Profiles + Extra Links**
Individually scrapes each social profile and important link you provided. LinkedIn, X, YouTube, Instagram, docs, portfolio, whatever. Saves them separately.

**Stage 4: Deep Analysis Pass**
This is the big one. The agent reads EVERY scraped page and extracts:

1. **Products & Services** - names, descriptions, pricing, features, tiers, who each is for
2. **Business Model** - how they make money, revenue streams, funnel structure, CTAs
3. **Target Audience** - exact customer language, pain points, aspirations, testimonials
4. **Brand Positioning** - differentiators, trust signals, authority markers
5. **Content Strategy** - blog topics, formats, frequency, lead magnets, email capture
6. **Tech Stack** - platform, payment processor, email provider, community tools
7. **Team & People** - founder info, team members, hiring signals
8. **Legal & Compliance** - privacy policy, terms, disclaimers
9. **Voice & Messaging** - headline formulas, CTA patterns, recurring phrases, tone shifts
10. **Gaps & Opportunities** - thin content, missing pages, broken journeys, opportunities

All of this goes into BUSINESS-INTEL.md. The agent also pre-fills answers for the conversational phases so you don't have to repeat what was already on the site.

**After scraping, you see a summary like:**
"I crawled 42 pages and scraped 3 social profiles. Here's what I know about your business: [products, audience, positioning, content strategy, trust signals, gaps]. Now let me confirm a few things I couldn't find on the site."

### Step 6: Conversational Q&A (4 Phases, ~10-15 Questions)

The agent walks you through questions one at a time. If the scrape already answered something, it shows you what it found and asks to confirm instead of asking from scratch.

**Phase 1: Business Type** (1 question)
Auto-detected from the site if possible. "This looks like a Creator / Personal Brand. Right?"

**Phase 2: The Person** (3-5 questions)
- Your background and what makes you different
- Your origin story
- What you care about / what pisses you off
- Writing samples (skipped if blog was scraped)
- Banned words and phrases (always asked)

**Phase 3: The Business** (3-5 questions)
- What you do and who it's for
- What you're optimizing for right now
- Competitors and differentiation
- Non-negotiables
- Plus bonus questions based on business type (SaaS, agency, e-com, etc.)

**Phase 4: The AI Agent** (3 questions)
- What should AI agents be able to do with this KB?
- What should AI never do? (hard boundaries)
- Legally sensitive topics or approval gates?

Questions can be skipped anytime. Skipped items get marked `<!-- TODO: fill in later -->`.

### Step 7: Review

Before generating anything, the agent shows you a summary of what it captured, organized by file. You can correct or add anything before it writes.

### Step 8: File Generation

All 7 files are generated from templates filled with your actual answers and scraped data. No placeholder fluff. Opinionated, specific, scannable.

### Step 9: Config Snippet

The agent gives you two snippets to paste into your project config:

**For Claude Code (CLAUDE.md):** A read order for the KB files.
**For OpenClaw (AGENTS.md):** A boot sequence addition so agents load the KB at session start.

---

## Where Everything Lives

```
KNOWLEDGE BASE/<project-name>/
  SOUL.md              <- agent identity
  CONTEXT.md           <- business context
  USER.md              <- the person
  VOICE.md             <- writing style
  GUARDRAILS.md        <- boundaries
  SITEMAP.md           <- site structure
  BUSINESS-INTEL.md    <- deep analysis
  site-content/        <- every page as markdown
    homepage.md
    about.md
    pricing.md
    blog-*.md
    ...

.firecrawl/
  api-key.txt          <- saved API key
  <project-slug>/
    map-result.json    <- URL discovery results
    crawl-job.json     <- crawl job ID
    crawl-raw.json     <- full crawl data (cache)
    social/            <- scraped social profiles
    links/             <- scraped extra links
```

---

## Error Handling

| What Happens | What It Does |
|-------------|-------------|
| No API key | Asks you for it, saves for next time |
| Invalid key (401) | Asks for a new one |
| Crawl times out | Saves partial results, continues with what it has |
| Social scrape blocked (anti-bot) | Notes "limited extraction", moves on |
| Rate limited (429) | Waits 30 seconds, retries up to 3 times |
| No website provided | Skips scraping, asks all questions manually |

---

## How It Uses Firecrawl Credits

| Action | Cost |
|--------|------|
| Map (discover URLs) | Free / near-free |
| Crawl (full site) | ~1 credit per page |
| Scrape (social/links) | 1 credit per URL |

The agent always shows you the estimated cost and asks for approval before crawling. You can limit the number of pages to control spend.

---

## Key Design Decisions

- **One question per message.** Never stacked. Non-technical users freeze on multi-question prompts.
- **Show before ask.** If the scrape found it, show it and confirm. Don't re-ask what the site already told us.
- **Skip-friendly.** "I don't know" or "skip" is always valid. Skipped items get a TODO marker.
- **Scrape first, ask second.** The more the scrape finds, the fewer questions you answer.
- **7-day cache.** Avoids re-scraping if you run it again soon.
- **No em dashes.** Ever. In any generated file.
