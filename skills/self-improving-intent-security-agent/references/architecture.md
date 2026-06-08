# Architecture Reference

Detailed system architecture for the self-improving intent security agent.

## Overview

The agent combines three integrated systems working in concert to provide safe, adaptive autonomous execution:

1. **Intent Security System** - Validates actions before execution
2. **Self-Improvement System** - Learns from experience
3. **Safety & Audit System** - Ensures transparency and safety

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  USER INTENT SPECIFICATION                       │
│                                                                   │
│  Goal: "What I want to achieve"                                  │
│  Constraints: ["What I don't want", "Boundaries"]                │
│  Expected Behavior: ["How it should act", "Patterns"]            │
│  Risk Level: low | medium | high                                 │
│                                                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTENT SECURITY SYSTEM                         │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │    Intent    │ -> │   Intent     │ -> │ Authorization   │   │
│  │   Capture    │    │  Validator   │    │    Engine       │   │
│  └──────────────┘    └──────────────┘    └─────────────────┘   │
│                             │                      │             │
│                        [VALIDATED]           [AUTHORIZED]        │
│                             │                      │             │
│                             └──────────┬───────────┘             │
└────────────────────────────────────────┼─────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       EXECUTION LAYER                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Task Executor                           │    │
│  │   ┌──────────────────────┬──────────────────────┐       │    │
│  │   │                      │                      │       │    │
│  │   ▼                      ▼                      ▼       │    │
│  │ Safety              Execution              Metrics      │    │
│  │ Guardrails          Monitor                Collector    │    │
│  └───┬─────────────────────┬──────────────────────┬────────┘    │
│      │                     │                      │              │
│      │              ┌──────┴──────┐               │              │
│      │              ▼             ▼               │              │
│      │       Anomaly         Checkpoint           │              │
│      │       Detector        Manager              │              │
│      │              │             │               │              │
│      │       [ANOMALY?]    [CHECKPOINTS]          │              │
│      │              │             │               │              │
│      │              └──────┬──────┘               │              │
│      │                     ▼                      │              │
│      │             Rollback Manager               │              │
│      │                     │                      │              │
└──────┼─────────────────────┼──────────────────────┼──────────────┘
       │                     │                      │
       │                     ▼                      │
       │              Audit Logger <────────────────┘
       │                     │
       │                     │
       ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SELF-IMPROVEMENT SYSTEM                         │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   Outcome    │ -> │   Pattern    │ -> │   Strategy      │   │
│  │   Analyzer   │    │  Extractor   │    │   Optimizer     │   │
│  └──────────────┘    └──────────────┘    └─────────────────┘   │
│                             │                      │             │
│                             ▼                      ▼             │
│                    ┌──────────────────────────────┐             │
│                    │    Knowledge Store           │             │
│                    │  - Strategies                │             │
│                    │  - Patterns                  │             │
│                    │  - Antipatterns              │             │
│                    └───────────┬──────────────────┘             │
│                                │                                 │
│                                ▼                                 │
│                        Feedback Loop                             │
│                                │                                 │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                                 └──> [Applied to Next Execution]
```

## Component Descriptions

### Intent Security System

#### Intent Capture
**Purpose**: Structures user requests into formal intent specifications.

**Inputs**:
- User's natural language goal
- Implicit and explicit constraints
- Context (files, environment, history)

**Outputs**:
- Structured Intent object with:
  - Goal (clear, measurable objective)
  - Constraints (boundaries and restrictions)
  - Expected Behavior (behavioral patterns)
  - Risk Level (low/medium/high)
  - Context metadata

**Process**:
1. Parse user request into components
2. Extract constraints from context (project rules, previous violations)
3. Infer expected behavioral patterns
4. Assess risk based on action types and scope
5. Create formal intent specification

#### Intent Validator
**Purpose**: Validates each action against the intent before execution.

**Validation Checks**:
1. **Goal Alignment**: Does action serve the stated goal?
2. **Constraint Compliance**: Respects all boundaries?
3. **Behavioral Match**: Fits expected patterns?
4. **Side Effect Assessment**: Acceptable consequences?

**Decision Logic**:
```
if !goalAlignment:
    BLOCK → Log Violation (Goal Drift)
else if !constraintCompliance:
    BLOCK → Log Violation (Constraint Breach)
else if !behavioralMatch:
    WARN → Log Anomaly (Pattern Deviation)
else if sideEffectsUnacceptable:
    BLOCK → Log Violation (Unsafe Side Effects)
else:
    PROCEED → Log Authorization
```

#### Authorization Engine
**Purpose**: Enforces permission boundaries and intent-specific authorization.

**Authorization Layers**:
1. **Permission Check**: Does agent have permission for this action type?
2. **Scope Validation**: Is action within authorized scope?
3. **Intent Authorization**: Does action serve the current intent?
4. **Risk Gates**: High-risk actions require approval?

**Permission Model**:
```typescript
{
  resource: "filesystem" | "network" | "process" | "api",
  actions: ["read", "write", "execute", "delete"],
  scope: "/allowed/paths" | "allowed.domains" | ["specific", "resources"],
  conditions: {
    riskLevel: "low" | "medium" | "high",
    requiresApproval: boolean,
    timeWindow: "business_hours" | "any"
  }
}
```

### Execution Layer

#### Task Executor
**Purpose**: Orchestrates validated action execution with monitoring.

**Execution Flow**:
1. Receive validated action from Intent Validator
2. Check Safety Guardrails
3. Create checkpoint (if risky)
4. Execute action
5. Monitor execution via Execution Monitor
6. Collect metrics via Metrics Collector
7. Log outcome via Audit Logger

#### Safety Guardrails
**Purpose**: Prevents dangerous operations even if validated.

**Guardrail Types**:
- **Complexity Limits**: Maximum complexity thresholds
- **Resource Limits**: CPU, memory, time, disk
- **Modification Limits**: Cannot modify core security logic
- **Permission Limits**: Cannot expand own permissions
- **Performance Limits**: Cannot degrade below thresholds

#### Execution Monitor
**Purpose**: Real-time monitoring of action execution.

**Monitoring Aspects**:
- Resource usage (CPU, memory, I/O)
- Time elapsed vs. expected
- Output patterns vs. expected
- Side effects detection
- Error rate tracking

#### Anomaly Detector
**Purpose**: Identifies behavioral deviations during execution.

**Anomaly Types**:

1. **Goal Drift**
   - Detection: Actions increasingly irrelevant to goal
   - Metric: Goal relevance score < threshold
   - Response: Halt, request clarification

2. **Capability Misuse**
   - Detection: Tools used inappropriately
   - Metric: Unexpected capability usage
   - Response: Rollback to checkpoint

3. **Side Effects**
   - Detection: Unintended consequences
   - Metric: State changes beyond expected
   - Response: Log warning, monitor closely

4. **Resource Anomalies**
   - Detection: Resource usage spikes
   - Metric: CPU/memory/time > baseline + threshold
   - Response: Throttle or halt

5. **Pattern Deviation**
   - Detection: Behavior differs from expected
   - Metric: Behavioral distance > threshold
   - Response: Log for analysis

**Detection Algorithm**:
```
baseline = historicalAverage(metric, domain)
threshold = anomalyThreshold * standardDeviation(metric)
current = currentValue(metric)

if abs(current - baseline) > threshold:
    triggerAnomaly(metric, severity)
```

#### Checkpoint Manager
**Purpose**: Creates and manages execution checkpoints for rollback.

**Checkpoint Contents**:
- File system state (modified files)
- Database state (affected records)
- API state (external system changes)
- Variable state (important values)
- Execution context (where we are)

**Checkpoint Strategy**:
- Create before high-risk operations
- Create at natural breakpoints (loops, batches)
- Limit checkpoint count (disk space)
- Expire old checkpoints (retention policy)

#### Rollback Manager
**Purpose**: Restores state to previous checkpoint on violations.

**Reversal Strategies**:
- **File Operations**: Restore from backup
- **API Calls**: Compensating transactions
- **Database**: Transaction rollback or snapshot restore
- **Process**: Terminate and restart
- **State**: Restore saved values

**Rollback Process**:
1. Identify checkpoint to restore
2. Reverse actions in reverse order
3. Verify state restoration
4. Log rollback operation
5. Notify user of rollback
6. Clear forward state

### Self-Improvement System

#### Outcome Analyzer
**Purpose**: Analyzes task outcomes to extract insights.

**Analysis Phases**:

1. **Success/Failure Classification**
   - Determine if goal was achieved
   - Identify what contributed to outcome
   - Measure against baseline performance

2. **Factor Extraction**
   - Success factors (what helped)
   - Failure causes (what hindered)
   - Performance metrics (time, resources, quality)

3. **Pattern Recognition**
   - Identify reusable approaches
   - Detect recurring issues
   - Note context-specific behavior

4. **Comparison**
   - Compare to similar past tasks
   - Identify improvements or regressions
   - Calculate effectiveness delta

#### Pattern Extractor
**Purpose**: Identifies reusable patterns from successful executions.

**Pattern Types**:
- **Execution Patterns**: Successful action sequences
- **Error Handling**: Effective recovery strategies
- **Optimization**: Performance improvements
- **Security**: Safe validation approaches

**Extraction Criteria**:
- Appears in multiple successful tasks (N >= 3)
- Improves success rate or performance
- Passes safety validation
- Generalizable (not task-specific)

**Pattern Structure**:
```typescript
{
  id: "pat-001",
  name: "batch-processing-with-checkpoints",
  domain: "file_processing",
  trigger: "bulk file operations",
  approach: {
    steps: [...],
    checkpoints: ["every 10 items"],
    errorHandling: "rollback batch"
  },
  effectiveness: 0.92,
  observations: 47,
  contexts: ["file_count > 10", "modifications required"]
}
```

#### Strategy Optimizer
**Purpose**: Evolves strategies through A/B testing and validation.

**Optimization Process**:

1. **Baseline Establishment**
   - Current strategy is control
   - Measure: success rate, time, resources
   - Sample size: minimum N tasks

2. **Candidate Generation**
   - Create alternative approach
   - Based on patterns or learnings
   - Hypothesis: why it should improve

3. **A/B Testing**
   - Split: 90% baseline, 10% candidate
   - Run both in parallel
   - Measure same metrics

4. **Statistical Comparison**
   - Test significance (p-value)
   - Minimum improvement threshold (10%)
   - Safety validation (no regression on critical metrics)

5. **Adoption Decision**
   ```
   if candidateSuccessRate > baseline + 10%
      and candidateRisk <= baselineRisk
      and safetyChecksPassed:
       adoptStrategy(candidate)
   else if candidateSuccessRate < baseline:
       rejectStrategy(candidate)
   else:
       extendTesting(candidate)
   ```

6. **Gradual Rollout**
   - Phase 1: 10% → 25%
   - Phase 2: 25% → 50%
   - Phase 3: 50% → 100%
   - Monitor each phase, rollback if degrades

#### Knowledge Store
**Purpose**: Persists learned strategies, patterns, and antipatterns.

**Storage Structure**:
```
.agent/learnings/
├── strategies/
│   ├── file-processing/
│   │   ├── STR-20250115-001.json
│   │   └── STR-20250120-003.json
│   └── api-interaction/
│       └── STR-20250118-002.json
├── patterns/
│   ├── error-handling/
│   │   └── retry-with-backoff.json
│   └── optimization/
│       └── batch-processing.json
└── antipatterns/
    └── file-operations/
        └── recursive-without-limit.json
```

**Querying**:
- By domain (file_processing, api_interaction)
- By effectiveness (>= threshold)
- By recency (last N days)
- By usage (most frequently used)

**Versioning**:
- Each strategy update creates new version
- Old versions retained for rollback
- Version comparison shows evolution

#### Feedback Loop
**Purpose**: Coordinates continuous improvement cycle.

**Loop Cycle**:
1. Task executes → metrics collected
2. Outcome analyzed → insights extracted
3. Patterns identified → knowledge updated
4. Strategies optimized → A/B tests launched
5. Results validated → adoption decisions made
6. Next task uses updated knowledge

**Cadence**:
- Real-time: Metrics collection, validation
- Per-task: Outcome analysis, pattern extraction
- Periodic: Strategy optimization (every N tasks)
- On-demand: Manual review and promotion

## Data Flow

### Intent Specification Flow
```
User Request
    → Intent Capture (parse, structure)
    → Intent Validator (validate feasibility)
    → Stored in .agent/intents/
    → Used by all subsequent actions
```

### Action Execution Flow
```
Proposed Action
    → Intent Validator (check against intent)
    → Authorization Engine (check permissions)
    → Safety Guardrails (check limits)
    → Checkpoint Manager (create checkpoint if risky)
    → Task Executor (execute action)
    → Execution Monitor (watch execution)
    → Metrics Collector (gather data)
    → Anomaly Detector (check for deviations)
    → [if anomaly] Rollback Manager (restore checkpoint)
    → Audit Logger (record everything)
```

### Learning Flow
```
Task Completion
    → Outcome Analyzer (what happened?)
    → Pattern Extractor (reusable approach?)
    → Knowledge Store (save insights)
    → Strategy Optimizer (better way?)
    → A/B Testing (validate improvement)
    → [if proven] Adopt new strategy
    → [if recurring] Promote to permanent memory
```

## Core Data Structures

### Intent
```typescript
interface Intent {
  id: string;                    // INT-YYYYMMDD-XXX
  goal: string;                  // What to achieve
  constraints: Constraint[];     // Boundaries
  expectedBehavior: Pattern[];   // Expected actions
  riskLevel: "low" | "medium" | "high";
  context: {
    files: string[];
    environment: string;
    previousAttempts: string[];
  };
  status: "active" | "completed" | "violated";
  created: timestamp;
}
```

### Action
```typescript
interface Action {
  id: string;
  type: "file_read" | "file_write" | "file_delete" |
        "api_call" | "command_execution" | "other";
  description: string;
  parameters: Record<string, any>;
  estimatedRisk: "low" | "medium" | "high";
  requiresCheckpoint: boolean;
}
```

### ValidationResult
```typescript
interface ValidationResult {
  valid: boolean;
  checks: {
    goalAlignment: boolean;
    constraintCompliance: boolean;
    behavioralMatch: boolean;
    authorized: boolean;
  };
  reason?: string;
  suggestions?: string[];
}
```

### Learning
```typescript
interface Learning {
  id: string;                    // LRN-YYYYMMDD-XXX
  intent: string;                // Related intent
  outcome: "success" | "failure" | "partial";
  pattern: Pattern;
  evidence: {
    successRate: number;
    executionTime: number;
    actionCount: number;
  };
  confidence: "low" | "medium" | "high";
  sampleSize: number;
  status: "pending" | "validated" | "promoted";
}
```

### Strategy
```typescript
interface Strategy {
  id: string;                    // STR-YYYYMMDD-XXX
  name: string;
  domain: string;
  version: string;
  approach: {
    steps: Step[];
    checkpoints: string[];
    errorHandling: string;
  };
  performance: {
    successRate: number;
    avgTime: number;
    resourceUsage: ResourceMetrics;
  };
  status: "testing" | "adopted" | "rejected" | "superseded";
  abTest?: ABTestResults;
}
```

## Design Decisions

### 1. Three-Layer Security
**Decision**: Validate at three points (pre, during, post execution)

**Rationale**:
- Pre-execution catches obvious violations
- During execution detects runtime anomalies
- Post-execution learns from outcomes

**Trade-off**: Higher overhead, but defense in depth

### 2. Checkpoint-Based Rollback
**Decision**: Use action reversal rather than full state snapshots

**Rationale**:
- More efficient (only store changes)
- Fine-grained (can rollback specific actions)
- Practical (full state restoration often impossible)

**Trade-off**: Requires action-specific reversal logic

### 3. A/B Testing for Learning
**Decision**: Gradual strategy rollout with statistical validation

**Rationale**:
- Proves improvement before full adoption
- Catches regressions early
- Maintains baseline as fallback

**Trade-off**: Slower learning, but safer

### 4. Structured Logging Format
**Decision**: Markdown files with consistent structure and IDs

**Rationale**:
- Human-readable for transparency
- Grep-able for analysis
- Version control friendly
- Cross-platform compatible

**Trade-off**: Less efficient than database, but more accessible

### 5. Intent-First Design
**Decision**: Require intent specification before execution

**Rationale**:
- Forces clarity of purpose
- Enables meaningful validation
- Provides context for learning
- Creates audit trail

**Trade-off**: Additional upfront work, but catches issues early

## Performance Considerations

### Validation Overhead
- Intent validation: ~1-5ms per action
- Authorization check: ~0.5-2ms per action
- Anomaly detection: ~5-10ms per monitoring interval
- Total overhead: ~10-20ms per action

**Mitigation**:
- Cache validation results for repeated actions
- Batch validation checks
- Async anomaly detection
- Configurable monitoring intervals

### Storage Growth
- Audit logs: ~1KB per action
- Checkpoints: Varies (1MB-1GB depending on state)
- Learning data: ~10KB per learning
- Strategies: ~5KB per strategy

**Mitigation**:
- Retention policies (default 90 days)
- Compression of old logs
- Checkpoint expiration
- Archival to cold storage

### Learning Convergence
- Minimum sample size: 10 observations
- A/B test duration: 50-100 tasks
- Strategy adoption: 3-4 weeks typical

**Factors**:
- Task frequency (more tasks = faster learning)
- Domain complexity (simpler = faster convergence)
- Performance variance (stable = faster validation)

## Scalability

### Horizontal Scaling
- Multiple agent instances share knowledge store
- Distributed A/B testing across instances
- Aggregated metrics for strategy evaluation
- Centralized audit logging

### Vertical Limits
- Single agent: 100-1000 actions/day
- Knowledge base: 10K patterns, 1K strategies
- Audit logs: 90 days retention (~100MB)
- Checkpoints: 10 concurrent (10GB typical)

## Security Properties

### Threat Model

**Threats Defended**:
- Goal drift (agent pursues wrong objective)
- Scope creep (agent exceeds boundaries)
- Privilege escalation (agent expands permissions)
- Side effects (unintended consequences)
- Knowledge corruption (malicious learning)

**Threats Not Defended**:
- Adversarial inputs (requires input validation)
- Host system compromise (OS-level security)
- Network attacks (requires network security)

### Security Guarantees

1. **Intent Alignment**: Provably validates every action
2. **Permission Boundaries**: Cannot self-elevate
3. **Auditability**: Complete action history
4. **Reversibility**: Rollback capability
5. **Bounded Learning**: Cannot learn to violate security

## Extension Points

### Custom Validators
Add domain-specific validation logic:
```typescript
interface CustomValidator {
  validate(action: Action, intent: Intent): Promise<ValidationResult>;
}
```

### Custom Anomaly Detectors
Add specialized anomaly detection:
```typescript
interface AnomalyDetector {
  detect(execution: ExecutionContext): Promise<Anomaly[]>;
}
```

### Custom Learning Strategies
Add domain-specific learning:
```typescript
interface LearningStrategy {
  analyze(outcome: Outcome): Promise<Learning[]>;
  extract(learnings: Learning[]): Promise<Pattern[]>;
}
```

## Future Enhancements

- **Multi-Agent Learning**: Share knowledge across agent instances
- **Formal Verification**: Prove safety properties mathematically
- **Advanced Anomaly Detection**: ML-based behavioral models
- **Distributed Execution**: Coordinate multiple agents on shared goals
- **Human-in-the-Loop**: Interactive approval and guidance
- **Transfer Learning**: Apply learnings across domains

---

This architecture provides a solid foundation for safe, adaptive autonomous agents while maintaining transparency and human oversight.
