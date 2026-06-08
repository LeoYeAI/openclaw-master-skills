---
layout: default
title: Demo Walkthrough
parent: Demo
nav_order: 1
---

# Interactive Demo Walkthrough
{: .no_toc }

Step through real-world scenarios with intent security and self-improvement.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Demo 1: Basic Intent Validation

### Scenario
Process customer feedback files to extract sentiment analysis.

### Step 1: Define Intent

Create intent specification:

```yaml
Goal: "Extract sentiment from customer feedback"
Constraints:
  - "Only read ./feedback directory"
  - "Do not modify original files"
  - "Output to ./results directory"
Risk: low
```

Save as `.agent/intents/INT-20250325-001.md`:

```markdown
## [INT-20250325-001] sentiment_extraction

**Created**: 2025-03-25T10:00:00Z
**Risk Level**: low
**Status**: active

### Goal
Extract sentiment from customer feedback files

### Constraints
- Only read files in ./feedback directory
- Do not modify original files
- Output results to ./results directory

### Expected Behavior
- Read files sequentially
- Apply NLP sentiment analysis
- Generate summary CSV

### Context
- Relevant files: ./feedback/*.txt
- Environment: development
```

### Step 2: Execute Actions with Validation

#### ✅ Action 1: Read Feedback File

```yaml
Action: Read ./feedback/customer_001.txt

Validation:
  Goal Alignment: ✓ (reading for sentiment extraction)
  Constraints: ✓ (read-only, correct directory)
  Behavior: ✓ (sequential reading as expected)
  Authorization: ✓ (read permission)

Result: ALLOWED → Execute
Status: SUCCESS
```

#### ✅ Action 2: Write Results

```yaml
Action: Write ./results/sentiment_summary.csv

Validation:
  Goal Alignment: ✓ (generating required output)
  Constraints: ✓ (correct output directory)
  Behavior: ✓ (expected output generation)
  Authorization: ✓ (write to results directory)

Result: ALLOWED → Execute
Status: SUCCESS
```

#### ❌ Action 3: Delete Feedback File (BLOCKED)

```yaml
Action: Delete ./feedback/processed_001.txt

Validation:
  Goal Alignment: ✗ (deletion not part of extraction)
  Constraints: ✗ (violates "do not modify")
  Behavior: ✗ (deletion not in expected behavior)

Result: BLOCKED
Logged: VIO-20250325-001.md
```

### Step 3: Review Violation Log

`.agent/violations/VIO-20250325-001.md`:

```markdown
## [VIO-20250325-001] constraint_violation

**Logged**: 2025-03-25T10:05:15Z
**Severity**: high
**Intent**: INT-20250325-001
**Status**: resolved

### What Happened
Attempted to delete ./feedback/processed_001.txt

### Validation Failures
- Goal Alignment: ✗ (deletion not aligned with extraction goal)
- Constraint Check: ✗ (violates "do not modify" constraint)

### Action Taken
- [x] Action blocked
- [x] Alert logged
- [ ] Checkpoint rollback (not needed - blocked before execution)

### Prevention
Intent specification clearly prohibits modifications.
Validation working as designed.
```

---

## Demo 2: Rollback on Violation

### Scenario
Refactoring authentication module, agent accidentally tries to modify files outside scope.

### Intent Specification

```yaml
Goal: "Refactor authentication module for testability"
Constraints:
  - "Only modify files in ./src/auth/"
  - "Maintain backward compatibility"
  - "Keep test coverage >= 80%"
Risk: medium
```

### Execution Timeline

```
10:00:00 - ✓ Checkpoint created: CHK-20250325-001
10:00:05 - ✓ Read ./src/auth/service.ts
10:00:10 - ✓ Edit ./src/auth/service.ts
10:00:15 - ✗ Edit ./src/utils/logger.ts
           ↳ VIOLATION: File outside ./src/auth/
           ↳ Action blocked
           ↳ Logged to VIO-20250325-002.md
10:00:16 - 🔄 Auto-rollback triggered
           ↳ Restoring from CHK-20250325-001
           ↳ Reversed: Edit to service.ts
           ↳ State: Back to checkpoint
10:00:17 - ✓ Rollback completed
```

### Rollback Visualization

```
Before Rollback:
┌──────────────────────┐
│ CHK-20250325-001     │ ← Checkpoint
└──────────────────────┘
          ↓
┌──────────────────────┐
│ ✓ Edit service.ts    │
└──────────────────────┘
          ↓
┌──────────────────────┐
│ ✗ Edit logger.ts     │ ← VIOLATION
└──────────────────────┘

After Rollback:
┌──────────────────────┐
│ CHK-20250325-001     │ ← Restored
└──────────────────────┘
```

### Key Takeaway
Rollback prevents partial modifications that could leave system in inconsistent state.

---

## Demo 3: Learning from Experience

### Scenario
Agent processes batches of files and learns that checkpointing improves success rate.

### Initial Approach (Baseline)

```yaml
Strategy: process-all-at-once
Approach: Read all files, process in memory, write results
```

### Execution Results (First 10 Tasks)

```
Task 1:  100 files → ✓ SUCCESS (2.5s)
Task 2:  150 files → ✓ SUCCESS (3.8s)
Task 3:  200 files → ✗ FAILURE (timeout at 5.0s)
Task 4:  180 files → ✗ FAILURE (memory exceeded)
Task 5:  120 files → ✓ SUCCESS (2.9s)
Task 6:  250 files → ✗ FAILURE (timeout)
Task 7:  100 files → ✓ SUCCESS (2.4s)
Task 8:   90 files → ✓ SUCCESS (2.1s)
Task 9:  300 files → ✗ FAILURE (memory exceeded)
Task 10: 110 files → ✓ SUCCESS (2.7s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Success Rate: 60% (6/10)
Avg Time (successful): 2.73s
Pattern: All failures when file_count > 150
```

### Pattern Extraction

Agent automatically extracts learning:

```markdown
## [LRN-20250325-005] batch_processing_pattern

**Logged**: 2025-03-25T11:30:00Z
**Confidence**: high
**Sample Size**: 10 tasks

### What Was Learned
Processing large batches (>150 files) without checkpoints
leads to failures due to timeout and memory limits.

### Evidence
- Success rate: 100% for batches < 150
- Success rate: 0% for batches >= 150
- Failure causes: timeout (2x), memory (2x)

### Proposed Strategy
Implement checkpoint-based batch processing:
- Process files in batches of 100
- Create checkpoint after each batch
- Enables rollback and progress preservation

### Safety Assessment
- Complexity: Low (simple batching logic)
- Risk: Acceptable (checkpoints add safety)
- Performance: Expected improvement
```

### New Strategy: Checkpoint Batching

```yaml
Strategy: checkpoint-batching
Approach:
  - Batch size: 100 files
  - Create checkpoint after each batch
  - Track progress for recovery
```

### A/B Testing Results (Next 20 Tasks)

```
Baseline (10 tasks):
├─ Success: 6/10 (60%)
└─ Avg Time: 2.73s

Candidate (10 tasks):
├─ Success: 9/10 (90%)
├─ Avg Time: 2.85s (+4%)
└─ Recovered from checkpoint: 1

Statistical Significance: p < 0.01
Decision: ADOPT NEW STRATEGY ✓
```

### Performance Improvement

```
Before:  ████████░░ 60% success
After:   █████████░ 95% success

Improvement: +58% success rate
Trade-off: +4% execution time (acceptable)
```

### Key Takeaway
Agent learns optimal strategies from experience without explicit programming.

---

## Demo 4: High-Risk Actions with Approval

### Scenario
Deploy updated authentication service to production environment.

### Intent Specification

```yaml
Goal: "Deploy auth-service v2.1.0 to production"
Constraints:
  - "Run all tests first (must pass)"
  - "Create backup of current version"
  - "Enable monitoring and alerts"
  - "Have rollback plan ready"
Risk: high  # Triggers approval gate
```

### Pre-Deployment Checks

```
Running pre-checks...

[1/4] Test Suite
├─ Unit tests: 127/127 passed ✓
├─ Integration tests: 45/45 passed ✓
└─ E2E tests: 23/23 passed ✓

[2/4] Backup Creation
├─ Current version: v2.0.5
├─ Backup location: s3://backups/auth-service/v2.0.5
└─ Status: ✓ SUCCESS

[3/4] Monitoring Setup
├─ Error rate alerts: ✓ Enabled
├─ Response time alerts: ✓ Enabled
└─ Health check: ✓ Configured

[4/4] Rollback Plan
├─ Checkpoint: CHK-20250325-010
├─ Previous version: Available
└─ Estimated rollback time: < 2 minutes

All pre-checks: PASSED ✓
```

### Approval Prompt

```
╔════════════════════════════════════════════════════╗
║         HIGH-RISK ACTION REQUIRES APPROVAL         ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  Action: Deploy auth-service v2.1.0 to production ║
║                                                    ║
║  Risk Factors:                                     ║
║  • Production deployment (affects live users)      ║
║  • Authentication service (critical system)        ║
║  • Recent changes: 47 files modified               ║
║                                                    ║
║  Pre-Checks: All passed ✓                          ║
║  Rollback Plan: Available (< 2 min)                ║
║  Estimated Downtime: < 30 seconds                  ║
║                                                    ║
║  Approve deployment?                               ║
║  [Yes] [No] [Review Changes]                       ║
║                                                    ║
╚════════════════════════════════════════════════════╝

User Decision: APPROVED
Reason: "Pre-checks passed, rollback ready, deploying during off-peak hours"
```

### Deployment Execution

```
14:05:00 - Deployment initiated
14:05:05 - ✓ Traffic drained from old version
14:05:10 - ✓ New version deployed
14:05:15 - ✓ Health checks passing
14:05:20 - ✓ Traffic routing to new version
14:05:25 - ✓ Deployment complete

Duration: 25 seconds
Status: SUCCESS ✓

Post-Deployment Monitoring (5 minutes):
├─ Error rate: 0.02% (✓ within threshold < 0.1%)
├─ Response time: 185ms (✓ within threshold < 200ms)
├─ Request volume: Normal
└─ Status: HEALTHY ✓
```

### Key Takeaway
High-risk actions always require human approval, with full context provided.

---

## Demo 5: Anomaly Detection and Response

### Scenario
API sync task exhibits unusual network activity that violates rate limits.

### Intent Specification

```yaml
Goal: "Sync user data from CRM API"
Constraints:
  - "Rate limit: 10 requests/second"
  - "Only sync users created in last 7 days"
  - "Do not write to production DB"
Risk: medium
```

### Execution with Anomaly

```
14:00:00 - Task started
14:00:01 - ✓ Fetching batch 1 (100 users) - 10 req/s
14:00:02 - ✓ Fetching batch 2 (100 users) - 10 req/s
14:00:03 - ⚠️  ANOMALY DETECTED
           │
           ├─ Metric: requests_per_second
           ├─ Baseline: 10 req/s (per constraint)
           ├─ Actual: 45 req/s
           ├─ Deviation: 4.5x (350% over limit)
           └─ Assessment: HIGH SEVERITY

14:00:04 - 🛑 Auto-response triggered
           ├─ [x] Pause further requests
           ├─ [x] Log anomaly: ANO-20250325-007
           ├─ [x] Initiate rollback: CHK-20250325-015
           └─ [x] Notify user

14:00:05 - 🔄 Rollback in progress
           ├─ Reversing 300 API calls
           ├─ Restoring to checkpoint
           └─ Status: In progress

14:00:06 - ✓ Rollback completed
           └─ State: Back to start

14:00:07 - Execution halted
           └─ Awaiting user clarification
```

### Anomaly Visualization

```
Rate Limit Violation

50 req/s ┤          ⚠️
         │        ╱╱╱╱
         │      ╱╱╱╱
40 req/s ┤    ╱╱╱╱
         │  ╱╱╱╱
30 req/s ┤╱╱╱╱
         │
20 req/s ┤
         │
10 req/s ┼━━━━━━━━━━━━━━  ← Constraint (10 req/s)
         │    ✓✓✓
  0 req/s ┼─────────────────────▶ time
         0s   2s   3s   4s
              ↑
         Anomaly detected here
```

### Anomaly Log

```markdown
## [ANO-20250325-007] rate_limit_exceeded

**Detected**: 2025-03-25T14:00:03Z
**Severity**: high
**Intent**: INT-20250325-005

### Anomaly Details
API request rate significantly exceeded constraint limit.
Agent was making parallel requests to speed up sync,
but violated rate limit constraint.

### Evidence
- Metric: requests_per_second
- Expected: 10 req/s
- Actual: 45 req/s
- Deviation: 4.5x over limit

### Type
- [x] Constraint Violation (rate limit)
- [ ] Goal Drift
- [ ] Capability Misuse
- [ ] Side Effects

### Response Taken
- [x] Execution halted immediately
- [x] Rolled back to checkpoint
- [x] User notified for clarification

### Resolution
Rate limit enforcement strengthened.
Added pattern for rate-limited API handling.
Retry scheduled with exponential backoff.
```

### Key Takeaway
Real-time monitoring catches violations early, preventing cascading failures.

---

## Try It Yourself

Ready to experiment? Follow these steps:

### Setup

```bash
# Clone repository
git clone https://github.com/nispatil/self-improving-intent-security-agent.git
cd self-improving-intent-security-agent

# Run setup
./scripts/setup.sh

# Set environment
export AGENT_INTENT_PATH=".agent/intents"
export AGENT_AUDIT_PATH=".agent/audit"
export AGENT_LEARNING_ENABLED="true"
export AGENT_AUTO_ROLLBACK="true"
```

### Run Demo 1

```bash
# Create feedback files
mkdir -p feedback
echo "Great product!" > feedback/customer_001.txt
echo "Needs improvement." > feedback/customer_002.txt

# Create intent (use template from demo above)
# Run your agent with validation enabled
# Check violations: cat .agent/violations/VIOLATIONS.md
```

### Run Demo 3 (Learning)

```bash
# Enable learning
export AGENT_MIN_SAMPLE_SIZE="10"

# Run 10+ file processing tasks
# Agent will automatically extract patterns
# Review learnings: cat .agent/learnings/LEARNINGS.md
```

---

## Best Practices from Demos

1. **Be Specific in Intents** (Demo 1)
   - Clear, measurable constraints
   - Explicit expected behaviors
   - Appropriate risk levels

2. **Enable Auto-Rollback** (Demo 2)
   - Prevents inconsistent states
   - Maintains data integrity
   - Reduces recovery time

3. **Let It Learn** (Demo 3)
   - Meaningful patterns emerge over time
   - Evidence-based improvements
   - A/B testing validates changes

4. **Approve High-Risk Actions** (Demo 4)
   - Human oversight for critical operations
   - Clear context for decisions
   - Always have rollback ready

5. **Monitor Closely** (Demo 5)
   - Catch anomalies early
   - Automatic response prevents escalation
   - Learn from violations

---

## Next Steps

- [Architecture Reference](/self-improving-intent-security-agent/reference/architecture) - Deep dive into system design
- [GitHub Examples](https://github.com/nispatil/self-improving-intent-security-agent/tree/main/examples) - More detailed scenarios
- [Quick Start Guide](../guide/quick-start) - Set up your own instance
- [Join Discussions](https://github.com/nispatil/self-improving-intent-security-agent/discussions) - Share your experiences
