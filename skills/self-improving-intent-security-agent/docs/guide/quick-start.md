---
layout: default
title: Quick Start
parent: Guide
nav_order: 2
---

# Quick Start Guide
{: .no_toc }

Get up and running with Intent Security Agent in 5 minutes.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Installation

### Option 1: NPM Package (Recommended)

```bash
# Install skill
npx skills add nispatil/self-improving-intent-security-agent
```

### Option 2: Clone Repository

```bash
# Clone repository
git clone https://github.com/nispatil/self-improving-intent-security-agent.git
cd self-improving-intent-security-agent

# Run setup script
./scripts/setup.sh
```

---

## Basic Setup

### 1. Create Directory Structure

```bash
# Create agent directories
mkdir -p .agent/{intents,violations,learnings,audit}
```

### 2. Set Environment Variables

```bash
# Required
export AGENT_INTENT_PATH=".agent/intents"
export AGENT_AUDIT_PATH=".agent/audit"

# Optional (with defaults shown)
export AGENT_RISK_THRESHOLD="medium"              # low | medium | high
export AGENT_REQUIRE_APPROVAL_HIGH_RISK="true"
export AGENT_AUTO_ROLLBACK="true"
export AGENT_LEARNING_ENABLED="true"
export AGENT_ANOMALY_THRESHOLD="0.8"
```

### 3. Create Your First Intent

```bash
# Create intent specification
cat > .agent/intents/INT-$(date +%Y%m%d)-001.md <<'EOF'
## [INT-$(date +%Y%m%d)-001] my_first_task

**Created**: $(date -Iseconds)
**Risk Level**: low
**Status**: active

### Goal
Process customer feedback files and extract sentiment

### Constraints
- Only read files in ./feedback directory
- Do not modify original files
- Respect PII privacy rules

### Expected Behavior
- Read files sequentially
- Apply analysis
- Generate summary report

### Context
- Relevant files: ./feedback/*.txt
- Environment: development
EOF
```

### 4. Or Scaffold a Full Run Folder

If you want a transcript, report, and `.agent` artifacts together:

```bash
./scripts/scaffold-run.sh examples/my-demo customer_feedback medium
```

This creates:
- `conversation.md`
- `report.md`
- `.agent/intents/...`
- `.agent/audit/...`
- `.agent/violations/...`
- `.agent/learnings/...`

---

## Your First Validation

### Create Test Files

```bash
# Create feedback directory
mkdir -p feedback

# Add sample feedback file
cat > feedback/customer_001.txt <<'EOF'
Great product! Very satisfied with the service.
EOF

cat > feedback/customer_002.txt <<'EOF'
Had some issues initially, but support team was helpful.
EOF
```

### Example: Allowed Action

```yaml
Action: Read ./feedback/customer_001.txt

Validation:
  Goal Alignment: ✓ (reading for processing)
  Constraints: ✓ (read-only, correct directory)
  Behavior: ✓ (sequential reading as expected)
  Authorization: ✓ (read permission)

Result: ALLOWED → Execute
```

### Example: Blocked Action

```yaml
Action: Delete ./feedback/customer_001.txt

Validation:
  Goal Alignment: ✗ (deletion not part of processing)
  Constraints: ✗ (violates "do not modify")
  Behavior: ✗ (deletion not expected)

Result: BLOCKED → Logged to VIO-xxx.md
```

---

## Review Outcomes

### Check for Violations

```bash
# View violations
cat .agent/violations/VIOLATIONS.md

# Find high-severity violations
grep -l "Severity**: high" .agent/violations/*.md
```

### Check Learnings

```bash
# View learnings
cat .agent/learnings/LEARNINGS.md

# View evolved strategies
cat .agent/learnings/STRATEGIES.md
```

### Generate Report

```bash
# Run report script
./scripts/report.sh

# Output shows:
# - Active intents
# - Recent violations
# - Learning progress
# - Success metrics
```

---

## Configuration File (Optional)

Create `.agent/config.json` for advanced configuration:

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

---

## Utilities

### Validate Intent Format

```bash
# Validate intent specification
./scripts/validate-intent.sh .agent/intents/INT-20250325-001.md

# Output: ✓ Valid or ✗ Errors with details
```

### Activity Report

```bash
# Generate activity summary
./scripts/report.sh

# Example output:
# ═══════════════════════════════════════
#  Intent Security Agent - Activity Report
# ═══════════════════════════════════════
#
# Active Intents: 3
# Total Violations: 12 (2 high, 5 medium, 5 low)
# Learnings Extracted: 8
# Strategies Evolved: 3
# Success Rate: 87%
```

### Scaffold a Conversation-Driven Run

```bash
./scripts/scaffold-run.sh examples/privacy-review pii_redaction high
```

Use this when you want a realistic working folder that captures:
- the user and agent conversation
- the formal intent
- the audit log
- anomaly and violation handling
- rollback steps
- post-run learning and strategy evolution

---

## Integration with AI Agents

### Claude Code

Add to `.claude/hooks.json`:
```json
{
  "before_action": "bash ./scripts/validate-intent.sh"
}
```

### OpenClaw

Skill automatically integrates when installed via `npx skills add`.

### GitHub Copilot

Manual integration - use validation scripts before committing actions.

---

## Next Steps

Now that you have the basics:

1. **[View Demo Walkthrough](/self-improving-intent-security-agent/demo/walkthrough)** - Interactive step-by-step examples
2. **[Read Architecture](/self-improving-intent-security-agent/reference/architecture)** - Understand system design
3. **[Explore Examples](https://github.com/nispatil/self-improving-intent-security-agent/tree/main/examples)** - Real-world scenarios
4. **[Join Discussions](https://github.com/nispatil/self-improving-intent-security-agent/discussions)** - Ask questions, share experiences

---

## Troubleshooting

### Issue: Validation not working

**Check**:
- Environment variables set correctly?
- Intent file format valid? (run `validate-intent.sh`)
- Directory structure created? (`.agent/intents` exists?)

### Issue: No learnings extracted

**Check**:
- `AGENT_LEARNING_ENABLED="true"`?
- Minimum sample size reached? (default: 10 tasks)
- Task outcomes logged properly?

### Issue: Rollback not triggered

**Check**:
- `AGENT_AUTO_ROLLBACK="true"`?
- Checkpoints being created?
- Violation detected and logged?

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/nispatil/self-improving-intent-security-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nispatil/self-improving-intent-security-agent/discussions)
- **Documentation**: [Full Reference](/self-improving-intent-security-agent/reference/architecture)
