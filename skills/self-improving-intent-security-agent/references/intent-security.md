# Intent Security Reference

Comprehensive guide to intent-based security for autonomous agents.

## What is Intent-Based Security?

Traditional security models (access control, permissions, firewalls) focus on **capabilities**: *what* an agent can do. Intent-based security adds a crucial layer: **purpose** - *why* the agent wants to do it and *whether it aligns with user goals*.

### Traditional Security vs. Intent Security

| Aspect | Traditional Security | Intent Security |
|--------|---------------------|----------------|
| Question | "Do you have permission?" | "Should you do this for this goal?" |
| Focus | Capabilities and resources | Goals and alignment |
| Validation | Static (permission list) | Dynamic (per-action validation) |
| Context | Resource-centric | Intent-centric |
| Granularity | Coarse (role-based) | Fine (action-based) |
| Adaptation | Manual policy updates | Learns from violations |

### Example

**Scenario**: Agent has permission to delete files

**Traditional Security**:
```
Agent: Delete file X
System: Do you have 'delete' permission? YES → Allow
```

**Intent Security**:
```
Agent: Delete file X
System:
  - Does this serve your stated goal? [Check]
  - Is this file in allowed scope? [Check]
  - Is deletion expected for this task? [Check]
  - Any unintended consequences? [Check]
  → If ALL pass: Allow
  → If ANY fail: Block + Log violation
```

## Core Concepts

### 1. Intent Specification

An **Intent** is a structured representation of what the user wants to achieve.

**Components**:

```typescript
interface Intent {
  // WHAT you want to achieve
  goal: string;

  // WHAT you must NOT do
  constraints: Constraint[];

  // HOW you should behave
  expectedBehavior: BehaviorPattern[];

  // HOW risky this is
  riskLevel: "low" | "medium" | "high";

  // CONTEXT for decision-making
  context: Context;
}
```

**Example Intent**:
```yaml
goal: "Refactor authentication module for better testability"

constraints:
  - "Only modify files in ./src/auth/"
  - "Do not change public API signatures"
  - "Maintain backward compatibility"
  - "Keep test coverage above 80%"

expectedBehavior:
  - "Read existing tests before modifying"
  - "Run tests after each change"
  - "Create backup before major refactoring"
  - "Update documentation if behavior changes"

riskLevel: medium

context:
  files: ["./src/auth/**/*.ts"]
  environment: "development"
  testCommand: "npm test -- src/auth"
```

### 2. Constraints

Constraints define **boundaries** the agent must respect.

**Constraint Types**:

| Type | Description | Example |
|------|-------------|---------|
| **Scope** | Where agent can operate | "Only files in ./src" |
| **Action** | What agent can/cannot do | "No file deletions" |
| **Resource** | Usage limits | "Max 1GB memory" |
| **Temporal** | Time-based restrictions | "Only during business hours" |
| **Dependency** | Required preconditions | "Must run tests first" |
| **Quality** | Quality gates | "Maintain 80% test coverage" |

**Constraint Format**:
```typescript
interface Constraint {
  type: "scope" | "action" | "resource" | "temporal" | "dependency" | "quality";
  condition: string;
  enforcement: "hard" | "soft";
  violation: {
    severity: "low" | "medium" | "high" | "critical";
    action: "block" | "warn" | "log";
  };
}
```

**Examples**:
```typescript
// Hard constraint - must be enforced
{
  type: "scope",
  condition: "files must be in ./src directory",
  enforcement: "hard",
  violation: { severity: "high", action: "block" }
}

// Soft constraint - warning but not blocking
{
  type: "quality",
  condition: "test coverage should be >= 80%",
  enforcement: "soft",
  violation: { severity: "medium", action: "warn" }
}
```

### 3. Expected Behavior

Expected Behavior defines **patterns** the agent should follow.

**Pattern Types**:

1. **Sequential Patterns**: "Do X before Y"
   - "Read file before modifying"
   - "Run tests after changes"
   - "Backup before destructive operations"

2. **Conditional Patterns**: "If X then Y"
   - "If modifying API, update docs"
   - "If test fails, rollback changes"
   - "If high risk, request approval"

3. **Frequency Patterns**: "How often to do X"
   - "Create checkpoint every 10 files"
   - "Run tests after each module"
   - "Report progress every minute"

4. **Resource Patterns**: "How to use resources"
   - "Process files in batches of 100"
   - "Limit concurrent connections to 5"
   - "Cache API responses for 5 minutes"

**Pattern Format**:
```typescript
interface BehaviorPattern {
  name: string;
  type: "sequential" | "conditional" | "frequency" | "resource";
  pattern: string;
  importance: "required" | "recommended" | "optional";
}
```

## Validation Mechanisms

### Pre-Execution Validation

Before every action, validate against intent:

```typescript
async function validateAction(
  action: Action,
  intent: Intent
): Promise<ValidationResult> {

  // 1. Goal Alignment Check
  const goalScore = computeGoalRelevance(action, intent.goal);
  if (goalScore < MIN_GOAL_RELEVANCE) {
    return {
      valid: false,
      reason: "Action does not serve stated goal",
      violation: "goal_misalignment"
    };
  }

  // 2. Constraint Compliance Check
  for (const constraint of intent.constraints) {
    if (!satisfiesConstraint(action, constraint)) {
      return {
        valid: false,
        reason: `Violates constraint: ${constraint.condition}`,
        violation: "constraint_breach",
        constraint: constraint
      };
    }
  }

  // 3. Behavioral Match Check
  const behaviorMatch = matchesBehavioralPatterns(
    action,
    intent.expectedBehavior
  );
  if (!behaviorMatch.matches) {
    return {
      valid: false,
      reason: `Deviates from expected behavior: ${behaviorMatch.deviation}`,
      violation: "behavior_deviation"
    };
  }

  // 4. Side Effect Assessment
  const sideEffects = analyzeS ideEffects(action, intent.context);
  if (sideEffects.unacceptable) {
    return {
      valid: false,
      reason: `Unacceptable side effects: ${sideEffects.list}`,
      violation: "unsafe_side_effects"
    };
  }

  return { valid: true };
}
```

### Goal Alignment Scoring

Compute how well an action serves the goal:

```typescript
function computeGoalRelevance(action: Action, goal: string): number {
  // Extract keywords from goal
  const goalKeywords = extractKeywords(goal);

  // Extract semantic meaning from action
  const actionSemantics = analyzeAction(action);

  // Compute semantic similarity (0-1)
  const similarity = cosineSimilarity(
    embed(goalKeywords),
    embed(actionSemantics)
  );

  // Adjust based on action type
  const typeRelevance = ACTION_TYPE_RELEVANCE[action.type];

  return similarity * typeRelevance;
}
```

**Example**:
```typescript
Goal: "Refactor authentication module"

Action: "Delete ./src/auth/old_auth.ts"
Keywords: ["delete", "auth", "file"]
Similarity to goal: 0.65 (moderate - related to auth)
Type relevance: 0.7 (deletion is common in refactoring)
Score: 0.65 * 0.7 = 0.455 → Below threshold (0.5) → BLOCK

Action: "Rename class AuthService to AuthenticationService"
Keywords: ["rename", "authentication", "service"]
Similarity to goal: 0.85 (high - directly about auth)
Type relevance: 0.9 (renaming is common in refactoring)
Score: 0.85 * 0.9 = 0.765 → Above threshold → ALLOW
```

### Constraint Satisfaction

Check if action satisfies constraints:

```typescript
function satisfiesConstraint(
  action: Action,
  constraint: Constraint
): boolean {
  switch (constraint.type) {
    case "scope":
      return checkScopeConstraint(action, constraint);
    case "action":
      return checkActionConstraint(action, constraint);
    case "resource":
      return checkResourceConstraint(action, constraint);
    // ...more types
  }
}

function checkScopeConstraint(action: Action, constraint: Constraint): boolean {
  // Example: "Only files in ./src"
  if (action.type === "file_operation") {
    const filePath = action.parameters.path;
    const allowedScope = extractScope(constraint.condition);
    return filePath.startsWith(allowedScope);
  }
  return true; // Constraint doesn't apply to this action type
}
```

## Authorization Boundaries

### Authorization Layers

1. **Resource Permissions**: Can agent access this resource?
2. **Action Permissions**: Can agent perform this action type?
3. **Scope Permissions**: Is target within authorized scope?
4. **Intent Authorization**: Does action serve current intent?

```typescript
async function authorizeAction(
  action: Action,
  intent: Intent
): Promise<AuthorizationResult> {

  // Layer 1: Resource permission
  if (!hasResourcePermission(action.resource)) {
    return deny("No permission for resource");
  }

  // Layer 2: Action permission
  if (!hasActionPermission(action.type)) {
    return deny("No permission for action type");
  }

  // Layer 3: Scope permission
  if (!inAuthorizedScope(action.target, action.scope)) {
    return deny("Target outside authorized scope");
  }

  // Layer 4: Intent authorization
  if (!authorizedForIntent(action, intent)) {
    return deny("Action not authorized for this intent");
  }

  // All layers passed
  return allow();
}
```

### Permission Elevation

**Rule**: Agent cannot self-elevate permissions.

```typescript
function authorizePermissionChange(
  currentPermissions: Permission[],
  requestedPermissions: Permission[]
): boolean {

  const expansion = findPermissionExpansion(
    currentPermissions,
    requestedPermissions
  );

  if (expansion.length > 0) {
    // Permission expansion detected
    logSecurityEvent({
      type: "permission_elevation_attempt",
      expansion: expansion,
      severity: "critical"
    });
    return false; // ALWAYS deny self-elevation
  }

  return true;
}
```

## Anomaly Detection

### Runtime Monitoring

Monitor execution for anomalies in real-time:

```typescript
class AnomalyDetector {
  private baselines: Map<string, Baseline>;
  private threshold: number;

  async detectAnomalies(execution: ExecutionContext): Promise<Anomaly[]> {
    const anomalies: Anomaly[] = [];

    // Check each monitored metric
    for (const metric of MONITORED_METRICS) {
      const baseline = this.baselines.get(metric);
      const current = execution.metrics[metric];

      if (this.isAnomalous(current, baseline)) {
        anomalies.push({
          type: metric,
          baseline: baseline.value,
          current: current,
          deviation: Math.abs(current - baseline.value) / baseline.stdDev,
          severity: this.assessSeverity(metric, current, baseline)
        });
      }
    }

    return anomalies;
  }

  private isAnomalous(current: number, baseline: Baseline): boolean {
    const zScore = Math.abs(current - baseline.value) / baseline.stdDev;
    return zScore > this.threshold;
  }
}
```

### Anomaly Types

#### 1. Goal Drift

**Detection**: Actions increasingly irrelevant to goal.

```typescript
function detectGoalDrift(execution: ExecutionContext): Anomaly | null {
  const recentActions = execution.actions.slice(-10);
  const goalRelevanceScores = recentActions.map(a =>
    computeGoalRelevance(a, execution.intent.goal)
  );

  const avgRelevance = mean(goalRelevanceScores);
  const trend = linearRegression(goalRelevanceScores);

  if (avgRelevance < 0.5 || trend.slope < -0.05) {
    return {
      type: "goal_drift",
      severity: "high",
      evidence: {
        avgRelevance: avgRelevance,
        trend: trend.slope,
        recentActions: recentActions
      },
      recommendation: "halt_and_clarify"
    };
  }

  return null;
}
```

#### 2. Capability Misuse

**Detection**: Tools used inappropriately or unexpectedly.

```typescript
function detectCapabilityMisuse(execution: ExecutionContext): Anomaly | null {
  const expectedCapabilities = inferExpectedCapabilities(execution.intent);
  const usedCapabilities = execution.actions.map(a => a.capability);

  const unexpected = usedCapabilities.filter(c =>
    !expectedCapabilities.includes(c)
  );

  if (unexpected.length > MAX_UNEXPECTED_CAPABILITIES) {
    return {
      type: "capability_misuse",
      severity: "medium",
      evidence: {
        expected: expectedCapabilities,
        used: usedCapabilities,
        unexpected: unexpected
      },
      recommendation: "verify_necessity"
    };
  }

  return null;
}
```

#### 3. Side Effects

**Detection**: Unintended state changes.

```typescript
function detectSideEffects(execution: ExecutionContext): Anomaly[] {
  const anomalies: Anomaly[] = [];

  // Check file system
  const unexpectedFiles = detectUnexpectedFileChanges(
    execution.intent.context.expectedFiles,
    execution.actualFileChanges
  );

  if (unexpectedFiles.length > 0) {
    anomalies.push({
      type: "unexpected_file_changes",
      severity: "medium",
      evidence: unexpectedFiles,
      recommendation: "review_and_rollback_if_unintended"
    });
  }

  // Check network calls
  const unexpectedNetworkCalls = detectUnexpectedNetworkActivity(
    execution.intent.constraints,
    execution.networkActivity
  );

  if (unexpectedNetworkCalls.length > 0) {
    anomalies.push({
      type: "unexpected_network_activity",
      severity: "high",
      evidence: unexpectedNetworkCalls,
      recommendation: "halt_and_investigate"
    });
  }

  return anomalies;
}
```

## Rollback and Recovery

### Checkpoint Strategy

**When to Create Checkpoints**:
- Before high-risk operations (file deletion, bulk modifications)
- At natural breakpoints (end of batch, before loop)
- User-requested checkpoints
- Automatic interval (every N actions)

```typescript
class CheckpointManager {
  async createCheckpoint(context: ExecutionContext): Promise<Checkpoint> {
    return {
      id: generateCheckpointId(),
      timestamp: Date.now(),
      intent: context.intent.id,
      state: await this.captureState(context),
      actions: []  // Will track actions after this point
    };
  }

  private async captureState(context: ExecutionContext): Promise<State> {
    return {
      fileSystem: await this.captureFileSystemState(context),
      variables: this.captureVariableState(context),
      externalState: await this.captureExternalState(context)
    };
  }
}
```

### Action Reversal

Each action type has a reversal strategy:

```typescript
interface ReversalStrategy {
  actionType: string;
  reverse(action: Action): Promise<Reversal>;
}

const FILE_WRITE_REVERSAL: ReversalStrategy = {
  actionType: "file_write",
  async reverse(action: Action): Promise<Reversal> {
    const {path, originalContent} = action.metadata;

    if (originalContent) {
      // Restore original content
      await fs.writeFile(path, originalContent);
      return {success: true, method: "restore"};
    } else {
      // Was new file, delete it
      await fs.unlink(path);
      return {success: true, method: "delete"};
    }
  }
};
```

### Recovery Strategies

Map anomaly types to recovery actions:

| Anomaly Type | Response | Recovery Strategy |
|--------------|----------|-------------------|
| Goal Drift | Halt | Request user clarification |
| Capability Misuse | Rollback | Restore last checkpoint |
| Constraint Violation | Rollback | Restore + log violation |
| Side Effect | Context-dependent | Assess severity → decide |
| Resource Exceeded | Throttle | Apply resource constraints |

## Examples

### Example 1: File Processing with Intent Security

```typescript
// Define intent
const intent = {
  goal: "Process customer feedback files and extract sentiment",
  constraints: [
    "Only read files in ./feedback directory",
    "Do not modify original files",
    "Respect PII privacy rules"
  ],
  expectedBehavior: [
    "Read files sequentially",
    "Create output in ./results directory",
    "Log processing status"
  ],
  riskLevel: "low"
};

// Agent proposes action
const action = {
  type: "file_delete",
  path: "./feedback/processed/old_file.txt"
};

// Validation
const validation = await validateAction(action, intent);
// Result: BLOCKED
// Reason: Violates constraint "Do not modify original files"
// Violation: constraint_breach

// Alternative action
const action2 = {
  type: "file_read",
  path: "./feedback/customer_001.txt"
};

const validation2 = await validateAction(action2, intent);
// Result: ALLOWED
// Checks passed:
//   - Goal alignment: ✓ (reading feedback for processing)
//   - Constraints: ✓ (read-only, correct directory)
//   - Behavior: ✓ (sequential reading as expected)
//   - Authorization: ✓ (read permission granted)
```

### Example 2: API Integration with Anomaly Detection

```typescript
// Intent
const intent = {
  goal: "Sync user data from external CRM",
  constraints: [
    "Only sync users created in last 7 days",
    "Do not write to production database",
    "Rate limit: 10 requests/second"
  ],
  expectedBehavior: [
    "Fetch users in batches of 100",
    "Validate data before inserting",
    "Log sync progress"
  ],
  riskLevel: "medium"
};

// Execution monitoring
const monitor = new ExecutionMonitor(intent);

// During execution, anomaly detected:
const anomaly = {
  type: "unexpected_api_calls",
  evidence: {
    expected: "10 requests/second",
    actual: "45 requests/second"
  },
  severity: "high"
};

// Recovery
await rollbackManager.restore(lastCheckpoint, {
  reason: "Rate limit violation detected",
  anomaly: anomaly
});

// Notify user
await notify({
  type: "violation_rollback",
  intent: intent.id,
  anomaly: anomaly,
  action: "rolled_back_to_checkpoint"
});
```

### Example 3: Goal Drift Detection

```typescript
// Intent
const intent = {
  goal: "Refactor authentication module",
  constraints: ["Only modify ./src/auth/**"],
  riskLevel: "medium"
};

// Actions taken:
const actions = [
  { type: "read", path: "./src/auth/service.ts" },      // Relevant
  { type: "edit", path: "./src/auth/service.ts" },      // Relevant
  { type: "read", path: "./src/auth/controller.ts" },   // Relevant
  { type: "edit", path: "./src/utils/logger.ts" },      // Less relevant
  { type: "edit", path: "./src/config/database.ts" },   // Not relevant
  { type: "edit", path: "./src/models/user.ts" }        // Not relevant
];

// Goal relevance scores:
const scores = [0.95, 0.95, 0.90, 0.45, 0.15, 0.20];

// Detection
const avgRelevance = mean(scores); // 0.60
const recentAvg = mean(scores.slice(-3)); // 0.27

if (recentAvg < 0.5) {
  triggerAnomaly({
    type: "goal_drift",
    severity: "high",
    evidence: {
      initialRelevance: 0.93,
      currentRelevance: 0.27,
      trend: "decreasing"
    },
    recommendation: "halt_and_clarify"
  });
}
```

## Best Practices

### Intent Specification

1. **Be Specific**: Vague goals lead to false violations
   - Bad: "Make the code better"
   - Good: "Refactor auth module to use dependency injection"

2. **List All Constraints**: Implicit constraints get violated
   - Include: File scope, action restrictions, quality gates
   - Document: Why each constraint matters

3. **Define Behavior**: Expected patterns catch deviations early
   - Specify: Order of operations, checkpointing strategy
   - Examples: "Read before write", "Test after change"

4. **Assess Risk Correctly**: Triggers appropriate safety mechanisms
   - Low: Read-only operations, non-production
   - Medium: Modifications, external API calls
   - High: Deletions, production changes, elevated privileges

### Validation Configuration

1. **Set Appropriate Thresholds**:
   - Goal relevance: 0.5-0.7 (higher = stricter)
   - Anomaly sensitivity: 0.8 (2-3 std deviations)
   - Resource limits: Based on historical usage

2. **Balance Safety and Flexibility**:
   - Too strict: Many false positives, blocks legitimate actions
   - Too loose: Misses violations, less safe
   - Calibrate: Based on domain and risk tolerance

3. **Learn from Violations**:
   - Review logs regularly
   - Adjust thresholds based on false positives/negatives
   - Promote recurring constraints to permanent rules

### Monitoring

1. **Monitor Continuously**: Not just at checkpoints
2. **Log Everything**: Even allowed actions need audit trail
3. **Alert on Anomalies**: Don't wait for violations
4. **Review Regularly**: Weekly review of violations and anomalies

---

Intent-based security transforms autonomous agents from "capable" to "trustworthy" by ensuring every action serves user goals within defined boundaries.
