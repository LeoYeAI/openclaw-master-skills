# Continuous Progressive Questioning Strategy

This document explains how the `idea-to-post` skill designs continuous follow-up questions.

**Core Approach: Framework internalization + Multiple choice to lock direction + Open questions to enrich content**

---

## Core Principles

### Principle 1: Internalize Frameworks, Don't Expose Them

**Use framework thinking to design questions, but don't say "I'm using [Framework Name]".**

```
Wrong Example:
"I recommend using the PREP framework. Now for Point: What's your viewpoint?"

Correct Approach:
"What's the core viewpoint you want to express?"
(Question has Point thinking, but dialogue is natural)
```

**Why?**
- Users don't care about frameworks, they just want to express their ideas clearly
- Mechanically applying frameworks makes dialogue stiff
- Frameworks are thinking tools, not questioning templates

---

### Principle 2: Combine Multiple Choice + Open Questions

```
Multiple Choice (AskUserQuestion)  Quickly lock direction
Open Questions (direct dialogue)    Deeply mine content

Multiple Choice = Skeleton | Open Questions = Flesh and blood
```

| Question Type | Applicable Scenario | Example |
|---------------|---------------------|---------|
| **Multiple Choice** | Clear options, quick classification | "What's the goal? A. Tutorial B. Tips C. Analysis" |
| **Open Questions** | Stories/experiences/emotions/details | "Can you tell me more?" |
| **Mixed** | Options + Custom follow-up | After selecting "Other", continue follow-up |

---

### Principle 3: Progressive Deepening, Dynamic Adjustment

**Each round of questions is based on the previous answer, naturally transitioning.**

```
User: "todo is an underrated command"
    ↓
Follow-up: What does "underrated" specifically mean? (What thinking)
    ↓
User: "People don't know its true purpose"
    ↓
Follow-up: What's the true purpose? (What thinking follow-up)
    ↓
User: "It's a conversation memory mechanism"
    ↓
Follow-up: What pain point does it solve? (Why thinking)
    ↓
Follow-up: Any specific examples? (Example thinking)
```

**Framework thinking is integrated into each question, but transitions are natural, not mechanically following a template.**

---

### Principle 4: Based on Topic, Don't Ask Irrelevant Questions

**Questions must be closely tied to the core topic of user input.**

```
Good questions:
- What does "ugly-handsome" specifically mean? (Tied to topic)
- Where in the skill architecture is it "ugly"? (Specific)
- What did this skill help you do? (Validate value)

Bad questions:
- Do you like drinking coffee? (Unrelated to topic)
- How's the weather today? (Completely unrelated)
```

---

### Principle 5: Focus on 1-2 Questions Per Round

**Avoid information overload, give user thinking space.**

```
Wrong: Ask 5 at once
"Goal? Audience? Platform? Style? What to emphasize?"

Correct: Multiple rounds
Round 1: What's the goal?
Round 2: Who's the audience?
Round 3: What's the platform?
```

---

## Framework Thinking Integrated into Questions

### PREP Thinking Integration

```
Point thinking   → "What's your core viewpoint?"
Reason thinking  → "Why do you think so? What's the reason?"
Example thinking → "Any specific examples or experiences?"
Point thinking   → "Want to summarize in one sentence?"
```

### 5W1H Thinking Integration

```
What thinking → "What does this specifically refer to?"
Why thinking  → "Why is it important? What does it solve?"
Who thinking  → "Who's the target audience?"
Where thinking→ "In what scenario?"
When thinking → "When did it happen?"
How thinking  → "How is it done?"
```

### SCQA Thinking Integration

```
Situation thinking    → "What was the initial state?"
Complication thinking → "What conflict or challenge appeared?"
Question thinking     → "What question arose?"
Answer thinking       → "What's the answer/solution?"
```

**Frameworks are thinking tools, not questioning templates. Use framework thinking to design questions, but don't mention frameworks.**

---

## Multiple Choice vs Open Questions

### When to Use Multiple Choice (AskUserQuestion)?

```
Suitable scenarios:
✅ Clear options (platform, style, goal, structure)
✅ Need quick classification
✅ Easy for users to choose
✅ No detailed explanation needed

Example:
"What's the target platform? A. WeChat OA B. Xiaohongshu C. Weibo"
"What's the article style? A. Professional B. Humorous C. Story-based"
```

### When to Use Open Questions (Direct Dialogue)?

```
Suitable scenarios:
✅ Need specific stories/experiences
✅ Need subtle emotions/feelings
✅ Need unique insights/thoughts
✅ Options cannot be preset

Example:
"Can you tell me more?"
"How did you feel at that moment?"
"Why do you think so?"
"Any specific examples?"
```

### Mixed Usage

```
AskUserQuestion provides options + "Other" option
    ↓
If user selects "Other"
    ↓
Continue open follow-up
```

---

## Progressive Questioning Flow

### Stage 1: Direction Locking (mainly multiple choice)

```
Round 1: What's the goal?
Round 2: Who's the target audience?
Round 3: Publishing platform?
```

**Purpose: Quickly position article type and direction**

---

### Stage 2: Core Deep Dive (mainly open questions)

```
User: "todo is an underrated command"
    ↓
"What does 'underrated' specifically mean?" (What thinking)
    ↓
"What's the true purpose?" (What follow-up)
    ↓
"What pain point does it solve?" (Why thinking)
    ↓
"Any specific examples?" (Example thinking)
```

**Purpose: Deeply mine core viewpoints and value**

---

### Stage 3: Supporting Material (mainly open questions)

```
"Can you tell me more?"
"Any comparison cases?"
"How did you feel at that moment?"
"Any specific data?"
```

**Purpose: Enrich content, get stories and emotions**

---

### Stage 4: Structure Confirmation (mainly multiple choice)

```
"Article structure? A. Problem-Analysis B. What-Why-How"
"Style preference? A. Professional B. Humorous C. Story-based"
```

**Purpose: Confirm generation method**

---

### Stage 5: Final Touches (mixed)

```
"Core golden sentence?"
"Want readers to do what?"
"Anything else to add?"
```

**Purpose: Check for gaps**

---

## Typical Dialogue Examples

### Example: Viewpoint-Type Topic

```
[Round 1: Direction Locking]
Skill: What's the article's goal?
User: Skill improvement
Skill: Who's the target reader?
User: Advanced users

[Round 2: Core Deep Dive]
Skill: What's the core viewpoint you want to express?
User: todo is an underrated command
Skill: What does "underrated" specifically mean?
User: People don't know its true purpose
Skill: What's the true purpose?
User: It's a conversation memory mechanism, lets Claude remember progress
Skill: What pain point does conversation memory solve?
User: When multitasking, Claude forgets where it got to

[Round 3: Supporting Material]
Skill: Can you tell me more? Any examples?
User: For example... (user describes specific experience)
Skill: In that experience, what was the moment you most felt todo's value?
User: When Claude accurately said "continue task 3"

[Round 4: Structure Confirmation]
Skill: Article structure tendency?
User: Problem-Analysis-Value

[Round 5: Closing]
Skill: Core golden sentence?
User: Underrated tool
Skill: What do you want readers to do?
User: Follow for more

→ Information complete, generate
```

---

## Follow-Up Techniques

### 1. What Follow-Up - Specify

```
User: "Efficiency improved a lot"
Follow-up: "How much specifically?"
```

### 2. Why Follow-Up - Dig Reasons

```
User: "This solution works well"
Follow-up: "Why do you think so?"
```

### 3. How Follow-Up - Dig Methods

```
User: "We succeeded"
Follow-up: "How did you do it?"
```

### 4. Example Follow-Up - Request Cases

```
User: "This is indeed a problem"
Follow-up: "Any specific examples?"
```

### 5. Emotion Follow-Up - Dig Emotions

```
User: "Finally solved the problem"
Follow-up: "How did you feel at that moment?"
```

### 6. Contrast Follow-Up - Compare

```
User: "Much better now"
Follow-up: "What's the biggest difference from before?"
```

---

## Specific Follow-Up Techniques (Prevent User Skipping)

### Problem: Follow-up too abstract, users easily skip

```
Too abstract: "Can you tell me more?"
More specific: "When was the most recent time you encountered
               'forgot progress when multitasking'?
               What feature were you working on? What specifically did Claude say?"
```

### Technique 1: Ask Specific Time

```
Vague: "Any specific examples?"
Specific: "When was the most recent time? Last week? Last month?"
```

### Technique 2: Ask Specific Scenario

```
Vague: "How did it happen?"
Specific: "What feature were you working on? Login? Payment? Or other?"
```

### Technique 3: Ask Specific Reaction

```
Vague: "How did you feel then?"
Specific: "When Claude said 'where did I get to', what was your reaction?
           Were you speechless? Frustrated? Or helpless?"
```

### Technique 4: Provide Template to Lower Barrier

```
Vague: "Can you tell me more?"
Specific: "Use this template:
           That day I was working on [feature],
           Claude said [specific words],
           My feeling at that time was [emotion]"
```

### Technique 5: Binary Choice to Reduce Difficulty

```
Vague: "What specific scenario?"
Specific: "Was it when developing new features, or when debugging bugs?"
```

### Technique 6: Ask Minimum Detail

```
Vague: "How did the whole process go?"
Specific: "What was the first thing Claude said?"
```

---

## Follow-Up Techniques for Mining Emotional Value

### Why Need Emotional Value?

**The core of social media is "people", not "information".**

Readers want to see:
- Pits you've stepped in
- Moments you broke down
- Surprise when you discovered value
- Not cold technical analysis

### Emotion Follow-Up Techniques

#### 1. Ask "Breakdown Moments"

```
"What was the most crushing/speechless/frustrating moment?
 What specifically happened?"
```

#### 2. Ask "Surprise Moments"

```
"How did you feel when you discovered todo's true value?
 Was it the 'aha!' of enlightenment,
 Or the relief of 'finally found it'?"
```

#### 3. Ask "Turning Points"

```
"From 'thought it was useless' to 'it's amazing', what happened in between?
 Was there a specific moment that changed your view?"
```

#### 4. Ask "Physical Reactions"

```
"What physical reaction did you have at that moment?
 Did you slap your thigh? Sigh deeply?
 Or couldn't help but laugh?"
```

#### 5. Ask "After-Effects"

```
"Since then, how has your usage habit changed?
 Do you use todo every time? Or recommend it to others?"
```

---

## Follow-Up Techniques for Mining Uniqueness

### Why Need Uniqueness?

**Avoid content being too "standard", like official documentation.**

Readers want to see:
- Tips others haven't discovered
- Pits others haven't stepped in
- Usage methods others don't have

### Uniqueness Follow-Up Techniques

#### 1. Ask "Unique Discoveries"

```
"Have you discovered any tips not mentioned in official docs?
 Or some usage others don't know about?"
```

#### 2. Ask "Unique Pits"

```
"Have you stepped in pits others haven't?
 Or encountered some weird bugs?"
```

#### 3. Ask "Unique Usage"

```
"Do you have any 'non-standard' usage methods?
 Like using todo for unexpected things?"
```

#### 4. Ask "Unique Viewpoints"

```
"Do you have any 'counter-intuitive' understanding of todo?
 Different from most people's views?"
```

#### 5. Ask "Unique Combinations"

```
"Have you combined todo with other commands/tools?
 Produced unexpected results?"
```

---

## Search Failure Handling Strategies

### Problem: Search failure loses external validation

```
If WebSearch fails:
- Content lacks data support
- Viewpoints lack authority
- Persuasiveness decreases
```

### Solutions

#### Solution 1: Clearly Inform and Seek Alternatives

```
"Search service temporarily unavailable.
To maintain content persuasiveness, do you have:
- Seen relevant discussions or articles?
- Done some tests or verification yourself?
- Have some data to share?"
```

#### Solution 2: Make User the Validation

```
"Search failed, but no worries.
Your usage experience is itself good validation.
Can you tell me:
- How long have you used todo?
- Roughly how many times?
- Compared using vs not using?"
```

#### Solution 3: Seek Community Validation

```
"Search failed.
Have you seen relevant discussions in:
- GitHub Issues
- Reddit
- Twitter/X
- Tech blogs

If so, can you share? I'll integrate into content."
```

#### Solution 4: Lower External Validation Priority

```
"Search failed, no external data support.
This affects content authority, but we can:
1. Use your real experience to compensate
2. Emphasize this is personal experience sharing
3. Add 'welcome to exchange and supplement' at the end

Is this okay?"
```

---

## Information Completeness Check

### Must Be Complete (Continue questioning if missing, cannot skip)

- [ ] **Core Viewpoint** - What's the viewpoint to express?
- [ ] **Target Audience** - Who's it written for?
- [ ] **Publishing Platform** - Where to publish?
- [ ] **Supporting Cases** - Any specific examples/experiences? (**Social media required**)
- [ ] **Emotional Value** - Any resonance points/emotional hooks? (**Social media required**)

### Should Be Complete (Try to question)

- [ ] **External Validation** - Any search materials to cite?
- [ ] **Unique Viewpoints** - Any insights others haven't mentioned?

### Nice to Have (Better if present)

- [ ] **Interactive Design** - Want readers to do what?
- [ ] **Call to Action** - Any specific action guidance?
- [ ] **Style Preference** - What style?

---

## Timing to Stop Questioning

### Can Stop

1. **Core dimensions complete** (viewpoint, audience, platform, cases, emotions)
2. User shows impatience (continuous short answers)
3. Information becomes redundant (new info no longer brings new dimensions)
4. User explicitly expresses satisfaction

### Must Continue

1. **Core viewpoint vague** - Don't know what you want to express
2. **Supporting cases missing** - No real cases/experiences (**Social media required**)
3. **Emotional value missing** - No resonance points/emotional hooks (**Social media required**)
4. **External validation missing** - Search failed and no alternative info

### Special Note on Cases and Emotions

**Cases and emotions are the soul of social media content, cannot be skipped.**

If user doesn't want to provide:
- Clearly inform impact: "Without real cases, content lacks authenticity"
- Provide guidance: "Can be a small fragment, doesn't need complete story"
- Lower barrier: "Even a momentary feeling is fine"
- Final confirmation: "Sure you don't need cases? Content will be quite dry"

---

## Iterative Optimization Flow (90+ Point Essential)

### Why Need Iterative Optimization?

**First draft is often only 70-80 points, needs polishing to reach 90+ points.**

```
After first draft generated:
- Information may not be fully integrated
- Cases may not be vivid enough
- Emotions may not be full enough
- Uniqueness may not be突出

Need: Reflect → Optimize → Regenerate
```

---

### Timing of Iterative Optimization

**After first draft generated, proactively ask:**

```
"Content generated. Before finalizing, I want to confirm a few questions:

1. Are cases vivid? Need to add details?
2. Is emotional resonance there? Need to strengthen?
3. Are unique viewpoints突出? Need to reinforce?
4. Anything else that needs optimization?"
```

---

### Directions for Iterative Optimization

#### 1. Cases Not Vivid Enough

```
"The case part feels it could be more vivid.
Can you add some details?
- Specific dialogue?
- The scene at the time?
- Your reaction?"
```

#### 2. Emotions Not Full Enough

```
"The emotion part could be fuller.
The moment that made you most [crushed/surprised],
Can you tell me more?
What was your thinking then?
Any physical reaction?"
```

#### 3. Uniqueness Not Prominent

```
"The uniqueness part could be more突出.
This tip/viewpoint,
Is it your exclusive discovery?
Or have others mentioned it?
If exclusive, can you emphasize it more?"
```

#### 4. Structure Can Be Optimized

```
"The article structure could be optimized.
Want to adjust:
- Put cases at the very beginning?
- Make golden sentences into titles?
- Make comparisons into tables?"
```

---

### Example of Iterative Optimization

```
Skill: First draft generated. Before finalizing, I want to confirm:
      Are cases vivid? Need to add details?

User: Cases are a bit dry, not specific enough

Skill: Can you add some details?
      Like:
      - What feature were you working on?
      - What specifically did Claude say?
      - What was your reaction?

User: It was when working on user login...
      Claude said "where did I get to"
      I was speechless...

Skill: Good, I'll update the content, add these details.
      (Regenerate)

Skill: Update complete. Anything else to optimize?

User: Title could be more attractive

Skill: Current title is "Underrated Tool: Claude Code's todo Command"
      What style title do you want?
      A. Suspense
      B. Data
      C. Contrast
      D. Golden sentence

User: D - Golden sentence

Skill: Good, I'll redesign the title...
      (Update title)

Skill: Final version complete.
      Want to see if anything else needs optimization?

User: No, this is fine

Skill: Good, final version is ready.
```

---

### Principles of Iterative Optimization

1. **Proactively initiate** - After generation, proactively ask, don't wait for user to bring up
2. **Specific suggestions** - Don't ask "is it good?", ask "what needs optimization?"
3. **Provide options** - Give specific optimization directions to choose from
4. **Quick iterations** - Small steps, one optimization at a time
5. **Confirm before ending** - User confirms no more optimization needed before ending

---

### Complete Iterative Optimization Flow

```
First draft generated
    ↓
Proactively reflect: What could be better?
    ↓
User feedback: Cases are a bit dry
    ↓
Specific follow-up: What details to add?
    ↓
Regenerate: Integrate new information
    ↓
Reflect again: Any more optimization?
    ↓
User feedback: Title not attractive enough
    ↓
Provide options: Suspense/Data/Contrast/Golden sentence?
    ↓
Regenerate: Update title
    ↓
Final confirmation: Anything else to optimize?
    ↓
User confirms: It's good
    ↓
Final version
```

---

## Key Takeaways Summary

1. **Framework internalization** - Use framework thinking to design questions, but don't mention frameworks
2. **Mixed questioning** - Multiple choice to set direction, open questions to enrich content
3. **Progressive deepening** - Each round based on previous answer, natural transition
4. **Tie to topic** - Don't ask irrelevant questions
5. **Focus per round** - 1-2 questions, no overload
6. **Complete before stop** - Only generate when core dimensions are all present
7. **Cases and emotions required** - Social media content must have real cases and emotional resonance
8. **Specific follow-ups** - Prevent user skipping, ask specific time/scenario/reaction
9. **Handle search failures** - Seek alternatives, don't give up on external validation
10. **Pursue uniqueness** - Mine tips, pits, viewpoints others don't have
11. **90+ point goal** - Need 7-10 rounds of dialogue, pursue quality social media content
12. **Iterative optimization** - After first draft, proactively reflect and optimize, don't settle for "can generate"

---

## Path to 90+ Point Content

### Dialogue Rounds vs Content Quality

| Rounds | Content Obtained | Quality Improvement |
|--------|-----------------|---------------------|
| 1-2 rounds | Direction, platform, audience | Technical documentation level (60 points) |
| 3-4 rounds | Core viewpoints, value analysis | Clear structure (70 points) |
| 5-6 rounds | Real cases, emotional resonance | Fleshed out (80 points) |
| 7-8 rounds | Unique viewpoints, external validation | Persuasive (85 points) |
| 9-10 rounds | Deep polishing, iterative optimization | Quality content (90+ points) |

### Three Pillars That Cannot Be Skipped

1. **Real Cases** - "Most recent when? What doing? What said?"
2. **Emotional Resonance** - "How did you feel then? Physical reaction?"
3. **Unique Viewpoints** - "Tips others haven't found? Counter-intuitive understanding?"

### Iterative Optimization Is Key to Final 10 Points

First draft 80 points → Reflect and optimize → 90+ points
