# Question Template Library

This document provides preset question templates for different thinking frameworks for the `idea-to-post` skill.

---

## Universal Stage Questions

Initial questioning stages experienced by all frameworks.

### Post Goal

Use `AskUserQuestion` tool to ask:

```yaml
question: What's the main goal of this post?
header: Post Goal
options:
  - label: Share experience and insights
    description: Record and share personal/team practical experiences, methods, insights
  - label: Express views and opinions
    description: Express your views and positions on something
  - label: Solve specific problems
    description: Provide solutions and suggestions for a problem
  - label: Promote product/service
    description: Introduce product features, attract users
multiSelect: false
```

### Target Audience

```yaml
question: Who's the target audience of this post?
header: Target Audience
options:
  - label: Industry peers/professionals
    description: Content for peers, colleagues, professionals
  - label: General public/readers
    description: Content for broad audience, accessible language
  - label: Specific group
    description: Like entrepreneurs, developers, students, etc.
  - label: Potential customers/users
    description: Content for users who might buy/use the product
multiSelect: false
```

### Target Platform

```yaml
question: Which platform do you plan to publish on?
header: Publishing Platform
options:
  - label: WeChat Official Account
    description: In-depth long articles, 2000+ words
  - label: Xiaohongshu
    description: Practical content, 500-1000 words, use emojis
  - label: Weibo/Twitter
    description: Short and concise, 140-280 characters
  - label: LinkedIn/Maimai
    description: Professional workplace, 1000-1500 words
multiSelect: true
```

---

## 5W1H Question Templates

### What (What is it?)

```yaml
question: What's the core topic you want to introduce/discuss?
header: Core Topic
options:
  - label: A concept/theory
    description: Explain a professional concept or theory
  - label: A product/tool
    description: Introduce usage of a product or tool
  - label: A method/technique
    description: Share a method or technique
  - label: A problem/phenomenon
    description: Discuss a problem or social phenomenon
multiSelect: false
```

### Why (Why?)

```yaml
question: Why is this topic important? What's the core meaning you want to convey?
header: Core Meaning
options:
  - label: Solve pain points
    description: What pain points can this topic solve
  - label: Provide new perspective
    description: Provide different angles of thinking
  - label: Share trends
    description: Share industry or technology trends
  - label: Convey values
    description: Convey certain values or philosophies
multiSelect: true
```

### Who (Who?)

```yaml
question: Who should care about this topic? Who are the main roles involved?
header: Involved Roles
options:
  - label: Individual users
    description: Regular users, individual consumers
  - label: Professionals
    description: Developers, designers, practitioners
  - label: Enterprises/Teams
    description: Company teams, organizations
  - label: Decision makers
    description: Managers, entrepreneurs, investors
multiSelect: true
```

### When (When?)

```yaml
question: What time dimension needs to be emphasized for this topic?
header: Time Dimension
options:
  - label: Current hot topic
    description: Happening now, current trends
  - label: Future trends
    description: Predictions and outlook for the future
  - label: Historical review
    description: Analysis from historical evolution perspective
  - label: Timing choice
    description: Emphasize the best timing for doing something
multiSelect: false
```

### Where (Where?)

```yaml
question: In what scenarios is this topic most relevant?
header: Application Scenarios
options:
  - label: Work scenarios
    description: Workplace, work-related
  - label: Life scenarios
    description: Daily life-related
  - label: Learning scenarios
    description: Learning, education-related
  - label: Specific industry
    description: Within a specific industry/field
multiSelect: true
```

### How (How?)

```yaml
question: What do you want readers to understand or do?
header: Action Orientation
options:
  - label: Understand and know
    description: Mainly let readers understand some knowledge
  - label: Learn methods
    description: Teach readers specific methods/techniques
  - label: Change behavior
    description: Prompt readers to change certain behaviors
  - label: Start action
    description: Prompt readers to start some action
multiSelect: false
```

---

## SCQA Question Templates

### Situation (Situation)

```yaml
question: What's the "Situation" of the story? What's the initial stable state?
header: Initial Situation
options:
  - label: Ideal state
    description: Everything is working normally
  - label: Routine state
    description: Business as usual daily life
  - label: Confused state
    description: Feeling confused or dissatisfied with status quo
  - label: Specific background
    description: A specific timing or background
multiSelect: false
```

### Complication (Conflict)

```yaml
question: What "Conflict" appeared? What broke the original balance?
header: Conflict Event
options:
  - label: Sudden problem
    description: Sudden problems, failures
  - label: New challenge
    description: New demands, new competition
  - label: Unexpected discovery
    description: Discovered something unexpected
  - label: Internal conflict
    description: Team disagreements or conflicts
multiSelect: false
```

### Question (Question)

```yaml
question: What key question arose facing this conflict?
header: Core Question
options:
  - label: How to solve
    description: How to solve this problem?
  - label: Why did it happen
    description: Why did this situation occur?
  - label: What to do
    description: What should we do?
  - label: Whether to change
    description: Do we need to change the status quo?
multiSelect: false
```

### Answer (Answer)

```yaml
question: What's the final "Answer"? What did you discover/do?
header: Solution
options:
  - label: Found root cause
    description: Discovered the source of the problem
  - label: Implemented new solution
    description: Tried a new solution
  - label: Changed understanding
    description: Gained new understanding of the problem
  - label: Achieved results
    description: What was ultimately achieved
multiSelect: true
```

---

## Golden Circle Question Templates

### Why (Core)

```yaml
question: What's the "Why" you most want to convey? What's your belief/original intention?
header: Core Belief
options:
  - label: Change status quo
    description: Believe the status quo needs to change
  - label: Create value
    description: Believe something can create huge value
  - label: Convey philosophy
    description: Believe some philosophy is worth promoting
  - label: Solve pain points
    description: Believe some pain point must be solved
multiSelect: false
```

### How (Method)

```yaml
question: What unique method do you use to achieve this belief?
header: Methodology
options:
  - label: Unique process
    description: Have a unique process/method
  - label: Innovative technology
    description: Used innovative technical means
  - label: Novel model
    description: Adopted novel business model
  - label: Thinking style
    description: Applied different thinking style
multiSelect: true
```

### What (Result)

```yaml
question: What's the final "Result" presented?
header: Final Outcome
options:
  - label: Specific product
    description: A specific product or service
  - label: Service solution
    description: A solution or service
  - label: Content output
    description: An article, course, content
  - label: Change outcome
    description: Some change or improvement result
multiSelect: false
```

---

## AIDA Question Templates

### Attention (Attention)

```yaml
question: What will you use to "grab" reader attention?
header: Attract Attention
options:
  - label: Shocking data
    description: Use counter-intuitive data to attract attention
  - label: Create suspense
    description: Use suspense to spark curiosity
  - label: Direct pain points
    description: Directly point out reader pain points
  - label: Counter-intuitive viewpoint
    description: Propose views opposite to common sense
multiSelect: false
```

### Interest (Interest)

```yaml
question: How to make readers feel "interested"?
header: Spark Interest
options:
  - label: Relate to self
    description: Make readers feel "this is about me"
  - label: Reveal truth
    description: Reveal some little-known truths
  - label: Promise benefits
    description: Promise gains after reading
  - label: Story introduction
    description: Use stories to spark interest
multiSelect: true
```

### Desire (Desire)

```yaml
question: How to make readers feel "desire", wanting your product/solution?
header: Spark Desire
options:
  - label: Paint vision
    description: Paint the beautiful state after use
  - label: Social proof
    description: Show successful cases from others
  - label: Scarcity
    description: Emphasize opportunity scarcity
  - label: Pain point escalation
    description: Emphasize consequences of not solving
multiSelect: true
```

### Action (Action)

```yaml
question: What action do you want readers to take?
header: Prompt Action
options:
  - label: Buy immediately
    description: Directly purchase product
  - label: Free trial
    description: Try first then decide
  - label: Learn more
    description: Click link to learn more
  - label: Follow account
    description: Follow for more content
multiSelect: false
```

---

## PREP Question Templates

### Point (Viewpoint)

```yaml
question: What's your core "viewpoint"? Summarize in one sentence.
header: Core Viewpoint
options:
  - label: Should do something
    description: Suggest doing something
  - label: Shouldn't do something
    description: Suggest not doing something
  - label: Something is good/bad
    description: Evaluation of something
  - label: Something will happen
    description: Prediction about the future
multiSelect: false
```

### Reason (Reason)

```yaml
question: Why do you hold this view? What's the main reason?
header: Supporting Reason
options:
  - label: Personal experience
    description: Based on own experience
  - label: Data support
    description: Based on data and research
  - label: Logical reasoning
    description: Based on logical derivation
  - label: Value judgment
    description: Based on values or principles
multiSelect: true
```

### Example (Example)

```yaml
question: What specific "examples" do you have to support this view?
header: Specific Examples
options:
  - label: Personal experience
    description: Your own story
  - label: Case study
    description: Others' cases
  - label: Data/facts
    description: Specific data or facts
  - label: Analogy explanation
    description: Use analogies to explain
multiSelect: true
```

---

## 5-Why Question Templates

### Initial Problem

```yaml
question: What "problem" do you want to deeply analyze?
header: Initial Problem
options:
  - label: User problem
    description: Problems users encounter
  - label: Product problem
    description: Problems with the product
  - label: Work problem
    description: Problems at work
  - label: Personal problem
    description: Problems in personal development
multiSelect: false
```

### Why Guidance

(Dynamically generated, each time ask "why?" and provide options)

---

## First Principles Question Templates

### Assumptions to Question

```yaml
question: What "common sense" or "assumption" do you want to question?
header: Question Target
options:
  - label: Industry practice
    description: What everyone in the industry does
  - label: Technical limitations
    description: Things considered technically impossible
  - label: Market perception
    description: Market-recognized perceptions
  - label: Personal limitations
    description: Limitations in one's own abilities
multiSelect: false
```

### Basic Facts

```yaml
question: What are the most basic "facts" when broken down?
header: Basic Facts
options:
  - label: Physical laws
    description: Natural physical laws
  - label: Economic laws
    description: Basic economic principles
  - label: Human needs
    description: Fundamental human needs
  - label: Technical essence
    description: Fundamental principles of technology
multiSelect: true
```

### Reconstruct Solution

```yaml
question: Starting from basic facts, how to "reconstruct" the solution?
header: Reconstruction Direction
options:
  - label: Brand new method
    description: Use completely new methods to solve
  - label: Simplify process
    description: Significantly simplify original process
  - label: Cost reduction
    description: Significantly reduce costs
  - label: Performance breakthrough
    description: Achieve performance breakthroughs
multiSelect: true
```

---

## FBA Question Templates

### Feature (Feature)

```yaml
question: What core "features" does your product/service have?
header: Product Features
options:
  - label: Technical features
    description: Technical characteristics
  - label: Functional features
    description: Functional characteristics
  - label: Design features
    description: Design characteristics
  - label: Service features
    description: Service characteristics
multiSelect: true
```

### Benefit (Benefit)

```yaml
question: What "benefit" does this feature bring to users?
header: User Benefits
options:
  - label: Save time
    description: Help users save time
  - label: Save money
    description: Help users save money
  - label: Improve efficiency
    description: Improve work efficiency
  - label: Better experience
    description: Provide better usage experience
multiSelect: true
```

### Advantage (Advantage)

```yaml
question: Compared to other products, what's your "advantage"?
header: Differentiated Advantage
options:
  - label: Faster
    description: Speed advantage
  - label: Cheaper
    description: Price advantage
  - label: Easier to use
    description: Usability advantage
  - label: More professional
    description: Professional advantage
multiSelect: true
```

---

## Style Preference Questions

All frameworks end by asking about style preferences.

```yaml
question: What's the overall style you want for the post?
header: Style Preference
options:
  - label: Professional and rigorous
    description: Data support, tight logic, professional terminology
  - label: Lighthearted and humorous
    description: Lively language, humorous, accessible
  - label: Story-based
    description: Use storytelling, vivid plot
  - label: Practical content
    description: Direct methods, list-style, actionable
multiSelect: false
```

---

## Questioning Strategies

### Progressive Questioning

1. **Broad then narrow**: Ask big picture first, then details
2. **Easy then hard**: Start with easy-to-answer questions, establish rhythm
3. **Provide options**: Provide 3-4 options for each question
4. **Allow customization**: Always support "Other" option for custom input

### Dynamic Adjustment

- Dynamically adjust subsequent questions based on user's previous answers
- If user selects "Other" custom input, analyze the input to determine next steps
- 3-5 questions per stage is appropriate, avoid causing fatigue

### Questioning Timing

- **Stage 1**: Before framework selection (goal, audience, platform)
- **Stage 2**: After framework selection (framework-specific questions)
- **Stage 3**: Before content generation (style preference, supplementary information)
