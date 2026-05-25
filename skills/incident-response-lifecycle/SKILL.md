---
name: incident-response-lifecycle
description: >-
  Incident response process management following the NIST 800-61 lifecycle.
  Covers severity classification, escalation matrices, role assignment,
  communication management, phased recovery coordination, blameless
  post-mortem facilitation, and 5-whys root cause analysis. Scoped to
  the process and coordination layer — for network-level evidence
  collection and forensic analysis, use incident-response-network instead.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"🚨","safetyTier":"read-only","requires":{"bins":["ssh"],"env":[]},"tags":["incident","nist","postmortem"],"mcpDependencies":[],"egressEndpoints":[]}'
---

# Incident Response Lifecycle

Structured process management for network incidents from detection through
post-incident review. This skill covers the organizational coordination
layer: severity classification, escalation, role assignment, stakeholder
communication, recovery coordination, and root cause analysis. It does not
cover technical evidence collection, device forensics, or containment
execution — use the incident-response-network skill for network-level
evidence gathering and forensic analysis.

The procedure follows the operational lifecycle shape: detect and classify
the incident, triage and escalate to the right people, coordinate the
investigation across teams, manage communications to all audiences, drive
resolution and recovery, then conduct a blameless post-incident review.

See `references/communication-templates.md` for notification templates by
audience and severity level. See `references/rca-framework.md` for
the 5-whys methodology, fishbone diagram guidance, and post-mortem
document structure.

## When to Use

- **Service-affecting incident declared** — a P1 or P2 event requires
  formal incident management with role assignment and communications
- **Escalation decision needed** — determining who to notify at what
  severity level and when to engage vendor support or management
- **Multi-team coordination required** — investigation spans network,
  security, application, and infrastructure teams needing a single
  command structure
- **Customer or regulatory notification required** — incident has
  external communication obligations (SLA breach, data exposure,
  regulatory reporting)
- **Post-incident review facilitation** — scheduling, structuring, and
  running blameless post-mortems with 5-whys root cause analysis
- **Incident metrics reporting** — collecting MTTD, MTTI, MTTR, and
  recurrence data for continuous improvement

## Prerequisites

- **Incident management authority** — the person initiating this process
  must have authorization to declare incidents and assign roles within
  the organization
- **Contact directory** — current on-call rosters, escalation contacts
  for management, vendor TAC numbers, and regulatory notification
  contacts must be accessible
- **Communication channels** — bridge call infrastructure (conference
  line or collaboration tool), status page access, and email
  distribution lists for each stakeholder group must be established
- **Incident tracking system** — a ticketing system to record the
  incident, track actions, and maintain the timeline of events
- **Defined severity criteria** — organizational agreement on what
  constitutes P1 through P4 severity (see Threshold Tables below for
  a reference framework)

## Procedure

Follow these six steps in sequence. Steps 3 and 4 run in parallel once
roles are assigned — investigation coordination and communication
management proceed simultaneously. Each step references templates from
`references/communication-templates.md` and methodology from
`references/rca-framework.md` where applicable.

### Step 1: Detection and Classification

Classify the incident by severity, type, and scope to determine the
appropriate response level.

**Severity assignment** — apply the P1–P4 taxonomy from the Threshold
Tables section. Base severity on the highest-impact criterion met.
When multiple criteria apply at different levels, the highest governs.

**Incident type classification** — categorize as outage (service
unavailable), degradation (reduced capacity), security (unauthorized
access or data exposure), or data loss (corruption or deletion).

**Scope determination** — assess whether the incident affects a single
device, a network segment, an entire site, or multiple sites. Scope
drives staffing, communication breadth, and recovery complexity.

**Initial impact assessment** — estimate affected user count, impacted
services and their business criticality, data at risk, and revenue
impact per hour. Record estimates in the incident ticket.

### Step 2: Triage and Escalation

Assign roles, notify stakeholders, and set response timeline
expectations based on the severity classification from Step 1.

**Role assignment** — every P1 or P2 incident needs four named roles:
Incident Commander (IC) — owns the incident end-to-end and makes
escalation decisions; Technical Lead — coordinates diagnostics and
synthesizes findings; Communications Lead — drafts stakeholder
notifications and manages the status page; Scribe — maintains the
real-time timeline and records bridge call decisions. For P3, IC and
Technical Lead may be combined. P4 uses normal operations workflows.

**Escalation matrix execution** — notify by severity:
P1 — all four roles plus engineering management, VP/director on-call,
vendor TAC if vendor equipment is involved, executive notification
within 30 minutes. P2 — all four roles plus engineering management
within 1 hour. P3 — Technical Lead plus team lead within 4 hours.
P4 — assigned engineer via normal ticket queue.

**Response timeline expectations:**
P1 — bridge in 15 minutes, first update in 30 minutes, then every
30 minutes. P2 — bridge in 30 minutes, first update in 1 hour, then
every 2 hours. P3 — initial assessment in 4 hours, daily updates.
P4 — acknowledgment within 1 business day.

**Vendor engagement criteria** — engage vendor TAC when the incident
involves hardware failure, software defects requiring patches, or when
internal triage has not identified root cause within the severity time
window.

### Step 3: Investigation Coordination

Coordinate the technical investigation across teams and evidence
sources. For network-level evidence collection (device state, routing
tables, interface data, log retrieval), reference the
incident-response-network skill — this step focuses on organizing the
investigation, not executing forensic commands.

**Evidence collection tasking** — assign team members to collect
evidence from relevant domains: network devices (via
incident-response-network procedures), application logs, infrastructure
metrics, and security tooling alerts. Each assignee reports findings
to the Technical Lead.

**Parallel investigation streams** — for complex incidents, run
multiple investigation threads simultaneously. Common parallel
tracks: (1) symptom analysis — what is failing and for whom,
(2) change correlation — what changed recently (deployments, config
modifications, maintenance), (3) external factors — upstream provider
issues, DDoS, DNS resolution failures.

**Hypothesis tracking** — maintain a running list of hypotheses with
current status (investigating, confirmed, ruled out). Each hypothesis
should have an owner and a validation method. Update the list on every
bridge call.

**Timeline of events (ToE)** — the Scribe maintains a running
chronological log of when events occurred, when they were detected,
what actions were taken, and what was discovered. The ToE becomes the
foundation for the post-incident review in Step 6.

**Subject matter expert engagement** — when investigation stalls or
enters an unfamiliar domain, escalate to specialists. Define clear
handoff: what has been tried, what data is available, and what
specific question needs answering.

### Step 4: Communication Management

Manage stakeholder communications throughout the incident. Use the
templates in `references/communication-templates.md` for consistent
messaging across audiences.

**Stakeholder notification by audience** — executive summary (business
impact, estimated resolution, customer exposure — no technical detail),
technical detail (root cause hypothesis, diagnostics, remediation plan
— delivered on bridge call), customer-facing (service impact, workaround
if available, estimated resolution — via status page), regulatory
(formal notification per compliance framework when required). Use
templates from `references/communication-templates.md`.

**Status update cadence** — follow severity-based cadence from Step 2.
Each update includes: current status, progress since last update, next
planned action, and revised time-to-resolution estimate.

**Bridge call management** — the IC runs calls with a fixed agenda:
(1) technical status from Tech Lead, (2) communication status from
Comms Lead, (3) hypothesis updates, (4) decisions needed, (5) action
items with owners and deadlines. Keep calls focused — park side
discussions as action items.

**External notification requirements** — track regulatory reporting
deadlines, law enforcement notification when criminal activity is
suspected, customer SLA breach notification per contractual terms, and
vendor escalation for ongoing support.

### Step 5: Resolution and Recovery

Drive service restoration through validated recovery steps with
monitoring to confirm the fix holds.

**Recovery validation criteria** — before declaring resolved, confirm:
(1) service health checks return normal for all affected components,
(2) monitoring dashboards show green for at least 15 minutes (P1) or
30 minutes (P2), (3) no new related alerts during observation, (4)
affected users confirm restoration (sample check for large populations).

**Phased restoration** — for multi-layer network incidents, restore in
order: core infrastructure → distribution layer → access layer →
end-to-end verification. Verify each phase before proceeding. Do not
restore all layers simultaneously — cascading failures during recovery
are worse than a phased approach.

**Back-out plan execution** — if the fix causes new issues, execute
the pre-defined rollback. Every remediation action should have a
documented rollback method before execution.

**Enhanced monitoring period** — maintain heightened monitoring after
resolution: P1 for 24 hours, P2 for 12 hours, P3 through the next
business day. This means reduced alert thresholds on affected systems,
active watch by on-call, and immediate re-escalation if symptoms recur.

**Incident closure** — send closure notification to all stakeholders
(template in `references/communication-templates.md`). Update the
ticket with resolution summary, total duration, and final impact.
Schedule the post-incident review.

### Step 6: Post-Incident Review

Conduct a blameless post-incident review to identify root cause,
contributing factors, and improvement actions. See
`references/rca-framework.md` for the full methodology.

**Scheduling** — hold the post-mortem within 72 hours of incident
resolution while details are fresh. Invite all incident participants
plus relevant stakeholders. Send the invitation using the template in
`references/communication-templates.md`.

**5-whys root cause analysis** — apply iteratively: for each "why"
answer, ask "why" again until reaching a systemic root cause (typically
3–5 iterations). See `references/rca-framework.md` for worked
examples and facilitation guidance.

**Contributing factor categorization** — classify each contributing
factor as process (missing runbook, unclear escalation path),
people (training gap, staffing shortage), or technology (monitoring
gap, single point of failure, software defect). This categorization
guides the type of remediation action needed.

**Action item classification** — assign each action item one of four
dispositions: fix (eliminate the root cause), mitigate (reduce
likelihood or impact), accept (risk is within tolerance, document
rationale), or transfer (assign to another team or vendor). Every
fix or mitigate action must have an owner, due date, and verification
method.

**Incident metrics** — collect and record: Mean Time to Detect (MTTD),
Mean Time to Investigate (MTTI), Mean Time to Resolve (MTTR), total
incident duration, number of customers affected, and whether this is
a recurrence of a previous incident. Track these metrics over time to
measure improvement trends.

## Threshold Tables

### Severity Classification Matrix

| Severity | User Impact | Service Impact | Data Risk | Response SLA |
|----------|-----------|----------------|-----------|-------------|
| **P1 Critical** | >50% of users or all VIP users | Complete outage of revenue-generating service | Confirmed data breach or loss | Bridge in 15 min, updates every 30 min |
| **P2 High** | 10–50% of users affected | Major degradation or redundancy loss on critical path | Suspected data exposure | Bridge in 30 min, updates every 2 hr |
| **P3 Medium** | <10% of users, workaround exists | Partial degradation, non-critical service | No data risk identified | Assessment in 4 hr, updates daily |
| **P4 Low** | Minimal or no user impact | Cosmetic, non-production, or fully redundant | None | Ack in 1 business day |

### Escalation and Role Matrix

| Severity | Incident Commander | Technical Lead | Comms Lead | Scribe | Management | Executive |
|----------|-------------------|---------------|------------|--------|-----------|-----------|
| **P1** | Required | Required | Required | Required | Immediate | Within 30 min |
| **P2** | Required | Required | Required | Optional | Within 1 hr | If SLA breached |
| **P3** | Combined with Tech Lead | Required | Optional | No | Within 4 hr | No |
| **P4** | No | Assigned engineer | No | No | Normal reporting | No |

### Enhanced Monitoring Duration

| Severity | Monitoring Period | Alert Threshold | Re-escalation Trigger |
|----------|------------------|----------------|-----------------------|
| **P1** | 24 hours | Reduced by 20% | Any recurrence symptom |
| **P2** | 12 hours | Reduced by 10% | Same failure signature |
| **P3** | Next business day | Normal thresholds | Identical alert |
| **P4** | None | Normal | Normal process |

## Decision Trees

### Incident Severity Assignment

```
Event detected or reported
├── Is the service completely unavailable?
│   ├── Yes → Is it a revenue-generating or safety-critical service?
│   │   ├── Yes → P1 Critical
│   │   └── No → P2 High
│   └── No → Service is partially available
│       ├── Are more than 10% of users affected without workaround?
│       │   ├── Yes → P2 High
│       │   └── No → Is there a workaround available?
│       │       ├── Yes → P3 Medium
│       │       └── No, but fewer than 10% of users → P3 Medium
│       └── Is this a non-production or cosmetic issue?
│           └── Yes → P4 Low
├── Is there confirmed or suspected data exposure?
│   ├── Confirmed breach → P1 Critical (regardless of service status)
│   └── Suspected exposure → P2 High minimum
└── Has redundancy been lost on a critical path?
    ├── Yes, no failover remaining → P2 High
    └── Yes, failover still available → P3 Medium
```

### Escalation Decision

```
Severity assigned
├── P1 or P2?
│   ├── Yes → Assign all four roles immediately
│   │   ├── Is vendor equipment involved in the failure?
│   │   │   ├── Yes → Open vendor TAC case immediately
│   │   │   └── No → Internal investigation first
│   │   └── Has root cause been identified within time window?
│   │       ├── P1: not identified within 30 min → Escalate to next tier
│   │       └── P2: not identified within 2 hr → Escalate to next tier
│   └── P3 or P4?
│       ├── P3 → Assign Technical Lead, monitor for escalation
│       │   └── Impact worsening? → Re-classify severity upward
│       └── P4 → Normal ticket queue, no escalation
└── At any point: if scope expands beyond initial classification
    └── Re-evaluate severity from Step 1, escalate if needed
```

## Report Template

```
INCIDENT REPORT
=====================================
Incident ID:          [ticket/tracking number]
Severity:             [P1/P2/P3/P4]
Incident Commander:   [name]
Duration:             [detection time] — [resolution time] ([total hours])
Status:               [Resolved / Monitoring / Under Review]

IMPACT SUMMARY:
  Users Affected:     [count or percentage]
  Services Affected:  [list of impacted services]
  Revenue Impact:     [estimated or confirmed]
  Data Impact:        [none / suspected / confirmed — description]

TIMELINE OF EVENTS:
| # | Time (UTC) | Event | Actor | Notes |
|---|-----------|-------|-------|-------|
| 1 | [time] | [event description] | [person/system] | [context] |

ROOT CAUSE:
  Category:           [Process / People / Technology]
  Root Cause:         [description from 5-whys analysis]
  Contributing Factors:
    - [factor 1 — category]
    - [factor 2 — category]

RESOLUTION:
  Fix Applied:        [description of what resolved the incident]
  Validated By:       [how resolution was confirmed]
  Back-out Available: [yes/no — description]

METRICS:
  MTTD:               [time from occurrence to detection]
  MTTI:               [time from detection to root cause identified]
  MTTR:               [time from detection to resolution]
  Recurrence:         [yes/no — reference to prior incident if yes]

ACTION ITEMS:
| # | Action | Type | Owner | Due Date | Status |
|---|--------|------|-------|----------|--------|
| 1 | [action] | [Fix/Mitigate/Accept/Transfer] | [name] | [date] | [status] |

POST-MORTEM STATUS:
  Scheduled:          [date/time or "pending"]
  Attendees:          [roles invited]
  Document Location:  [link to post-mortem document]
```

## Troubleshooting

### Severity Disagreement Between Teams

**Symptom:** Teams classify the same incident at different severity
levels, causing confusion about response urgency.

**Resolution:** The IC makes the final determination using the
Threshold Tables criteria. The highest applicable severity governs.
Document rationale in the ticket. If the IC is not yet assigned, the
first responder sets initial severity and the IC may adjust.

### Escalation Fatigue and Alert Noise

**Symptom:** Frequent P1/P2 declarations for issues that resolve
quickly, eroding trust in severity classification.

**Resolution:** Review severity criteria quarterly. Track the
false-positive rate (incidents downgraded after initial classification).
If P1 downgrade rate exceeds 30%, tighten P1 criteria. Ensure P3/P4
incidents are not over-classified.

### Post-Mortem Action Items Not Completed

**Symptom:** Action items accumulate but are not completed, leading
to recurring incidents from known causes.

**Resolution:** Assign every action item an owner and due date at the
review. Track completion in the incident system, not separate documents.
Review open items in weekly standups. Escalate overdue items to
management and report completion rates alongside MTTD/MTTR.

### Communication Gaps During Extended Incidents

**Symptom:** Status updates become infrequent during long incidents
(>4 hours), leaving stakeholders uninformed.

**Resolution:** The Communications Lead maintains cadence regardless of
investigation progress. If no new findings exist, state that explicitly
in the update. For incidents exceeding 8 hours, rotate the Comms Lead
role to prevent fatigue.

### Incident Recurrence After Resolution

**Symptom:** The same incident recurs after being marked resolved.

**Resolution:** Check whether prior post-mortem action items were
completed. If yes, the root cause analysis was incomplete — reconvene
with broader scope. If not, escalate the completion failure. Tag the
new incident as a recurrence and increase severity by one level to
reflect accumulated impact.
