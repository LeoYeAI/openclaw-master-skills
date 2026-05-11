# Questioning Mode Selection Guide

This document explains how the `idea-to-post` skill chooses between multiple choice and open questions.

---

## Core Approach

```
Multiple Choice (AskUserQuestion)  Quickly lock direction
Open Questions (direct dialogue)    Deeply mine content

Multiple Choice = Skeleton | Open Questions = Flesh and blood
```

**Combining both makes information richer.**

---

## When to Use Multiple Choice?

### Applicable Scenarios

```
✅ Clear options
✅ Need quick classification
✅ Easy for users to choose
✅ No detailed explanation needed
```

### Typical Use Cases

#### 1. Direction Questions

```
"What's the main goal of the article?"
A. Tutorial introduction
B. Skill improvement
C. Viewpoint expression
D. Problem analysis
```

#### 2. Audience Positioning

```
"Who's the target reader?"
A. Complete beginner
B. User with foundation
C. Advanced user
D. Expert
```

#### 3. Platform Selection

```
"Which platform to publish on?"
A. WeChat Official Account
B. Xiaohongshu
C. Weibo/Twitter
D. Juejin/Zhihu
```

#### 4. Style Preference

```
"What's the article style?"
A. Professional and rigorous
B. Lighthearted and humorous
C. Story-based
D. Practical content
```

#### 5. Structure Selection

```
"Article structure tendency?"
A. Problem-Analysis-Value
B. What-Why-How
C. Discovery-Deep dive-Practice
```

### Why Use AskUserQuestion?

```
1. Users choose quickly, no brain strain
2. Options themselves provide inspiration
3. Avoid users not knowing how to answer
4. Standardized, easy to process later
```

---

## When to Use Open Questions?

### Applicable Scenarios

```
✅ Need specific stories/experiences
✅ Need subtle emotions/feelings
✅ Need unique insights/thoughts
✅ Options cannot be preset
```

### Typical Use Cases

#### 1. Concept Deep Dive

```
"What specifically does 'ugly-handsome' mean?"
"What specifically does 'underrated' refer to?"
```

#### 2. Experience Inquiry

```
"Can you tell me more?"
"How specifically did it happen?"
"What difficulty did you encounter at that step?"
```

#### 3. Emotion Mining

```
"How did you feel at that moment?"
"What was the most impressive moment?"
```

#### 4. Case Request

```
"Any specific examples?"
"Can you give a comparison case?"
```

#### 5. Reason Inquiry

```
"Why do you think so?"
"What's the reason for this conclusion?"
```

### Why Use Open Questions?

```
1. Get information multiple choice can't cover
2. Let users express freely, not limited by options
3. Mine deeper content
4. Get personalized answers
```

---

## How to Mix Usage?

### Mode 1: Multiple Choice First, Then Open Follow-up

```
Skill: What's your core viewpoint?
A. Viewpoint 1
B. Viewpoint 2
C. Other (custom)

User: C - Other (custom)

Skill: Please tell me your view specifically:

User: ... (user elaborates)
```

**Usage scenario: Provide option guidance, but allow customization.**

---

### Mode 2: Open First, Then Multiple Choice Confirmation

```
Skill: What's the core viewpoint you want to express?

User: ... (user describes)

Skill: I understand your view is XXX, right?
A. Yes, that's it
B. Not completely, let me add
C. No, let me restate

User: A

Skill: Good, continue to next question...
```

**Usage scenario: Let user express freely first, then confirm understanding.**

---

### Mode 3: Multiple Choice Locks, Open Questions Enrich

```
【Multiple choice locks direction】
Skill: What's the article goal?
User: Skill improvement

【Open questions deep dive】
Skill: What specifically does skill improvement mean?
User: ... (elaborates)

Skill: Any specific cases?
User: ... (case description)
```

**Usage scenario: Most commonly used mode, quick positioning then deep mining.**

---

## Questioning Strategies for Different Stages

### Stage 1: Direction Locking (mainly multiple choice)

```
Purpose: Quickly position article type and direction

Example questions:
- What's the goal? (A/B/C/D)
- Who's the audience? (A/B/C/D)
- Publishing platform? (A/B/C/D)

Why use multiple choice?
- Need quick classification
- Clear options
- Easy for users to choose
```

---

### Stage 2: Core Deep Dive (mainly open questions)

```
Purpose: Deeply mine core viewpoints and value

Example questions:
- What specifically does "underrated" mean?
- What's the true purpose?
- What pain point does it solve?
- Any specific examples?

Why use open questions?
- Need specificity
- Options can't be preset
- Need user to elaborate
```

---

### Stage 3: Supporting Material (mainly open questions)

```
Purpose: Enrich content, get stories and emotions

Example questions:
- Can you tell me more?
- How did you feel at that moment?
- Any comparison cases?
- What's the specific data?

Why use open questions?
- Need stories/experiences
- Need emotions/feelings
- Need details
```

---

### Stage 4: Structure Confirmation (mainly multiple choice)

```
Purpose: Confirm generation method

Example questions:
- Article structure? (A/B/C)
- Style preference? (A/B/C/D)

Why use multiple choice?
- Need standardization
- Clear options
- Easy for subsequent processing
```

---

### Stage 5: Final Touches (mixed)

```
Purpose: Check for gaps

Example questions:
- Core golden sentence? (can be open or provide options)
- What do you want readers to do? (A/B/C/D + Other)
- Anything else to add? (open)

Why mixed?
- Some need confirmation (multiple choice)
- Some need supplement (open questions)
```

---

## Multiple Choice Design Techniques

### Technique 1: Mutually Exclusive Options

```
Not good:
A. Share experience
B. Convey value
(These may overlap)

Good:
A. Share experience
B. Teach methods
C. Express views
D. Analyze problems
```

### Technique 2: Comprehensive Coverage

```
Good options cover main situations:
A. Tutorial introduction
B. Skill improvement
C. Viewpoint expression
D. Problem analysis
E. Other (custom)
```

### Technique 3: Clear Descriptions

```
Not good:
A. Professional
B. Not professional

Good:
A. Professional and rigorous (data support, tight logic)
B. Lighthearted and humorous (lively language, accessible)
```

---

## Open Question Design Techniques

### Technique 1: Specific Follow-up

```
Vague: "Can you elaborate?"
Specific: "What specifically does 'underrated' refer to?"
```

### Technique 2: Guided Inquiry

```
Closed: "Is this experience good?"
Open: "What did this experience bring you?"
```

### Technique 3: Layered Inquiry

```
Layer 1: What is it?
Layer 2: What specifically is it?
Layer 3: Can you give an example?
```

---

## Common Questions

### Q1: When to use multiple choice, when to use open questions?

```
Clear options → Multiple choice
Need stories/emotions → Open questions
Uncertain → Multiple choice first, then open follow-up
```

---

### Q2: How many options for multiple choice is appropriate?

```
Generally 3-4 options + "Other"

Too few (1-2) → No choice meaning
Too many (5+) → Information overload
```

---

### Q3: What if user selects "Other"?

```
Continue open follow-up:
"Please tell me your thoughts specifically:"

Let user elaborate.
```

---

### Q4: What if open question answer is too brief?

```
Continue follow-up:
"Can you tell me more?"
"How specifically was it done?"
"What happened at that step?"

Go deeper layer by layer.
```

---

## Real Combat Example

### Complete Dialogue Flow

```
【Round 1: Multiple choice】
Skill: What's the article goal?
A. Tutorial introduction
B. Skill improvement
C. Viewpoint expression
D. Problem analysis

User: B - Skill improvement

【Round 2: Multiple choice】
Skill: Target audience?
A. Beginner
B. With foundation
C. Advanced
D. Expert

User: C - Advanced

【Round 3: Open question】
Skill: What's the core viewpoint you want to express?

User: todo is an underrated command

【Round 4: Open question】
Skill: What specifically does "underrated" mean?

User: People don't know its true purpose

【Round 5: Open question】
Skill: What's the true purpose?

User: It's a conversation memory mechanism, lets Claude remember progress

【Round 6: Open question】
Skill: Can you tell me more? Any examples?

User: Like... (user describes in detail)

【Round 7: Multiple choice】
Skill: Article structure?
A. Problem-Analysis-Value
B. What-Why-How
C. Discovery-Deep dive-Practice

User: A

【Round 8: Mixed】
Skill: Core golden sentence?
A. Underrated tool
B. Niche but hot
C. Other

User: A

→ Information complete, generate
```

---

## Key Points

1. **Multiple choice** - Quickly lock direction, provide option inspiration
2. **Open questions** - Deeply mine content, get stories and emotions
3. **Mixed usage** - Multiple choice to position, open questions to enrich
4. **Stage distinction** - Use multiple choice for locking and confirmation, open questions for deep diving
5. **Progressive deepening** - Each round based on previous one, natural transition
