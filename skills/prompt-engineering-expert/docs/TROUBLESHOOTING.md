# Troubleshooting Guide

## Common Prompt Issues and Solutions

### Issue 1: Inconsistent Outputs

**Symptoms:**
- Same prompt produces different results
- Outputs vary in format or quality
- Unpredictable behavior

**Root Causes:**
- Ambiguous instructions
- Missing constraints
- Insufficient examples
- Unclear success criteria

**Solutions:**
```
1. Add specific format requirements
2. Include multiple examples
3. Define constraints explicitly
4. Specify output structure with XML tags
5. Use role-based prompting for consistency
```

**Example Fix:**
```
❌ Before: "Summarize this article"

✅ After: "Summarize this article in exactly 3 bullet points, 
each 1-2 sentences. Focus on key findings and implications."
```

---

### Issue 2: Hallucinations or False Information

**Symptoms:**
- Claude invents facts
- Confident but incorrect statements
- Made-up citations or data

**Root Causes:**
- Prompts that encourage speculation
- Lack of grounding in facts
- Insufficient context
- Ambiguous questions

**Solutions:**
```
1. Ask Claude to cite sources
2. Request confidence levels
3. Ask for caveats and limitations
4. Provide factual context
5. Ask "What don't you know?"
```

**Example Fix:**
```
❌ Before: "What will happen to the market next year?"

✅ After: "Based on current market data, what are 3 possible 
scenarios for next year? For each, explain your reasoning and 
note your confidence level (high/medium/low)."
```

---

### Issue 3: Vague or Unhelpful Responses

**Symptoms:**
- Generic answers
- Lacks specificity
- Doesn't address the real question
- Too high-level

**Root Causes:**
- Vague prompt
- Missing context
- Unclear objective
- No format specification

**Solutions:**
```
1. Be more specific in the prompt
2. Provide relevant context
3. Specify desired output format
4. Give examples of good responses
5. Define success criteria
```

**Example Fix:**
```
❌ Before: "How can I improve my business?"

✅ After: "I run a SaaS company with $2M ARR. We're losing 
customers to competitors. What are 3 specific strategies to 
improve retention? For each, explain implementation steps and 
expected impact."
```

---

### Issue 4: Too Long or Too Short Responses

**Symptoms:**
- Response is too verbose
- Response is too brief
- Doesn't match expectations
- Wastes tokens

**Root Causes:**
- No length specification
- Unclear scope
- Missing format guidance
- Ambiguous detail level

**Solutions:**
```
1. Specify word/sentence count
2. Define scope clearly
3. Use format templates
4. Provide examples
5. Request specific detail level
```

**Example Fix:**
```
❌ Before: "Explain machine learning"

✅ After: "Explain machine learning in 2-3 paragraphs for 
someone with no technical background. Focus on practical 
applications, not theory."
```

---

### Issue 5: Wrong Output Format

**Symptoms:**
- Output format doesn't match needs
- Can't parse the response
- Incompatible with downstream tools
- Requires manual reformatting

**Root Causes:**
- No format specification
- Ambiguous format request
- Format not clearly demonstrated
- Missing examples

**Solutions:**
```
1. Specify exact format (JSON, CSV, table, etc.)
2. Provide format examples
3. Use XML tags for structure
4. Request specific fields
5. Show before/after examples
```

**Example Fix:**
```
❌ Before: "List the top 5 products"

✅ After: "List the top 5 products in JSON format:
{
  \"products\": [
    {\"name\": \"...\", \"revenue\": \"...\", \"growth\": \"...\"}
  ]
}"
```

---

### Issue 6: Claude Refuses to Respond

**Symptoms:**
- "I can't help with that"
- Declines to answer
- Suggests alternatives
- Seems overly cautious

**Root Causes:**
- Prompt seems harmful
- Ambiguous intent
- Sensitive topic
- Unclear legitimate use case

**Solutions:**
```
1. Clarify legitimate purpose
2. Reframe the question
3. Provide context
4. Explain why you need this
5. Ask for general guidance instead
```

**Example Fix:**
```
❌ Before: "How do I manipulate people?"

✅ After: "I'm writing a novel with a manipulative character. 
How would a psychologist describe manipulation tactics? 
What are the psychological mechanisms involved?"
```

---

### Issue 7: Prompt is Too Long

**Symptoms:**
- Exceeds context window
- Slow responses
- High token usage
- Expensive to run

**Root Causes:**
- Unnecessary context
- Redundant information
- Too many examples
- Verbose instructions

**Solutions:**
```
1. Remove unnecessary context
2. Consolidate similar points
3. Use references instead of full text
4. Reduce number of examples
5. Use progressive disclosure
```

**Example Fix:**
```
❌ Before: [5000 word prompt with full documentation]

✅ After: [500 word prompt with links to detailed docs]
"See REFERENCE.md for detailed specifications"
```

---

### Issue 8: Prompt Doesn't Generalize

**Symptoms:**
- Works for one case, fails for others
- Brittle to input variations
- Breaks with different data
- Not reusable

**Root Causes:**
- Too specific to one example
- Hardcoded values
- Assumes specific format
- Lacks flexibility

**Solutions:**
```
1. Use variables instead of hardcoded values
2. Handle multiple input formats
3. Add error handling
4. Test with diverse inputs
5. Build in flexibility
```

**Example Fix:**
```
❌ Before: "Analyze this Q3 sales data..."

✅ After: "Analyze this [PERIOD] [METRIC] data. 
Handle various formats: CSV, JSON, or table.
If format is unclear, ask for clarification."
```

---

## Debugging Workflow

### Step 1: Identify the Problem
- What's not working?
- How does it fail?
- What's the impact?

### Step 2: Analyze the Prompt
- Is the objective clear?
- Are instructions specific?
- Is context sufficient?
- Is format specified?

### Step 3: Test Hypotheses
- Try adding more context
- Try being more specific
- Try providing examples
- Try changing format

### Step 4: Implement Fix
- Update the prompt
- Test with multiple inputs
- Verify consistency
- Document the change

### Step 5: Validate
- Does it work now?
- Does it generalize?
- Is it efficient?
- Is it maintainable?

---

## Quick Reference: Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Inconsistent | Add format specification + examples |
| Hallucinations | Ask for sources + confidence levels |
| Vague | Add specific details + examples |
| Too long | Specify word count + format |
| Wrong format | Show exact format example |
| Refuses | Clarify legitimate purpose |
| Too long prompt | Remove unnecessary context |
| Doesn't generalize | Use variables + handle variations |

---

## Testing Checklist

Before deploying a prompt, verify:

- [ ] Objective is crystal clear
- [ ] Instructions are specific
- [ ] Format is specified
- [ ] Examples are provided
- [ ] Edge cases are handled
- [ ] Works with multiple inputs
- [ ] Output is consistent
- [ ] Tokens are optimized
- [ ] Error handling is clear
- [ ] Documentation is complete
