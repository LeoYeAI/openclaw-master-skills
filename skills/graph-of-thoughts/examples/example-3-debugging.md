# Graph of Thoughts - Test Cases

## Test Suite

These test cases verify the Graph of Thoughts implementation works correctly.

---

## Test 1: Basic Multi-Path Generation

**Input**: "How should I implement user authentication?"

**Expected Output**:
- At least 5 distinct paths generated
- Each path has different approach (not variations)
- Each path scored on multiple dimensions

**Test Command**:
```
got "How should I implement user authentication?"
```

**Validation**:
```python
assert len(paths) >= 5
assert all(path.approach != other.approach for path, other in combinations(paths, 2))
assert all(has_dimensions(path.evaluation) for path in paths)
```

---

## Test 2: Synergy Detection

**Input**: Two paths with complementary approaches

**Paths**:
- A: "Use JWT for stateless auth"
- B: "Add rate limiting for security"

**Expected Output**:
- Synergy detected between A and B
- Synergy type: Complementary
- Synergy score > 0.7

**Test Command**:
```
synergy [path_A, path_B]
```

**Validation**:
```python
synergy = find_synergy(path_A, path_B)
assert synergy.type == "complementary"
assert synergy.score > 0.7
```

---

## Test 3: Thought Combination

**Input**: Two paths with synergy

**Paths**:
- A: "JWT tokens (fast, stateless)"
- B: "Refresh tokens (secure, revocable)"

**Expected Output**:
- Combined solution that includes both
- Combined score > max(individual scores)
- Clear explanation of combination strategy

**Test Command**:
```
combine [path_A, path_B]
```

**Validation**:
```python
combined = combine_thoughts(path_A, path_B)
assert combined.includes_jwt == True
assert combined.includes_refresh == True
assert combined.score > max(path_A.score, path_B.score)
```

---

## Test 4: Feedback Loop

**Input**: Initial solution with known weakness

**Initial Solution**: "Cache all API responses"

**Critique**: "What about cache invalidation?"

**Expected Output**:
- Improved solution addressing critique
- Score improvement after iteration
- Convergence after 2-4 iterations

**Test Command**:
```
feedback "Cache all API responses"
```

**Validation**:
```python
solution_v1 = Solution("Cache all API responses")
solution_v2 = iterate_with_feedback(solution_v1)
assert "invalidation" in solution_v2.approach.lower()
assert solution_v2.score > solution_v1.score
```

---

## Test 5: Solution Aggregation

**Input**: Multiple partial solutions

**Partial Solutions**:
- A: "Use Redis for caching"
- B: "Add CDN for static assets"
- C: "Optimize database queries"

**Expected Output**:
- Unified solution incorporating all insights
- Clear explanation of synthesis
- Single coherent architecture

**Test Command**:
```
aggregate [solution_A, solution_B, solution_C]
```

**Validation**:
```python
final = aggregate([solution_A, solution_B, solution_C])
assert "redis" in final.approach.lower()
assert "cdn" in final.approach.lower()
assert "database" in final.approach.lower() or "query" in final.approach.lower()
```

---

## Test 6: Full GoT Reasoning

**Input**: Complex multi-dimensional problem

**Problem**: "Design a scalable notification system"

**Expected Output**:
- 5+ paths generated
- 2+ synergies identified
- 1+ combinations created
- 2+ feedback iterations
- Final solution with >80% confidence

**Test Command**:
```
got "Design a scalable notification system"
```

**Validation**:
```python
result = graph_of_thoughts.reason("Design a scalable notification system")

assert len(result.paths) >= 5
assert len(result.synergies) >= 2
assert len(result.combinations) >= 1
assert result.iterations >= 2
assert result.confidence >= 0.80
assert result.final_score >= 8.0
```

---

## Test 7: GoT vs ToT Comparison

**Problem**: "Choose a database for a new project"

**Expected**:
- ToT: Selects best single option
- GoT: May combine aspects or create hybrid

**Test Command**:
```
tot "Choose a database for a new project"
got "Choose a database for a new project"
```

**Analysis**:
```python
tot_result = tree_of_thoughts.reason(problem)
got_result = graph_of_thoughts.reason(problem)

# ToT should pick single best option
assert tot_result.type == "selection"

# GoT may create hybrid
assert got_result.type in ["selection", "hybrid", "synthesis"]

# GoT should have equal or better score
assert got_result.score >= tot_result.score - 0.5
```

---

## Test 8: Convergence Detection

**Input**: Solution that has converged

**Expected Output**:
- System detects diminishing returns
- Stops iterating appropriately
- Reports convergence reason

**Test Command**:
```
got [problem] --verbose
```

**Validation**:
```python
result = graph_of_thoughts.reason(problem)
assert result.converged == True
assert result.convergence_reason in [
    "diminishing_returns",
    "threshold_met",
    "max_iterations"
]
```

---

## Test 9: Uncertainty Propagation

**Input**: Paths with confidence levels

**Expected Output**:
- Combined uncertainty calculated correctly
- Final confidence reflects all uncertainties
- Low-confidence decisions flagged

**Test Command**:
```
got [problem] --with-uncertainty
```

**Validation**:
```python
result = graph_of_thoughts.reason(problem, with_uncertainty=True)

assert result.uncertainty is not None
assert result.confidence_interval is not None
assert result.low_confidence_areas is not None
```

---

## Test 10: Error Recovery

**Input**: Invalid combination attempt

**Expected Output**:
- System detects invalid combination
- Backtracks gracefully
- Continues with valid alternatives

**Test Command**:
```
got [problem] --force-combine [incompatible_paths]
```

**Validation**:
```python
result = graph_of_thoughts.reason(
    problem, 
    force_combine=[path_A, path_B]  # incompatible
)

assert result.recovered == True
assert result.alternative_solution is not None
assert result.errors_encountered > 0
```

---

## Performance Benchmarks

| Test | Expected Time | Memory |
|------|---------------|--------|
| Basic generation | <5s | <100MB |
| Synergy detection | <2s | <50MB |
| Full GoT reasoning | <30s | <200MB |
| Complex problem | <60s | <500MB |

---

## Integration Tests

### Test with Self-Consistency
```python
result = got_with_voting(problem, num_runs=3)
assert result.votes is not None
assert result.consensus_score > 0.7
```

### Test with Error Recovery
```python
result = got_with_recovery(problem_with_error)
assert result.recovery_applied == True
assert result.final_solution is not None
```

### Test with Self-Criticism
```python
result = got_with_criticism(problem)
assert result.critique_applied == True
assert result.improvement_iterations > 0
```

---

## Manual Test Scenarios

### Scenario 1: Architecture Decision
```
Problem: "Design microservices architecture for e-commerce"

Expected behavior:
1. Generate paths for different approaches
2. Find synergies between patterns
3. Combine best practices
4. Iterate on integration details
5. Deliver cohesive architecture
```

### Scenario 2: Algorithm Optimization
```
Problem: "Optimize search for 10M documents"

Expected behavior:
1. Generate different algorithm approaches
2. Identify complementary techniques
3. Combine for hybrid solution
4. Refine through feedback
5. Deliver optimized solution
```

### Scenario 3: Creative Problem
```
Problem: "Design engaging onboarding experience"

Expected behavior:
1. Generate diverse creative approaches
2. Find synergies between ideas
3. Combine into cohesive experience
4. Refine based on critique
5. Deliver innovative solution
```

---

## Test Runner

```bash
# Run all tests
pwsh skills/graph-of-thoughts/run-tests.ps1

# Run specific test
pwsh skills/graph-of-thoughts/run-tests.ps1 -Test test_synergy_detection

# Run with verbose output
pwsh skills/graph-of-thoughts/run-tests.ps1 -Verbose
```

---

## Success Criteria

All tests pass when:
- [ ] Multi-path generation works (5+ paths)
- [ ] Synergy detection accurate (>80%)
- [ ] Combinations improve scores (+0.5 minimum)
- [ ] Feedback loops converge (3 iterations max)
- [ ] Aggregation produces coherent solutions
- [ ] Confidence scoring calibrated (<10% error)
- [ ] Error recovery works gracefully
- [ ] Performance within benchmarks
