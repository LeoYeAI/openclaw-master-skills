# Reference Draft — Multi-Agent Governance

Status: draft-for-skill
Role: deployable governance guide for supervised deployment, routing, and downgrade-run operation (no full automation support in v1)

## Scope

Use this guide when an OpenClaw workspace:
- has 2 or more agents participating in delivery, review, or governance work
- needs stable routing for implementation, documentation, and governance changes
- needs a safe degraded mode when fewer agents are available than the ideal shape
- wants a lightweight governance model without hardcoding one private org chart

This guide is meant for:
- supervised deployment-shape selection
- change-type and risk-tier routing
- reviewer / policy-auditor separation
- degraded-run declarations
- closure discipline and minimum governance artifacts

## Non-goals

This guide does **not** provide:
- autonomous task routing
- autonomous approval decisions
- autonomous role substitution
- autonomous consensus triggering
- self-validating full automation

All routing and governance decisions still require explicit coordinator and/or human supervision.

## Purpose

Help an OpenClaw workspace introduce multi-agent governance without hardcoding one private organization chart.

This reference is for:
- role separation
- change-type routing
- reviewer / policy-auditor boundaries
- deployment shapes
- degraded-run procedures when fewer agents are available
- approval boundaries
- closure discipline
- minimum governance artifacts

This reference is **not** a full automated orchestrator.

---

## Core Principle

Do not let one role silently do all of these at once on structural or high-risk work:
- propose the change
- implement the change
- review the change
- approve the policy impact

Default rule:
- structural or high-risk changes must not close through a single-person hidden loop
- if degraded operation forces role merging, the loss of independence must be declared explicitly and escalated to explicit human approval where required

---

## Quick Start

Use this guide in five steps:
1. classify the change type
2. assign a risk tier
3. choose the available deployment shape
4. route the work through the routing matrix
5. record the minimum artifacts and closure state

If any step is unclear, escalate upward rather than silently downgrading risk.

## Generic Roles

### Coordinator
Owns:
- framing the task
- choosing the path
- deciding whether the work is implementation, documentation, or governance/policy
- closing the loop

### Implementer
Owns:
- making the actual operational/file/script changes

### Reviewer
Owns:
- checking implementation quality
- catching technical mistakes, regressions, or overreach

### Policy Auditor
Owns:
- reviewing governance/policy/process/rule changes
- checking approval requirements and safety boundary changes

### Consensus Peer
Owns:
- second-brain directional review before risky structural changes
- giving an independent perspective before the work commits to a governance path

Important:
- Consensus Peer does not replace Reviewer or Policy Auditor
- it is a pre-commit sense-check layer, not the final approval layer

---

## Change Types

### 1. Implementation change
Examples:
- feature implementation
- bug fix
- script repair
- purely clerical, non-behavior-changing file edits

Default route:
- Coordinator → Implementer → Reviewer

---

### 2. Documentation / explanation change
Examples:
- explanatory docs
- doc status labeling
- inventory/index updates
- wording changes that do not alter meaning, default behavior, precedence, or approval boundaries

Default route:
- Coordinator → Implementer/Writer → Reviewer

Escalate if:
- the doc changes policy meaning
- the doc changes default behavior
- the doc changes source-of-truth precedence
- the doc alters approval boundaries

---

### 3. Governance / policy / process change
Examples:
- role boundaries
- approval requirements
- workflow rules
- maintenance rules
- safety restrictions
- source-of-truth precedence changes
- automation scope or permission boundary changes

Default route:
- Coordinator → Policy Auditor → explicit human approval when required → execution

Consensus pre-step:
- add Consensus Peer before Policy Auditor for structural or high-risk governance changes when that capacity exists

## Risk Tiers

Risk tier is separate from change type.

### Low-risk
Typical conditions:
- no change to default behavior
- no change to approval boundary
- no change to permissions or safety boundary
- no change to routing, role separation, or source-of-truth precedence
- no data-structure or automation-boundary changes

### Medium-risk
Typical conditions:
- affects operating guidance or normal routing behavior
- modifies deployable instructions used by others
- changes diagnostics, closure behavior, or maintenance handling
- crosses from explanation into operational meaning

### High-risk / structural
Trigger conditions include:
- changes role boundaries
- changes approval rules
- changes default routing
- changes source-of-truth precedence
- changes automation scope
- changes permission or safety boundaries
- merges roles in a way that removes independence on risky work
- cannot be confidently classified under a lower tier

Default escalation:
- high-risk / structural work must go through Policy Auditor review
- use Consensus Peer when the workspace has that capacity and the change affects broad governance direction
- if classification remains unclear after first pass, escalate upward rather than defaulting downward

---

## Routing Matrix

| Change type | Risk tier | Can one person close it? | Default route | Policy Auditor required? | Human approval required? | Downgrade declaration required? |
|---|---|---:|---|---|---|---|
| Implementation | Low | Only for purely clerical, non-behavior-changing edits with no lost independent review | Coordinator → Implementer → Reviewer | No | No, unless stricter local rules say otherwise | Yes, if independent review is lost |
| Implementation | Medium | No | Coordinator → Implementer → Reviewer | Required if the change alters operational meaning, default behavior, routing behavior, or approval interpretation | Required when degraded execution removes normal independence on risky work, or when local rules require approval | Yes, if roles merge or review independence is reduced |
| Implementation | High / structural | No | Coordinator → Implementer → Reviewer → Policy Auditor | Yes | Yes | Yes |
| Documentation / explanation | Low | Only for purely clerical, non-meaning-changing edits with no effect on defaults, precedence, or approvals | Coordinator → Writer/Implementer → Reviewer | No | No | Yes, if independent review is lost |
| Documentation / explanation | Medium | No | Coordinator → Writer/Implementer → Reviewer | Required if the document changes operational meaning, default behavior, precedence, or approval interpretation | Required when degraded execution removes normal independence, or when the doc affects approval/routing meaning | Yes, if roles merge or review independence is reduced |
| Documentation / explanation | High / structural | No | Coordinator → Writer/Implementer → Reviewer → Policy Auditor | Yes | Yes | Yes |
| Governance / policy / process | Medium | No | Coordinator → Policy Auditor → approval checkpoint → execution | Yes | Yes, unless a stricter local process already defines an equivalent explicit approval step | Yes |
| Governance / policy / process | High / structural | No | Coordinator → Consensus Peer (when available) → Policy Auditor → explicit human approval → execution | Yes | Yes | Yes |

Notes:
- this matrix is a routing default, not a replacement for stricter local safety rules
- if local rules are stricter, the stricter rule wins
- if classification is unclear, do not downgrade risk by guesswork; treat it as higher-risk until clarified
- degraded operation is a constrained fallback, not an equivalent substitute for normal separation

## Deployment Shapes

### 2-agent minimum
Use when the workspace is only moderately complex.

Roles:
- Agent 1: Coordinator + Implementer
- Agent 2: Reviewer

Run guidance:
- default route: Coordinator/Implementer → Reviewer
- governance and policy changes should not be treated as routine edits
- if Coordinator also effectively shaped the implementation, the review note should state that independence is limited
- for structural changes, add explicit human approval before execution

Required outputs:
- route decision
- review note
- degraded-run declaration when governance review is degraded
- closure note

Forbidden shortcuts:
- do not pretend governance review exists when it does not
- do not treat merged Coordinator/Implementer roles as equivalent to independent review

---

### 3-agent recommended
Use when the workspace has recurring implementation and maintenance complexity.

Roles:
- Agent 1: Coordinator
- Agent 2: Implementer
- Agent 3: Reviewer

Run guidance:
- default route: Coordinator → Implementer → Reviewer
- use this as the normal shape for implementation and non-governance documentation work
- governance changes still require explicit policy review or human escalation

Required outputs:
- route decision
- review note
- closure note

Forbidden shortcuts:
- do not let Reviewer silently replace Policy Auditor on governance changes
- do not close a governance change as routine documentation just because 3 agents are available

---

### 4-agent governance-aware
Use when policy/process changes are common.

Roles:
- Coordinator
- Implementer
- Reviewer
- Policy Auditor

Run guidance:
- default route for implementation: Coordinator → Implementer → Reviewer
- default route for governance/process changes: Coordinator → Policy Auditor → approval checkpoint → execution
- use this shape when approval rules, operating boundaries, or source-of-truth precedence are changed

Required outputs:
- route decision
- review note
- policy audit note
- closure note

Forbidden shortcuts:
- do not merge review and policy-audit conclusions into one vague note
- do not skip the approval checkpoint on governance changes that touch boundaries

---

### 5-agent governance-enhanced
Use when structural changes are frequent and risky.

Roles:
- Coordinator
- Implementer
- Reviewer
- Policy Auditor
- Consensus Peer

Run guidance:
- use Consensus Peer before Policy Auditor when governance direction is broad, structural, or hard to classify
- do not treat Consensus Peer as approval or final review
- use this shape for large workspaces with many layers and frequent system upgrades

Required outputs:
- route decision
- review note
- policy audit note
- consensus note
- closure note with final recommendation

Forbidden shortcuts:
- do not let Consensus Peer replace Policy Auditor
- do not treat consensus agreement as execution approval

---

## Degraded-run Procedure

Use degraded operation only when the preferred deployment shape is unavailable.

### Step 1 — Declare available capacity
State how many agents are actually available and which roles must be merged.

### Step 2 — Select the degraded shape explicitly
Examples:
- 1-agent degraded run
- 2-agent minimum shape
- 3-agent no-policy-auditor shape

### Step 3 — Declare independence loss
State which independence properties are lost, such as:
- proposer and implementer are the same
- implementer and reviewer are the same
- no independent policy audit exists

### Step 4 — Escalate risky work
If the change is medium-risk or higher and degraded operation removes normal independence:
- require explicit human confirmation where approval boundaries are involved
- do not claim degraded operation is equivalent to full separation

### Step 5 — Record the degraded run
Include a degraded-run declaration in the output artifacts.

### If only 1 agent exists
Do not pretend self-review equals independent review.

Required behavior:
- explicitly state where a second review would normally be used
- ask for human confirmation on medium-risk governance/policy changes
- require human approval on high-risk or structural governance changes
- avoid silently approving your own structural changes as if separation exists

### If only 2 agents exist
Use 2-agent minimum shape, but treat governance changes more cautiously.

Required behavior:
- if the same agent is acting as Coordinator and Implementer, governance/policy changes should not be treated as low-friction edits
- if no Policy Auditor exists, declare that governance review is degraded and route high-risk changes to human approval

---

## Approval Boundary

Use explicit human approval by default when a change:
- modifies approval rules
- modifies role boundaries
- changes default routing
- changes source-of-truth precedence
- changes automation scope
- changes permission or safety boundaries
- is being executed under degraded conditions with lost independence on risky work

Who decides whether approval is required:
- first, the routing matrix and local safety rules
- second, the Policy Auditor when present
- if still unclear, escalate rather than assuming approval is unnecessary

Never treat silence, historical approval, or broad prior permission as approval for a new structural change.

## Required Artifacts

A deployable governance flow should produce, at minimum:
- route decision
- review note (when review exists)
- policy audit note (when policy audit exists)
- degraded-run declaration (when degraded)
- closure note

These artifacts can be short, but they should be explicit enough to reconstruct how the change was routed and why.

## Consensus Pattern

Use a Consensus Peer before structural or high-risk changes when:
- the change alters governance/process/routing structure
- the impact is broad enough that one planner’s framing may be incomplete
- the workspace is already complex enough that a second directional check reduces risk

Do not use consensus as a substitute for:
- Policy Auditor review
- Reviewer checks
- explicit approval when required

---

## Precedence and Conflict Handling

This guide provides default governance guidance.

Conflict order:
1. explicit local safety and approval rules
2. stricter project or workspace governance rules
3. this guide as default routing and degraded-run guidance

This guide must not be used as justification for autonomous policy change, autonomous approval, or self-validating full automation.

---

## Closure Discipline

Every significant upgrade/change stream should eventually move from:
- active construction

to:
- maintenance observation

Closure is a supervised state transition, not an autonomous governance rewrite.
It should not automatically revoke rules, change approval boundaries, or rewrite source-of-truth precedence.

### Close-mainline criteria
A change stream is ready to close only when:
- the intended governance or routing change is landed clearly enough to operate
- the live source-of-truth documents are identified
- deferred items are explicitly listed instead of being silently dropped
- any degraded-run exceptions are recorded
- the remaining work is maintenance/improvement, not unresolved core design

### Closure decision outputs
At closure time, decide and record:
- what is landed
- what is improving
- what is deferred
- what remains live
- what becomes historical/background only
- who made the closure decision
- whether the closure happened under degraded conditions

### Archive rule
When a new governance or routing document is proposed:
- first check whether an existing source-of-truth document should be updated instead
- if a new document is still needed, state how it relates to existing live documents
- do not let multiple overlapping documents silently compete as current truth

---

## Minimal Examples

### Example 1 — Ordinary implementation change
Situation:
- a script bug needs fixing
- 3-agent shape is available

Route:
- Coordinator classifies as implementation / medium-risk
- Implementer makes the fix
- Reviewer checks correctness and regression risk
- closure note records landed result

### Example 2 — Documentation rewrite with operational impact
Situation:
- a doc rewrite changes the default behavior users will follow

Route:
- Coordinator classifies as documentation / medium-risk
- Writer updates the document
- Reviewer checks wording and operational effect
- because default behavior changed, escalate to Policy Auditor before treating it as final

### Example 3 — Governance change under 2-agent shape
Situation:
- approval boundaries must be tightened
- only 2 agents are available

Route:
- declare 2-agent minimum shape
- declare degraded governance review capacity
- classify as governance / high-risk
- obtain human approval before execution
- closure note records degraded run and approval checkpoint

### Example 4 — High-risk structural change with 1 agent
Situation:
- one agent wants to change routing precedence and approval rules

Route:
- declare 1-agent degraded run
- state that independent review and policy audit are unavailable
- do not self-close the change as if separation exists
- escalate to explicit human approval before execution
- record closure as degraded and high-risk

---

## v1 Boundary

This reference gives deployable guidance for:
- how to set up roles
- how to route work
- how to downgrade safely when fewer agents exist

It does **not** in v1 provide:
- automatic role spawning
- automatic routing decisions
- automatic approval enforcement
- automatic consensus orchestration

Treat it as an operations/governance playbook, not as an orchestration engine.
