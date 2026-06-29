---
name: afrexai-seo-content-engine
description: Complete SEO content creation system for AI agents. Research keywords, analyze competitors, write optimized articles, and track rankings — all through natural conversation. No APIs required.
metadata:
  openclaw:
    version: "1.0.0"
    author: "AfrexAI"
    license: "MIT"
    tags: ["seo", "content", "writing", "blog", "marketing", "articles", "keywords"]
    category: "marketing"
---

# SEO Content Engine

Turn your AI agent into a full SEO content team. Research → Plan → Write → Optimize → Publish — all in natural language.

No APIs. No subscriptions. Just smart agent workflows using web search and structured frameworks.

---

## 1. Keyword Research Framework

### Seed Expansion
When given a topic, expand it systematically:

1. **Core keyword**: The main term (e.g., "project management software")
2. **Long-tail variants**: Add modifiers — best, top, free, for [audience], vs, alternative, review, how to, guide
3. **Question keywords**: How/What/Why/When/Where + core keyword
4. **Problem keywords**: What pain does this solve? ("team missing deadlines", "project overruns")
5. **Comparison keywords**: "[Product A] vs [Product B]", "[Product] alternatives"

### Search Intent Classification

For each keyword, classify intent:

| Intent | Signal Words | Content Type |
|--------|-------------|--------------|
| **Informational** | how to, what is, guide, tutorial, why | How-to guide, explainer, tutorial |
| **Commercial** | best, top, review, comparison, vs | Listicle, comparison, review |
| **Transactional** | buy, pricing, discount, free trial, download | Product page, landing page |
| **Navigational** | [brand name], login, support, docs | Brand page (skip — low value) |

### Competition Analysis (Using Web Search)

For each target keyword:

```
Step 1: Search the exact keyword
Step 2: Analyze top 5 results:
  - What type of content ranks? (listicle, guide, review)
  - What's the average word count? (check article length)
  - What subtopics do ALL top results cover? (table stakes)
  - What subtopics do NONE cover? (your opportunity)
  - Who wrote them? (big brand = harder, niche blog = beatable)
Step 3: Score opportunity:
  - Mostly forums/Reddit in top 5 = HIGH opportunity (no dedicated content)
  - All big brands (Forbes, HubSpot) = LOW opportunity (hard to outrank)
  - Mix of niche sites = MEDIUM opportunity (winnable with better content)
```

### Keyword Prioritization Matrix

Score each keyword (1-5 per dimension):

| Dimension | 1 (Low) | 5 (High) |
|-----------|---------|----------|
| **Relevance** | Tangentially related | Core topic |
| **Intent match** | Informational only | Commercial/transactional |
| **Competition gap** | All big brands | Forums, thin content |
| **Business value** | No conversion path | Direct product tie-in |
| **Content feasibility** | Need proprietary data | Can write from expertise |

**Priority**: Score ≥ 18 = write immediately. 13-17 = queue. < 13 = skip.

---

## 2. Content Planning

### Content Brief Template

Before writing ANY article, create this brief:

```markdown
# Content Brief: [Title]

**Target keyword**: [primary keyword]
**Secondary keywords**: [3-5 related terms to weave in naturally]
**Search intent**: [informational/commercial/transactional]
**Target word count**: [based on competitor analysis]
**Content type**: [guide/listicle/comparison/review/case study]

## Audience
- Who is searching this? [persona]
- What do they already know? [beginner/intermediate/advanced]
- What do they want to DO after reading? [action]

## Must-Cover Subtopics (from competitor analysis)
1. [Topic all competitors cover — table stakes]
2. [Topic all competitors cover — table stakes]
3. ...

## Differentiation Angles (our edge)
1. [Topic NO competitor covers — our advantage]
2. [Fresh data/perspective they're missing]
3. [Practical template/tool they don't provide]

## Internal Links
- Link TO: [existing content on your site]
- Link FROM: [update these older articles to link to this one]

## CTA
- Primary: [what should the reader do?]
- Secondary: [email signup, related article, tool]
```

### Content Calendar Structure

Organize articles into clusters:

```
PILLAR PAGE: "Complete Guide to [Topic]" (3,000-5,000 words)
├── CLUSTER: "How to [Subtopic A]" (1,500-2,500 words)
├── CLUSTER: "Best [Subtopic B] for [Audience]" (2,000-3,000 words)
├── CLUSTER: "[Subtopic C] vs [Subtopic D]" (1,500-2,000 words)
├── CLUSTER: "[Subtopic E] Template + Examples" (1,000-1,500 words)
└── CLUSTER: "Common [Topic] Mistakes" (1,500-2,000 words)
```

Each cluster article links back to the pillar. The pillar links to all clusters. This builds topical authority.

---

## 3. Writing Framework

### Article Structure (The HBCFC Formula)

Every article follows this skeleton:

#### H — Hook (first 100 words)
- Open with a specific stat, question, or bold claim
- NO generic intros ("In today's fast-paced world...")
- State what the reader will get and why it matters
- Include primary keyword naturally in first paragraph

#### B — Bridge (setup the problem)
- Acknowledge the reader's pain or goal
- Show you understand their situation
- Create tension: "Most advice on X misses Y"
- Transition to your solution

#### C — Core Content (the meat — 80% of word count)
- Use H2s for major sections, H3s for subsections
- Every H2 should work as a standalone answer to a question
- Include at minimum:
  - **One data point or stat per section** (search for current data)
  - **One practical example or template** per major section
  - **One "pro tip" callout** per 500 words
  - **Bullet lists** for scannable items (readers skim)
- Natural keyword placement: primary keyword in 2-3 H2s, secondary keywords in H3s and body

#### F — FAQ Section (5-7 questions)
- Pull from "People Also Ask" in search results
- Answer concisely (40-60 words each)
- Include primary/secondary keywords naturally
- This section generates FAQ rich snippets in Google

#### C — Conclusion + CTA (final 150-200 words)
- Summarize 3 key takeaways (bullet points)
- Restate the primary keyword naturally
- Clear call to action (one CTA only — don't dilute)

### Writing Rules

1. **Sentence variety**: Mix short (5-8 words) with medium (12-18) and occasional long (20-25). Never three long sentences in a row.
2. **Paragraph length**: 2-4 sentences max. One-sentence paragraphs are fine for emphasis.
3. **Active voice**: "The tool analyzes data" not "Data is analyzed by the tool"
4. **Specific > vague**: "Increased conversions by 34%" not "significantly improved results"
5. **No filler phrases**: Cut "it's important to note that", "in order to", "at the end of the day"
6. **Transition words**: Use sparingly and vary them. Not every paragraph needs "However" or "Additionally".
7. **Read-aloud test**: If it sounds robotic when read aloud, rewrite it.

### Keyword Integration (Natural Placement)

```
✅ DO:
- Primary keyword in title (H1)
- Primary keyword in first 100 words
- Primary keyword in 1-2 H2 headings
- Primary keyword in conclusion
- Secondary keywords scattered in body (1-2 each)
- Semantic variants throughout (synonyms, related phrases)

❌ DON'T:
- Use exact keyword more than 1x per 200 words
- Force keywords into headings where they sound unnatural
- Use the same keyword phrase 3x in one paragraph
- Stuff keywords in image alt text unnaturally
```

---

## 4. On-Page SEO Checklist

Run this checklist on every article before publishing:

### Title Tag (H1)
- [ ] Contains primary keyword (preferably near the beginning)
- [ ] Under 60 characters (won't get truncated in search)
- [ ] Compelling — would YOU click this in search results?
- [ ] Includes a power word (ultimate, complete, proven, essential)
- [ ] Includes current year if relevant (e.g., "Best X in 2026")

### Meta Description
- [ ] 150-160 characters
- [ ] Contains primary keyword
- [ ] Includes a benefit or outcome
- [ ] Has a call to action ("Learn how", "Discover", "Find out")
- [ ] Unique (not duplicated from another page)

### URL Slug
- [ ] Short (3-5 words)
- [ ] Contains primary keyword
- [ ] No stop words (the, and, of, etc.)
- [ ] Hyphens between words
- [ ] Example: `/best-project-management-tools`

### Headings
- [ ] Only ONE H1 (the title)
- [ ] H2s for major sections (5-8 per article)
- [ ] H3s for subsections within H2s
- [ ] At least 2 H2s contain primary or secondary keywords
- [ ] Headings are descriptive (not "Part 1", "Section A")

### Content
- [ ] Minimum 1,500 words (2,000+ for competitive keywords)
- [ ] Primary keyword appears 4-8 times naturally
- [ ] Secondary keywords appear 1-3 times each
- [ ] At least one internal link per 500 words
- [ ] At least 2-3 external links to authoritative sources
- [ ] Images every 300-500 words (stock photos, diagrams, screenshots)
- [ ] All images have descriptive alt text

### Technical
- [ ] Schema markup defined (Article type at minimum)
- [ ] Table of contents for articles over 2,000 words
- [ ] Mobile-friendly formatting (no wide tables, reasonable image sizes)
- [ ] No broken links

### Schema Markup Template (Article)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Title]",
  "description": "[Meta description]",
  "author": {
    "@type": "Person",
    "name": "[Author]"
  },
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "publisher": {
    "@type": "Organization",
    "name": "[Site Name]"
  }
}
```

### FAQ Schema Template

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 1]"
      }
    }
  ]
}
```

---

## 5. Content Types — Templates

### Template A: "Best [X] for [Y]" Listicle

```markdown
# Best [X] for [Y] in [Year]

[Hook: Stat about the problem or market size]
[Bridge: Why choosing the right X matters for Y]

## Quick Comparison Table
| Product | Best For | Price | Rating |
|---------|----------|-------|--------|

## 1. [Product Name] — Best Overall
### Why It Stands Out
### Key Features
### Pricing
### Who It's For
### Downsides

[Repeat for 7-10 products]

## How We Evaluated
[Methodology — builds trust]

## FAQ
## Final Verdict
```

### Template B: "How to [X]" Guide

```markdown
# How to [X]: Step-by-Step Guide ([Year])

[Hook: What you'll achieve by the end]
[Bridge: Common mistakes people make with X]

## What You'll Need
[Prerequisites, tools, time estimate]

## Step 1: [Action Verb + Outcome]
[Detailed instructions]
[Screenshot or example]
[Pro tip callout]

[Repeat for each step]

## Common Mistakes to Avoid
## Advanced Tips
## FAQ
## Next Steps
```

### Template C: "[X] vs [Y]" Comparison

```markdown
# [X] vs [Y]: Which Is Better in [Year]?

[Hook: The core difference in one sentence]
[Bridge: When to choose X vs Y]

## Quick Verdict
[TL;DR comparison — who should choose what]

## Overview Comparison
| Feature | X | Y |
|---------|---|---|

## [Feature Category 1]: [X] vs [Y]
### How [X] Handles It
### How [Y] Handles It
### Winner: [X/Y] because [reason]

[Repeat for 5-7 feature categories]

## Pricing Breakdown
## Who Should Choose [X]
## Who Should Choose [Y]
## FAQ
## Our Recommendation
```

### Template D: Ultimate Guide (Pillar Page)

```markdown
# The Ultimate Guide to [Topic] ([Year])

[Hook: Why this topic matters now]
[Bridge: What this guide covers that others don't]

## Table of Contents

## Chapter 1: [Foundational Concept]
[Explain the basics — link to cluster article for deep dive]

## Chapter 2: [Core Strategy]
[Main approach — link to how-to cluster]

## Chapter 3: [Tools & Resources]
[Curated list — link to comparison cluster]

## Chapter 4: [Advanced Techniques]
[Expert-level tactics]

## Chapter 5: [Common Mistakes]
[What to avoid — link to mistakes cluster]

## Chapter 6: [Case Studies / Examples]
[Real-world applications]

## FAQ (10-15 questions for this one)
## Conclusion + What to Do Next
```

---

## 6. Content Optimization Workflow

### Pre-Publish Optimization

```
1. READABILITY CHECK
   - Flesch Reading Ease: aim for 60-70 (8th-9th grade level)
   - No paragraphs over 4 sentences
   - No sentences over 25 words without a break
   - Subheading every 250-300 words

2. KEYWORD DENSITY CHECK
   - Primary keyword: 0.5-1.5% density (not higher)
   - If over 1.5%: replace some instances with synonyms
   - If under 0.5%: add naturally in body paragraphs

3. LINK AUDIT
   - Internal links: 3-5 per 1,500 words minimum
   - External links: 2-3 to authoritative sources (.gov, .edu, industry leaders)
   - No orphan pages (every article linked from at least one other)

4. MEDIA CHECK
   - Featured image with alt text
   - In-content images/diagrams every 300-500 words
   - Tables where data comparison exists
   - Callout boxes for key takeaways

5. CTA CHECK
   - One primary CTA (not competing CTAs)
   - CTA appears at end and optionally mid-article
   - CTA is specific ("Download the template" not "Learn more")
```

### Post-Publish Actions

```
1. INDEX REQUEST
   - Submit URL to Google Search Console
   - Share on social media (generates initial signals)

2. INTERNAL LINKING UPDATE
   - Find 3-5 existing articles related to this topic
   - Add contextual links from those articles to this new one
   - This distributes link equity and helps discovery

3. MONITOR (Week 1-4)
   - Track ranking position for target keyword
   - Monitor organic impressions in Search Console
   - Check bounce rate and time on page

4. UPDATE CYCLE
   - Refresh content every 6-12 months
   - Update stats, add new sections, improve based on search performance
   - Articles that rank page 2 (positions 11-20) = highest ROI to update
```

---

## 7. Content Scoring Rubric

Score every article before publishing (aim for 85+):

| Criteria | Points | How to Score |
|----------|--------|-------------|
| **Keyword optimization** | /15 | Title + H2s + natural body placement |
| **Content depth** | /20 | Covers all subtopics competitors cover + unique angles |
| **Readability** | /15 | Short paragraphs, varied sentences, scannable |
| **Practical value** | /15 | Templates, examples, actionable steps (not just theory) |
| **Structure** | /10 | Clear H2/H3 hierarchy, logical flow, TOC for long articles |
| **Internal links** | /5 | 3+ contextual internal links |
| **External links** | /5 | 2+ authoritative external references |
| **Media** | /5 | Images, tables, or diagrams present |
| **Meta tags** | /5 | Title < 60 chars, description 150-160 chars, both include keyword |
| **CTA clarity** | /5 | Single clear CTA with specific action |
| **TOTAL** | /100 | |

**Score guide:**
- 90-100: Publish immediately — strong ranking potential
- 80-89: Publish with minor tweaks noted
- 70-79: Needs revision — likely missing depth or optimization
- Below 70: Rewrite — significant gaps

---

## 8. SEO Agent Commands

Use natural language to trigger these workflows:

| Command | What It Does |
|---------|-------------|
| "Research keywords for [topic]" | Full keyword expansion + prioritization matrix |
| "Analyze competitors for [keyword]" | Top 5 SERP analysis with content gaps |
| "Create a content brief for [keyword]" | Full brief using the template above |
| "Write an article about [topic]" | Full article using HBCFC framework + on-page checklist |
| "Optimize this article for [keyword]" | Run the optimization workflow on existing content |
| "Score this article" | Apply the 100-point scoring rubric |
| "Plan a content cluster for [topic]" | Pillar + 5-6 cluster articles with internal linking map |
| "Generate schema for this article" | Article + FAQ JSON-LD markup |
| "Create a [listicle/guide/comparison]" | Use the specific template for that content type |
| "Audit my SEO" | Full on-page checklist against provided content |

---

## 9. Advanced Techniques

### Semantic SEO (Topic Authority)
Don't just target one keyword — own the entire topic:
1. Map ALL subtopics in your niche using keyword research
2. Create content for each subtopic (content cluster model)
3. Interlink everything with contextual anchor text
4. Google rewards sites that comprehensively cover a topic

### Featured Snippet Optimization
To win featured snippets (position 0):
- **Paragraph snippets**: Answer the question in 40-60 words directly under an H2 that IS the question
- **List snippets**: Use ordered/unordered lists with clear H2
- **Table snippets**: Use HTML tables with clear headers
- Target keywords where current snippets are weak or missing

### Content Freshness Signals
Google favors fresh content for time-sensitive queries:
- Include the current year in titles where relevant
- Update stats and data annually
- Add "Last updated: [date]" to articles
- Republish with new publish date after major updates

### E-E-A-T Signals (Experience, Expertise, Authority, Trust)
- **Experience**: Include first-hand examples ("When I tested this...")
- **Expertise**: Cite specific data, reference methodology
- **Authority**: Link to/from authoritative sources, get cited by others
- **Trust**: Clear author bios, about page, contact info, HTTPS, privacy policy

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI agent infrastructure for businesses that ship.*
