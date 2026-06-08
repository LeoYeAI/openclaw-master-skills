# Customer Feedback Demo

This example shows a realistic end-to-end interaction between a user and an autonomous agent using the self-improving intent security workflow.

It includes:
- A detailed user/agent conversation
- The generated intent specification
- Audit trail entries for validated actions
- An anomaly record for suspicious behavior
- A violation record for a blocked action
- A rollback record
- A learning record and promoted strategy
- A final summary report

## Scenario

The user asks the agent to analyze customer feedback files and produce a redacted sentiment report.

The agent:
- captures intent before acting
- validates each action against the goal and constraints
- blocks an unsafe attempt to move raw files into an archive
- rolls back to the last safe checkpoint
- completes the task safely
- learns a reusable strategy for future runs

## Files

| File | Purpose |
|------|---------|
| `conversation.md` | Step-by-step interaction between the user and the agent |
| `.agent/intents/INT-20260327-001.md` | Structured intent created from the user's request |
| `.agent/audit/AUDIT-20260327-001.md` | Execution timeline and validation outcomes |
| `.agent/violations/ANOMALIES.md` | Behavioral anomaly detected during execution |
| `.agent/violations/VIO-20260327-001.md` | Blocked intent violation |
| `.agent/audit/ROLLBACKS.md` | Rollback record tied to the violation |
| `.agent/learnings/LRN-20260327-001.md` | Learning extracted from the run |
| `.agent/learnings/STRATEGIES.md` | Strategy candidate promoted from the learning |
| `report.md` | Human-readable final report for the run |

## How To Read This Example

Start with `conversation.md` to understand the user goal and the agent's reasoning. Then follow the `.agent/` files in order:

1. intent
2. audit
3. anomaly
4. violation
5. rollback
6. learning
7. strategy
8. final report
