---
name: production-model-router
description: Route each user request to the most cost-effective model or multi-model workflow based on task type, complexity, risk, latency, budget, tool needs, and verification requirements.
version: 2026.3.27
---


# Production Model Router

## Overview
Use this skill to decide which model tier, workflow shape, and verification strategy should handle a user's request.

The goal is to maximize cost-effectiveness without sacrificing task fit, correctness, or operational reliability.

This skill does not blindly choose the strongest model. It chooses the cheapest safe path that still meets the quality bar for the task.

It may recommend:
- a single low-cost model
- a single balanced model
- a single premium model
- a tool-assisted model workflow
- a staged multi-model pipeline
- a parallel comparison workflow
- a draft-and-review workflow
- a consensus or verifier workflow

## Primary objective
For every request, choose the minimum-cost execution path that can still satisfy:
- task quality
- correctness requirements
- latency expectations
- safety or risk constraints
- output format needs
- tool and modality requirements

## When to use
Use this skill when you need to decide:
- which model should answer a given user request
- whether a cheap model is enough
- when to escalate to a stronger reasoning model
- when to use one model versus multiple models
- when to use tools instead of relying on pure model reasoning
- how to handle complex calculations, code, multimodal input, long context, or high-risk tasks
- how to balance cost, speed, and answer quality in production

## Do not use
Do not use this skill to:
- answer the original business question directly
- fabricate model capabilities without evidence from the environment or configuration
- assume the most expensive model is always the best choice
- route high-risk exact tasks to a cheap model without verification
- rely on pure language generation for exact arithmetic when tools are available

## Inputs to collect
Collect or infer the following from the request and system context:

### Request characteristics
- task type
- domain
- expected output type
- presence of images, files, tables, code, or long documents
- need for exactness versus approximate usefulness
- whether the request is open-ended or precision-critical

### Execution constraints
- budget sensitivity
- latency sensitivity
- quality expectation
- token or context size pressure
- tool availability
- need for citations or traceability
- need for reproducibility

### Risk profile
- low-risk
- medium-risk
- high-risk

### Failure tolerance
- whether a rough answer is acceptable
- whether the answer must be verified
- whether disagreement between models would be valuable

## Task taxonomy
Classify the request into one or more of these categories:

1. Simple generation
   - rewrite
   - summarization
   - formatting
   - light translation
   - basic brainstorming

2. General reasoning
   - explanation
   - comparison
   - concept mapping
   - normal business analysis

3. Deep reasoning
   - multi-step planning
   - tradeoff analysis
   - architecture design
   - ambiguous decision support
   - chain-dependent reasoning

4. Exact calculation or formal logic
   - arithmetic
   - financial calculations
   - unit conversion
   - spreadsheet-like reasoning
   - symbolic or step-sensitive math
   - combinatorics or logic puzzles where exactness matters

5. Coding and technical execution
   - code generation
   - debugging
   - refactoring
   - test generation
   - query writing
   - infrastructure or API design

6. Long-context synthesis
   - large documents
   - multiple files
   - multi-source comparison
   - transcript or contract review

7. Multi-modal tasks
   - image understanding
   - diagram interpretation
   - PDF with layout-heavy content
   - video or audio related tasks if supported

8. High-risk tasks
   - medical
   - legal
   - financial decisions
   - compliance
   - security-sensitive operations
   - anything where incorrect advice has material consequences

## Core routing principle
Always prefer the cheapest path that can safely succeed.

Apply this order of preference:
1. Cheap single-model path
2. Balanced single-model path
3. Premium single-model path
4. Tool-assisted path
5. Staged multi-model path
6. Parallel multi-model comparison
7. Premium plus verifier or consensus workflow

Do not escalate unless the task characteristics justify it.

## Model tiers
Use abstract capability tiers unless the deployment specifies exact providers.

### Economy tier
Use for:
- simple rewriting
- formatting
- low-risk classification
- short summaries
- lightweight extraction
- first-pass triage

Strengths:
- lowest cost
- fast response
- good for straightforward tasks

Weaknesses:
- weaker deep reasoning
- more brittle on ambiguity
- worse on exactness-critical tasks

### Balanced tier
Use for:
- everyday product and engineering work
- standard reasoning
- moderate code tasks
- moderate document analysis
- most business and writing tasks

Strengths:
- solid quality-cost tradeoff
- handles most normal production traffic
- reasonable speed and robustness

Weaknesses:
- may still fail on highly ambiguous or exacting tasks
- not always enough for hard reasoning or high-risk requests

### Premium tier
Use for:
- deep reasoning
- difficult code and architecture problems
- long-context synthesis with subtle dependencies
- high-value outputs
- high-risk tasks requiring stronger judgment

Strengths:
- strongest reasoning
- better ambiguity handling
- better synthesis quality

Weaknesses:
- highest cost
- often slower
- overkill for simple tasks

### Tool-assisted tier
Use when exactness matters more than fluent wording.

Use this path for:
- arithmetic
- deterministic calculations
- spreadsheet operations
- formula application
- structured data transformation
- exact code execution or testing if available
- retrieval-backed factual tasks

Rule:
When a task requires exact numeric correctness, prefer tools plus model orchestration over pure model reasoning.

## Decision dimensions
Score the request across these dimensions:

### 1. Complexity
- low
- medium
- high
- very high

### 2. Exactness requirement
- low: approximate answer is acceptable
- medium: mostly correct is acceptable
- high: exact result expected
- critical: exact result plus verification required

### 3. Risk level
- low
- medium
- high

### 4. Latency priority
- urgent
- normal
- relaxed

### 5. Budget strategy
- minimize cost
- balanced
- quality-first

### 6. Context burden
- short
- moderate
- long
- extreme

### 7. Modality burden
- text only
- image or PDF
- mixed inputs

## Hard routing rules
Apply these rules before any soft optimization.

### Exact calculation rule
If the task involves exact arithmetic, formulas, tables, accounting-like operations, unit-sensitive conversions, or step-sensitive logic:
- do not rely on a pure language-only route when tools are available
- prefer tool-assisted execution
- use a balanced or premium model only to interpret the task and explain results
- add a verification step for high-impact numeric outputs

### High-risk rule
If the task is high-risk:
- do not use economy-only routing as the final path
- require either premium single-model reasoning with grounding or a model plus verifier workflow
- add citations, checks, or a review pass when possible

### Ambiguity rule
If the task is materially ambiguous and the answer quality depends on interpretation:
- use a stronger reasoning tier or a two-stage workflow
- do not finalize on a cheap first-pass answer without clarification or review

### Long-context rule
If the input is large or multi-document:
- prefer staged processing
- use extraction or chunk summarization first
- then use a stronger model for synthesis if needed
- avoid sending everything to the strongest model by default if staged reduction is cheaper and safe

### Multimodal rule
If the task includes images, diagrams, PDFs with layout dependence, or visual interpretation:
- use a model path that actually supports the required modality
- do not route to a text-only path

### Coding rule
For code tasks:
- simple boilerplate or syntax transforms may use balanced or economy tiers
- debugging, architecture, concurrency, performance, or tricky refactors should escalate to balanced or premium tiers
- if execution, linting, tests, or static analysis tools are available, prefer tool-assisted validation

## Recommended workflows
Choose one of these workflow shapes.

### 1. Single economy
Use when:
- low complexity
- low risk
- low exactness requirement
- low business impact
- latency and cost matter more than polish

Examples:
- rewrite text
- generate short summaries
- classify intent
- format content

### 2. Single balanced
Use when:
- the task is typical production traffic
- moderate reasoning is needed
- quality matters but premium is not justified

Examples:
- standard technical Q&A
- ordinary product copy
- moderate coding tasks
- document understanding with limited ambiguity

### 3. Single premium
Use when:
- the task needs strong reasoning
- the output is strategically important
- ambiguity is high
- long dependency chains matter

Examples:
- system design
- complex debugging
- nuanced tradeoff analysis
- sensitive writing requiring higher judgment

### 4. Tool-assisted reasoning
Use when:
- exactness matters
- calculations are required
- data must be transformed reliably
- code can be executed or checked
- retrieval is needed for factual grounding

Pattern:
- model interprets the request
- tools compute, retrieve, or validate
- model explains and formats the result

### 5. Staged pipeline
Use when:
- the request is large, expensive, or decomposable
- cheap preprocessing can reduce downstream cost

Pattern:
1. economy or balanced model for triage or extraction
2. balanced or premium model for synthesis
3. optional verifier pass

Examples:
- long-document analysis
- large support threads
- multi-file engineering review

### 6. Draft and review
Use when:
- low-cost drafting is possible but final quality matters

Pattern:
1. cheaper model drafts
2. stronger model critiques, corrects, or upgrades

Best for:
- writing
- technical explanations
- proposal drafting
- code review style tasks

### 7. Parallel comparison
Use when:
- model disagreement is informative
- solution diversity is valuable
- the task is comparative or open-ended

Pattern:
1. two models produce independent answers
2. a stronger model or rule layer compares and merges

Best for:
- architecture options
- planning alternatives
- ambiguous recommendations

### 8. Consensus or verifier workflow
Use when:
- correctness matters enough to justify extra cost
- false confidence is dangerous

Pattern:
1. primary model produces answer
2. verifier model checks logic, calculations, or policy fit
3. disagreements trigger escalation or explicit uncertainty

Best for:
- high-risk reasoning
- important financial outputs
- compliance-sensitive content
- high-value technical decisions

## Cost-control strategy
Use these strategies to keep cost high-value.

### Default strategy
- start cheap when safe
- escalate only on signals of failure risk
- avoid premium for routine tasks
- reuse extracted structure instead of repeating full-context calls

### Escalation triggers
Escalate to a stronger model or multi-step workflow when any of these appear:
- multiple dependent reasoning steps
- ambiguous user intent with multiple plausible interpretations
- repeated self-contradiction in draft output
- failure to follow structure or constraints
- long context with subtle dependencies
- code correctness matters beyond surface syntax
- exactness-critical math or finance output
- high-risk domain or high business impact

### De-escalation triggers
Use a cheaper path when:
- the task is mostly formatting or rewriting
- the answer can be approximate
- the task is repetitive and pattern-based
- first-pass triage is enough
- premium capabilities would not materially improve the outcome

## Complex calculation policy
When the request includes complex calculations or formal reasoning:

1. Separate interpretation from computation.
2. Use the model to parse the problem and define the method.
3. Use a deterministic tool or calculational path when available.
4. Ask a verifier layer to check assumptions, formulas, units, and edge cases for high-impact outputs.
5. Present the final answer with explicit assumptions and, when relevant, step order.

Never use a fluent but non-verified freeform model answer as the final authority for exact numeric work when a deterministic path exists.

## Long-context policy
When the request includes large context:
- first extract relevant segments, summaries, or structured facts
- reduce duplication
- preserve citations or pointers when possible
- synthesize only after reduction
- use premium synthesis only if the reduced problem still demands it

## Output format
Return exactly this structure:

Routing Decision:
<single-economy | single-balanced | single-premium | tool-assisted | staged-pipeline | draft-and-review | parallel-comparison | consensus-check>

Primary Reason:
<one-sentence explanation of why this route is the best cost-effective choice>

Task Profile:
- taskType: <task category>
- complexity: <low | medium | high | very high>
- exactness: <low | medium | high | critical>
- risk: <low | medium | high>
- latency: <urgent | normal | relaxed>
- budget: <minimize-cost | balanced | quality-first>
- contextLoad: <short | moderate | long | extreme>
- modality: <text | multimodal>

Recommended Execution Plan:
1. <step 1>
2. <step 2>
3. <step 3>
4. <step 4 if needed>

Model Role Assignment:
- planner: <economy | balanced | premium | not-needed>
- generator: <economy | balanced | premium | tool-assisted>
- verifier: <none | balanced | premium | tool>

Why This Is Cost-Effective:
- <reason 1>
- <reason 2>
- <reason 3>

Escalation Rule:
<when to move to a stronger model or more expensive workflow>

Fallback Rule:
<what to do if the chosen path fails or produces uncertainty>

## Examples

### Example 1: Simple rewrite
Request:
"Rewrite this email to sound more professional."

Output:
Routing Decision:
single-economy

Primary Reason:
This is a low-risk rewriting task where a low-cost model should meet the quality bar.

Task Profile:
- taskType: simple generation
- complexity: low
- exactness: low
- risk: low
- latency: urgent
- budget: minimize-cost
- contextLoad: short
- modality: text

Recommended Execution Plan:
1. Use an economy model to rewrite the email.
2. Preserve intent and tone constraints.
3. Return one polished version and one shorter variant.

Model Role Assignment:
- planner: not-needed
- generator: economy
- verifier: none

Why This Is Cost-Effective:
- The task is structurally simple.
- Premium reasoning is unnecessary.
- Fast low-cost generation is sufficient.

Escalation Rule:
Escalate only if the user requests highly nuanced persuasion, legal sensitivity, or multiple tone variants.

Fallback Rule:
If the first rewrite is too generic, retry once with stricter tone instructions using a balanced model.

### Example 2: Complex system design
Request:
"Design an AI agent architecture for long-form writing with memory, retrieval, conflict resolution, and chapter planning."

Output:
Routing Decision:
single-premium

Primary Reason:
This task requires deep reasoning, abstraction, and multi-part architecture tradeoff analysis.

Task Profile:
- taskType: deep reasoning
- complexity: high
- exactness: medium
- risk: medium
- latency: normal
- budget: balanced
- contextLoad: moderate
- modality: text

Recommended Execution Plan:
1. Use a premium model to identify major architecture components and constraints.
2. Structure the answer into memory layers, retrieval flow, consistency controls, and orchestration.
3. Include tradeoffs and failure modes.
4. Add implementation recommendations only after the design is coherent.

Model Role Assignment:
- planner: premium
- generator: premium
- verifier: none

Why This Is Cost-Effective:
- A weaker model may produce shallow or inconsistent architecture.
- One premium pass is cheaper than multiple failed lower-tier retries.
- The task value justifies stronger reasoning.

Escalation Rule:
Escalate to parallel-comparison only if multiple competing architecture strategies are explicitly required.

Fallback Rule:
If the first answer is too generic, rerun with a staged outline-first then full-design workflow.

### Example 3: Financial calculation with policy impact
Request:
"Calculate the projected monthly burn and runway under three hiring scenarios and explain the assumptions."

Output:
Routing Decision:
tool-assisted

Primary Reason:
This request depends on exact calculations, so deterministic computation is safer and more cost-effective than pure model reasoning.

Task Profile:
- taskType: exact calculation or formal logic
- complexity: high
- exactness: critical
- risk: high
- latency: normal
- budget: balanced
- contextLoad: moderate
- modality: text

Recommended Execution Plan:
1. Use a balanced model to extract the variables, hiring scenarios, and required formulas.
2. Use a deterministic calculator or spreadsheet-capable path to compute burn and runway.
3. Run a verification check on formulas, assumptions, and units.
4. Use the model to present the results clearly with assumptions and scenario breakdowns.

Model Role Assignment:
- planner: balanced
- generator: tool-assisted
- verifier: tool

Why This Is Cost-Effective:
- Exact arithmetic should not depend on freeform model reasoning.
- Deterministic calculation reduces error risk.
- A smaller model can still explain the results after computation.

Escalation Rule:
Escalate to premium review only if the scenario assumptions are ambiguous or strategically sensitive.

Fallback Rule:
If tool-based computation is unavailable, return assumptions explicitly and mark the result as unverified instead of presenting certainty.

### Example 4: Multi-document review
Request:
"Compare these five candidate proposals and recommend the best one based on cost, timeline, technical fit, and risk."

Output:
Routing Decision:
staged-pipeline

Primary Reason:
The request is large and decomposable, so staged extraction and synthesis is more cost-effective than sending everything directly to a premium model.

Task Profile:
- taskType: long-context synthesis
- complexity: high
- exactness: medium
- risk: medium
- latency: relaxed
- budget: balanced
- contextLoad: long
- modality: text

Recommended Execution Plan:
1. Use an economy or balanced model to extract structured facts from each proposal.
2. Normalize the proposals into a common comparison table.
3. Use a stronger model to synthesize tradeoffs and recommend the best option.
4. Add a brief verifier pass if the recommendation is high stakes.

Model Role Assignment:
- planner: balanced
- generator: staged-pipeline
- verifier: balanced

Why This Is Cost-Effective:
- Cheap extraction lowers total token cost.
- Structured normalization improves synthesis quality.
- Premium reasoning is reserved for the part that truly needs it.

Escalation Rule:
Escalate to consensus-check if the recommendation will drive a major decision or if proposal differences are subtle.

Fallback Rule:
If extraction quality is poor, rerun the extraction stage with a stronger model before recomputing the final recommendation.
