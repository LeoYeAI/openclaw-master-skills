---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: bc203e0cd506d5a9ca68357cf773d010
    PropagateID: bc203e0cd506d5a9ca68357cf773d010
    ReservedCode1: 30440220540d3f58319068646b7214325de7a1afa68ed12a2eb91223e55452ba6d28b652022024fb2c261d27f9224890637aa90f255cc65293332b2620d4c4d4502098849fe9
    ReservedCode2: 30460221008d52cba1d41b13b2708c6333d89597deffd67670f7d4124f4913ca8f2725b556022100e58a2bd576c0a1ba00408a9dd98c611a9e4972674e7b1c4e3576710470d1c2f7
description: Conduct critical analysis of viewpoints, factual statements, or web content using the critical thinking framework from "Asking the Right Questions". Use when users ask to verify information authenticity, examine viewpoint logic, analyze argument validity, distinguish facts from opinions, or need dialectical thinking based on the Socratic method.
name: is-it-ture
---

# Critical Analysis Skill (Is-It-Ture)

A comprehensive framework for systematic dialectical examination of viewpoints, factual statements, or web content, based on the critical thinking methodology of "Asking the Right Questions" by Browne and Keeley.

## Core Analysis Process

### Step 1: Determine Analysis Type

**Classify the input into one of the following types:**

| Type | Characteristics | Analysis Focus |
|------|-----------------|----------------|
| **Factual Statement** | Verifiable objective claims involving data, research, statistics, etc. | Authenticity, scientific basis, evidence support |
| **Opinion-based Statement** | Contains value judgments, opinions, or suggestions | Thesis, conclusion, argument, evidence, assumptions |
| **Web/Article Content** | Mixed content combining facts and opinions | Separate facts from opinions, then analyze each |

### Step 2: Factual Statement Verification Framework

For each factual statement, systematically verify the following dimensions:

#### 2.1 Source Tracing
- **Original Source**: Where did this data/conclusion originate?
- **Authority**: Does the source have professional credentials (academic journals, government agencies, renowned research institutions)?
- **Timeliness**: Is the information outdated? Are there more recent studies or data?

#### 2.2 Multi-Source Cross-Validation (Mandatory Step)

Multi-source cross-validation must be performed for ALL types of input (factual statements, opinion-based statements, web content):

**2.2.1 Verification Strategies**

| Verification Method | Action |
|---------------------|--------|
| **Direct Search Verification** | Use search engines to find reliable sources for original data/research |
| **Cross-Validation** | Verify the same fact through 3+ different reliable sources |
| **Reverse Verification** | Search whether the information has been denied by official/authoritative institutions |
| **Deep Tracing** | Trace the information dissemination chain to find the original source |

**2.2.2 Source Reliability Ratings**

| Grade | Type | Description |
|-------|------|-------------|
| **A+** | Government official data, prestigious academic journals, peer-reviewed research | Highest credibility |
| **A** | Reports from renowned institutions (WHO, World Bank, etc.), verified mainstream media reports | Highly credible |
| **B+** | Professional media, industry association reports, content with clear source citations | Basically credible |
| **B** | General media reports, personal blogs without clear sources | Requires cross-validation |
| **C** | Social media, forum posts, content with untraceable sources | Suspicious |
| **D** | Anonymous posts, marketing content, confirmed misinformation | Not credible |

**2.2.3 Information Source Type Identification**

| Type | Characteristics | Risk Level |
|------|------------------|------------|
| **Misinformation** | Content contradicts established facts, no reliable source support | High |
| **Marketing Copy** | Commercial purpose, exaggeration or out-of-context presentation | High |
| **Unverifiable Private Information** | No verifiable source, subjective statements presented as objective facts | Medium-High |
| **Misleading Information** | Partially true but deliberately misleading | High |
| **Outdated Information** | Previously correct data/conclusions that are now obsolete | Medium |

**2.2.4 Cross-Validation Checklist**

- [ ] Was the original source found? What is the original source?
- [ ] Are there 3+ independent reliable sources supporting this information?
- [ ] Are there any reliable sources that contradict this?
- [ ] Has this information been denied or corrected by authoritative institutions?
- [ ] Does the information come from known misinformation sources?
- [ ] Is there any out-of-context or selective quoting?
- [ ] Have the data/statistics been deliberately distorted (scale, base, comparison method)?

**2.2.5 Information Tracing Path**

```
Original Input
    ↓
Is a specific source mentioned? (research/report/institution/person)
    ├─ Yes → Trace that source → Verify source reliability → Find original data
    └─ No → Multi-keyword search → Attempt to find reliable sources
              ↓
        Reliable source found?
            ├─ Yes → Compare original statement with original information
            └─ No → Mark as "source unknown" → Lower credibility rating
```

#### 2.3 Scientific Principle Verification
- **Consistency with Known Scientific Principles**: Does the statement align with established scientific theories?
- **Mechanism Explanation**: Can it explain the underlying causal mechanism?
- **Boundary Conditions**: What are the applicable conditions and scope of this conclusion?

#### 2.4 Evidence Quality Assessment
- **Direct Evidence**: Is there direct experimental data, statistical data, or research results supporting it?
- **Indirect Evidence**: Is the inference chain rigorous?
- **Sample Quality**: Is the research sample representative? Is the sample size sufficient?
- **Research Design**: Is the research methodology scientific? Are there design flaws?

#### 2.5 Logical Consistency
- **Internal Consistency**: Are there internal contradictions within the statement?
- **External Consistency**: Does it align with other reliable evidence?
- **Causation vs. Correlation**: Has causation been confused with correlation?

### Step 3: Opinion-Based Statement Analysis Framework

Deconstruct opinion-based statements into their components for systematic analysis, while performing multi-source cross-validation on any factual content involved:

#### 3.1 Thesis Identification
- **Core Question**: What question is the author trying to answer?
- **Thesis Type**: Descriptive (what is) or Prescriptive (what should be)?

#### 3.2 Conclusion Extraction
- **Main Conclusion**: What is the author's core claim?
- **Sub-conclusions**: What specific points support the main conclusion?
- **Conclusion Priority**: Which are main points and which are supporting arguments?

#### 3.3 Argument Structure Analysis
```
Argument = Conclusion + Reasons + Evidence + Hidden Assumptions
```

- **Reasons**: What reasons does the author use to support the conclusion?
- **Evidence Types**:
  - Personal experience/cases
  - Unofficial expert opinions
  - Eyewitness testimony
  - Typical cases
  - Quoted authorities/experts
  - Personal observation
  - Research results/statistical data
  - Analogies
  - Presumed premises
- **Evidence Quality**: How strong a conclusion can this type of evidence support?

#### 3.4 Assumption Identification

**Explicit Assumptions** (clearly stated by the author):
- What are the author's preconditions?

**Implicit Assumptions** (unstated but necessary):
- Value Assumption: What does the author consider more important? (efficiency vs. fairness, individual vs. collective, etc.)
- Descriptive Assumption: What does the author believe about how the world works?

**Questions for Examining Assumptions**:
- Is this assumption true/correct?
- If the assumption is false, does the conclusion still hold?
- Does this assumption conflict with reader or societal consensus?

#### 3.5 Position Analysis
- **Author's Position**: From what standpoint is the author speaking?
- **Beneficiary**: Who benefits from this viewpoint?
- **Conflict of Interest**: Is there obvious interest-driven motivation?
- **Reader's Position**: Is the reader automatically placed in a certain position?

### Step 4: Common Fallacy Identification

Examine arguments in opinion-based statements for logical fallacies:

| Fallacy Type | Description | Verification Question |
|--------------|-------------|---------------------|
| **Ad Hominem** | Attacking the person rather than the argument | Is it questioning the person rather than the argument? |
| **Straw Man** | Distorting the opposing view | Is it refuting a point the opponent didn't make? |
| **Slippery Slope** | Unwarranted chain inference | Is there sufficient evidence for each step? |
| **Appeal to Authority** | Using authority instead of argument | Is the authority an expert in this field? Is the issue within their expertise? |
| **Appeal to Emotion** | Using emotion instead of logic | Is it manipulating reader emotions rather than reasoning? |
| **False Dilemma** | Creating a false either/or situation | Are middle-ground or other possibilities ignored? |
| **Equivocation** | Changing key term definitions | Have key concepts changed during argumentation? |
| **Circular Reasoning** | Using the conclusion to prove the premise | Are the reasons merely restatements of the conclusion? |
| **Hasty Generalization** | Concluding from insufficient samples | Is the sample sufficient to represent the whole? |
| **Post Hoc Ergo Propter Hoc** | Assuming sequence equals causation | Is there another explanation? |

### Step 5: Web/Article Content Processing

For web content, additionally perform the following steps:

#### 5.1 Source Reliability Assessment
- **Website Reputation**: What is the nature of the website? (government/academic/commercial/personal blog)
- **Author Information**: Is author information provided? What is the author's professional background?
- **Citations**: Are reliable sources cited?
- **Update Date**: Is the information current?

#### 5.2 Content Structure Analysis
- **Fact vs. Opinion Separation**: Distinguish between objective facts and subjective opinions
- **Contextual Completeness**: Is it taken out of context? Is important background missing?
- **Presentation Method**: Is the data presentation misleading (truncated scales, sample selection, etc.)?

#### 5.3 Source Cross-Validation (Web-Specific)

Web content cross-validation requires special attention to:

| Verification Item | Action |
|-------------------|--------|
| **Domain Verification** | Check if it's a spoofed/phishing website |
| **Publication Time Verification** | Find the original publication date and subsequent update records |
| **Content Consistency Verification** | Compare web snapshots to check for content tampering |
| **Citation Source Tracing** | Trace all external links cited in the webpage |
| **Reverse Image Search** | Perform reverse image search to verify if images have been misappropriated |
| **Social Media Cross-Validation** | Search whether this content was spread on social media and if there was subsequent debunking |

### Step 6: Comprehensive Assessment

Based on the above analysis, provide a structured assessment conclusion:

#### Assessment Standards

| Grade | Rating | Meaning |
|-------|--------|---------|
| **Highly Credible** | ⭐⭐⭐⭐⭐ | Sufficient reliable evidence, consistent with scientific principles, rigorous logic |
| **Basically Credible** | ⭐⭐⭐⭐ | Evidence basically sufficient, minor doubts may exist |
| **Pending Verification** | ⭐⭐⭐ | Insufficient evidence, more information needed |
| **Questionable** | ⭐⭐ | Obvious logical problems or insufficient evidence |
| **Not Credible** | ⭐ | Serious errors, misinformation, or malicious misleading |

#### Assessment Report Structure

```
## Comprehensive Assessment Report

### Verdict
[Credibility rating and brief conclusion]

### Key Findings
1. [Primary finding 1]
2. [Primary finding 2]
3. [Primary finding 3]

### Multi-Source Cross-Validation Results
- Original Source Rating: [A+/A/B+/B/C/D]
- Cross-Validation Source Count: [X independent reliable sources]
- Verification Results:
  - Supported by: [X sources]
  - Contradicted by: [X sources]
  - No reliable source found: [description]
- Information Type Identification: [Misinformation/Marketing Copy/Unverifiable Private Information/Misleading Information/Outdated Information/Normal]

### Evidence Assessment
- Evidence Source: [description]
- Evidence Quality: [assessment]
- Evidence Gap: [existing deficiencies]

### Argumentation Quality
- Logical Structure: [assessment]
- Assumption Reasonableness: [assessment]
- Potential Fallacies: [identified issues]

### Position and Interest Analysis
- Author's Position: [identified]
- Potential Bias: [identified]
- Reader Impact: [analysis]

### Reasoning Process Supporting Conclusion
[detailed reasoning chain]

### Usage Recommendations
[How to use this information, any precautions]
```

## Usage Examples

### Example 1: Factual Statement Verification

**Input**: "A study shows that drinking coffee every day can extend lifespan."

**Analysis Output**:
```
### Analysis Type: Factual Statement

### Source Tracing
- Research Source: [tracing results]
- Authority: [assessment]
- Sample Size and Research Design: [analysis]

### Scientific Principle Verification
- Mechanism Explanation: [whether it exists]
- Causation vs. Correlation: [distinction result]

### Evidence Assessment
- Direct Evidence: [assessment]
- Confounding Variables: [whether considered]
- Reproducibility: [whether other research supports/contradicts]

### Comprehensive Assessment
[verdict and reasoning]
```

### Example 2: Opinion-Based Statement Verification

**Input**: "We should completely ban artificial intelligence because it will replace human jobs."

**Analysis Output**:
```
### Analysis Type: Opinion-based Statement

### Thesis Identification
- Core Question: Should AI be banned?
- Thesis Type: Prescriptive

### Conclusion Extraction
- Main Conclusion: AI should be completely banned
- Implicit Premise: The harm of AI replacing jobs outweighs its benefits

### Argumentation Structure
- Reason: AI will replace human jobs
- Evidence: [missing argumentation]
- Assumptions: Work is the main value of life; banning AI won't cause other problems

### Fallacy Identification
- Slippery Slope: Assuming replacement will lead to complete replacement
- False Dilemma: Ignoring the possibility of "regulated development"
- Hasty Generalization: Using partial replacement cases to generalize the whole

### Comprehensive Assessment
[verdict]
```

## Important Notes

1. **Maintain Objectivity**: Do not take sides during analysis; let evidence speak
2. **Distinguish Certainty from Speculation**: Clearly mark what is certain vs. what is speculation
3. **Acknowledge Uncertainty**: Be transparent about problems that cannot be determined rather than forcing conclusions
4. **Focus on Evidence Quality**: Not all evidence has equal value
5. **Recognize Timeliness**: Information may change over time; dynamic evaluation is needed
6. **Multi-perspective Examination**: Multiple reasonable perspectives may exist for the same issue
7. **Prioritize Multi-Source Validation**: For all input, multi-source cross-validation MUST be performed first; do not rely solely on a single source
8. **Be Vigilant Against Source-less Information**: For information that cannot be traced to reliable sources, credibility ratings must be lowered

## Output Standards

The final output MUST contain ALL of the following sections:

1. **Analysis Type Determination**: Clearly state whether it is factual or opinion-based
2. **Multi-Source Cross-Validation** (Mandatory):
   - Original source rating
   - Cross-validation results (supported/contradicted/not found)
   - Information type identification
3. **Systematic Verification**: Analyze item by item according to the above framework
4. **Verdict**: Clear credibility rating (⭐-⭐⭐⭐⭐⭐)
5. **Reasoning Process**: Complete reasoning chain supporting the conclusion
6. **Usage Recommendations**: How to correctly use this information

### Credibility Downgrade Triggers

The following situations MUST trigger credibility rating downgrade:

| Trigger Condition | Downgrade Magnitude |
|-------------------|---------------------|
| Original source cannot be found | At least 1 grade lower |
| No reliable source for cross-validation | At least 2 grades lower |
| Contradicting information found | At least 1 grade lower |
| Identified as misinformation/marketing/misleading | Directly mark as not credible |
| Information from anonymous/private sources | At least 2 grades lower |
