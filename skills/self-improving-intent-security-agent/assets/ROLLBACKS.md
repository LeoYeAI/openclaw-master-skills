# Rollback Operations Log

Track checkpoint restorations and their outcomes.

---

## [RBK-YYYYMMDD-XXX] checkpoint_id

**Executed**: 2025-01-15T14:00:00Z
**Intent**: INT-20250115-001
**Trigger**: automatic | manual | on_violation | on_anomaly
**Status**: completed | partial | failed

### Reason
Why rollback was necessary (violation, anomaly, user request, etc.)

### Checkpoint Details
- Checkpoint ID: CHK-20250115-001
- Created: 2025-01-15T13:00:00Z
- Location: [description of state captured]
- Actions since checkpoint: [N]

### Actions Reversed
1. Action 1 name (reversed successfully) ✓
2. Action 2 name (reversed successfully) ✓
3. Action 3 name (reversal failed - manual intervention) ✗

### Reversal Methods
- File operations: [restored from backup | regenerated | manual]
- API calls: [compensating transaction | manual cleanup]
- State changes: [snapshot restore | incremental undo]

### Status
- [x] Fully restored to checkpoint state
- [ ] Partially restored (see notes below)
- [ ] Manual intervention required

### Post-Rollback State
- All constraints satisfied: yes | no
- Intent still achievable: yes | no | modified
- Next steps: [continue | abort | revise intent]

### Notes
Additional context about the rollback (challenges, manual steps, etc.)

### Metadata
- Violation: VIO-20250115-002 (if triggered by violation)
- Anomaly: ANO-20250115-003 (if triggered by anomaly)
- Duration: [time to complete rollback]
- Actions reversed: [N] successful, [N] failed

---
