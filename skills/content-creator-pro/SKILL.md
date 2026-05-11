---
name: content-creator-pro
description: >
  Autonomous content creation engine for agents. Writes platform-native posts,
  threads, newsletters, and long-form articles that meet the highest standards
  of authentic human writing. Masters hooks, storytelling, and brand voice across
  Twitter/X, LinkedIn, Reddit, Substack, and short-form video. Applies professional
  editorial craft to ensure every piece reads with genuine voice and natural rhythm. Tracks performance, learns what works, and improves
  every week. Triggered by agent-shark-mindset signals. Feeds acquisition-master
  with ready-to-publish content. Use whenever the agent needs to write or queue
  content for any channel.
version: 1.0.7
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "✍️"
    security_level: L1
    required_paths:
      read:
        - /workspace/content/voice.md
        - /workspace/content/calendar.json
        - /workspace/content/performance.json
        - /workspace/content/hooks.md
        - /workspace/.learnings/LEARNINGS.md
      write:
        - /workspace/content/voice.md
        - /workspace/content/calendar.json
        - /workspace/content/performance.json
        - /workspace/content/hooks.md
        - /workspace/content/queue/
        - /workspace/content/library/
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/.learnings/ERRORS.md
        - /workspace/AUDIT.md
    network_behavior:
      makes_requests: false
      uses_agent_telegram: false
      network_note: >
        This skill performs filesystem operations only. Content is written
        to /workspace/content/queue/ for acquisition-master to publish.
        Notifications to principal are handled by the agent's core
        Telegram integration, not by this skill directly.
    always: false
    requires:
      skills:
        - agent-shark-mindset
        - acquisition-master
---

# Content Creator Pro — Authentic Voice Content Engine

> "Content is the only asset that works while you sleep." — Operator principle
> "Post like a human. Think like a strategist. Scale like a machine."

shark-mindset detects the signal.
acquisition-master distributes.
**This skill creates the content they need.**

Without content the acquisition funnel is empty.
Without content there is no audience to sell to.
Without content the agent is invisible.

---

## The Non-Negotiable Foundation — Human Writing

Before any content is written, the agent understands this:

**Generic, low-quality content destroys credibility. Authentic voice builds it.**

The agent does not produce flat, generic content.
It produces content that reads like a sharp, experienced human
who happens to publish consistently.

This is not optional. It is the foundation of everything.

Full technical guide → `references/human_writing.md`

---

## ENGINE 1 — AUTHENTIC VOICE SYSTEM

### What separates authentic writing from generic content

```
SIGNAL 1 — WORD CHOICE (predictability)
  Generic writing defaults to the safest, most expected word.
  Authentic writing surprises at the sentence level.
  Fix: choose the precise, unexpected word — not the obvious one.

SIGNAL 2 — RHYTHM (sentence variation)
  Generic writing uses uniform, even sentence lengths.
  Authentic writing alternates naturally: short punch. Then a longer
  sentence that expands the idea with context and texture.
  Then short again.
  Fix: vary sentence length deliberately. Short. Medium. Long. Short.

SIGNAL 3 — STRUCTURAL VARIETY
  Generic writing repeats the same logical pattern across paragraphs.
  Same transition words. Same paragraph length. Same rhythm.
  Fix: break the pattern. Start a paragraph with a fragment.
  Use a one-word sentence. Let the structure breathe.
```

### The Quality Blacklist — Words and Patterns That Kill Voice

```
WEAK WORDS (generic writing patterns to eliminate):
  delve, tapestry, pivotal, underscore, testament, landscape,
  meticulous, intricate, interplay, garner, bolstered, nuanced,
  vibrant, foster, showcase, leverage, paradigm, seamless,
  comprehensive, robust, streamline, revolutionize, game-changer,
  cutting-edge, synergy, unlock, harness, empower, crucial,
  it's worth noting, it is important to note, in conclusion,
  in the realm of, when it comes to, having said that,
  on the other hand, needless to say, as previously mentioned

WEAK STRUCTURES (patterns that flatten voice):
  → Starting every paragraph with "Additionally," "Moreover," "Furthermore,"
  → Perfectly balanced pro/con structure (too neutral = AI flag)
  → Lists of exactly 3 items with the same sentence length each
  → Ending every section with a clean summary sentence
  → The "X, Y, and Z" three-part parallel structure used more than once per piece
  → Transitions that feel like they were inserted by an editor: "This raises
     an important question." / "Let's explore this further."

WEAK TONE PATTERNS (what generic content sounds like):
  → Consistent neutral tone across the entire piece (humans shift tone)
  → Never admitting uncertainty (AI is always confident — humans aren't)
  → Perfect grammar throughout (humans make deliberate informal choices)
  → No personality — no opinion — no friction
```

### What Makes Writing Feel Human

```
TECHNIQUE 1 — SPECIFICITY OVER GENERALITY
  AI: "Many entrepreneurs struggle with marketing."
  Human: "I talked to 12 founders last month. 9 of them
          said the same thing: they don't know what to post."

  The number. The timeframe. The specific observation.
  These are things only someone who actually lived it would write.

TECHNIQUE 2 — DELIBERATE IMPERFECTION
  A sentence fragment works. Like this one.
  A dash — used mid-thought — feels like a thinking brain.
  An em dash is not the same as a hyphen. Know the difference.
  Starting a sentence with "And" or "But" feels natural.
  It's how people actually think.

TECHNIQUE 3 — OPINION WITH FRICTION
  AI hedges everything. Humans take positions.
  "This is wrong." not "This may not be the optimal approach."
  "I disagree with the consensus here." not "There are
  multiple perspectives on this topic."
  Friction earns engagement. Neutral earns nothing.

TECHNIQUE 4 — EARNED TRANSITIONS
  Bad: "Additionally, there are other factors to consider."
  Good: "Here's what nobody mentions though:"
  Good: "The part that surprised me most:"
  Good: "Which brings up something uncomfortable:"
  These feel like a real person making a real point.

TECHNIQUE 5 — SENSORY AND CONTEXTUAL ANCHORS
  AI writes about ideas. Humans write about moments.
  "At 2am, staring at a spreadsheet that showed -€847,
   I realized the problem wasn't the product."
  The time. The detail. The emotional context.
  These cannot be fabricated — they read as lived experience.

TECHNIQUE 6 — INTELLECTUAL HONESTY
  "I don't know yet." "This might be wrong." "I've changed
  my mind on this twice in the last six months."
  Humans are uncertain. AI is never uncertain.
  Uncertainty builds trust because it signals honesty.
```
### AI Writing Anti-Patterns — What the Agent Must Never Produce

```
The following patterns are produced by language models by default.
The agent actively detects and eliminates them before publishing.

ANTI-PATTERN 1 — LOW PERPLEXITY (predictable word sequences)
  What it looks like: every word is the statistically safest choice
  Examples:
    "It is important to note that..."
    "This comprehensive approach ensures..."
    "Leveraging these insights, we can..."
  Why it happens: models optimize for fluency → predictable output
  Fix: rewrite with the specific, concrete, or unexpected word

ANTI-PATTERN 2 — LOW BURSTINESS (uniform sentence rhythm)
  What it looks like: all sentences are 15-20 words, even pacing
  "The strategy involves three key components that work together
   to achieve the desired outcome and maximize overall results."
  "This approach has been proven effective across many industries
   and consistently delivers measurable improvements in performance."
  Why it happens: models maintain consistent output length
  Fix: alternate. Short. Then a longer sentence that actually develops
  the idea with texture and specificity. Then short again.

ANTI-PATTERN 3 — STRUCTURAL PARALLELISM OVERLOAD
  What it looks like: every section follows the same template
  → Introduction sentence
  → Three supporting points
  → Conclusion sentence
  Repeated across every paragraph of the piece
  Fix: vary the paragraph architecture. Some paragraphs are one line.
  Some are a question. Some start with the conclusion.

ANTI-PATTERN 4 — THE TRANSITION INSERTION
  What it looks like: connective tissue that adds nothing
  "This raises an important question."
  "Let's explore this further."
  "With this in mind, we can now turn our attention to..."
  "Building on the above, it becomes clear that..."
  Fix: delete these sentences entirely. Jump to the next point.

ANTI-PATTERN 5 — CONFIDENT NEUTRALITY
  What it looks like: covering all sides with zero opinion
  "While some argue X, others believe Y. Both perspectives
   have merit and should be considered carefully."
  Fix: take a position. "X is right. Here's why Y fails."

ANTI-PATTERN 6 — THE SUMMARY TRAP
  What it looks like: every section ends by summarizing itself
  "In summary, these three factors demonstrate the importance of..."
  "As we have seen, the key takeaway is..."
  Fix: end sections mid-thought or with a hook into the next one.

ANTI-PATTERN 7 — FAKE SPECIFICITY
  What it looks like: numbers that sound precise but mean nothing
  "Many studies show..." / "Research indicates..."
  "A significant number of entrepreneurs..."
  Fix: real numbers only. "12 of the 14 founders I spoke with..."
  If you don't have the number, don't fake it. Remove the claim.

ANTI-PATTERN 8 — HEDGED EVERYTHING
  What it looks like: every claim is softened
  "It could be argued..." / "One might consider..."
  "It may be worth exploring..." / "This seems to suggest..."
  Fix: own the claim. "This is wrong." "This works." "I disagree."
```



---

## ENGINE 2 — HOOK MASTERY

The hook determines everything. A bad hook = zero readers.
A great hook with mediocre content still gets engagement.
A great hook with great content builds an audience.

### The 10 Hook Archetypes

```
1. CREDIBILITY HOOK
   Lead with proof that you have the right to speak on this.
   "I've sent 12,000 cold emails. Here's what actually works:"
   "47 client calls in 90 days. The pattern I noticed:"
   Rule: specific numbers only. "Many" and "several" = AI.

2. CURIOSITY GAP HOOK
   Open a gap between what they know and what they're about to learn.
   "The thing nobody tells you about [topic]:"
   "I was wrong about [common belief]. Here's what changed my mind:"
   "Why [obvious thing] doesn't work anymore:"

3. CONTRARIAN HOOK
   Challenge something the audience believes.
   "Cold email is dead. (Not what you think it means.)"
   "Stop optimizing your funnel. Fix this first."
   Rule: the parenthetical softener makes it land better.
   Don't be contrarian for shock — be contrarian because you mean it.

4. RESULT HOOK
   Lead with the outcome, not the journey.
   "+€2,847 in 30 days. Here's the full breakdown:"
   "This post got me 3 inbound clients. No paid ads."
   Rule: real numbers only. Round numbers feel fake.

5. STORY HOOK (the most powerful on LinkedIn)
   Drop the reader into a specific moment.
   "I got a message at 11pm. 'We need to cancel.'"
   "Three years ago I had €0 and a VPS."
   Rule: start in the middle of something happening.
   No setup. No "let me tell you a story about..."

6. PERSONAL FAILURE HOOK
   Vulnerability with a lesson.
   "I made a €4,000 mistake last week."
   "My first 90 days of posting: 12 followers total."
   Rule: always pivot to the lesson. Failure without
   insight is just self-pity.

7. DATA / PATTERN HOOK
   A surprising number or observation.
   "94% of Twitter threads get fewer than 10 retweets."
   "I analyzed 450 LinkedIn posts. One format dominates."
   Rule: cite the source or make clear it's your own data.

8. QUESTION HOOK
   A question they haven't been asked but instantly feels relevant.
   "When did you last create content you were genuinely proud of?"
   "What would you post if you knew nobody was watching?"
   Rule: avoid generic questions. "Have you thought about X?"
   is weak. Make it specific and slightly uncomfortable.

9. LIST HOOK
   Promise a specific number of things.
   "7 things I stopped doing to grow faster:"
   "3 email subject lines that got 60%+ open rates:"
   Rule: odd numbers outperform even numbers.
   Specific numbers outperform "several."

10. DECLARATION HOOK
    A bold statement of belief or position.
    "Long-form content is the only moat left."
    "The personal brand era is over. Here's what's next."
    Rule: back it up. A declaration without proof is noise.
```

### Platform-Specific Hook Rules

```
TWITTER / X
  → Hook = first tweet in the thread
  → Max 280 characters — every word earns its place
  → The hook tweet must work as a standalone
  → Add "🧵" at the end to signal thread
  → First hour engagement determines reach — post when your
    audience is active (test, then optimize)

LINKEDIN
  → First 2 lines are all that shows before "see more"
  → Those 2 lines are everything
  → Use the LINE — GAP — LINE structure:
    Line 1: hook statement (short, bold)
    [blank line]
    Line 2: expand or contrast
  → The gap creates visual breathing room and forces the hook
    to stand alone before they click

SUBSTACK / NEWSLETTER
  → Subject line IS the hook — treat it like the post hook
  → Opening sentence must reward the click immediately
  → Never start with "In this issue we'll cover..."
  → Start with the most interesting thing

SHORT-FORM VIDEO (TikTok / Reels / Shorts)
  → First 2 seconds determine completion rate
  → Say the hook out loud — does it demand attention?
  → Visual hook + spoken hook together = highest retention
  → Pattern interrupt: unexpected angle, unusual setting, bold text
```

---

## ENGINE 3 — STORYTELLING FRAMEWORKS

### Framework 1 — The Moment of Change (best for LinkedIn)

```
STRUCTURE:
  1. Drop into a specific moment (not "once upon a time" — NOW)
  2. Name the problem or tension
  3. The unexpected insight or turning point
  4. What changed because of it
  5. The lesson the reader can apply

EXAMPLE:
  Hook:    "I almost deleted the post."
  Moment:  "It was 11pm. I'd spent 3 hours writing it. 
             Re-reading it, I thought: who cares about this?"
  Tension: "I posted it anyway. Went to sleep."
  Turn:    "Woke up to 47 comments and 3 DMs from potential clients."
  Lesson:  "The posts you almost don't publish are often the best ones.
             Your self-doubt is not a reliable editor."
```

### Framework 2 — Before / After / Bridge

```
STRUCTURE:
  BEFORE: describe the situation before the insight
  AFTER:  describe the situation after (lead with this if it's compelling)
  BRIDGE: what created the change — this is your value

EXAMPLE:
  Before: "6 months ago: 0 inbound leads. Spending 4h/day on outreach."
  After:  "Today: 3-5 inbound DMs/week. Outreach = 30 min/day."
  Bridge: "The difference was one decision: stop selling in the content,
           start documenting the work."
```

### Framework 3 — The Unexpected Lesson (contrarian)

```
STRUCTURE:
  1. State the common belief
  2. Challenge it with your own experience
  3. Present the counter-evidence
  4. Give the actual framework

EXAMPLE:
  Common: "Post every day to grow."
  Challenge: "I posted every day for 3 months. Zero growth."
  Evidence: "What actually moved the needle: 3 posts/week,
              each one 10x better than my daily posts."
  Framework: "Frequency < Quality × Consistency. Here's how
              I think about the balance now:"
```

### Framework 4 — The Step-by-Step (educational)

```
STRUCTURE:
  Hook:   specific result + timeframe
  Body:   numbered steps, one idea each
  Rule:   each step must be actionable, not abstract
  Close:  acknowledge the one thing that actually determines
          success or failure

RULE: never use "Step 1: Do X" without explaining WHY.
The why is where the human insight lives.
Without it it reads like a template — because it is.
```

### Framework 5 — The Observation (thought leadership)

```
STRUCTURE:
  1. Something you noticed (specific, recent, real)
  2. Why it matters
  3. What it implies
  4. What you're doing differently because of it

This is the hardest format to fake.
Real observation from real experience cannot be faked.
A made-up observation about a general trend is obviously AI.

EXAMPLE:
  "I've noticed something in my last 20 sales calls.
   When I ask 'what have you already tried?'
   before pitching anything, the close rate doubles.
   Not because the pitch is better.
   Because they feel heard before they feel sold to."
```

---

## ENGINE 4 — LONG-FORM HUMAN ARTICLES

For newsletters, blog posts, and Substack articles.
The agent writes these with the discipline of a journalist
and the voice of a practitioner.

### The Article Architecture

```
SECTION 1 — THE LEAD (first 150 words)
  Most important section. If this fails, nothing else matters.
  
  Options:
  → The anecdote lead: drop into a specific scene
  → The surprising fact lead: counterintuitive data point
  → The question lead: a question they haven't been asked
  → The declaration lead: bold position statement
  
  Never: "In today's post, we will explore..."
  Never: "It has become increasingly clear that..."
  Never: summarize what the article will say before saying it

SECTION 2 — THE CORE ARGUMENT
  One main idea. Not three. Not five. One.
  Every section serves the main idea.
  If a section doesn't serve it → cut it.
  
  Structure each section:
  → Claim (what you're arguing)
  → Evidence (data, story, or example — never abstract)
  → Implication (so what does this mean?)

SECTION 3 — THE TURN
  The moment when the piece goes deeper.
  Usually the third or fourth section.
  Where the expected argument reveals a hidden layer.
  "But here's the part nobody talks about:"

SECTION 4 — THE CLOSE
  Not a summary. Not "in conclusion."
  A final image, story, or question that stays with the reader.
  Ideally mirrors something from the lead (circular structure).
  The close should make the reader feel they arrived somewhere.
```

### Human Writing Checklist — Run Before Publishing

```
VOICE CHECK:
  ☐ Does this sound like a specific person or like "content"?
  ☐ Is there at least one opinion that someone could disagree with?
  ☐ Is there at least one admission of uncertainty or failure?
  ☐ Are there any weak/generic words? (see references/human_writing.md)

STRUCTURE CHECK:
  ☐ Do sentence lengths vary? (count: mix of 5, 10, 20+ words)
  ☐ Do paragraphs vary in length? (1 line, then 4 lines, then 2 lines)
  ☐ Are transitions earned or inserted? (rewrite inserted ones)
  ☐ Does the piece start in the middle of something happening?

SPECIFICITY CHECK:
  ☐ Are there real numbers? (not "many" or "significant")
  ☐ Are there specific times, dates, or contexts?
  ☐ Is there at least one detail that could only come from experience?
  ☐ Is the piece about a real situation or about a general concept?

READABILITY CHECK:
  ☐ Read it out loud — does it sound like a person speaking?
  ☐ Any sentence that sounds like it was written by a committee → rewrite
  ☐ Any sentence where you used a thesaurus to avoid repetition → rewrite
     (repetition is human; forced synonyms are AI)
```

---

## ENGINE 5 — BRAND VOICE

The agent reads `/workspace/content/voice.md` before writing anything.
This file defines exactly how the principal wants to sound.

### Default Voice Template (customize in voice.md)

```
TONE:
  Direct. No filler. No corporate speak.
  Every sentence earns its place or it's cut.

IDENTITY (what we talk about):
  [Fill: 3-4 topics this account owns]

WHAT WE NEVER DO:
  → Humblebrag ("So honored to announce...")
  → Fake vulnerability ("I almost quit but...")
  → Engagement bait ("Comment YES if you agree")
  → Generic advice without proof

SIGNATURE ELEMENTS:
  → Lead with a result or a specific number
  → One strong idea per post — never two
  → Use "I" — personal builds faster than brand voice
  → Show proof before making claims

PROOF OVER CLAIMS:
  → "I tested X" beats "X is effective"
  → Screenshots and real numbers beat assertions
  → Specific examples beat general principles
```

---

## ENGINE 6 — CONTENT MODES

### Mode 1 — Signal-Reactive (triggered by shark-mindset)

```
Input:  market signal from agent-shark-mindset
Output: 3 platform-specific posts ready to publish
Time:   < 5 minutes signal to queue

Process:
  1. Read the signal (what happened, why it matters)
  2. Identify the angle: contrarian / confirmation / prediction
  3. Check voice.md for tone
  4. Write Twitter thread + LinkedIn post + Reddit comment
  5. Save to /workspace/content/queue/
```

### Mode 2 — Calendar-Driven (cron, Mon/Wed/Fri)

```
Input:  calendar.json + performance.json (best hooks)
Output: written post ready for acquisition-master to publish

Process:
  1. Read today's calendar slot
  2. Check performance.json → what hook type performed best?
  3. Write using top hook pattern for today's format
  4. Run human writing checklist
  5. Queue in /workspace/content/queue/
```

### Mode 3 — On-Demand (principal request)

```
Input:  "write a post about [topic]"
Output: draft written to /workspace/content/queue/ with status: pending_review

Process:
  1. Identify platform + format from context
  2. Apply voice.md
  3. Write → run checklist
  4. Write to /workspace/content/queue/[id].json with status: pending_review
```

### Mode 4 — Repurposing (Sunday)

```
Input:  top 3 posts from the week (by engagement rate)
Output: adapted versions for other platforms

Rule: never write from scratch when you can repurpose a winner.
Twitter thread → LinkedIn post → Substack section
Performance compounds when the same insight travels.
```

---

## Performance Tracking

After every published post, the agent logs to `performance.json`:

```json
{
  "id": "tw-20260316-001",
  "date": "2026-03-16",
  "platform": "twitter",
  "format": "thread",
  "hook_type": "result",
  "hook_text": "I sent 500 cold emails. Here's what I learned:",
  "impressions": 4200,
  "engagements": 312,
  "engagement_rate": 7.4,
  "follows": 28,
  "revenue_attributed": 194,
  "voice_quality_score": null
}
```

When engagement_rate > 5% on Twitter or > 3% on LinkedIn:
→ Log hook to `/workspace/content/hooks.md` as validated
→ Log to AUDIT.md: "🔥 Viral: [hook text] → [X]% ER" (agent core picks this up)
→ Flag for repurposing to other platforms

---

## Weekly Learning Routine

Every Monday the agent reviews performance.json and writes to LEARNINGS.md:

```
→ Top 3 hooks by engagement rate → add to hooks.md library
→ Bottom 3 posts → log what didn't work + why
→ Pattern identified this week (format / topic / tone)
→ 1 proposed adjustment to calendar.json
→ Weekly summary saved to performance.json + logged to AUDIT.md
```

---

## Workspace Structure

```
/workspace/content/
├── voice.md              ← brand voice definition (customize this)
├── calendar.json         ← weekly content plan (from acquisition-master)
├── performance.json      ← all posts + engagement metrics
├── hooks.md              ← validated hooks library (grows over time)
├── queue/                ← written posts waiting to publish
│   └── [id].json
└── library/              ← published posts archive
    └── [YYYY-MM]/
        └── [id].json
```

---

---

## Installation & Setup

### Required Workspace Structure

Before using this skill, the following structure must exist in `/workspace/`.
The agent creates missing files automatically on first run.

```
/workspace/
├── content/
│   ├── voice.md              ← REQUIRED — copy from templates/voice.md and customize
│   ├── calendar.json         ← REQUIRED — copy from templates/calendar.json
│   ├── performance.json      ← auto-created on first post log
│   ├── hooks.md              ← auto-created when first viral post detected
│   ├── queue/                ← auto-created — written posts waiting to publish
│   └── library/              ← auto-created — published posts archive
│       └── YYYY-MM/
│           └── [id].json
└── .learnings/
    ├── LEARNINGS.md           ← usually exists — created if missing
    └── ERRORS.md              ← auto-created on first error
```

### Bootstrap — First Run Instructions

Tell your agent to run this on first install:

```
1. Copy /skills/content-creator-pro/templates/voice.md
   to /workspace/content/voice.md
   Then open it and fill in your tone, identity pillars, and platforms.

2. Copy /skills/content-creator-pro/templates/calendar.json
   to /workspace/content/calendar.json
   Then update week_template with your preferred platforms and frequencies.

3. Copy /skills/content-creator-pro/templates/performance.json
   to /workspace/content/performance.json

4. Copy /skills/content-creator-pro/templates/ERRORS.md
   to /workspace/.learnings/ERRORS.md

5. Copy /skills/content-creator-pro/scripts/content_tracker.py
   to /workspace/content/scripts/content_tracker.py

6. Verify python3 is available:
   python3 --version

7. Run the setup verification:
   python3 /workspace/content/scripts/content_tracker.py stats
   Expected output: "Total posts: 0"
```

### Cron Schedule

Add these to your agent's HEARTBEAT.md or cron configuration:

```
# Content creation — Mon, Wed, Fri at 8h
0 8 * * 1,3,5   content-creator-pro → Mode 2 (calendar-driven)

# Weekly performance review — Every Monday at 9h
0 9 * * 1       python3 /workspace/content/scripts/content_tracker.py weekly

# Weekly learning routine — Every Monday at 9h30
30 9 * * 1      content-creator-pro → weekly learning (review performance.json → update LEARNINGS.md)

# Sunday repurposing — Every Sunday at 10h
0 10 * * 0      content-creator-pro → Mode 4 (repurpose top 3 posts from week)
```

### Setup Checklist

```
[ ] voice.md copied to /workspace/content/ and customized
[ ] calendar.json copied to /workspace/content/ and configured
[ ] performance.json initialized in /workspace/content/
[ ] content_tracker.py copied to /workspace/content/scripts/
[ ] python3 available on the agent container (python3 --version)
[ ] content_tracker.py stats runs without error
[ ] agent-shark-mindset installed (for Mode 1 signal-reactive)
[ ] acquisition-master installed (for auto-publishing from queue/)
[ ] Crons added to HEARTBEAT.md
```

### Files Written By This Skill

| File | Frequency | Content |
|---|---|---|
| `/workspace/content/queue/[id].json` | Per post | Written post ready to publish |
| `/workspace/content/library/YYYY-MM/[id].json` | Per post | Published post archive |
| `/workspace/content/performance.json` | Per post | Engagement metrics log |
| `/workspace/content/hooks.md` | On viral | Validated hook library |
| `/workspace/content/voice.md` | On missing | Default template created |
| `/workspace/.learnings/LEARNINGS.md` | Weekly | Content patterns learned |
| `/workspace/.learnings/ERRORS.md` | On error | Error log with resolution |
| `/workspace/AUDIT.md` | On event | Key actions and alerts |

---

## Constraints

```
❌ Never publish content that fails the human writing checklist
❌ Never use weak generic words that flatten voice (see references/human_writing.md)
❌ Never post without reading voice.md first
❌ Never log fake engagement metrics
❌ Never repurpose a post without crediting the original performance data
✅ Always run the human writing checklist before queuing
✅ Always log every post to performance.json after publishing
✅ Always flag viral posts (ER > 5% Twitter / > 3% LinkedIn) to AUDIT.md
✅ One content improvement per weekly review — never a list of 10
✅ If voice.md is missing → create from template, log to AUDIT.md, do not guess
```


## Error Handling

```
ERROR: voice.md not found
  Action: Use default voice template above, create voice.md
  Log: AUDIT.md → "Default voice.md created [date]"

ERROR: calendar.json empty or no slot for today
  Action: Check shark-mindset for latest signal → write from that
          If no signal → repurpose best post from last 14 days
  Log:    AUDIT.md → "Calendar fallback: [source] [date]"

ERROR: Quality checklist fails (generic patterns detected)
  Action: Do NOT publish. Rewrite the flagged sections.
          A post without authentic voice is worse than no post.
  Log:    AUDIT.md → "Post rewritten: voice quality improved [date]"

ERROR: performance.json corrupted
  Action: Rebuild from library/ files (each post saved individually)
  Log:    ERRORS.md → "performance.json rebuilt [date]"

ERROR: Post queued but acquisition-master not installed
  Action: Save to /workspace/content/queue/ with status: pending
          Log to AUDIT.md: "Post queued — acquisition-master needed to publish"
```
