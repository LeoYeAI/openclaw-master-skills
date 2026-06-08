# Anomaly Detection Log

Track unusual behavioral patterns detected during execution.

---

## [ANO-YYYYMMDD-XXX] anomaly_type

**Detected**: 2025-01-15T11:00:00Z
**Severity**: low | medium | high | critical
**Intent**: INT-20250115-001
**Status**: resolved | monitoring | escalated

### Anomaly Details
What unusual behavior was detected

### Evidence
- Metric that triggered alert: [metric_name]
- Baseline value: [expected]
- Actual value: [observed]
- Deviation: [percentage or absolute]
- Timeline: Started at [timestamp], detected at [timestamp]

### Assessment
Why this is anomalous (context and analysis)

### Type
- [ ] Goal Drift (actions diverging from stated goal)
- [ ] Capability Misuse (tools used inappropriately)
- [ ] Side Effects (unexpected consequences)
- [ ] Resource Exceeded (CPU/memory/time limits)
- [ ] Pattern Deviation (behavior differs from expected)

### Response Taken
- [ ] Continued with monitoring
- [ ] Applied constraints
- [ ] Rolled back to checkpoint
- [ ] Halted execution
- [ ] Requested clarification

### Metadata
- Related Intent: INT-20250115-001
- Threshold: [value]
- False Positive: yes | no | unknown
- See Also: ANO-20250112-001 (if related)

---
