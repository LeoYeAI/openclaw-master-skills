---
name: idea-to-post
description: Expand scattered ideas into in-depth posts. Use this skill when users need to "expand ideas," "generate posts," "brainstorm content," "writing assistance," "enrich thoughts," "deepen thinking," or provide scattered ideas that need systematic expression.
version: 1.5.0
allowed-tools: AskUserQuestion, WebSearch, mcp__web_reader__webReader
model: claude-sonnet-4-20250514
---

# Idea-to-Post Expansion Skill

## Skill Overview

This skill helps you expand scattered ideas (a sentence, a few words, a vague thought) into **90+ point** social media posts.

**Target Positioning: Quality social media content, not technical documentation**

It works through the following ways:
1. **Framework Internalization** - Use thinking frameworks to design questions, but don't mechanically apply them
2. **Information Search & Integration** - Automatically search for high-quality materials, supplement relevant data and cases
3. **Progressive Deep Questioning** - Multiple-choice to set direction + open questions to enrich content, **7-10 rounds of dialogue** until complete
4. **Iterative Polishing & Optimization** - Reflect and optimize after generation, pursuing 90+ point quality
5. **Multi-Platform Output** - Generate post versions adapted to different platforms

**Expected dialogue rounds: 7-10 rounds**
- 3-4 rounds: Get direction and core viewpoints (technical documentation level)
- 5-7 rounds: Add cases, emotions, uniqueness (social media level)
- 7-10 rounds: Deep mining, repeated polishing (quality social media level)

## Core Mechanism: Progressive Questioning + Framework Internalization

### Three Core Principles

**1. Internalize Frameworks, Don't Expose Them**

Use thinking framework logic to design questions, but don't say "I'm using [Framework Name]":

```
Wrong: "I recommend using the PREP framework. Now for Point: What's your viewpoint?"
Correct: "What's the core viewpoint you want to express?"

Questions have framework thinking, but the dialogue is natural.
```

**2. Combine Multiple Choice + Open Questions**

```
Multiple Choice (AskUserQuestion)  Quickly lock direction
Open Questions (direct dialogue)    Deeply mine content

Multiple Choice = Skeleton | Open Questions = Flesh and blood
```

**3. Progressive Deepening, Dynamic Adjustment**

Each round of questions is based on the previous answer, naturally transitioning to the next dimension:

```
User: "todo is an underrated command"
    ↓
Follow-up: What does "underrated" specifically mean? (Concept deepening)
    ↓
User: "People don't know it's a conversation memory mechanism"
    ↓
Follow-up: What pain point does it solve? (Value inquiry)
    ↓
Follow-up: Any specific examples? (Case supplement)
```

---

### Questioning Flow (7-10 Rounds of Dialogue + Multi-Stage Search)

```
┌─────────────────────────────────────────────────┐
│  User inputs idea                                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  [Initial Search] Background information        │
│  collection                                     │
│  - Identify core concepts                        │
│  - Multi-angle search queries                    │
│  - Get background materials                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Rounds 1-2: Direction locking                  │
│  (mainly multiple choice)                        │
│  - Goal? Audience? Platform?                     │
│  - Quickly position article type                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Rounds 3-4: Core deep dive                     │
│  (open questions)                                │
│  - What's the core viewpoint?                    │
│  - What does "underrated" specifically mean?     │
│  - What pain point does it solve?                │
│  - Why do you think so?                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Rounds 5-6: Real cases                         │
│  (open questions, required)                      │
│  - When was the most recent time?                │
│  - What feature? What specifically was said?     │
│  - How did you feel at that moment?              │
│  - Any comparison cases? (with vs without)       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Round 7: Emotional resonance                   │
│  (open questions, required)                      │
│  - Most frustrated/surprised moment?             │
│  - Physical reaction? Slap thigh? Long sigh?     │
│  - Turning point from "useless" to "amazing"?    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Round 8: Uniqueness                            │
│  (open questions)                                │
│  - Any undiscovered tips?                        │
│  - Any unique usage methods?                     │
│  - Any counter-intuitive understanding?          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  [Precision Search] Based on user's unique      │
│  viewpoints                                      │
│  - Extract unique insights/counter-intuitive     │
│    viewpoints                                    │
│  - Reverse search for supporting evidence        │
│  - Multi-angle validation                        │
│    (industry/competitors/data)                   │
│  - Try different keywords if search fails        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Round 9: Structure confirmation                │
│  (multiple choice)                               │
│  - Article structure?                            │
│  - Style preference?                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Round 10: Final touches                        │
│  (mixed)                                         │
│  - Core golden sentence?                         │
│  - Call to action?                               │
│  - Anything else to add?                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Information completeness assessment            │
│  (90+ point standard)                            │
│  Core viewpoint                                  │
│  Real cases (required)                           │
│  Emotional resonance (required)                  │
│  Unique viewpoints (required)                    │
│  External validation (search results)            │
│  → Complete, generate content                    │
│  → Incomplete, continue questioning              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  First draft generation                         │
│  (standard Markdown format)                      │
│  - Integrate all information                     │
│  - Use heading levels, bold, quote blocks, etc.  │
│  - Generate structured content                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Reflection and optimization (optional)         │
│  - What's not good enough?                       │
│  - What needs supplementing?                     │
│  - Iterate and optimize                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Final output (standard Markdown format)        │
└─────────────────────────────────────────────────┘
```

**Note: Cases, emotions, and uniqueness are required and cannot be skipped. The second round of precision search is a key环节.**

---

### Integrating Framework Thinking into Questions

| Framework Thinking | Questioning Approach | Example |
|-------------------|---------------------|---------|
| Point | What's the core viewpoint? | "What's the core viewpoint you want to express?" |
| Reason | Why do you think so? | "Why do you think so? What's the reason?" |
| What | What specifically? | "What does this specifically refer to?" |
| Why | Why is it important? | "What pain point does it solve?" |
| How | How is it done? | "How is it implemented?" |
| Example | Any examples? | "Any specific cases?" |
| Situation | Initial state? | "What was the initial state?" |
| Complication | What conflict? | "What challenge appeared?" |

**Frameworks are thinking tools, not questioning templates.**

---

## Quick Framework Selection Guide

### Automatic Recommendation Rules

Based on keywords in your input, the system will automatically recommend frameworks:

| Keywords | Recommended Framework |
|----------|----------------------|
| Why, essence, original intention, mission, value | Golden Circle |
| Problem, challenge, dilemma, turning point, story | SCQA |
| Promotion, publicity, conversion, sales, marketing | AIDA |
| Viewpoint, opinion, think, should, suggest | PREP |
| Deep dive, root cause, trace back, underlying | 5-Why |
| Innovation, breakthrough, disrupt, reconstruct, essence | First Principles |
| Product, feature, advantage, selling point, characteristic | FBA |
| Other or unclear | 5W1H (default) |

### Framework Introduction

For detailed framework explanations, refer to `references/thinking-frameworks.md`

---

## Usage Flow

### Core Flow: Keep Questioning Until Complete

```
┌─────────────────────────────────────────────────┐
│  User inputs idea                                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  First round: Direction questions                │
│  - Keyword analysis based on topic               │
│  - Recommend thinking framework                  │
│  - Confirm target platform and audience          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  User answers                                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Second round: Framework deep dive               │
│  - Ask core elements based on selected framework │
│  - Focus on 1-2 key questions per round          │
│  - Dynamically adjust subsequent questions       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Third round: Detail supplement                  │
│  - Ask missing details based on available info   │
│  - Cases, data, emotional points, etc.           │
│  - Interactive design and call to action         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
            ...Loop...
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Skill judges: Information completeness          │
│  assessment                                      │
│  - Is core viewpoint clear?                      │
│  - Is supporting material sufficient?            │
│  - Are emotional resonance points clear?         │
│  - Is interactive design specific?               │
│                                                 │
│  → Incomplete: Continue questioning              │
│  → Complete: Enter generation phase              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Integrate information to generate post          │
│  - Original idea                                 │
│  - Search materials                              │
│  - User answers                                  │
│  - Framework structure                           │
└─────────────────────────────────────────────────┘
```

### Information Search (Multi-Stage Execution, Required)

Search must be performed in **multiple stages** to ensure precise external validation is collected:

#### Stage 1: Initial Background Search (Before questioning begins)

Execute initial information search before questioning starts:
1. Identify core concepts in the topic
2. Build multi-angle search queries
3. Use WebSearch to get relevant materials
4. Use WebFetch to read key pages in depth
5. Organize search results for later use

#### Stage 2: Precision Deep Search (After collecting core viewpoints)

**This is the most critical step** - after collecting the user's core viewpoints and unique insights, you must perform a **second round of precision search**:

1. **Build search terms based on user's unique viewpoints**
   - Extract unique insights/counter-intuitive viewpoints proposed by user
   - Use these viewpoints as keywords for reverse search
   - Look for supporting or refuting evidence

2. **Multi-angle validation search**
   - Search industry reports, news media
   - Search competitors/international cases
   - Search data support

3. **Handling search failures**
   - If one search fails/is limited, try different keyword combinations
   - Use more generic or more specific search terms
   - Try English search terms for international perspective
   - Record search status, inform user (e.g., if search was restricted)

#### Search Keyword Strategy

| Stage | Search Focus | Example Keywords |
|-------|-------------|------------------|
| Initial search | Background info, basic facts | "Qianwen 3 release", "AI e-commerce assistant" |
| Precision search | User unique viewpoint validation | "AI vs e-commerce conflict", "traffic distribution AI impact" |
| Comparison search | International cases, competitor analysis | "ChatGPT e-commerce", "foreign AI shopping assistant" |

**Search results must be integrated into final content as external validation.**

**Even if search is limited, try multiple different keywords and inform user of search status.**

### Question Design Principles

**1. Question Based on Topic**

Questions must be closely tied to the core topic of user input, don't ask irrelevant questions.

**2. Framework-Based Design**

Use framework thinking to design questions, but don't say "I'm using [Framework Name]".

**3. Mix Multiple Choice + Open Questions**

- **Multiple Choice**: When there are clear options, need quick classification
- **Open Questions**: When need stories/experiences/emotions/details
- **Mixed**: After AskUserQuestion "Other" option, continue follow-up questions

**4. Progressive Deepening, Dynamic Adjustment**

Each round is based on the previous answer, naturally transitioning to the next dimension. Not mechanically following a template.

**5. Focus on 1-2 Questions Per Round**

Avoid information overload, give user thinking space.

**6. Complete Information Before Stopping**

Check core dimensions, question what's missing, only generate when complete.

### Completeness Judgment Standards (90+ Point Target)

When judging whether information is complete, the skill checks the following dimensions:

#### Must Be Complete (Continue questioning if missing, cannot skip)

| Dimension | Check Item | Description |
|-----------|-----------|-------------|
| **Core Viewpoint** | Is the core viewpoint to be expressed clear? | The soul of the article |
| **Target Audience** | Is it clear who it's written for? | Determines expression style |
| **Publishing Platform** | Is it clear where to publish? | Determines content format |
| **Real Cases** | Are there specific examples/experiences? | **Social media required** |
| **Emotional Resonance** | Are there resonance points/emotional hooks? | **Social media required** |
| **Unique Viewpoints** | Are there insights others haven't mentioned? | **90+ point required** |

#### Should Be Complete (Try to question)

| Dimension | Check Item | Description |
|-----------|-----------|-------------|
| **External Validation** | Is there search material to support? | Adds persuasiveness |

#### Nice to Have (Better if present)

| Dimension | Check Item | Description |
|-----------|-----------|-------------|
| **Interactive Design** | Is there a clear call to action? | Guide reader participation |
| **Style Preference** | What style? | Professional/humorous/story-based |

---

### 90+ Point Content Standards

| Score | Characteristics | What's Missing |
|-------|----------------|----------------|
| **60-70 points** | Clear structure, clear viewpoints | Lacks real cases, emotional resonance |
| **80-85 points** | + Real cases, emotional resonance | Lacks uniqueness, external validation |
| **90+ points** | + Unique viewpoints, external validation | Nothing missing, polished |

**Only enter generation phase when all "must complete" dimensions are present.**

**Real cases, emotional resonance, and unique viewpoints are the three pillars of social media content - all are essential.**

---

## Output Format

### Markdown Format Specifications (Required)

**All post content must be output in standard Markdown format**, including:

| Format Element | Use Case | Example |
|----------------|----------|---------|
| **Heading Levels** | Main title H1, sections H2-H4 | `# Title` `## Section` |
| **Bold Emphasis** | Core viewpoints, keywords | `**Core viewpoint**` |
| **Quote Blocks** | Golden sentences, key assertions | `> Quote content` |
| **Lists** | Parallel points, step descriptions | `- Item 1` |
| **Horizontal Rules** | Separate different parts | `---` |
| **Code Blocks** | Technical content, data | ` ```code``` ` |

**Pre-output checklist:**
- [ ] Clear heading levels (H1 main title, H2 sections, H3 subsections)
- [ ] Bold emphasis on core viewpoints
- [ ] Quote blocks for golden sentences/key assertions
- [ ] Long content in bullet points
- [ ] Horizontal rules between sections
- [ ] Overall format follows standard Markdown syntax

### Universal Structure

```markdown
# [Main Title] Engaging title based on core viewpoint

## [Hook] Attention-grabbing opening

Body content...

---

## [Body Part 1] Expand based on framework structure

- Framework-guided hierarchical content
- Search data-supported viewpoints
- Specific cases and stories

> Core golden sentence in quote block

---

## [Body Part 2] Continue expansion

More content...

---

## [Conclusion] Call to action or summary reinforcement

Concluding content...

---

**[Tags]** #topic1 #topic2 #topic3

**[Reference Materials]** Data sources cited (if search was used)
```

### Platform-Adapted Versions

| Platform | Word Count | Characteristics |
|----------|-----------|-----------------|
| WeChat Official Account | 2000+ | In-depth long articles, clear sections, image suggestions |
| Xiaohongshu | 500-1000 | Practical content, emoji embellishment, list-style |
| Twitter/Weibo | 140-280 | Concise and powerful, one-sentence core, golden sentence style |
| LinkedIn/Maimai | 1000-1500 | Professional workplace, industry insights, case support |

For detailed structure explanations, refer to `references/post-structures.md`

---

## High-Quality Information Sources

The system prioritizes the following types of high-quality sources when searching:

| Source Type | Examples |
|-------------|----------|
| Academic Resources | arXiv, Google Scholar, CNKI |
| Industry Reports | McKinsey, Gartner, iResearch |
| Professional Technical | Official docs, tech blogs, GitHub |
| News Media | Caixin, 36Kr, TechCrunch |
| Knowledge Platforms | Wikipedia, Zhihu high-voted, Medium |

For detailed data source lists, refer to `references/data-sources.md`

---

## Best Practices

1. **Provide sufficient context** - Even for scattered ideas, try to include key points you care about
2. **Answer questions honestly** - Your answers during interactive questioning directly affect post quality
3. **Define target platform** - Knowing which platform you're posting to can generate more suitable content
4. **Leverage search results** - Materials searched by the system can greatly enrich your content
5. **Compare multiple versions** - Compare outputs from different versions, choose the most suitable
6. **Iterate and optimize** - Continue questioning and optimizing based on generated results

---

## Examples

See `examples/` directory for complete usage examples:
- `basic-usage.md` - Basic usage examples
- `advanced-usage.md` - Advanced scenario examples

---

## Reference Documents

- `references/thinking-frameworks.md` - Detailed framework explanations
- `references/questioning-strategy.md` - **Continuous progressive questioning strategy (core)**
- `references/questioning-modes.md` - **Questioning mode selection guide (new)**
- `references/question-templates.md` - Question template library
- `references/post-structures.md` - Post structure guide
- `references/data-sources.md` - High-quality data source list
