# Graph of Thoughts - Examples

This folder contains worked examples demonstrating the Graph of Thoughts reasoning system.

## Examples

### 1. Architecture Decision (`example-1-architecture.md`)
**Problem**: Design an API architecture for high-traffic e-commerce

**Demonstrates**:
- Multi-path generation (5 approaches)
- Synergy detection between paths
- Thought combination (Hybrid REST/gRPC)
- Feedback loop iteration
- Solution aggregation

**Key Insight**: Combining caching strategy (Path A) with protocol split (Path C) created a solution better than either alone.

---

### 2. Algorithm Optimization (`example-2-optimization.md`)
**Problem**: Optimize search for 10M+ documents

**Demonstrates**:
- Diverse algorithmic approaches
- Complementary technique identification
- Hybrid solution creation (Inverted Index + Semantic Search)
- Performance optimization through feedback
- Benchmark validation

**Key Insight**: Combining exact matching (Inverted Index) with fuzzy matching (Vector Embeddings) enabled both precision and flexibility.

---

### 3. Debugging/Testing (`example-3-debugging.md`)
**Problem**: Various test cases for GoT validation

**Demonstrates**:
- Multi-path generation validation
- Synergy detection accuracy
- Thought combination mechanics
- Feedback loop convergence
- Error recovery patterns

**Key Insight**: Tests verify that GoT produces consistent, high-quality results across problem types.

---

## How to Use These Examples

### As Reference
When facing a similar problem, reference these examples for:
- How to structure your problem statement
- How to generate diverse paths
- How to identify synergies
- How to combine thoughts effectively

### As Template
Copy the template structure and adapt for your problem:

```markdown
## GoT: [Your Problem]

### Phase 1: Generate Paths (N=5)
[Generate 5 diverse approaches]

### Phase 2: Evaluate Paths
[Score each path]

### Phase 3: Identify Synergies
[Find complementary pairs]

### Phase 4: Combine Thoughts
[Create hybrid solutions]

### Phase 5: Iterate with Feedback
[Refine through critique]

### Phase 6: Aggregate Final Solution
[Synthesize unified answer]

### Verification
[Check against requirements]
```

### As Learning Material
Study the reasoning patterns:
- What made certain combinations work?
- How did feedback improve solutions?
- What led to high confidence scores?

---

## Creating Your Own Examples

When you successfully use GoT on a new problem:

1. **Document the session** in `memory/got-sessions.md`
2. **Create example file** if it's a good demonstration
3. **Extract patterns** for future reference
4. **Update metrics** to track improvement

### Example Template

```markdown
# Example: [Problem Type]

## Problem
[Clear problem statement]

## Context
[Background, constraints, requirements]

## Phase 1: Generate Paths (N=5)
[5 diverse approaches with initial scores]

## Phase 2: Evaluate Paths
[Detailed evaluation of each path]

## Phase 3: Identify Synergies
[Synergy analysis and top pairs]

## Phase 4: Combine Thoughts
[Combined solutions with improved scores]

## Phase 5: Iterate with Feedback
[Feedback loop iterations and improvements]

## Phase 6: Aggregate Final Solution
[Synthesized solution with reasoning]

## Verification
[Requirements check, confidence scoring]

## Summary
[Metrics, key insights, outcome]
```

---

## Metrics from Examples

| Example | Paths | Synergies | Iterations | Final Score | Confidence |
|---------|-------|-----------|------------|-------------|------------|
| Architecture | 5 | 2 | 3 | 9.1 | 85% |
| Optimization | 5 | 2 | 3 | 9.4 | 90% |

**Average Improvement over Best Individual**: +1.15 points

---

## Related Files

- `../SKILL.md` - Main skill documentation
- `../QUICKREF.md` - Quick reference guide
- `../INTEGRATION.md` - Integration with other skills
- `../TEST-CASES.md` - Validation test cases
