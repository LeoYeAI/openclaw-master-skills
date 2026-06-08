# Usage Examples

Practical examples demonstrating intent security and self-improvement.

## End-to-End Demo Folder

For a realistic multi-file example with conversation, audit logs, violation handling, rollback, and learning artifacts, see [`customer-feedback-demo/`](./customer-feedback-demo).

To scaffold a new folder like this automatically, run:

```bash
./scripts/scaffold-run.sh examples/my-demo task_slug medium
```

## Example 1: Basic Intent Specification and Validation

### Scenario
Process customer feedback files to extract sentiment analysis.

### Intent Specification
```yaml
Goal: "Extract sentiment from customer feedback files"

Constraints:
  - "Only read files in ./feedback directory"
  - "Do not modify original files"
  - "Output results to ./results directory"
  - "Respect PII privacy (no storing personal data)"

Expected Behavior:
  - "Read files sequentially"
  - "Apply NLP sentiment analysis"
  - "Generate summary CSV"
  - "Log processing status"

Risk Level: low
```

### Execution
```bash
# Save intent
cat > .agent/intents/INT-20250115-001.md <<'EOF'
## [INT-20250115-001] sentiment_extraction

**Created**: 2025-01-15T10:00:00Z
**Risk Level**: low
**Status**: active

### Goal
Extract sentiment from customer feedback files

### Constraints
- Only read files in ./feedback directory
- Do not modify original files
- Output results to ./results directory
- Respect PII privacy (no storing personal data)

### Expected Behavior
- Read files sequentially
- Apply NLP sentiment analysis
- Generate summary CSV
- Log processing status

### Context
- Relevant files: ./feedback/*.txt
- Environment: development
- Output: ./results/sentiment_summary.csv
EOF

# Execute task with validation
# Agent automatically validates each action against intent
```

### Example Actions and Validation

**Action 1: Read feedback file** ✓
```yaml
Action: Read ./feedback/customer_001.txt
Validation:
  - Goal Alignment: ✓ (reading for sentiment extraction)
  - Constraints: ✓ (read-only, correct directory)
  - Behavior: ✓ (sequential reading as expected)
  - Authorization: ✓ (read permission)
Result: ALLOWED
```

**Action 2: Write summary** ✓
```yaml
Action: Write ./results/sentiment_summary.csv
Validation:
  - Goal Alignment: ✓ (generating required output)
  - Constraints: ✓ (correct output directory)
  - Behavior: ✓ (expected output generation)
  - Authorization: ✓ (write to results)
Result: ALLOWED
```

**Action 3: Delete feedback file** ✗
```yaml
Action: Delete ./feedback/processed_001.txt
Validation:
  - Goal Alignment: ✗ (deletion not part of extraction)
  - Constraints: ✗ (violates "do not modify")
  - Behavior: ✗ (deletion not expected)
Result: BLOCKED → Logged to VIO-20250115-001.md
```

---

## Example 2: Handling Violations and Rollback

### Scenario
Refactoring authentication module, agent accidentally modifies files outside scope.

### Intent
```yaml
Goal: "Refactor authentication module for testability"
Constraints:
  - "Only modify files in ./src/auth/"
  - "Maintain backward compatibility"
  - "Keep test coverage >= 80%"
Risk Level: medium
```

### Execution Timeline

```
10:00:00 - Checkpoint created: CHK-20250115-001
10:00:05 - Read ./src/auth/service.ts ✓
10:00:10 - Edit ./src/auth/service.ts ✓
10:00:15 - Edit ./src/utils/logger.ts ✗
          ↳ Violation detected: File outside ./src/auth/
          ↳ Action blocked
          ↳ Logged to VIO-20250115-002.md
10:00:16 - Auto-rollback triggered
          ↳ Restoring from CHK-20250115-001
          ↳ Reversed: Edit to service.ts
          ↳ State: Back to checkpoint
```

### Violation Log
```markdown
## [VIO-20250115-002] scope_violation

**Logged**: 2025-01-15T10:00:15Z
**Severity**: high
**Intent**: INT-20250115-002
**Status**: resolved

### What Happened
Attempted to edit ./src/utils/logger.ts

### Validation Failures
- Goal Alignment: ✓ (logger refactoring related)
- Constraint Check: ✗ (file outside ./src/auth/ directory)
- Behavior Match: ✓ (editing as expected)

### Action Taken
- [x] Action blocked
- [x] Checkpoint rollback to CHK-20250115-001
- [x] Alert sent
- [ ] Execution halted

### Root Cause
Agent identified logger dependency and attempted to refactor it along
with auth module. Legitimate intent but violates scope constraint.

### Prevention
Add explicit constraint: "Do not modify dependencies outside scope"
OR: Expand scope if logger refactoring is acceptable

### Resolution
- **Resolved**: 2025-01-15T10:00:20Z
- **Action**: Scope constraint enforced, rollback successful
- **Follow-up**: User clarified to keep logger as-is
```

---

## Example 3: Learning from Task Outcomes

### Scenario
Agent processes large batch of files, learns that checkpointing improves success rate.

### Initial Approach (Baseline)
```
Strategy: process-all-at-once
Approach: Read all files, process, write results
```

### Execution Results (First 10 Tasks)
```
Task 1: 100 files → SUCCESS (2.5s)
Task 2: 150 files → SUCCESS (3.8s)
Task 3: 200 files → FAILURE (timeout at 5.0s)
Task 4: 180 files → FAILURE (memory exceeded)
Task 5: 120 files → SUCCESS (2.9s)
Task 6: 250 files → FAILURE (timeout)
Task 7: 100 files → SUCCESS (2.4s)
Task 8: 90 files → SUCCESS (2.1s)
Task 9: 300 files → FAILURE (memory exceeded)
Task 10: 110 files → SUCCESS (2.7s)

Success Rate: 60% (6/10)
Avg Time (successful): 2.73s
Failures: All when file_count > 150
```

### Pattern Extraction
```markdown
## [LRN-20250115-005] batch_processing_pattern

**Logged**: 2025-01-15T11:30:00Z
**Intent**: INT-20250115-003
**Outcome**: partial (60% success)

### What Was Learned
Processing large batches (>150 files) without checkpoints leads to
failures due to timeout and memory limits.

### Evidence
- Success rate: 100% for batches < 150
- Success rate: 0% for batches >= 150
- Failure causes: timeout (2x), memory exceeded (2x)

### Strategy Impact
Implement checkpoint-based batch processing:
- Process files in batches of 100
- Create checkpoint after each batch
- Enables rollback and progress preservation

### Application Scope
- Task types: file_processing, data_transformation
- Risk levels: low, medium
- Conditions: file_count > 100

### Safety Check
- Complexity: low (simple batching logic)
- Performance: expected improvement
- Risk: acceptable (checkpoints add safety)

### Metadata
- Category: optimization
- Confidence: high
- Sample Size: 10 tasks
- Pattern-Key: file.batch_processing
```

### New Strategy Created
```markdown
## [STR-20250115-003] checkpoint_batching

**Created**: 2025-01-15T11:35:00Z
**Domain**: file_processing
**Status**: testing
**Version**: 1.0.0

### Approach
Process files in batches of 100, create checkpoint after each batch

### Hypothesis
Batching with checkpoints will improve success rate for large file sets
and enable recovery from mid-process failures

### Baseline Performance
- Success rate: 60%
- Avg time: 2.73s (only successful tasks)
- Failures: 40% (all on large batches)

### Candidate Performance
(After A/B testing with 20 more tasks...)
- Success rate: 95% (19/20 successful)
- Avg time: 2.85s (slightly slower but more reliable)
- Failures: 5% (1 task failed, but recovered from checkpoint)

### Improvement
- Success rate: +58% (60% → 95%)
- Execution time: +4% (acceptable trade-off)
- Reliability: Significantly better

### A/B Test Configuration
- Test ratio: 10% candidate, 90% baseline
- Test tasks: 20
- Candidate wins: 19, Baseline wins: 12
- Statistical significance: p < 0.01

### Adoption Decision
- [x] Adopt (major improvement in reliability)

### Rollout Plan
- Phase 1: 10% of tasks (complete) → 95% success
- Phase 2: 25% of tasks (in progress)
- Phase 3: 50% of tasks (if validated)
- Phase 4: 100% adoption (target: week 3)
```

---

## Example 4: High-Risk Actions with Approval

### Scenario
Deploy updated service to production.

### Intent
```yaml
Goal: "Deploy authentication service v2.1.0 to production"
Constraints:
  - "Run all tests first (must pass)"
  - "Create backup of current version"
  - "Enable monitoring and alerts"
  - "Have rollback plan ready"
Risk Level: high  # Triggers approval gate
```

### Execution Flow

```typescript
// 1. Agent prepares deployment
const deployment = {
  service: "auth-service",
  version: "2.1.0",
  environment: "production",
  preChecks: [
    "run_tests",
    "create_backup",
    "enable_monitoring"
  ]
};

// 2. Pre-checks execute
runTests() → ALL PASS ✓
createBackup() → SUCCESS ✓
enableMonitoring() → SUCCESS ✓

// 3. High-risk action requires approval
const action = {
  type: "deployment",
  target: "production",
  riskLevel: "high"
};

// 4. Approval prompt shown to user
const approvalRequest = {
  action: "Deploy auth-service v2.1.0 to production",
  riskFactors: [
    "Production deployment (affects live users)",
    "Authentication service (critical system)",
    "Recent changes: 47 files modified"
  ],
  preChecks: "All passed ✓",
  rollbackPlan: "CHK-20250115-010 available",
  estimatedDowntime: "< 30 seconds"
};

// 5. User reviews and approves
userApproval = await promptForApproval(approvalRequest);

if (userApproval) {
  // 6. Execute deployment with monitoring
  executeDeployment(deployment);

  // 7. Monitor for anomalies
  monitorDeployment({
    errorRate: "< 0.1%",
    responseTime: "< 200ms",
    duration: "5 minutes"
  });
} else {
  log("Deployment cancelled by user");
}
```

### Approval Log
```markdown
## [INT-20250115-004] production_deployment

**Created**: 2025-01-15T14:00:00Z
**Risk Level**: high
**Status**: completed

### Goal
Deploy authentication service v2.1.0 to production

### Constraints
- Run all tests first (must pass)
- Create backup of current version
- Enable monitoring and alerts
- Have rollback plan ready

### Approval Request
**Timestamp**: 2025-01-15T14:05:00Z
**User**: john@example.com
**Decision**: APPROVED
**Reason**: "Pre-checks passed, rollback ready, off-peak deployment"

### Execution
- Pre-checks: ALL PASSED
- Deployment: SUCCESS
- Monitoring: No anomalies detected
- Duration: 25 seconds

### Post-Deployment
- Error rate: 0.02% (within threshold)
- Response time: 185ms (within threshold)
- Status: HEALTHY
```

---

## Example 5: Anomaly Detection and Response

### Scenario
API sync task exhibits unusual network activity.

### Intent
```yaml
Goal: "Sync user data from CRM API"
Constraints:
  - "Rate limit: 10 requests/second"
  - "Only sync users created in last 7 days"
  - "Do not write to production DB"
Risk Level: medium
```

### Execution with Anomaly

```
14:00:00 - Task started
14:00:01 - Fetching users batch 1 (100 users)
14:00:02 - Fetching users batch 2 (100 users)
14:00:03 - Fetching users batch 3 (100 users)
14:00:04 - ⚠️  ANOMALY DETECTED: Rate limit exceeded
           Expected: 10 req/s
           Actual: 45 req/s
           Deviation: 4.5x baseline

14:00:05 - Auto-response triggered:
           ✓ Pause further requests
           ✓ Log anomaly: ANO-20250115-007
           ✓ Assess severity: HIGH
           ✓ Initiate rollback: CHK-20250115-015

14:00:06 - Rollback completed:
           ✓ Restored to checkpoint
           ✓ 300 API calls reversed (compensating deletes)
           ✓ State: Back to start

14:00:07 - Execution halted
           ✓ User notified
           ✓ Request clarification on rate limit handling
```

### Anomaly Log
```markdown
## [ANO-20250115-007] rate_limit_exceeded

**Detected**: 2025-01-15T14:00:04Z
**Severity**: high
**Intent**: INT-20250115-005
**Status**: resolved

### Anomaly Details
API request rate significantly exceeded constraint limits

### Evidence
- Metric: requests_per_second
- Baseline: 10 req/s (per constraint)
- Actual: 45 req/s
- Deviation: 4.5x (350% over limit)
- Timeline: Started at 14:00:01, detected at 14:00:04

### Assessment
Agent was making parallel requests to speed up sync,
but violated rate limit constraint. Likely to trigger
API throttling or account suspension.

### Type
- [x] Constraint Violation (rate limit)
- [ ] Goal Drift
- [ ] Capability Misuse
- [ ] Side Effects
- [ ] Resource Exceeded

### Response Taken
- [x] Halted execution
- [x] Rolled back to checkpoint CHK-20250115-015
- [x] Logged anomaly for analysis
- [x] Requested user clarification

### Resolution
- **Resolved**: 2025-01-15T14:10:00Z
- **Action**: Rate limit enforcement strengthened
- **Learning**: Added pattern for rate-limited APIs
- **Next**: Retry with exponential backoff and rate limiting
```

---

## Running the Examples

### Prerequisites
```bash
# Create directory structure
mkdir -p .agent/{intents,violations,learnings,audit}

# Copy templates
cp assets/*.md .agent/

# Set environment
export AGENT_INTENT_PATH=".agent/intents"
export AGENT_AUDIT_PATH=".agent/audit"
export AGENT_LEARNING_ENABLED="true"
```

### Try Example 1
```bash
# Create intent
cp examples/intent-sentiment.md .agent/intents/INT-$(date +%Y%m%d)-001.md

# Run with validation
# (Your agent implementation here)

# Review logs
grep -r "BLOCKED" .agent/violations/
```

### Try Example 2
```bash
# Enable rollback
export AGENT_AUTO_ROLLBACK="true"

# Run refactoring task
# Agent will auto-rollback on violations

# Review rollback log
cat .agent/audit/ROLLBACKS.md
```

### Try Example 3
```bash
# Enable learning
export AGENT_LEARNING_ENABLED="true"
export AGENT_MIN_SAMPLE_SIZE="10"

# Run multiple file processing tasks
# Agent will extract patterns automatically

# Review learnings
cat .agent/learnings/LEARNINGS.md
cat .agent/learnings/STRATEGIES.md
```

---

## Best Practices from Examples

1. **Be Specific in Intents**: Example 1 shows clear, measurable constraints
2. **Enable Auto-Rollback**: Example 2 demonstrates safety value
3. **Let It Learn**: Example 3 shows meaningful patterns emerge over time
4. **Approve High-Risk**: Example 4 demonstrates human oversight
5. **Monitor Closely**: Example 5 shows catching anomalies early prevents bigger issues

## Next Steps

- See [SKILL.md](../SKILL.md) for complete usage guide
- See [references/](../references/) for detailed concepts
- See [scripts/](../scripts/) for helper tools
