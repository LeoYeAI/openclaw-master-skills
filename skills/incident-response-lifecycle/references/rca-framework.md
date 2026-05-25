# RCA Framework

Root cause analysis methodology, contributing factor taxonomy, and
post-mortem document structure for incident response reviews.

## 5-Whys Methodology

The 5-whys technique identifies root cause by asking "why" iteratively
until reaching a systemic cause — typically 3 to 5 iterations. The goal
is to move past symptoms to underlying process, technology, or
organizational failures.

### Rules for Effective 5-Whys

1. Start from the observable failure, not from assumptions
2. Each "why" must be answered with a factual, verifiable statement
3. If a "why" has multiple valid answers, branch and follow each path
4. Stop when you reach a cause that is actionable (you can create a
   fix, mitigation, or process change for it)
5. Avoid blame-oriented answers ("because the engineer made a mistake")
   — ask why the system allowed the mistake to happen

### Worked Example: Network Outage

```
Failure: Core router BGP sessions dropped, causing site-wide outage

Why 1: Why did BGP sessions drop?
→ The router reloaded unexpectedly during business hours

Why 2: Why did the router reload?
→ A scheduled firmware upgrade was applied at 10:00 AM
  instead of the planned 2:00 AM maintenance window

Why 3: Why was the upgrade applied at the wrong time?
→ The change management ticket listed 10:00 AM due to a
  timezone conversion error (UTC vs local time)

Why 4: Why was the timezone error not caught?
→ The change review process does not include timezone
  verification for maintenance windows

Why 5: Why is there no timezone verification?
→ The change request template uses a free-text time field
  without enforcing UTC or explicit timezone notation

Root Cause: Change request template allows ambiguous time entries
Action: Update change request template to require UTC timestamps
  with explicit timezone field and automated conversion
```

### Worked Example: Monitoring Failure

```
Failure: P1 outage ran for 45 minutes before detection

Why 1: Why was the outage not detected for 45 minutes?
→ No alert fired for the service health check failure

Why 2: Why did the alert not fire?
→ The alert rule had a 30-minute pending period configured

Why 3: Why was the pending period set to 30 minutes?
→ It was increased from 5 minutes to reduce false positives
  after a noisy alert period three months ago

Why 4: Why was the increased pending period not reviewed?
→ There is no periodic review process for alert threshold
  changes — changes are made ad-hoc without expiration

Root Cause: Alert threshold changes are permanent with no
  review cycle or automatic reversion
Action: Implement quarterly alert threshold review; add
  expiration dates to threshold change tickets
```

## Fishbone (Ishikawa) Diagram Template

Organize contributing factors into six standard categories to ensure
comprehensive analysis. Each category prompts investigation of a
different failure domain.

```
                         ┌─────────────────────┐
    ┌────────────────────┤   Incident / Failure │
    │                    └─────────────────────┘
    │
    ├── Process
    │   ├── Was there a runbook? Was it followed?
    │   ├── Was the change management process followed?
    │   ├── Were escalation procedures clear and current?
    │   └── Was there a review or approval step that was skipped?
    │
    ├── People
    │   ├── Was the on-call engineer trained on this system?
    │   ├── Was staffing adequate for the complexity?
    │   ├── Was handoff communication clear between shifts?
    │   └── Was there fatigue, overload, or distraction?
    │
    ├── Technology
    │   ├── Did monitoring detect the issue promptly?
    │   ├── Was there a single point of failure?
    │   ├── Was the software/firmware version known-stable?
    │   └── Did automation behave as expected?
    │
    ├── Environment
    │   ├── Was the failure related to capacity or load?
    │   ├── Were environmental conditions unusual (traffic spike)?
    │   └── Were dependencies (power, cooling, connectivity) stable?
    │
    ├── Information
    │   ├── Was documentation accurate and current?
    │   ├── Were network diagrams reflecting actual topology?
    │   ├── Were asset records and contact lists up to date?
    │   └── Was tribal knowledge a factor (undocumented procedure)?
    │
    └── External
        ├── Was a vendor or upstream provider involved?
        ├── Was there a third-party service dependency failure?
        └── Were external threats a factor (DDoS, compromise)?
```

## Contributing Factor Taxonomy

Classify each contributing factor to guide the type of remediation.

### Process Factors

- **Missing procedure** — no runbook or documented process existed
- **Outdated procedure** — runbook existed but did not match current
  environment or configuration
- **Procedure not followed** — runbook existed and was current but
  was not used during the incident
- **Insufficient review** — change or action was not reviewed by
  the appropriate parties
- **Communication gap** — information did not reach the right people
  at the right time

### People Factors

- **Training gap** — responder lacked knowledge of the affected system
- **Staffing shortage** — not enough people available for the response
- **Fatigue or overload** — responder was handling too many concurrent
  tasks or had been on-call too long
- **Handoff failure** — information was lost during shift change or
  role transfer

### Technology Factors

- **Monitoring gap** — the failure condition was not monitored or
  alerted on
- **Single point of failure** — no redundancy for the failed component
- **Software defect** — bug in firmware, application, or automation
- **Configuration error** — incorrect setting that was not caught by
  validation or review
- **Capacity limitation** — system reached a resource limit under
  normal or peak load

## Action Item Tracking Template

Every action item from the post-incident review must be tracked to
completion with clear ownership and verification criteria.

```
ACTION ITEM REGISTER — Incident [ID]

| # | Action Description | Type | Owner | Due Date | Status | Verification |
|---|-------------------|------|-------|----------|--------|-------------|
| 1 | [what needs to be done] | [Fix/Mitigate/Accept/Transfer] | [name] | [date] | [Open/In Progress/Done/Overdue] | [how to confirm completion] |
```

### Action Item Types

- **Fix** — eliminates the root cause entirely. Highest priority.
  Example: "Add timezone validation to change request template"
- **Mitigate** — reduces likelihood or impact without fully
  eliminating the cause. Example: "Add peer review requirement for
  maintenance window time entries"
- **Accept** — risk is within organizational tolerance. Requires
  documented rationale and management sign-off. Example: "Accept
  15-minute detection delay for non-critical monitoring paths"
- **Transfer** — assign responsibility to another team, vendor, or
  process. Example: "Escalate firmware bug to vendor for patch
  in next release"

### Verification Methods

Each action item needs a concrete verification method:

- Process changes: updated runbook reviewed and published
- Configuration changes: validated in staging, deployed, verified
  in production
- Monitoring additions: alert fires correctly in test scenario
- Training: attendance record, knowledge check completion
- Vendor actions: vendor confirms fix in release notes

## Post-Mortem Document Structure

The post-mortem document is the permanent record of the incident and
its review. Use this structure for consistency across reviews.

```
POST-MORTEM: [Incident ID] — [Brief Title]
============================================

DATE OF REVIEW: [date]
FACILITATOR:    [name]
ATTENDEES:      [list of participants and roles]

1. INCIDENT SUMMARY
   Severity: [P1/P2/P3]
   Duration: [start] — [end] ([total hours])
   Impact:   [users, services, revenue, data]
   One-line: [single sentence describing what happened]

2. TIMELINE
   | Time (UTC) | Event | Source |
   |-----------|-------|--------|
   | [time] | [what happened] | [log/person/alert] |

3. ROOT CAUSE
   5-Whys Analysis:
   - Why 1: [question] → [answer]
   - Why 2: [question] → [answer]
   - Why 3: [question] → [answer]
   - (continue until root cause reached)
   Root Cause Statement: [one paragraph]

4. CONTRIBUTING FACTORS
   | Factor | Category | Severity |
   |--------|----------|----------|
   | [description] | [Process/People/Technology] | [Primary/Secondary] |

5. WHAT WENT WELL
   - [aspects of the response that worked effectively]

6. WHAT COULD BE IMPROVED
   - [aspects of the response that need improvement]

7. ACTION ITEMS
   | # | Action | Type | Owner | Due | Verification |
   |---|--------|------|-------|-----|-------------|
   | 1 | [action] | [Fix/Mitigate/Accept/Transfer] | [name] | [date] | [method] |

8. LESSONS LEARNED
   - [key takeaways that apply beyond this incident]

9. FOLLOW-UP
   Action item review date: [date]
   Responsible for tracking: [name]
   Next recurrence check:   [date or "N/A if first occurrence"]
```
