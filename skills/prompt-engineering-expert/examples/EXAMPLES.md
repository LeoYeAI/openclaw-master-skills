# Prompt Engineering Expert - Examples

## Example 1: Refining a Vague Prompt

### Before (Ineffective)
```
Help me write a better prompt for analyzing customer feedback.
```

### After (Effective)
```
You are an expert prompt engineer. I need to create a prompt that:
- Analyzes customer feedback for sentiment (positive/negative/neutral)
- Extracts key themes and pain points
- Identifies actionable recommendations
- Outputs structured JSON with: sentiment, themes (array), pain_points (array), recommendations (array)

The prompt should handle feedback of 50-500 words and be consistent across different customer segments.

Please review this prompt and suggest improvements:
[ORIGINAL PROMPT HERE]
```

## Example 2: Custom Instructions for a Data Analysis Agent

```yaml
---
name: data-analysis-agent
description: Specialized agent for financial data analysis and reporting
---

# Data Analysis Agent Instructions

## Role
You are an expert financial data analyst with deep knowledge of:
- Financial statement analysis
- Trend identification and forecasting
- Risk assessment
- Comparative analysis

## Core Behaviors

### Do's
- Always verify data sources before analysis
- Provide confidence levels for predictions
- Highlight assumptions and limitations
- Use clear visualizations and tables
- Explain methodology before results

### Don'ts
- Don't make predictions beyond 12 months without caveats
- Don't ignore outliers without investigation
- Don't present correlation as causation
- Don't use jargon without explanation
- Don't skip uncertainty quantification

## Output Format
Always structure analysis as:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points)
3. Detailed Analysis (with supporting data)
4. Limitations and Caveats
5. Recommendations (if applicable)

## Scope
- Financial data analysis only
- Historical and current data (not speculation)
- Quantitative analysis preferred
- Escalate to human analyst for strategic decisions
```

## Example 3: Few-Shot Prompt for Classification

```
You are a customer support ticket classifier. Classify each ticket into one of these categories:
- billing: Payment, invoice, or subscription issues
- technical: Software bugs, crashes, or technical problems
- feature_request: Requests for new functionality
- general: General inquiries or feedback

Examples:

Ticket: "I was charged twice for my subscription this month"
Category: billing

Ticket: "The app crashes when I try to upload files larger than 100MB"
Category: technical

Ticket: "Would love to see dark mode in the mobile app"
Category: feature_request

Now classify this ticket:
Ticket: "How do I reset my password?"
Category:
```

## Example 4: Chain-of-Thought Prompt for Complex Analysis

```
Analyze this business scenario step by step:

Step 1: Identify the core problem
- What is the main issue?
- What are the symptoms?
- What's the root cause?

Step 2: Analyze contributing factors
- What external factors are involved?
- What internal factors are involved?
- How do they interact?

Step 3: Evaluate potential solutions
- What are 3-5 viable solutions?
- What are the pros and cons of each?
- What are the implementation challenges?

Step 4: Recommend and justify
- Which solution is best?
- Why is it superior to alternatives?
- What are the risks and mitigation strategies?

Scenario: [YOUR SCENARIO HERE]
```

## Example 5: XML-Structured Prompt for Consistency

```xml
<prompt>
  <metadata>
    <version>1.0</version>
    <purpose>Generate marketing copy for SaaS products</purpose>
    <target_audience>B2B decision makers</target_audience>
  </metadata>
  
  <instructions>
    <objective>
      Create compelling marketing copy that emphasizes ROI and efficiency gains
    </objective>
    
    <constraints>
      <max_length>150 words</max_length>
      <tone>Professional but approachable</tone>
      <avoid>Jargon, hyperbole, false claims</avoid>
    </constraints>
    
    <format>
      <headline>Compelling, benefit-focused (max 10 words)</headline>
      <body>2-3 paragraphs highlighting key benefits</body>
      <cta>Clear call-to-action</cta>
    </format>
    
    <examples>
      <example>
        <product>Project management tool</product>
        <copy>
          Headline: "Cut Project Delays by 40%"
          Body: "Teams waste 8 hours weekly on status updates. Our tool automates coordination..."
        </example>
      </example>
    </examples>
  </instructions>
</prompt>
```

## Example 6: Prompt for Iterative Refinement

```
I'm working on a prompt for [TASK]. Here's my current version:

[CURRENT PROMPT]

I've noticed these issues:
- [ISSUE 1]
- [ISSUE 2]
- [ISSUE 3]

As a prompt engineering expert, please:
1. Identify any additional issues I missed
2. Suggest specific improvements with reasoning
3. Provide a refined version of the prompt
4. Explain what changed and why
5. Suggest test cases to validate the improvements
```

## Example 7: Anti-Pattern Recognition

### ❌ Ineffective Prompt
```
"Analyze this data and tell me what you think about it. Make it good."
```

**Issues:**
- Vague objective ("analyze" and "what you think")
- No format specification
- No success criteria
- Ambiguous quality standard ("make it good")

### ✅ Improved Prompt
```
"Analyze this sales data to identify:
1. Top 3 performing products (by revenue)
2. Seasonal trends (month-over-month changes)
3. Customer segments with highest lifetime value

Format as a structured report with:
- Executive summary (2-3 sentences)
- Key metrics table
- Trend analysis with supporting data
- Actionable recommendations

Focus on insights that could improve Q4 revenue."
```

## Example 8: Testing Framework for Prompts

```
# Prompt Evaluation Framework

## Test Case 1: Happy Path
Input: [Standard, well-formed input]
Expected Output: [Specific, detailed output]
Success Criteria: [Measurable criteria]

## Test Case 2: Edge Case - Ambiguous Input
Input: [Ambiguous or unclear input]
Expected Output: [Request for clarification]
Success Criteria: [Asks clarifying questions]

## Test Case 3: Edge Case - Complex Scenario
Input: [Complex, multi-faceted input]
Expected Output: [Structured, comprehensive analysis]
Success Criteria: [Addresses all aspects]

## Test Case 4: Error Handling
Input: [Invalid or malformed input]
Expected Output: [Clear error message with guidance]
Success Criteria: [Helpful, actionable error message]

## Regression Test
Input: [Previous failing case]
Expected Output: [Now handles correctly]
Success Criteria: [Issue is resolved]
```

## Example 9: Skill Metadata Template

```yaml
---
name: analyzing-financial-statements
description: Expert guidance on analyzing financial statements, identifying trends, and extracting actionable insights for business decision-making
---

# Financial Statement Analysis Skill

## Overview
This skill provides expert guidance on analyzing financial statements...

## Key Capabilities
- Balance sheet analysis
- Income statement interpretation
- Cash flow analysis
- Ratio analysis and benchmarking
- Trend identification
- Risk assessment

## Use Cases
- Evaluating company financial health
- Comparing competitors
- Identifying investment opportunities
- Assessing business performance
- Forecasting financial trends

## Limitations
- Historical data only (not predictive)
- Requires accurate financial data
- Industry context important
- Professional judgment recommended
```

## Example 10: Prompt Optimization Checklist

```
# Prompt Optimization Checklist

## Clarity
- [ ] Objective is crystal clear
- [ ] No ambiguous terms
- [ ] Examples provided
- [ ] Format specified

## Conciseness
- [ ] No unnecessary words
- [ ] Focused on essentials
- [ ] Efficient structure
- [ ] Respects context window

## Completeness
- [ ] All necessary context provided
- [ ] Edge cases addressed
- [ ] Success criteria defined
- [ ] Constraints specified

## Testability
- [ ] Can measure success
- [ ] Has clear pass/fail criteria
- [ ] Repeatable results
- [ ] Handles edge cases

## Robustness
- [ ] Handles variations in input
- [ ] Graceful error handling
- [ ] Consistent output format
- [ ] Resistant to jailbreaks
```
