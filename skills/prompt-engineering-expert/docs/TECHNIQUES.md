# Advanced Prompt Engineering Techniques

## Table of Contents
1. Chain-of-Thought Prompting
2. Few-Shot Learning
3. Structured Output with XML
4. Role-Based Prompting
5. Prefilling Responses
6. Prompt Chaining
7. Context Management
8. Multimodal Prompting

## 1. Chain-of-Thought (CoT) Prompting

### What It Is
Encouraging Claude to break down complex reasoning into explicit steps before providing a final answer.

### When to Use
- Complex reasoning tasks
- Multi-step problems
- Tasks requiring justification
- When consistency matters

### Basic Structure
```
Let's think through this step by step:

Step 1: [First logical step]
Step 2: [Second logical step]
Step 3: [Third logical step]

Therefore: [Conclusion]
```

### Example
```
Problem: A store sells apples for $2 each and oranges for $3 each. 
If I buy 5 apples and 3 oranges, how much do I spend?

Let's think through this step by step:

Step 1: Calculate apple cost
- 5 apples × $2 per apple = $10

Step 2: Calculate orange cost
- 3 oranges × $3 per orange = $9

Step 3: Calculate total
- $10 + $9 = $19

Therefore: You spend $19 total.
```

### Benefits
- More accurate reasoning
- Easier to identify errors
- Better for complex problems
- More transparent logic

## 2. Few-Shot Learning

### What It Is
Providing examples to guide Claude's behavior without explicit instructions.

### Types

#### 1-Shot (Single Example)
Best for: Simple, straightforward tasks
```
Example: "Happy" → Positive
Now classify: "Terrible" →
```

#### 2-Shot (Two Examples)
Best for: Moderate complexity
```
Example 1: "Great product!" → Positive
Example 2: "Doesn't work well" → Negative
Now classify: "It's okay" →
```

#### Multi-Shot (Multiple Examples)
Best for: Complex patterns, edge cases
```
Example 1: "Love it!" → Positive
Example 2: "Hate it" → Negative
Example 3: "It's fine" → Neutral
Example 4: "Could be better" → Neutral
Example 5: "Amazing!" → Positive
Now classify: "Not bad" →
```

### Best Practices
- Use diverse examples
- Include edge cases
- Show correct format
- Order by complexity
- Use realistic examples

## 3. Structured Output with XML Tags

### What It Is
Using XML tags to structure prompts and guide output format.

### Benefits
- Clear structure
- Easy parsing
- Reduced ambiguity
- Better organization

### Common Patterns

#### Task Definition
```xml
<task>
  <objective>What to accomplish</objective>
  <constraints>Limitations and rules</constraints>
  <format>Expected output format</format>
</task>
```

#### Analysis Structure
```xml
<analysis>
  <problem>Define the problem</problem>
  <context>Relevant background</context>
  <solution>Proposed solution</solution>
  <justification>Why this solution</justification>
</analysis>
```

#### Conditional Logic
```xml
<instructions>
  <if condition="input_type == 'question'">
    <then>Provide detailed answer</then>
  </if>
  <if condition="input_type == 'request'">
    <then>Fulfill the request</then>
  </if>
</instructions>
```

## 4. Role-Based Prompting

### What It Is
Assigning Claude a specific role or expertise to guide behavior.

### Structure
```
You are a [ROLE] with expertise in [DOMAIN].

Your responsibilities:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

When responding:
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

Your task: [Specific task]
```

### Examples

#### Expert Consultant
```
You are a senior management consultant with 20 years of experience 
in business strategy and organizational transformation.

Your task: Analyze this company's challenges and recommend solutions.
```

#### Technical Architect
```
You are a cloud infrastructure architect specializing in scalable systems.

Your task: Design a system architecture for [requirements].
```

#### Creative Director
```
You are a creative director with expertise in brand storytelling and 
visual communication.

Your task: Develop a brand narrative for [product/company].
```

## 5. Prefilling Responses

### What It Is
Starting Claude's response to guide format and tone.

### Benefits
- Ensures correct format
- Sets tone and style
- Guides reasoning
- Improves consistency

### Examples

#### Structured Analysis
```
Prompt: Analyze this market opportunity.

Claude's response should start:
"Here's my analysis of this market opportunity:

Market Size: [Analysis]
Growth Potential: [Analysis]
Competitive Landscape: [Analysis]"
```

#### Step-by-Step Reasoning
```
Prompt: Solve this problem.

Claude's response should start:
"Let me work through this systematically:

1. First, I'll identify the key variables...
2. Then, I'll analyze the relationships...
3. Finally, I'll derive the solution..."
```

#### Formatted Output
```
Prompt: Create a project plan.

Claude's response should start:
"Here's the project plan:

Phase 1: Planning
- Task 1.1: [Description]
- Task 1.2: [Description]

Phase 2: Execution
- Task 2.1: [Description]"
```

## 6. Prompt Chaining

### What It Is
Breaking complex tasks into sequential prompts, using outputs as inputs.

### Structure
```
Prompt 1: Analyze/Extract
↓
Output 1: Structured data
↓
Prompt 2: Process/Transform
↓
Output 2: Processed data
↓
Prompt 3: Generate/Synthesize
↓
Final Output: Result
```

### Example: Document Analysis Pipeline

**Prompt 1: Extract Information**
```
Extract key information from this document:
- Main topic
- Key points (bullet list)
- Important dates
- Relevant entities

Format as JSON.
```

**Prompt 2: Analyze Extracted Data**
```
Analyze this extracted information:
[JSON from Prompt 1]

Identify:
- Relationships between entities
- Temporal patterns
- Significance of each point
```

**Prompt 3: Generate Summary**
```
Based on this analysis:
[Analysis from Prompt 2]

Create an executive summary that:
- Explains the main findings
- Highlights key insights
- Recommends next steps
```

## 7. Context Management

### What It Is
Strategically managing information to optimize token usage and clarity.

### Techniques

#### Progressive Disclosure
```
Start with: High-level overview
Then provide: Relevant details
Finally include: Edge cases and exceptions
```

#### Hierarchical Organization
```
Level 1: Core concept
├── Level 2: Key components
│   ├── Level 3: Specific details
│   └── Level 3: Implementation notes
└── Level 2: Related concepts
```

#### Conditional Information
```
If [condition], include [information]
Else, skip [information]

This reduces unnecessary context.
```

### Best Practices
- Include only necessary context
- Organize hierarchically
- Use references for detailed info
- Summarize before details
- Link related concepts

## 8. Multimodal Prompting

### Vision Prompting

#### Structure
```
Analyze this image:
[IMAGE]

Specifically, identify:
1. [What to look for]
2. [What to analyze]
3. [What to extract]

Format your response as:
[Desired format]
```

#### Example
```
Analyze this chart:
[CHART IMAGE]

Identify:
1. Main trends
2. Anomalies or outliers
3. Predictions for next period

Format as a structured report.
```

### File-Based Prompting

#### Structure
```
Analyze this document:
[FILE]

Extract:
- [Information type 1]
- [Information type 2]
- [Information type 3]

Format as:
[Desired format]
```

#### Example
```
Analyze this PDF financial report:
[PDF FILE]

Extract:
- Revenue by quarter
- Expense categories
- Profit margins

Format as a comparison table.
```

### Embeddings Integration

#### Structure
```
Using these embeddings:
[EMBEDDINGS DATA]

Find:
- Most similar items
- Clusters or groups
- Outliers

Explain the relationships.
```

## Combining Techniques

### Example: Complex Analysis Prompt

```xml
<prompt>
  <role>
    You are a senior data analyst with expertise in business intelligence.
  </role>
  
  <task>
    Analyze this sales data and provide insights.
  </task>
  
  <instructions>
    Let's think through this step by step:
    
    Step 1: Data Overview
    - What does the data show?
    - What time period does it cover?
    - What are the key metrics?
    
    Step 2: Trend Analysis
    - What patterns emerge?
    - Are there seasonal trends?
    - What's the growth trajectory?
    
    Step 3: Comparative Analysis
    - How does this compare to benchmarks?
    - Which segments perform best?
    - Where are the opportunities?
    
    Step 4: Recommendations
    - What actions should we take?
    - What are the priorities?
    - What's the expected impact?
  </instructions>
  
  <format>
    <executive_summary>2-3 sentences</executive_summary>
    <key_findings>Bullet points</key_findings>
    <detailed_analysis>Structured sections</detailed_analysis>
    <recommendations>Prioritized list</recommendations>
  </format>
</prompt>
```

## Anti-Patterns to Avoid

### ❌ Vague Chaining
```
"Analyze this, then summarize it, then give me insights."
```

### ✅ Clear Chaining
```
"Step 1: Extract key metrics from the data
Step 2: Compare to industry benchmarks
Step 3: Identify top 3 opportunities
Step 4: Recommend prioritized actions"
```

### ❌ Unclear Role
```
"Act like an expert and help me."
```

### ✅ Clear Role
```
"You are a senior product manager with 10 years of experience 
in SaaS companies. Your task is to..."
```

### ❌ Ambiguous Format
```
"Give me the results in a nice format."
```

### ✅ Clear Format
```
"Format as a table with columns: Metric, Current, Target, Gap"
```
