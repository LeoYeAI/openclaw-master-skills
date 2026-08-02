#!/usr/bin/env bash
# Scaffold a conversation-driven intent security run folder.

set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 <target-dir> <slug> [risk-level]"
    exit 1
fi

TARGET_DIR="$1"
SLUG="$2"
RISK_LEVEL="${3:-medium}"

case "$RISK_LEVEL" in
    low|medium|high) ;;
    *)
        echo "Error: risk level must be one of: low, medium, high"
        exit 1
        ;;
esac

DATE_STAMP="$(date +%Y%m%d)"
ISO_NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

INTENT_ID="INT-${DATE_STAMP}-001"
AUDIT_ID="AUD-${DATE_STAMP}-001"
VIOLATION_ID="VIO-${DATE_STAMP}-001"
ANOMALY_ID="ANO-${DATE_STAMP}-001"
ROLLBACK_ID="RBK-${DATE_STAMP}-001"
LEARNING_ID="LRN-${DATE_STAMP}-001"
STRATEGY_ID="STR-${DATE_STAMP}-001"
CHECKPOINT_ID="CHK-${DATE_STAMP}-001"

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$TARGET_DIR/.agent/intents"
mkdir -p "$TARGET_DIR/.agent/audit"
mkdir -p "$TARGET_DIR/.agent/violations"
mkdir -p "$TARGET_DIR/.agent/learnings"

cat > "$TARGET_DIR/README.md" <<EOF
# ${SLUG//_/ } Run

This folder was scaffolded by \`scripts/scaffold-run.sh\`.

It is intended for:
- working through a real user and agent interaction
- documenting how intent security decisions were made
- recording violations, rollbacks, and learnings in one place

## Files

- \`conversation.md\`
- \`report.md\`
- \`.agent/intents/${INTENT_ID}.md\`
- \`.agent/audit/${AUDIT_ID}.md\`
- \`.agent/violations/ANOMALIES.md\`
- \`.agent/violations/${VIOLATION_ID}.md\`
- \`.agent/audit/ROLLBACKS.md\`
- \`.agent/learnings/${LEARNING_ID}.md\`
- \`.agent/learnings/STRATEGIES.md\`
EOF

if [ -f "$SKILL_DIR/assets/CONVERSATION-TEMPLATE.md" ]; then
    cp "$SKILL_DIR/assets/CONVERSATION-TEMPLATE.md" "$TARGET_DIR/conversation.md"
else
    cat > "$TARGET_DIR/conversation.md" <<EOF
# Detailed User and Agent Conversation

Replace this file with the real transcript for the run.
EOF
fi

cat > "$TARGET_DIR/report.md" <<EOF
# Intent Security Agent Report

## Run Summary

- Intent: \`${INTENT_ID}\`
- Scenario: ${SLUG//_/ }
- Final status: in_progress
- Risk level: ${RISK_LEVEL}

## Outcome

Document the final outcome here after the run completes.

## Security Behavior

- Intent captured before execution: pending
- Per-action validation applied: pending
- Unsafe action blocked: pending
- Auto-rollback used: pending

## Learnings

Document reusable learnings here.
EOF

cat > "$TARGET_DIR/.agent/intents/${INTENT_ID}.md" <<EOF
## [${INTENT_ID}] ${SLUG}

**Created**: ${ISO_NOW}
**Risk Level**: ${RISK_LEVEL}
**Status**: active

### Goal
State the single primary goal for this run.

### Constraints
- Add hard boundaries here
- Add approved paths, systems, or data types here
- Add privacy or safety constraints here

### Expected Behavior
- Read before write
- Validate before execution
- Create checkpoints before risky actions

### Context
- Relevant files:
- Environment:
- Requested by:

---
EOF

cat > "$TARGET_DIR/.agent/audit/${AUDIT_ID}.md" <<EOF
# Audit Log

## [${AUDIT_ID}] execution_trace

**Started**: ${ISO_NOW}
**Intent**: ${INTENT_ID}
**Status**: in_progress

### Timeline

| Time | Action | Validation Outcome | Notes |
|------|--------|--------------------|-------|
| ${ISO_NOW##*T} | Intent created | allowed | Initial capture complete |
| ${ISO_NOW##*T} | Checkpoint ${CHECKPOINT_ID} created | allowed | Before risky work |

### Decision Notes

- Record key validation decisions here.

### Summary Metrics

- Allowed actions: 0
- Blocked actions: 0
- Checkpoints created: 1
- Rollbacks executed: 0

---
EOF

cat > "$TARGET_DIR/.agent/violations/ANOMALIES.md" <<EOF
# Anomaly Detection Log

Track unusual behavioral patterns detected during execution.

---

## [${ANOMALY_ID}] anomaly_type

**Detected**: ${ISO_NOW}
**Severity**: medium
**Intent**: ${INTENT_ID}
**Status**: monitoring

### Anomaly Details
Document any suspicious or unusual behavior here.

### Evidence
- Metric that triggered alert:
- Baseline value:
- Actual value:
- Deviation:
- Timeline:

### Assessment
Explain why this behavior was considered anomalous.

### Type
- [ ] Goal Drift
- [ ] Capability Misuse
- [ ] Side Effects
- [ ] Resource Exceeded
- [ ] Pattern Deviation

### Response Taken
- [ ] Continued with monitoring
- [ ] Applied constraints
- [ ] Rolled back to checkpoint
- [ ] Halted execution
- [ ] Requested clarification

### Metadata
- Related Intent: ${INTENT_ID}
- Threshold:
- False Positive: unknown

---
EOF

cat > "$TARGET_DIR/.agent/violations/${VIOLATION_ID}.md" <<EOF
# Intent Violations

Log actions that failed validation or violated user intent.

---

## [${VIOLATION_ID}] violation_type

**Logged**: ${ISO_NOW}
**Severity**: high
**Intent**: ${INTENT_ID}
**Status**: pending_review

### What Happened
Describe the blocked or unsafe action here.

### Validation Failures
- Goal Alignment:
- Constraint Check:
- Behavior Match:
- Authorization:

### Action Taken
- [ ] Action blocked
- [ ] Checkpoint rollback
- [ ] Alert sent
- [ ] Execution halted

### Root Cause
Explain why the agent attempted this action.

### Prevention
Explain how to avoid repeating it.

### Metadata
- Related Intent: ${INTENT_ID}
- Action Type: command_execution
- Risk Level: ${RISK_LEVEL}

---
EOF

cat > "$TARGET_DIR/.agent/audit/ROLLBACKS.md" <<EOF
# Rollback History

---

## [${ROLLBACK_ID}] checkpoint_restore

**Triggered**: ${ISO_NOW}
**Intent**: ${INTENT_ID}
**Checkpoint**: ${CHECKPOINT_ID}
**Reason**: Describe rollback trigger
**Status**: pending

### State Restored
- Document restored state here.

### Recovery Outcome
- Recovery time:
- Data loss:
- Execution resumed:

### Lessons
- Capture rollback-specific insights here.

---
EOF

cat > "$TARGET_DIR/.agent/learnings/${LEARNING_ID}.md" <<EOF
## [${LEARNING_ID}] learning_category

**Logged**: ${ISO_NOW}
**Intent**: ${INTENT_ID}
**Outcome**: partial
**Status**: pending

### What Was Learned
Describe the reusable pattern, failure mode, or safeguard.

### Evidence
- Success rate:
- Execution time:
- Actions taken:
- Checkpoints created:
- Rollbacks:

### Strategy Impact
Describe how future runs should change.

### Application Scope
- Task types:
- Risk levels:
- Conditions:

### Safety Check
- Complexity:
- Performance:
- Risk:

---
EOF

cat > "$TARGET_DIR/.agent/learnings/STRATEGIES.md" <<EOF
# Strategy Registry

---

## [${STRATEGY_ID}] strategy_name

**Created**: ${ISO_NOW}
**Status**: testing
**Source Learning**: ${LEARNING_ID}
**Domain**: file_processing
**Version**: 1.0.0

### Strategy
Describe the candidate strategy here.

### Expected Benefit
- Lower violation rate
- Improved safety
- Better task completion quality

### Evidence
- Sample size: 0
- Violation prevented: pending
- Rollback-assisted recovery: pending
- Outcome after correction: pending

### Rollout Guidance
- Start with limited use
- Reevaluate after more runs

---
EOF

echo "Scaffolded run folder at: $TARGET_DIR"
echo "Intent: $INTENT_ID"
