---
name: decision-mode
description: Activate when the user asks a question that requires judgment, choice, or decision-making. This skill helps provide structured decision support by analyzing from both AI perspective and user's perspective, with confidence levels and confidence ratings to help users assess the certainty of conclusions.
version: 1.0.0
user-invocable: true
commands:
  - /decide - Activate decision mode for the current question
metadata: {"clawbot":{"emoji":"🎯"}}
---

# Decision Mode 🎯

A structured framework for providing decision support with confidence assessment.

## When to Activate

Activate this skill when:
- User asks "我应该...吗？" / "Should I...?"
- User asks for advice on choices or options
- User presents a dilemma or trade-off
- User asks for predictions or forecasts
- User asks "哪个更好？" / "Which is better?"
- Any question requiring judgment or subjective assessment

**⚠️ CRITICAL: Before activating, determine if information gathering is needed:**
- Does this involve current market conditions? → Search first
- Does this involve recent events or trends? → Search first
- Does this involve time-sensitive data? → Search first
- Is this a general principle question? → Can proceed without search

## Decision Framework

### Step 0: Information Gathering (CRITICAL)

**⚠️ BEFORE providing any analysis, you MUST gather current information.**

#### When to Search
Activate information gathering when the decision involves:
- **Market conditions** (stocks, crypto, real estate, job market)
- **Current events** (policy changes, industry trends, company news)
- **Time-sensitive factors** (economic data, seasonal patterns, deadlines)
- **Rapidly changing domains** (technology, regulations, competitive landscape)
- **Location-specific information** (local laws, market conditions, opportunities)

#### Information Gathering Process

1. **Identify Key Information Needs**
   ```
   For decision "X", I need to know:
   - Current market/industry status
   - Recent trends or changes
   - Relevant data or statistics
   - Expert opinions or consensus
   ```

2. **Execute Search Strategy**
   - Use `web_search` for broad trends and recent news
   - Use `web_fetch` for specific articles or data sources
   - Use `browser` if real-time data needed (prices, job listings, etc.)
   - Check multiple sources for conflicting information

3. **Assess Information Quality**
   | Source Type | Reliability | Use For |
   |-------------|-------------|---------|
   | Official data (gov, exchanges) | High | Facts, statistics |
   | Major news outlets | High-Medium | Current events |
   | Industry reports | Medium | Trends, forecasts |
   | Social media/forums | Low-Medium | Sentiment, anecdotes |
   | Personal blogs | Low | Alternative views |

4. **Document Information Gaps**
   - Note what you couldn't find
   - Acknowledge conflicting sources
   - Adjust confidence downward when information is incomplete

#### Search Result Integration

After gathering information, structure your analysis:

```
### 📊 Information Landscape

**Key Findings:**
- [Finding 1 from search with source]
- [Finding 2 from search with source]
- [Finding 3 from search with source]

**Information Gaps:**
- [What you couldn't find]
- [Conflicting information between sources]

**Source Reliability:**
- High: [Official/expert sources]
- Medium: [News/industry sources]
- Low: [Opinion/social sources]
```

### Step 1: Identify Decision Type

| Type | Description | Example |
|------|-------------|---------|
| **Binary** | Yes/No decision | "Should I quit my job?" |
| **Multi-choice** | Select from options | "Which laptop should I buy?" |
| **Trade-off** | Balance competing factors | "Work-life balance vs career growth" |
| **Prediction** | Forecast future outcome | "Will the stock market crash?" |
| **Risk assessment** | Evaluate potential downsides | "Is this investment safe?" |

### Step 2: Dual Perspective Analysis

For every decision, provide TWO perspectives:

#### 🤖 AI Perspective (Objective Analysis)
- Based on **gathered information** + training data patterns
- Considers typical outcomes and probabilities
- References similar cases or established best practices
- **Explicitly cites sources** for key claims
- Acknowledges limitations of training data AND information gaps

**⚠️ CRITICAL:** If you did NOT search for current information, state clearly:
> *Note: This analysis is based on general patterns from training data. For time-sensitive decisions, current market/condition data should be verified.*

#### 👤 User Perspective (Subjective Analysis)
- Consider user's specific context from conversation history
- Factor in user's stated preferences, values, constraints
- Account for user's risk tolerance (if known)
- Respect user's unique circumstances

### Step 2.5: Information Quality Assessment

Before assigning confidence, evaluate:

| Factor | Impact on Confidence |
|--------|---------------------|
| Information freshness | Older data = lower confidence |
| Source diversity | Single source = lower confidence |
| Source authority | Official > News > Opinion |
| Conflicting signals | Conflicts = lower confidence |
| Information completeness | Gaps = lower confidence |
| Personal knowledge cutoff | Post-cutoff events = lower confidence |

**Confidence Adjustment Rules:**
- No search performed on time-sensitive topic: **Max confidence C (50-69%)**
- Single source: **Reduce by 1 grade**
- Conflicting sources without resolution: **Reduce by 1-2 grades**
- Information >6 months old: **Reduce by 1 grade**

### Step 3: Confidence Assessment

#### Confidence Score (0-100%)

| Score | Interpretation |
|-------|----------------|
| 90-100% | Very High - Strong evidence, clear consensus |
| 70-89% | High - Good evidence, minor uncertainties |
| 50-69% | Moderate - Mixed evidence, reasonable assumptions |
| 30-49% | Low - Limited evidence, significant uncertainty |
| 0-29% | Very Low - Highly speculative, major unknowns |

#### Confidence Level (A-F Rating)

| Rating | Criteria | Action for User |
|--------|----------|-----------------|
| **A** (90-100%) | Multiple reliable sources, clear patterns, strong consensus | Can rely on this conclusion |
| **B** (70-89%) | Good sources, minor gaps, generally reliable | Reliable but verify key facts |
| **C** (50-69%) | Some evidence, reasonable assumptions, mixed signals | Consider as one factor among many |
| **D** (30-49%) | Limited evidence, significant assumptions | Treat as tentative, seek more info |
| **F** (0-29%) | Mostly speculation, major unknowns | Do not rely on this conclusion |

### Step 4: Structured Output Format

```
## 🎯 Decision Analysis: [Brief Title]

### 📋 Decision Type: [Binary/Multi-choice/Trade-off/Prediction/Risk]

---

### 🤖 AI Perspective (Objective)

**Analysis:**
[2-3 sentences of objective analysis based on data/patterns]

**Conclusion:**
[Clear statement of what the data suggests]

**Confidence:** XX% (Grade X)
- **Basis:** [Why this confidence level - what evidence supports it]
- **Limitations:** [What could change this conclusion]

---

### 👤 User Perspective (Subjective)

**Context Considerations:**
- [Factor 1 from user's situation]
- [Factor 2 from user's situation]
- [Factor 3 from user's situation]

**Personalized Conclusion:**
[How the general advice applies specifically to this user]

**Confidence:** XX% (Grade X)
- **Basis:** [Why this confidence level given user's context]
- **Unknowns:** [What user information would improve confidence]

---

### ⚖️ Synthesis

| Factor | AI View | User View | Alignment |
|--------|---------|-----------|-----------|
| [Key factor 1] | [AI assessment] | [User-specific] | ✅/⚠️/❌ |
| [Key factor 2] | [AI assessment] | [User-specific] | ✅/⚠️/❌ |

**Overall Recommendation:**
[Clear, actionable recommendation]

**Confidence Summary:**
- AI Confidence: XX% (Grade X)
- User Confidence: XX% (Grade X)
- **Combined: XX% (Grade X)** ← Most important number

---

### ⚠️ Caveats & Next Steps

**What could change this:**
- [Factor that would increase confidence]
- [Factor that would change recommendation]

**Recommended next steps:**
1. [Specific action to gather more info]
2. [Specific action to reduce risk]
3. [Specific action to validate assumption]

**Disclaimer:**
This analysis is for informational purposes only. Final decisions should consider your complete personal circumstances and, where appropriate, professional advice.
```

## Special Cases

### When User Context is Unknown

If you don't have enough information about the user's specific situation:

> **User Perspective:** *Limited information available about your specific circumstances. The following assumes typical preferences - please share more details for a personalized analysis.*

Confidence for User Perspective should be **D or F** when context is unknown.

### When Evidence is Contradictory

Present both sides clearly:

> **Conflicting Evidence:**
> - **Pro:** [Evidence supporting conclusion X]
> - **Con:** [Evidence supporting conclusion Y]
> 
> **Resolution:** [How you weighed the evidence]

### When Decision Involves Ethics/Values

Be explicit about value judgments:

> **Value Assumption:** This recommendation assumes [value X] is more important than [value Y]. If you prioritize differently, the conclusion may change.

## Examples

### Example 1: Career Decision

**User:** "Should I accept a job offer with 30% higher pay but longer hours?"

**Output:**
```
## 🎯 Decision Analysis: Job Offer Evaluation

### 📋 Decision Type: Trade-off (Compensation vs Work-Life Balance)

---

### 🤖 AI Perspective (Objective)

**Analysis:**
Research indicates that beyond a certain income threshold (varies by location, roughly $75-100K in US), additional income shows diminishing returns on life satisfaction. However, career trajectory impact of early high-paying roles can compound significantly over 10-20 years.

**Conclusion:**
If the user is early in career (< 35 years old), the long-term career capital likely outweighs short-term lifestyle costs. If mid-to-late career, work-life balance becomes relatively more important.

**Confidence:** 65% (Grade C)
- **Basis:** General research on income/happiness correlation and career trajectory patterns
- **Limitations:** Individual variation is enormous; industry-specific factors not considered

---

### 👤 User Perspective (Subjective)

**Context Considerations:**
- User mentioned being 28 years old (early career)
- User previously expressed interest in "building wealth quickly"
- User has no dependents mentioned
- Current role described as "comfortable but stagnant"

**Personalized Conclusion:**
Given your age, stated financial goals, and current career stagnation, the new role aligns well with your expressed priorities. The lifestyle trade-off is likely acceptable given your current life stage.

**Confidence:** 72% (Grade B)
- **Basis:** Good alignment between offer and stated goals
- **Unknowns:** Actual work hours undefined; health impact unclear; partner/family preferences unknown

---

### ⚖️ Synthesis

| Factor | AI View | User View | Alignment |
|--------|---------|-----------|-----------|
| Career timing | Early career = take risks | Early career, wants growth | ✅ Strong |
| Financial priority | Moderate importance | High importance | ✅ Strong |
| Work-life balance | Important long-term | Not stated as priority | ⚠️ Unclear |
| Risk tolerance | Varies individually | Seems moderate-high | ✅ Likely |

**Overall Recommendation:**
**ACCEPT the offer**, with conditions: negotiate start date for transition time; set 6-month review checkpoint; maintain strict boundaries on hours where possible.

**Confidence Summary:**
- AI Confidence: 65% (Grade C)
- User Confidence: 72% (Grade B)
- **Combined: 68% (Grade C+)**

---

### ⚠️ Caveats & Next Steps

**What could change this:**
- If actual hours exceed 60/week consistently
- If health/relationship impacts emerge
- If better offer materializes within 3 months

**Recommended next steps:**
1. Ask current employer for counter-offer (market test)
2. Clarify exact expectations and hours with new employer
3. Set date 6 months out to reassess
```

### Example 2: Simple Factual Question

**User:** "Is Python better than JavaScript for data science?"

**Output:**
```
## 🎯 Decision Analysis: Language Choice for Data Science

### 📋 Decision Type: Multi-choice (Tool Selection)

---

### 🤖 AI Perspective (Objective)

**Analysis:**
Python dominates data science ecosystems with libraries (NumPy, Pandas, scikit-learn, PyTorch, TensorFlow) that have no JavaScript equivalents in maturity or performance. JavaScript's data science ecosystem (TensorFlow.js, Danfo.js) is nascent and primarily targets web deployment, not analysis.

**Conclusion:**
Python is objectively superior for data science work in virtually all dimensions: library ecosystem, performance, community support, job market.

**Confidence:** 95% (Grade A)
- **Basis:** Market data, library maturity metrics, job posting analysis, performance benchmarks
- **Limitations:** Specific use cases (web-embedded ML) may favor JavaScript

---

### 👤 User Perspective (Subjective)

**Context Considerations:**
- No specific user context provided
- Assuming general data science goals

**Personalized Conclusion:**
Without knowing your specific constraints (team requirements, deployment targets, existing skills), the general recommendation is Python.

**Confidence:** 85% (Grade B) → reduced due to unknown context
- **Basis:** Strong general case, but individual circumstances vary
- **Unknowns:** Your current skills, team standards, deployment requirements

---

### ⚖️ Synthesis

| Factor | AI View | User View | Alignment |
|--------|---------|-----------|-----------|
| Library ecosystem | Python dominant | N/A | ✅ |
| Performance | Python better | N/A | ✅ |
| Job market | Python preferred | N/A | ✅ |

**Overall Recommendation:**
Use **Python** for data science. Only consider JavaScript if: (1) your team mandates it, (2) you're deploying to web browsers, or (3) you're building a web app with light ML features.

**Confidence Summary:**
- AI Confidence: 95% (Grade A)
- User Confidence: 85% (Grade B)
- **Combined: 90% (Grade A)**
```

## Confidence Calibration Guide

### Overconfidence Traps to Avoid

❌ **Don't say:** "You should definitely do X"
✅ **Do say:** "Based on [evidence], X appears to be the better option with 75% confidence"

❌ **Don't say:** "The answer is obviously Y"
✅ **Do say:** "Y is supported by [factors], though Z is also reasonable if you prioritize [different factor]"

❌ **Don't say:** "I'm certain that..."
✅ **Do say:** "The evidence strongly suggests... (Grade A, 92% confidence)"

### Underconfidence to Avoid

Don't be so cautious that the analysis becomes useless:

❌ **Weak:** "Both options have pros and cons, it depends on your preferences"
✅ **Stronger:** "Option A is better for [specific scenario], Option B for [specific scenario]. Given [user's stated priority], A is recommended with 70% confidence"

## Final Checklist

Before providing decision analysis, verify:

### Information Gathering
- [ ] **Determined if search is needed** (time-sensitive? market-dependent?)
- [ ] **Performed search** if needed (web_search, web_fetch, browser)
- [ ] **Assessed source quality** (official > news > opinion)
- [ ] **Noted information gaps** and conflicting sources
- [ ] **Documented findings** in Information Landscape section

### Analysis Quality
- [ ] Identified decision type correctly
- [ ] **AI Perspective cites sources** (not just general knowledge)
- [ ] Provided both AI and User perspectives
- [ ] **Adjusted confidence for information quality**
- [ ] Assigned confidence scores (0-100%) and grades (A-F)
- [ ] Explained basis for confidence levels
- [ ] Listed key limitations and unknowns
- [ ] Synthesized perspectives into clear recommendation
- [ ] Included specific caveats and next steps
- [ ] Added appropriate disclaimer

### Red Flags to Avoid
- [ ] Did NOT make time-sensitive claims without current data
- [ ] Did NOT present training data as current market reality
- [ ] Did NOT hide information gaps
- [ ] Did NOT overstate confidence when sources are weak
