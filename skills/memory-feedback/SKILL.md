---
name: memory-feedback
description: Agent memory and learning system. Logs actions/failures, detects patterns, proposes skill improvements via GitHub PRs. Human approval required.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "memory", "learning", "github-integration"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl", "gh", "openclaw"], "env": ["OPENCLAW_DATA_DIR", "GITHUB_TOKEN"]}, "notes": "GITHUB_TOKEN is optional — required only for the GitHub PR workflow that proposes skill improvements. Core memory and failure logging works without it using local files only. The gh CLI is optional.", "path_prefix": "/data/ in examples refers to $OPENCLAW_DATA_DIR (default: /data/)"}}
---

# Memory and Feedback

This skill gives the OpenClaw system a learning loop. All 18 skills log their episodes and failures. This skill reads those logs, detects patterns, and proposes improvements — as GitHub pull requests against the SKILL.md files that govern behaviour. Humans review and merge. The system learns.

This is Phase 4 infrastructure, designed to be activated once Phase 3B has been running long enough to generate meaningful data — typically 2-3 months of real operation. The episode and failure hooks in Skills 14-18 write to `/data/memory/` from day one. When this skill is activated, months of learning data are already waiting.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq || sudo apt install jq

# Optional: for GitHub PR workflow
export GITHUB_TOKEN="ghp_your_token"
which gh || echo "gh CLI optional — only needed for PR-based improvement proposals"
```

GITHUB_TOKEN is optional — required only for the PR workflow that proposes skill improvements. Core memory logging and failure tracking works without it using local files only.


## Core Philosophy

- **Semi-Automatic by Design**: The agent owns its memory files — episodes and failures are written without approval. Skill files govern behaviour and require human review before any change takes effect. This boundary is non-negotiable
- **Pattern Detection, Not Gut Feel**: Improvements are proposed only when a pattern appears with sufficient frequency and confidence. A single failure is a data point. Three failures of the same type with the same trigger is a pattern
- **Human in the Loop for Skill Changes**: Every proposed skill improvement becomes a GitHub pull request. The accountant or developer sees exactly what changed, why, and what evidence led to the proposal. Merge = accepted. Close = rejected and never re-proposed
- **Rate Limited to Protect the Machine**: Memory operations are token-budgeted. Pattern scans run overnight. Storage limits are enforced. The system cannot consume itself
- **Honest About What It Does Not Know**: Patterns below the confidence threshold are stored but not proposed. The system does not act on weak evidence

---

## OpenClaw Commands

### Episode and Failure Logging (called by other skills)
```bash
# Log a successful episode (called internally by all skills)
openclaw memory log-episode --skill greek-financial-statements --type statement_generated --afm EL123456789 --period 2026-01 --session S20260218-001 --tokens 1240 --duration-seconds 31

# Log a failure (called internally by all skills)
openclaw memory log-failure --skill conversational-ai-assistant --type intent_misread --session S20260218-003 --query "send the summary to Alpha" --action-taken "attempted openclaw comms send" --what-went-wrong "Skill 16 not available" --what-should-have-happened "draft text and state manual sending required"

# Log a human correction (called when accountant provides explicit feedback)
openclaw memory log-correction --session S20260218-005 --failure-id FAIL-20260218-003 --correction "Draft the text and tell me to send it manually"
```

### Pattern Scanning and Analysis
```bash
# Run pattern scan manually (normally runs nightly)
openclaw memory scan-patterns --since 30-days
openclaw memory scan-patterns --since 30-days --skill conversational-ai-assistant
openclaw memory scan-patterns --failures-only --min-occurrences 3

# View detected patterns
openclaw memory patterns-list --all
openclaw memory patterns-list --above-threshold   # Confidence >= 0.85
openclaw memory patterns-list --below-threshold   # Promising but not yet proposable
openclaw memory pattern-detail --id PAT-20260218-007

# View recent episodes and failures
openclaw memory episodes --last 7-days
openclaw memory episodes --skill greek-financial-statements --last 30-days
openclaw memory failures --last 7-days
openclaw memory failures --type completeness_gate_failed --last 30-days
openclaw memory corrections --last 30-days
```

### Proposal Generation and GitHub Integration
```bash
# Generate a proposal from a detected pattern
openclaw memory propose --pattern-id PAT-20260218-007
openclaw memory propose --pattern-id PAT-20260218-007 --dry-run   # Show proposed change without creating PR

# List proposals
openclaw memory proposals-list --all
openclaw memory proposals-list --status pending-pr
openclaw memory proposals-list --status pr-open
openclaw memory proposals-list --status rejected

# Create GitHub PR from a proposal
openclaw memory create-pr --proposal-id PROP-20260218-001
openclaw memory create-pr --proposal-id PROP-20260218-001 --branch-name "memory/skill-improvement/PROP-001"

# Sync PR status (check if merged or closed)
openclaw memory sync-prs
openclaw memory pr-status --proposal-id PROP-20260218-001
```

### Rate Limit Management
```bash
# View current consumption
openclaw memory rate-limit-status
openclaw memory rate-limit-status --verbose   # Show all counters and limits

# View config
openclaw memory rate-limit-config

# Reset daily counter (use only if counter stuck after verified issue)
openclaw memory rate-limit-reset --counter daily-tokens --confirm

# View storage usage
openclaw memory storage-usage
openclaw memory storage-usage --by-directory
```

### Memory Maintenance
```bash
# Archive old episodes (auto-runs, but can be triggered manually)
openclaw memory archive --episodes --older-than 90-days
openclaw memory archive --failures --older-than 90-days

# View memory health
openclaw memory health
openclaw memory health --verbose

# Generate memory report (monthly summary of learning activity)
openclaw memory report --period 2026-01
openclaw memory report --period 2026-01 --format pdf --output /data/reports/system/
```

---

## Episode Log Structure

```json
{
  "episode_id": "EP-20260218-001",
  "session_id": "S20260218-001",
  "user": "maria.g",
  "timestamp_utc": "2026-02-18T09:14:32Z",
  "skill": "greek-financial-statements",
  "action_type": "statement_generated",
  "client_afm": "EL123456789",
  "period": "2026-01",
  "commands_called": [
    "openclaw statements check-ready --afm EL123456789 --period 2026-01",
    "openclaw statements generate --afm EL123456789 --period 2026-01 --type all"
  ],
  "human_confirmation_required": false,
  "outcome": "success",
  "result_summary": "Full statement pack generated. P&L, balance sheet, cash flow, VAT summary. v1 issued.",
  "tokens_used": 1240,
  "duration_seconds": 31
}
```

---

## Failure Log Structure

```json
{
  "failure_id": "FAIL-20260218-003",
  "episode_id": "EP-20260218-003",
  "session_id": "S20260218-001",
  "user": "maria.g",
  "timestamp_utc": "2026-02-18T11:22:14Z",
  "skill": "conversational-ai-assistant",
  "failure_type": "intent_misread",
  "user_query": "Send the January summary to Alpha Trading",
  "agent_action_taken": "Attempted openclaw comms send — skill not yet available",
  "what_went_wrong": "Agent tried to send client communication directly. Skill 16 not deployed at time of query.",
  "what_should_have_happened": "Recognise outgoing communication unavailable. Draft the summary text. Inform user it needs manual sending.",
  "human_correction_provided": true,
  "human_correction_text": "Just write the summary text and tell me to send it manually",
  "pattern_candidate": true,
  "skill_improvement_candidate": "14-conversational-ai-assistant",
  "proposed_change_summary": "Add scope boundary: if comms send requested and Skill 16 unavailable, draft content and state manual sending required"
}
```

---

## Pattern Detection

### Detection Algorithm

```yaml
Pattern_Detection:
  runs: "Nightly at 02:00 Athens time"
  lookback_window: "30 days rolling"
  minimum_occurrences: 3
  confidence_threshold_for_proposal: 0.85

  grouping_keys:
    - skill + failure_type                     # Same skill, same failure type
    - user_query_intent + agent_action_taken   # Same intent, same wrong action
    - skill + missing_data_source              # Same skill, same upstream data missing

  confidence_calculation:
    factors:
      - occurrence_count (weight: 40%)
      - recency_bias (more recent = higher weight) (weight: 30%)
      - human_correction_present (weight: 20%)
      - consistent_what_should_have_happened across occurrences (weight: 10%)

  output:
    above_threshold: "Write pattern to /data/memory/patterns/failures/{id}.json — eligible for proposal"
    below_threshold: "Write pattern to /data/memory/patterns/failures/{id}.json — marked WATCH, not proposable yet"
```

### Pattern Record Structure

```json
{
  "pattern_id": "PAT-20260218-007",
  "detected_date": "2026-02-18",
  "pattern_type": "recurring_failure",
  "skill": "14-conversational-ai-assistant",
  "failure_type": "intent_misread",
  "occurrences": 4,
  "failure_ids": ["FAIL-20260212-001", "FAIL-20260214-003", "FAIL-20260217-002", "FAIL-20260218-003"],
  "confidence": 0.91,
  "common_trigger": "User requests outgoing client communication",
  "common_failure": "Agent attempts Skill 16 which is not deployed",
  "what_should_have_happened": "Draft content and state manual sending required until Skill 16 deployed",
  "proposed_skill_change": {
    "skill_file": "14-conversational-ai-assistant-SKILL.md",
    "section": "Scope Boundaries / Out_Of_Scope__Redirect",
    "change_description": "Add explicit handling for comms send requests when Skill 16 unavailable",
    "current_text_excerpt": "Draft document request text (for human review before sending)",
    "proposed_addition": "If user requests outgoing communication and Skill 16 (client-communication-engine) is not deployed: draft the full text content, clearly state it requires manual sending, and note that Skill 16 will handle this automatically when deployed."
  },
  "proposal_status": "pending",
  "github_pr_status": null,
  "rejected": false
}
```

---

## GitHub Integration Flow

```yaml
GitHub_PR_Flow:

  prerequisites:
    - GitHub repo URL configured in /data/memory/rate-limits/config.json
    - GitHub token stored in /data/auth/github-token.enc
    - Agent has push access to create branches only (not merge to main)

  step_1_branch_creation:
    command: "git checkout -b memory/skill-improvement/{proposal-id}"
    naming: "memory/skill-improvement/PROP-{YYYYMMDD}-{3digits}"

  step_2_file_edit:
    target: "The specific SKILL.md file identified in the pattern"
    change: "Exactly the text change described in proposed_skill_change"
    commit_message: |
      "Memory system: {brief description}
      
      Pattern: {pattern_id} — {confidence} confidence
      Occurrences: {N} over {lookback_window}
      Failure type: {failure_type}
      
      See /data/memory/patterns/failures/{pattern_id}.json for full evidence."

  step_3_pull_request:
    title: "[Memory] {skill_name}: {brief description of change}"
    body: |
      ## What This Changes
      {plain English description of the specific text change}
      
      ## Why This Is Proposed
      Pattern {pattern_id} detected {N} occurrences of {failure_type} 
      in {skill_name} over the last {days} days.
      
      Confidence score: {confidence} (threshold: 0.85)
      
      ## Evidence
      Failure IDs: {list}
      Common trigger: {common_trigger}
      Common failure: {common_failure}
      What should have happened: {what_should_have_happened}
      
      ## To Accept
      Review the specific text change in the diff and merge if correct.
      
      ## To Reject
      Close this PR. The pattern will be marked as reviewed/rejected 
      and this specific change will not be re-proposed.
    labels: ["memory-proposal", "skill-improvement"]

  step_4_post_pr:
    on_merge:
      - Mark proposal status as "merged"
      - Log episode: proposal_accepted
      - Pattern marked as resolved
    on_close:
      - Mark proposal status as "rejected"  
      - Pattern marked as reviewed/rejected
      - Same change never re-proposed for this pattern
      - Agent learns: log rejection reason for future calibration

  hard_limits:
    max_prs_per_day: 2
    max_proposals_per_day: 3
    agent_never_pushes_to: "main, master, or any protected branch"
    agent_never_merges: "Any PR — merge requires human action only"
```

---

## Rate Limiting

```yaml
Rate_Limit_Config:
  location: "/data/memory/rate-limits/config.json"

  token_budgets:
    memory_logging: 500     # Per-operation logging (episodes and failures)
    pattern_scan: 1500      # Nightly scan of last 30 days
    proposal_generation: 1000  # Per proposal — includes SKILL.md diff computation
    daily_total: 5000       # Hard ceiling across all memory operations
    note: "Token budget counts only memory/reflection tokens, not accounting operations"

  operation_frequency:
    episode_logging: "Every qualifying action — no rate limit (lightweight)"
    failure_logging: "Every failure — no rate limit (lightweight)"
    pattern_scan: "Once daily at 02:00 Athens — never during business hours"
    proposal_generation: "Maximum 3 per day"
    github_pr_creation: "Maximum 2 per day"

  storage_limits:
    episodes_max_mb: 500
    failures_max_mb: 200
    patterns_max_mb: 50
    proposals_max_mb: 50
    total_memory_max_gb: 2
    auto_archive_after_days: 90
    halt_at_percent: 90    # Halt memory writes at 90% of total_memory_max_gb

  circuit_breakers:
    halt_if_daily_token_budget_exceeded: true
    halt_if_storage_exceeds_90_percent: true
    alert_at_80_percent_storage: true
    never_run_pattern_scan_during_business_hours: true
    never_run_more_than_one_scan_per_day: true

  hard_floors:
    note: "These values cannot be set lower by the agent — they are code-enforced minimums"
    min_confidence_for_proposal: 0.85
    min_occurrences_for_proposal: 3
    min_lookback_days: 7
```

---

## File System

```yaml
Memory_File_Structure:
  owns: "/data/memory/"

  episodes:
    path: "/data/memory/episodes/{YYYY-MM-DD}/{session-id}_{action-type}.json"
    written_by: "All 18 skills via openclaw memory log-episode"
    read_by: "memory-feedback only"
    auto_archived_after: "90 days"

  failures:
    path: "/data/memory/failures/{YYYY-MM-DD}/{session-id}_{failure-type}.json"
    written_by: "All 18 skills via openclaw memory log-failure"
    read_by: "memory-feedback only"
    auto_archived_after: "90 days"

  patterns:
    path: "/data/memory/patterns/failures/{pattern-id}.json"
         "/data/memory/patterns/successes/{pattern-id}.json"
    written_by: "memory-feedback (nightly scan)"
    retained: "Indefinitely — patterns are system learning assets"

  corrections:
    path: "/data/memory/corrections/{YYYY-MM-DD}_{correction-id}.json"
    written_by: "conversational-ai-assistant (when human provides correction)"
    read_by: "memory-feedback"
    retained: "Indefinitely"

  proposals:
    path: "/data/memory/proposals/{YYYY-MM-DD}_{skill-name}_{id}.md"
    written_by: "memory-feedback"
    retained: "Indefinitely (audit record of what was proposed and outcome)"

  rate_limits:
    path: "/data/memory/rate-limits/"
    files:
      - "current-state.json"   # Live counters — updated per operation
      - "daily-log.json"       # Historical daily consumption
      - "config.json"          # Configurable limits
```

---

## Activation Checklist

Skill 19 should be activated when:

```yaml
Activation_Prerequisites:
  data_maturity:
    - "Phase 3B has been running for minimum 60 days"
    - "At least 100 episodes logged across all skills"
    - "At least 20 failures logged with what_should_have_happened populated"
    - "At least 3 human corrections on record"

  infrastructure:
    - "GitHub repo URL and token configured"
    - "Agent has branch creation access (not merge)"
    - "/data/memory/ directories exist and are writable"
    - "Storage monitoring confirms adequate space (min 5 GB free)"

  team_readiness:
    - "Senior accountant / developer briefed on PR review process"
    - "GitHub notifications configured for the memory/skill-improvement/* branch pattern"
    - "Team understands: close PR = rejected, merge PR = accepted change goes live"

  first_run:
    - "Run openclaw memory scan-patterns --since 60-days --dry-run first"
    - "Review all patterns detected before enabling live proposal creation"
    - "Confirm rate limit config matches team preferences"
    - "Enable with: openclaw memory activate --confirm"
```

---

## Integration Points

```yaml
Written_By_All_Skills:
  hook: "Every skill calls openclaw memory log-episode or openclaw memory log-failure as final step"
  episode_triggers: "Decision made, output produced, government system interaction"
  failure_triggers: "Any error, intent misread, missing data, human correction"

Read_By_Memory_Feedback_Only:
  note: "No other skill reads from /data/memory/ for decision-making"
  reason: "Memory data is raw and unverified until pattern-processed. Direct reads would propagate noise."

Downstream_Of_Memory_System:
  github: "Proposed skill improvements as pull requests"
  dashboard: "Memory health metrics (token usage, storage, pattern counts)"
  reports: "/data/reports/system/ — monthly memory activity report"
```

---

## Success Metrics

A successful deployment of this skill should achieve:
- ✅ 100% of qualifying agent actions generate an episode log within 5 seconds
- ✅ 100% of failures generate a failure log with what_should_have_happened populated
- ✅ Nightly pattern scan completes within the daily token budget
- ✅ At least one high-confidence pattern detected per month after 90 days of operation
- ✅ PRs opened for all proposals above the confidence threshold — zero silently dropped
- ✅ Rejected patterns never re-proposed — the rejection is respected
- ✅ Storage consumption stays within configured limits — no unchecked growth
- ✅ Zero PR merges without human action — agent never self-merges

Remember: This skill is how the system gets better over time without requiring manual review of every interaction. The value compounds. Month 3 of operation is more valuable than month 1. The team should expect to see the quality of the conversational assistant and financial statement generation improve measurably within 6 months of activation.
