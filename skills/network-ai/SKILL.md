---
name: Network-AI
description: "Python orchestration skill: local multi-agent workflows via blackboard file, permission gating, and token budget scripts. All execution is local — no network calls, no Node.js required. TypeScript/Node.js features (HMAC tokens, AES-256, MCP server, 14 adapters, CLI) are in the SEPARATE companion npm package (npm install -g network-ai) and are NOT part of this skill bundle."
metadata:
  openclaw:
    emoji: "\U0001F41D"
    homepage: https://github.com/jovanSAPFIONEER/Network-AI
    bundle_scope: "Python scripts only (scripts/*.py). The README.md in this repo describes the FULL project including the companion Node.js npm package — features documented there (HMAC tokens, AES-256 encryption, MCP server, 14 adapters, CLI) are NOT implemented in these Python scripts and are NOT part of this ClawHub skill. Install the npm package separately for those features."
    requires:
      bins:
        - python3
      optional_bins:
        - node  # Only needed if you separately install and run the Node.js MCP server (network-ai-server via npm). Not required for this skill's Python instructions.
    env:
      SWARM_TOKEN_SECRET:
        required: false
        description: "Node.js MCP server only — not used by these Python scripts. The Python permission layer uses UUID-based tokens stored in data/active_grants.json."
      SWARM_ENCRYPTION_KEY:
        required: false
        description: "Node.js MCP server only — not used by these Python scripts. The Python blackboard does not encrypt data at rest."
      OPENAI_API_KEY:
        required: false
        description: "Not used by these Python scripts. Only used by the optional Node.js demo examples when running the companion npm package."
    privacy:
      audit_log:
        path: data/audit_log.jsonl
        scope: local-only
        description: "Local append-only JSONL file recording operation metadata (agentId, action, timestamp, outcome). No data leaves the machine. Disable with --no-audit flag on network-ai-server, or pass auditLogPath: undefined in createSwarmOrchestrator config."
---

# Swarm Orchestrator Skill

> **Scope of this skill bundle:** All instructions below run local Python scripts (`scripts/*.py`). No network calls are made by this skill. Tokens are UUID-based (`grant_{uuid4().hex}`) stored in `data/active_grants.json`. Audit logging is plain JSONL (`data/audit_log.jsonl`) — no HMAC signing in the Python layer. HMAC-signed tokens, AES-256 encryption, and the standalone MCP server are all features of the **companion Node.js package** (`npm install -g network-ai`) — they are **not** implemented in these Python scripts and do **not** run automatically.

Multi-agent coordination system for complex workflows requiring task delegation, parallel execution, and permission-controlled access to sensitive APIs.

## 🎯 Orchestrator System Instructions

**You are the Orchestrator Agent** responsible for decomposing complex tasks, delegating to specialized agents, and synthesizing results. Follow this protocol:

### Core Responsibilities

1. **DECOMPOSE** complex prompts into 3 specialized sub-tasks
2. **DELEGATE** using the budget-aware handoff protocol
3. **VERIFY** results on the blackboard before committing
4. **SYNTHESIZE** final output only after all validations pass

### Task Decomposition Protocol

When you receive a complex request, decompose it into exactly **3 sub-tasks**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLEX USER REQUEST                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  SUB-TASK 1   │   │  SUB-TASK 2   │   │  SUB-TASK 3   │
│ data_analyst  │   │ risk_assessor │   │strategy_advisor│
│    (DATA)     │   │   (VERIFY)    │   │  (RECOMMEND)  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌───────────────┐
                    │  SYNTHESIZE   │
                    │ orchestrator  │
                    └───────────────┘
```

**Decomposition Template:**
```
TASK DECOMPOSITION for: "{user_request}"

Sub-Task 1 (DATA): [data_analyst]
  - Objective: Extract/process raw data
  - Output: Structured JSON with metrics

Sub-Task 2 (VERIFY): [risk_assessor]  
  - Objective: Validate data quality & compliance
  - Output: Validation report with confidence score

Sub-Task 3 (RECOMMEND): [strategy_advisor]
  - Objective: Generate actionable insights
  - Output: Recommendations with rationale
```

### Budget-Aware Handoff Protocol

**CRITICAL:** Before EVERY `sessions_send`, call the handoff interceptor:

```bash
# ALWAYS run this BEFORE sessions_send
python {baseDir}/scripts/swarm_guard.py intercept-handoff \
  --task-id "task_001" \
  --from orchestrator \
  --to data_analyst \
  --message "Analyze Q4 revenue data"
```

**Decision Logic:**
```
IF result.allowed == true:
    → Proceed with sessions_send
    → Note tokens_spent and remaining_budget
ELSE:
    → STOP - Do NOT call sessions_send
    → Report blocked reason to user
    → Consider: reduce scope or abort task
```

### Pre-Commit Verification Workflow

Before returning final results to the user:

```bash
# Step 1: Check all sub-task results on blackboard
python {baseDir}/scripts/blackboard.py read "task:001:data_analyst"
python {baseDir}/scripts/blackboard.py read "task:001:risk_assessor"
python {baseDir}/scripts/blackboard.py read "task:001:strategy_advisor"

# Step 2: Validate each result
python {baseDir}/scripts/swarm_guard.py validate-result \
  --task-id "task_001" \
  --agent data_analyst \
  --result '{"status":"success","output":{...},"confidence":0.85}'

# Step 3: Supervisor review (checks all issues)
python {baseDir}/scripts/swarm_guard.py supervisor-review --task-id "task_001"

# Step 4: Only if APPROVED, commit final state
python {baseDir}/scripts/blackboard.py write "task:001:final" \
  '{"status":"SUCCESS","output":{...}}'
```

**Verdict Handling:**
| Verdict | Action |
|---------|--------|
| `APPROVED` | Commit and return results to user |
| `WARNING` | Review issues, fix if possible, then commit |
| `BLOCKED` | Do NOT return results. Report failure. |

---

## When to Use This Skill

- **Task Delegation**: Route work to specialized agents (data_analyst, strategy_advisor, risk_assessor)
- **Parallel Execution**: Run multiple agents simultaneously and synthesize results
- **Permission Wall**: Gate access to DATABASE, PAYMENTS, EMAIL, or FILE_EXPORT operations (abstract local resource types — no external credentials required)
- **Shared Blackboard**: Coordinate agent state via persistent markdown file

## Quick Start

### 1. Initialize Budget (FIRST!)

**Always initialize a budget before any multi-agent task:**

```bash
python {baseDir}/scripts/swarm_guard.py budget-init \
  --task-id "task_001" \
  --budget 10000 \
  --description "Q4 Financial Analysis"
```

### 2. Delegate a Task to Another Session

Use OpenClaw's built-in session tools to delegate work:

```
sessions_list    # See available sessions/agents
sessions_send    # Send task to another session
sessions_history # Check results from delegated work
```

**Example delegation prompt:**
```
Use sessions_send to ask the data_analyst session to:
"Analyze Q4 revenue trends from the SAP export data and summarize key insights"
```

### 3. Check Permission Before API Access

Before accessing SAP or Financial APIs, evaluate the request:

```bash
# Run the permission checker script
python {baseDir}/scripts/check_permission.py \
  --agent "data_analyst" \
  --resource "DATABASE" \
  --justification "Need Q4 invoice data for quarterly report" \
  --scope "read:invoices"
```

The script will output a grant token if approved, or denial reason if rejected.

### 4. Use the Shared Blackboard

Read/write coordination state:

```bash
# Write to blackboard
python {baseDir}/scripts/blackboard.py write "task:q4_analysis" '{"status": "in_progress", "agent": "data_analyst"}'

# Read from blackboard  
python {baseDir}/scripts/blackboard.py read "task:q4_analysis"

# List all entries
python {baseDir}/scripts/blackboard.py list
```

### 5. Use the Node.js CLI (optional — requires `npm install -g network-ai`)

The CLI gives direct terminal access to all four subsystems without running a server:

```bash
# Blackboard
network-ai bb get task:q4_analysis
network-ai bb set task:q4_analysis '{"status": "complete"}' --agent orchestrator
network-ai bb list
network-ai bb snapshot

# Permissions
network-ai auth token data_analyst --resource DATABASE --action read \
  --justification "Need Q4 invoices for revenue report"
network-ai auth check grant_a1b2c3...
network-ai auth revoke grant_a1b2c3...

# Budget
network-ai budget status
network-ai budget set-ceiling 50000

# Audit log
network-ai audit log --limit 50
network-ai audit tail          # live-stream as events arrive
```

Global flags: `--data <path>` (override data directory) · `--json` (machine-readable output)

## Agent-to-Agent Handoff Protocol

When delegating tasks between agents/sessions:

### Step 1: Initialize Budget & Check Capacity
```bash
# Initialize budget (if not already done)
python {baseDir}/scripts/swarm_guard.py budget-init --task-id "task_001" --budget 10000

# Check current status
python {baseDir}/scripts/swarm_guard.py budget-check --task-id "task_001"
```

### Step 2: Identify Target Agent
```
sessions_list  # Find available agents
```

Common agent types:
| Agent | Specialty |
|-------|-----------|
| `data_analyst` | Data processing, SQL, analytics |
| `strategy_advisor` | Business strategy, recommendations |
| `risk_assessor` | Risk analysis, compliance checks |
| `orchestrator` | Coordination, task decomposition |

### Step 3: Intercept Before Handoff (REQUIRED)

```bash
# This checks budget AND handoff limits before allowing the call
python {baseDir}/scripts/swarm_guard.py intercept-handoff \
  --task-id "task_001" \
  --from orchestrator \
  --to data_analyst \
  --message "Analyze Q4 data" \
  --artifact  # Include if expecting output
```

**If ALLOWED:** Proceed to Step 4
**If BLOCKED:** Stop - do not call sessions_send

### Step 4: Construct Handoff Message

Include these fields in your delegation:
- **instruction**: Clear task description
- **context**: Relevant background information
- **constraints**: Any limitations or requirements
- **expectedOutput**: What format/content you need back

### Step 5: Send via sessions_send

```
sessions_send to data_analyst:
"[HANDOFF]
Instruction: Analyze Q4 revenue by product category
Context: Using SAP export from ./data/q4_export.csv
Constraints: Focus on top 5 categories only
Expected Output: JSON summary with category, revenue, growth_pct
[/HANDOFF]"
```

### Step 4: Check Results

```
sessions_history data_analyst  # Get the response
```

## Permission Wall (AuthGuardian)

**CRITICAL**: Always check permissions before accessing:
- `DATABASE` - Internal database / data store access
- `PAYMENTS` - Financial/payment data services
- `EMAIL` - Email sending capability
- `FILE_EXPORT` - Exporting data to local files

> **Note**: These are abstract local resource type names used by `check_permission.py`. No external API credentials are required or used — all permission evaluation runs locally.

### Permission Evaluation Criteria

| Factor | Weight | Criteria |
|--------|--------|----------|
| Justification | 40% | Must explain specific task need |
| Trust Level | 30% | Agent's established trust score |
| Risk Assessment | 30% | Resource sensitivity + scope breadth |

### Using the Permission Script

```bash
# Request permission
python {baseDir}/scripts/check_permission.py \
  --agent "your_agent_id" \
  --resource "PAYMENTS" \
  --justification "Generating quarterly financial summary for board presentation" \
  --scope "read:revenue,read:expenses"

# Output if approved:
# ✅ GRANTED
# Token: grant_a1b2c3d4e5f6
# Expires: 2026-02-04T15:30:00Z
# Restrictions: read_only, no_pii_fields, audit_required

# Output if denied:
# ❌ DENIED
# Reason: Justification is insufficient. Please provide specific task context.
```

### Restriction Types

| Resource | Default Restrictions |
|----------|---------------------|
| DATABASE | `read_only`, `max_records:100` |
| PAYMENTS | `read_only`, `no_pii_fields`, `audit_required` |
| EMAIL | `rate_limit:10_per_minute` |
| FILE_EXPORT | `anonymize_pii`, `local_only` |

## Shared Blackboard Pattern

The blackboard (`swarm-blackboard.md`) is a markdown file for agent coordination:

```markdown
# Swarm Blackboard
Last Updated: 2026-02-04T10:30:00Z

## Knowledge Cache
### task:q4_analysis
{"status": "completed", "result": {...}, "agent": "data_analyst"}

### cache:revenue_summary  
{"q4_total": 1250000, "growth": 0.15}
```

### Blackboard Operations

```bash
# Write with TTL (expires after 1 hour)
python {baseDir}/scripts/blackboard.py write "cache:temp_data" '{"value": 123}' --ttl 3600

# Read (returns null if expired)
python {baseDir}/scripts/blackboard.py read "cache:temp_data"

# Delete
python {baseDir}/scripts/blackboard.py delete "cache:temp_data"

# Get full snapshot
python {baseDir}/scripts/blackboard.py snapshot
```

## Parallel Execution

For tasks requiring multiple agent perspectives:

### Strategy 1: Merge (Default)
Combine all agent outputs into unified result.
```
Ask data_analyst AND strategy_advisor to both analyze the dataset.
Merge their insights into a comprehensive report.
```

### Strategy 2: Vote
Use when you need consensus - pick the result with highest confidence.

### Strategy 3: First-Success
Use for redundancy - take first successful result.

### Strategy 4: Chain
Sequential processing - output of one feeds into next.

### Example Parallel Workflow

```
1. sessions_send to data_analyst: "Extract key metrics from Q4 data"
2. sessions_send to risk_assessor: "Identify compliance risks in Q4 data"  
3. sessions_send to strategy_advisor: "Recommend actions based on Q4 trends"
4. Wait for all responses via sessions_history
5. Synthesize: Combine metrics + risks + recommendations into executive summary
```

## Security Considerations

1. **Never bypass the permission wall** for gated resources
2. **Always include justification** explaining the business need
3. **Use minimal scope** - request only what you need
4. **Check token expiry** - tokens are valid for 5 minutes
5. **Validate tokens** - use `python {baseDir}/scripts/validate_token.py TOKEN` to verify grant tokens before use
6. **Audit trail** - all permission requests are logged

## 📝 Audit Trail Requirements (MANDATORY)

**Every sensitive action MUST be logged to `data/audit_log.jsonl`** to maintain compliance and enable forensic analysis.

### What Gets Logged Automatically

The scripts automatically log these events:
- `permission_granted` - When access is approved
- `permission_denied` - When access is rejected
- `permission_revoked` - When a token is manually revoked
- `ttl_cleanup` - When expired tokens are purged
- `result_validated` / `result_rejected` - Swarm Guard validations

### Log Entry Format

```json
{
  "timestamp": "2026-02-04T10:30:00+00:00",
  "action": "permission_granted",
  "details": {
    "agent_id": "data_analyst",
    "resource_type": "DATABASE",
    "justification": "Q4 revenue analysis",
    "token": "grant_abc123...",
    "restrictions": ["read_only", "max_records:100"]
  }
}
```

### Reading the Audit Log

```bash
# View recent entries (last 10)
tail -10 {baseDir}/data/audit_log.jsonl

# Search for specific agent
grep "data_analyst" {baseDir}/data/audit_log.jsonl

# Count actions by type
cat {baseDir}/data/audit_log.jsonl | jq -r '.action' | sort | uniq -c
```

### Custom Audit Entries

If you perform a sensitive action manually, log it:

```python
import json
from datetime import datetime, timezone
from pathlib import Path

audit_file = Path("{baseDir}/data/audit_log.jsonl")
entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "action": "manual_data_access",
    "details": {
        "agent": "orchestrator",
        "description": "Direct database query for debugging",
        "justification": "Investigating data sync issue #1234"
    }
}
with open(audit_file, "a") as f:
    f.write(json.dumps(entry) + "\n")
```

## 🧹 TTL Enforcement (Token Lifecycle)

Expired permission tokens are automatically tracked. Run periodic cleanup:

```bash
# Validate a grant token
python {baseDir}/scripts/validate_token.py grant_a1b2c3d4e5f6

# List expired tokens (without removing)
python {baseDir}/scripts/revoke_token.py --list-expired

# Remove all expired tokens
python {baseDir}/scripts/revoke_token.py --cleanup

# Output:
# 🧹 TTL Cleanup Complete
#    Removed: 3 expired token(s)
#    Remaining active grants: 2
```

**Best Practice**: Run `--cleanup` at the start of each multi-agent task to ensure a clean permission state.

## ⚠️ Swarm Guard: Preventing Common Failures

Two critical issues can derail multi-agent swarms:

### 1. The Handoff Tax 💸

**Problem**: Agents waste tokens "talking about" work instead of doing it.

**Prevention**:
```bash
# Before each handoff, check your budget:
python {baseDir}/scripts/swarm_guard.py check-handoff --task-id "task_001"

# Output:
# 🟢 Task: task_001
#    Handoffs: 1/3
#    Remaining: 2
#    Action Ratio: 100%
```

**Rules enforced**:
- **Max 3 handoffs per task** - After 3, produce output or abort
- **Max 500 chars per message** - Be concise: instruction + constraints + expected output
- **60% action ratio** - At least 60% of handoffs must produce artifacts
- **2-minute planning limit** - No output after 2min = timeout

```bash
# Record a handoff (with tax checking):
python {baseDir}/scripts/swarm_guard.py record-handoff \
  --task-id "task_001" \
  --from orchestrator \
  --to data_analyst \
  --message "Analyze sales data, output JSON summary" \
  --artifact  # Include if this handoff produces output
```

### 2. Silent Failure Detection 👻

**Problem**: One agent fails silently, others keep working on bad data.

**Prevention - Heartbeats**:
```bash
# Agents must send heartbeats while working:
python {baseDir}/scripts/swarm_guard.py heartbeat --agent data_analyst --task-id "task_001"

# Check if an agent is healthy:
python {baseDir}/scripts/swarm_guard.py health-check --agent data_analyst

# Output if healthy:
# 💚 Agent 'data_analyst' is HEALTHY
#    Last seen: 15s ago

# Output if failed:
# 💔 Agent 'data_analyst' is UNHEALTHY
#    Reason: STALE_HEARTBEAT
#    → Do NOT use any pending results from this agent.
```

**Prevention - Result Validation**:
```bash
# Before using another agent's result, validate it:
python {baseDir}/scripts/swarm_guard.py validate-result \
  --task-id "task_001" \
  --agent data_analyst \
  --result '{"status": "success", "output": {"revenue": 125000}, "confidence": 0.85}'

# Output:
# ✅ RESULT VALID
#    → APPROVED - Result can be used by other agents
```

**Required result fields**: `status`, `output`, `confidence`

### Supervisor Review

Before finalizing any task, run supervisor review:
```bash
python {baseDir}/scripts/swarm_guard.py supervisor-review --task-id "task_001"

# Output:
# ✅ SUPERVISOR VERDICT: APPROVED
#    Task: task_001
#    Age: 1.5 minutes
#    Handoffs: 2
#    Artifacts: 2
```

**Verdicts**:
- `APPROVED` - Task healthy, results usable
- `WARNING` - Issues detected, review recommended
- `BLOCKED` - Critical failures, do NOT use results

## Troubleshooting

### Permission Denied
- Provide more specific justification (mention task, purpose, expected outcome)
- Narrow the requested scope
- Check agent trust level

### Blackboard Read Returns Null
- Entry may have expired (check TTL)
- Key may be misspelled
- Entry was never written

### Session Not Found
- Run `sessions_list` to see available sessions
- Session may need to be started first

## References

- [AuthGuardian Details](references/auth-guardian.md) - Full permission system documentation
- [Blackboard Schema](references/blackboard-schema.md) - Data structure specifications
- [Agent Trust Levels](references/trust-levels.md) - How trust is calculated
- [CLI Reference](QUICKSTART.md) - Full `network-ai` CLI command reference (§ 10. CLI)
