# Graph of Thoughts - Quick Reference

## TL;DR

**Graph of Thoughts (GoT)** = Multi-path reasoning with thought combination and feedback loops.

**When to use**: Complex problems where combining partial solutions could create better outcomes.

---

## Core Algorithm

```
1. GENERATE → Multiple solution paths (5+)
2. EVALUATE → Score each path
3. SYNERGIZE → Find complementary insights
4. COMBINE → Create hybrid solutions
5. ITERATE → Refine with feedback
6. AGGREGATE → Synthesize final answer
7. VERIFY → Check against requirements
```

---

## Key Operations

### Combine Thoughts
```
A (fast) + B (accurate) = Hybrid (fast + accurate)
```

### Identify Synergies
```
Pair Analysis:
- Complementary: Address different aspects
- Enhancing: One improves the other
- Redundant: Similar, no gain from combining
```

### Feedback Loop
```
Solution → Critique → Improvement → Re-evaluate
```

---

## Template

```markdown
## GoT: [Problem]

### Paths (N=5)
| Path | Approach | Score |
|------|----------|-------|
| A | [...] | X.X |
| B | [...] | X.X |
...

### Synergies
| Pair | Type | Score |
|------|------|-------|
| A+C | Complementary | 0.85 |
...

### Combination
A + C → [Hybrid solution]
Score: X.X (+Y.Y improvement)

### Feedback
Iteration 1: Critique → Improvement → Score: X.X
...

### Final
Solution: [Synthesized answer]
Confidence: XX%
```

---

## Scoring

```
Score = Feasibility(0.25) + Quality(0.25) + 
        Novelty(0.15) + Coverage(0.20) + Efficiency(0.15)
```

**Target**: >8.5 with >80% confidence

---

## GoT vs ToT vs CoT

| Aspect | CoT | ToT | GoT |
|--------|-----|-----|-----|
| Paths | 1 | Multiple | Multiple |
| Combination | No | No | **Yes** |
| Feedback | No | No | **Yes** |
| Complexity | Low | Medium | High |
| Best for | Simple | Decisions | Synthesis |

---

## Quick Actions

```
got [problem]        - Full GoT reasoning
got-quick [problem]  - Fast (3 paths, 1 iteration)
combine [thoughts]   - Merge thoughts
synergy [paths]      - Find synergies
feedback [solution]  - Create feedback loop
```

---

## Success Indicators

✅ Multiple synergies found
✅ Combinations improve on individuals
✅ Feedback loop converges
✅ High confidence (>80%)

❌ No synergies → Try more diverse paths
❌ No improvement → Check combination strategy
❌ No convergence → Make critiques more actionable
