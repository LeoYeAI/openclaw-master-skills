---
name: self-improving-intent-security-agent
description: "Documentation-first skill and workflow toolkit for intent-based security. Provides templates, examples, and local helper scripts for capturing intent, reviewing actions, documenting rollbacks, and recording learnings. Use when: (1) designing or prototyping intent validation workflows, (2) documenting high-risk operations, (3) creating audit trails and rollback records, (4) building your own runtime enforcement layer."
---

# Self-Improving Intent Security Agent

## Install

```bash
npx skills add nishantapatil3/self-improving-intent-security-agent
```

Use this skill to structure and document intent validation workflows. It does not ship a production runtime engine that automatically intercepts agent actions; instead, it provides templates, examples, and local scripts that help you build, simulate, or document that workflow.

## Scope Clarification

- This package includes markdown templates, examples, and helper shell scripts
- The helper shell scripts operate on local files only
- Automatic enforcement, anomaly detection, rollback execution, and learning application must be implemented by the host agent or surrounding system

## Quick Reference

| Situation | Action |
|-----------|--------|
| Starting autonomous task | Capture intent specification (goal, constraints, expected behavior) |
| Before each action | Validate against intent, check authorization |
| Action violates intent | Document the violation and follow the rollback workflow |
| Unusual behavior detected | Log an anomaly, assess severity, and decide whether to halt or roll back |
| Task completes | Analyze outcome, extract patterns, update strategies |
| High-risk operation | Require human approval before execution |
| Need transparency | Review audit log with full action history |
| Strategy improves | A/B test new approach, adopt if better |
| Recurring violation | Promote to permanent constraint in CLAUDE.md |

## Setup

Create `.agent/` directory in project root:

```bash
mkdir -p .agent/{intents,violations,learnings,audit}
```

Copy templates from `assets/` or create files with headers. Review the included shell scripts before running them if you want to understand exactly what they do.

For a complete conversation-driven working folder, scaffold a run pack:

```bash
./scripts/scaffold-run.sh examples/my-demo customer_feedback medium
```

This creates:
- `conversation.md` for the user/agent transcript
- `report.md` for the final summary
- a local `.agent/` tree with intent, audit, violation, rollback, learning, and strategy files

## Intent Specification Format

Before executing autonomous tasks, capture structured intent:

```markdown
## [INT-YYYYMMDD-XXX] task_name

**Created**: ISO-8601 timestamp
**Risk Level**: low | medium | high
**Status**: active | completed | violated

### Goal
What you want to achieve (single clear objective)

### Constraints
- Boundary 1 (e.g., "Only modify files in ./src")
- Boundary 2 (e.g., "Do not make network calls")
- Boundary 3 (e.g., "Preserve existing test coverage")

### Expected Behavior
- Pattern 1 (e.g., "Read files before modifying")
- Pattern 2 (e.g., "Run tests after changes")
- Pattern 3 (e.g., "Create backups of modified files")

### Context
- Relevant files: path/to/file.ext
- Environment: development | staging | production
- Previous attempts: INT-20250115-001 (if retry)

---
```

Save to `.agent/intents/INT-YYYYMMDD-XXX.md`.

## Validation Workflow

## Conversation-Driven Workflow

Use this when you want the skill to document not just the intent, but the full user and agent interaction over time.

### Recommended Sequence

1. Capture the user request in `conversation.md`
2. Translate it into a structured intent in `.agent/intents/`
3. Record allowed and blocked actions in `.agent/audit/`
4. Log suspicious behavior in `.agent/violations/ANOMALIES.md`
5. Log hard validation failures in `.agent/violations/`
6. Record recovery steps in `.agent/audit/ROLLBACKS.md`
7. Extract reusable learnings in `.agent/learnings/`
8. Promote stable improvements into `.agent/learnings/STRATEGIES.md`
9. Summarize the run in `report.md`

### Good Fit

- High-risk or privacy-sensitive tasks
- Tasks where you need a human-readable transcript
- Demos and evaluations
- Incident reviews and postmortems

### Example

See `examples/customer-feedback-demo/` for a full run showing:
- intent capture
- per-action validation
- anomaly detection
- blocked violation
- rollback
- learning promotion

### Pre-Execution Validation

Before each action, validate:

1. **Goal Alignment**: Does this action serve the stated goal?
2. **Constraint Check**: Does it respect all boundaries?
3. **Behavior Match**: Does it fit expected patterns?
4. **Authorization**: Do we have permission for this?

If ANY check fails → block action, log violation.

### Example Validation

```yaml
Intent: "Process customer feedback files"
Constraints: ["Only read ./feedback", "No file modifications"]

Action: "delete ./feedback/temp.txt"
Validation:
  - Goal Alignment: ❌ Deleting isn't "processing"
  - Constraint Check: ❌ Violates "no modifications"
  - Behavior Match: ❌ Not expected for this task
  - Authorization: ✓ (but blocked by other checks)

Result: BLOCKED → Log violation → Consider rollback
```

## Logging Violations

When validation fails, log to `.agent/violations/`:

```markdown
## [VIO-YYYYMMDD-XXX] violation_type

**Logged**: ISO-8601 timestamp
**Severity**: low | medium | high | critical
**Intent**: INT-20250115-001
**Status**: pending_review

### What Happened
Action that was attempted

### Validation Failures
- Goal Alignment: [reason]
- Constraint Check: [which constraint violated]
- Behavior Match: [how it deviated]

### Action Taken
- [ ] Action blocked
- [ ] Checkpoint rollback
- [ ] Alert sent
- [ ] Execution halted

### Root Cause
Why the agent attempted this (if analyzable)

### Prevention
How to prevent this in the future

### Metadata
- Related Intent: INT-20250115-001
- Action Type: file_delete | api_call | command_execution
- Risk Level: high
- See Also: VIO-20250110-002 (if recurring)

---
```

## Anomaly Detection

Monitor execution for behavioral anomalies:

### Anomaly Types

| Type | Description | Response |
|------|-------------|----------|
| **Goal Drift** | Actions diverging from stated goal | Halt, request clarification |
| **Capability Misuse** | Using tools inappropriately | Rollback to checkpoint |
| **Side Effects** | Unexpected consequences detected | Log warning, continue with monitoring |
| **Resource Exceeded** | CPU/memory/time limits breached | Throttle or halt |
| **Pattern Deviation** | Behavior differs from expected | Log for analysis |

### Anomaly Logging

Log to `.agent/violations/ANOMALIES.md`:

```markdown
## [ANO-YYYYMMDD-XXX] anomaly_type

**Detected**: ISO-8601 timestamp
**Severity**: low | medium | high
**Intent**: INT-20250115-001

### Anomaly Details
What unusual behavior was detected

### Evidence
- Metric that triggered alert
- Baseline vs. actual values
- Timeline of deviation

### Assessment
Why this is anomalous

### Response Taken
- [ ] Continued with monitoring
- [ ] Applied constraints
- [ ] Rolled back
- [ ] Halted execution

---
```

## Learning Workflow

After task completion, log learnings to `.agent/learnings/`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Intent**: INT-20250115-001
**Outcome**: success | failure | partial

### What Was Learned
Pattern or insight discovered

### Evidence
- Success rate: 95%
- Execution time: 2.3s
- Actions taken: 15
- Checkpoints: 3

### Strategy Impact
How this affects future executions

### Application Scope
- Tasks: file_processing, data_transformation
- Risk Levels: low, medium
- Conditions: when X and Y are true

### Safety Check
- Complexity: low | medium | high
- Performance: baseline_comparison
- Risk: assessment

### Metadata
- Category: pattern | optimization | error_handling | security
- Confidence: low | medium | high
- Sample Size: N tasks observed
- Pattern-Key: file.batch_processing (if recurring)

---
```

## Rollback Operations

### Creating Checkpoints

Before risky operations:

```typescript
const checkpoint = await agent.checkpoint.create({
  intent: currentIntent,
  reason: "Before bulk file operations"
});
```

### Rollback on Violation

Automatic rollback when intent violated:

```typescript
// Happens automatically, but can also trigger manually:
await agent.rollback.restore(checkpointId, {
  reason: "Detected constraint violation",
  notify: true
});
```

### Rollback Log

Track in `.agent/audit/ROLLBACKS.md`:

```markdown
## [RBK-YYYYMMDD-XXX] checkpoint_id

**Executed**: ISO-8601 timestamp
**Intent**: INT-20250115-001
**Trigger**: automatic | manual

### Reason
Why rollback was necessary

### Actions Reversed
- Action 1 (reversed successfully)
- Action 2 (reversed successfully)
- Action 3 (reversal failed - manual intervention needed)

### Checkpoint Restored
- Checkpoint: CHK-20250115-001
- Created: 2025-01-15T10:00:00Z
- Actions since checkpoint: 15

### Status
- [ ] Fully restored
- [ ] Partially restored (see notes)
- [ ] Manual intervention required

---
```

## Strategy Evolution

When agent learns better approaches:

### A/B Testing

1. **Baseline**: Current strategy (90% of tasks)
2. **Candidate**: New strategy (10% of tasks)
3. **Measure**: Compare success rate, time, resource usage
4. **Validate**: Safety checks pass
5. **Adopt**: Roll out if candidate is 10%+ better
6. **Rollback**: Revert if candidate degrades performance

### Strategy Log

Track in `.agent/learnings/STRATEGIES.md`:

```markdown
## [STR-YYYYMMDD-XXX] strategy_name

**Created**: ISO-8601 timestamp
**Domain**: file_processing | api_interaction | error_handling
**Status**: testing | adopted | rejected | superseded

### Approach
What this strategy does differently

### Performance
- Baseline: 85% success, 3.2s avg
- Candidate: 92% success, 2.1s avg
- Improvement: +7% success, -34% time

### A/B Test Results
- Test Tasks: 50
- Candidate Used: 5 tasks
- Wins: 4, Losses: 1, Ties: 0

### Safety Validation
- Complexity: within limits (complexity: 45/100)
- Permissions: no expansion
- Risk: acceptable (no high-risk changes)

### Adoption Decision
- [ ] Adopt (outperforms baseline)
- [ ] Reject (underperforms baseline)
- [ ] Extend testing (inconclusive)

---
```

## Promoting to Permanent Memory

When learnings are broadly applicable, promote to project files:

### Promotion Targets

| Target | What Belongs There |
|--------|-------------------|
| `CLAUDE.md` | Intent patterns, common constraints for this project |
| `AGENTS.md` | Agent-specific workflows, validation rules |
| `.github/copilot-instructions.md` | Security guidelines, constraint templates |
| `SECURITY.md` | Security-critical constraints and validation rules |

### When to Promote

Promote when:
- Violation occurs 3+ times (recurring constraint)
- Learning applies across multiple task types
- Strategy is adopted and proven (success rate 90%+)
- Security pattern prevents entire class of violations

### Promotion Examples

**Violation** (recurring):
> VIO-20250115-001: Attempted to modify files outside ./src
> VIO-20250118-002: Attempted to modify files outside ./src
> VIO-20250120-003: Attempted to modify files outside ./src

**Promote to CLAUDE.md**:
```markdown
## File Modification Constraints
- Only modify files within `./src` directory
- Other directories are read-only unless explicitly authorized
```

**Learning** (proven strategy):
> LRN-20250115-005: Batch processing with checkpoints every 10 files
> Results: 95% success, 40% faster, easy rollback on failures

**Promote to AGENTS.md**:
```markdown
## File Processing Strategy
- Use batch processing (10 files per batch)
- Create checkpoint before each batch
- Enables fast rollback on errors
```

## Configuration

### Environment Variables

**Important**: All environment variables are **optional**. The skill works with sensible defaults without any configuration.

**Security Note**: This skill does NOT require any credentials or secrets. All data stays local in the `.agent/` directory. No data is transmitted externally.

```bash
# Paths (optional - defaults shown)
export AGENT_INTENT_PATH=".agent/intents"       # Default: .agent/intents
export AGENT_AUDIT_PATH=".agent/audit"          # Default: .agent/audit

# Security Settings (optional tuning)
export AGENT_RISK_THRESHOLD="medium"            # low | medium | high
export AGENT_AUTO_ROLLBACK="true"               # true | false
export AGENT_ANOMALY_THRESHOLD="0.8"            # 0.0 - 1.0

# Learning Settings (optional tuning)
export AGENT_LEARNING_ENABLED="true"            # true | false
export AGENT_MIN_SAMPLE_SIZE="10"               # Min observations before adopting
export AGENT_AB_TEST_RATIO="0.1"                # 10% of tasks for A/B testing

# Monitoring (optional tuning)
export AGENT_METRICS_INTERVAL="1000"            # Metrics collection (ms)
export AGENT_AUDIT_LEVEL="detailed"             # minimal | standard | detailed
```

### Configuration File

Create `.agent/config.json`:

```json
{
  "security": {
    "requireApproval": ["file_delete", "api_write", "command_execution"],
    "autoRollback": true,
    "anomalyThreshold": 0.8,
    "maxPermissionScope": "read-write"
  },
  "learning": {
    "enabled": true,
    "minSampleSize": 10,
    "abTestRatio": 0.1,
    "maxStrategyComplexity": 100
  },
  "monitoring": {
    "metricsInterval": 1000,
    "auditLevel": "detailed",
    "retentionDays": 90
  }
}
```

## ID Generation

Format: `TYPE-YYYYMMDD-XXX`
- `INT`: Intent specification
- `VIO`: Violation (failed validation)
- `ANO`: Anomaly (behavioral deviation)
- `LRN`: Learning (insight from execution)
- `STR`: Strategy (new approach)
- `RBK`: Rollback operation
- `CHK`: Checkpoint

Examples: `INT-20250115-001`, `VIO-20250115-A3F`, `LRN-20250115-002`

## Priority Guidelines

| Priority/Severity | When to Use |
|-------------------|-------------|
| `critical` | Immediate security risk, data loss, system compromise |
| `high` | Intent violation, unauthorized action, goal drift |
| `medium` | Anomaly detected, suboptimal strategy, warning condition |
| `low` | Minor deviation, optimization opportunity, observation |

## Best Practices

### Intent Specification
1. **Be specific** - Vague goals lead to validation failures
2. **List all constraints** - Implicit boundaries often get violated
3. **Define expected behavior** - Helps catch deviations early
4. **Set correct risk level** - Triggers appropriate approval gates

### Validation
1. **Validate early** - Before execution, not after
2. **Fail safe** - Block on doubt, don't assume permission
3. **Log all violations** - Even if they seem minor
4. **Review regularly** - Patterns emerge over time

### Learning
1. **Let it learn** - Requires sample size to be effective
2. **Monitor A/B tests** - Don't adopt blindly
3. **Safety first** - Reject strategies that reduce safety
4. **Promote proven patterns** - Turn learnings into permanent rules

### Audit
1. **Keep detailed logs** - Debugging requires context
2. **Archive old logs** - Retention policies prevent bloat
3. **Review anomalies** - Often reveal edge cases
4. **Share learnings** - Team benefits from documented patterns

## Detection Triggers

Automatically apply intent security when:

**High-Risk Operations**:
- File deletion or bulk modifications
- API calls with write permissions
- Command execution with elevated privileges
- Database modifications
- Deployment operations

**Autonomous Workflows**:
- Multi-step task sequences
- Background job execution
- Scheduled automation
- Agent-initiated operations

**Learning Opportunities**:
- Task completes successfully
- Failure with identifiable cause
- User provides correction
- Better approach discovered

## Hook Integration (Optional)

Enable automatic intent validation through agent hooks.

### Setup (Claude Code / Codex)

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improving-intent-security-agent/scripts/intent-capture.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash|Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improving-intent-security-agent/scripts/action-validator.sh"
      }]
    }]
  }
}
```

### Available Hook Scripts

| Script | Hook Type | Purpose |
|--------|-----------|---------|
| `scripts/intent-capture.sh` | UserPromptSubmit | Prompts for intent specification |
| `scripts/action-validator.sh` | PostToolUse | Validates actions against intent |
| `scripts/learning-capture.sh` | TaskComplete | Captures learnings after tasks |

See `references/hooks-setup.md` for detailed configuration.

## Quick Commands

```bash
# Initialize agent structure
mkdir -p .agent/{intents,violations,learnings,audit}

# Count active intents
grep -h "Status**: active" .agent/intents/*.md | wc -l

# List high-severity violations
grep -B5 "Severity**: high" .agent/violations/*.md | grep "^## \["

# Find learnings for file processing
grep -l "Domain**: file_processing" .agent/learnings/*.md

# Review recent rollbacks
ls -lt .agent/audit/ROLLBACKS.md | head -5

# Check strategy adoption rate
grep "Status**: adopted" .agent/learnings/STRATEGIES.md | wc -l
```

## Examples

See [examples/README.md](examples/README.md) for detailed usage examples:
- Basic intent specification and validation
- Handling violations and rollbacks
- Learning from task outcomes
- Strategy evolution through A/B testing
- Security monitoring and anomaly detection

## References

- [Architecture](references/architecture.md) - System design and components
- [Intent Security](references/intent-security.md) - Validation and authorization
- [Self-Improvement](references/self-improvement.md) - Learning mechanisms
- [Hooks Setup](references/hooks-setup.md) - Automation configuration
- [API Reference](references/api.md) - Programmatic usage

## Multi-Agent Support

Works with Claude Code, Codex CLI, GitHub Copilot, and OpenClaw. See `references/multi-agent.md` for agent-specific configurations.

## Safety Guarantees

✓ Intent Alignment - Every action validated against goal
✓ Permission Boundaries - Cannot exceed authorized scope
✓ Reversibility - Checkpoint-based rollback
✓ Auditability - Complete action history
✓ Bounded Learning - Safety-constrained improvements
✓ Human Oversight - Approval gates for high-risk operations

## License

MIT

---

**Note**: This skill provides strong safety mechanisms but requires proper configuration and usage. Always:
- Define clear, specific intents
- Review violation logs regularly
- Monitor learning effectiveness
- Keep approval gates enabled for high-risk operations
- Test in non-production environments first

**Intent-based security is a powerful approach, but human judgment remains essential.**
