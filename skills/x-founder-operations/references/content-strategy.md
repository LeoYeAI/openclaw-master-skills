# Content Strategy

A systematic framework for creating high-performing X content. This replaces ad-hoc posting with a disciplined pipeline from ideation to measurement.

---

## Five Content Pillars

Every piece of content should map to one of these pillars. The mix ratio is configurable in [goals](../config/goals.example.json) (default: 40/25/25/10).

### Pillar 1: Technical Depth (40% — Value)

Deep insights, tutorials, analysis, and non-obvious observations about your domain.

**Why it works**: Establishes authority. Generates bookmarks (high algorithm weight) and long dwell time. Attracts your ideal audience.

**Formats**:
- Technical insight with concrete example
- Tutorial or how-to (step-by-step)
- Tool/framework comparison
- Architecture or design decision analysis
- Code snippet with explanation
- Data analysis with visualization

**Template — Technical Insight**:
```
[Bold technical claim or non-obvious observation]

[Specific example or proof — screenshot, code, data]

[Why this matters for your audience]

[Optional: CTA or question to prompt discussion]
```

**Template — Tutorial Thread**:
```
Tweet 1: [Hook — "Here's how to X in Y steps"]
Tweet 2-N: [One step per tweet, with screenshot or code]
Final: [Summary + CTA — "Bookmark for later" or "Follow for more"]
```

### Pillar 2: Industry Pulse (25% — Opinion)

Hot takes, predictions, trend analysis, and contrarian perspectives on your industry.

**Why it works**: Drives engagement through agreement and disagreement. Shows you're plugged into the industry. Generates replies and quote tweets.

**Formats**:
- Contrarian take on popular opinion
- Prediction with reasoning
- Reaction to industry news (within 2 hours of breaking)
- "Everyone's talking about X, but the real story is Y"
- Comparison of competing approaches

**Template — Contrarian Take**:
```
[Conventional wisdom] is wrong.

[Your contrarian position]

[Evidence or reasoning — 2-3 points]

[What this means going forward]
```

**Template — Rapid Reaction**:
```
[Breaking news reference]

[Your immediate analysis — what most people miss]

[What this means for your space specifically]

[Optional: link to deeper analysis in reply]
```

### Pillar 3: Builder's Journey (25% — Story)

Behind-the-scenes content, build-in-public updates, decisions, failures, and lessons learned.

**Why it works**: Builds emotional connection. Humanizes you beyond your expertise. Creates loyal followers who feel invested in your journey.

**Formats**:
- Build-in-public update with real metrics
- Decision and the reasoning behind it
- Failure post-mortem (what went wrong, what you learned)
- Milestone celebration with context
- "Day in the life" moments
- Founder/builder reflections

**Template — Build-in-Public Update**:
```
[Product/Project] week [N] update:

[Metric 1]: [number] → [number] ([change])
[Metric 2]: [number] → [number] ([change])

What worked: [specific thing]
What didn't: [specific thing]
Next week: [focus area]

[Screenshot of dashboard/metrics]
```

**Template — Lesson Learned**:
```
[Mistake or unexpected outcome]

I thought [assumption].
Reality: [what actually happened].

The lesson: [actionable takeaway]

[Optional: what you're doing differently now]
```

### Pillar 4: Community Value (10% — Engagement)

Questions, polls, resource shares, and content designed to spark conversation.

**Why it works**: Generates replies (highest algorithm weight). Builds community. Surfaces insights from your audience. Shows you value others' perspectives.

**Formats**:
- Open-ended question about your domain
- "Which do you prefer: A or B?"
- Resource roundup (tools, articles, repos)
- Community highlight (sharing others' great work)
- Poll with follow-up analysis

**Template — Engaging Question**:
```
[Specific, answerable question about your domain]

(Genuinely curious — I'm [context for why you're asking])
```

**Template — Resource Share**:
```
[N] [tools/resources/articles] I've been using for [specific use case]:

1. [Name] — [one-line why it's good]
2. [Name] — [one-line why it's good]
...

What would you add? 👇
```

### Pillar 5: Personal Touch (woven into all pillars)

Humor, personality, cultural references, and human moments. Not a separate category — this is the texture layered into every pillar.

**Why it works**: Creates the "活人感" (human feel) that differentiates real accounts from bots and corporate accounts. Makes your content memorable and shareable.

**How to apply**:
- Add a self-deprecating observation to technical content
- Include a relevant meme or cultural reference with industry commentary
- Share a genuine emotional reaction (excitement, frustration, surprise)
- Use your natural speaking voice, not a "content creator" voice
- Occasionally break format with something purely human

---

## Content Pipeline

### Stage 1: Ideation (Continuous)

Sources for content ideas:
- **Your daily work**: Problems you're solving, decisions you're making, tools you're using
- **Industry feeds**: News, product launches, research papers
- **Core circle**: What are thought leaders discussing? Where can you add value?
- **Audience signals**: What questions are people asking? What content gets bookmarked?
- **Competitor analysis**: What angles are working for accounts in your space?
- **Personal experience**: Unique stories, non-obvious observations, failures

Keep a running list (notes app, draft tweets, content calendar). Capture ideas immediately — don't rely on memory.

### Stage 2: Drafting

- Write the core insight first, then craft the hook
- The hook (first line) must stop the scroll: bold claim, surprising stat, contrarian take, or compelling question
- Keep tweets concise. Cut every word that doesn't add value
- For threads: write all tweets, then revise for flow and make each tweet standalone-worthy
- Add visual elements where they enhance the message (see [multimodal guide](multimodal-guide.md))
- Check product integration opportunity (see [product integration](product-integration.md))

### Stage 3: Review

Before posting, check:
- [ ] Does this add genuine value? Would I engage with this if someone else posted it?
- [ ] Is the hook strong enough to stop the scroll?
- [ ] Is there a clear takeaway or discussion point?
- [ ] No external links in main tweet (links in first reply)
- [ ] No typos, broken formatting
- [ ] Appropriate content pillar and product integration tier
- [ ] Optimal posting time for this content type

### Stage 4: Scheduling & Posting

- Schedule using content calendar rhythm (see [content calendar config](../config/content-calendar.example.json))
- Post at optimal windows for your target audience
- For threads: post at 08:00-10:00 in target audience timezone
- For single tweets: space 2-3 hours apart
- Stay active 30-60 min after posting to reply to early engagement

### Stage 5: Measurement

After 24-48 hours, collect:
- Impressions, engagement rate, reply count, bookmark count
- Compare against your baseline (from [goals config](../config/goals.example.json))
- Tag content type and pillar for pattern analysis
- Feed results into weekly review (see [methodology](methodology.md))

---

## Content Formulas

Proven structural formulas ranked by typical engagement:

### Formula A: Claim + Evidence + Insight
```
[Bold, specific claim]
[Evidence: data, example, screenshot]
[What this means / why it matters]
```
Best for: Technical depth, industry pulse

### Formula B: Story + Lesson + Takeaway
```
[Brief story or situation]
[What happened / what went wrong]
[The lesson or non-obvious insight]
```
Best for: Builder's journey, personal touch

### Formula C: Question + Context + Invitation
```
[Specific, thoughtful question]
[Why you're asking / your current thinking]
[Invitation to share perspectives]
```
Best for: Community value, engagement

### Formula D: List + Value + CTA
```
[N things about X]
1. [Item + brief explanation]
2. [Item + brief explanation]
...
[CTA: bookmark, follow, what would you add?]
```
Best for: Resource shares, tutorials, threads

### Formula E: Reaction + Analysis + Prediction
```
[Reference to event/news/trend]
[Your analysis — what most people miss]
[What you think happens next]
```
Best for: Industry pulse, rapid reaction to news

---

## Content Repurposing Loop

Maximize ROI from every piece of content:

### Unbundling (Thread → Standalone Tweets)
A high-performing thread contains 5-10 standalone insights. Over the following week, extract individual tweets:
- Each thread tweet becomes a standalone post with slight rewording
- Space them out (1-2 per day from a single thread)
- Reference the original thread for those who want the full context

### Expansion (Tweet → Thread)
When a single tweet performs unexpectedly well:
- Expand the core insight into a 5-7 tweet thread
- Add examples, data, visuals that flesh out the idea
- Post 2-3 days after the original tweet's peak engagement

### Cross-Format Repurposing
- Thread → blog post or newsletter edition
- X Spaces discussion → thread summarizing key insights
- Blog post → thread extracting the key points
- Product launch → multiple angles over 1-2 weeks (announcement, behind-the-scenes, user reactions, technical deep-dive)

### Evergreen Recycling
- Repost your best-performing content every 3-4 weeks
- Rephrase the hook and update any dated details
- Different audience segments see your content at different times
- Track whether recycled content maintains or declines in performance

---

## Timing Framework

Rather than hardcoded posting times, optimize based on YOUR audience's timezone and activity patterns.

### Determining Optimal Times

1. **Identify your primary audience timezone** (from [profile config](../config/profile.example.json))
2. **Map peak activity windows**:
   - Window A: 09:00-12:00 in audience timezone (morning engagement)
   - Window B: 17:00-20:00 in audience timezone (evening engagement)
3. **Convert to your local timezone** and set up cron reminders (see [cron schedule](cron-schedule.md))
4. **A/B test**: Try different times within these windows and measure

### Day-of-Week Patterns

Research-backed general patterns (test for your audience):
- **Tuesday-Thursday**: Highest engagement for professional/tech content
- **Wednesday**: Particularly strong for morning threads
- **Friday**: Good for lighter, community-oriented content
- **Weekend**: Lower overall but less competition — good for niche technical content

---

*Content Strategy v1.0*
