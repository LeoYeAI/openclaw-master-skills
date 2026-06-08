# Claude Context: Self-Improving Intent Security Agent

This document provides context and guidelines for AI agents (Claude, Copilot, etc.) working on this project.

## Project Overview

**Type**: Claude Code Skill / OpenClaw Agent Skill
**Purpose**: Autonomous agent with intent-based security validation, real-time monitoring, and continuous self-improvement
**Repository**: https://github.com/nishantapatil3/self-improving-intent-security-agent
**Clawhub**: https://clawhub.ai/nishantapatil3/self-improving-intent-security-agent
**Documentation**: https://nishantapatil3.github.io/self-improving-intent-security-agent/

## Core Concept: Intent Security

Traditional security: "Do you have permission?"
**Intent security: "Should you do this for this goal?"**

Every action is validated against user-specified intent BEFORE execution. This prevents:
- Goal drift and misalignment
- Scope creep and mission expansion
- Unintended side effects
- Security violations

### Intent Specification Format

Intents are stored in `.agent/intents/` as markdown files:

```markdown
## [INT-YYYYMMDD-NNN] task_name

**Created**: ISO-8601 timestamp
**Risk Level**: low | medium | high
**Status**: active | completed | violated

### Goal
Clear, specific objective (what success looks like)

### Constraints
- Explicit boundaries (what NOT to do)
- Resource limits
- Privacy/security requirements

### Expected Behavior
- Anticipated actions
- Acceptable patterns
- Performance expectations

### Context
- Relevant files/directories
- Environment details
- Dependencies
```

## Architecture

```
User Intent → Validation → Authorization → Execution → Monitoring
                                              ↓
                                      Anomaly Detection
                                              ↓
                                   [Violation?] → Rollback
                                              ↓
                                       Outcome Analysis
                                              ↓
                                       Pattern Extraction
                                              ↓
                                      Strategy Evolution
```

### Key Components

1. **Intent Validator**: Pre-execution checks against intent spec
2. **Authorization Engine**: Multi-layer permission verification
3. **Execution Monitor**: Real-time behavioral monitoring
4. **Anomaly Detector**: Identifies goal drift, capability misuse, side effects
5. **Rollback Manager**: Checkpoint-based state restoration
6. **Outcome Analyzer**: Extracts insights from task results
7. **Pattern Extractor**: Identifies reusable successful approaches
8. **Strategy Optimizer**: A/B tests and evolves strategies
9. **Knowledge Store**: Persists learnings and strategies

## Directory Structure

```
.agent/
├── intents/           # Intent specifications (INT-*.md)
├── violations/        # Violation logs (VIO-*.md)
├── learnings/         # Extracted patterns and strategies
│   ├── LEARNINGS.md   # Learning records
│   └── STRATEGIES.md  # Evolved strategies
├── audit/             # Complete audit trail
└── config.json        # Configuration

scripts/
├── setup.sh           # Initialize agent structure
├── validate-intent.sh # Validate intent format
└── report.sh          # Generate activity reports

hooks/ (optional - create your own)
├── pre-action-hook.sh    # Run before actions (user-created)
└── post-action-hook.sh   # Run after actions (user-created)
```

## Development Guidelines

### When Adding Features

1. **Maintain Intent-First Approach**: All new features should validate against intent
2. **Preserve Safety Guarantees**: Don't bypass validation, rollback, or approval gates
3. **Keep Learning Bounded**: Self-modification must stay within guardrails
4. **Ensure Auditability**: Log all decisions and rationale

### Code Patterns

#### Validation Pattern
```bash
# Always validate before execution
./scripts/validate-intent.sh "$INTENT_FILE" || exit 1

# Check constraints
if ! check_constraints "$ACTION"; then
    log_violation "$ACTION" "$INTENT_ID"
    rollback_to_checkpoint
    exit 1
fi
```

#### Learning Pattern
```bash
# Record outcome
record_outcome() {
    local strategy="$1"
    local success="$2"
    local metrics="$3"

    echo "- Strategy: $strategy" >> .agent/learnings/LEARNINGS.md
    echo "  Success: $success" >> .agent/learnings/LEARNINGS.md
    echo "  Metrics: $metrics" >> .agent/learnings/LEARNINGS.md
}
```

#### Rollback Pattern
```bash
# Create checkpoint before risky operations
create_checkpoint() {
    local checkpoint_id="CP-$(date +%s)"
    # Save state...
    echo "$checkpoint_id"
}

# Rollback on violation
rollback_to_checkpoint() {
    local checkpoint_id="$1"
    # Restore state...
}
```

### Environment Variables

**Important**: All environment variables are **optional**. The skill works without any environment variables set, using sensible defaults.

**Security Note**: This skill does NOT require any credentials or secrets. All data stays local in the `.agent/` directory. No data is transmitted to external services.

#### Configuration Variables (All Optional)

```bash
# Paths (default to .agent/intents and .agent/audit)
AGENT_INTENT_PATH           # Path to intent specifications (default: .agent/intents)
AGENT_AUDIT_PATH            # Path to audit logs (default: .agent/audit)

# Security (optional tuning)
AGENT_RISK_THRESHOLD        # Risk threshold: low | medium | high (default: medium)
AGENT_AUTO_ROLLBACK         # Auto rollback on violations: true | false (default: true)
AGENT_ANOMALY_THRESHOLD     # Anomaly detection threshold: 0.0 - 1.0 (default: 0.8)

# Learning (optional tuning)
AGENT_LEARNING_ENABLED      # Enable self-improvement: true | false (default: true)
AGENT_MIN_SAMPLE_SIZE       # Min samples before learning: integer (default: 10)
AGENT_AB_TEST_RATIO         # A/B test ratio: 0.0 - 1.0 (default: 0.1)

# Monitoring (optional tuning)
AGENT_METRICS_INTERVAL      # Metrics interval in ms: integer (default: 1000)
AGENT_AUDIT_LEVEL           # Audit detail: minimal | standard | detailed (default: detailed)
```

## Testing Guidelines

### Test Intent Validation
```bash
# Create test intent
cat > test_intent.md <<'EOF'
## [INT-TEST-001] test_task
**Risk Level**: low
### Goal
Test validation logic
### Constraints
- No file deletions
EOF

# Validate format
./scripts/validate-intent.sh test_intent.md

# Test violation detection
# (should block and log)
```

### Test Learning Mechanism
```bash
# Run task multiple times with different strategies
# Verify patterns are extracted
# Confirm better strategies are adopted
grep "adopted" .agent/learnings/STRATEGIES.md
```

### Test Rollback
```bash
# Create checkpoint
# Make changes
# Trigger rollback
# Verify state restored
```

## File Format Specifications

### Intent File (INT-*.md)
- Naming: `INT-YYYYMMDD-NNN.md` (e.g., `INT-20250326-001.md`)
- Required fields: Goal, Constraints, Risk Level, Status
- Must be valid markdown
- Use ISO-8601 timestamps

### Violation File (VIO-*.md)
```markdown
## [VIO-YYYYMMDD-NNN] Violation Description

**Detected**: ISO-8601 timestamp
**Intent**: INT-YYYYMMDD-NNN
**Severity**: low | medium | high | critical

### Action Attempted
What was blocked

### Violation Type
- goal_drift | constraint_violation | capability_misuse | side_effect

### Rationale
Why this violated intent

### Rollback
- Checkpoint: CP-timestamp
- Status: success | failed
```

### Learning Record (LEARNINGS.md)
```markdown
## Pattern: pattern-name

**Extracted**: ISO-8601 timestamp
**Category**: strategy | antipattern | optimization
**Confidence**: 0.0 - 1.0

### Observation
What was observed across multiple executions

### Pattern
Identified reusable approach

### Evidence
- Sample size: N
- Success rate: X%
- Performance: metrics

### Application
When and how to apply this pattern
```

## Integration Points

### Claude Code Hooks (Optional)

Users can create custom hooks in a `hooks/` directory:

```json
{
  "hooks": {
    "beforeTool": "bash hooks/pre-action-hook.sh",
    "afterTool": "bash hooks/post-action-hook.sh"
  }
}
```

Note: Hooks are user-created and optional. This skill does not include default hooks.

### OpenClaw Integration
Uses `openclaw` field in `package.json` for skill metadata and installation.

### GitHub Actions
- `.github/workflows/pages.yml` - Deploys documentation to GitHub Pages
- Add `.github/workflows/test.yml` for CI/CD validation

## Common Tasks

### Adding a New Component
1. Ensure it validates against intent
2. Add audit logging
3. Implement rollback if stateful
4. Document in `references/`
5. Add examples to `examples/`

### Modifying Validation Logic
1. Update `scripts/validate-intent.sh`
2. Add tests for edge cases
3. Update `SKILL.md` documentation
4. Consider backward compatibility

### Enhancing Learning
1. Modify pattern extraction in learning module
2. Test with multiple sample scenarios
3. Verify safety guardrails still apply
4. Document new strategies in `references/self-improvement.md`

### Updating Documentation
1. Main docs in `SKILL.md`
2. Deep dives in `references/`
3. Practical examples in `examples/`
4. Keep README.md synchronized
5. GitHub Pages auto-deploys from `main`

## Safety Principles

### Always Enforce
1. **Intent Alignment**: Every action must serve stated goal
2. **Permission Boundaries**: Cannot exceed authorized scope
3. **Reversibility**: Must be able to rollback
4. **Auditability**: Complete transparency log
5. **Bounded Learning**: Self-modification within guardrails
6. **Human Oversight**: Approval gates for high-risk ops

### Never Do
- Skip intent validation
- Bypass approval gates for high-risk operations
- Modify safety guardrails without explicit user consent
- Learn patterns that violate constraints
- Execute without audit logging
- Disable rollback capability

## Debugging

### Check Intent Validity
```bash
./scripts/validate-intent.sh .agent/intents/INT-*.md
```

### Review Violations
```bash
cat .agent/violations/VIOLATIONS.md
grep "Severity**: high" .agent/violations/*.md
```

### Check Learning Progress
```bash
cat .agent/learnings/LEARNINGS.md
cat .agent/learnings/STRATEGIES.md
```

### Generate Report
```bash
./scripts/report.sh
```

### Audit Trail
```bash
ls -ltr .agent/audit/
tail -f .agent/audit/$(date +%Y%m%d).log
```

## Package Management

### Publishing to Clawhub

This repository includes automated publishing via GitHub Actions. See `PUBLISHING.md` for complete details.

**Quick release:**
```bash
npm version patch  # or minor, major
git push --follow-tags
gh release create v$(node -p "require('./package.json').version") --generate-notes
```

The GitHub Action (`.github/workflows/publish.yml`) automatically publishes on release.

**Required secrets** (configure in GitHub repo settings):
- `NPM_TOKEN` - For npm publishing (if Clawhub syncs from npm)
- `CLAWHUB_TOKEN` - For direct Clawhub publishing (if available)
- `CLAWHUB_WEBHOOK_URL` - For webhook-based publishing (if applicable)

### Version Strategy
- **Patch** (1.0.0 → 1.0.1): Bug fixes, documentation updates
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Major** (1.0.0 → 2.0.0): Breaking changes, architecture changes

See `PUBLISHING.md` for detailed publishing instructions and troubleshooting.

## Resources

- **SKILL.md**: User-facing skill documentation
- **references/**: Deep technical documentation
  - `architecture.md`: System design
  - `intent-security.md`: Security model
  - `self-improvement.md`: Learning mechanisms
  - `multi-agent.md`: Agent integrations
- **examples/**: Step-by-step walkthroughs
- **GitHub Issues**: Bug reports and feature requests
- **Clawhub**: Installation and discovery

## Contributing

When contributing to this project:
1. Read this file thoroughly
2. Understand the intent security model
3. Test with real intent specifications
4. Verify safety guarantees are maintained
5. Update documentation for any changes
6. Add examples for new features

---

## Clawhub Publishing & Security: Lessons Learned

This section documents critical learnings from publishing to Clawhub and passing security scans.

### Security Scan Triggers (What Gets Flagged)

The Clawhub security scanner (DinoScan) flags skills as "suspicious" with medium confidence for:

1. **Environment Variable Mismatches**
   - ❌ Declaring env vars as `required` in package.json but not actually using them in scripts
   - ❌ Documentation referencing env vars that scripts don't read
   - ✅ **Fix**: Declare all env vars as optional with defaults, document clearly they're configuration-only

2. **Missing/Inconsistent Directory References**
   - ❌ Referencing directories in package.json `files` array that don't exist (e.g., `hooks/`)
   - ❌ Documentation mentioning files/scripts that aren't included
   - ✅ **Fix**: Only list actual files/directories, mark optional features as "user-created"

3. **Base64-Encoded Content**
   - ❌ Base64 blobs in documentation (even legitimate image badges)
   - ❌ Any `base64 -d` or `echo "..." | base64 --decode` patterns in scripts
   - ✅ **Fix**: Use external image URLs (shields.io, img.shields.io) instead of inline base64 SVGs

4. **Script Security Concerns**
   - ❌ Scripts without clear comments explaining what they do
   - ❌ Scripts that could phone home (curl, wget, nc) without documentation
   - ❌ Scripts reading arbitrary system files outside project scope
   - ✅ **Fix**: Add header comments to all scripts clarifying: no credentials needed, local-only operation, no external transmission

5. **Credential/Secret Confusion**
   - ❌ Publishing docs mentioning tokens (NPM_TOKEN, CLAWHUB_TOKEN) without clarifying they're maintainer-only
   - ❌ Users might think they need to provide secrets to use the skill
   - ✅ **Fix**: Add prominent security notes: "No credentials required", "All data stays local", "Nothing transmitted externally"

### Publishing Best Practices

#### Before Publishing Checklist

```bash
# 1. Verify package.json accuracy
- [ ] Remove non-existent directories from "files" array
- [ ] Declare env vars as optional with defaults in config.env
- [ ] Add security notes in config.notes

# 2. Script hygiene
- [ ] Add header comments to all .sh files explaining:
      - What the script does
      - That no credentials are needed
      - That data stays local
      - That nothing is transmitted externally

# 3. Documentation clarity
- [ ] Mark ALL environment variables as "optional"
- [ ] Add security note: "No credentials or secrets required"
- [ ] Clarify publishing tokens are maintainer-only (not for users)
- [ ] Replace [your-org] placeholders with actual org name

# 4. Directory consistency
- [ ] Only reference directories that actually exist
- [ ] Mark optional/user-created features clearly
- [ ] Ensure SKILL.md, README.md, CLAUDE.md are synchronized
```

#### Version Publishing Command

```bash
# Increment version and publish
npm version patch  # or minor, major
git push --follow-tags
clawhub publish --version X.Y.Z --changelog "Clear description of changes" .
```

#### Writing Good Changelogs

Bad: "bug fixes"
Good: "Fix security scan issues: clarify all environment variables are optional (not required), add security notes documenting no credentials needed and no data transmitted externally"

### Security Scan Response Pattern

When security scan flags your skill:

1. **Read the full scan report** - identifies specific triggers
2. **Check each flagged item**:
   - Base64 blocks → Replace with external image URLs
   - Missing directories → Remove from files array or create them
   - Env var mismatches → Mark as optional, add defaults
   - Script concerns → Add clarifying comments
3. **Commit fixes** with clear message explaining what was fixed
4. **Publish new version** with changelog referencing security improvements
5. **Wait for rescan** - VirusTotal + OpenClaw scan runs automatically

### What Clawhub Security Scans For

Based on Clawhub security documentation and issues:

| Category | Triggers | Severity |
|----------|----------|----------|
| Obfuscated code | base64 decode, eval, exec patterns | Critical |
| Network calls | curl, wget, nc without documentation | High |
| Credential requests | Asking for tokens/secrets at runtime | High |
| File system abuse | Reading /etc, ~/.ssh, system files | Critical |
| Env var mismatches | Declared required but not used | Medium |
| Missing files | Referenced but not included | Medium |
| Prompt injection | User input passed to shell without escaping | High |

### Trust Signals for Users

Skills that pass security scans should display:
- ✅ Clear purpose (name/description match functionality)
- ✅ Minimal permissions (only what's actually needed)
- ✅ Transparent operation (comments in scripts, clear docs)
- ✅ Local-only data (no external transmission)
- ✅ No credential requirements for runtime use

---

## Questions?

If you're unsure about something:
1. Check existing intent specifications in `examples/`
2. Review violation logs for similar cases
3. Consult `references/intent-security.md`
4. Look at learning patterns in `.agent/learnings/`
5. Check GitHub issues for discussions

---

**Remember**: Intent security is about alignment, not just permission. Every decision should serve the user's stated goal while respecting constraints. When in doubt, validate against intent and ask for clarification.
