---
name: skylv-metacognition-engine
description: Enables AI agents to reflect on their own reasoning, detect cognitive biases, and improve decision quality through structured self-examination loops.
keywords: metacognition, self-reflection, bias-detection, reasoning, self-improvement, agent-ai
triggers: metacognition, self-reflection, agent thinking, bias detection, reasoning quality
---

# Metacognition Engine

**Give your AI agent the ability to think about its own thinking.**

## What is Metacognition?

Metacognition = "thinking about thinking." This skill enables AI agents to:
- Detect when they're uncertain or confused
- Identify reasoning gaps before they cause errors
- Recognize cognitive biases in their own output
- Self-correct before delivering answers

## Core Framework

### 1. Pre-Output Check
Before responding, run through these questions:

```
1. Am I confident in this answer? (Yes / Partial / No)
2. What are the 3 most likely ways this could be wrong?
3. What information would I need to be 100% certain?
```

### 2. Cognitive Bias Detection
Check for common biases:
- **Anthropomorphism** — projecting human traits onto AI
- **Authority bias** — deferring to stated credentials without verification
- **Hindsight bias** — acting like something was obvious after the fact
- **Confirmation bias** — seeking only confirming evidence

### 3. Uncertainty Quantification
Express confidence explicitly:

| Confidence | Meaning | Action |
|------------|---------|--------|
| 90%+ | Highly confident | Answer directly |
| 70-89% | Likely correct | Answer + add caveat |
| 50-69% | Uncertain | Ask clarifying questions |
| <50% | Likely wrong | Decline or escalate |

## Example

**Without metacognition:**
> "The capital of France is Paris."

**With metacognition:**
> "Based on my training data, the capital of France is Paris (confidence: 95%).
> Note: My knowledge has a cutoff date. For real-time data, verify current information."

## Use Cases

- **Critical decisions**: Add metacognition checkpoint before any consequential answer
- **User corrections**: When a user corrects you, analyze WHY you were wrong
- **Complex problems**: Run bias detection before solving multi-step problems
- **Knowledge boundaries**: Automatically flag when you're approaching your knowledge limit

## MIT License © SKY-lv
