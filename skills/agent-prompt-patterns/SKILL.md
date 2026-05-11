---
name: agent-prompt-patterns
description: 'Battle-tested prompt patterns for production AI agents. Covers consumer-first design, deletion test, cascading validation, advisory mode tiers, proof-of-work enforcement, heartbeat protocol, contradiction detection, WAL protocol, rule escalation ladder, and cross-validation patterns. Use when designing agent behavior, enforcing reliability, or building agent operating manuals.'
license: MIT
metadata:
  openclaw:
    emoji: '🎯'
---

# Agent Prompt Patterns

> Battle-tested patterns for agents that ship, not agents that demo.
> If your agent works in a live-fire notebook but breaks in production, you have a demo, not an agent.

---

## When to Use

- Designing a new agent's behavioral rules and operating manual
- An agent is hallucinating completions, skipping steps, or claiming work it didn't do
- Building multi-agent pipelines where output quality compounds (or collapses)
- Setting up human-in-the-loop approval tiers for different risk levels
- Enforcing reliability in automated workflows (cron jobs, scheduled tasks, pipelines)
- Writing AGENTS.md or operating manuals for production agent workspaces
- Debugging why an agent keeps violating rules you've already stated
- Evaluating whether an agent should exist at all (deletion test)
- Building harnesses that make autonomy safe and useful

## When NOT to Use

- One-shot prompts with no agent persistence — these patterns assume continuity
- Pure chatbot / conversational UX with no action-taking capability
- Academic prompt engineering research — these are production patterns, not benchmarks
- Agents with no filesystem, no tool access, and no side effects — nothing to harness
- You're still in the "make it work at all" phase — get basic functionality first, then harden

---

## 1. Consumer-First Design

**Principle:** Every agent output must have a named consumer. If nobody uses the output, the agent shouldn't exist.

This is the most important pattern because it kills bloat before it starts. Agents proliferate. Each one feels useful when you build it. Six months later you have 14 agents and can't remember what half of them do.

### The Deletion Test

Ask: *If I delete this agent, which other agent's work breaks?*

If the answer is "nothing" or "I'm not sure," the agent is a vanity project.

```markdown
# Agent Registry (in AGENTS.md)

## daily-digest
- **Consumers:** Sam (morning briefing), weekly-report agent (aggregation)
- **Deletion impact:** Sam loses morning summary, weekly-report loses daily inputs
- **Verdict:** KEEP

## inbox-sorter
- **Consumers:** None identified
- **Deletion impact:** Unknown
- **Verdict:** CANDIDATE FOR REMOVAL — validate or kill within 7 days
```

### How to Apply

Every agent entry in your operating manual should answer:

1. **Who consumes this output?** (name the human or agent)
2. **What format do they need?** (not what's convenient to produce)
3. **What breaks if this stops?** (the deletion test)
4. **What's the feedback loop?** (how does the consumer signal quality issues?)

If an agent produces beautiful summaries that nobody reads, it's burning tokens for nothing.

### Anti-Pattern: The "Nice to Have" Agent

```markdown
# BAD: No consumer, no deletion impact
## sentiment-tracker
Monitors social media sentiment about our brand.
Runs daily. Outputs to sentiment-log.md.

# GOOD: Named consumer, clear dependency
## sentiment-tracker
Monitors social media sentiment for weekly-report.
Consumer: weekly-report agent (pulls sentiment delta for executive summary)
Deletion impact: weekly-report loses sentiment section; Sam must manually check socials
Format: JSON with {platform, score_delta, top_mentions[3]}
```

---

## 2. Proof-of-Work Enforcement

**Principle:** Never claim done unless the action actually started. Every status update needs proof — PID, file path, URL, command output. No proof = didn't happen. Write first, speak second.

This pattern exists because LLMs are pathological completers. They want to say "Done!" because that's the satisfying end of a sequence. The problem is they'll say "Done!" before doing anything, or after attempting something that silently failed.

### The Rule

```
STATUS UPDATE FORMAT:
- "Started X" → must include: PID, command, or file path
- "Completed X" → must include: output snippet, file path, or URL
- "Failed X" → must include: error message, what was tried
- "Skipped X" → must include: reason with evidence
```

### Examples

```markdown
# BAD: No proof
✅ Backed up database
✅ Sent daily digest email
✅ Rotated API keys

# GOOD: Every claim has evidence
✅ Backed up database → /backups/2026-03-15-db.sql.gz (43MB, sha256: a1b2c3...)
✅ Sent daily digest → Message-ID: <abc123@mail.example.com>, 3 recipients
✅ Rotated API keys → new key fingerprint: sk-...x4f2, old key revoked at 14:32 UTC
```

### Implementation Pattern

```bash
# In a script gate or agent wrapper:
run_with_proof() {
  local task="$1"
  shift
  local output
  output=$("$@" 2>&1)
  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    echo "DONE: $task | proof: $(echo "$output" | tail -3)"
  else
    echo "FAIL: $task | exit=$exit_code | error: $(echo "$output" | tail -5)"
  fi
  return $exit_code
}

# Usage:
run_with_proof "database backup" pg_dump -Fc mydb -f /backups/latest.dump
```

### Agent Operating Manual Rule

```markdown
## Proof-of-Work (AGENTS.md entry)

NEVER say "done" without evidence. For every completed action, include at least one of:
- File path of output produced
- PID of process started
- URL of resource created/modified
- Command output (truncated to last 5 lines)
- Screenshot or hash of artifact

If you cannot produce proof, say "ATTEMPTED but cannot verify" and explain why.
```

---

## 3. Cascading Validation

**Principle:** Dependent sequential steps — each task validates the previous output before starting its own work. Failures loop back with fix instructions, not silent continuations.

Cascading validation prevents the "garbage in, garbage out" problem in multi-step pipelines. Without it, step 3 happily processes the corrupt output of step 2, and you don't discover the problem until step 7.

### The Pattern

```
Step 1: Produce output A
Step 2: Validate A meets spec → if invalid, return to Step 1 with fix instructions
Step 3: Use validated A to produce B
Step 4: Validate B meets spec → if invalid, return to Step 3 with fix instructions
...
```

### Example: Content Pipeline

```markdown
## Newsletter Pipeline (cascading validation)

### Step 1: Research
- Output: research-notes.md
- Validation: must contain ≥ 3 sources, each with URL and date
- Failure: "Research incomplete — need 3+ sourced items. Currently have {n}. Add more."

### Step 2: Draft
- Input: validated research-notes.md
- Pre-check: verify research-notes.md passes Step 1 validation (don't trust upstream)
- Output: draft.md
- Validation: 400-800 words, includes all research items, no placeholder text
- Failure: "Draft {issue}. Fix and resubmit. Do not proceed to editing."

### Step 3: Edit
- Input: validated draft.md
- Pre-check: verify draft.md passes Step 2 validation
- Output: final.md
- Validation: grammar check passes, links resolve, formatting correct
- Failure: "Edit issues found: {list}. Return to editing. Do not publish."

### Step 4: Publish
- Input: validated final.md
- Pre-check: verify final.md passes Step 3 validation
- Gate: HUMAN APPROVAL REQUIRED before publish
```

### Key Rule: Never Trust Upstream

Even if Step 1 "passed," Step 2 should re-validate Step 1's output before proceeding. This catches:
- Race conditions (output modified between steps)
- Silent corruption (file written but content wrong)
- Upstream validation bugs (Step 1's validator had a gap)

### Implementation

```python
def cascading_step(input_path, input_validator, processor, output_validator, max_retries=3):
    """Each step validates its input AND its output."""
    # Validate input (don't trust upstream)
    input_valid, input_errors = input_validator(input_path)
    if not input_valid:
        return {"status": "BLOCKED", "reason": f"Input validation failed: {input_errors}"}

    for attempt in range(max_retries):
        output = processor(input_path)
        output_valid, output_errors = output_validator(output)
        if output_valid:
            return {"status": "DONE", "output": output, "attempts": attempt + 1}
        # Loop back with fix instructions
        processor = make_fix_processor(processor, output_errors)

    return {"status": "FAILED", "reason": f"Failed after {max_retries} attempts", "last_errors": output_errors}
```

---

## 4. Advisory Mode Tiers

**Principle:** Not all actions carry the same risk. Categorize agent capabilities into tiers with different autonomy levels and approval requirements.

The mistake people make is binary: either the agent can do everything, or it can do nothing. Tiers let you give autonomy where it's safe and require approval where it's not.

### The Four Tiers

| Tier | Risk | Probation | Graduation | Example |
|------|------|-----------|------------|---------|
| **Low** | Reversible, internal only | 3 days | Self-promote after clean streak | Read files, search, summarize |
| **Medium** | Visible to user, recoverable | 2 weeks | Human approves promotion | Create files, edit code, run tests |
| **High** | Visible to others, hard to reverse | 2 weeks minimum | Never fully unsupervised | Git push, create PRs, post to Slack |
| **Restricted** | Irreversible or impersonation risk | Permanent | Always draft-only | Send email from user's account, delete data, financial transactions |

### Critical Rule: Email = Restricted

Sending email from a user's account is **always Restricted tier**. No exceptions. No graduation. Always draft-only with human send.

Why: Email is identity. An AI sending email "as you" creates legal, professional, and trust risks that no amount of testing eliminates.

```markdown
## Advisory Mode Configuration (AGENTS.md)

### Tier: Low (auto-approve after 3-day probation)
- Read any file in workspace
- Search codebase
- Generate summaries to memory files
- Run read-only API calls

### Tier: Medium (human approves after 2-week probation)
- Create/edit files in workspace
- Run test suites
- Generate reports
- Schedule cron jobs (read-only actions only)

### Tier: High (2-week probation, never fully autonomous)
- Git commit and push
- Create pull requests
- Post to Slack channels
- Modify cron jobs

### Tier: Restricted (always draft-only, human executes)
- Send email from user's account
- Delete files/data outside workspace
- Financial transactions (invoice, payment)
- Modify access controls or permissions
- Post to social media as user
```

### Probation Protocol

```markdown
## Probation Rules

1. New capability starts at its tier's probation period
2. During probation: agent proposes action, human approves/denies
3. Clean streak = no denials or corrections for full probation period
4. After clean streak:
   - Low: auto-promotes, agent logs the promotion
   - Medium: agent requests promotion, human approves
   - High: agent requests promotion, human approves, but spot-checks continue
   - Restricted: never promotes — always draft-only
5. Any denial during probation resets the probation clock
6. Graduated capability can be demoted if quality degrades
```

---

## 5. Completion Contracts

**Principle:** Every automated workflow needs binary done-criteria, observable evidence, staged approval, and timeout bounds. No "probably done" — it's done or it's not.

### The Contract Template

```markdown
## Completion Contract: {workflow name}

### Done Criteria (all must be true)
- [ ] {criterion 1} — verified by: {method}
- [ ] {criterion 2} — verified by: {method}
- [ ] {criterion 3} — verified by: {method}

### Evidence Required
- {artifact 1}: {location/format}
- {artifact 2}: {location/format}

### Approval Stages
1. Automated validation passes (criteria above)
2. Agent self-review (checklist)
3. Human approval (if tier requires it)

### Timeout
- Maximum duration: {time}
- On timeout: {action — alert human, retry once, abort}
- Escalation: {who gets notified}

### Rollback
- Revert procedure: {steps}
- Rollback trigger: {conditions}
```

### Example: Deployment Contract

```markdown
## Completion Contract: Production Deploy

### Done Criteria
- [ ] All tests pass on deploy branch — verified by: CI green check
- [ ] Docker image builds successfully — verified by: image SHA in registry
- [ ] Health check returns 200 — verified by: curl to /health within 60s
- [ ] No error spike in first 5 minutes — verified by: error rate < 0.1%

### Evidence Required
- CI run URL with green status
- Docker image SHA256
- Health check response (timestamp + status code)
- Error rate dashboard screenshot at T+5min

### Approval Stages
1. CI passes automatically
2. Agent verifies health check and error rate
3. Human confirms "deploy complete" in Slack

### Timeout
- Maximum duration: 15 minutes from deploy start
- On timeout: auto-rollback to previous version, alert #ops channel
- Escalation: page on-call engineer if rollback also fails

### Rollback
- Revert: deploy previous Docker image SHA
- Trigger: health check fails OR error rate > 0.5% OR human says "rollback"
```

---

## 6. Cross-Validation

**Principle:** Generate with one model, review with another. Different architectures catch different blind spots.

Single-model pipelines have correlated failure modes. If Claude hallucinates a fact, Claude reviewing its own work will often confirm the hallucination. A different model (or a human) brings uncorrelated errors.

### The Sub-Agent QC Workflow

```
Produce (Sonnet) → Review (Sam) → Cross-check (GPT) → Incorporate → Deliver
```

This isn't about which model is "better." It's about error decorrelation. Each reviewer catches things the others miss.

### Implementation

```markdown
## Cross-Validation Protocol

### Step 1: Produce (Primary Model)
- Model: Claude Sonnet (fast, cost-effective for drafts)
- Output: first draft with citations

### Step 2: Review (Human)
- Reviewer: Sam
- Focus: factual accuracy, tone, strategic alignment
- Output: annotated draft with corrections

### Step 3: Cross-Check (Secondary Model)
- Model: GPT-4 or different Claude variant
- Prompt: "Review this document for factual errors, logical inconsistencies,
  and unsupported claims. Do not rewrite — only flag issues with explanations."
- Focus: catch blind spots the primary model and human missed
- Output: issue list with severity ratings

### Step 4: Incorporate
- Primary model incorporates human + cross-check feedback
- Changes tracked and justified

### Step 5: Deliver
- Final version with revision history
- Confidence rating based on number of issues found and fixed
```

### When Cross-Validation Matters Most

- **Legal or compliance content** — different models interpret regulations differently
- **Financial calculations** — arithmetic errors are model-specific
- **Factual claims** — hallucination patterns differ across architectures
- **Security reviews** — different models catch different vulnerability classes

### When It's Overkill

- Internal notes nobody else will read
- Ephemeral content (daily logs, scratch work)
- Tasks where speed matters more than correctness
- Outputs with automated validation (tests, linters) that catch errors mechanically

---

## 7. Rule Escalation Ladder

**Principle:** Rules start as prose. If violated, they escalate to loaded rules. If violated again, they become script gates. Critical rules skip the ladder entirely.

The problem with prose rules is enforcement. An agent "knows" the rule but still violates it under pressure (long context, competing instructions, ambiguous situations). The escalation ladder adds mechanical enforcement for rules that matter.

### The Three Levels

```
Level 1: Prose Rule (in AGENTS.md)
  "Don't send emails without approval"
  → Relies on agent reading and following the rule
  → Appropriate for: new rules, low-risk guidelines

Level 2: Loaded Rule (in decisions.md, checked at session start)
  "EMAIL_SENDING: RESTRICTED — always draft-only, never auto-send"
  → Agent must load and acknowledge before acting
  → Appropriate for: rules violated once, medium-risk operations

Level 3: Script Gate (mechanical enforcement)
  Pre-send hook checks for human approval token
  → Agent literally cannot bypass the rule
  → Appropriate for: rules violated twice, high-risk operations, critical rules
```

### Escalation Protocol

```markdown
## Rule Escalation (AGENTS.md)

### Escalation Triggers
- First violation of a prose rule → add to decisions.md as loaded rule
- Second violation (now a loaded rule) → implement as script gate
- Any violation of a critical rule → skip to script gate immediately

### Critical Rules (always script-gated)
- Sending email from user's account
- Deleting files outside workspace
- Financial transactions
- Modifying access controls
- Publishing to external platforms

### Currently Loaded Rules (decisions.md)
- See decisions.md for the current set — these are checked every session start
```

### Script Gate Example

```bash
#!/bin/bash
# scripts/gate-email-send.sh — mechanical enforcement of email restriction

APPROVAL_TOKEN_FILE="/tmp/.email-approval-$(date +%Y%m%d)"

if [ ! -f "$APPROVAL_TOKEN_FILE" ]; then
  echo "BLOCKED: Email sending requires human approval."
  echo "Human: run 'echo APPROVED > $APPROVAL_TOKEN_FILE' to authorize."
  exit 1
fi

APPROVAL=$(cat "$APPROVAL_TOKEN_FILE")
if [ "$APPROVAL" != "APPROVED" ]; then
  echo "BLOCKED: Approval token invalid."
  exit 1
fi

echo "GATE PASSED: Email send authorized for today."
# Proceed with email send
"$@"

# Consume the token (one-time use)
rm "$APPROVAL_TOKEN_FILE"
```

---

## 8. Heartbeat Protocol

**Principle:** Periodic health checks batched together. Context monitor, system health, memory maintenance — all in one scheduled pulse, not scattered across individual crons.

### Heartbeat vs. Cron Decision

| Use Heartbeat When | Use Individual Cron When |
|---|---|
| Check is lightweight (< 30 seconds) | Task is heavyweight (minutes) |
| Multiple checks share context | Task is completely independent |
| Failure in one check should inform others | Task has its own retry/error handling |
| You want a single "system status" view | Task needs its own schedule (not aligned) |

### Heartbeat Structure

```markdown
## Heartbeat Protocol (runs every 4 hours)

### Phase 1: Context Monitor (5 seconds)
- Check MEMORY.md size (warn if > 200 lines)
- Check daily note exists for today
- Verify SOUL.md and AGENTS.md haven't been modified unexpectedly

### Phase 2: System Health (10 seconds)
- Disk space check (warn if < 10% free)
- Check if critical services are running (by PID file)
- Verify cron jobs are registered and last-ran within expected windows

### Phase 3: Memory Maintenance (15 seconds)
- Scan for contradictions (see Pattern 9)
- Archive daily notes older than 7 days
- Update system-health.json with current status

### Output
- Write to HEARTBEAT.md: timestamp, all-clear or issues found
- If issues found: list them with severity and suggested fix
- If critical issue: alert human immediately (don't wait for next heartbeat)
```

### Implementation

```bash
#!/bin/bash
# scripts/heartbeat.sh

HEARTBEAT_FILE="HEARTBEAT.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
STATUS="ALL CLEAR"
ISSUES=""

# Phase 1: Context Monitor
MEMORY_LINES=$(wc -l < MEMORY.md 2>/dev/null || echo "0")
if [ "$MEMORY_LINES" -gt 200 ]; then
  ISSUES="$ISSUES\n- WARN: MEMORY.md is $MEMORY_LINES lines (limit: 200)"
  STATUS="ISSUES FOUND"
fi

if [ ! -f "memory/$(date +%Y-%m-%d).md" ]; then
  ISSUES="$ISSUES\n- INFO: No daily note for today"
fi

# Phase 2: System Health
DISK_FREE=$(df -h . | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_FREE" -gt 90 ]; then
  ISSUES="$ISSUES\n- CRITICAL: Disk usage at ${DISK_FREE}%"
  STATUS="CRITICAL"
fi

# Phase 3: Memory Maintenance
# (Contradiction detection delegated to agent — see Pattern 9)

# Write heartbeat
cat > "$HEARTBEAT_FILE" << EOF
# Heartbeat
Last check: $TIMESTAMP
Status: $STATUS
$(if [ -n "$ISSUES" ]; then echo -e "\n## Issues\n$ISSUES"; fi)
EOF

echo "Heartbeat complete: $STATUS"
```

---

## 9. Contradiction Detection

**Principle:** Actively scan for conflicts between memory entries, between memory and SOUL, stale facts, and decision reversals. Don't wait for contradictions to cause errors — find them during maintenance.

### Contradiction Types

| Type | Description | Example |
|------|-------------|---------|
| **Memory-Memory** | Two memory entries say opposite things | "Client prefers email" vs "Client prefers Slack" |
| **Memory-SOUL** | Memory contradicts core identity/rules | SOUL says "never auto-send email" but memory says "auto-send enabled for digest" |
| **Stale Facts** | Memory entry is outdated | "API endpoint: api.v1.example.com" when v1 was deprecated |
| **Decision Reversal** | decisions.md contradicts earlier decision without noting the change | "Use PostgreSQL" then later "Use SQLite" with no migration note |

### Scan Protocol

```markdown
## Contradiction Detection (run during heartbeat Phase 3)

### Scan Checklist
1. Load all memory entries with type=project and type=reference
2. For each pair, check for semantic conflicts:
   - Same topic, different conclusions
   - Same entity, different attributes
   - Same process, different steps
3. Load SOUL.md rules and check memory entries against each rule
4. Check decisions.md for entries that reverse previous decisions without rationale
5. Flag entries older than 30 days for staleness review

### Output Format
- If contradictions found: write to memory/contradictions-{date}.md
- Each entry: the two conflicting sources, the conflict, suggested resolution
- Critical contradictions (SOUL violations): alert immediately

### Resolution
- Human reviews contradictions list
- For each: keep A, keep B, merge, or delete both
- Update affected files
- Log resolution in decisions.md
```

### Example Contradiction Report

```markdown
# Contradictions Found — 2026-03-15

## CRITICAL: Memory-SOUL Conflict
- **SOUL.md line 23:** "Never auto-send email from user's account"
- **memory/gmail-daily-summary.md:** "Auto-send daily digest at 7am"
- **Resolution needed:** Either update SOUL or disable auto-send
- **Severity:** CRITICAL — active violation of core rule

## WARN: Memory-Memory Conflict
- **memory/wallets-onchain-identity.md:** "Primary wallet: 0xABC..."
- **memory/2026-03-12.md:** "Migrated primary wallet to 0xDEF..."
- **Resolution needed:** Update wallets file with new primary address
- **Severity:** MEDIUM — stale reference may cause wrong wallet usage

## INFO: Stale Entry
- **memory/starred-repos.md:** Last updated 45 days ago
- **Suggestion:** Review and refresh or archive
- **Severity:** LOW
```

---

## 10. Tight Harness Principle

**Principle:** Autonomy gets useful when the harness is tight. Don't sell agents — sell harnesses. An agent without a harness is a liability. A harness without an agent is just a script.

### The Five Harness Components

Every autonomous agent operation needs all five:

| Component | Question | Example |
|-----------|----------|---------|
| **Objective Metric** | How do we know it worked? | "Test suite passes" not "code looks good" |
| **Bounded Scope** | What can it touch? | "Only files in /src/api/" not "any file" |
| **Time Budget** | When does it stop? | "15 minutes max" not "when it's done" |
| **Reversibility** | Can we undo it? | "Git branch, not direct commit to main" |
| **Observability** | Can we see what it did? | "Full command log" not "trust me" |

### The Key Insight

Most agent failures aren't capability failures — they're harness failures. The agent could do the task, but:
- Nobody defined "done" objectively (no metric)
- It modified files it shouldn't have (no scope bound)
- It ran for 3 hours burning tokens (no time budget)
- It pushed directly to main (no reversibility)
- Nobody could tell what it did (no observability)

### Harness Configuration Example

```markdown
## Harness: Automated PR Review Agent

### Objective Metric
- All review comments reference specific code lines
- No false positive rate > 10% (tracked over 2-week window)
- Review completed within 5 minutes of PR open

### Bounded Scope
- READ: any file in the repository
- WRITE: only PR comments via GitHub API
- CANNOT: approve PRs, merge PRs, modify code, close PRs

### Time Budget
- Maximum 5 minutes per PR
- Maximum 20 PRs per day
- On budget exceeded: skip PR, log reason, alert human

### Reversibility
- All comments can be deleted
- No permanent actions taken
- Human can dismiss any comment

### Observability
- Every review logged to reviews/{date}-{pr-number}.md
- Includes: files reviewed, issues found, comments posted, time taken
- Weekly accuracy report generated automatically
```

### Selling Harnesses, Not Agents

When someone asks "can your agent do X?" — the right answer is "here's the harness that makes X safe":

```
BAD:  "Yes, our agent can deploy to production!"
GOOD: "Yes, with this harness: deploys only to staging first, requires health
       check pass, auto-rollback on error spike, human approval for prod
       promotion, full audit log, 15-minute timeout."
```

The harness IS the product. The agent is just the engine inside it.

---

## Quick Reference: Pattern Selection Guide

| Situation | Pattern |
|-----------|---------|
| "Should this agent exist?" | Consumer-First Design (#1) |
| "Agent says it's done but I don't believe it" | Proof-of-Work (#2) |
| "Multi-step pipeline keeps producing garbage" | Cascading Validation (#3) |
| "How much autonomy should this agent have?" | Advisory Mode Tiers (#4) |
| "When is this workflow actually done?" | Completion Contracts (#5) |
| "Agent keeps making the same kind of error" | Cross-Validation (#6) |
| "Agent keeps violating a rule" | Rule Escalation Ladder (#7) |
| "How do I monitor agent health?" | Heartbeat Protocol (#8) |
| "Agent's memory is inconsistent" | Contradiction Detection (#9) |
| "How do I make autonomy safe?" | Tight Harness Principle (#10) |

---

## Combining Patterns

These patterns are composable. A production agent typically uses several together:

```
Consumer-First Design    → Does this agent need to exist?
  ↓ yes
Advisory Mode Tiers      → What can it do autonomously?
  ↓ configured
Completion Contracts     → How do we know each task is done?
  ↓ defined
Cascading Validation     → How do multi-step tasks flow?
  ↓ piped
Proof-of-Work            → How do we verify claims?
  ↓ enforced
Cross-Validation         → How do we catch blind spots?
  ↓ reviewed
Rule Escalation Ladder   → How do we handle violations?
  ↓ gated
Heartbeat Protocol       → How do we monitor ongoing health?
  ↓ pulsing
Contradiction Detection  → How do we keep memory consistent?
  ↓ clean
Tight Harness            → How do we keep all of this safe?
```

Start with #1 (does this agent need to exist?) and #10 (is the harness tight?). Add the others as complexity demands.