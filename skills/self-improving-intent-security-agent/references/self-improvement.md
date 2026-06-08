# Self-Improvement Reference

How agents learn from experience while maintaining safety guarantees.

## Overview

Self-improvement enables agents to:
- **Learn from outcomes**: Analyze what worked and what didn't
- **Extract patterns**: Identify reusable approaches
- **Optimize strategies**: Evolve better ways to accomplish tasks
- **Avoid failures**: Remember and prevent past mistakes

All within **bounded safety constraints** that prevent harmful learning.

## Learning Cycle

```
Execute Task
    ↓
Collect Metrics (success, time, resources)
    ↓
Analyze Outcome (what contributed to result?)
    ↓
Extract Patterns (reusable approaches)
    ↓
Update Knowledge Store
    ↓
Generate Strategy Candidates
    ↓
A/B Test New Strategies (10% vs 90% baseline)
    ↓
Validate Safety (guardrails check)
    ↓
Adopt if Better (statistical significance)
    ↓
Apply to Next Task
```

## Knowledge Storage

### Directory Structure
```
.agent/learnings/
├── strategies/          # Proven approaches
│   ├── file-processing/
│   ├── api-interaction/
│   └── error-handling/
├── patterns/            # Reusable patterns
│   ├── optimization/
│   ├── error-handling/
│   └── security/
└── antipatterns/        # Failed approaches
    └── avoid/
```

### Strategy Format
```json
{
  "id": "STR-20250115-001",
  "name": "batch-processing-with-checkpoints",
  "domain": "file_processing",
  "version": "1.0.0",
  "approach": {
    "steps": ["batch files", "create checkpoint", "process", "verify"],
    "batchSize": 10,
    "checkpointFrequency": "per_batch"
  },
  "performance": {
    "successRate": 0.95,
    "avgTime": 2.3,
    "sampleSize": 50
  },
  "status": "adopted",
  "adoptedAt": "2025-01-20T10:00:00Z"
}
```

## Pattern Extraction

### Criteria for Patterns
- Appears in 3+ successful tasks
- Improves success rate by 10%+ OR reduces time by 20%+
- Passes safety validation
- Generalizable (not task-specific)

### Pattern Types

**1. Execution Patterns**
```
Pattern: "checkpoint-before-bulk-operation"
Trigger: Processing > 10 items
Action: Create checkpoint before starting
Benefit: Easy rollback on failures
Evidence: 95% success (vs 78% without)
```

**2. Error Handling Patterns**
```
Pattern: "exponential-backoff-retry"
Trigger: Network errors
Action: Retry with 2^n second delays
Benefit: Better success with rate-limited APIs
Evidence: 90% eventual success (vs 60% immediate retry)
```

**3. Optimization Patterns**
```
Pattern: "cache-api-responses"
Trigger: Repeated API calls
Action: Cache for 5 minutes
Benefit: 70% faster, fewer API costs
Evidence: Avg time 0.5s (vs 1.7s uncached)
```

## Strategy Evolution

### A/B Testing Framework

**Setup**:
```typescript
const abTest = {
  baseline: currentStrategy,    // 90% of tasks
  candidate: newStrategy,        // 10% of tasks
  metrics: ["successRate", "executionTime", "resourceUsage"],
  minimumSampleSize: 20,
  significanceLevel: 0.05
};
```

**Evaluation**:
```typescript
function evaluateStrategy(results: ABTestResults): Decision {
  const improvement = (results.candidate.successRate - results.baseline.successRate)
                    / results.baseline.successRate;

  const pValue = tTest(results.candidate.samples, results.baseline.samples);

  if (improvement > 0.10 && pValue < 0.05 && passesSafetyChecks(results.candidate)) {
    return { decision: "adopt", reason: "Significant improvement" };
  } else if (improvement < -0.05) {
    return { decision: "reject", reason: "Performance degradation" };
  } else {
    return { decision: "extend_testing", reason: "Inconclusive" };
  }
}
```

### Gradual Rollout

**Phases**:
1. **Initial Test**: 10% of tasks (20-50 tasks)
2. **Extended Test**: 25% of tasks (if promising)
3. **Expanded Test**: 50% of tasks (if validated)
4. **Full Adoption**: 100% of tasks (if proven)

**Rollback Triggers**:
- Success rate drops > 5%
- Execution time increases > 30%
- Safety violations detected
- Resource usage exceeds limits

## Safety Guardrails

### Modification Constraints

**What can be learned**:
- Execution strategies (how to accomplish tasks)
- Error handling approaches (how to recover)
- Optimization techniques (how to be faster)
- Pattern recognition (what works when)

**What cannot be learned**:
- Bypassing intent validation (security logic immutable)
- Expanding permissions (cannot self-elevate)
- Violating constraints (boundaries are fixed)
- Ignoring anomalies (monitoring is mandatory)

### Complexity Limits

```typescript
interface ComplexityLimits {
  maxCyclomaticComplexity: 100;
  maxNestingDepth: 5;
  maxFunctionLength: 200;
  maxBranchingFactor: 10;
}

function validateStrategyComplexity(strategy: Strategy): boolean {
  const complexity = calculateComplexity(strategy);

  return complexity.cyclomatic <= ComplexityLimits.maxCyclomaticComplexity
      && complexity.nesting <= ComplexityLimits.maxNestingDepth
      && complexity.length <= ComplexityLimits.maxFunctionLength;
}
```

### Performance Constraints

```typescript
interface PerformanceConstraints {
  minSuccessRate: 0.70;          // Must maintain 70% success
  maxTimeIncrease: 2.0;          // Cannot be 2x slower
  maxResourceMultiplier: 2.0;    // Cannot use 2x resources
}

function validatePerformance(
  candidate: Strategy,
  baseline: Strategy
): boolean {
  return candidate.successRate >= PerformanceConstraints.minSuccessRate
      && candidate.avgTime <= baseline.avgTime * PerformanceConstraints.maxTimeIncrease
      && candidate.resourceUsage <= baseline.resourceUsage * PerformanceConstraints.maxResourceMultiplier;
}
```

### Human Approval Gates

**Require approval when**:
- Strategy complexity > 80/100
- Performance improvement > 50% (too good to be true?)
- Changes affect security-sensitive domains
- Modifies error handling logic

```typescript
async function requiresApproval(strategy: Strategy): Promise<boolean> {
  if (strategy.complexity > 80) return true;
  if (strategy.performance.improvement > 0.50) return true;
  if (strategy.domain in SECURITY_SENSITIVE_DOMAINS) return true;
  if (modifiesErrorHandling(strategy)) return true;

  return false;
}
```

## Learning from Failures

### Antipattern Registry

Track approaches that failed:

```json
{
  "id": "anti-008",
  "name": "recursive-without-depth-limit",
  "domain": "file_processing",
  "symptom": "excessive memory usage, timeouts",
  "occurrence": 3,
  "lastSeen": "2025-01-15",
  "prevention": {
    "rule": "always set max depth for recursive operations",
    "safeguard": "memory limit check before recursion"
  }
}
```

### Failure Analysis

```typescript
async function analyzeFailure(task: Task): Promise<FailureAnalysis> {
  return {
    rootCause: identifyRootCause(task.errors),
    contributingFactors: extractFactors(task.context),
    preventable: couldHaveBeenPrevented(task),
    learnings: [
      {
        type: "antipattern",
        description: "Avoid recursive operations without limits",
        prevention: "Add depth check and memory monitoring"
      }
    ]
  };
}
```

## Incremental Learning

### Running Averages

Use exponential moving average for metrics:

```typescript
function updateMetric(
  current: number,
  newObservation: number,
  alpha: number = 0.2
): number {
  // Alpha = 0.2 gives more weight to recent observations
  return alpha * newObservation + (1 - alpha) * current;
}

// Example:
currentSuccessRate = 0.85;
newTaskSuccessRate = 0.92;
updatedSuccessRate = updateMetric(currentSuccessRate, newTaskSuccessRate);
// Result: 0.864 (gradual update, not jumping to 0.92)
```

### Minimum Sample Size

Require sufficient observations before adopting:

```typescript
const MIN_SAMPLE_SIZE = 10;

function hasEnoughData(strategy: Strategy): boolean {
  return strategy.observationCount >= MIN_SAMPLE_SIZE;
}
```

### Confidence Levels

Track confidence based on sample size:

```typescript
function calculateConfidence(sampleSize: number): "low" | "medium" | "high" {
  if (sampleSize < 10) return "low";
  if (sampleSize < 50) return "medium";
  return "high";
}
```

## Multi-Domain Learning

### Transfer Learning

Apply patterns from one domain to related domains:

```typescript
// Pattern learned in file_processing
const filePattern = {
  name: "batch-with-checkpoints",
  domain: "file_processing",
  approach: "Process in batches, checkpoint between"
};

// Can transfer to api_interaction
const apiPattern = {
  ...filePattern,
  domain: "api_interaction",
  approach: "Fetch in batches, checkpoint between",
  transferredFrom: "file_processing"
};
```

### Domain Similarity

```typescript
const DOMAIN_SIMILARITY = {
  "file_processing": ["data_transformation", "batch_operations"],
  "api_interaction": ["network_operations", "rate_limited_operations"],
  "error_handling": ["all"]  // Error handling applies everywhere
};

function getApplicableDomains(pattern: Pattern): string[] {
  return [
    pattern.domain,
    ...DOMAIN_SIMILARITY[pattern.domain] || []
  ];
}
```

## Knowledge Export/Import

### Export Format

```json
{
  "exportedAt": "2025-01-15T10:00:00Z",
  "version": "1.0.0",
  "strategies": [...],
  "patterns": [...],
  "antipatterns": [...],
  "metadata": {
    "totalTasks": 500,
    "avgSuccessRate": 0.89,
    "domains": ["file_processing", "api_interaction"]
  }
}
```

### Importing Knowledge

```typescript
async function importKnowledge(
  data: KnowledgeExport,
  options: ImportOptions
): Promise<ImportResult> {

  const validated = [];
  const rejected = [];

  for (const strategy of data.strategies) {
    // Validate against safety guardrails
    if (passesSafetyChecks(strategy)) {
      if (options.requireReview) {
        // Flag for human review
        await flagForReview(strategy);
      }
      validated.push(strategy);
    } else {
      rejected.push({
        strategy: strategy,
        reason: "Failed safety validation"
      });
    }
  }

  // Merge with existing knowledge
  if (options.merge) {
    await mergeKnowledge(validated);
  } else {
    await replaceKnowledge(validated);
  }

  return {
    imported: validated.length,
    rejected: rejected.length,
    details: rejected
  };
}
```

## Monitoring Learning Effectiveness

### Metrics to Track

```typescript
interface LearningMetrics {
  // Overall
  totalLearnings: number;
  adoptedStrategies: number;
  rejectedStrategies: number;

  // Performance
  baselineSuccessRate: number;
  currentSuccessRate: number;
  improvement: number;  // Percentage improvement

  // Efficiency
  avgExecutionTime: {
    baseline: number;
    current: number;
    improvement: number;
  };

  // Safety
  violationRate: number;
  anomalyRate: number;
  rollbackRate: number;
}
```

### Progress Over Time

```typescript
function trackLearningProgress(): ProgressReport {
  const weeks = last12Weeks();

  return {
    successRateTrend: weeks.map(w => w.successRate),
    executionTimeTrend: weeks.map(w => w.avgTime),
    strategiesAdopted: weeks.map(w => w.newStrategies),
    improvement: {
      week1: weeks[0].successRate,
      week12: weeks[11].successRate,
      delta: weeks[11].successRate - weeks[0].successRate
    }
  };
}
```

## Best Practices

### 1. Let It Learn
- Requires sample size (10+ observations)
- Don't judge too early
- Give time to converge

### 2. Monitor Closely
- Track success rates
- Watch for regressions
- Review A/B test results

### 3. Safety First
- Never bypass guardrails
- Reject strategies that reduce safety
- Require approval for high-complexity changes

### 4. Promote Proven Patterns
- Move recurring patterns to permanent memory
- Share across team via knowledge export
- Document in CLAUDE.md or AGENTS.md

### 5. Clean Up Periodically
- Archive old strategies
- Remove obsolete patterns
- Consolidate similar learnings

## Common Pitfalls

### Overfitting
**Problem**: Strategy works great on test tasks but fails on new scenarios

**Solution**: Test across diverse task types, require minimum sample size

### Premature Optimization
**Problem**: Adopting strategy after 2-3 successes

**Solution**: Enforce minimum sample size (10+), require statistical significance

### Ignoring Safety
**Problem**: Adopting faster strategy that violates constraints

**Solution**: Always run safety validation, reject if fails

### Learning Harmful Patterns
**Problem**: Learning to bypass security checks

**Solution**: Core security logic is immutable, cannot be modified through learning

---

Self-improvement makes agents adaptable and efficient, but safety guardrails ensure they never learn to be unsafe.
