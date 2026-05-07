---
name: content-pipeline
description: "Use when creating content end-to-end: ideation, drafting, editing, humanizing, and publishing across blogs, social media, and newsletters."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [content, writing, publishing, blog, social-media, newsletter]
    related_skills: [humanizer, xurl, youtube-content, ideation]
---

# Content Pipeline

## Overview

End-to-end content creation: from raw idea to published piece. Covers blogs, Twitter/X threads, LinkedIn posts, newsletters, and long-form articles. Each stage has its own quality gate — nothing ships half-baked.

## When to Use

- Creating a blog post, article, or long-form piece
- Writing a Twitter/X thread or social media post
- Producing a newsletter edition
- Repurposing content across platforms
- Going from idea → draft → edit → publish

Don't use for:
- Quick one-off social posts (just write it)
- Research-only tasks (use deep-research skill)
- Code documentation (use standard dev practices)

## Pipeline Stages

```
IDEA → OUTLINE → DRAFT → EDIT → HUMANIZE → FORMAT → PUBLISH
```

Each stage feeds the next. Skip stages at your peril.

### Stage 1: Ideation

Sources for content ideas:
- **Deep research** on a topic — what's underserved?
- **YouTube transcripts** — extract key insights, reframe
- **Reddit/HN questions** — what are people asking?
- **Trending topics** — what's the conversation?
- **Personal experience** — lessons learned, war stories

```bash
# Use the ideation skill for structured brainstorming
# Use deep-research for topic validation
# Use youtube-content to extract from video content
```

Output: 1-3 content ideas with working titles and angle.

### Stage 2: Outline

Before writing a single paragraph, lock the structure:

```markdown
# [Working Title]

## Angle
One line: what's the unique take?

## Structure
1. Hook — why should anyone care?
2. Context — what's the background?
3. Core insight — the main point
4. Evidence — data, examples, stories
5. So what? — practical takeaway
6. Close — memorable ending

## Key Points
- Point 1
- Point 2
- Point 3

## Sources / References
- [Source 1]
- [Source 2]
```

### Stage 3: Draft

Write without editing. Get it down.

Rules:
- **Write fast, edit slow.** Don't polish sentences mid-draft.
- **Hit the structure.** Follow the outline. Tangents are for later.
- **Voice matters.** Match the platform (see Platform Voices below).
- **Length target.** Know your word count before you start.

| Format | Target Length |
|---|---|
| Tweet | 280 chars |
| Thread | 5-10 tweets |
| LinkedIn post | 150-300 words |
| Blog post | 800-1500 words |
| Long-form article | 2000-4000 words |
| Newsletter edition | 500-1000 words |

### Stage 4: Edit

The real writing happens here.

Checklist:
- [ ] **Hook** — first line grabs attention? Would YOU keep reading?
- [ ] **Clarity** — can you say it in fewer words? Cut ruthlessly.
- [ ] **Flow** — does each paragraph lead to the next? No jumps.
- [ ] **Evidence** — every claim backed up? No hand-waving.
- [ ] **Ending** — does it land? No limp conclusions.
- [ ] **Consistency** — tone, tense, POV consistent throughout?
- [ ] **SEO** (blog only) — keyword in title, H1, first 100 words, meta description

### Stage 5: Humanize

Load the `humanizer` skill. Strip the AI tells:

- Remove "In conclusion," "It's important to note," "Furthermore"
- Kill hedge language: "somewhat," "arguably," "it could be said"
- Replace jargon with plain language where possible
- Add specific, concrete details (not generic examples)
- Make it sound like a person wrote it, not a model

### Stage 6: Format for Platform

Each platform has its own conventions:

**Blog (Markdown)**
```markdown
# Title (H1)

Opening paragraph — hook.

## Section 1 (H2)

Body text with **bold** for emphasis.

> Pull quotes for key insights.

- Bullet points for lists
- Keep paragraphs short (2-3 sentences)

## Conclusion

End with a question or call to action.
```

**Twitter/X Thread**
```
1/ Hook tweet — bold claim or question

2-8/ Each tweet = one point
- One idea per tweet
- End with a transition ("But here's the thing...")
- Add numbers (2/ 3/ etc.)

9/ Summary tweet — the TL;DR

10/ CTA — follow, share, link
```

**LinkedIn Post**
```
Hook line (no more than 2 lines before "see more" cutoff)

Body with line breaks.
Short paragraphs.
No bullets — narrative flow.

CTA at the bottom.
Relevant hashtags (3-5 max).
```

**Newsletter**
```
Subject line: [curiosity gap or clear value prop]

Quick intro — what's in this edition.

---

## Section 1
Content...

## Section 2
Content...

---

That's it. [Sign-off]

P.S. [One extra thing — a link, a thought, a recommendation]
```

### Stage 7: Publish

```bash
# Blog — depends on platform
# If using a static site (Hugo/Jekyll):
hugo new post/my-post.md
# Edit content, then:
hugo deploy  # or git push

# Twitter/X — use xurl skill
xurl tweet "Your tweet text here"

# Thread — use xurl skill for thread posting
# (load xurl skill for full thread syntax)

# Newsletter — depends on platform (Mailchimp, ConvertKit, etc.)
```

## Content Repurposing Matrix

One piece of content → multiple formats:

| Source | Blog Post | Thread | LinkedIn | Newsletter |
|---|---|---|---|---|
| Deep research | Full article | Key findings thread | Executive summary | Research digest |
| YouTube video | Transcript-based post | Top 5 takeaways | One key insight | "This week I watched..." |
| Personal story | Full narrative | Story thread | Lesson learned | Behind the scenes |
| Technical tutorial | Step-by-step guide | Tips thread | "Here's what I learned" | Tool spotlight |

## Common Pitfalls

1. **Skipping the outline.** Writing without structure = rambling. Always outline first.

2. **Editing while drafting.** Kills momentum. Draft fast, then edit.

3. **Forgetting to humanize.** AI-written content has tells. Always run through humanizer before publishing.

4. **Platform-agnostic formatting.** A LinkedIn post is not a blog paragraph. Format for the platform.

5. **Weak hooks.** The first line determines if anyone reads the rest. Spend 50% of your editing time on the first 2 sentences.

6. **No CTA.** Every piece of content should have a next step for the reader — even if it's just "think about this."

7. **Publishing without a final read-aloud.** Read it out loud. If it sounds awkward, it reads awkward.

## Verification Checklist

- [ ] Content follows the full pipeline (idea → outline → draft → edit → humanize → format → publish)
- [ ] Hook passes the "would I keep reading?" test
- [ ] Humanized — no AI tells remaining
- [ ] Formatted for the target platform
- [ ] Word count in the target range
- [ ] Every claim has evidence
- [ ] Ending lands (not a limp conclusion)
- [ ] CTA included
