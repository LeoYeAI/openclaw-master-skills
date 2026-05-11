# Graph of Thoughts - Integration Guide

## Integration with Enhanced Reasoning Framework

The Graph of Thoughts skill integrates with the existing reasoning ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    META-REASONING LAYER                         │
│         (Decides which reasoning strategy to use)               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Tree of      │   │  GRAPH OF     │   │  Chain of     │
│  Thoughts     │   │  THOUGHTS     │   │  Thought      │
│               │   │               │   │               │
│  Discrete     │   │  Combining    │   │  Simple       │
│  options      │   │  insights     │   │  linear       │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        │   ┌───────────────┘
        │   │
        ▼   ▼
┌───────────────────────────────────────────────────────────────┐
│                    SHARED COMPONENTS                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Self-     │  │   Error     │  │   Self-     │           │
│  │  Consistency│  │  Recovery   │  │  Criticism  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Uncertainty │  │   Memory    │  │   Analogical│           │
│  │   Quant.    │  │  Integration│  │  Reasoning  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────────────────────────────────────────┘
```

## When to Use Each Reasoning Mode

### Use Graph of Thoughts when:
- Problem has multiple dimensions to optimize
- Partial solutions exist in different branches
- Combination could create better solution
- Feedback loops would improve quality
- Synthesis of ideas needed
- Quality > Speed

### Use Tree of Thoughts when:
- Simple decision with discrete options
- Paths are truly independent
- Tree structure sufficient
- Faster decision needed
- Clear evaluation criteria

### Use Chain of Thought when:
- Straightforward problem
- Single clear solution path
- Speed is priority
- Simple reasoning sufficient

## Integration Points

### 1. GoT + Tree of Thoughts

```python
def hybrid_reasoning(problem):
    """Start with ToT, upgrade to GoT if synergies detected."""
    
    # Phase 1: ToT exploration
    tot = TreeOfThoughts()
    paths = tot.generate_paths(problem, num_paths=5)
    
    # Phase 2: Check for synergies
    synergies = identify_synergies(paths)
    
    if synergies and max(s.score for s in synergies) > 0.7:
        # High synergy potential - upgrade to GoT
        got = GraphOfThoughts()
        got.load_paths(paths)  # Reuse ToT paths
        return got.combine_and_solve()
    else:
        # No significant synergies - continue with ToT
        return tot.select_best_path()
```

### 2. GoT + Self-Consistency

```python
def got_with_voting(problem, num_runs=3):
    """Run GoT multiple times and vote on solutions."""
    
    solutions = []
    for _ in range(num_runs):
        got = GraphOfThoughts()
        result = got.reason(problem)
        solutions.append(result)
    
    # Extract key decisions from each solution
    decisions = [extract_decisions(s) for s in solutions]
    
    # Vote on each decision point
    final_decisions = vote_on_decisions(decisions)
    
    # Reconstruct solution with voted decisions
    return synthesize_solution(final_decisions)
```

### 3. GoT + Error Recovery

```python
def got_with_recovery(problem):
    """GoT with built-in error recovery."""
    
    got = GraphOfThoughts()
    
    try:
        result = got.reason(problem)
        
        # Verify result
        if not verify_solution(result):
            # Add verification failure as critique
            got.add_critique(
                node=result.node,
                critique="Verification failed: [reason]"
            )
            # Re-iterate with feedback
            return got.iterate_with_feedback()
        
        return result
        
    except Exception as e:
        # Error becomes new node in graph
        got.add_error_node(error=e)
        # Generate recovery paths
        recovery_paths = generate_recovery_paths(e)
        got.add_paths(recovery_paths)
        # Continue reasoning
        return got.continue_reasoning()
```

### 4. GoT + Self-Criticism

```python
def got_with_criticism(problem):
    """Apply self-criticism as feedback loop."""
    
    got = GraphOfThoughts()
    solution = got.reason(problem)
    
    # Apply 7-step self-criticism
    criticism = SelfCriticism()
    critique = criticism.critique(solution)
    
    # Add critique as node in graph
    got.add_critique_node(
        target=solution.node,
        critique=critique
    )
    
    # Generate improvements
    improvements = criticism.generate_improvements(critique)
    got.add_improvement_nodes(improvements)
    
    # Re-aggregate with improvements
    return got.reaggregate()
```

### 5. GoT + Uncertainty Quantification

```python
def got_with_uncertainty(problem):
    """GoT with confidence scoring."""
    
    got = GraphOfThoughts()
    
    # Generate paths with uncertainty
    paths = got.generate_paths(problem)
    for path in paths:
        path.confidence = calculate_confidence(path)
        path.uncertainty = identify_unknowns(path)
    
    # Evaluate with uncertainty bounds
    evaluations = []
    for path in paths:
        eval_score = evaluate(path)
        eval_score.confidence_interval = (
            eval_score.point - eval_score.uncertainty,
            eval_score.point + eval_score.uncertainty
        )
        evaluations.append(eval_score)
    
    # Combine with uncertainty propagation
    combined = got.combine_thoughts(paths, evaluations)
    combined.uncertainty = propagate_uncertainty(combined)
    
    # Final solution with confidence
    solution = got.aggregate_solution(combined)
    solution.confidence = calculate_final_confidence(solution)
    
    return solution
```

## Meta-Reasoning Decision Tree

```python
def select_reasoning_strategy(problem):
    """Meta-reasoning: choose optimal strategy."""
    
    # Assess problem characteristics
    assessment = assess_problem(problem)
    
    # Decision tree
    if assessment.complexity == 'simple':
        return 'chain_of_thought'
    
    elif assessment.type == 'decision' and assessment.options < 5:
        return 'tree_of_thoughts'
    
    elif assessment.dimensions > 2:
        # Multi-dimensional optimization
        return 'graph_of_thoughts'
    
    elif assessment.synergy_potential == 'high':
        # Likely combinable solutions
        return 'graph_of_thoughts'
    
    elif assessment.stakes == 'critical':
        # High stakes - use GoT with self-consistency
        return 'graph_of_thoughts_with_voting'
    
    elif assessment.time_budget < 60:  # seconds
        return 'tree_of_thoughts'
    
    else:
        return 'graph_of_thoughts'
```

## Memory Integration

### Recording GoT Sessions

```markdown
## memory/got-sessions.md

### [Date] GoT: Architecture Decision

**Problem**: Design API architecture
**Paths Generated**: 5
**Synergies Found**: 2 (A+C: 0.88, B+D: 0.72)
**Iterations**: 3
**Final Score**: 9.1/10
**Confidence**: 85%

**Key Insights**:
- Caching + Protocol split = strong synergy
- Event-driven invalidation critical
- gRPC complexity manageable

**Solution**: Hybrid REST/gRPC with caching

**Outcome**: [To be filled after implementation]
```

### Learning from GoT Sessions

```python
def learn_from_got_session(session):
    """Extract learnings for future sessions."""
    
    learnings = {
        'synergy_patterns': extract_synergy_patterns(session),
        'combination_strategies': extract_combination_strategies(session),
        'feedback_effectiveness': analyze_feedback_loops(session),
        'convergence_patterns': analyze_convergence(session)
    }
    
    # Store for future reference
    memory.store(f"got-learnings/{session.id}", learnings)
    
    # Update heuristics
    update_synergy_heuristics(learnings['synergy_patterns'])
    update_combination_heuristics(learnings['combination_strategies'])
```

## Quick Actions Integration

Add to AGENTS.md or command system:

```markdown
## Reasoning Commands

- `/reason` - Auto-select reasoning strategy
- `/tot [problem]` - Force Tree of Thoughts
- `/got [problem]` - Force Graph of Thoughts
- `/got-quick [problem]` - Fast GoT (3 paths, 1 iteration)
- `/combine [thoughts]` - Combine multiple thoughts
- `/synergy [paths]` - Find synergies
- `/feedback [solution]` - Create feedback loop
```

## Metrics Integration

Track GoT performance:

```json
{
  "reasoning_metrics": {
    "graph_of_thoughts": {
      "sessions_total": 15,
      "avg_paths_generated": 5.2,
      "avg_synergies_found": 2.3,
      "avg_iterations": 2.8,
      "avg_final_score": 8.7,
      "avg_confidence": 0.84,
      "avg_improvement_over_best_individual": 1.3,
      "success_rate": 0.93
    },
    "tree_of_thoughts": {
      "sessions_total": 42,
      "avg_paths_generated": 4.8,
      "avg_final_score": 7.9,
      "success_rate": 0.88
    }
  }
}
```
