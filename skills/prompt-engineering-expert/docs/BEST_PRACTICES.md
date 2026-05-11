# Prompt Engineering Expert - Best Practices Guide

This document synthesizes best practices from Anthropic's official documentation and the Claude Cookbooks to create a comprehensive prompt engineering skill.

## Core Principles for Prompt Engineering

### 1. Clarity and Directness
- **Be explicit**: State exactly what you want Claude to do
- **Avoid ambiguity**: Use precise language that leaves no room for misinterpretation
- **Use concrete examples**: Show, don't just tell
- **Structure logically**: Organize information hierarchically

### 2. Conciseness
- **Respect context windows**: Keep prompts focused and relevant
- **Remove redundancy**: Eliminate unnecessary repetition
- **Progressive disclosure**: Provide details only when needed
- **Token efficiency**: Optimize for both quality and cost

### 3. Appropriate Degrees of Freedom
- **Define constraints**: Set clear boundaries for what Claude should/shouldn't do
- **Specify format**: Be explicit about desired output format
- **Set scope**: Clearly define what's in and out of scope
- **Balance flexibility**: Allow room for Claude's reasoning while maintaining control

## Advanced Prompt Engineering Techniques

### Chain-of-Thought (CoT) Prompting
Encourage step-by-step reasoning for complex tasks:
```
"Let's think through this step by step:
1. First, identify...
2. Then, analyze...
3. Finally, conclude..."
```

### Few-Shot Prompting
Use examples to guide behavior:
- **1-shot**: Single example for simple tasks
- **2-shot**: Two examples for moderate complexity
- **Multi-shot**: Multiple examples for complex patterns

### XML Tags for Structure
Use XML tags for clarity and parsing:
```xml
<task>
  <objective>What you want done</objective>
  <constraints>Limitations and rules</constraints>
  <format>Expected output format</format>
</task>
```

### Role-Based Prompting
Assign expertise to Claude:
```
"You are an expert prompt engineer with deep knowledge of...
Your task is to..."
```

### Prefilling
Start Claude's response to guide format:
```
"Here's my analysis:

Key findings:"
```

### Prompt Chaining
Break complex tasks into sequential prompts:
1. Prompt 1: Analyze input
2. Prompt 2: Process analysis
3. Prompt 3: Generate output

## Custom Instructions & System Prompts

### System Prompt Design
- **Define role**: What expertise should Claude embody?
- **Set tone**: What communication style is appropriate?
- **Establish constraints**: What should Claude avoid?
- **Clarify scope**: What's the domain of expertise?

### Behavioral Guidelines
- **Do's**: Specific behaviors to encourage
- **Don'ts**: Specific behaviors to avoid
- **Edge cases**: How to handle unusual situations
- **Escalation**: When to ask for clarification

## Skill Structure Best Practices

### Naming Conventions
- Use **gerund form** (verb + -ing): "analyzing-financial-statements"
- Use **lowercase with hyphens**: "prompt-engineering-expert"
- Be **descriptive**: Name should indicate capability
- Avoid **generic names**: Be specific about domain

### Writing Effective Descriptions
- **First line**: Clear, concise summary (max 1024 chars)
- **Specificity**: Indicate exact capabilities
- **Use cases**: Mention primary applications
- **Avoid vagueness**: Don't use "helps with" or "assists in"

### Progressive Disclosure Patterns

**Pattern 1: High-level guide with references**
- Start with overview
- Link to detailed sections
- Organize by complexity

**Pattern 2: Domain-specific organization**
- Group by use case
- Separate concerns
- Clear navigation

**Pattern 3: Conditional details**
- Show details based on context
- Provide examples for each path
- Avoid overwhelming options

### File Structure
```
skill-name/
├── SKILL.md (required metadata)
├── CLAUDE.md (main instructions)
├── reference-guide.md (detailed info)
├── examples.md (use cases)
└── troubleshooting.md (common issues)
```

## Evaluation & Testing

### Success Criteria Definition
- **Measurable**: Define what "success" looks like
- **Specific**: Avoid vague metrics
- **Testable**: Can be verified objectively
- **Realistic**: Achievable with the prompt

### Test Case Development
- **Happy path**: Normal, expected usage
- **Edge cases**: Boundary conditions
- **Error cases**: Invalid inputs
- **Stress tests**: Complex scenarios

### Failure Analysis
- **Why did it fail?**: Root cause analysis
- **Pattern recognition**: Identify systematic issues
- **Refinement**: Adjust prompt accordingly

## Anti-Patterns to Avoid

### Common Mistakes
- **Vagueness**: "Help me with this task" (too vague)
- **Contradictions**: Conflicting requirements
- **Over-specification**: Too many constraints
- **Hallucination risks**: Prompts that encourage false information
- **Context leakage**: Unintended information exposure
- **Jailbreak vulnerabilities**: Prompts susceptible to manipulation

### Windows-Style Paths
- ❌ Use: `C:\Users\Documents\file.txt`
- ✅ Use: `/Users/Documents/file.txt` or `~/Documents/file.txt`

### Too Many Options
- Avoid offering 10+ choices
- Limit to 3-5 clear alternatives
- Use progressive disclosure for complex options

## Workflows and Feedback Loops

### Use Workflows for Complex Tasks
- Break into logical steps
- Define inputs/outputs for each step
- Implement feedback mechanisms
- Allow for iteration

### Implement Feedback Loops
- Request clarification when needed
- Validate intermediate results
- Adjust based on feedback
- Confirm understanding

## Content Guidelines

### Avoid Time-Sensitive Information
- Don't hardcode dates
- Use relative references ("current year")
- Provide update mechanisms
- Document when information was current

### Use Consistent Terminology
- Define key terms once
- Use consistently throughout
- Avoid synonyms for same concept
- Create glossary for complex domains

## Multimodal & Advanced Prompting

### Vision Prompting
- Describe what Claude should analyze
- Specify output format
- Provide context about images
- Ask for specific details

### File-Based Prompting
- Specify file types accepted
- Describe expected structure
- Provide parsing instructions
- Handle errors gracefully

### Extended Thinking
- Use for complex reasoning
- Allow more processing time
- Request detailed explanations
- Leverage for novel problems

## Skill Development Workflow

### Build Evaluations First
1. Define success criteria
2. Create test cases
3. Establish baseline
4. Measure improvements

### Develop Iteratively with Claude
1. Start with simple version
2. Test and gather feedback
3. Refine based on results
4. Repeat until satisfied

### Observe How Claude Navigates Skills
- Watch how Claude discovers content
- Note which sections are used
- Identify confusing areas
- Optimize based on usage patterns

## YAML Frontmatter Requirements

```yaml
---
name: skill-name
description: Clear, concise description (max 1024 chars)
---
```

## Token Budget Considerations

- **Skill metadata**: ~100-200 tokens
- **Main instructions**: ~500-1000 tokens
- **Reference files**: ~1000-5000 tokens each
- **Examples**: ~500-1000 tokens each
- **Total budget**: Varies by use case

## Checklist for Effective Skills

### Core Quality
- [ ] Clear, specific name (gerund form)
- [ ] Concise description (1-2 sentences)
- [ ] Well-organized structure
- [ ] Progressive disclosure implemented
- [ ] Consistent terminology
- [ ] No time-sensitive information

### Content
- [ ] Clear use cases defined
- [ ] Examples provided
- [ ] Edge cases documented
- [ ] Limitations stated
- [ ] Troubleshooting guide included

### Testing
- [ ] Test cases created
- [ ] Success criteria defined
- [ ] Edge cases tested
- [ ] Error handling verified
- [ ] Multiple models tested

### Documentation
- [ ] README or overview
- [ ] Usage examples
- [ ] API/integration notes
- [ ] Troubleshooting section
- [ ] Update mechanism documented
