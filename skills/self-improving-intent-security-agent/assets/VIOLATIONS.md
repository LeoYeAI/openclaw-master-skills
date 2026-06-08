# Intent Violations

Log actions that failed validation or violated user intent.

---

## [VIO-YYYYMMDD-XXX] violation_type

**Logged**: 2025-01-15T10:30:00Z
**Severity**: low | medium | high | critical
**Intent**: INT-20250115-001
**Status**: pending_review | resolved | wont_fix

### What Happened
Describe the action that was attempted

### Validation Failures
- Goal Alignment: [why action didn't serve the goal]
- Constraint Check: [which constraint was violated]
- Behavior Match: [how it deviated from expected]
- Authorization: [permission issue if any]

### Action Taken
- [x] Action blocked
- [ ] Checkpoint rollback
- [ ] Alert sent
- [ ] Execution halted

### Root Cause
Why the agent attempted this (analysis)

### Prevention
How to prevent this in the future

### Metadata
- Related Intent: INT-20250115-001
- Action Type: file_delete | api_call | command_execution | other
- Risk Level: low | medium | high | critical
- See Also: VIO-20250110-002 (if recurring)

---
