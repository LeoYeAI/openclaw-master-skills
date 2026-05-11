---
name: creative-eye
description: "Give AI agents creative judgment and design taste. Use when: (1) creating any visual content — merch, social posts, ads, product photography, brand materials, (2) evaluating creative quality before publishing, (3) building a reference library or style guide, (4) setting up creative quality gates, (5) training an agent to develop aesthetic judgment. Triggers: 'review this design,' 'is this good enough to post,' 'creative quality,' 'design feedback,' 'brand consistency,' 'visual audit,' 'creative evaluation,' 'design taste,' 'aesthetic judgment,' 'pre-publish check.'"
---

# Creative Eye — Design Judgment for AI Agents

## The Problem

AI agents ship bad creative because they have no taste. Specifically:

1. **They confuse "exists" with "good."** Generating output ≠ creating quality. The first version is almost never good enough, but agents treat it as done.
2. **They have no benchmarks.** Without seeing what "great" looks like, agents can't distinguish amateur from professional work.
3. **They optimize for volume over quality.** 50 mediocre variations when 1 excellent piece would outperform all of them combined.
4. **They can't self-evaluate.** They lack the vocabulary and frameworks to critique their own work.
5. **They don't learn from failures.** Same mistakes repeat across sessions because there's no feedback loop.

This skill provides the frameworks, prompts, and workflows to fix all five problems.

---

## The Framework: STUDY → COMPARE → CREATE → EVALUATE

Every creative task follows this sequence. Never skip steps.

### 1. STUDY — Build Taste Through Exposure

Before creating anything in a given domain, study what "great" looks like.

**Daily practice (10 min):**
Pick ONE brand or creator. Analyze ONE piece of their content. Ask:
- What makes it work visually? Be specific (not "it looks good" but "the 200-tracking on uppercase Didot creates editorial authority")
- What are the exact typography choices? (font, weight, size, tracking, color)
- What's the composition doing? (where does the eye land first, second, third?)
- What role does negative space play?
- What would break if you changed one element?
- What feeling does it create, and HOW does it create that feeling?

Log findings to a study log file. Accumulate observations over time. This builds the vocabulary and pattern library that enables judgment.

**Picking brands to study:**
Choose 8-12 brands across these tiers:
- **Tier 1 (3-4 brands):** Direct competitors or brands with a similar aesthetic to yours
- **Tier 2 (3-4 brands):** Brands your target audience admires, even if different category
- **Tier 3 (2-3 brands):** Category leaders with exceptional design systems
- **Tier 4 (1-2 brands):** Wildcard inspiration from unrelated fields (architecture, editorial, fashion)

### 2. COMPARE — Find References Before Creating

Before generating any visual content:
1. Find 3-5 reference examples of what "great" looks like for THIS specific format
2. Save them or note URLs
3. Identify the specific qualities that make each one great
4. Use those qualities as the creative brief constraints

**Never create in a vacuum.** The difference between amateur and professional creative is almost always that professionals looked at references first.

### 3. CREATE — Every Decision Needs a Reason

When generating creative, every choice must be intentional:
- **Why this font?** Not "it's available" — what does it communicate? (Serif = editorial authority. Geometric sans = modern tech. Humanist sans = friendly approachable.)
- **Why this color?** Does it match the brand palette? What emotion does it carry?
- **Why this layout?** What does left-aligned vs centered communicate? Where should the eye go first?
- **Why this size?** Small and restrained = premium/exclusive. Large and bold = loud/promotional.
- **Why this image treatment?** Warm and grainy = authentic/vintage. Clean and sharp = modern/clinical.

If you can't articulate why, you're guessing. Stop and refer back to your references.

### 4. EVALUATE — Score Before Shipping

Run every piece through both evaluation tools below before publishing.

---

## The 5-Point Creative Scorecard

Adapted from Runway's video evaluation framework. Score each dimension 1-10.

| # | Dimension | Question | Min Score |
|---|-----------|----------|-----------|
| 1 | **Brief Adherence** | Does this serve the stated business/creative goal? | 7 |
| 2 | **Brand Consistency** | Does this look like it came from the same brand as everything else? | 8 |
| 3 | **Visual Quality** | No artifacts, misspellings, clip-art vibes, AI tells? | 9 |
| 4 | **Emotional Resonance** | Would a real human stop scrolling for this? | 7 |
| 5 | **Style Match** | Does this match the brand's specific aesthetic? | 8 |

**If ANY score is below its minimum → do not publish. Fix or discard.**

---

## The 10-Point Pre-Publish Checklist

Quick yes/no gate. Requires 8+ "yes" to ship.

1. Does this look like it came from a well-funded brand? (not a weekend side project)
2. Would your most design-savvy friend say "this is fire" unprompted?
3. If you remove all text, is the composition still interesting?
4. Does the typography have personality, or is it just "text on a thing"?
5. Are there more than 3 elements competing for attention? (if yes, remove one)
6. Would someone in your target audience actually use/wear/share this?
7. Is there anything that looks AI-generated or clip-art-like?
8. Have you compared this side-by-side with a real brand reference?
9. Would you personally pay the listed price for this?
10. If this got 100K views, would it help or hurt the brand?

---

## The Self-Refine Loop

Based on Andrew Ng's Reflection pattern and the Self-Refine research framework (CMU). This is the core workflow for iterative improvement.

```
Generate → Critique (vision model) → Fix → Critique again → Ship or Kill
```

### The Loop

**Step 1: Generate.** Create the first draft using references and brand constraints.

**Step 2: Critique.** Use a vision model to evaluate the output. Feed it the generated image plus 2-3 reference images from your library. Use the evaluation prompts below. Get specific scores and specific issues.

**Step 3: Fix.** Address ONLY the specific issues identified. Do not regenerate from scratch unless the critique identifies fundamental problems (wrong concept, wrong style direction).

**Step 4: Re-critique.** Run the improved version through the same evaluation. Compare scores.

**Step 5: Ship or Kill.**
- All scores at or above minimums → ship it
- Improved but still below on 1-2 dimensions → one more iteration (go to Step 3)
- No meaningful improvement after iteration → kill it and try a different approach
- **Maximum 3 iterations.** If it's not working after 3 passes, the concept is wrong, not the execution. Escalate to a human or start over with a fundamentally different direction.

### Why 3 Iterations Max

Diminishing returns hit fast. If the core concept is sound, 1-2 refinements will get it there. If it takes more than 3, you're polishing the wrong thing. The discipline to kill bad work is as important as the ability to refine good work.

---

## Vision Model Evaluation Prompts

Use these with any vision-capable model (GPT-4o, Claude, Gemini). Feed the generated image alongside 2-3 reference images from aspirational brands.

### Merch Design Review

```
You are a senior creative director at a premium lifestyle brand.

Review this merch design against these criteria:

1. TYPOGRAPHY: Is the type treatment sophisticated? Does it have personality and intentional styling (tracking, weight, case)? Or does it look like default text on a template?
2. COMPOSITION: Is the layout balanced and intentional? Does whitespace serve the design? Or is it cluttered or awkwardly empty?
3. BRAND ALIGNMENT: Does this feel like it belongs to a specific brand with a clear identity? Or is it generic?
4. WEARABILITY/USABILITY: Would someone in the target demographic actually buy and use this? Would they be proud to be seen with it?
5. PRODUCTION QUALITY: Does this look like it was designed by a professional? Or does it have AI-generation artifacts, clip-art qualities, or amateur touches?

Score each dimension 1-10. Be brutally honest.
For any score below 7, explain exactly what's wrong and provide a specific fix.
Compare against the reference images provided — how does this stack up?
```

### Social Content Review

```
You are a social media creative director for a premium brand.

Review this social post (image + copy) against:

1. SCROLL-STOPPING POWER: Would this make someone pause mid-scroll? What specifically catches the eye — or fails to?
2. AUTHENTICITY: Does this feel real and human? Or corporate, AI-generated, or try-hard?
3. BRAND VOICE: Does the copy feel like a consistent, distinctive voice? Or generic marketing speak?
4. VISUAL QUALITY: Is the image/graphic high quality? Any AI tells (weird hands, text artifacts, uncanny valley, over-smoothed skin)?
5. VALUE EXCHANGE: Does this give the viewer something (entertainment, information, emotion, identity validation)? Or is it just noise in their feed?

Score each 1-10. For any score below 7, explain the issue and suggest a fix.
```

### Product Photography Review

```
You are an art director reviewing product photography for an ecommerce brand.

Evaluate this image on:

1. LIGHTING: Is the lighting intentional and flattering? Natural/warm vs flat/clinical? Does it create dimension and mood?
2. COMPOSITION: Does the product placement feel deliberate? Is there a clear focal point? How does the background serve the product?
3. STYLING: Do props and context elements enhance or distract? Is the scene believable and aspirational?
4. TECHNICAL QUALITY: Resolution, focus, color accuracy, white balance — are these professional grade?
5. BRAND STORY: Does this image tell a story about the brand? Does it evoke a lifestyle or feeling? Or is it just "product on white background"?

Score each 1-10. Minimum 8 across all dimensions for publication.
Identify the single biggest improvement that would elevate this image.
```

### Video/Motion Content Review

```
You are a creative director reviewing video content for a brand's social channels.

Evaluate on:

1. HOOK (first 2 seconds): Would someone keep watching? What grabs attention — or doesn't?
2. PACING: Does the edit rhythm match the content and platform? Too slow = skip. Too fast = confusion.
3. VISUAL CONSISTENCY: Does every frame feel on-brand? Any jarring transitions, off-brand elements, or quality drops?
4. AUDIO/TEXT: If there's text overlay or audio, does it enhance or distract? Is it readable/audible?
5. CTA/ENDING: Does the video end with purpose? Does it drive the intended action (follow, click, share, buy)?

Score each 1-10. For video, emotional resonance matters more than technical perfection.
```

---

## Building a Reference Library

Organized inspiration is the foundation of good creative judgment.

### Folder Structure

```
reference-library/
├── merch/
│   ├── premium-examples/        # Best-in-class merch from brands you admire
│   ├── typography-focused/      # Type-forward designs specifically
│   └── anti-examples/           # Bad merch — annotate WHY it's bad
├── social-content/
│   ├── scroll-stoppers/         # Posts with exceptional engagement
│   ├── brand-voice-examples/    # Copy that nails a specific tone
│   └── anti-examples/           # Cringe brand content to avoid
├── product-photography/
│   ├── hero-shots/              # Best product photos in your category
│   ├── lifestyle/               # In-context, aspirational photography
│   └── anti-examples/           # Flat, stock-photo-vibes shots
├── brand-systems/
│   ├── [brand-name]/            # Full system screenshots per brand
│   └── ...
├── style-profiles/
│   ├── [brand]-aesthetic.json   # Extracted JSON style profiles
│   └── ...
└── failures/
    ├── our-failures/            # Everything we shipped that was bad
    └── lessons.md               # Root cause analysis for each failure
```

### Extracting JSON Style Profiles

For any reference image you want to replicate the aesthetic of, use an LLM to extract a structured style profile:

**Prompt:**
```
Analyze this image and produce a detailed JSON style profile that captures its aesthetic DNA. Include:

{
  "color_palette": {
    "primary": ["#hex1", "#hex2"],
    "secondary": ["#hex3"],
    "background": "#hex",
    "text": "#hex",
    "accents": ["#hex"]
  },
  "lighting": {
    "type": "natural/studio/mixed",
    "direction": "description",
    "warmth": "warm/neutral/cool",
    "contrast": "high/medium/low",
    "shadows": "soft/hard/minimal"
  },
  "composition": {
    "layout": "centered/rule-of-thirds/asymmetric/etc",
    "focal_point": "description",
    "negative_space": "heavy/moderate/minimal",
    "depth": "shallow-dof/deep-dof/flat"
  },
  "typography": {
    "headline_style": "serif/sans/slab/etc",
    "weight": "light/regular/bold/black",
    "case": "uppercase/lowercase/mixed",
    "tracking": "tight/normal/wide/very-wide",
    "personality": "description"
  },
  "mood": {
    "primary_emotion": "description",
    "energy": "calm/moderate/energetic",
    "era_reference": "description",
    "cultural_reference": "description"
  },
  "texture": {
    "surface": "smooth/grainy/textured",
    "film_grain": "none/subtle/heavy",
    "imperfections": "none/intentional/natural"
  }
}

Be extremely specific with hex codes and descriptions. This profile will be used to generate new images in the same aesthetic.
```

Store these profiles in `reference-library/style-profiles/`. Use them as context when generating new creative — feed the JSON into your image generation prompts for consistent aesthetic output.

### Anti-Pattern Documentation

For every failure, document:
```markdown
## [Date] — [What Was Created]
**What happened:** [description]
**Why it seemed okay at the time:** [what fooled us]
**Why it's actually bad:** [specific problems]
**Root cause:** [the judgment failure — not just "it was bad"]
**Rule to prevent recurrence:** [new rule or checklist item]
```

The "why it seemed okay" field is critical. Understanding your blind spots is how you fix them.

---

## The Brand Guardian Pattern

Inspired by Jasper's Brand IQ approach. Set up automated quality gates that catch violations before publishing.

### Pre-Publish Guardrails Checklist

Create a `brand-guardrails.md` file in your workspace with these sections:

```markdown
# Brand Guardrails

## Visual Rules (hard stops — violating any one blocks publishing)
- [ ] Colors match approved palette (list hex codes)
- [ ] Typography uses approved fonts only
- [ ] No AI-generation artifacts visible (weird hands, text distortion, uncanny faces)
- [ ] No misspelled text in images
- [ ] Logo usage follows guidelines (clear space, minimum size, approved lockups)
- [ ] Image resolution meets minimum for intended platform

## Voice Rules (hard stops)
- [ ] Copy matches brand voice guidelines (list specific traits)
- [ ] No off-brand language or tone
- [ ] No claims that violate legal/regulatory requirements
- [ ] No competitor mentions (unless intentional comparison content)

## Quality Rules (soft stops — flag for review)
- [ ] Passes 5-Point Creative Scorecard (all dimensions at minimum)
- [ ] Passes 10-Point Pre-Publish Checklist (8+ yes)
- [ ] Has been compared against reference library
- [ ] Would pass the "100K views" test
```

### Brand Violation Detection

When reviewing content, scan for these common violations:
- **Color drift:** Hex codes look close but aren't exact. Use a color picker to verify.
- **Font substitution:** System font rendered instead of brand font. Check carefully.
- **Voice inconsistency:** Formal language in a casual brand. Slang in a premium brand.
- **Visual inconsistency:** Different filter/treatment than established content.
- **Accidental claims:** "Best," "guaranteed," "#1" without substantiation.

### Automated Quality Gate Workflow

Integrate into your agent's publishing workflow:

```
1. Agent generates creative
2. Run Self-Refine Loop (score + fix, max 3 iterations)
3. Run Brand Guardrails Checklist (hard stops block, soft stops flag)
4. If all hard stops pass and scores meet minimums → auto-publish
5. If any hard stop fails → block and report specific violation
6. If soft stops flag → publish with note to review in next creative retrospective
```

---

## The 7-Day Creative Training Curriculum

A structured week to systematically build creative judgment. Adapt brand references to your own context.

### Day 1: Build the Foundation
- Create the `reference-library/` folder structure (see above)
- Collect 50+ reference images from 5-6 brands you admire
- Write a `style-guide.md` for your brand covering: color palette (exact hex), typography (specific fonts, weights, tracking rules), photography style, composition rules, explicit "never do" list
- Write an `anti-patterns.md` documenting every past creative mistake with root cause analysis
- Deep-study 10 social posts from your top 2 aspirational brands. Write specific notes on what makes each one work.

### Day 2: Build the Evaluation System
- Implement the 5-Point Creative Scorecard as a reusable template
- Customize the vision model evaluation prompts for your brand (replace generic descriptions with your specific aesthetic)
- Test the full Self-Refine Loop: generate a test image → run evaluation → iterate → score again
- Set up a `creative-log.md` for ongoing feedback tracking
- Run 3 existing pieces of your content through the evaluation system. Be honest about scores.

### Day 3: Extract Style Profiles
- Take 5 reference images from each of your top 3 aspirational brands
- Extract JSON style profiles from each using the prompt above
- Create a composite profile for your brand by combining the best elements
- Generate 3 images using the composite profile as prompt context
- Compare outputs against references. Iterate the profile until outputs consistently match.

### Day 4: Format Deep Dive (Merch/Product)
- Study 20 pieces of merch or product design from category leaders
- Identify patterns: typography choices, color limitations, layout structures, what makes something premium vs amateur
- Create format-specific design rules (max colors, type hierarchy, spacing, what to avoid)
- Generate 5 new designs using the rules
- Run each through the relevant evaluation prompt. Only keep designs scoring 8+ on every dimension.

### Day 5: Format Deep Dive (Social/Content)
- Audit 20 top-performing posts from aspirational brand accounts
- For each: what's the hook? What's the visual? What's the emotional trigger? What makes it shareable?
- Create a `content-playbook.md` with specific post frameworks that work
- Generate 5 social posts using the playbook
- Run each through the social content evaluation prompt. Honest scoring.

### Day 6: Practice the Rejection Loop
- Run the full creative workflow 10 times from brief to finished piece
- Track: how many iterations to reach "publishable"? What are the most common failure modes?
- Practice KILLING work that isn't working after 3 iterations. This is a skill.
- Update anti-patterns and style guide based on what you learned

### Day 7: Integration
- Embed the creative evaluation into your agent's workflow as a mandatory pre-publish step
- Update your agent's personality/soul document with refined creative identity and taste profile
- Set up a daily creative study task (see cron template below)
- Schedule weekly creative retrospectives: review all content against the scorecard
- Document the entire system for your team

---

## Daily Creative Study — Cron Template

Add this as a recurring task for your agent:

```
DAILY CREATIVE STUDY

1. Pick today's brand from the study rotation list
2. Find ONE recent piece of content from that brand (social post, product shot, merch, packaging, or ad)
3. Analyze it in 5 sentences or less:
   - What specifically makes this effective? (be precise — name the font choice, the color, the composition technique)
   - What's the ONE technique I can steal for our brand?
4. Save the analysis to the study log
5. If the technique is broadly applicable, update the style guide or design rules

Time budget: 10 minutes max. Depth over breadth.
```

---

## Common Anti-Patterns

These are the most frequent ways AI agents produce bad creative. Learn to recognize and avoid each one.

### 1. "Something Exists" ≠ "Something Is Good"
The most dangerous failure mode. An agent generates an image, sees it rendered successfully, and declares it ready. Existence is not quality. The gap between "technically produced" and "genuinely good" is enormous. Always score before shipping.

### 2. Volume Over Quality
Generating 50 variations and picking the "best" one is not creative judgment — it's a lottery. Produce fewer outputs with more intentional input. 3 well-directed generations beat 50 random ones.

### 3. No Benchmark Comparison
Creating in a vacuum guarantees mediocre output. Every piece of creative should be evaluated against reference examples from brands that are actually good at this. If you haven't looked at references, you haven't started the creative process.

### 4. Illustration Over Typography
For most brands (especially early-stage), type-forward design reads as more premium and professional than illustration. Custom illustrations require exceptional skill to execute well. Bad illustration looks worse than good typography. Default to type-forward until you have proven illustration chops.

### 5. Upscaling Bad Work
Taking a low-quality concept and increasing its resolution, adding more detail, or making it bigger does not make it better. It makes it a larger, more detailed version of something bad. Fix the concept before scaling.

### 6. Ignoring Feedback Loops
If you don't track what works and what doesn't, you can't improve. Every piece of published creative should be reviewed against performance data. What got engagement? What fell flat? Feed this back into your creative decisions.

### 7. The "Too Clean" Tell
AI-generated content often looks unnaturally perfect — too smooth, too symmetrical, too evenly lit. Real creative has subtle imperfections. If everything looks like a stock photo render, add texture, grain, or asymmetry. Intentional imperfection reads as authentic.

### 8. Decorating Instead of Designing
Adding more elements (borders, shadows, gradients, icons) to fill space is decoration, not design. Good design is about what you remove. If an element doesn't serve a specific purpose, cut it.

### 9. Copying Without Understanding
Replicating a reference image's surface features (colors, fonts) without understanding WHY those choices work leads to designs that look "almost right" but feel wrong. Study the principles behind the reference, not just its appearance.

### 10. Skipping the Brief
Jumping straight to generation without defining what success looks like means you'll only know if something works by accident. Write the brief first: who is this for, what should they feel, what should they do after seeing it?

---

## Quick Reference: When to Use What

| Situation | Use This |
|-----------|----------|
| About to create any visual content | Full STUDY → COMPARE → CREATE → EVALUATE flow |
| Reviewing a single piece before posting | 5-Point Scorecard + 10-Point Checklist |
| Improving a draft that's close but not there | Self-Refine Loop (max 3 iterations) |
| Starting work in a new creative format | Day 1-3 of the Training Curriculum |
| Setting up quality gates for a brand | Brand Guardian Pattern |
| Building ongoing creative taste | Daily Creative Study cron |
| Debugging why creative keeps missing | Anti-Patterns checklist — identify which pattern applies |
| Extracting aesthetic from reference images | JSON Style Profile extraction prompt |

---

*Creative judgment isn't magic. It's a system. Study what good looks like, compare before you create, make intentional choices, evaluate honestly, and learn from every failure. Ship less, ship better.*
